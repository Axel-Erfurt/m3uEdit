#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys

if not len(sys.argv) == 3:
    print("Usage: \npython3 ./m3u_to_csv.py input.m3u output.csv")
    sys.exit()
    
m3u_file = sys.argv[1]
csv_file = sys.argv[2]

mylist = open(m3u_file, 'r').read().splitlines()

group = ""
ch = ""
url = ""
id = ""
logo = ""
csv_content = ""

headers = ['tvg-name', 'group-title', 'tvg-logo', 'tvg-id', 'url']
csv_content += '\t'.join(headers)
csv_content += "\n"

for x in range(1, len(mylist)-1):
    line = mylist[x]
    nextline = mylist[x+1]
    if line.startswith("#EXTINF") and not "**********" in line:
        if 'tvg-name="' in line:
            ch = line.partition('tvg-name="')[2].partition('" ')[0]
        elif 'tvg-name=' in line:
            ch = line.partition('tvg-name=')[2].partition(' tvg')[0]
        else:
            ch = line.rpartition(',')[2]        
        if ch == "":
            ch = "No Name"
        ch = ch.replace('"', '')
            
        if 'group-title="' in line:
            group = line.partition('group-title="')[2].partition('"')[0]

        elif "group-title=" in line:
            group = line.partition('group-title=')[2].partition(' tvg')[0]
        else:
            group = "TV"
        group = group.replace('"', '')        
        
        if 'tvg-id="' in line:
            id = line.partition('tvg-id="')[2].partition('"')[0]
        elif 'tvg-id=' in line:
            id = line.partition('tvg-id=')[2].partition(' ')[0]
        else:
            id = ""
        id = id.replace('"', '')
        url = nextline
        if 'tvg-logo="' in line:
            logo = line.partition('tvg-logo="')[2].partition('"')[0]
        elif 'tvg-logo=' in line:
            logo = line.partition('tvg-logo=')[2].partition(' ')[0]        
        else:
            logo = ""            
        csv_content += (f'{ch}\t{group}\t{logo}\t{id}\t{url}\n')

with open(csv_file, 'w') as f:        
    f.write(csv_content)
        
    
