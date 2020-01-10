# Champion Loyalty In League Of Legends
![LoL](/Lol_cover_image.jpg?raw=true "LoL")

Charlie Engelhard


# Background

League of Legends (LoL) is a popular computer game by Riot Games in which two teams of five players compete to destroy one another's base. Each player picks a "champion" from a pool of about 150 in-game characters, each with unique abilities and powers. LoL has around 100 million active players, and the most recent world championship tournament had a prize of $1 million for the winning team. 

As a competitive game, LoL players are greatly concerned with their in-game rank, and how they can increase it. Rank for a particular player goes up when that player is on a team that wins and down when that player is on a team that loses. 

There is a particular superstition among the players, including many professional-level players, that you can rise in rank faster if you pick a favorite champion and stick with it. This makes intuitive sense to many players, but I want to find out if it can be backed up by data.

Ranks are divided into tiers which are color coded in most of my charts. The tiers included in my data set are Iron, Bronze, Silver, Gold, Platinum, and Diamond. There are tiers higher than Diamond, but they have very low populations and did not appear in my sample. Note that Platinum is represented by a greenish color to avoid confusing it with Iron and Gold.

Each tier is divided into ranks from IV (worst) to I (best). And then each rank has a number of "league points" from 0 to 100, which is used to go up ranks and tiers. I converted Riot's rank system into a single number using the following forumula:

```
tiers = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"]
ranks = ["IV", "III", "II", "I"]

#tested
def numerical_ranking(league_entry):
	tier = league_entry['tier']
	rank = league_entry['rank']
	lp = league_entry['leaguePoints']
	return tiers.index(tier)*400 + ranks.index(rank)*100 + lp
```
It is also worth mentioning that a player's "best rank" as used in this study is their highest rank among ranked queues that they've participated in. (There are different queues for different maps, and for pre-made teams vs assigned teams for solo players.)

# Data Description

I used the Riot games API to obtain most of my data. One exception was my initial sample of matches, which was generated through a random walk of the graph of matches and players, from the website http://canisback.com/matchId/matchlist_na1.json. (This data is recalculated every 2 days or so.)

I took my sample of 1000 players from this list of matches. 

I tested this data set to see how representative of the population it was. The rank distribution matches calculations made by several other websites: op.gg, esportstales.com, leagueofgraphs.com. Although Riot doesn't publish their own calculations, there appears to be a consensus from users of the API.
![Rank histogram](/rank_histo.png?raw=true "Rank histogram")

Note the peaks in population. This is probably due to players quitting ranked matches as soon as they reach a threshold for getting a reward, and players who are almost to a threshold working extra hard to pass it.

However, because the matches are all recent, it has a bias towards currently active players. It also seems to bias towards players who play many ranked games, which is fortunate for my purposes. The data is entirely from the North American servers.

# Data Processing

My first task was to define a statistic representing a player's loyalty to their favorite champion. The API provides a list of all champions that a player has played, and assignes a "mastery score" to each. Mastery score is affected by many things: how many matches the player has completed with the champion, how well they performed in those matches, and other factors listed on this wiki page: https://leagueoflegends.fandom.com/wiki/Champion_Mastery

I decided to use champion mastery as an estimation of the player's preference for a particular champion because it's what Riot and the players use, and because if I were to loop through each player's match history and calculate my own preference value, this would be hindered by the rate limits on the API. (Making 1000 API calls is rate limited to about 20 minutes, so multiply that by the number of matches to look back on, and we have a situation.)

To calculate "loyalty", I divided the mastery score of a player's highest scored champion by the total mastery score of all champions that player has used, producing a number in the range 0.0 to 1.0. 


# Initial results
![Loyalty vs Rank](/loyalty_v_rank.png?raw=true "Loyalty vs Rank")

The chart above shows that naively, the superstition of players appears to be incorrect. There is actually a weak negative correlation between loyalty and rank. Why might this be? Surely, practicing more with a champion should lead to more skill. 

My theory is that because LoL is a team game, it is important to pick your champion based on your teammates' and opponents' choices. When a player tries to bullheadedly force a particular champion into a matchup that is not suited to that champion, it not only affects that player's performance, but can also cause strife within the team. Perhaps flexibility is just as important as specialized practice. A player who allows their 4 teammates to play their favorite champion by picking a champion that compliments them may have a better chance of winning than a player who always plays their own favorite.

But in the interest of honesty, I considered counter arguments based on further exploration of the data.

# What actually does correlate with rank?

I calculated many more statistics that I thought might correlate with rank. Champions are categorized by Riot into 1 or 2 of 6 different classes (Fighter, Tank, Mage, Assassin, Support, Marksman), and I wasn't able to find a correlation between these and rank. I also tried to isolate Yasuo players (Yasuo is the most popular favorite champion, and is somewhat infamous in the community) but was not able to find anything interesting. I also looked at "summoner level", which is a representation of how much the player has played the game, and this correlated too strongly with total number of matches played to draw any new conclusions. (0.72) 

The strongest correlation to rank that I could find was unsurprising: number of ranked games played. (0.32)
![Total vs Rank](/total_v_rank.png?raw=true "Total vs Rank")

But lo! Number of ranked games played also negatively correlates with loyalty. 
![Loyalty vs Total](/loyalty_v_total.png?raw=true "Loyalty vs Total")

The more games a player plays, the more variety of champions they tend to have used. This includes players who are "serial monogamists", who stick to one champion at a time, but have changed which champion this is in the past. 

# Loyalty revisited

It could be argued that because loyalty correlates negatively with number of games played, and number of games played correlates strongly with rank, that we need to control our variable better.

So I defined a new statistic called "controlledRank" which is equal to the player's rank divided by the number of games played. This number represents the increase in rank per game played. This may be a better representation of how loyalty affects performance.
![Loyalty vs ControlledRank](/loyalty_v_controlledRank.png?raw=true "Loyalty vs ControlledRank")

In this figure, the data appears to confirm the superstition of players, but the correlation is weak.

# Conclusion

If I were to convert my findings into advice for players, I think it would be this: stick to a single champion when you are first starting out. When controlled for number of games played, loyalty seems to help. However, as you play more games, you should diversify and choose your champion based on strategy rather than forcing your favorite into the game.

But truly, the only statistic I found that had a significant correlation to rank was number of games played. So perhaps the best advice is to keep practicing and don't worry about it.