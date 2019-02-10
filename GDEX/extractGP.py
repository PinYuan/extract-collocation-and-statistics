import re
from collections import defaultdict 

cambridgeDict = eval(open('camDict.txt', 'r').read())
cambridgeWords = set(cambridgeDict.keys())

pgPreps = set('under|without|around|round|in_favor_of|_|about|after|against|among|as|at|between|behind|by|for|from|in|into|of|on|upon|over|through|to|toward|off|on|across|towards|with|out'.split('|'))
prts = 'out|off|down|up|across'.split('|')

verbpat = ('V n; V ord; V pron-refl; V adj; V prep; V adv; V -ing; V to v; V inf; V to inf; V n to inf; V v; V that; V wh; V wh to v; V quote; '+\
              'V so; V not; V as if; V as though; V someway; V together; V as adj; V as to wh; V by amount; '+\
              'V amount; V by -ing; V in favour of n; V in favour of ing; V n in favour of n; V n in favour of ing; V n n; V n adj; V n -ing; V n to v; V n inf; V that n inf; V n that; '+\
              'V n wh; V n wh to inf; V n v-ed; V n someway; V n to n; V n with n'+\
              'V n as adj; V n into -ing; V adv; V and v; V ord prep; V n ord prep; '+\
              'V it; V it v-ed; V it n; V it prep;V it adv; V it inf; V prep it; V it as n; V it as adj; '+\
              'V it over n; V it to n; V n for it; V by -ing; V pl-n; V adj among pl-n; V among pl-n; V between pl-n;'+\
              'V to n; V way prep; V way adv; wh it V to n; V out of n').split('; ')

verbpat += ['V %s n' % prep for prep in pgPreps]+['V n %s n' % prep for prep in pgPreps]+\
            ['V n %s' % prt for prt in prts]+['V %s n' % prt for prt in prts]+\
            ['V pron-refl %s' % prt for prt in prts]+\
            ['V pron-refl %s n' % prep for prep in pgPreps]
            # [pat+' %s n' % prep for prep in pgPreps for pat in ['V n %s' % prt for prt in prts]]

nounpat = ('on N; out of N; with N; under N; in N; within N; without N; to N; at N; of N; ord N; into N; from N; '+\
           'N for n to v; N from n that; N from n to v; N from n for n; N in favor of; N in favour of; '+\
            'N of amount; '+ \
            'N that; N to v; N to n that; N to n to v; N with n for n; N with n that; N with n to v; '+\
            'adj N; N on n to inf; from N to N; N to inf; N as to wh; n N; N for n to inf; in N of n; '+\
            'on N of; on N of n; amount N').split('; ') # v out of N; v n out of N; N of n as n; N of n to n; N of n with n; N on n for n; N on n to v; 
nounpat += ['N %s -ing' % prep for prep in pgPreps] + \
            ['N %s n' % prep for prep in pgPreps] + \
            ['v N %s n' % prep for prep in pgPreps] + \
            ['v %s N' % prep for prep in pgPreps]

adjpat = ('ADJ adj; ADJ and adj; ADJ as to wh; ADJ against n; ADJ for n to inf; ADJ n; ADJ to inf; n ADJ; '+\
        'ADJ enough; ADJ enough for n; ADJ enough for n to v; ADJ enough n; amount ADJ; '+\
        'ADJ enough n for n; ADJ enough n for n to v; ADJ enough n that; ADJ enough to v; '+\
        'ADJ for n to v; ADJ from n to n; ADJ in color; ADJ -ing; v ADJ; '+\
        'ADJ in n as n; ADJ in n from n; ADJ in n to n; ADJ in n with n; ADJ in n as n; ADJ n for n; '+\
        'ADJ n to v; ADJ on n for n; ADJ on n to v; ADJ that; ADJ to v; ADJ to n for n; ADJ n for -ing; '+\
        'ADJ wh; ADJ on n for n; ADJ on n to v; ADJ that; ADJ to v; ADJ to n for n; ADJ n for -ing').split('; ')
adjpat += ['ADJ %s n'%prep for prep in pgPreps ] + \
           ['v it ADJ to inf']# + ['ADJ between pl-n']

pgPatterns = set(verbpat) | set(nounpat) | set(adjpat)


