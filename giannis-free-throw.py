
### All NBA web scraping code adapted from jman4190 (John Mannelly) on GitHub: 
### https://github.com/Jman4190/NBAPlayByPlay/blob/main/free-throw-time-elapsed.py
import requests
import pandas as pd
import numpy as np
import io
from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
plt.style.use('default')

# Prep pbp data scraping
headers  = {
    'Connection': 'keep-alive',
    'Accept': 'application/json, text/plain, */*',
    'x-nba-stats-token': 'true',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36',
    'x-nba-stats-origin': 'stats',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-Mode': 'cors',
    'Referer': 'https://stats.nba.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
}

play_by_play_url = "https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_0042000404.json"
response = requests.get(url=play_by_play_url, headers=headers).json()
play_by_play = response['game']['actions']

# Get 2021-2022 Bucks pbp data
bucks22 = pd.DataFrame(play_by_play)

gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=['2021-22'], 
                                              league_id_nullable='00', 
                                              season_type_nullable='Regular Season',
                                              player_id_nullable='203507')
games = gamefinder.get_data_frames()[0]

game_ids = games['GAME_ID'].unique().tolist()

def get_data(game_id):
    play_by_play_url = "https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_"+game_id+".json"
    response = requests.get(url=play_by_play_url, headers=headers).json()
    play_by_play = response['game']['actions']
    bucks22 = pd.DataFrame(play_by_play)
    bucks22['gameid'] = game_id
    return bucks22

buckspbpdata = []
for game_id in game_ids:
    game_data = get_data(game_id)
    buckspbpdata.append(game_data)
    
bucks22 = pd.concat(buckspbpdata, ignore_index=True)

# Get 2020-2021 Bucks pbp data
bucks21 = pd.DataFrame(play_by_play)

gamefinder = leaguegamefinder.LeagueGameFinder(season_nullable=['2020-21'], 
                                              league_id_nullable='00', 
                                              season_type_nullable='Regular Season',
                                              player_id_nullable='203507')
games = gamefinder.get_data_frames()[0]

game_ids = games['GAME_ID'].unique().tolist()

def get_data(game_id):
    play_by_play_url = "https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_"+game_id+".json"
    response = requests.get(url=play_by_play_url, headers=headers).json()
    play_by_play = response['game']['actions']
    bucks21 = pd.DataFrame(play_by_play)
    bucks21['gameid'] = game_id
    return bucks21

buckspbpdata = []
for game_id in game_ids:
    game_data = get_data(game_id)
    buckspbpdata.append(game_data)
    
bucks21 = pd.concat(buckspbpdata, ignore_index=True)

# Filter only Giannis free throws
giannis22ft = bucks22[(bucks22['personId'] == 203507) & (bucks22['actionType'] == 'freethrow')]
giannis21ft = bucks21[(bucks21['personId'] == 203507) & (bucks21['actionType'] == 'freethrow')]

# Get ft % by quarter
### Code adapted from user exp1orer on StackOverflow: https://stackoverflow.com/questions/23377108/pandas-percentage-of-total-with-groupby
ftct22 = giannis22ft.groupby(['period','shotResult']).count()['actionNumber']
ftper22 = ftct22.groupby(level=0).apply(lambda x: 100 * x / float(x.sum()))

ftct21 = giannis21ft.groupby(['period','shotResult']).count()['actionNumber']
ftper21 = ftct21.groupby(level=0).apply(lambda x: 100 * x / float(x.sum()))

# Get time between 1st and 2nd free throws
### All "time between free throws" code adapted from jman4190 (John Mannelly) on GitHub: 
### https://github.com/Jman4190/NBAPlayByPlay/blob/main/free-throw-time-elapsed.py

# Get 2021-2022 time between free throws data
giannis22fttime = giannis22ft.sort_values(by=['gameid', 'orderNumber'])
giannis22fttime['dtm'] = giannis22fttime['timeActual'].astype('datetime64[s]')
giannis22fttime['ptm'] = giannis22fttime['dtm'].shift(1)
giannis22fttime['elp'] = (giannis22fttime['dtm'] - giannis22fttime['ptm']).astype('timedelta64[s]')
giannis22fttime['pact'] = giannis22fttime['actionType'].shift(1)
giannis22fttime['psub'] = giannis22fttime['subType'].shift(1)
giannis22fttime['pmake'] = giannis22fttime['shotResult'].shift(1)
giannis22fttime[giannis22fttime['elp'] > 0]
giannis22fttime = giannis22fttime[['gameid',
                     'clock',
                     'actionNumber',
                     'orderNumber',
                     'subType',
                     'pact',
                     'psub',
                     'dtm',
                     'ptm',
                     'pmake',
                     'elp',
                     'personId',
                     'playerNameI',
                     'shotResult',
                     'period']]

giannis22fttime = giannis22fttime[(giannis22fttime.subType == '2 of 2') | (giannis22fttime.subType == '3 of 3')]
giannis22fttime = giannis22fttime[(giannis22fttime.elp > 0) & (giannis22fttime.elp < 40)]
ave22 = giannis22fttime['elp'].mean()

