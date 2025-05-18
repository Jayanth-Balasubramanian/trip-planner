from enum import Enum

import requests


class Locations(Enum):
    PRK = 1  # parakode
    THM = 2  # thenmala
    JAT = 3  # jatayupara
    VRK = 4  # varkala
    NEY = 5  # neyyar
    PON = 6  # ponmudi
    ALP = 7  # Alleppey
    KOC = 8  # Kochi


API_KEY = "YOUR_API_KEY"


# TODO: get real maps data
def get_locations():
    LOCATIONS = {
        "Parakode, Kerala",
        "Thenmala, Kerala",
        "Jatayu Earth Center, Kerala",
        "Varkala, Kerala",
        "Neyyar Dam, Kerala",
        "Ponmudi, Kerala",
        "Alleppey, Kerala",
        "Kochi, Kerala",
    }

    addresses = list(LOCATIONS.values())
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    params = {
        "origins": "|".join(addresses),
        "destinations": "|".join(addresses),
        "key": API_KEY,
        "mode": "driving",
    }
    response = requests.get(url, params=params).json()


ROOT = Locations.PRK
END = Locations.ALP

MOCK_DISTANCES = [
    [0, 30, 20, 60, 65, 60, 80, 105],  # PRK
    [30, 0, 35, 70, 60, 50, 95, 120],  # THM
    [20, 35, 0, 55, 75, 65, 85, 110],  # JAT
    [60, 70, 55, 0, 50, 70, 90, 120],  # VRK
    [65, 60, 75, 50, 0, 30, 110, 135],  # NEY
    [60, 50, 65, 70, 30, 0, 120, 145],  # PON
    [80, 95, 85, 90, 110, 120, 0, 60],  # ALP
    [105, 120, 110, 120, 135, 145, 60, 0],  # KOC
]
MAX_LEG = 150
NUM_DAYS = 5
# locations we can't stay in have a dummy large cost
STAY_COST: dict[Locations, float] = {i: 10**9 for i in Locations}
STAY_COST[Locations.PRK] = 0
STAY_COST[Locations.VRK] = 10**4
MAX_NON_STAY_PER_DAY = 2
MIN_NON_STAY_PER_DAY = 1
RUPEES_PER_KM = 100 / 10
TOTAL_LOCS = len(Locations)
MAX_COST_ESTIMATE = 6 * 10**4  # for normalizing
