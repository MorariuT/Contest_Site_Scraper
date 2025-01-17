import numpy as np
import requests
import re
import pandas as pd
import json
from funcs.GenericScraper import GenericScraper



class IAScraper(GenericScraper):
    def __init__(self, username: str, pages=10, config_file_location="config.json"):
        '''
        :param username: The username of the person you are stalking
        :param pages: The number of pages you are scraping
        :param config_file_location: Location of the config file
        '''
        super().__init__(
            contest_site_name="infoarena",
            config_file_location=config_file_location,
            username = username
        );

        self.pages = pages

        self.run(
            username=username
        );

    def resolve_ia(self):
        '''
        Fucntion that resolves the specific infoarena dependencies
        '''
        url = self.contest_data[0]["format_url"]
        self.contest_data[0]["get_url"] = url;

    def fill_dataframe(self, user):
        '''
        Function that makes the requests to the contest site and parses the html
        :param user: The username of the person you are stalking
        '''
        self.resolve_ia();

        for page in range(0, self.pages):
            try:
                request_url = self.contest_data[0]["get_url"].format(
                    dspl_entry=50,
                    fst_entry=page*50,
                    user=user
                )

                html_content = requests.get(
                    request_url,
                    headers=self.headers
                ).content;

                html_table_as_df = pd.read_html(html_content)[1]

                if (len(html_table_as_df) == 0): break;

                self.df_submissions = pd.concat(
                    [self.df_submissions, html_table_as_df],
                    ignore_index=True
                )

            except IndexError:
                print("Done.")
                break;

    def extract_info_from_problem(self, pb_name):
        '''
        Function that extracts the information from the given problem name
        :param pb_name: The name of the problem you want to analyze
        :return: python list --> problem tags
        '''
        pb_link = "https://www.infoarena.ro/problema/" + pb_name

        html_content = requests.get(
            url=pb_link,
            headers=self.headers
        ).text;

        tag_search = re.findall(
            pattern='<div class="sub_tag_name">\s*<a class="sub_tag_search_anchor" href="/cauta-probleme\?tag_id\[\]=[^"]*">[^<]*</a>\s*</div>',
            string=html_content
        )

        tags = [];

        for match in tag_search:
            tag = str(match).split("</a></div>")[0].split(">")[-1];
            tags.append(tag)

        return tags

    def split_submission_date(self, date: str):
        '''
        Function that splits a string date into a usable form
        :param date: String representing the date in the DataFrame
        :return: Python List[5] -> [minute, hour, day, month, year]
        '''
        #15 feb 24 20:39:13
        split_data = date.strip().split(' ');

        day = split_data[0];
        month = split_data[1];
        year = "20" + split_data[2];

        hour = split_data[3].split(':')[0];
        minute = split_data[3].split(':')[1];

        map_month = {
            "ian": 1,
            "feb": 2,
            "mar": 3,
            "apr": 4,
            "mai": 5,
            "iun": 6,
            "iul": 7,
            "aug": 8,
            "sep": 9,
            "oct": 10,
            "nov": 11,
            "dec": 12
        }

        month = map_month[month];

        return [minute, hour, day, month, year];



    def run(self, username):
        '''
        Function that runs the scraping function and converts the dataframe into a standard form
        :param username: The username of the person you are stalking
        '''
        self.fill_dataframe(
            user=username
        )


        def unpack_date(row):
            date_list = self.split_submission_date(row["data"])
            row["sub_minute"] = date_list[0]
            row["sub_hour"] = date_list[1]
            row["sub_day"] = date_list[2]
            row["sub_month"] = date_list[3]
            row["sub_year"] = date_list[4]
            return row

        def add_tags_to_df(row):
            prob = row['problem']
            tags = self.extract_info_from_problem(prob)

            row['tags'] = tags;
            return row;

        formated_df = pd.DataFrame();
        formated_df["id_submission"] = self.df_submissions["ID"];
        formated_df["problem"] = self.df_submissions["Problema"];
        formated_df["code_size"] = self.df_submissions["Marime"];
        formated_df["memory_user"] = np.nan;  # TODO: Take from sub info
        formated_df["language"] = np.nan;  # Not mentioned anywhere???

        formated_df["data"] = self.df_submissions["Data"];
        formated_df["scor"] = self.df_submissions["Stare"];

        formated_df["scor"] = formated_df["scor"].apply(lambda x: x.split(" ")[2])
        formated_df = formated_df.apply(add_tags_to_df, axis=1)
        formated_df = formated_df.apply(unpack_date, axis=1);

        formated_df.drop(columns="data", inplace=True);

        self.df_submissions = formated_df;

        self.save_to_file();

if(__name__ == "__main__"):
    scr = IAScraper(
        username="MorariuT",
        pages=10,
        config_file_location="config.json"
    );

    scr.extract_info_from_problem("xormax");