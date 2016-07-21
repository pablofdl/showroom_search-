# -*- coding: utf-8 -*-

import sys
import re
import copy
from collections import defaultdict

## Class that controls the searching in the index
class QueryIndex:
    def __init__(self):
        self.index = {}
        self.stopwordsFile = "stopwords.dat"
        self.indexFile = "productsIndex.dat"
        self.titleIndexFile = "titleIndex.dat"
        self.titleIndex={}
        self.tf={}      #term frequencies
        self.idf={}    #inverse document frequencies
        self.readIndex()  
        self.getStopwords()

    def intersectLists(self,lists):
        if len(lists) == 0:
            return []
        #start intersecting from the smaller list
        lists.sort(key=len)
        return list(reduce(lambda x,y: set(x)&set(y),lists)) 
    
    def getStopwords(self):
        f = open(self.stopwordsFile, 'r')
        stopwords = [line.rstrip() for line in f]
        self.sw = dict.fromkeys(stopwords)
        f.close() 

    # Gets the formatted term for the search
    def getTerms(self, line):
        line = line.lower()
        line = re.sub(r'[^a-z0-9 ]',' ',line) 
        line = line.split()
        line = [x for x in line if x not in self.sw]
        return line 
    
    def getPostings(self, terms):
        #all terms in the list are guaranteed to be in the index
        return [ self.index[term] for term in terms ]
    
    def getDocsFromPostings(self, postings):
        #no empty list in postings
        return [ [x[0] for x in p] for p in postings ]

    def readIndex(self):
        f=open(self.indexFile, 'r');
        #first read the number of documents
        self.numDocuments=int(f.readline().rstrip())
        for line in f:
            line = line.rstrip()
            #term='termID', postings='docID1:pos1,pos2;docID2:pos1,pos2'
            term, postings, tf, idf = line.split('|') 
            #postings=['docId1:pos1,pos2','docID2:pos1,pos2']
            postings = postings.split(';')
            #postings=[['docId1', 'pos1,pos2'], ['docID2', 'pos1,pos2']]
            postings = [x.split(':') for x in postings]
            #final postings list 
            postings = [ [int(x[0]), map(int, x[1].split(','))] for x in postings ]    
            self.index[term] = postings
            #read term frequencies
            tf=tf.split(',')
            self.tf[term]=map(float, tf)
            #read inverse document frequency
            self.idf[term]=float(idf)
        f.close()
     
    def dotProduct(self, vec1, vec2):
        if len(vec1)!=len(vec2):
            return 0
        return sum([ x*y for x,y in zip(vec1,vec2) ])
            
    def rankDocuments(self, terms, docs):
        #term at a time evaluation
        docVectors = defaultdict(lambda: [0]*len(terms))
        queryVector = [0]*len(terms)
        for termIndex, term in enumerate(terms):
            if term not in self.index:
                continue
            
            queryVector[termIndex] = self.idf[term]
            
            for docIndex, (doc, postings) in enumerate(self.index[term]):
                if doc in docs:
                    docVectors[doc][termIndex] = self.tf[term][docIndex]
                    
        #calculate the score of each doc
        docScores = [ [self.dotProduct(curDocVec, queryVector), doc] for doc, curDocVec in docVectors.iteritems() ]
        docScores.sort(reverse=True)
        resultDocs = [x[1] for x in docScores][:10]
        #print document titles instead if document id's
##        resultDocs = [ self.titleIndex[x] for x in resultDocs ]
        return resultDocs
##        return '\n'.join(resultDocs), '\n'


    def queryType(self,q):
        if '"' in q:
            return 'PQ'
        elif len(q.split()) > 1:
            return 'FTQ'
        else:
            return 'OWQ'

    def owq(self,q):
        '''One Word Query'''
        originalQuery = q
        q = self.getTerms(q)
        if len(q) == 0:
            return ''
        elif len(q) > 1:
            return self.ftq(originalQuery)
        term = q[0]
        if term not in self.index:
            return ''
        else:
            postings = self.index[term]
            docs = [x[0] for x in postings]
            p = self.rankDocuments(q, docs)
            return p
          
    def ftq(self,q):
        """Free Text Query"""
        q = self.getTerms(q)
        if len(q) == 0:
            return ''
        
        li = set()
        for term in q:
            try:
                postings = self.index[term]
                docs = [x[0] for x in postings]
                li = li|set(docs)
            except:
                #term not in index
                pass
        
        li = list(li)
        return self.rankDocuments(q, li)

    def pq(self,q):
        originalQuery = q
        q = self.getTerms(q)
        if len(q) == 0:
            return ''
        elif len(q) == 1:
            self.owq(originalQuery)
            return
        phraseDocs = self.pqDocs(q)
        return self.rankDocuments(q, phraseDocs)
        
    def pqDocs(self, q):
        phraseDocs = []
        length = len(q)
        #first find matching docs
        for term in q:
            if term not in self.index:
                #if a term doesn't appear in the index
                #there can't be any document maching it
                return []
        #all the terms in q are in the index
        postings = self.getPostings(q)    
        docs = self.getDocsFromPostings(postings)
        #docs are the documents that contain every term in the query
        docs = self.intersectLists(docs)
        #postings are the postings list of the terms in the documents docs only
        for i in xrange(len(postings)):
            postings[i] = [x for x in postings[i] if x[0] in docs]
        
        #check whether the term ordering in the docs is like in the phrase query
        
        #subtract i from the ith terms location in the docs
        #this is important since we are going to modify the postings list   
        postings = copy.deepcopy(postings)    
        
        for i in xrange(len(postings)):
            for j in xrange(len(postings[i])):
                postings[i][j][1] = [x-i for x in postings[i][j][1]]
        
        #intersect the locations
        result = []
        for i in xrange(len(postings[0])):
            li = self.intersectLists( [x[i][1] for x in postings] )
            if li == []:
                continue
            else:
                result.append(postings[0][i][0])
        
        return result

    def querySearch(self, q):
        qt = self.queryType(q)
        if qt == 'OWQ':
            result = self.owq(q)
        elif qt == 'FTQ':
            result = self.ftq(q)
        elif qt == 'PQ':
            result = self.pq(q)
        return result
