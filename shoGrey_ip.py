# !/usr/bin/env python
# shoGrey_ip.py
#
# Stupid simple IP lookup against Greynoise.io
# Also looks up against Shodan and returns ports, tags, vulns
# requires json, requests, shodan
#
# Also requires Shodan API key
#
# Example: python3 shoGrey_ip.py 1.2.3.4
#
import sys
import json
import requests
import shodan

headers = {'key': 'GREYNOISE API KEY GOES HERE'}
SHODAN_API_KEY = "SHODAN API KEY GOES HERE"
api = shodan.Shodan(SHODAN_API_KEY)
bots = {}

ip = sys.argv[1]

gnr = requests.get('https://research.api.greynoise.io/v2/noise/context/' + ip, headers = headers) #V2 IP API lookup
data = gnr.json()

try:
    host = api.host(ip)
    tags = host['tags']
    vulns = host['vulns']
    ports = host['ports']
    data['shodan_tags'] = tags
    data['vulns'] = vulns
    data['open_ports'] = ports
    # Compare open Shodan ports against GN scan ports to find bots
    for i in data['raw_data'].get('scan'):
        if i['port'] in host['ports']:
            key = i['port']
            bots[key] = 'True'
    data['bots'] = bots

except:
    pass

json_str = json.dumps(data, indent=4, sort_keys=False)
print(json_str)
