import json
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from dataclasses import dataclass
from typing import TypedDict

@dataclass
class Drop:
    member: str
    collection: int
    available_from: datetime | str
    sale_end: datetime | str

class CollectionCount(TypedDict):
    totalCount: int

MEMBERS = ["SeoYeon", "HyeRin", "JiWoo", "ChaeYeon", "YooYeon", "SooMin", "NaKyoung", "YuBin", "Kaede", "DaHyun", "Kotone", "YeonJi", "Nien", "SoHyun", "Xinyu", "Mayu", "Lynn", "JooBin", "HaYeon", "ShiOn", "ChaeWon", "Sullin", "SeoAh", "JiYeon"]

#region schedule generation
def generate_aram_schedule(collections:list[int], start_time:datetime, set_sale_duration: timedelta) -> list[Drop]:

    schedule: list[Drop] = []

    for collection in collections:
        for member in MEMBERS:
            schedule.append(
                Drop(
                    member,
                    collection,
                    start_time.isoformat().replace("+00:00", "Z"),
                    (start_time + set_sale_duration).isoformat().replace("+00:00", "Z")
                )
            )
    
    return schedule

def generate_number_schedule(collections:list[int], start_time:datetime, spacing:timedelta, set_sale_duration: timedelta) -> list[Drop]:
    
    schedule: list[Drop] = []

    for index, collection in enumerate(collections):
        collection_time = (start_time + (index * spacing))

        for member in MEMBERS:
            schedule.append(
                Drop(
                    member,
                    collection,
                    collection_time.isoformat().replace("+00:00", "Z"),
                    (collection_time + set_sale_duration).isoformat().replace("+00:00", "Z")
                )
            )
    return schedule

def generate_member_schedule(collections:list[int], start_time:datetime, cluster_size:int, member_spacing:timedelta, cluster_spacing:timedelta, reverse:bool=False):
    members = MEMBERS[::-1] if reverse else MEMBERS

    schedule: list[Drop] = []

    for member_index, member in enumerate(members):
        cluster = member_index // cluster_size
        position = member_index % cluster_size

        member_time = (
            start_time + (cluster * cluster_spacing) + (position * member_spacing)
        )

        for collection in collections:
            schedule.append(
                Drop(
                    member,
                    collection,
                    member_time.isoformat().replace("+00:00", "Z"),
                    (member_time + cluster_spacing).isoformat().replace("+00:00", "Z")
                )
            )
    return schedule

def get_sale_type() -> list[Drop]:

    ui = """What type of set do you need the data of?
    1. "All at once" sets (OT24 301-304, same time)
    2. "Number" sets (ex : OT24 301, then OT24 302, etc...)
    3. "Member" sets (ex : 101-108 Seoyeon, then 101-108 Hyerin, etc...)\nYour choice : """

    collections = get_set_lenght()
    start_time, sale_duration = get_timestamp()
    reverse_order = get_member_order()

    valid_answer = {
    1: lambda : generate_aram_schedule(collections, start_time, sale_duration),
    2: lambda : generate_number_schedule(collections, start_time, get_set_spacings(), sale_duration),
    3: lambda : generate_member_schedule(collections, start_time, get_cluster_size(), get_set_spacings(), get_cluster_spacings(), reverse_order),
    }

    while True:
        reply = int(input(ui))
        if reply in valid_answer:
            break
        else:
            print("Ik you'd want a \"Jaden sale\" option, but that's sadly available sorry :JadenSip:\n")

    schedule = valid_answer[reply]()

    return schedule

def get_set_lenght() -> list[int]:

    ui = """What type of set do you need the data of?
    1. FCO 1st Edition
    2. FCO 2nd Edition
    3. FCO 3rd Edition
    4. DCO/others Objekts\nYour choice : """

    ui_dcos = """What is the lowest card number? (i.e 101, 356, 206, don't include Z or A)\nNumber juseyo : """
    ui_dcos_2 = """How many cards is there in that set? (312-313-314 is 3)\nNumber juseyo : """

    while True:
        set_type = int(input(ui))
        if set_type == 1 :
            return list(range(101,109))
        elif set_type == 2 :
            return list(range(109,117))
        elif set_type == 3 :
            return list(range(117,121))
        elif set_type == 4 :    
            start_range = int(input(ui_dcos))
            range_lenght = int(input(ui_dcos_2))
            return list(range(start_range, start_range+range_lenght))
        else:
            print(":DahyunSUS: Trying to break my stuff I see... There's only 4 option, no more\n")


def get_member_order() -> bool:
    ui = """What the member drop order?
    1. S1 (Seoyeon) -> S24 (Jiyeon)
    2. S24 (Jiyeon) -> S1 (Seoyeon)\nOrder : """

    while True:
        reply = int(input(ui))
        if reply == 1:
            return False
        elif reply == 2:
            return True        

def get_cluster_size() -> int:
    ui = """How many member are sold in one day?\nNumber juseyo : """
    return int(input(ui))

