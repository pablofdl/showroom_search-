# -*- coding: utf-8 -*-

import sys
import json
import time
from createIndex import CreateIndex
from queryIndex import QueryIndex

## Main class that controlls the execution
class Index:
    def __init__(self):
        ## We create an index of the documents to be able to search better and faster
        ## It's better if our document gets bigger
        ## The search will be much faster than a lineal method or a Python filter
        c = CreateIndex(sys.argv[1])
        self.products = c.createIndex()
        self.qi = QueryIndex()
    
    ## Make a simple linear search
    def simpleSearch(self, q):
        result = (filter(lambda x: q in x["title"] , self.data))
        return result

    ## Wrapper to time a function
    def timing(f):
        def wrap(*args):
            time1 = time.time()
            ret = f(*args)
            time2 = time.time()
            print '%s function took %0.3f ms' % (f.func_name, (time2-time1)*1000.0)
            return ret
        return wrap

    ## Search querying or index
    @timing
    def querySearch(self, q):
        return self.qi.querySearch(q)

if __name__=='__main__':
    if (sys.argv) and (len(sys.argv) > 1):
        print("Building Index")
        index = Index()
        print("Index Ready")
        while True:
            q=sys.stdin.readline().strip("\r\n")
            if q=='':
                break
            s = "Search for " + q + ":"
            print(s)
            result = index.querySearch(q)
            if result[0] != "":
                for x in result:
                    print(json.dumps(index.products[int(x)], sort_keys=True, indent=4))
            else:
                print("No results found")
