#!/usr/bin/env python3
"""
Unified Otari Merchant Generator
Combines merchant generation and image fixing in one script
Uses JSON data for equipment
"""
import random
import re
import os
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import json
import sys

# Manual mapping of common items to their correct image URLs
ITEM_IMAGE_MAP = {
    # Alchemical Items
    "alchemist's fire": 'https://2e.aonprd.com/Images/Treasure/Alchemists_Fire.webp',
    'acid flask': 'https://2e.aonprd.com/Images/Treasure/Acid_Flask.webp',
    'tanglefoot bag': 'https://2e.aonprd.com/Images/Treasure/Tanglefoot_Bag.webp',
    'smokestick': 'https://2e.aonprd.com/Images/Treasure/Smokestick.webp',
    'thunderstone': 'https://2e.aonprd.com/Images/Treasure/Thunderstone.webp',
    'antidote': 'https://2e.aonprd.com/Images/Treasure/Antidote.webp',
    'antiplague': 'https://2e.aonprd.com/Images/Treasure/Antiplague.webp',
    'elixir of life': 'https://2e.aonprd.com/Images/Treasure/Elixir_of_Life.webp',
    'healing potion': 'https://2e.aonprd.com/Images/Treasure/Healing_Potion.webp',
    'bottled lightning': 'https://2e.aonprd.com/Images/Treasure/Bottled_Lightning.webp',
    # Adventuring Gear
    'waterskin': 'https://2e.aonprd.com/Images/Treasure/Waterskin.webp',
    'backpack': 'https://2e.aonprd.com/Images/Treasure/Backpack.webp',
    'bedroll': 'https://2e.aonprd.com/Images/Treasure/Bedroll.webp',
    'rope': 'https://2e.aonprd.com/Images/Treasure/Rope.webp',
    'grappling hook': 'https://2e.aonprd.com/Images/Treasure/Grappling_Hook.webp',
    'torch': 'https://2e.aonprd.com/Images/Treasure/Torch.webp',
    'rations': 'https://2e.aonprd.com/Images/Treasure/Rations.webp',
    'flint and steel': 'https://2e.aonprd.com/Images/Treasure/Flint_and_Steel.webp',
    'chalk': 'https://2e.aonprd.com/Images/Treasure/Chalk.webp',
    'piton': 'https://2e.aonprd.com/Images/Treasure/Piton.webp',
    'climbing kit': 'https://2e.aonprd.com/Images/Treasure/Climbing_Kit.webp',
    'lantern': 'https://2e.aonprd.com/Images/Treasure/Lantern.webp',
    'oil': 'https://2e.aonprd.com/Images/Treasure/Oil.webp',
    'tent': 'https://2e.aonprd.com/Images/Treasure/Tent.webp',
    'fishing tackle': 'https://2e.aonprd.com/Images/Treasure/Fishing_Tackle.webp',
    "healer's tools": 'https://2e.aonprd.com/Images/Treasure/Healers_Tools.webp',
    "explorer's clothing": 'https://2e.aonprd.com/Images/Treasure/Explorers_Clothing.webp',
    'winter clothing': 'https://2e.aonprd.com/Images/Treasure/Winter_Clothing.webp',
    # Weapons
    'longsword': 'https://2e.aonprd.com/Images/Weapons/Longsword.webp',
    'shortsword': 'https://2e.aonprd.com/Images/Weapons/Shortsword.webp',
