import requests 
import argparse
import uuid
import json 
import re
import pandas as pd

parser = argparse.ArgumentParser(description='Get data from fb group / page')

parser.add_argument('limit', type=str, 
                    help='Loop limit')
parser.add_argument('url', type=str, 
                    help='url')
parser.add_argument('csv_no', type=str, 
                    help='no to append on csv')

args = parser.parse_args()

messages = []
numbers = []
first_names = []
last_names = []
emails = []
blacklists = []
whitelists = []


# load whitelists 
with open("whitelists.txt") as file:
    for line in file:
        whitelists = line.split(",")

# load blacklists 
with open("blacklists.txt") as file:
    for line in file:
        blacklists = line.split(",")

malaysia_phone_patterns = "((\/[6])\w*)|((\/\+[6])\w*)"
pattern = re.compile(malaysia_phone_patterns)

def get_data(url):
    res = requests.get(url)
    result_json = res.json()
    print (result_json)
    next_page_url = result_json["paging"].get("next")
    data = result_json["data"]
    
    # get first data
    for item in data:
        message = item.get("message")
        if message:
            # whitelist posts
            if  any ( whitelist in message.lower() for whitelist in whitelists):
                # check if there are blacklisted words
                if not any (blacklist in message.lower() for blacklist in blacklists):
                    number=""
                    match = pattern.search(message)
                    if match :
                        if match.group(0):
                            number=match.group(0).replace("/", "")
                        elif match.group(1):
                            number=match.group(1).replace("/+", "")
                            # ensure that we only take the number phone digits
                            number=re.find("\d", number)
                        # check if number is exists.
                        if number not in numbers:
                            messages.append(message)
                            numbers.append(number)

    return next_page_url

url = args.url
for x in range(0,int(args.limit)):
    print (url)
    url = get_data(url)
    df = pd.DataFrame({"Message":messages, "Mobile":numbers}, columns = ['Mobile','Message'])
    df.to_csv('fb_group_numbers_%s.csv' % args.csv_no, encoding='utf-8')


