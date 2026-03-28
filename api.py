import random
import requests
from typing import Optional, List
from pprint import pprint
import hashlib

from api_types import *

authHost = "http://auth.mconly.net"

authHost_updates = lambda modpack: authHost + "/serverauth/updates.php?type=" + modpack
authHost_hwids = authHost + "/serverauth/hwids.php"
authHost_getCoins = authHost + "/serverauth/getcoins.php"
authHost_getServers = authHost + "/launcher/getServers.php"
authHost_getSessionData = authHost + "/serverauth/a.php"

authsalt = "jiiwijr9124bbuabyIAW"

md5 = lambda input: hashlib.md5(input.encode()).hexdigest()

class BadLoginException(Exception):
    pass

def get_updates(modpack):
    updates_raw = requests.get(authHost_updates(modpack)).content.decode().strip()

    updates = [Updater_Entry(path = y[0],
                             md5 = y[1],
                             type = UpdateType(int(y[2])))
           for i in updates_raw.split("\n") for y in [i.split(":")]]

    return updates

def get_servers() -> List[Servers_Server]:
    servers_raw, minimal_memory_raw = requests.get(authHost_getServers).content.decode().strip().split("\n", maxsplit=1)

    servers = {server[0]: Servers_Server(*server) for i in servers_raw.split(":") if len(i) != i.count(",") for server in [i.split(",")]}
    # minimal_memory = {k:int(v) for i in minimal_memory_raw.split("\n") for k, v in [i.split(":")]}

    return servers

def get_server(modpack) -> Servers_Server:
    return get_servers().get(modpack)


get_sessionhash = lambda coinsHash: md5(f"{authsalt}|{coinsHash}")
get_oshash = lambda coinsHash: md5(f"false|{authsalt}|{coinsHash}")

def get_coins_hash(username, password):
    captcha = random.randint(1000_000_000, 10_000_000_000)
    response = requests.post(authHost_getCoins, data = {
        "user": username,
        "password": password,
        "hwidfull": "null",
        "ch": md5(f"{username}{password}|{authsalt}|{captcha}"),
        "c": captcha
    }).text

    if response == "Bad login":
        raise BadLoginException()

    return response.split("[")[-1][:-1]

def send_hwids(username, coins_hash):
    return requests.post(authHost_hwids, data = {
        "username": username,
        "oh": get_oshash(coins_hash),
        "sh": get_sessionhash(coins_hash)
    })

def get_session(username, password, server: Servers_Server):
    coins_hash = get_coins_hash(username, password)
    send_hwids(username, coins_hash)
    session_data_raw = requests.post(authHost_getSessionData, data = {
        "user": username,
        "password": password,
        "serverType": server.type,
        "checkh": 0,
        "version": 0,
        "sh": get_sessionhash(coins_hash)
    })
    return Session(*session_data_raw.text.split(":"))
