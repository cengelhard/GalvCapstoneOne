
import re
import requests
import json
from datetime import datetime
import time

#load the app id and the api key. These should not be added to the git repo.
#currently strings.
app_id = None
api_key = None

with open("../API_key.txt", "r") as file:
	app_id = re.split(": ", file.readline())[-1].strip()
	api_key = re.split(": ", file.readline())[-1].strip()

#tests
#print(app_id)
#print(api_key)

'''
20 requests every 1 seconds
100 requests every 2 minutes
'''
short_term_wait = 1
long_term_wait = 120

last_successful_request = None

def get(url):
	def with_auth(r):
		r.headers["X-Riot-Token"] = api_key
		return r

	global last_successful_request

	r = requests.get(url, auth=with_auth)
	while r.status_code == 429:

		now = datetime.now()
		time_since = (now - last_successful_request).seconds if last_successful_request else 0

		if time_since < short_term_wait: #if short might work
			print("trying a short wait.")
			time.sleep(short_term_wait)
		else: 
			print(f"DOING A LONG WAIT: {long_term_wait} seconds")
			time.sleep(long_term_wait)
		r = requests.get(url, auth=with_auth)


	last_successful_request = datetime.now()
	return r

				




def match(id):
	return f"https://na1.api.riotgames.com/lol/match/v4/matches/{id}"

def summoner_by_name(name):
	return f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/by-name/{name}'


def mastery_by_summoner(id):
	return f'https://na1.api.riotgames.com/lol/champion-mastery/v4/champion-masteries/by-summoner/{id}'



'''load static data from json files.'''
#champs
champions = None
with open("champion.json") as file:
	champions = json.loads(file.read())

champs_by_name = champions['data']
champs = {v['key']: v for _,v in champs_by_name.items()}

#our sample (courtesy of http://canisback.com/matchId/matchlist_na1.json) for now.
sample_matches = None
with open("match_sample.json") as file:
	sample_matches = json.loads(file.read())

#our player sample (courtesy of make_player_sample() below)
sample_players = None
with open("player_sample.json") as file:
	sample_players = json.loads(file.read())


def get_match(id):
	return get(match(id))
#generates a list of players based on the sample_matches
def make_player_sample(max_n):
	playerIds = set()
	for matchId in sample_matches:
		r = get_match(matchId)
		if r.status_code != 200: #hit the limit for the API
			print(f'make_player_sample failed with status code {r.status_code}')
			break
		match = r.json()

		for participant in match['participantIdentities']:
			playerIds.add(participant['player']['summonerId'])
			if len(playerIds) >= max_n:
				return list(playerIds)
	return list(playerIds)

def save_as_json(data, filename):
	with open(filename, 'w') as outfile:
		json.dump(data, outfile)


		


def test_seasons():
	test_matches = [get_match(i).json() for i in sample_matches[10:20]]
	for m in test_matches:
		print(m['seasonId'])


def test_butseps():
	r = get(summoner_by_name('butseps'))
	print(r.status_code)
	my_json = r.json()
	my_id = my_json['id']
	print(my_id)

	r = get(mastery_by_summoner(my_id))
	print(r.status_code)
	return r.json()

#my_masteries = test_butseps()


#actually, somebody helpful on the discord recommended a different approach to this.
#but I'll keep this here just in case.
def get_player_samples(n, sample = set()):

	while len(sample) < n:
		r = get("https://na1.api.riotgames.com/lol/spectator/v4/featured-games")
		if r.status_code != 200:
			return sample
		fgames = r.json()
		time.sleep() #sleep for the suggested time.
		





