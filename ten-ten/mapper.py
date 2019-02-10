import sys
sys.path.append('./')

from extractGP import *

def getDependencies(line):
    dependency = line[:-1].split(', ')
    dependency = [ word.split('\t') for word in dependency ]
    dependency = [ (int(iword), word, lemma, dep, tag, pos, int(ihead), NER) for iword, word, lemma, dep, tag, pos, ihead, NER in dependency]
    return dependency

for line in sys.stdin:
    index, line = line.split(' ||| ')
    dependency = getDependencies(line)

    sentence = [ x[1] for x in dependency ]
    if any(x in sentence for x in ['@@@', '<', '>']): continue
    for keyword, pos, pattern, colls, passive in dependency_to_GP(dependency, getRoot(dependency)):
        print(keyword+', '+pos+', '+pattern+'\t'+colls)
    
