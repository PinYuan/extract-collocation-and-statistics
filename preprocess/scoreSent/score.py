import subprocess
import sys
from joblib import Parallel, delayed
from collections import defaultdict

with open('word_level/A_level_word.txt', 'r') as file:
    aLevel = set(file.read().split())
with open('word_level/B_level_word.txt', 'r') as file:
    bLevel = set(file.read().split())
with open('word_level/C_level_word.txt', 'r') as file:
    cLevel = set(file.read().split())

prons = set(['i', 'you', 'your', 'yours', 'he', 'she', 'they', 'him', 'her', 'them', 'his', 'their', 'it'])
hifres = set([word for word in open('HiFreWords', 'r').readline().split('\t')])
    
cambridgeDict = eval(open('../Camb/camDict.txt', 'r').read())
cambridgeWords = set(cambridgeDict.keys())
    
def getDependencies(line):
    dependency = line[:-1].split(', ')
    dependency = [ word.split('\t') for word in dependency ]
    dependency = [ (int(iword), word, lemma, dep, tag, pos, int(ihead), NER) for iword, word, lemma, dep, tag, pos, ihead, NER in dependency]
    return dependency

def scoreEX(sent):
    deduct = abs(len(sent) - 12) ** 2
    for word in sent:
        # pron
        if word in prons: deduct += 2
        # frequency
        if word not in hifres: deduct += 4
        # proper noun
        if word.istitle(): deduct += 2
        elif word.isupper(): deduct += 10
        # cambridge
        if word not in cambridgeWords: deduct += 5
        # level
        if word in aLevel: deduct -= 2
        elif word in bLevel: deduct += 2
        else: deduct += 8
    return deduct

def score(line):
    index, line = line.split(' ||| ')
    index = int(index)
    dependency = getDependencies(line)
    wordNum = len(dependency)
    if not (wordNum >= 5 and wordNum <= 23): return

    words = [ x[2] for x in dependency ]
    score = scoreEX(words)

    return index, score

# coca
result = Parallel(n_jobs=20, verbose=2)(delayed(score)(line) for line in sys.stdin)

file = open('score.txt', 'w')
score_dict = dict()
for r in result:
    if r != None:
        index, score = r
        if score > 200: continue
        score_dict[index] = score
file.write(str(score_dict))
file.close()
