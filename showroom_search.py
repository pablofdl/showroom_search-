#!/usr/bin/python

import sys
import json

class QueryIndex:
    def __init__(self):
        self.data = []
        with open(sys.argv[1]) as f:
            for line in f:
                self.data.append(json.loads(line))
    def simpleSearch(self, q):
        result = (filter(lambda x: q in x["title"] , self.data))
        return result

if __name__=='__main__':
    if (sys.argv) and (len(sys.argv) > 1):
        qi = QueryIndex()
        while True:
            q=sys.stdin.readline()
            if q=='':
                break
            s = "Search for " + q.strip("\r\n") + ":"
            print(s)
            print(json.dumps(qi.simpleSearch(q.strip("\r\n")), sort_keys=True, indent=4))
