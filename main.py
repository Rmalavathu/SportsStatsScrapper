import requests
import time
import pandas as pd
from requests_html import HTMLSession
import csv
from bs4 import BeautifulSoup
from nfl_player_ids import *
from inputs import *

import warnings

#https://github.com/djblechn-su/nba-player-team-ids


def starting_messages():
    print("		  	   SPORTS STATS MACHINE")
    print("\t\t\t\tby Rohan Malavathu\n\n")

    print("This program will allow to get player stats for either NBA or NFL.")
    print("First, input the sport you want and after input the player you want")
    print("to get stats. After that, if you want to get players stats from each")
    print("games type \"game log\" then select whether you want all the games \"all\"")
    print("or just the last 5 games using \"5\", and get use \"average\" to get ")
    print("player averages. For football players, you get the option to get stats or")
    print("predict the players rushing yards they have a player line on draftkings.")
    print("At the end it will ask if you want to restart which is answered with a ")
    print("\"Yes\" or \"No\".\n")

def clean_nba_ids():
    df = pd.read_csv('NBA_Player_IDs.csv')
    df_clean = df.dropna()
    df_clean = df_clean.astype({'ESPNID':'int'})
    df_clean.to_csv("NBA_Player_IDs_clean.csv", index=False)

def create_nba_dictionary():
    df = pd.read_csv("NBA_Player_IDs_clean.csv")
    df['ESPNName'] = df['ESPNName'].str.upper()
    dictionaryID = df.set_index('ESPNName').T.to_dict('list')
    return dictionaryID

def create_nfl_dictionary():
    df = pd.read_csv("nfl_ids_2022.csv")
    df['name'] = df['name'].str.upper()
    dictionaryID = df.set_index('name').T.to_dict('list')
    return dictionaryID

def scrape_nba(name, nba, type, type_len, printing):

    if (type == "game log"):
        id = nba[name]

        URL = "https://www.espn.com/nba/player/gamelog/_/id/" + str(int(id[0]))
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, "html.parser")

        job_elements = soup.find_all(class_="Table__TD")

        gameStats = []
        seasonStats = []
        gameInfo = "Date, Opp, Result, MIN, FG, FG%, 3PT, 3P%, FT, FT%, REB, AST, BLK, STL, PF, TO, PTS".split(', ')
        months =  ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september', 'october', 'november', 'december']
        for job_element in job_elements:
            temp = job_element.text

            if temp == "october":
                break

            if "/" in temp:
                seasonStats.append(gameStats)
                gameStats = []
                gameStats.append(temp)
                addd = True
            else:
                if (temp.lower() in months):
                    addd = False
                if addd:
                    gameStats.append(temp)

        seasonStats = seasonStats[1:]

        stats = pd.DataFrame(data=seasonStats, columns=gameInfo)

        stats.set_index('Date', inplace=True, drop=True)

        if printing:
            if (type_len == "5"):
                print(stats.head(5))
            else:
                print(stats)
    else:
        id = nba[name]

        URL = "https://www.espn.com/nba/player/stats/_/id/" + str(int(id[0]))
        page = requests.get(URL)

        soup = BeautifulSoup(page.content, "html.parser")

        job_elements = soup.find_all( class_ ="Table__TBODY")[1]

        limit = len(job_elements) - 2
        i = 0
        for x in job_elements:
            if (i == limit):
                averages = x
            i += 1

        average_stats = ['2022-2023']
        for y in averages:
            average_stats.append(y.text)

        headers = "SEASON, GP, GS, MIN, FG, FG%, 3PT, 3%, FT, FT%, OR, DR, REB, AST, BLK, STL, PF, TO, PTS".split(', ')

        stats = pd.DataFrame(data=average_stats)

        stats = stats.transpose()

        stats.columns = headers

        stats.set_index('SEASON', inplace=True, drop=True)

        if printing:
            print(stats)

    return stats

def scrape_nfl(name, nfl, type, type_len, printing):

    id = nfl[name]

    URL = "https://www.pro-football-reference.com" + str(id[0])

    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    header = soup.find_all('thead')[0]

    if (type != "averages"):
        i = 0
        for x in header:
            if (i == 3):
                headers = x.text
            i += 1

        headers_list = headers.strip("\n").split("\n")

        job_elements = soup.find_all('tbody')[0]

        complete_game_log = []
        temp = []

        for x in job_elements:
            for y in x:
                try:
                    temp.append(y.text)
                except:
                    complete_game_log.append(temp)
                    temp = []

        complete_game_log.pop()

        stats = pd.DataFrame(data=complete_game_log, columns=headers_list)

        stats.set_index('Week', inplace = True, drop=True)

        stats = stats.iloc[::-1]

        if printing:
            if (type_len == "5"):
                print(stats.head(5))
            else:
                print(stats)

        return stats
    else:

        job_elements2 = soup.find_all('tbody')[1]

        limit = len(job_elements2) - 2;
        i = 0
        for x in job_elements2:
            if (i == limit):
                averages = x
            i += 1

        average_stats = []
        for y in averages:
            average_stats.append(y.text)

        header = soup.find_all('thead')[1]


        i = 0
        for x in header:
            if (len(x.text) > 100):
                headers2 = x.text
            i += 1

        headers_temp = headers2.strip("\n")
        headers_list = (headers_temp.split(" "))[1:]
        headers_list.pop()

        stats2 = pd.DataFrame(data=average_stats)

        stats2 = stats2.transpose()

        stats2.columns = headers_list

        stats2.set_index('Year', inplace=True, drop=True)

        if printing:
            print(stats2)

        return stats2

