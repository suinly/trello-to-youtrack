#!/usr/bin/env python3

import sys
import json
import csv
import os
import argparse
import time
import requests

from config import (
    TRELLO_API_KEY,
    TRELLO_API_TOKEN,
    MEMBER_TO_USER,
    LIST_TO_STATE,
    ARCHIVE_STATE,
)


def trelloRequest(method, path, params=None):
    url = "https://api.trello.com/1/{}".format(path)
    query = {
        "key": TRELLO_API_KEY,
        "token": TRELLO_API_TOKEN,
    }

    if params:
        query = {**query, **params}

    response = requests.request(method, url, params=query)

    return json.loads(response.text)


parser = argparse.ArgumentParser()
parser.add_argument("--board", help="Board ID from Trello", required=False, type=str)
parser.add_argument(
    "--output",
    help="File to output to (default: output.csv)",
    default="output.csv",
    required=False,
    type=str,
)
parser.add_help = True
args = parser.parse_args()

if args.board is None:
    boards = trelloRequest("GET", "member/me/boards")

    print("Please choose a board and run again with --board argument")

    for board in boards:
        print("{}: {}".format(board["name"], board["id"]))

    sys.exit()


print("Loading Data...")

# fetch cards
cards = trelloRequest("GET", "boards/{}/cards/all".format(args.board))

# fetch lists
lists = trelloRequest(
    "GET",
    "boards/{}/lists".format(args.board),
    {
        "filter": "all",
        "cards": "all",
    },
)
lists = {l["id"]: l["name"] for l in lists}

print("Found {} cards in {} lists".format(len(cards), len(lists)))
print("Parsing...")


# Return issue author username
def getAuthor(username):
    try:
        return MEMBER_TO_USER[username]
    except:
        return "!{}".format(username)


# Return state name for YouTrack
def getState(card):
    cardList = lists[card["idList"]]

    if card["closed"]:
        return ARCHIVE_STATE

    try:
        return LIST_TO_STATE[cardList]
    except:
        return "Готово"


with open(os.path.abspath(args.output), "w") as f:
    writer = csv.writer(f)

    writer.writerow(
        [
            "$type$",
            "id",
            "author",
            "created",
            "summary",
            "description",
            "State (state)",
            "Trello URL (string)",
        ]
    )

    cards_count = 1
    id = 999999

    for card in cards:
        time.sleep(300 / 1000)
        createdAt = "1970-01-01T00:00:00.000Z"

        actions = trelloRequest(
            "GET",
            "cards/{}/actions".format(card["id"]),
            {
                "limit": 1000,
                "filter": "createCard,commentCard,addAttachmentToCard",
            },
        )

        for action in actions:
            if action["type"] == "createCard":
                writer.writerow(
                    [
                        "issue",
                        card["idShort"],
                        getAuthor(action["memberCreator"]["username"]),
                        action["date"],
                        card["name"] if card["name"] else "-",
                        card["desc"].replace("@thedanielflow", "@danielflow"),
                        getState(card),
                        card["shortUrl"],
                    ]
                )

        for action in actions:
            if action["type"] == "commentCard":
                writer.writerow(
                    [
                        "comment",
                        id,
                        getAuthor(action["memberCreator"]["username"]),
                        action["date"],
                        action["data"]["text"],
                        "",
                        "",
                        "",
                    ]
                )

                id += 1

            elif action["type"] == "addAttachmentToCard":
                if action["data"]["attachment"].get("url"):
                    writer.writerow(
                        [
                            "comment",
                            id,
                            getAuthor(action["memberCreator"]["username"]),
                            action["date"],
                            "Add attachment: {}".format(
                                action["data"]["attachment"]["url"]
                            ),
                            "",
                            "",
                            "",
                        ]
                    )

                id += 1

        print("{}/{}".format(cards_count, len(cards)))
        cards_count += 1

print("Output to {}".format(os.path.abspath(args.output)))
