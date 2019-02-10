#!/usr/bin/python 
from collections import defaultdict
import sys

cambridgeDict = eval(open('camDict.txt', 'r').read())
cambridgeWords = set(cambridgeDict.keys())

unWantColls = {'it', 'that', 'this', 'these', 'those'} # , 'something', 'someone', 'some'
unWantADVs = {'by', 'maybe', 'evenly', 'as', 'eventually', 'elsewhere', 'soon', 'sometims', 'now', 'evetually', 'after', 'below', 'so', 'exactly', 'even', 'instead', 'merely', 'very', 'anymore', 'then', 'still', 'really', 'once', 'actually', 'ever', 'in', 'also', 'only', 'just', 'else', 'anytime', 'rather', 'indeed', 'again', 'of', 'likely', 'ago', 'further', 'all', 'likewise', 'already', 'thereby', 'together', 'enough', 'everyday', 'before', 'much', 'almost', 'altogether', 'anyway', 'always', 'everywhere', 'on', 'meanwhile', 'best', 'afterward'}

def getTop10Coll(): 
    for head in phraseCollsCount.keys():
        for phrase in phraseCollsCount[head].keys():
            pattern_Coll = defaultdict(lambda: [])

            for pattern in phraseCollsCount[head][phrase].keys():
                total = sum( [ x for x in phraseCollsCount[head][phrase][pattern].values()] )
                
                # score coll
                top10 = []
                for coll, count in phraseCollsCount[head][phrase][pattern].items():
                    if any( unWantColl in coll for unWantColl in unWantColls ): continue
                    if pattern == 'V adv' and any( unWantADV in coll for unWantADV in unWantADVs ): continue
                    deduct = 0
                    
                    for c in coll.split('_'):
                        if c.startswith('&lt'): continue
                        if c.lower() not in cambridgeWords: deduct += 2
                            
                    top10 += [ (coll, count-deduct) ] 
                
                top10 = sorted(top10, key=lambda x: -x[1])[:10]
                pattern_Coll[pattern] = (top10, total)

            pattern_Coll = sorted(list(pattern_Coll.items()), key=lambda x: -x[1][1])
            for pattern, (top10, _) in pattern_Coll[:10]:
                print(head+'_'+phrase+'_'+pattern+'\t'+str(top10))

    for keyword in collsCount.keys():
        for pos in collsCount[keyword].keys():
            pattern_Coll = defaultdict(lambda: [])

            for pattern in collsCount[keyword][pos].keys():
                total = sum( [ x for x in collsCount[keyword][pos][pattern].values()] )
                # if total < 20: continue
                # score coll
                top10 = []
                for coll, count in collsCount[keyword][pos][pattern].items():
                    if any( unWantColl in coll for unWantColl in unWantColls ): continue
                    if pattern == 'V adv' and any( unWantADV in coll for unWantADV in unWantADVs ): continue    
                    deduct = 0
                    
                    for c in coll.split('_'):
                        if c.startswith('&lt'): continue
                        if c.lower() not in cambridgeWords: deduct += 2
                            
                    top10 += [ (coll, count-deduct) ] 
                
                top10 = sorted(top10, key=lambda x: -x[1])[:10]
                pattern_Coll[pattern] = (top10, total)
                
            pattern_Coll = sorted(list(pattern_Coll.items()), key=lambda x: -x[1][1])
            for pattern, (top10, _) in pattern_Coll[:10]:
                print(keyword+'_'+pos+'_'+pattern+'\t'+str(top10))

collsCount = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))
phraseCollsCount = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))
                
# Statistic GP
for line in sys.stdin:
    key, colls = line.strip('\n').split('\t')

    keyword, pos, pattern = key.split(', ')

    # statistic collocation count
    if ' ' in keyword:
        head = keyword.split()[0]
        phraseCollsCount[head][keyword][pattern][colls] += 1
    else:
        collsCount[keyword][pos][pattern][colls] += 1

# Find top 10 collocation for each keyword
getTop10Coll()


