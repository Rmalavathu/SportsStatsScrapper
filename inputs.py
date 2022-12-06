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

def get_type_of_stat():
    valid = True
    while valid:
        name = input("Averages or Game Log: ").lower()
        if (name == "averages"):
            return name, "none"
        elif name == "game log":
            while True:
                type_log = input("Entire Season Game Log or Last 5 games? Input \"all\" or \"5\": ").lower()
                if (type_log == "all") or (type_log == "5"):
                    return name, type_log
                else:
                    print("INVALID TYPE")
                    print("Please input either \"all\" or \"5\"")
        else:
            print("INVALID TYPE")
            print("Please input either \"Averages\" or \"Game Log\"")

def get_stats_or_predict(s):
    while True:
        name = input(f"Stats or Predict {s}: ").lower()
        if ( name == "stats" or name == "predict"):
            return name
        else:
            print("INVALID INPUT")
            print("Please input either \"Stats\" or \"Predict\"")