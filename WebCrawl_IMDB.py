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

#Create links for season homepages for both classic and modern series
season_classic = "https://www.imdb.com/title/tt0056751/episodes?season="
season_modern = "https://www.imdb.com/title/tt0436992/episodes?season="
seasons_classic = ["https://www.imdb.com/title/tt0056751/episodes?season=" + str(i) for i in range(1,27)]
seasons_modern = ["https://www.imdb.com/title/tt0436992/episodes?season=" + str(i) for i in range(1,14)]

#Initialise link frame
links_classic = pd.DataFrame(columns=["Season","Episode","Link"])

#Loop over all links on season homepages and save episode links
seasonNo = 1
for season in seasons_classic:
	html_page = urllib.request.urlopen(season)
	soup = BeautifulSoup(html_page, features = "lxml")

	episodeNo = 1

	for link in soup.findAll('a'):
		epLink = link.get("href")
		if re.match(r"/title/.*/$",epLink): 
			if epLink != "/title/tt0056751/":
				if ~links_classic["Link"].str.contains(epLink).any():
					temp = pd.DataFrame({"Season":[seasonNo],
										  "Episode":[episodeNo],
										  "Link":[epLink]})

					links_classic = pd.concat([links_classic,temp], ignore_index = True)
					episodeNo += 1

	seasonNo += 1



links_modern = pd.DataFrame(columns=["Season","Episode","Link"])

#Repeat for modern series
seasonNo = 1
for season in seasons_modern:
	html_page = urllib.request.urlopen(season)
	soup = BeautifulSoup(html_page, features = "lxml")

	episodeNo = 1

	for link in soup.findAll('a'):
		epLink = link.get("href")
		if re.match(r"/title/.*/$",epLink): 
			if epLink != "/title/tt0436992/":
				if ~links_modern["Link"].str.contains(epLink).any():
					temp = pd.DataFrame({"Season":[seasonNo],
										  "Episode":[episodeNo],
										  "Link":[epLink]})

					links_modern = pd.concat([links_modern,temp], ignore_index = True)
					episodeNo += 1

	seasonNo += 1



links_modern["Season"] = links_modern["Season"]+26
links_modern.drop(links_modern.tail(1).index,inplace=True)

print("Classic Seasons:")
print(links_classic)
print("Modern Seasons:")
print(links_modern)

detail_df_c = pd.DataFrame(columns=["Season","Episode","Rating","Runtime","Writers"])

for index, epRow in links_classic.iterrows():

	seasonNo = epRow["Season"]
	episodeNo = epRow["Episode"]

	print("Grabbing details for:")
	print(seasonNo,episodeNo)

	link = epRow.Link

	html_page = urllib.request.urlopen("https://www.imdb.com"+link)

	soup = BeautifulSoup(html_page, "lxml")

	epRating = re.sub("<[^>]+>","",soup.find("span", class_="sc-7ab21ed2-1 jGRxWM").text)
	epRuntime = re.sub("Runtime","",re.sub("<[^>]+>","",soup.find("li", class_="ipc-metadata-list__item", attrs={"data-testid":"title-techspec_runtime"}).text))
	
	temp = pd.DataFrame({"Season":[seasonNo],
						 "Episode":[episodeNo],
						 "Rating":[epRating],
						 "Runtime":[epRuntime]})

	detail_df_c = pd.concat([detail_df_c,temp], ignore_index = True)

with open("Classic_Seasons_IMDB.csv", mode='w', newline='\n', encoding='utf-8') as f:
	detail_df_c.to_csv(f, sep=",", line_terminator='\n', encoding='utf-8')

detail_df_m = pd.DataFrame(columns=["Season","Episode","Rating","Runtime","Writers"])

for index, epRow in links_modern.iterrows():

	seasonNo = epRow["Season"]
	episodeNo = epRow["Episode"]

	print("Grabbing details for:")
	print(seasonNo,episodeNo)

	link = epRow.Link

	html_page = urllib.request.urlopen("https://www.imdb.com"+link)

	soup = BeautifulSoup(html_page, "lxml")

	#Episode tt15243958 doesn't really exist

	epRating = re.sub("<[^>]+>","",soup.find("span", class_="sc-7ab21ed2-1 jGRxWM").text)
	epRuntime = re.sub("Runtime","",re.sub("<[^>]+>","",soup.find("li", class_="ipc-metadata-list__item", attrs={"data-testid":"title-techspec_runtime"}).text))
	
	temp = pd.DataFrame({"Season":[seasonNo],
						 "Episode":[episodeNo],
						 "Rating":[epRating],
						 "Runtime":[epRuntime]})

	detail_df_m = pd.concat([detail_df_m,temp], ignore_index = True)

with open("Modern_Seasons_IMDB.csv", mode='w', newline='\n', encoding='utf-8') as f:
	detail_df_m.to_csv(f, sep=",", line_terminator='\n', encoding='utf-8')

