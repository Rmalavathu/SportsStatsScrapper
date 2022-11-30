from bs4 import BeautifulSoup
import requests
import pandas as pd


def create_nfl_ids_csv():
    url = 'https://www.pro-football-reference.com'
    year = 2022

    r = requests.get(url + '/years/' + str(year) + '/fantasy.htm')
    soup = BeautifulSoup(r.content, 'html.parser')
    parsed_table = soup.find_all('table')[0]

    pro_football_reference_ids = dict()

    for i, row in enumerate(parsed_table.find_all('tr')[2:]):
        try:
            dat = row.find('td', attrs={'data-stat': 'player'})
            name = dat.a.get_text()
            stub = dat.a.get('href')
            pro_football_reference_ids[name] = stub

        except:
            pass
    df = pd.DataFrame(pro_football_reference_ids.items(), columns=["name", "PFRID"])

    df.to_csv("nfl_ids_2022.csv", index=False)
