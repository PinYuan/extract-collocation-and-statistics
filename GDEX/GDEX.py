from collections import defaultdict
import re

with open('../preprocess/scoreSent/score.txt', 'r') as file:# ../preprocess/scoreSent/
    score_sentences = eval(file.read())
score_indexes = set(score_sentences.keys())

cambridgeDict = eval(open('../preprocess/Camb/cam(index_GP).txt', 'r').read())
cambridgeWords = set(cambridgeDict.keys())
    
def findCambridgeEx(keyword, targetPOS, targetPat):#, bestColls):
    head = keyword.split()[0] if len(keyword.split()) > 1 else keyword
    
    if head in cambridgeWords:
        if targetPOS not in cambridgeDict[head].keys(): return -1
        
        for index, GPs in cambridgeDict[head][targetPOS]:
            targetWordGPs = [ (word, pos, pat, colls, passive) for word, pos, pat, colls, passive in GPs \
                             if word == keyword and pos == targetPOS and pat == targetPat and not passive ] #  and colls in bestColls
            if targetWordGPs: return index
    return -1
        
def select_example(wordEX, phraseEX, wordCoreDict, phraseCoreDict):
    for word in phraseCoreDict.keys():
        for phrase in phraseCoreDict[word].keys():
            clean_phrase = phrase.rsplit('%', 1)[0]
            
            for pat, colls in phraseCoreDict[word][phrase]:
                clean_pat = pat.rsplit('%', 1)[0]
                clean_colls = [ coll.rsplit('%', 1)[0] for coll in colls ]
                
                 # 爬劍橋字典選適當的句子，
                camIndex = findCambridgeEx(clean_phrase, 'V', clean_pat)#, clean_colls[:3])
                if camIndex != -1: 
                    print(word+', '+phrase+', '+pat+'\t'+str(clean_colls)+'|||'+str(camIndex)+'|||'+'cam')
                # COCA 
                else:
                    score = {}
                    for clean_coll in clean_colls[:3]:
                        for sentIndex in phraseEX[word][clean_phrase][clean_pat][clean_coll]:
                            score[sentIndex] = score_sentences[sentIndex] # 扣分
                    bestIndex = sorted(score.items(), key=lambda x: x[1])[0][0] if score else -1
                    print(word+', '+phrase+', '+pat+'\t'+str(clean_colls)+'|||'+str(bestIndex)+'|||'+'coca')

    for word in wordCoreDict.keys():
        for pos in wordCoreDict[word].keys():
            for pat, colls in wordCoreDict[word][pos]:
                clean_pat = re.sub('[()]', '', pat.rsplit('%', 1)[0])
                clean_colls = [ re.sub('[()]', '', coll.rsplit('%', 1)[0]) for coll in colls ]

                # 爬劍橋字典選適當的句子，
                camIndex = findCambridgeEx(word, pos, clean_pat)#, clean_colls[:3])
                if camIndex != -1: 
                    print(word+', '+pos+', '+pat+'\t'+str([ coll.rsplit('%', 1)[0] for coll in colls ])+'|||'+str(camIndex)+'|||'+'cam')
                # COCA 
                else:
                    score = {}
                    for clean_coll in clean_colls[:3]:
                        for sentIndex in wordEX[word][pos][clean_pat][clean_coll]:
                            score[sentIndex] = score_sentences[sentIndex] # 扣分
                    bestIndex = sorted(score.items(), key=lambda x: x[1])[0][0] if score else -1
                    print(word+', '+pos+', '+pat+'\t'+str([ coll.rsplit('%', 1)[0] for coll in colls ])+'|||'+str(bestIndex)+'|||'+'coca')