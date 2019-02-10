from collections import defaultdict
import os
import sys
sys.path.append('./')
from extractGP import *

def getRoot(dependency):
    root = [ (iword, word, lemma, dep, tag, pos, ihead, NER) for iword, word, lemma, dep, tag, pos, ihead, NER in dependency if dep == 'ROOT' ]
    if not root: return []
    else: return root[0][0]

def getDependencies(line):
    dependency = line[:-1].split(', ')
    dependency = [ word.split('\t') for word in dependency ]
    dependency = [ (int(iword), word, lemma, dep, tag, pos, int(ihead), NER) for iword, word, lemma, dep, tag, pos, ihead, NER in dependency]
    return dependency

def loadTenTen():
    phraseTenTen = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: set())))
    wordTenTen = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: set())))

    infile = open('total.txt', 'r')
    for line in infile:
        key, colls = line.split('\t')

        keyword, pos, pattern = key.split('_')
        colls = set([ coll for coll, count in eval(colls) ])

        if ' ' in pos: # phrase
            phraseTenTen[keyword][pos][pattern] = colls
        else:
            wordTenTen[keyword][pos][pattern] = colls

    return wordTenTen, phraseTenTen
       
# load ten-ten
wordTenTen, phraseTenTen = loadTenTen()

# sample sentence 
for line in sys.stdin:
    index, line = line.split(' ||| ')
    index = int(index)
    dependency = getDependencies(line)

    sentence = [ x[1] for x in dependency ]
    if any(x in sentence for x in ['@@@', '<', '>']): continue
    
    for keyword, pos, pattern, colls, passive in dependency_to_GP(dependency, getRoot(dependency)):
        if 'V-ed' not in pattern and passive: continue
        if ' ' in keyword:
            head = keyword.split()[0]
            try:
                if pattern in phraseTenTen[head][keyword].keys():
                    if colls in phraseTenTen[head][keyword][pattern] or \
                        (all( x not in pattern for x in ['v', 'n', 'adj']) and colls == ''):
                        print(keyword+', '+pos+', '+pattern+', '+colls+'\t'+str(index))
            except: continue
        else:
            if pattern in wordTenTen[keyword][pos].keys():
                if colls in wordTenTen[keyword][pos][pattern] or \
                    (all( x not in pattern for x in ['v', 'n', 'adj']) and colls == ''):
                    print(keyword+', '+pos+', '+pattern+', '+colls+'\t'+str(index))
    
