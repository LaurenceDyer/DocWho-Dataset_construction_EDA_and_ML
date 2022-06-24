from bs4 import BeautifulSoup

import pandas as pd
import numpy as np
from itertools import chain

import os
import re

pd.set_option('display.max_rows', 1000)
pd.set_option('max_colwidth',80)
pd.set_option('display.max_columns', None)
pd.set_option('display.expand_frame_repr', False)

directory = "Raw/"

all_Episodes = pd.DataFrame(columns=["Character","Location","Script","Character_Location","DoctorWho","SeriesNo","EpisodeNo"])

links = pd.read_csv("links.csv", index_col = 0)

links["EpisodeNo"] = links["EpisodeNo"].str.replace(".html","",regex=True)
links["EpisodeNo"] = links["EpisodeNo"].str.replace(r"\.htm","",regex=True)

links.insert(0, "File_Location", links["Season"])

#links = links[(links["Link"] == "http://www.chakoteya.net/DoctorWho/35-2.html")]

#Iterate over files for data sanitation
for index, row in links.iterrows():

	url = row["Link"]
	this_doctor = row["Doctor"]
	this_episode = row["EpisodeNo"]
	this_season = row["Season"]

	this_file = "./Raw/DoctorWho_"+str(row["Season"])+"-"+str(this_episode)+".csv"

	print("Sanitizing:")
	print(this_doctor, this_season, this_episode, this_file)

	#Convert to usable array
	soup_df = pd.read_csv(this_file, index_col = 0)

	#Try to select for lines containing dialogue or location
	#drop NAs
	soup_df = soup_df.dropna()

	#Remove all potential stage directions
	soup_str = soup_df.Script.str.cat(sep="###")
	
	#Removing erroneous ":"s after [OC]
	soup_str = re.sub(r"\: \:",":",soup_str)
	soup_str = re.sub(r"\([^()]*\)"," ",soup_str)

	#Fix all double-lined locations (Why are locations ever double-lined? Pointless!)
	#I'm quite proud of these two regex commnds
	soup_str = re.sub(r"(\[[^\]]*)\#\#\#([^\]]*\])",r"\1 \2 ###",soup_str)

	#Fix names that are needlessly split
	soup_str = re.sub(r"([A-Z])\s(?=[A-Z])",r"\1",soup_str)
	soup_str = re.sub(r"([A-Z])\s(?=[0-9]+)",r"\1",soup_str)

	#Fix names with '+'s in them
	soup_str = re.sub(r"([A-Z]*)\s*\+\s*([A-Z]*)",r"\1-AND-\2",soup_str)

	#Fix erroneous "}"s
	soup_str = re.sub(r"(\})",r"]",soup_str)
	soup_str = re.sub(r"(\{})",r"[",soup_str)
	soup_str = re.sub(r"(\[on monitor)",r"",soup_str)
	soup_str = re.sub(r"(OC\])",r"",soup_str)
	soup_str = re.sub(r"(on monitor\])",r"",soup_str)
 
	#Removing more stage directions which are hidden next to character specifications
	#There were a LOT of these, but it was generally not safe to regex over these
	#specific sets, due to the fact that occasionlly genuine locations are mistakenly
	#followed by a ":". It took about 30 minutes to find them all. Bleh.
	annoying_patterns = [r" \[(OC)\]",r" \[(on scanner)\]",r" \[(on radio)\]",r" \[(on monitor)\]",r" \[(on laptop)\]",r" \[(on camera)\]",r" \[(on screen)\]",r" \[(on machine)\]",
						 r" \[(on viewscreen)\]",r" \[(on tv screen)\]",r" \[(on TV)\]",r" \[(TV)\]",r" \[(PC)\]",r" \[(previously)\]",r" \[(on film)\]",r" \[(on telephone)\]",
						 r" \[(on television)\]",r" \[(on holoimager)\]",r" \[(on ball)\]",r" \[(on phone)\]",r" \[(on horseback)\]",r" \[(on tannoy)\]",r" \[(projection)\]",
						 r" \[(bedroom)\]",r" \[(through door)\]",r" \[(behind door)\]",r" \[(mirror)\]",r" \[(monitor)\]",r" \[(watch)\]",r" \[(text)\]",r" \[(hologram)\]",
						 r" \[(hotel reception)\]",r" \[(memory)\]",r" \[(tower)\]",r" \[(room 12)\]",r" \[(Doctor's memory)\]",r" \[(Human Nature)\]",r" \[(Genesis of the Daleks)\]",
						 r" \[(Resurrection of the Daleks)\]",r" \[(Remembrance of the Daleks)\]",r" \[(Stolen Earth)\]",r" \[(Dalek Asylum)\]",r" \[(advert)\]",r" \[(telepathic)\]",
						 r" \[(transmission)\]",r" \[(silent)\]",r" \[(answerphone)\]",r" \[(over tannoy)\]",r" \[(facetime)\]",r" \[(muffled)\]",r" \[(closing titles)\]",
						 r" \[(in ball)\]",r" \[(in bag)\]",r" \[(in tunnel)\]",r" \[(in cauldron)\]",r" \[(in glass)\]",r" \[(in orbit)\]",r" \[(in box)\]",
						 r" \[(in slave quarters)\]",r" \[(in the Dalek)\]",r" \[(in picture frame)\]",r" \[(Revelation of the Daleks)\]",r" \[(Outside the records room)\]"]

	for pattern in annoying_patterns:
		soup_str = re.sub(pattern,r"",soup_str)



	#Add line break immediately before and after all locations, because many are carried over
	soup_str = re.sub(r"(\[[^\]]*\])",r"\1 ###",soup_str)
	soup_str = re.sub(r"(\[[^\]]*\])",r"### \1",soup_str)

	#Add new lines immediately before a character speaks, because many are missing, except where character is preceeded by -AND-
	soup_str = re.sub(r"([^A-Z|\-])([A-Z]+:)",r"\1 ### \2",soup_str)

	#Back to DF
	soup_str = soup_str.split("###")
	soup_df = pd.DataFrame(soup_str)
	soup_df.columns = ["Script"]

	#Find first location and remove all preamble
	firstloc = soup_df[soup_df["Script"].str.match(r"\s*\[.*\]")].index[0]
	soup_df = soup_df[soup_df.index >= firstloc]

	#Remove everything before "Next episode" or "<Back to episode listing"
	lastloc = soup_df[soup_df["Script"].str.match(r"(\s*Next episode|\<Back)")].index[0]
	soup_df = soup_df[soup_df.index < lastloc]

	#Remove empty script lines
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\s*$")]

	#Separate character into a new col
	soup_df.insert(0, "Character", "")
	soup_df.loc[soup_df["Script"].str.contains(":"), "Character"] = soup_df.Script.str.split(":").str[0]
	soup_df.loc[~soup_df["Script"].str.contains(":"), "Character"] = None

	#Forward fill characters and remove script references
	soup_df["Character"] = soup_df["Character"].fillna(method="ffill")
	soup_df.loc[soup_df["Script"].str.contains(":"), "Script"] = soup_df.Script.str.split(":").str[1]

	#Separate Location into a new col
	soup_df.insert(2, "Location", None)
	soup_df.loc[soup_df["Script"].str.match(r"\s*\[.*\]"), "Location"] = soup_df.Script

	#Forward fill location, then remove remaining vestigal location rows
	soup_df["Location"] = soup_df["Location"].fillna(method="ffill")
	soup_df = soup_df[~soup_df["Script"].str.match(r"\s*\[.*\]")]	

	#Remove character location cues such as [On screen] or [OC]
	soup_df["Character"] = soup_df["Character"].str.replace(r"\[[^\]]*\]","",regex=True)

	#Remove trailing and ending spaces in character
	soup_df["Character"] = soup_df["Character"].str.replace(r"^\s+","",regex=True)
	soup_df["Character"] = soup_df["Character"].str.replace(r"\s+$","",regex=True)
	#And in location
	soup_df["Location"] = soup_df["Location"].str.replace(r"^\s+","",regex=True)
	soup_df["Location"] = soup_df["Location"].str.replace(r"\s+$","",regex=True)

	#print(soup_df)

	#Combine multi-line dialogue, except where characters switch location
	soup_df.insert(3, "Character_Location", None)
	soup_df["Character_Location"] = soup_df["Character"] + ";" + soup_df["Location"]

	#Remove empty script lines
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\s*$")]

	soup_df = soup_df.drop(columns=["Character","Location"])

	grp = (soup_df['Character_Location'] != soup_df['Character_Location'].shift()).cumsum().rename('group')
	soup_df = soup_df.groupby(['Character_Location', grp], sort=False)['Script'].agg(' '.join).reset_index().drop('group', axis=1)
		
	#Separate character and location specifications
	soup_df["Character"] = soup_df["Character_Location"].str.split(";").str[0]
	soup_df["Location"] = soup_df["Character_Location"].str.split(";").str[1]

	#Reorder
	soup_df = soup_df[["Character","Location","Script","Character_Location"]]

	soup_df.insert(4, "DoctorWho", this_doctor)
	soup_df.insert(5, "SeriesNo", this_season)
	soup_df.insert(6, "EpisodeNo", this_episode)
	soup_df.insert(6, "EpisodeURL", url)

	all_Episodes = pd.concat([all_Episodes,soup_df])

print("Writing all episodes to file.")
all_Episodes.to_csv("all_Episodes.csv", sep='\t')
