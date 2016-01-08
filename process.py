import csv
import gpsdio
import datetime
import sys
import math

names=set()
classifications = {}
with open("classification-hourlyResultsAll.txt") as f:
    for row in csv.DictReader(f, skipinitialspace=True):
        mmsi = row['mmsi'] = int(row['mmsi'])
        if mmsi not in classifications: classifications[mmsi] = {}
        t = row['start_hour_ms'] = datetime.datetime.utcfromtimestamp(float(row['start_hour_ms'])/1000.0)
        if t not in classifications[mmsi]: classifications[mmsi][t] = set()
        classifications[mmsi][t].add(row['classification'])
        names.add(row['classification'])


with gpsdio.open("classified.msg", "w") as outf:
    with gpsdio.open("tracks.msg") as f:
        c = 0
        for row in f:
            mmsiclass = classifications[int(row['mmsi'])]
            keys = [key for key in mmsiclass.iterkeys()
                   if key <= row['timestamp'] and key + datetime.timedelta(hours=1) >= row['timestamp']]   
            if keys:
                key = keys[0]
                clss = mmsiclass[key]
                total = len(clss)
                if total > 0:
                    fishing = len([cls for cls in clss if cls and cls != 'Not fishing'])
                    row['classification'] = float(fishing) / float(total)
            for key in row:
                if isinstance(row[key], float) and (math.isnan(row[key]) or math.isinf(row[key])):
                    row[key] = None
            outf.write(row)
            c += 1
            if c % 1000 == 0:
                sys.stdout.write(".")
                sys.stdout.flush()
