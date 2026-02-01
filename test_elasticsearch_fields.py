#!/usr/bin/env python3
"""Test what fields are available in Elasticsearch for equipment"""
import requests
import json

AON_ELASTIC_URL = "https://elasticsearch.aonprd.com/aon/_search"

# Query for a known item to see all available fields
query = {
    "size": 1,
    "query": {
        "bool": {
            "must": [
                {"match": {"category": "equipment"}},
                {"match": {"name": "Backpack"}}
            ]
        }
    }
}

headers = {
    'Content-Type': 'application/json',
    'User-Agent': 'Mozilla/5.0'
}

response = requests.post(AON_ELASTIC_URL, json=query, headers=headers, timeout=10)
data = response.json()

if data.get('hits', {}).get('hits'):
    item = data['hits']['hits'][0]['_source']
    print("Available fields for 'Backpack':")
    print(json.dumps(item, indent=2))
else:
    print("No results found")

# Try a weapon
print("\n" + "="*60 + "\n")

query['query']['bool']['must'] = [
    {"match": {"category": "weapon"}},
    {"match": {"name": "Longsword"}}
]

response = requests.post(AON_ELASTIC_URL, json=query, headers=headers, timeout=10)
data = response.json()

if data.get('hits', {}).get('hits'):
    item = data['hits']['hits'][0]['_source']
    print("Available fields for 'Longsword':")
    print(json.dumps(item, indent=2))
else:
    print("No results found")

# Try armor
print("\n" + "="*60 + "\n")

query['query']['bool']['must'] = [
    {"match": {"category": "armor"}},
    {"match": {"name": "Leather Armor"}}
]

response = requests.post(AON_ELASTIC_URL, json=query, headers=headers, timeout=10)
data = response.json()

if data.get('hits', {}).get('hits'):
    item = data['hits']['hits'][0]['_source']
    print("Available fields for 'Leather Armor':")
    print(json.dumps(item, indent=2))
else:
    print("No results found")
