#Morariu Tudor 12-17 ian 2025

from funcs.GenericScraper import GenericScraper
import sys
import os

print('''
  _                          __              __                     
 /   _  ._ _|_  _   _ _|_   (_  o _|_  _    (_   _ ._ _. ._   _  ._ 
 \_ (_) | | |_ (/_ _>  |_   __) |  |_ (/_   __) (_ | (_| |_) (/_ |  
                                                         |          ''')

if(len(sys.argv) <= 2):
    print(
        '''
    usage: python3 ContestSiteScraper.py [contest site name] [username] [opt. config file location (json)]
    example: python3 ContestSiteScraper.py codeforces morariu.tudor
    example: python3 ContestSiteScraper.py kilonva morariu_tudor
    example: python3 ContestSiteScraper.py infoarena MorariuT /tmp/conf.json
    
    avalible site names: codeforces, pbinfo, infoarena, kilonova        
        '''
    )

    sys.exit()

os.system("mkdir ./plots");


contest_site_name = sys.argv[1];
usr = sys.argv[2];
config_file_location = "./utils/config.json"

print("Getting " + usr + " submissions from " + contest_site_name)

if(len(sys.argv) >= 4): config_file_location = sys.argv[3],

scr = GenericScraper(
    contest_site_name = contest_site_name,
    config_file_location = config_file_location,
    username=usr
).get_class()(
    username=usr,
    config_file_location= config_file_location
)

print("Got " + str(len(scr.get_df())) + " entries");

dataframe = scr.get_df();

f = open("./utils/table", 'w')
f.write(dataframe.to_json())

print("Plotting. Generating output in ./plots/" + usr);

scr.plot_hist("sub_year", open_plt_window=False);
scr.plot_pie_chart("sub_year", open_plt_window=False);
scr.plot_wordcloud("problem", open_plt_window=False);
scr.plot_wordcloud("tags", open_plt_window=False);

url_path = scr.compile_report();

print("Access this url for result: " + url_path)l



