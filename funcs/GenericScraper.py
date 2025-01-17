import functools
import glob
import os

import pandas as pd
import json

from jinja2.utils import open_if_exists
from wordcloud import WordCloud
from IPython.core.display_functions import display
from matplotlib import pyplot as plt


class GenericScraper():
    df_submissions = pd.DataFrame()

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'
    }
    def __init__(self, contest_site_name, username: str, config_file_location="./utils/config.json", matplotlib_style="dark_background"):
        '''
        :param contest_site_name: Name of the contest site you are scraping.
        :param config_file_location: Location of the configuration file.
        :param username: Username of the user
        :param matplotlib_style: Style of the matplotlib plot.
        '''
        plt.style.use(matplotlib_style)
        self.contest_data = None;
        self.contest_site_name = contest_site_name
        self.user = username
        conf = open(config_file_location, "r")
        self.data = json.load(conf)
        self.contest_data = self.data[contest_site_name];
        conf.close()

    def __str__(self):
        return self.df_submissions

    def __repr__(self):
        return self.df_submissions

    def print(self):
        '''
        Function that prints the dataframe.
        '''
        print(self.df_submissions)

    def get_df(self):
        '''
        Function that return the submissoins DataFrame.
        :return: Pandas DataFrame
        '''
        return self.df_submissions

    def save_to_file(self, path="./submissions"):
        '''
        Function that saves the dataframe to a file.
        :param path: Path where the submissions df will be saved.
        '''
        os.system("mkdir -p " + path + "/" + self.user);
        self.df_submissions.to_csv(path + "/" + self.user + "/" + self.contest_site_name + ".csv", index=False)

    def get_class(self):
        '''
        Function that returns the class of the contest site for a given name in the init.
        :return: Python Class Object
        '''
        mod = __import__("funcs." + self.contest_data[0]["scraper"], fromlist=self.contest_data[0]["scraper"])
        klass = getattr(mod, self.contest_data[0]["scraper"])
        return klass

    def plot_col_by_col(self, col1, col2, height=7, width=15, open_plt_window=True):
        '''
        Function that plots a column against other column of the dataframe.
        :param col1: The first column of the plot (the x)
        :param col2: The second column of the plot (the y)
        :param height: Height of the plot (param for matplotlib)
        :param width: Weight of the plot (param for matplotlib)
        '''
        try:
            fig, ax = plt.subplots(
                nrows=1,
                ncols=2,
                figsize=(width, height),
                dpi=250
            );

            ax.set_title("Column by Column plot for Columns: " + str(col1) + " & " + str(col2));


            print(self.df_submissions[col1])
            print(self.df_submissions[col2])

            ax[0].plot(self.df_submissions[col1], self.df_submissions[col2], 'o');
            ax[0].set_title(col1 + " by " + col2);
            ax[0].set_xlabel(col1);
            ax[0].set_ylabel(col2);
            ax[1].plot(self.df_submissions[col2], self.df_submissions[col1], 'o');
            ax[1].set_title(col2 + " by " + col1);
            ax[1].set_xlabel(col2);
            ax[1].set_ylabel(col1);

            plt.savefig('./plots/' + self.user + '/col_by_col_' + str(col1) + "_" + str(col2) + "_" + self.contest_site_name + '.png')


            if (open_plt_window):
                plt.show()
        except Exception as e:
            print("Column by Column plot Failed: " + str(e));

    def plot_wordcloud(self, col, width=750, height=400, max_font=50, max_words=300, open_plt_window=True):
        '''
        Function that plots a word cloud for a given column.
        :param col: The column
        :param width: Width of the word cloud (param for wordcloud)
        :param height: Height of the word cloud (param for wordcloud)
        :param max_font: Max font size (param for wordcloud)
        :param max_words: Max number of words (param for wordcloud)
        '''
        try:
            col_as_words = ""

            for val in self.df_submissions[col].values.tolist():
                col_as_words = col_as_words + str(val) + " "

            wordcloud = WordCloud(
                max_font_size=max_font,
                max_words=max_words,
                background_color="black",
                width=width,
                height=height,
            )

            wordcloud.generate(col_as_words)

            fig, ax = plt.subplots(
                nrows=1,
                ncols=1,
            );

            ax.set_title("Wordcloud for Column: " + str(col))


            ax.imshow(
                wordcloud,
                interpolation='bilinear'
            )

            ax.axis('off')

            plt.savefig('./plots/' + self.user + '/wordcloud_' + str(col) + "_" + self.contest_site_name + '.png')


            if (open_plt_window):
                plt.show()
        except Exception as e:
            print("Wordcloud Failed: " + str(e));

    def plot_hist(self, col, height=7, width=15, bins=100, dpi=100, open_plt_window=True):
        '''
        Function that plots a histogram for a given column.
        :param col: The column.
        :param height: Height of the histogram (param for matplotlib)
        :param width: Width of the histogram (param for matplotlib)
        :param bins: Number of bins (param for matplotlib)
        :param dpi: DPI of the plot (param for matplotlib)
        :param open_plt_window: bool, used for report
        :return PNG image of hist
        '''

        def cmp(x: str, y: str):
            if(len(x) > len(y)): return 0
            elif(len(x) < len(y)): return 1

            for i in range(len(x)):
                if(x[i] < y[i]): return 1

            return 0;

        try:


            values_as_strings = [];

            for val in self.df_submissions[col].values:
                values_as_strings.append(str(val));

            values_as_strings = sorted(
                values_as_strings,
                key=functools.cmp_to_key(cmp)
            );

            fig, ax = plt.subplots(
                nrows=1,
                ncols=1,
                figsize=(width, height),
                dpi=dpi
            );

            ax.set_title("Histogram Plot for Column: " + str(col))


            ax.hist(
                x=values_as_strings,
                bins=bins,
            );

            os.system("mkdir -p " + "./plots/" + self.user);

            plt.savefig('./plots/' + self.user + '/hist_plot_' + str(col) + "_" + self.contest_site_name + '.png')


            if (open_plt_window):
                plt.show()

        except Exception as e:
            print("Histogram Plot Failed:" + str(e));

    def plot_pie_chart(self, col, height=7, width=7, dpi=100, open_plt_window=True):
        '''
        Function to plot the piechart of a row with countable objects
        :param col: The column.
        :param height: Height of the histogram (param for matplotlib)
        :param width: Width of the histogram (param for matplotlib)
        :param dpi: DPI of the plot (param for matplotlib)
        '''
        try:
            fig, ax = plt.subplots(
                nrows=1,
                ncols=1,
                figsize=(width, height),
                dpi=dpi
            );

            ax.set_title("Pie Chart for Column: " + str(col))

            vf = {}
            vf_vals = [];
            vf_keys = [];

            for val in self.df_submissions[col].values:
                if(val not in vf): vf[val] = 0;
                vf[val] += 1;

            for key in vf.keys():
                vf_vals.append(vf[key]);
                vf_keys.append(key);

            ax.pie(
                x=vf_vals,
                labels=vf_keys,
                autopct='%1.1f%%'
            )

            os.system("mkdir -p " + "./plots/" + self.user);

            plt.savefig('./plots/' + self.user + '/pie_chart_' + str(col) + "_" + self.contest_site_name + '.png')

            if (open_plt_window):
                plt.show()

        except Exception as e:
            print("PieChart Plot Failed:" + str(e));

    def compile_report(self):
        '''
        Function that generates a html containing the obtained data
        :param plots_path: Path of the plots folder
        :return: path to html --> str
        '''

        plots_path = ("./plots/" + str(self.user) + '/')

        img_paths = glob.glob(plots_path + "*.png")
        template = open("./utils/template.html", "r").readlines();

        images = [];

        for path in img_paths:
            img = '<img src="{path}" class="center">'.format(path=path.split('/')[-1]);
            images.append(img)

        os.system("mkdir -p " + "./plots/" + self.user);

        report = open("./plots/" + self.user + "/report_" + self.contest_site_name + "_" + self.user + ".html", 'w');

        for line in template:
            line = line.strip();
            if("{USER}" in line):
                line = line.format(USER=self.user);
            if ("{DataFrame}" in line):
                line = line.format(DataFrame=self.df_submissions.to_json(orient="records"));
            report.write(line + '\n');
            if('<div id="Content">' == line):
                for img in images:
                    report.write(img + '\n');
        report.close()

        return "file://" + str(os.path.abspath("./plots/" + self.user + "/report_" + self.contest_site_name + "_" + self.user + ".html"));