# nonAdv = {'later', 'already', 'nowhere', 'much', 'either', 'fast', 'well', 'so', 'thus', 'then', 'just', 'also', 'still', 'therefore', 'nearby', 'rather', 'sometimes', 'ever', 'always', 'inward', 'once', 'indeed', 'far', 'ago', 'again', 'here', 'there', 'together', 'even', 'next', 'first', 'yet', 'now', 'straight', 'all', 'too', 'often'}
selfWords = {'oneself', 'myself', 'ourselves', 'yourself', 'himself', 'herself', 'themselves'}
unWantColls = {'it', 'that', 'this', 'these', 'those', 'something', 'someone', 'some'}
AUXes = {'does', 'would', 'can', 'shall', 'may', 'should', 'are', 'is', 'were', 'have', 'might', 'do', 'dare', 'ought', 'could', 'must', 'need', 'had', 'been', 'am', 'was', 'be', 'did', 'will', 'has'}


def isPat(pat):
    if pat in pgPatterns: return True
    else: return pat.startswith('be V-ed') and len(pat.split())<=4   

maxDegree = 9
def direct_to_ngram(direct_labels): 
    return [ (k, k+degree) for k in range(0,len(direct_labels)) for degree in range(2, min(maxDegree, len(direct_labels)-k+1)) ]

def getKeywords(dependency):
    keywords = [ (iword, word, lemma, dep, tag, pos, ihead, NER) for iword, word, lemma, dep, tag, pos, ihead, NER in dependency\
                if not len(lemma) == 1 and word.isalpha() and lemma != '-PRON-' and \
                    (pos in ['VERB', 'NOUN', 'ADJ']) ]
    # return keywords
    # filter by cambridge
    keywordsInCamb = []
    for keyword in keywords:
        if keyword[2] not in cambridgeWords: continue
        if keyword[4][0] == 'V':
            if 'V' not in cambridgeDict[keyword[2]].keys(): continue
        elif (keyword[4][0] == 'N' or keyword[3] in ['pobj']):
            if 'N' not in cambridgeDict[keyword[2]].keys(): continue
        elif keyword[4][0] == 'J': 
            if 'ADJ' not in cambridgeDict[keyword[2]].keys(): continue
        if keyword[3] == 'pobj' and 'N' not in cambridgeDict[keyword[2]].keys(): continue
        keywordsInCamb.append(keyword)

    return keywordsInCamb

    
def getRoot(dependency):
    root = [ (iword, word, lemma, dep, tag, pos, ihead, NER) for iword, word, lemma, dep, tag, pos, ihead, NER in dependency if dep == 'ROOT' ]
    if not root: return []
    else: return root[0][0]

    
