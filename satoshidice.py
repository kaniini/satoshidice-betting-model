#!/usr/bin/env python
#
# SatoshiDice safe-betting model.  Queries last 100 bets and proposes a safe bet.
# Also provides a pretty graph to show visually how the determination is made.
#
# Public domain.  DEFINITELY NO WARRANTY.
#
# Questions to: William Pitcock <mogri@dereferenced.org>
# If you like it, send some bitcoins to: 17cfpD3n9h6uaCE9LTH9p5Xt5cENNyMNoh
#

import math
import functools
import urllib
import json
import sys
from collections import OrderedDict

def get_betting_data(limit=100):
    uri = 'http://satoshidice.com/lookup.php?tx=&limit={0}&min_bet=0&status=ALL&format=json'.format(limit)
    data = urllib.URLopener().open(uri).read()
    return json.loads(urllib.URLopener().open(uri).read())['bets']

def percentile(values, percent, key=lambda x: x):
    if not values:
        return None
    base = (len(values) - 1) * percent
    floor = math.floor(base)
    ceiling = math.ceil(base)
    if floor == ceiling:
        return key(values[int(base)])
    set0 = key(values[int(floor)]) * (ceiling - base)
    set1 = key(values[int(ceiling)]) * (base - floor)
    return set0 + set1

def likelyhood(percentiles, target):
    return len(filter(lambda x: x < target, percentiles))

data = get_betting_data()
luckybets = map(lambda x: x['lucky'], reversed(data))

percentiles = list()
for i in xrange(100):
    percentiles.append(percentile(luckybets, i * 0.01))

print "50th percentile:", percentiles[50]
print "95th percentile:", percentiles[95]
print "99th percentile:", percentiles[99]

delta = percentiles[99] - percentiles[95]
print "95th% delta    :", delta

thresholds = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1000, 1500, 2000, 3000, 4000,
              6000, 8000, 12000, 16000, 24000, 32000, 32768, 48000, 52000, 56000,
              60000, 64000]

likelyness_dict = {x: likelyhood(percentiles, x) for x in thresholds}

safe_recommendations = filter(lambda x: likelyness_dict[x] > 95, thresholds)
print "Safe bets (95% likely to succeed or better):"
for i in safe_recommendations:
    print "    ", i, likelyness_dict[i], "% likely to succeed"

print "Recommendation : lessthan", safe_recommendations[-2]

try:
    import matplotlib.pyplot as plt
except:
    print "I would make a graph but you don't have matplotlib installed..."
    sys.exit(0)

print "Plotting above to bets.png."
plt.plot(luckybets)
plt.hlines(safe_recommendations, 0, 100, colors='ryg', linestyles='dashed')
plt.ylabel('lucky numbers (safe thresholds marked)')
plt.xlabel('last 100 bets evaluated')
plt.title('satoshidice betting strategy')
plt.savefig('bets.png')
