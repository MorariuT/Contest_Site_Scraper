import numpy as np
import requests
import re
import pandas as pd
import json
from funcs.GenericScraper import GenericScraper

class PBScraper(GenericScraper):
    def __init__(self, username: str, pages=100, config_file_location="config.json"):
        '''
        :param username: Username of the person you are stalking
        :param pages: The number of pages to iterate when extracting the submissions
        :param config_file_location: Location of the config file
        '''
        self.pages = pages

        super().__init__(
            config_file_location=config_file_location,
            contest_site_name="pbinfo",
            username=username
        )
        self.run(
            username=username
        );

    def resolve_pb(self):
        '''
        Function for solving specific pbinfo dependencies
        :return: Nothing
        '''
        url = self.contest_data[0]["format_url"]
        self.contest_data[0]["get_url"] = url;

    def fill_dataframe(self, user):
        '''
        Function that fills the dataframe from the contest site
        :param user: Username of the person you are stalking
        :return: Nothing
        '''
        self.resolve_pb();

        for page in range(0, self.pages):
            try:
                url = self.contest_data[0]["get_url"].format(fst_entry=page*50, user=user)
                html_content = requests.get(url, headers=self.headers).content;
                html_table_as_df = pd.read_html(html_content)[0]

                if(len(html_table_as_df) == 0):
                    break;

                self.df_submissions = pd.concat([self.df_submissions, html_table_as_df], ignore_index=True)

            except IndexError:
                print("Done.")

    def extract_info_from_problem(self, pb_name):
        '''
        TODO:
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
        split_data = date.strip().split(' ');

        day = split_data[0];
        month = split_data[1];
        year = split_data[2][:-1]; #last elm is comma

        hour = split_data[3].split(':')[0];
        minute = split_data[3].split(':')[1];

        map_month = {
            "Ianuarie": 1,
            "Februarie": 2,
            "Martie": 3,
            "Aprilie": 4,
            "Mai": 5,
            "Iunie": 6,
            "Iulie": 7,
            "August": 8,
            "Septembrie": 9,
            "Octombrie": 10,
            "Noiembrie": 11,
            "Decembrie": 12
        }

        month = map_month[month];

        return [minute, hour, day, month, year];


    def run(self, username):
        '''
        A type of main but its name is run, it also formats the dataset to a standard form
        :param username: The username of the person you are stalking
        :return: Nothing
        '''
        self.fill_dataframe(
            user=username,
        )

        def unpack_date(row):
            date_list = self.split_submission_date(row["data"])
            row["sub_minute"] = date_list[0]
            row["sub_hour"] = date_list[1]
            row["sub_day"] = date_list[2]
            row["sub_month"] = date_list[3]
            row["sub_year"] = date_list[4]
            return row

        self.df_submissions["Scor"] = self.df_submissions["Unnamed: 1"];
        self.df_submissions.drop(columns="Unnamed: 1", inplace=True);

        formated_df = pd.DataFrame();

        formated_df["id_submission"] = self.df_submissions["ID"];
        formated_df["problem"] = self.df_submissions["Problema"];

        formated_df["code_size"] = np.nan; #TODO: Take from sub info
        formated_df["memory_user"] = np.nan; #TODO: Take from sub info
        formated_df["language"] = np.nan; #TODO: Take from sub info

        formated_df["data"] = self.df_submissions["Data încărcării"];
        formated_df["scor"] = self.df_submissions["Stare.1"];
        formated_df["tags"] = np.nan;

        formated_df = formated_df.apply(unpack_date, axis=1);
        formated_df.drop(columns="data", inplace=True);

        self.df_submissions = formated_df;
        self.save_to_file();




if(__name__ == "__main__"):
    scr = PBScraper(
        username="rake2008",
        pages=10,
        config_file_location="config.json"
    );