def dependency_to_GP(dependency, iroot):
    # return  [(keyword, pos, pat, coll, passive)...]
    def nounToColl(label):
        if label[-1] != ' ': 
            return '&lt;'+label[-1]+'&gt;'
        else: 
            if label[2] == '-PRON-': return label[2]
            else: 
                preps = [dependency[ichild] for ichild in childs[label[0]] if dependency[ichild][2] == 'of']
                if preps: # findRealNoun
                    nouns = [dependency[ichild] for ichild in childs[preps[0][0]] if dependency[ichild][3] in {'pobj'}] # 'pcomp', 'plmod' 
                    if nouns: 
                        if nouns[0][1][-1] == 's' or len(nouns[0][1]) == len(nouns[0][2]): return nouns[0][2]
                        else: return nouns[0][1].lower()
                if label[1][-1] == 's' or len(label[1]) == len(label[2]): return label[2]
                else: return label[1].lower()
    def hasAux(iword):
        return [dependency[ichild] for ichild in childs[iword] if dependency[ichild][3] == 'aux']
    def hasAuxPass(iword):
        return [dependency[ichild] for ichild in childs[iword] if dependency[ichild][3] == 'auxpass']
    def hasThat(iword):
        return [dependency[ichild] for ichild in childs[iword] if dependency[ichild][2] == 'that']
    def getNSubj(iword, ihead):
        nSubjs = [ label for label in dependency if label[3].startswith('nsubj') and \
                    (label[6] == iword or label[0] == ihead) ]
        return nSubjs[0] if nSubjs else ''
    def getPrepObj(iword):
        prepObjs = [dependency[ichild] for ichild in childs[iword] if dependency[ichild][3] in {'pcomp', 'pobj', 'plmod'}]
        return prepObjs[0] if prepObjs else ''
    def getPostPrep(iword):
        return dependency[iword+1] if dependency[iword+1][3] in ['prep'] else ''
    def getPrevPrep(iword):
        return dependency[iword-1] if dependency[iword-1][3] in ['prep'] else ''
    def getVB(iword):
        VBs = [dependency[ichild] for ichild in childs[iword] if dependency[ichild][4] == 'VB']
        return VBs[0] if VBs else ''
    def getWh(iword):
        wh = [dependency[ichild] for ichild in childs[iword] if dependency[ichild][4] in {'WRB', 'WP'}]
        return wh[0] if wh else ''
    def isObj(iword):
        return dependency[iword][5] in ['NOUN', 'NUM']
    def modifyPat(pat, colls, adv, adj, amount, modN):
        adv = adv.replace('%', 'percent')
        adj = adj.replace('%', 'percent')
        amount = amount.replace('%', 'percent')
        modN = modN.replace('%', 'percent')
        colls = [ word.replace('%', 'percent') for word in colls ]

        if pat in ['adv V', 'V adv']:            return 'V adv', False, colls
        elif pat in ['V adj', 'V n adj']:        return pat, False, colls
        elif pat in ['be V-ed by n', 'be V-ed']: return 'V n', True, colls
        elif pat in ['adj N', 'n N', 'ADJ n', 'ADJ and adj', 'n ADJ']: return pat, False, colls 
        elif pat in ['adj n N']: 
            colls.remove(modN)
            return pat.replace(' n', ''), False, colls
        else:
            try:
                if adv: colls.remove(adv)
                if adj: colls.remove(adj)
                if amount: colls.remove(amount)
                if modN: 
                    colls.remove(modN)
                    pat = pat.replace('n N', 'N')
                if 'V' in pat: return pat.replace(' adv', ''), False, colls
                elif 'N' in pat: return pat.replace(' adj', '').replace(' amount', ''), False, colls
                elif 'ADJ' in pat: return pat.replace(' adj', '').replace(' and', ''), False, colls
            except:
                return

    GPs = set() 
    keywords = getKeywords(dependency)

    childs = defaultdict(lambda: [])
    for iword, word, lemma, dep, tag, pos, ihead, NER in dependency:
        if ihead != iword: childs[ihead].append(iword)

    for ikeyword, _, keyword, keyword_dep, _, keyword_pos, ikeyhead, _ in keywords:
        if keyword_pos == 'VERB': POS = 'V'
        elif keyword_pos == 'NOUN': POS = 'N'
        elif keyword_pos == 'ADJ': POS = 'ADJ'

        if POS == 'V': 
            direct_depend = [ labels for labels in dependency \
                                if (labels[6] == ikeyword or labels[0] == ikeyword) ] 
        elif POS == 'N': 
            direct_depend = [ labels for labels in dependency \
                                 if labels[6] == ikeyword or labels[0] == ikeyword or \
                                  (labels[0] == ikeyhead and labels[5] not in ['NOUN', 'ADJ']) ] 
        elif POS == 'ADJ':
            direct_depend = [ labels for labels in dependency \
                            if (labels[6] == ikeyword or labels[0] == ikeyword) or labels[0] == ikeyhead ] 
#         print(keyword, direct_depend)
        candidates = set()
        for start, end in direct_to_ngram(direct_depend):
