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

#Find doctors and episodes that exist from existing series sets
doctors = ["http://www.chakoteya.net/DoctorWho/episodes1.htm",
		   "http://www.chakoteya.net/DoctorWho/episodes2.htm",
		   "http://www.chakoteya.net/DoctorWho/episodes3.htm",
		   "http://www.chakoteya.net/DoctorWho/episodes4.htm",
		   "http://www.chakoteya.net/DoctorWho/episodes5.htm",
		   "http://www.chakoteya.net/DoctorWho/episodes6.htm",
		   "http://www.chakoteya.net/DoctorWho/episodes7.htm",
		   "http://www.chakoteya.net/DoctorWho/episodes9.html",
		   "http://www.chakoteya.net/DoctorWho/episodes10.html",
		   "http://www.chakoteya.net/DoctorWho/episodes11.html",
		   "http://www.chakoteya.net/DoctorWho/episodes12.html",
		   "http://www.chakoteya.net/DoctorWho/episodes13.html"]

links = pd.DataFrame(columns=["Doctor","Link","Season","EpisodeNo"])

#Crawl for episode links
for url in doctors:
	html_page = urllib.request.urlopen(url)
	soup = BeautifulSoup(html_page, features = "lxml")
	doctor_who = re.sub(r'http://www.chakoteya.net/DoctorWho/episodes',"Doctor_",url)
	doctor_who = re.sub(r"\.htm","",doctor_who)
	doctor_who = re.sub(r"l","",doctor_who)

	for link in soup.findAll('a'):
		if re.match(r".*-.*", link.get("href")):
			
			season = re.sub("-.*","",str(link.get("href")))
			j = re.sub(".*-","",str(link.get("href")))
			temp = pd.DataFrame({"Doctor":[doctor_who],
								 "Link":"http://www.chakoteya.net/DoctorWho/"+str(link.get("href")),
								 "Season":season,
								 "EpisodeNo":j})
			links = pd.concat([links,temp])
			#links = pd.concat([links,tempdf],axis=1)

links = links.reset_index()

#remove nuisance episodes
links = links[~((links["Season"] == "33") & (links["EpisodeNo"] == "05.htm"))]

with open("links.csv", mode='w', newline='\n', encoding='utf-8') as f:
	links.to_csv(f, sep=",", line_terminator='\n', encoding='utf-8')

#Init data frame for all scripts
all_Episodes = pd.DataFrame(columns=["Character","Script","Location","DoctorWho","SeriesNo","EpisodeNo"])

#Iterate over all episode links
for ind, row in links.iterrows():

	url = row["Link"]
	this_doctor = row["Doctor"]
	this_episode = row["EpisodeNo"]
	this_season = row["Season"]

	this_file = re.sub("http://www.chakoteya.net/","",url)
	this_file = re.sub(r"\.htm","",this_file)
	this_file = re.sub("l","",this_file)
	this_file = re.sub("/","_",this_file)
	this_file += ".csv"

	print("Downloading season " + str(this_season) + ", Episode " + str(this_episode))

	#View html
	data = {}
	resp = requests.get(url)
	if resp.status_code == 200:
		data[url] = resp.text

	#Extract text
	soup = BeautifulSoup(data[url], features = "lxml")
	soup_text = soup.get_text().split("\n")

	#Convert to usable array
	soup_df = pd.DataFrame(soup_text)
	soup_df.columns = ["Script"]
	soup_df["Script"] = soup_df["Script"].astype(str)

	this_file_raw = "Raw/"+str(this_file)
	
	#Remove carriage returns and [OC] from script lines
	soup_df["Script"] = soup_df["Script"].str.replace(r"\r","", regex = True)
	soup_df["Script"] = soup_df["Script"].str.replace(r"\[OC\]","", regex = True)
	soup_df["Script"] = soup_df["Script"].str.replace(r"\[on monitor\]","", regex = True)

	with open(this_file_raw, mode='w', newline='\n', encoding='utf-8') as f:
		soup_df.to_csv(f, sep=",", line_terminator='\n', encoding='utf-8')



