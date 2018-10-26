# !/usr/bin/env python
# gnDailyActivity.py
#
# Report statistics on daily activity
# in a specified Autonomous System as seen
# by Greynoise.io
#
# Requires: Greynoise API key
#
# Example: python3 gnDailyActivity.py AS12345
#
import sys
import json
import requests
from collections import Counter, defaultdict
from pprint import pprint

# Create a function called "chunks" with two arguments, l and n:
def chunks(l, n):
    # For item i in a range that is a length of l,
    for i in range(0, len(l), n):
        # Create an index range for l of n items:
        yield l[i:i+n]

# Create function to sort results in reverse order
def sorting(a):
    sorted = [x for x in a.items()]
    sorted.sort(key=lambda x: x[1])
    sorted.reverse()
    pprint(sorted[0:9])
    

headers = {'key': 'GREYNOISE API KEY GOES HERE'}

asn = sys.argv[1]

print("Looking up "+ str(asn))

asrankraw = requests.get('http://as-rank.caida.org/api/v1/asns/' + asn.split('AS')[1])
asrank = asrankraw.json()

print("Finding daily stats for " + asrank['data']['org']['name'])

asraw = requests.get('https://research.api.greynoise.io/v2/experimental/recent/asn/' + asn, headers=headers)
asdaily = asraw.json()

allips = []
asnports = defaultdict(int)
asnpaths = defaultdict(int)
asntags = defaultdict(int)
asnagents = defaultdict(int)

if asdaily['ips'] is None:
    print(str(asn) + " was not seen by Greynoise in the last 24 hours")
    exit()
else:
    for i in asdaily['ips']:
        allips.append(i)

chunked = list(chunks(allips, 1000))

for i in chunked:
    bulkips = ",".join(i)
    getbulk = requests.get('https://research.api.greynoise.io/v2/experimental/mass/' + bulkips, headers=headers)
    bulkstats = getbulk.json()
    for stat in bulkstats['data']:
        try:
            for ip in stat['raw_data']['scan']:
                asnports[ip['port']] += 1
        except:
            pass
        try:
            for path in stat['raw_data']['web']['paths']:
                asnpaths[path] += 1
        except:
            pass
        try:
            for tag in stat['tags']:
                asntags[tag] += 1
        except:
            pass
        try:
            for agent in stat['raw_data']['web']['useragents']:
                asnagents[agent] += 1
        except:
            pass

print(str(asn) + " Daily Ports: "); sorting(asnports)
print(str(asn) + " Daily Paths: "); sorting(asnpaths)
print(str(asn) + " Daily Tags: "); sorting(asntags)
print(str(asn) + " Daily UserAgents: "); sorting(asnagents)
