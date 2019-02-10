# run-down

main code: `/home/nlplab/pinyuan/104062121/GP_spacy/Hadoop`

pre-process code: `/home/nlplab/pinyuan/104062121/GP_spacy/sentParsed`

COCA sentence:` /home/nlplab/pinyuan/104062121/data/coca`

result: `/home/nlplab/pinyuan/104062121/GP_spacy/Hadoop/translate/GPs.txt, phrase.txt`



## pre-processing

1. re-organize parsed (add line number, combine one sentence into one line)

   - code `/home/nlplab/pinyuan/104062121/GP_spacy/sentParsed/parse_sent.py`

2. CAM index2exam.txt, cam(index_GP).txt

   - index2exam.txt: index map to en example, ch example, and phrase
   - cam(index_GP): this corresponding index's example has what grammar patterns

3. CAM need extract GP for every sentence map to index

4. score sentences: COCA

   - for choosing the best examples

   - `cat ../../../sentParsed/parsed_sent\(coca\).txt | python3 score.py`



## ten-ten

1. extract GP from every sentences (mapper)
2. find the top 10 (reducer)

need: camDict.txt

**code**

```shell
hadoop fs -rm -r -f pinyuan/ten-ten && yarn jar $HADOOP_STREAMING -files mapper.py,reducer.py,extractGP.py,../preprocess/Camb/camDict.txt -mapper 'python3 mapper.py' -reducer 'python3 reducer.py' -input pinyuan/parsed_sent\(coca\).txt -output pinyuan/ten-ten
rm -rf ten-ten && hadoop fs -get pinyuan/ten-ten
cat ten-ten/part* > ten-ten/total.txt
```



## GDEX

choose a best example for each pattern (record by line number)
1. extract GP (include in ten-ten) from every sentences (mapper)
2. calculate count and filter some seldom pattern, use pre-processed scores to choose GDEX (reducer)

mapper need: camDict.txt, ten-ten/
reducer need: score.txt, cam(index-GP).txt

**code**

```shell
hadoop fs -rm -r -f pinyuan/GDEX && yarn jar $HADOOP_STREAMING -files mapper.py,extractGP.py,../preprocess/Camb/camDict.txt,../ten-ten/ten-ten/total.txt -mapper 'python3 mapper.py' -input pinyuan/parsed_sent\(coca\).txt -output pinyuan/GDEX
rm -rf GDEX && hadoop fs -get pinyuan/GDEX
cat GDEX/part* > GDEX/maptotal.txt && cat GDEX/maptotal.txt | python3 reducer.py > output.txt
```

**transfer**

```shell
scp -P 2222 -r output.txt pinyuan@nlp-ultron.cs.nthu.edu.tw:104062121/GP_spacy/Hadoop/translate
```



## tranlate

For saving the memory, I preprocess(parse) the sentences and record the example by its line number instead of the whole sentence.

The following 2 files are the results of the pre-processing part.

- parsed_sent(coca).txt: line number map to sentence

- Camb/index2exam.txt: line number map to English example and its translation ...

Steps:

1. detokenize the example(refer by line number) we want to translate
2. translate by some tools(Bing, google translate...)
3. tag the source (COCA, CAM)



## testing

You can use `/home/nlplab/pinyuan/104062121/GP_spacy/test.ipynb` to test your extracting GP code