
import re
import requests
import json

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

def get(url):
	def with_auth(r):
		r.headers["X-Riot-Token"] = api_key
		return r
	return requests.get(url, auth=with_auth)

def match(id):
	return f"https://na1.api.riotgames.com/lol/match/v4/matches/{id}"

#/lol/champion-mastery/v4/champion-masteries/by-summoner/{encryptedSummonerId}
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


test_matches = [get(match(i)).json() for i in sample_matches[10:20]]
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
		time.sleep()
		





