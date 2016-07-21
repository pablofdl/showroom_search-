#!/usr/bin/env python

import sys
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

    def getStopwords(self):
        f = open(self.stopwordsFile, 'r')
        stopwords = [line.rstrip() for line in f]
        self.sw = dict.fromkeys(stopwords)
        f.close()
        
    ## Returns the formatted Term
    def getTerms(self, line):
        line = line.lower()
        line = re.sub(r'[^a-z0-9 ]',' ',line) #put spaces instead of non-alphanumeric characters
        line = line.split()
        line = [x for x in line if x not in self.sw]  #eliminate the stopwords
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
        for term in self.index.iterkeys():
            postinglist = []
            for p in self.index[term]:
                docID = p[0]
                positions = p[1]
                postinglist.append(':'.join([str(docID) ,','.join(map(str,positions))]))
            print >> f, ''.join((term,'|',';'.join(postinglist)))
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
            #build the index for the current page
            termdictPage = {}
            for position, term in enumerate(terms):
                try:
                    termdictPage[term][1].append(position)
                except:
                    termdictPage[term] = [pageid, array('I',[position])]
            #merge the current page index with the main index
            for termpage, postingpage in termdictPage.iteritems():
                self.index[termpage].append(postingpage)
            pagedict=self.parseCollection()
        self.writeIndexToFile()
        return self.products
