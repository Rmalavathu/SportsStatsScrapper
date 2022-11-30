import requests

import pandas as pd

import csv

from bs4 import BeautifulSoup
from nfl_player_ids import *
import os.path
import re

import warnings

#https://github.com/djblechn-su/nba-player-team-ids


def starting_messages():
    print("		  	   SPORTS STATS MACHINE")
    print("\t\t\t\tby Rohan Malavathu\n\n")

    print("This program will allow to get player stats for either NBA or NFL.")
    print("First, input the sport you want and after input the player you want")
    print("to get stats. After that, if you want to get players stats from last")
    print("ten games type \"game log\", \"total\" for total season stats, and ")
    print("\"average\" to get player averages. Type \"reset\" to go back to the")
    print("start and restart the process.")

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

def get_sport():
    valid_sport = True
    while valid_sport:
        sport = input("Which sport do you want player stats from NFL or NBA?  Input \"NFL\" or \"NBA\": ").upper()
        if sport != "NFL" and sport != "NBA":
            print("INVALID SPORT")
            print("Please input either \"NFL\" or \"NBA\"")
        else:
            return sport
    return sport

def get_name(sport, nfl, nba):
    valid_name = True
    while valid_name:
        name = input("What player do you want stats from? Input full name: ").upper()
        if (sport == "NFL" and name in nfl) or (sport == "NBA" and name in nba):
            return name
        else:
            print("INVALID NAME")
            print("Please input the full name and make sure it is spelled correctly")
    return name

def scrape_nba(name, nba):

    id = nba[name]

    URL = "https://www.espn.com/nba/player/gamelog/_/id/" + str(int(id[0]))
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    job_elements = soup.find_all(class_="Table__TD")

    gameStats = []
    seasonStats = []
    gameInfo = ["Date, Opp, Result, MIN, FG, FG%, 3PT, 3%, FT, FT%, REB, AST, BLK, STL, PF, TO, PTS"]
    for job_element in job_elements:
        temp = job_element.text

        if "/" in temp:
            seasonStats.append(gameStats)
            gameStats = []
            gameStats.append(temp)
        else:
            gameStats.append(temp)

    print(seasonStats)

def scrape_nfl(name, nfl):

    id = nfl[name]

    URL = "https://www.pro-football-reference.com" + str(id[0])

    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    job_elements = soup.find_all('tbody')[0]

    for x in job_elements:
        for y in x:
            try:
                print(y.text)
            except:
                print("fail")

    #box_score = soup.find_all(id = )
    '''

    gameStats = []
    seasonStats = []
    gameInfo = ["Date, Opp, Result, MIN, FG, FG%, 3PT, 3%, FT, FT%, REB, AST, BLK, STL, PF, TO, PTS"]
    for job_element in job_elements:
        temp = job_element.text

        if "/" in temp:
            seasonStats.append(gameStats)
            gameStats = []
            gameStats.append(temp)
        else:
            gameStats.append(temp)

    print(seasonStats)
    '''

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


    completed = True
    while completed:
        sport = get_sport()
        player = get_name(sport, nfl_player_ids, nba_player_ids)
        if sport == "NFL":
            scrape_nfl(player, nfl_player_ids)
        if sport == "NBA":
            scrape_nba(player, nba_player_ids)

if __name__ == "__main__":
    main()
