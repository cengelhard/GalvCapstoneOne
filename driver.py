
import re
import requests
import json
from datetime import datetime
import time
import numpy as np
from scipy import stats

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

def leagues_by_summoner(id):
	return f'https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/{id}'

def load_json(filename):
	with open(filename) as file:
		return json.loads(file.read())

def load_json_array(filename):
	return np.array(load_json(filename))

'''load static data from json files.'''
#champs
champions = load_json("champion.json")
champs_by_name = champions['data']
champs = {v['key']: v for _,v in champs_by_name.items()}

#our sample (courtesy of http://canisback.com/matchId/matchlist_na1.json) for now.
sample_matches = load_json("match_sample.json")

#our player sample (courtesy of make_player_sample() below + our sample matches)
sample_players = load_json("player_sample.json")

#our mastery-based character loyalty data (courtesy of mastery_loyalty() below)
#same index as player sample.
sample_loyalties = load_json_array("loyalty_sample.json")

#our ranked total for each player. (how many ranked games they've played this season)
sample_total_ranked = load_json_array("totalranked_sample.json")

#our best rank for each player (their highest rank of all their ranked queues)
sample_best_ranked = load_json_array("bestrank_sample.json")



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



#takes a python dict.
def mastery_loyalty(masteries):
	return masteries[0]['championPoints']/sum(m['championPoints'] for m in masteries)

#now I want more information from the "leagues" database.
#this is only about ranked matches.
#maybe "number of ranked matches played"
'''
{
	total_ranked = _ (how much ranked do you play)
	best_lp = _ (how good are you in your best queue)
}
'''

tiers = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
ranks = ["IV", "III", "II", "I"]

#tested
def numerical_ranking(league_entry):
	tier = league_entry['tier']
	rank = league_entry['rank']
	lp = league_entry['leaguePoints']
	return tiers.index(tier)*400 + ranks.index(rank)*100 + lp

#returns two lists
def league_info(summoner_id):
	r = get(leagues_by_summoner(summoner_id))
	if r.status_code == 200:
		leagues = r.json()
		total_ranked = sum(l['wins'] + l['losses'] for l in leagues)
		lps = [numerical_ranking(l) for l in leagues]
		best_lp = max(lps) if len(lps) > 0 else 0
		return total_ranked, best_lp
	else:
		print("league info got status code {r.status_code}")

def unzip(list_of_tuples):
	return list(map(list, zip(*list_of_tuples)))

def league_info_many(summoner_ids):
	return unzip(map(league_info, summoner_ids))


'''misc tests'''
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
		





