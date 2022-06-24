from bs4 import BeautifulSoup
import requests
import urllib.request

import pandas as pd
import numpy as np
from itertools import chain

import re

pd.set_option('display.max_rows', 1000)
pd.set_option('max_colwidth',60)
pd.set_option('display.max_columns', None)

#Input wikipedia url
url = "https://en.wikipedia.org/wiki/List_of_Doctor_Who_episodes_(1963-1989)"
html_page = urllib.request.urlopen(url)
soup = BeautifulSoup(html_page, features = "lxml")

#Take tables from soup page
tables = soup.find_all('table',{'class':"wikitable"})

all_tabs_df = pd.DataFrame(columns=["Season",tables[2].columns])

#Transform tables to pandas.df
for table in tables[2:]:
	tab_df=pd.read_html(str(table))
	tab_df=pd.DataFrame(tab_df[0])

	tab_df.insert(0,"Season",value = str(seasonNo))

	all_tabs_df = pd.concat([all_tabs_df,tab_df], ignore_index=True)

with open("Classic_Wikipedia.csv", mode='w', newline='\n', encoding='utf-8') as f:
	all_tabs_df.to_csv(f, sep=",", line_terminator='\n', encoding='utf-8')

#Input wikipedia url
url = "https://en.wikipedia.org/wiki/List_of_Doctor_Who_episodes_(2005-present)"
html_page = urllib.request.urlopen(url)
soup = BeautifulSoup(html_page, features = "lxml")

#Take tables from soup page
tables = soup.find_all('table',{'class':"wikitable"})

all_tabs_df = pd.DataFrame(columns=["Season",tables[2].columns])
seasonNo = 1
#Transform tables to pandas.df
for table in tables[2:]:
	tab_df=pd.read_html(str(table))
	tab_df=pd.DataFrame(tab_df[0])

	tab_df.insert(0,"Season",value = str(seasonNo))

	all_tabs_df = pd.concat([all_tabs_df,tab_df], ignore_index=True)

with open("Modern_Wikipedia.csv", mode='w', newline='\n', encoding='utf-8') as f:
	all_tabs_df.to_csv(f, sep=",", line_terminator='\n', encoding='utf-8')