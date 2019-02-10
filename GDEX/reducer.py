from collections import defaultdict
import sys

from GDEX import *

cambridgeDict = eval(open('../preprocess/Camb/camDict.txt', 'r').read())
cambridgeWords = set(cambridgeDict.keys())

def refineGP(patColls):
    refined = patColls.copy()
    pats = set([pat for pat, collCounts, patTotal in patColls])
    passivePats = [patColl for patColl in patColls if patColl[0].startswith('be V-ed')]
    vPats = [patColl for patColl in patColls if patColl[0].startswith('v')]
    
    for pat, collCounts, patTotal in passivePats:
        potentialPat = pat.replace('be V-ed', 'V n')
        if potentialPat in pats:
            target = [ patColl for patColl in refined if patColl[0] == potentialPat ][0]
            refined.remove(target)
            refined.append((target[0], target[1], target[2]+patTotal))
            refined.remove((pat, collCounts, patTotal))
            
        
    for pat, collCounts, patTotal in vPats:
        potentialPat = pat.replace('v ', '')
        if potentialPat in pats:
            target = [ patColl for patColl in refined if patColl[0] == potentialPat ][0]
            # 量過少不合併
            if (patTotal < target[2] and patTotal/target[2] <= 0.1 and patTotal < 5) or\
               (target[2] < patTotal and target[2]/patTotal <= 0.1 and target[2] < 5):\
                continue    
            refined.remove(target)

            overlap = []
            for coll, count in collCounts:
                for targetColl, targetCount in target[1]:
                    if targetColl in coll: 
                        if len(coll.split('_')) == 2: 
                            overlap += [('('+coll.split('_')[0]+')'+'_'+coll.split('_')[1], count+targetCount)]
                        else: # 1
                            overlap += [('('+coll.split('_')[0]+')', count+targetCount)]
                        break
            if not overlap: 
                for coll, count in collCounts:
                    if len(coll.split('_')) == 2: 
                        overlap += [('('+coll.split('_')[0]+')'+'_'+coll.split('_')[1], count)]
                    else: # 1
                        overlap += [('('+coll.split('_')[0]+')', count)]

            refined.append(('(v) '+target[0], overlap, target[2]+patTotal))
            refined.remove((pat, collCounts, patTotal))

    return refined

