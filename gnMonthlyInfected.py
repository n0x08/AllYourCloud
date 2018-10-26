# !/usr/bin/env python
# gnMonthlyInfected.py
#
# Report statistics on monthly infections
# in a specified Autonomous System as seen
# by Greynoise.io
#
# Requires: Greynoise API key
#
# Example: python3 gnMonthlyInfected.py AS12345
#
import sys
import json
import requests
from collections import Counter, defaultdict
from pprint import pprint

headers = {'key': 'GREYNOISE API KEY GOES HERE'}

asn = sys.argv[1]

print("Looking up "+ str(asn))

asrankraw = requests.get('http://as-rank.caida.org/api/v1/asns/' + asn.split('AS')[1])
asrank = asrankraw.json()

print("Finding infection stats for " + asrank['data']['org']['name'])

asnraw = requests.get('https://research.api.greynoise.io/v2/infections/asn/' + asn, headers = headers) #V2 IP API lookup
asndata = asnraw.json()

tagstats = defaultdict(int)

for i in asndata:
    tagstats[str(i['tag_name'])] += 1

sorted_tags = [x for x in tagstats.items()]
sorted_tags.sort(key=lambda x: x[1])
sorted_tags.reverse()

pprint(sorted_tags)
print("Total infected hosts in " + str(asn) + ": " + str(sum(n for _, n in sorted_tags)))
