#!/usr/bin/env python2.7
from string import maketrans, punctuation

from src.mail_functions import *

import pickle



allFiles = getListOfFiles('../../maildir')
count = 0
columnNames = {}
parsedFiles = {}
for file in allFiles:
    count += 1


    if file.translate(maketrans("", ""), punctuation) in parsedFiles:
        #print "skip " + file
        continue

    parsedFiles[file.translate(maketrans("", ""), punctuation)] = 1

    #print "working on " + file
    parsed = getParsedContent(file)

    for key in [p.lower() for p in parsed.keys() if p.lower() not in columnNames and p != ""]:
        print "found new key " + key
        columnNames[key.lower()] = parsed['filepath']

    if count % 10000 == 0:
        print "checked " + str(count) + " files"


with open('columnNames.pkl', 'w') as f:
    pickle.dump(columnNames, f)

print columnNames