def nba_predict_points(name, nba):
    urls = "https://sportsbook.draftkings.com/leagues/basketball/nba?category=player-props&subcategory=points"

    page = requests.get(urls)
    soup = BeautifulSoup(page.content, "html.parser")
    #print(soup)

    elements = soup.find_all(class_ = "sportsbook-table__body")

    lines = []
    i = 0
    good = False
    is_prediction = False

    my_val = 0.0

    for x in elements:
        for y in x:
            temp = []
            i = 0.0
            for w in y:
                z = str(w.text)
                if (i == 0):
                    temp.append(z.upper())
                    if z.upper() == name:
                        good = True
                        is_prediction = True
                if (i == 1):
                    try:
                        temp.append(z[z.index(chr(160)) + 1:z.index(chr(8722))])
                    except:
                        temp.append(z[z.index(chr(160)) + 1:z.index(chr(43))])
                    if good:
                        try:
                            temp.append(z[z.index(chr(160)) + 1:z.index(chr(8722))])
                            my_val = float(temp[1])
                        except:
                            temp.append(z[z.index(chr(160)) + 1:z.index(chr(43))])
                            my_val = float(temp[1])
                i += 1
            lines.append(temp)
            good = False

    if is_prediction:

        data = scrape_nba(name.upper(), nba, "game log", "all", False)

        points_data = data["PTS"]

        count = 0
        for y in points_data.tail(10):
            if (int(y) >= my_val):
                count += 1

        if(count >6):
            print(f'\nThe {name} got over {my_val} points {count} times. Since, they went over the prediction 7 or more times we can assume they will go OVER {my_val} points in the following week')
        elif (count > 3):
            print(f'\nThe {name} got over {my_val} points {count} times. Since, they went over the prediction 4-6 times we are UNSURE if they will go over or below {my_val} points in the following week')
        else:
            print(f'\nThe {name} got over {my_val} points {count} times. Since, they went over the prediction 3 or less times we can assume they will go BELOW {my_val} points in the following week')
    else:
        print("Player doesn't have a projected line available")

def nfl_predict_rushing(name, nfl):

    urls = "https://sportsbook.draftkings.com/leagues/football/nfl?category=rush/rec-props&subcategory=rush-yds"

    page = requests.get(urls)
    soup = BeautifulSoup(page.content, "html.parser")
    #print(soup)

    elements = soup.find_all(class_ = "sportsbook-table__body")

    lines= []
    i = 0
    good = False
    is_prediction = False

    my_val = 0.0

    for x in elements:
        for y in x:
            temp = []
            i = 0.0
            for w in y:
                z = str(w.text)
                if(i == 0):
                    temp.append(z.upper())
                    if z.upper() == name:
                        good = True
                        is_prediction = True
                if (i == 1):
                    try:
                        temp.append(z[z.index(chr(160))+1:z.index(chr(8722))])
                    except:
                        temp.append(z[z.index(chr(160))+1:z.index(chr(43))])
                    if good:
                        try:
                            temp.append(z[z.index(chr(160)) + 1:z.index(chr(8722))])
                            my_val = float(temp[1])
                        except:
                            temp.append(z[z.index(chr(160)) + 1:z.index(chr(43))])
                            my_val = float(temp[1])
                i += 1
            lines.append(temp)
            good = False

    if is_prediction:

        data = scrape_nfl(name.upper(), nfl, "game log", "all", False)
        data['Rush'] = data["Rush"].astype('int')

        rushing_data = data.iloc[:,data.columns.get_loc("Rush")+1]

        count = 0
        for y in rushing_data.tail(10):
            if (int(y) >= my_val):
                count += 1

        if(count >6):
            print(f'\nThe {name} got over {my_val} yards {count} times. Since, they went over the prediction 7 or more times we can assume they will go OVER {my_val} yards in the following week')
        elif (count > 3):
            print(f'\nThe {name} got over {my_val} yards {count} times. Since, they went over the prediction 4-6 times we are UNSURE if they will go over or below {my_val} yards in the following week')
        else:
            print(f'\nThe {name} got over {my_val} yards {count} times. Since, they went over the prediction 3 or less times we can assume they will go BELOW {my_val} yards in the following week')
    else:
        print("Player doesn't have a projected line available")

def main():

    starting_messages()

    warnings.filterwarnings('ignore')  # setting ignore as a parameter

    try:
        clean_nba_ids()
        create_nfl_ids_csv()
    except:
        pass

    nba_player_ids = create_nba_dictionary()
    nfl_player_ids = create_nfl_dictionary()

    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    completed = True
    while completed:
        sport = get_sport()
        player = get_name(sport, nfl_player_ids, nba_player_ids)
        if sport == "NFL":
            s_or_p = get_stats_or_predict("Rushing Yards")
            if (s_or_p == "stats"):
                stat_type, length_stat = get_type_of_stat()
                scrape_nfl(player, nfl_player_ids, stat_type, length_stat, True)
            else:
                nfl_predict_rushing(player, nfl_player_ids)
        if sport == "NBA":
            s_or_p = get_stats_or_predict("Points")
            if (s_or_p == "stats"):
                stat_type, length_stat = get_type_of_stat()
                scrape_nba(player, nba_player_ids, stat_type, length_stat, True)
            else:
                nba_predict_points(player, nba_player_ids)

        state = input("Want to continue? Input \"Yes\" or \"No\": ").lower()
        if(state == "no"):
            completed = False
            print("Thank you for using my stats machine")


if __name__ == "__main__":
    main()
