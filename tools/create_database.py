#!/usr/bin/env python2.7


from mail_functions import *

import os
import cPickle
import time

print "gathering all file paths"
listOfAllFiles = []
if os.path.isfile('allFiles.pkl'):
    with open("allFiles.pkl", "r") as f:
        listOfAllFiles = cPickle.load(f)
if len(listOfAllFiles) < 1000 :
    listOfAllFiles = getListOfFiles("../maildir")
    with open("allFiles.pkl", "w") as f:
        cPickle.dump(listOfAllFiles, f)


print "parsing files"
all_mails = {}
if os.path.isfile('all_mails.pkl'):
    with open("all_mails.pkl", "r") as f:
        try:
            all_mails = cPickle.load(f)
        except:
            print "error when reading all_mails - file corrupt"

count = -1
for filename in listOfAllFiles:
    count += 1
    if filename in all_mails:
        print filename + " already in table"
        continue

    all_mails[filename] = getParsedContent(filename)
    createStructure(filename)

    if count % 10000 == 0:
        print "Writing out file. Please don't kill me now"
        with open("all_mails.pkl", "w") as f:
            cPickle.dump(all_mails, f)
        print "done, sleeping for 1 second"
        time.sleep(1)
        print "done sleeping"

with open("all_mails.pkl", "w") as f:
    cPickle.dump(all_mails, f)

with open('from_to_mails.pkl', "w") as f:
    cPickle.dump(from_to_mail, f)

with open('names.pkl', "w") as f:
    cPickle.dump(names, f)

print "Striping mails"
all_stripped_mails = all_mails.copy()

for frm in all_stripped_mails:
    for to in all_stripped_mails[frm]:
        all_stripped_mails[frm][to] = " ".join(filter(lambda w: w.lower() not in names, all_stripped_mails[frm][to].split()))

with open('all_stripped_mails.pkl', "w") as f:
    cPickle.dump(all_stripped_mails, f)


print "DONE!!! MOFO"

