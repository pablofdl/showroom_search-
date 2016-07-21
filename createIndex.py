# -*- coding: utf-8 -*-

import sys
import math
import re
from collections import defaultdict
from array import array
import json

## Class that controls creating the index
class CreateIndex:
    def __init__(self, collfile):
        self.index = defaultdict(list)
        self.stopwordsFile = "stopwords.dat"
        self.collectionFile = collfile
        self.indexFile = "productsIndex.dat" 
        self.titleIndexFile="titleIndex.dat"
        self.titleIndex={}
        #term frequencies of terms in documents
        #documents in the same order as in the main index
        self.tf=defaultdict(list)          
        #document frequencies of terms in the corpus
        self.df=defaultdict(int)         
        self.numDocuments=0

    def getStopwords(self):
        f = open(self.stopwordsFile, 'r')
        stopwords = [line.rstrip() for line in f]
        self.sw = dict.fromkeys(stopwords)
        f.close()
        
    ## Returns the formatted Term
    def getTerms(self, line):
        line = line.lower()
        #put spaces instead of non-alphanumeric characters
        line = re.sub(r'[^a-z0-9 ]',' ',line) 
        line = line.split()
        #eliminate the stopwords
        line = [x for x in line if x not in self.sw]  
        return line

    ## Returns the data of the next product
    def parseCollection(self):
        doc = []
        for line in self.collFile:
            doc.append(json.loads(line))
            break
        if doc:
            d = doc[0]
            if d['brand'] == None:
                d['brand'] = ''
            self.products.append(d)
        else:
             d = {}     
        return d


    def writeIndexToFile(self):
        f = open(self.indexFile, 'w')
        print >>f, self.numDocuments
        self.numDocuments=float(self.numDocuments)
        for term in self.index.iterkeys():
            postinglist = []
            for p in self.index[term]:
                docID = p[0]
                positions = p[1]
                postinglist.append(':'.join([str(docID) ,','.join(map(str,positions))]))
            #print data
            postingData=';'.join(postinglist)
            tfData=','.join(map(str,self.tf[term]))
            idfData='%.4f' % (self.numDocuments/self.df[term])
            print >> f, '|'.join((term, postingData, tfData, idfData))
        f.close()
        #write title index
        f=open(self.titleIndexFile,'w')
        for pageid, title in self.titleIndex.iteritems():
            try:
                print >> f, pageid, title
            except UnicodeEncodeError:
                print >> f, pageid, re.sub(r'[^a-z0-9 ]',' ',title) 
        f.close()
        
    ## Creates the index
    def createIndex(self):
        self.collFile = open(self.collectionFile,'r')
        self.getStopwords()
        self.products = []
        pagedict = {}
        pagedict = self.parseCollection()
        i = 0
        #main loop creating the index
        while pagedict != {}:
            lines = '\n'.join((pagedict['title'],pagedict['description'],pagedict['supplier'],pagedict['brand']))
            pageid = i
            i += 1
            terms = self.getTerms(lines)
            self.titleIndex[i]=pagedict['title']
            self.numDocuments+=1
            #build the index for the current page
            termdictPage = {}
            for position, term in enumerate(terms):
                try:
                    termdictPage[term][1].append(position)
                except:
                    termdictPage[term] = [pageid, array('I',[position])]
            
            #normalize the document vector
            norm=0
            for term, posting in termdictPage.iteritems():
                norm+=len(posting[1])**2
            norm=math.sqrt(norm)
            
            #calculate the tf and df weights
            for term, posting in termdictPage.iteritems():
                self.tf[term].append('%.4f' % (len(posting[1])/norm))
                self.df[term]+=1
            
            #merge the current page index with the main index
            for termPage, postingPage in termdictPage.iteritems():
                self.index[termPage].append(postingPage)
            
            pagedict=self.parseCollection()
        self.writeIndexToFile()
        return self.products
