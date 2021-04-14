#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys

if not len(sys.argv) == 3:
    print("Usage: \npython3 ./csv_to_m3u.py input.csv output.m3u")
    sys.exit()
    
csv_file = sys.argv[1]
print(f"Datei: {csv_file} wird konvertiert")
m3u_file = sys.argv[2]

mylist = open(csv_file, 'r').read().splitlines()

group = ""
ch = ""
url = ""
id = ""
logo = ""
m3u_content = ""

headers = ['tvg-name', 'group-title', 'tvg-logo', 'tvg-id', 'url']
m3u_content += "#EXTM3U\n"

for x in range(1, len(mylist)):
    line = mylist[x].split('\t')
    ch = line[0]
    group = line[1]
    logo = line[2]
    id = line[3]
    url = line[4]
    
    m3u_content += f'#EXTINF:-1 tvg-name="{ch}" group-title="{group}" tvg-logo="{logo}" tvg-id="{id}",{ch}\n{url}\n'

with open(m3u_file, 'w') as f:        
    f.write(m3u_content)