def get_timestamp() -> tuple[datetime, timedelta]:
    ui_date = """What is the KST date of the drop? (use format yyyy-mm-dd)\nDate : """
    ui_time = """What is the KST time of the drop? (use format hh:mm)\nTime : """
    ui_duration = """What is the time period you want to query, in days? (reply with a number)\nDuration : """


    raw_date = input(ui_date)
    raw_time = input(ui_time)
    raw_duration = int(input(ui_duration))

    raw_ts = f"{raw_date}T{raw_time}:00"

    dt = datetime.fromisoformat(raw_ts)
    dt_kst = dt.replace(tzinfo=ZoneInfo("Asia/Seoul"))
    dt_utc = dt_kst.astimezone(ZoneInfo("UTC"))
    dt_duration = timedelta(days=raw_duration)

    return dt_utc, dt_duration

def get_set_spacings() -> timedelta:
    ui = """What is the spacing, in minutes, between sets? (within one day, if member sets)\nTime (in minutes) : """
    return timedelta(minutes=int(input(ui))) 

def get_cluster_spacings() -> timedelta:
    ui = """What is the spacing, in days, between set clusters? (time between Day1 and Day2)\nTime (in days) : """
    return timedelta(days=int(input(ui)))
#endregion

#region Query creation
def get_objekt_type() -> str:
    while True:
        reply = input("Is the set digital only (Z type)? (yes/no)\nAnswer : ")
        if reply.lower() in ["yes", "ye","y"]:
            return "Z"
        elif reply.lower() in ["no","n"]:
            return "A"
        else:
            print(":KaedeMeep: I said no breaking the code smh\n")

def get_season() -> tuple[str,str]:

    ui = """What is the season you request?
    1. Atom01  2. Binary01  3. Cream01  4. Divine01  5. Ever01
    6. Atom02  7. Binary02  8. Cream02\nYour choice : """

    valid_answer = {
    1: ("Atom01","A"),
    2: ("Binary01","B"),
    3: ("Cream01","C"),
    4: ("Divine01","D"),
    5: ("Ever01","E"),
    6: ("Atom02","AA"),
    7: ("Binary02","BB"),
    8: ("Cream02","CC")
    }

    while True:
        reply = int(input(ui))
        if reply in valid_answer:
            return valid_answer[reply]
        else:
            print("Yk that's not in the options, right? :SoominNervous:\n")

def create_query(schedule:list[Drop], season:str) -> str:
    
    objekt_type = get_objekt_type()

    sub_queries: list[str] = []

    for drop in schedule:
        sub_queries.append(f"""{drop.member}_{drop.collection} : objektsConnection(orderBy: id_ASC, where: {{collection: {{collectionId_eq: "{season} {drop.member} {drop.collection}{objekt_type}"}}, mintedAt_lte: "{drop.sale_end}"}}) {{
                totalCount
            }}
        """)

    query = f'''
    query GetObjektCounts {{
        {"".join(sub_queries)}
    }}
    '''
    return query

#endregion
#region API fetch
def fetch_objekt_data(req_query:str) -> dict[str,CollectionCount]:
    """Requests Pulsar's API for all new Objekts since the last run

    Parameters
    ----------
    - group : str
        Name of the wanted group
    - timestamp : str
        The ISO 8601 date located in timestamp-*group*.txt

    Returns
    -------
    - objekts : json
        API response containing the new objekts
    """

    url = 'https://api.pulsar.azagal.eu/graphql'
    query = req_query

    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'Bifrost v0.1'
    }
    data = {'query': query}

    objekts: dict[str,CollectionCount] = {}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        objekts = response.json()['data']
    except requests.JSONDecodeError as e:
        print(f"[WARN] Couldn't fetch objekt data : {e}")
    except KeyError :
        print(f"[ERROR] Invalid response structure")
    except requests.RequestException as req_err:
        print(f"[ERROR] Couldn't reach the API : {req_err}")

    return objekts

#region Data formatting
def format_data(data: dict[str,CollectionCount], season_key:str) -> dict[str, dict[str, int]]:

    formatted_response: dict[str, dict[str, int]] = {}

    for entry in data:
        member, collection = entry.split("_")
        
        if member not in formatted_response:
            formatted_response[member] = {}

        formatted_response[member][f"{season_key}{collection}"] = data[entry]["totalCount"]
    
    return formatted_response

def export_data(data: dict[str, dict[str, int]]):
    to_export:list[str] = []

    to_export.append(
        "\t".join(
            ["", "Total"] + [c for c in data[next(iter(data))].keys()] + ["\n"]
        )
    )

    for member in data:
        total = sum(data[member].values())
        
        row: list[str] = [
            member,
            str(total),
            *(str(data[member][c]) for c in data[member].keys()),
            "\n"
        ]
    
        to_export.append("\t".join(row))
    
    with open(f"Request_result_{datetime.now():%Y-%m-%d_%H-%M-%S}.txt", "w", encoding="utf8") as file:
        file.writelines(to_export)

if __name__ == "__main__":
    schedule = get_sale_type()
    season, shorthand = get_season()
    query = create_query(schedule, season)
    data = fetch_objekt_data(query)
    formatted = format_data(data, shorthand)
    export_data(formatted)
    