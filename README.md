# Champion Loyalty In League Of Legends

Charlie Engelhard

# Background

League of Legends (LoL) is a popular computer game in which two teams of five players compete to destroy one another's base. Each player picks a "champion" from a pool of about 150 in-game characters, each with unique abilities and powers. LoL has around 100 million active players, and the most recent world championship tournament had a prize of $1 million for the winning team. 

As a competitive game, LoL players are greatly concerned with their in-game rank, and how they can increase it. Rank for a particular player goes up when that player is on a team that wins and down when that player is on a team that loses. 

There is a particular superstition among the players, including many professional-level players, that you can rise in rank faster if you pick a favorite champion and stick with it. This makes intuitive sense to many players, but I want to find out if it can be backed up by data.

Ranks are divided into tiers which are color coded in most of my charts. The tiers included in my data set are Iron, Bronze, Silver, Gold, Platinum, and Diamond. There are tiers higher than Diamond, but they have very low populations and did not appear in my sample. Note that Platinum is represented by a greenish color to avoid confusing it with Iron and Gold.

# Data Description

I used the Riot games API to get most of my data. One exception was my initial sample of matches, which was generated through a random walk of the graph of matches and players, from the website http://canisback.com/matchId/matchlist_na1.json. (This data is recalculated every 2 days or so.)

I took my sample of 1000 players from this list of matches. 

I tested this data set to see how representative of the population it was. In terms of rank, it matches the figures that Riot publishes. However, because the matches are all recent, it appears to have a bias towards currently active players. It also seems to bias towards players who play many ranked games, which is fortunate for my purposes. The data is entirely from the North American servers.

# Data Processing

My first task was to define a statistic representing a player's loyalty to their favorite champion. The API provides a list of all champions that a player has played, and assignes a "mastery score" to each. Mastery score is affected by many things: how many matches the player has completed with the champion, how well they performed in those matches, and other factors listed on this wiki page: https://leagueoflegends.fandom.com/wiki/Champion_Mastery

I decided to use champion mastery as an estimation of the player's preference for a particular champion because it's what Riot and the players use, and because if I were to loop through each player's match history and calculate my own preference value, this would be hindered by the rate limits on the API. (Making 1000 API calls was rate limited to about 20 minutes, so multiply that by the number of matches to look back on, and we have a situation.)

To calculate "loyalty", I divided the mastery score of a player's highest scored champion by the total mastery score of all champions that player has used, producing a number in the range 0.0 to 1.0. 

# Initial results

![Loylty vs Rank](/loyalty_v_rank.png?raw=true "Loylty vs Rank")

The chart above shows that naively, the superstition of players appears to be incorrect. There is no strong correlation between champion loyalty and rank, and there is actually a weak negative correlation. Why might this be? Surely, practicing more with a champion should lead to more skill. 

My theory is that because LoL is a team game, it is important to pick your champion based on your teammates' and opponents' choices. When a player tries to bullheadedly force a particular champion into a matchup that is not suited to that champion, it not only affects that player's performance, but can also cause strife within the team. Perhaps flexibility is just as important as specialized practice. 

But in the interest of honesty, I considered counter arguments based on further exploration of the data.

# What actually does correlate with rank?

I calculated many more statistics that I thought might correlate with rank. Champions are categorized by Riot into up to 2 of 6 different champions, and I wasn't able to find a correlation between these and rank. I also looked at "summoner level", which is a representation of how much the player has played the game, and correlated too strongly with total number of matches played to be useful. 

The strongest correlation to rank that I could find was unsurprising: number of ranked games played.

But lo! Number of ranked games played also negatively correlates with loyalty. 

The more games a player plays, the more variety of champions they tend to have used. This includes players who are "serial monogamists", who stick to one champion at a time, but have changed which champion this is in the past. 

# Loyalty revisited

It could be argued that because loyalty correlates negatively with number of games played, and number of games played correlates strongly with rank, that we need to control our variable better.

So I defined a new statistic called "controlledRank" which is equal to the player's rank divided by the number of games played. This number represents how much rank on average a player gains per game played. This may be a better representation of how loyalty affects performance.

In this figure, the correlation appears to confirm the superstition of players, but the correlation is weak.

# Conclusion

If I were to convert my findings into advice for players, I think it would be this: stick to a single champion when you are first starting out. When controlled for number of games played, loyalty seems to help. However, as you play more games, you should diversify and choose your champion based on strategy rather than forcing your favorite into the game.

But truly, the only statistic I found that had a strong correlation to rank was number of games played. So perhaps the best advice is to keep practicing and don't worry about it.