def percentGP(collsCount, phraseCollsCount, NO_COLL, NO_PAT, NO_PHR):
    wordCoreDict = defaultdict(lambda: defaultdict(lambda: [])) 
    phraseCoreDict = defaultdict(lambda: defaultdict(lambda: [])) 
    
    for word in phraseCollsCount.keys():
        phrasePatColls = []
        for phrase in phraseCollsCount[word].keys():
            patsColls = []
            for pat in phraseCollsCount[word][phrase].keys():
                patTotal = sum([ x for x in phraseCollsCount[word][phrase][pat].values() ])
                
                # score coll
                pairs = []
                for coll, count in phraseCollsCount[word][phrase][pat].items():
                    deduct = 0
                    for c in coll.split('_'):
                        if c.startswith('&lt'): continue
                        if c.lower() not in cambridgeWords: deduct += 2
                            
                    pairs += [ (coll, count-deduct) ] 
                
                if pat == 'V n': # filter '' caused by ''
                    pairs = [ (coll, count) for coll, count in pairs if coll != '']
              
                collCounts = sorted(pairs, key=lambda x: -x[1])[:NO_COLL]
                patsColls += [ (pat, collCounts, patTotal) ]
            
            patsColls = refineGP(patsColls)
            patsColls.sort(key=lambda x: -x[2])
            phraseTotal = sum(patsColl[2] for patsColl in patsColls)
            
            # filter pattern by std
            # patsCount = [ patsColl[2]  for patsColl in patsColls ]
            # std = numpy.std(patsCount)
            # mean = numpy.mean(patsCount)
            # topPatColls = [ patsColl for patsColl in patsColls if patsColl[2] >= std+mean ]
            
            phrasePatColls += [ (phrase, patsColls, phraseTotal) ]

        phrasePatColls.sort(key=lambda x: -x[2])
        wordTotal = sum(phrasePatColl[2] for phrasePatColl in phrasePatColls)
      
        for phrase, patCounts, phraseTotal in phrasePatColls[:NO_PHR]:
            phrasePercent = str(int(phraseTotal / wordTotal * 100))
            if phraseTotal < 20 and int(phrasePercent) <= 10: continue
            
            for pat, colls, patTotal in patCounts[:NO_PAT]:
                patPercent = str(int(patTotal / phraseTotal * 100))
                if patTotal < 10 and int(patPercent) <= 5: continue
                    
                coll_percent = []
                for coll, count in colls:
                    collPercent = str(int(count / patTotal * 100))
                    coll_percent += [coll+'%'+collPercent]
                    
                phraseCoreDict[word][phrase+'%'+phrasePercent] += [(pat+'%'+patPercent, coll_percent)]
    
    for word in collsCount.keys():
        for pos in collsCount[word].keys():
            patsColls = []

            for pat in collsCount[word][pos].keys():
                patTotal = sum([ x for x in collsCount[word][pos][pat].values() ])

                # score coll
                pairs = []
                for coll, count in collsCount[word][pos][pat].items():
                    deduct = 0
                    for c in coll.split('_'):
                        if c.startswith('&lt'): continue
                        if c.lower() not in cambridgeWords: deduct += 2
                            
                    pairs += [ (coll, count-deduct) ] 
                    
                if pat == 'V n': # filter '' caused by ''
                    pairs = [ (coll, count) for coll, count in pairs if coll != '' ]

                collCounts = sorted(pairs, key=lambda x: -x[1])[:NO_COLL]
                patsColls += [ (pat, collCounts, patTotal) ]

            patsColls = refineGP(patsColls)
            patsColls.sort(key=lambda x: -x[2])

            wordTotal = sum(patsColl[2] for patsColl in patsColls)

            for pat, colls, patTotal in patsColls[:NO_PAT]:
                patPercent = str(int(patTotal / wordTotal * 100))
                if patTotal < 20 and int(patPercent) <= 5: continue

                coll_percent = []
                for coll, count in colls:
                    collPercent = str(int(count / patTotal * 100))
                    coll_percent += [coll+'%'+collPercent]
                    
                wordCoreDict[word][pos] += [(pat+'%'+patPercent, coll_percent)]
    return wordCoreDict, phraseCoreDict
    
collsCount = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))
phraseCollsCount = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: 0))))
wordEX = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: []))))
phraseEX = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: []))))

# Statistic GP
for line in sys.stdin:
    key, sentIndex = line.strip('\n').split('\t')
    sentIndex = int(sentIndex)
    keyword, pos, pattern, colls = key.split(', ')

    # statistic collocation count
    if ' ' in keyword:
        head = keyword.split()[0]
        if sentIndex in score_indexes: phraseEX[head][keyword][pattern][colls].append(sentIndex)
        #for coll in colls.split('_'):
        phraseCollsCount[head][keyword][pattern][colls] += 1
    else:
        if sentIndex in score_indexes: wordEX[keyword][pos][pattern][colls].append(sentIndex)
        #for coll in colls.split('_'):
        collsCount[keyword][pos][pattern][colls] += 1

    del line, key, sentIndex, keyword, pos, pattern, colls

# percent grammar pattern
wordCoreDict, phraseCoreDict = percentGP(collsCount, phraseCollsCount, 3, 5, 5)

#file = open('wordD.txt', 'w')
#file.write(str(json.loads(json.dumps(wordCoreDict))))
#file.close()
del collsCount,phraseCollsCount

# good example
select_example(wordEX, phraseEX, wordCoreDict, phraseCoreDict)