#             print(direct_depend[start:end])
            if ikeyword not in { label[0] for label in direct_depend[start:end] }: continue

            pat = []; colls = []
            passSubj = ''; prt = ''; adv = ''
            adj = ''; amount = ''; modN = ''
            fail = False
            
            for iword, word, lemma, dep, tag, pos, ihead, NER in direct_depend[start:end]:
                # word = word.lower()
                word_label = (iword, word, lemma, dep, tag, pos, ihead, NER)
                gram = ''
                if iword == ikeyword:
                    if POS == 'V':
                        if hasAuxPass(iword) or (dep in ['acomp', 'acl', 'advcl'] and tag == 'VBN'):
                            bePassive = True
                        elif hasAux(iword):
                            auxlist = sorted(hasAux(iword).copy(), key=lambda x: iword-x[0])
                            if auxlist[0][2] not in AUXes and tag == 'VBN':
                                bePassive = True
                            else: bePassive = False
                        else: bePassive = False
                       
                        if bePassive:
                            gram = 'be V-ed'
                            nSubj = getNSubj(iword, ihead)
                            passSubj = nSubj[2] if nSubj else '' 
                        else:
                            gram = 'V'
                    elif POS == 'N' or dep in ['pobj']: gram = 'N'
                    elif POS == 'ADJ': gram = 'ADJ'
                elif (dep in ['prt'] or tag in ['RP']) and POS == 'V':
                    if iword == ikeyword+1:
                        prt = lemma
                    else:
                        gram = lemma
                elif dep in ['dative'] and lemma == 'to':
                    prepObj = getPrepObj(iword)
                    if prepObj: 
                        gram = 'to n'
                        colls += [nounToColl(prepObj)]
                    else:
                        gram = 'to'
                elif dep in ['advmod'] and tag[0] == 'W':
                    gram = 'wh'
                    colls += [lemma]
                elif dep in ['dobj', 'attr', 'dative', 'nsubj', 'pobj']: 
                    # 'npadvmod' sleep well tonight  and (pos[0] == 'N' or pos == 'PROPN' or pos == 'PRON')
                    # advmod  and (tag not in {'RB', 'RBR', 'RBS', 'JJ', 'JJS'})
                    if word in selfWords:
                        gram = 'pron-refl'
                    else: 
                        gram = 'n' 
                        colls += [nounToColl(word_label)]
                elif dep in ['nsubj'] and word == 'it':
                    gram = 'it' 
                elif dep in ['advcl'] and tag == 'VB':
                    if [ aux for aux in hasAux(iword) if aux[4] == 'TO' ]:
                        gram = 'to inf'
                        colls += [word]
                elif dep in ['xcomp'] and tag == 'VB':
                    # need to check how to inf fixed
                    wh = getWh(iword)
                    if not wh:
                        gram = 'to inf'
                        colls += [word]
                    else:
                        gram = 'wh to inf'
                        colls += [wh[2], word]
                elif dep in ['relcl'] and pos in ['VERB']:
                    if [ aux for aux in hasAux(iword) if aux[4] == 'TO' ]:
                        if tag == 'VBN':
                            VB = getVB(iword)
                            if VB:
                                gram = 'to inf'
                                colls += [VB[1]+' '+word]
                        else:
                            gram = 'to inf'
                            colls += [word]
                elif dep in ['xcomp'] and tag == 'VBG':
                    if not hasAux(iword): # V to be -ing
                       gram = '-ing'
                       colls += [word]
                elif dep in ['advmod'] and tag == 'RB':
                    # if lemma in nonAdv: continue
                    if (abs(iword-ikeyword) <= 1) or (prt and abs(iword-ikeyword) <= 2):
                        gram = 'adv'
                        colls += [lemma]
                        adv = lemma 
                elif dep in ['ccomp', 'acl'] and ikeyword == ihead:
                    clauseSubj = getNSubj(iword, ihead)
                    if not clauseSubj: fail = True; break 

                    clauseSubjWord = clauseSubj[1]
                    clauseSubjLemma = clauseSubj[2]
                    clauseSubjNER = clauseSubj[-1]

                    if tag == 'VB' and ikeyhead != iword: 
                        if hasAux(iword) and not hasThat(iword): # 須排出to
                            gram = 'n' 
                            colls += ['something'] # nounToColl(clauseSubj)
                        elif hasThat(iword): 
                            gram = 'that n inf'
                            colls += [nounToColl(clauseSubj), word]
                        else: 
                            if clauseSubjWord == "'s": 
                                gram = 'inf'
                                colls += [word]
                            else:
                                gram = 'n inf'
                                colls += [nounToColl(clauseSubj), word]
                    elif tag == 'JJ':
                        if clauseSubjLemma:
                            gram = 'n adj'
                            colls += [nounToColl(clauseSubj), word]
                        else:
                            gram = 'adj'
                            colls += [lemma]
                    elif tag == 'VBG':
                        if clauseSubjLemma:
                            gram = 'n -ing'
                            colls += [nounToColl(clauseSubj), word]
                        else:
                            gram = '-ing'
                            colls += [word]
                    else:
                        mark = [dependency[ichild][2] for ichild in childs[iword] if dependency[ichild][3] == 'mark']
                        if mark: gram = mark[0]
                        wh = getWh(iword)
                        if wh: gram = 'wh'; colls += [dependency[wh[0]][2]] 
                elif (dep in ['range', 'nummod'] or tag == 'CD') and amount == '':
                    gram = 'amount'
                    colls += [lemma]
                    amount = lemma
                elif ((dep in ['acomp', 'amod', 'oprd'] and pos != 'NOUN') or (dep in ['compound', 'conj'] and tag == 'JJ')) and adj == '': # for VBN adj
                    gram = 'adj'
                    colls += [word]
                    adj = word
                elif (dep in ['prep', 'agent', 'dative'] and lemma in pgPreps) or word.lower() in ['as']: # closed prep
                    # parser bug
                    if word.lower() in 'as': lemma = word.lower()
                    if lemma == 'upon': lemma = 'on'
                    
                    if POS in ['V', 'ADJ']:
                        if iword - ikeyword < 0: continue  
                        if lemma in ['out']:
                            postPrep = getPostPrep(iword)
                            if postPrep: prepObj = getPrepObj(postPrep[0])
                            if postPrep and prepObj:
                                gram = lemma + ' ' + postPrep[2] + ' n'
                                colls += [nounToColl(prepObj)]
                            elif postPrep and not prepObj:
                                gram = lemma + ' ' + postPrep[2]
                            else:
                                gram = lemma 
                        else:
                            prepObj = getPrepObj(iword)
                            if prepObj:
                                gram = lemma + ' n'
                                if prepObj[3] in ['pcomp']:
                                    colls += ['something']
                                else:    
                                    colls += [nounToColl(prepObj)]
                            else:
                                gram = lemma
                    elif POS == 'N':
                        if lemma in ['of']:
                            if ihead != ikeyword and isObj(ihead): fail = True; break # bags of apple                        
                            prevPrep = getPrevPrep(iword)
                            prepObj = getPrepObj(iword)
                            if prevPrep and prepObj:
                                if prepObj[2] == 'VBG': 
                                    gram = prevPrep[2] + ' ' + lemma + ' -ing'
                                    colls += [prepObj[1]] 
                                else: 
                                    gram = prevPrep[2] + ' ' + lemma + ' n'
                                    colls += [nounToColl(prepObj)]
                            elif prevPrep and not prepObj:
                                gram = prevPrep[2] + ' ' + lemma
                            elif not prevPrep and prepObj:
                                gram =  lemma + ' n'
                                colls += [nounToColl(prepObj)]
                            else:
                                gram = lemma 
                        else:
                            prepObj = getPrepObj(iword)
                            if prepObj and prepObj[0] != ikeyword:
                                if prepObj[4] == 'VBG': 
                                    gram = lemma + ' -ing'
                                    colls += [prepObj[1]]
                                else: 
                                    gram = lemma + ' n'
                                    colls += [nounToColl(prepObj)]
                            else:
                                gram = lemma
                elif dep in ['compound', 'amod'] and pos == 'NOUN' and modN == '':
                    gram = 'n'
                    colls += [nounToColl(word_label)]
                    modN = nounToColl(word_label)
                elif pos == 'VERB' and POS == 'N':
                    gram = 'v'
                    colls += [lemma]
                elif dep == 'cc'and POS == 'ADJ':
                    gram = lemma

                if '-PRON-' in colls or '-PRON-' in passSubj: fail = True; break
                if gram != '': pat += [gram] 
                    
#                 print(str(pat)+gram)

            if not pat or fail: continue 
            
            try:
                strPat, passiveBy, mod_colls = modifyPat(' '.join(pat), colls.copy(), adv, adj, amount, modN)
            except:
                continue

#             print(keyword, pat, strPat, mod_colls)
            if strPat == 'v ADJ' and mod_colls == ['be']: continue
            if isPat(strPat):
                final_keyword = keyword + ' ' + prt if prt else keyword
                if strPat in {'V adv', 'adj N', 'amount N', 'n N', 'ADJ n', 'ADJ and adj'}: 
                    GPs.add((final_keyword, POS, strPat, '_'.join(mod_colls), False))
                else:
                    matchColls = passSubj if passSubj and passiveBy else '_'.join(mod_colls)
                    if passiveBy: candidates.add((final_keyword, POS, strPat, matchColls, True))# passSubj and
                    else: candidates.add((final_keyword, POS, strPat, matchColls, False)) 
                
        bestPat = sorted(list(candidates), key=lambda x: -len(re.split(r"[- ]", x[2])))[0] if candidates else ''
#         print(candidates)
        if bestPat:
            GPs.add(bestPat)
            
    return GPs