#Sanitize script, remove descriptive text, separate characters and locations	
for script in this_file_raw:

	#Try to select for lines containing dialogue or location
	#Lines that contain "(", ")" and do not contain ":" are typically stage directions
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\s*\(.*\)$")]
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\(.*\)$")]
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\(.*\)\s*$")]
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\s*$")]

	#Find first location and remove all preamble
	firstloc = soup_df[soup_df["Script"].str.match(r"\s*\[.*\]")].index[0]
	soup_df = soup_df[soup_df.index >= firstloc]

	#Separate character into a new col
	soup_df.insert(0, "Character", "")
	soup_df.loc[soup_df["Script"].str.contains(":"), "Character"] = soup_df.Script.str.split(":").str[0]
	soup_df.loc[~soup_df["Script"].str.contains(":"), "Character"] = None

	#Separate Location into a new col
	soup_df.insert(2, "Location", None)
	soup_df.loc[soup_df["Script"].str.match(r"\s*\[.*\]"), "Location"] = soup_df.Script

	#Forward fill location, then remove remaining vestigal location rows
	soup_df["Location"] = soup_df["Location"].fillna(method="ffill")
	soup_df = soup_df[~soup_df["Script"].str.match(r"\s*\[.*\]")]

	#Forward fill characters and remove script references
	soup_df["Character"] = soup_df["Character"].fillna(method="ffill")
	soup_df.loc[soup_df["Script"].str.contains(":"), "Script"] = soup_df.Script.str.split(":").str[1]

	#Remove empty script lines
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\s*$")]

	#Try to remove all stage directions
	#Remove directions nestled in dialogue
	soup_df["Script"] = soup_df["Script"].str.replace(r"\(.*\)","", regex = True)

	#Remove directions that take up an entire script line
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\s*\(.*\)\s*$")]
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\(.*\)$")]
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\(.*\)\s*$")]
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\s*\(.*\)$")]

	#re-do indices after 1st removals
	soup_df = soup_df.reset_index()

	#Remove stage directions which span multiple script lines
	bracket_starts = soup_df[soup_df["Script"].str.contains(r"^(?!.*\().*\)")].index.values.tolist()
	bracket_ends = soup_df[soup_df["Script"].str.contains(r"^(?!.*\)).*\(")].index.values.tolist()
	brackets_indices = [list(x) for x in zip(bracket_starts,bracket_ends)]

	rem_ranges = []
	for remove in brackets_indices:
		rem_range = list(range(int(remove[1]),int(remove[0]+1)))
		rem_ranges.append(rem_range)

	flat_rem_range = list(chain.from_iterable(rem_ranges))
	soup_df = soup_df.drop(soup_df.index[flat_rem_range])	

	print(soup_df.loc[1:100])

	#Remove everything before "Next episode"
	lastloc = soup_df[soup_df["Script"].str.match(r"(\s*Next episode|\<Back)")].index[0]
	
	print(str(lastloc))
	
	soup_df = soup_df[soup_df.index < lastloc]
	soup_df = soup_df.dropna()
	soup_df = soup_df.reset_index()

	#Remove empty script lines
	soup_df = soup_df[~soup_df["Script"].str.match(r"^\s*$")]

	#Combine multi-line dialogue
	char_groups = soup_df['Character'].ne(soup_df['Character'].shift()).cumsum()
	soup_df[["Script","Character","Location"]] = soup_df[["Script","Character","Location"]].groupby(char_groups).agg(" " .join).reset_index(drop=True)
	soup_df = soup_df.dropna()

	#Clearing up artefacts in char and loc
	soup_df["Character"] = soup_df["Character"].str.replace(r"\s+", r' ', regex=True)
	soup_df["Location"] = soup_df["Location"].str.replace(r"\s+", r' ', regex=True)
	soup_df["Character"] = soup_df["Character"].str.replace(r"\t", r'', regex=True)

	#Remove trailing spaces from char and loc
	soup_df["Character"] = soup_df["Character"].str.replace(r"^\s", r'', regex=True)
	soup_df["Location"] = soup_df["Location"].str.replace(r"^\s", r'', regex=True)

	#Remove ['s and ]'s from locations
	soup_df["Location"] = soup_df["Location"].str.replace(r"\[", r'', regex=True)
	soup_df["Location"] = soup_df["Location"].str.replace(r"\]", r'', regex=True)

	#Remove repeats
	soup_df['Location'] = soup_df['Location'].apply(lambda x: ','.join(pd.unique(x.split(' '))))
	soup_df['Character'] = soup_df['Character'].apply(lambda x: ','.join(pd.unique(x.split(' '))))
	
	soup_df["Character"] = soup_df["Character"].str.replace(r",", r' ', regex=True)
	soup_df["Location"] = soup_df["Location"].str.replace(r",", r' ', regex=True)

	#Remove trailing spaces, AGAIN
	soup_df["Location"] = soup_df["Location"].str.replace(r"\s*$", r'', regex=True)
	soup_df["Location"] = soup_df["Location"].str.replace(r"^\s*", r'', regex=True)

	soup_df["Character"] = soup_df["Character"].str.replace(r"\s*$", r'', regex=True)
	soup_df["Character"] = soup_df["Character"].str.replace(r"^\s*", r'', regex=True)



	soup_df.insert(3, "DoctorWho", this_doctor)
	soup_df.insert(4, "SeriesNo", this_season)
	soup_df.insert(5, "EpisodeNo", this_episode)

	all_Episodes = pd.concat([all_Episodes,soup_df])

	#with open(this_file, "w", encoding="utf-8") as f:
	#	dfAsString = soup_df.to_string(header=True, index=False)
	#	f.write(dfAsString)

print("Writing all episodes to file.")

all_Episodes.to_csv("all_Episodes.csv", sep='\t')