# Get 2020-2021 time between free throws data
giannis21fttime = giannis21ft.sort_values(by=['gameid', 'orderNumber'])
giannis21fttime['dtm'] = giannis21fttime['timeActual'].astype('datetime64[s]')
giannis21fttime['ptm'] = giannis21fttime['dtm'].shift(1)
giannis21fttime['elp'] = (giannis21fttime['dtm'] - giannis21fttime['ptm']).astype('timedelta64[s]')
giannis21fttime['pact'] = giannis21fttime['actionType'].shift(1)
giannis21fttime['psub'] = giannis21fttime['subType'].shift(1)
giannis21fttime['pmake'] = giannis21fttime['shotResult'].shift(1)
giannis21fttime[giannis21fttime['elp'] > 0]
giannis21fttime = giannis21fttime[['gameid',
                     'clock',
                     'actionNumber',
                     'orderNumber',
                     'subType',
                     'pact',
                     'psub',
                     'dtm',
                     'ptm',
                     'pmake',
                     'elp',
                     'personId',
                     'playerNameI',
                     'shotResult',
                     'period']]

giannis21fttime = giannis21fttime[(giannis21fttime.subType == '2 of 2') | (giannis21fttime.subType == '3 of 3')]
giannis21fttime = giannis21fttime[(giannis21fttime.elp > 0) & (giannis21fttime.elp < 40)]
ave21 = giannis21fttime['elp'].mean()

# Do 5-game moving average of Giannis' ft % for 2020-2021 compared to 2021-2022
### Data obtained from basketball-reference.com
gameft22 = pd.read_csv('giannis-ft-2021-2022.csv')
gameft21 = pd.read_csv('giannis-ft-2020-2021.csv')

gameft22 = gameft22.dropna(subset = ['G'])
gameft21 = gameft21.dropna(subset = ['G'])

# Convert ft% to float
gameft22['FT%'] = gameft22['FT%'].astype(float) * 100
gameft21['FT%'] = gameft21['FT%'].astype(float) * 100

# Create moving average
gameft22['5GameAve'] = gameft22['FT%'].rolling(window = 5).mean()
gameft21['5GameAve'] = gameft21['FT%'].rolling(window = 5).mean()

# Plot ft % over season
# ax = plt.gca()
# gameft22.plot(kind = 'line', x = 'G', y = 'FT%', ax=ax)
# gameft22.plot(kind = 'line', x = 'G', y = '5GameAve', ax=ax)
# plt.show()

# ax = plt.gca()
# gameft21.plot(kind = 'line', x = 'G', y = 'FT%', ax=ax)
# gameft21.plot(kind = 'line', x = 'G', y = '5GameAve', ax=ax)
# plt.show()

# Combine 2020-2021 and 2021-2022 seasons
gameftmerge = pd.merge(gameft21, gameft22, how = "outer", on = 'G')
gameftmerge = gameftmerge.rename(columns = {'5GameAve_x': '2020-2021', '5GameAve_y': '2021-2022'})


# Plot both years ft % over season
ax = plt.gca()
gameftmerge.plot(kind = 'line', x = 'G', y = '2020-2021', ax=ax,
                 color = '#702F8A', linewidth = 2.5, alpha = .9)
gameftmerge.plot(kind = 'line', x = 'G', y = '2021-2022', ax=ax,
                 color = '#00471B', linewidth = 2.5, alpha = .9)
plt.title("Giannis' Free Throw Percentage (5 Game Moving Average)")
plt.xlabel('Games', fontsize = 12)
plt.ylabel('Free Throw %', fontsize = 12)
plt.show()

# Plot ft % by quarter by season
ftperquarter = pd.merge(ftper21, ftper22, left_index = True, right_index = True)
ftperquarter = ftperquarter.reset_index()
ftperquarter = ftperquarter[ftperquarter['shotResult'] == 'Made']
ftperquarter = ftperquarter.rename(columns = {'actionNumber_x': '2020-2021', 'actionNumber_y': '2021-2022', 'period': 'Quarter'})

ftplot = ftperquarter.plot(kind = 'bar', x = 'Quarter', y = ['2020-2021', '2021-2022'], 
                           color = ['#702F8A','#00471B'], width = 0.7)
ftplot.set_title("Giannis' Free Throw % by Quarter", fontsize = 16)
ftplot.set_ylabel('Free Throw %', fontsize=12)
ftplot.set_xlabel('Quarter', fontsize=12)
ftplot.tick_params(axis='x', labelrotation = 0)
for p in ftplot.patches:
    ftplot.annotate("%.1f" % p.get_height(), (p.get_x() + p.get_width() / 2., 
                                              p.get_height()), ha='center', 
                    va='center', xytext=(0, -10), textcoords='offset points', 
                    color = 'white', weight = 'bold')

# Plot ft time distribution
giannisfttime = pd.merge(giannis22fttime['elp'].reset_index(), 
                         giannis21fttime['elp'].reset_index(), 
                         left_index = True, right_index = True, how = 'outer')[['elp_x','elp_y']]

# Plot ft time distribution
ax = plt.gca()
giannisfttime['elp_x'].hist(bins = 16, ax=ax, alpha = 0.75, color = '#00471B')
giannisfttime['elp_y'].hist(bins = 16, ax=ax, alpha = 0.65, color = '#702F8A')
plt.title("Giannis' Time Between 1st and 2nd Free Throws")
plt.xlabel('Number of Seconds')
plt.ylabel('Number of Free Throws')
green_patch = mpatches.Patch(color='#00471B', label='2021-2022')
purple_patch = mpatches.Patch(color='#702F8A', label='2020-2021')
plt.legend(handles=[purple_patch, green_patch])
plt.show()