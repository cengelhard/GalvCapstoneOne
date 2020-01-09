
import re
import requests
import json
from datetime import datetime
import time
import numpy as np
from numpy.polynomial.polynomial import polyfit
from scipy import stats
import matplotlib.pyplot as plt
import pandas as pd

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

#makes an API call and corrects for rate limits. May stall for 2 minutes.
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

def summoner_by_id(summoner_id):
	return f'https://na1.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}'

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
n = len(sample_players)

#our mastery-based character loyalty data (courtesy of mastery_loyalty() below)
#same index as player sample.
sample_loyalties = load_json_array("loyalty_sample.json")

#our ranked total for each player. (how many ranked games they've played this season)
sample_total_ranked = load_json_array("totalranked_sample.json")

#our best rank for each player (their highest rank of all their ranked queues)
sample_best_ranked = load_json_array("bestrank_sample.json")

#summoner level for each player
sample_levels = load_json_array("levels_sample.json")

#each player's favorite champ
sample_favs = load_json_array("favs_sample.json")

#players who like each champion class based on their fav:
classes = ['Fighter', 'Assassin', 'Mage', 'Support', 'Tank', 'Marksman']
#indecies of players, not their id.
#contains sets of indecies.
players_by_class = {clss: set(i for i,p in enumerate(sample_players) if (clss in champs[str(sample_favs[i])]['tags'])) for clss in classes}



#some categories
Yasuo_mains = set(i for i,p in enumerate(sample_players) if sample_favs[i] == 157)

hardcore_players = set(i for i,t in enumerate(sample_total_ranked) if t > 1500)
casual_players = set(i for i,t in enumerate(sample_total_ranked) if t < 10)

fan_children = set(i for i,l in enumerate(sample_loyalties) if l > .5)
dabblers = set(i for i,l in enumerate(sample_loyalties) if l < .2)

support_players = set(i for i in range(n) if ((i in players_by_class['Support']) or (i in players_by_class['Tank'] and not (i in players_by_class['Fighter']))))

def category_bools(category):
	return [(i in category) for i in range(n)]

def class_main_bools(clss):
	mains = players_by_class[clss]
	return [(i in mains) for i in range(n)]

playerDF = pd.DataFrame({
	'summonerId': sample_players,
	'level': sample_levels,
	'loyalty': sample_loyalties,
	'totalRanked': sample_total_ranked,
	'bestRanked': sample_best_ranked,
	'fav': list(map(str,sample_favs)),
	'fighter': class_main_bools('Fighter'),
	'mage': class_main_bools('Mage'),
	'assassin': class_main_bools('Assassin'),
	'support': class_main_bools('Support'),
	'marksman': class_main_bools('Marksman'),
	'tank': class_main_bools('Tank'),
	'yasuo': category_bools(Yasuo_mains),
	'controlledRank': sample_best_ranked / sample_total_ranked,
	'supportPlayer': category_bools(support_players),
	#'hardcore': category_bools(hardcore_players),
	#'casual': category_bools(casual_players)
})

#playerDF = playerDF[playerDF.totalRanked != 0]


'''
champion dataframe
'''
#win rate
#play rate
#classes
#gender?



'''
team/match dataframe
'''
#win
#first dragon
#game length?
#number of unique classes on team
#total rank of players
#total other things of players


def likes_class(player_index, clss):
	#return clss in champs[str(sample_favs[player_index])]['tags']
	return player_index in players_by_class[clss]


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

def summoner_level(summoner_id):
	r = get(summoner_by_id(summoner_id))
	if r.status_code == 200:
		return r.json()['summonerLevel']
	else:
		print(f"something went wrong getting summoner level: {r.status_code}")

def save_as_json(data, filename):
	with open(filename, 'w') as outfile:
		json.dump(data, outfile)



#takes a python dict.
def mastery_loyalty(masteries):
	return masteries[0]['championPoints']/sum(m['championPoints'] for m in masteries)

def favorite_champ(masteries):
	return masteries[0]['championId']



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

def tier_color(num_rank):
	return [(.4,.4,.5), (.8,.5,.2), (.7,.7,.7), (.8,.8,.2), (.1,.8,.5), (.7,.8,.9), (0,0,0)][num_rank // 400]

tier_color_sample = np.array([tier_color(r) for r in sample_best_ranked])

def color_by_category(category):
	return np.array(["blue" if (i in category) else "red" for i in range(n)])

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


'''
graphs
'''
player_set = set(sample_players)
idset = set(range(len(sample_players)))

#for quick graphs
def graph(x,y, **kwargs):
	fig, ax = plt.subplots()
	logx = kwargs.get('logx')
	xlabel = kwargs.get('xlabel')
	ylabel = kwargs.get('ylabel')
	fitline = kwargs.get('fitline')

	if logx:
		ax.set_xscale("log")
	if xlabel:
		ax.set_xlabel(xlabel)
	if ylabel:
		ax.set_ylabel(ylabel)

	mask = np.isfinite(x) & np.isfinite(y)
	kwarg_color = kwargs.get('c')
	c = kwarg_color if kwarg_color is not None else tier_color_sample

	c = c[mask]
	x = x[mask]
	y = y[mask]

	ax.scatter(x,y,c=c)

	if fitline:
		b, m = polyfit(x, y, 1)
		ax.plot(x, b+m*x, '-')

	return ax

def graph_from_df(x, y, **kwargs):
	kwargs['xlabel'] = x
	kwargs['ylabel'] = y
	return graph(playerDF[x].to_numpy(), playerDF[y].to_numpy(), **kwargs)


def graph_by_class(ax,x,y,clss):
	lovers = players_by_class[clss]
	haters = idset - lovers
	print(len(lovers), len(haters))
	size = .1
	ax.scatter([x[i] for i in lovers], [y[i] for i in lovers], color="blue", s = size*1.5)
	ax.scatter([x[i] for i in haters], [y[i] for i in haters], color="red", s = size)
	ax.set_title(clss)
	return ax

def graph_by_all_classes(x, y):
	fig, axs = plt.subplots(2,3)
	axs = axs.flatten()
	for i,ax in enumerate(axs):
		graph_by_class(ax, x, y, classes[i])
	return axs

def graph_by_Yasuo_mains(x, y):
	fig, ax = plt.subplots()
	ax.scatter(x,y,color="blue", s=2)
	ax.scatter([x[i] for i in Yasuo_mains], [y[i] for i in Yasuo_mains], color="red", s=3)
	return ax




