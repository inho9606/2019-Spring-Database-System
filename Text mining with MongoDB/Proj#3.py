import datetime
import time
import sys
import MeCab
import operator
from pymongo import MongoClient
from bson import ObjectId
from itertools import combinations

stop_word = {  }
DBname = ''
conn = MongoClient('')
db = conn[DBname]
db.authenticate(DBname, DBname)
def p1():
    for doc in db['news_freq'].find():
        doc['morph'] = morphing(doc['content'])
        db['news_freq'].update({'_id': doc['_id']}, doc)

def p2(url):
    for doc in db['news_freq'].find():
        if doc['url'] == url:
            for m in doc['morph']:
                print m

def p3():
    col1 = db['news_freq']
    col2 = db['news_wordset']
    col2.drop()
    for doc in col1.find():
        new_doc = {  }
        new_set = set()
        for w in doc['morph']:
            new_set.add(w.encode('utf-8'))
        new_doc['word_set'] = list(new_set)
        new_doc['url'] = doc['url']
        col2.insert(new_doc)

def p4(url):
    for doc in db['news_wordset'].find():
        if doc['url'] == url:
            for word in doc['word_set']:
                print word

def p5(length):
    col1 = db['candidate_L'+str(length)]
    col1.drop()
    min_sup = db['news_freq'].count()*0.1
    if length == 1:
        wordset = {}
        for doc in db['news_wordset'].find():
            for word in doc['word_set']:
                if word not in wordset:
                    wordset[word] = 1
                else:
                    wordset[word] += 1
        for k in wordset.keys():
            if wordset[k]>=min_sup:
                dic={}
                dic['item_set']=[k]
                dic['support']=wordset[k]
                col1.insert(dic)

    elif length > 1:
        c = []
        for doc in db['candidate_L1'].find():
            for word in doc['item_set']:
                c.append(word)
       
        wordset = {}
        for doc in db['news_wordset'].find():
            new=[]
            for word in doc['word_set']:
                if word in c: new.append(word)
            new = list(combinations(new, length))
            for k in new:
                if frozenset(k) in wordset:
                    wordset[frozenset(k)] += 1
                else:
                    wordset[frozenset(k)] = 1
        for k in wordset.keys():
            if wordset[k]>=min_sup:
                dic={}
                dic['item_set']=list(k)
                dic['support']=wordset[k]
                col1.insert(dic)

def p6(length):
    c1 = dict()
    for doc in db['candidate_L1'].find():
        c1[frozenset(doc['item_set'])] = doc['support']
    c2 = dict()
    for doc in db['candidate_L2'].find():
        c2[frozenset(doc['item_set'])] = doc['support']
    if length == 2:
        for k in c2.keys():
            d=float(c2[k])
            l=list(k)
            e=c1[frozenset([l[0]])]
            f=c1[frozenset([l[1]])]
            pro = d/e
            if pro >= 0.5: print l[0], '=>', l[1], pro
            pro = d/f
            if pro >= 0.5: print l[1], '=>', l[0], pro

    if length == 3:
        c3 = dict()
        for doc in db['candidate_L3'].find():
            c3[frozenset(doc['item_set'])] = doc['support']
        
        for k in c3.keys():
            d=float(c3[k])
            l=list(k)
            for i in range(3):
                x=[l[i]]
                y=[l[(i+1)%3],l[(i+2)%3]]
                e=c1[frozenset(x)]
                f=c2[frozenset(y)]
                pro = d/e
                if pro >= 0.5: print x[0], '=>', y[0], ",", y[1], pro
                pro = d/f
                if pro >= 0.5: print y[0], ",", y[1], "=>", x[0], pro

def printMenu():
    print "0.CopyData"
    print "1. Morph"
    print "2. print morphs"
    print "3. print wordset"
    print "4. frequent item set"
    print "5. association rule"

def p0():
    col1 = db['news']
    col2 = db['news_freq']
    col2.drop()
    for doc in col1.find():
        contentDic = {  }
        for key in doc.keys():
            if key != "_id":
                contentDic[key] = doc[key]
        col2.insert(contentDic)

def make_stop_word():
    f = open('wordList.txt', 'r')
    while True:
        line = f.readline()
        if not line: break
        stop_word[line.strip('\n')] = line.strip('\n')
    f.close()

def morphing(content):
    t = MeCab.Tagger('-d/usr/local/lib/mecab/dic/mecab-ko-dic')
    nodes = t.parseToNode(content.encode('utf-8'))
    MorpList = []
    while nodes:
        if nodes.feature[0] == 'N' and nodes.feature[1] == 'N':
            w = nodes.surface
            if not w in stop_word:
                try:
                    w = w.encode('utf-8')
                    MorpList.append(w)
                except:
                    pass
        nodes = nodes.next
    return MorpList

if __name__ == '__main__':
    make_stop_word()
    printMenu()
    selector = input()
    if selector == 0:
        p0()
    elif selector == 1:
        p1()
        p3()
    elif selector == 2:
        url = str(raw_input('input news url:'))
        p2(url)
    elif selector == 3:
        url = str(raw_input('input news url:'))
        p4(url)
    elif selector == 4:
        length = int(raw_input('input length of the frequent item:'))
        p5(length)
    elif selector == 5:
        length = int(raw_input('input length of frequent item:'))
        p6(length)
