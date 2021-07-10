import json
import requests
from time import time
from tqdm import tqdm
import pickle
import pandas as pd


def getUserNames():
    url = 'https://raw.githubusercontent.com/KiranGershenfeld/VisualizingTwitchCommunities/CloudCompute/DataCollection/ChannelList.txt'
    data = requests.get(url).text.split('\n')[:-1]

    return data


def getCreds():
    with open('secrets.json', 'r') as fh:
        secrets = json.load(fh)

    client_id = secrets['client-id']
    client_secret = secrets['client-secret']

    return client_id, client_secret


def getToken():
    client_id, client_secret = getCreds()
    response = requests.post(
            f'''https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'''
        )
    data = response.json()
    print(data)

    return data


def getIdsFromUserNames():
    # Output Written to outfile
    ids = {}

    names = getUserNames()
    client_id, client_secret = getCreds()

    token = getToken()
    access_token = token['access_token']
    expires_in = token['expires_in']
    set_time = time()

    with tqdm(total=len(names)) as pbar:
        # Loops through the names
        for name in names:
            # If token expires in 5 seconds, get new token
            if (time() - set_time) > (expires_in - 5):
                foo = getToken()
                access_token = foo['access_token']
                expires_in = foo['expires_in']

            # Set Headers
            headers = {
                "Client-ID": client_id,
                "Authorization": "Bearer " + access_token
            }

            # Create Session
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(
                f"https://api.twitch.tv/helix/search/channels?query={name}",
                headers=session.headers,
            )

            # Get data
            data = response.json()['data']
            for i in data:
                temp = i['id']
                dp = i['display_name']
                if temp not in ids.keys():
                    ids[temp] = dp

            # Update Progress bar
            pbar.update(1)

    with open('outfile', 'wb') as fp:
        pickle.dump(ids, fp)

    print(f"Saved {len(ids.keys())} names to file")


def emotesFromId():
    DATASET = []

    with open('outfile', 'rb') as fp:
        ids = pickle.load(fp)

    client_id, client_secret = getCreds()

    token = getToken()
    access_token = token['access_token']
    expires_in = token['expires_in']
    set_time = time()

    with tqdm(total=len(ids.keys())) as pbar:
        # Loops through the names
        for idx in ids.keys():
            # If token expires in 5 seconds, get new token
            if (time() - set_time) > (expires_in - 5):
                foo = getToken()
                access_token = foo['access_token']
                expires_in = foo['expires_in']

            # Set Headers
            headers = {
                "Client-ID": client_id,
                "Authorization": "Bearer " + access_token
            }

            # Create Session
            session = requests.Session()
            session.headers.update(headers)
            response = session.get(
                f"https://api.twitch.tv/helix/chat/emotes?broadcaster_id={idx}",
                headers=session.headers,
            )

            # Get data
            data = response.json()['data']
            for emote in data:
                uid = idx
                eid = emote['id']
                ename = emote['name']
                image = emote['images']['url_2x']
                tier = emote['tier']
                emote_type = emote['emote_type']
                emote_set = emote['emote_set_id']

                DATASET.append([uid, eid, ename, image, tier, emote_type, emote_set])

            # Update Progress bar
            pbar.update(1)

    df = pd.DataFrame(
        DATASET,
        columns=["uid", "eid", "ename", "image_url", "tier", "emote_type", "emote_set"]
    )

    print(df.head)
    df.to_csv('file1.csv')


def downloadEmoteImages():
    pass


if __name__ == '__main__':
    getIdsFromUserNames()
    emotesFromId()
