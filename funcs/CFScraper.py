import datetime

import numpy as np
import requests
import re
import pandas as pd
import json
from funcs.GenericScraper import GenericScraper

class CFScraper(GenericScraper):
    def __init__(self, username: str, config_file_location="config.json"):
        '''
        :param username: The username of the person you are stalking
        :param config_file_location: Location of the config file
        '''
        super().__init__(
            contest_site_name="codeforces",
            config_file_location=config_file_location,
            username=username
        )
        self.run(
            username=username
        );

    def resolve_cf(self):
        '''
        Function that resolves the dependencies of the codeforces url
        :return: Nothing
        '''
        url = self.contest_data[0]["format_url"]
        self.contest_data[0]["get_url"] = url;

    def fill_dataframe(self, user):
        '''
        Function that actually makes the requests and puts it all together. The CF submission request
        works on basis of an API CF provided, so no need for pages.
        :param user: The username of the person you are stalking
        :return: Nothing
        '''
        self.resolve_cf();

        try:
            url = self.contest_data[0]["get_url"].format(
                user=user
            )
            html_text = requests.get(
                url=url,
                headers=self.headers
            ).text

            submissions_json = json.loads(html_text)['result'];
            self.df_submissions = pd.concat([self.df_submissions, pd.DataFrame(submissions_json)], ignore_index=True)
        except IndexError:
            print("Done or code is faulty.")

    def unpack_df(self):
        '''
        Special function, unique to CF, that unpacks columns that are returned as a dict
        :return: Nothing
        '''

        def process_row(row):
            mp = row["problem"]
            for k in mp.keys(): row[k] = mp[k];
            return row;

        self.df_submissions = self.df_submissions.apply(process_row, axis=1);
        self.df_submissions.drop(columns=["problem", "author"], inplace=True);

    def split_submission_date(self, date: int):
        '''
        Function that splits a string date into a usable form
        :param date: int representing the seconds from the beginning of the epoch
        :return: Python List[5] -> [minute, hour, day, month, year]
        '''
        #15 feb 24 20:39:13
        date = datetime.datetime.fromtimestamp(date);

        day = date.day;
        month = date.month;
        year = date.year;

        hour = date.hour;
        minute = date.minute;

        return [minute, hour, day, month, year];

    def run(self, username):
        '''
        Function that puts all the above together and formats the resulting DataFrame into a standard form.
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

        self.unpack_df();

        formated_df = pd.DataFrame();

        formated_df["id_submission"] = self.df_submissions["id"];
        formated_df["problem"] = self.df_submissions["name"];
        formated_df["code_size"] = np.nan;
        formated_df["data"] = self.df_submissions["creationTimeSeconds"];
        formated_df["memory_user"] = self.df_submissions["memoryConsumedBytes"];
        formated_df["language"] = self.df_submissions["programmingLanguage"];  # Not mentioned anywhere???
        formated_df["tags"] = self.df_submissions["tags"];
        formated_df["scor"] = self.df_submissions["verdict"];

        formated_df = formated_df.apply(unpack_date, axis=1);

        formated_df.drop(columns=["data"], inplace=True);

        self.df_submissions = formated_df;
        self.save_to_file();

if __name__ == "__main__":
    scr = CFScraper(
        username="morariu.tudor",
        config_file_location="config.json"
    );
