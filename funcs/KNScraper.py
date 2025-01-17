import base64
import datetime

import requests
import re
import pandas as pd
import json
from funcs.GenericScraper import GenericScraper

class KNScraper(GenericScraper):
    def __init__(self, username: str, pages=10, config_file_location="config.json"):
        '''
        :param username: The username of the person you are stalking
        :param pages: The number of pages you are scraping
        :param config_file_location: Location of the config file
        '''

        super().__init__(
            contest_site_name="kilonova",
            config_file_location=config_file_location,
            username=username
        );
        self.pages = pages;
        self.run(
            username=username
        );

    def resolve_kn(self, user):
        '''
        Function that find the user_id from the username provided. It makes a request to the profile page
        of the person and searches for the submissions page, using a regex.
        :param user: The username of the person you are stalking
        :return: Nothing
        '''

        profile_url = self.contest_data[0]["format_url"].format(
            user=user
        )

        user_page_html = requests.get(profile_url)
        user_id_postfix = re.search('user_id=\d+', user_page_html.text).group()

        url = "https://kilonova.ro/api/submissions/get?ascending=false&limit=50&offset={page}&ordering=id&" + user_id_postfix;
        self.contest_data[0]["get_url"] = url;
        self.contest_data[0]["dependencies"].append("page")

    def fill_dataframe(self, user):
        '''
        Function that does the requests to the contest site and parses the html into DataFrames.
        :param user: The username of the person you are stalking
        :return: Nothing
        '''
        self.resolve_kn(
            user=user
        )

        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
        }

        for page in range(1, self.pages):
            try:
                url = self.contest_data[0]["get_url"].format(
                    page=page
                )

                submissions_json = json.loads(
                    requests.get(
                        url=url,
                        headers=headers
                    ).text
                )["data"]["submissions"];

                if(len(submissions_json) == 0): break;

                for submisson in submissions_json:
                    self.df_submissions = pd.concat(
                        [self.df_submissions, pd.DataFrame([submisson])],
                        ignore_index=True
                    )

            except IndexError:
                break;

    def extract_info_from_problem(self, pb_id):
        '''
        Function that extracts the information from the given problem name
        :param pb_id: The id of the problem you want to analyze
        :return: python list --> problem tags
        '''
        try:
            pb_link = "https://kilonova.ro/problems/" + str(pb_id)
            html_content = requests.get(
                url=pb_link,
                headers=self.headers
            ).text;

            tag_search = re.findall(
                pattern='</p><p>Tags: <kn-pb-tags enc=[^\s>]+',
                string=html_content
            )

            tags = [];

            tag = str(tag_search[0]).split('="')[1].split('"')[0] + "=";
            tags_as_json = json.loads(base64.b64decode(tag))

            for tag_dict in tags_as_json:
                tags.append(tag_dict["name"])

            return tags
        except IndexError:
            pass

    def split_submission_date(self, date: str):
        '''
        Function that splits a string date into a usable form
        :param date: String representing the date in ISO format
        :return: Python List[5] -> [minute, hour, day, month, year]
        '''
        date = datetime.datetime.fromisoformat(date);

        day = date.day;
        month = date.month;
        year = date.year; #last elm is comma

        hour = date.hour;
        minute = date.minute;

        return [minute, hour, day, month, year];

    def run(self, username):
        '''
        Function that runs the above code and formats the DataFrame into a standard form.
        :param username: The username of the person you are stalking
        :return: Nothing
        '''
        self.fill_dataframe(
            user=username,
        )

        # Add problem tags to df
        def add_tags_to_df(row):
            prob = row['problem']
            tags = self.extract_info_from_problem(prob)

            row['tags'] = tags;
            return row;

        def unpack_date(row):
            date_list = self.split_submission_date(row["data"])
            row["sub_minute"] = date_list[0]
            row["sub_hour"] = date_list[1]
            row["sub_day"] = date_list[2]
            row["sub_month"] = date_list[3]
            row["sub_year"] = date_list[4]
            return row

        formated_df = pd.DataFrame();
        formated_df["id_submission"] = self.df_submissions["id"];
        formated_df["problem"] = self.df_submissions["problem_id"];
        formated_df["code_size"] = self.df_submissions["code_size"];
        formated_df["memory_user"] = self.df_submissions["max_memory"];
        formated_df["language"] = self.df_submissions["language"];
        formated_df["data"] = self.df_submissions["created_at"];
        formated_df["scor"] = self.df_submissions["score"];

        formated_df = formated_df.apply(add_tags_to_df, axis=1)
        formated_df = formated_df.apply(unpack_date, axis=1)

        formated_df.drop(columns=["data"], inplace=True)


        self.df_submissions = formated_df;

        self.save_to_file();


if __name__ == "__main__":
    scr = KNScraper(
        username="morariu_tudor",
        config_file_location="config.json"
    );

    scr.extract_info_from_problem(10);
