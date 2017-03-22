#!/usr/bin/env python2.7

import os
import cPickle
import time

def getListOfFiles(root):

    ret = []
    for path, subdirs, files in os.walk(root):
        print path
        for file in files:
            ret += [os.path.join(path, file)]

        for subdir in subdirs:
            #print "calling for " + os.path.join(path, subdir)
            ret += getListOfFiles(os.path.join(path, subdir))

    return ret


def getParsedContent(filefullpath):
    ret = {}
    with open(filefullpath, 'r') as f:
        content = f.read()

    lines = content.split("\n")
    isBody = 0
    mailBody = ""
    lastKey = ""
    for line in lines:
        line = line.replace("\r", "")
        if isBody:
            mailBody += line + "\n"
            continue
        elif ":" not in line:
            isBody = 1
            continue

        parts = line.split(": ")

        if len(parts) < 2:
            print "corrupt line in header in '" + filefullpath + "', last key: " + lastKey + ", line: " + line
            key = lastKey
            ret[lastKey] += "\n" + ": ".join(parts)
            print "value now: " + ret[lastKey]
        else:
            key = parts[0]
            del parts[0]
            ret[key] = ": ".join(parts)

        lastKey = key

    ret['body'] = mailBody
    ret['filepath'] = filefullpath

    return ret

table = {}
from_to_mail = {}
def createStructure(filename):
    mail = table[filename]

    try:
        frm = mail['From']
    except:
        print "Error: this email has no sender ", mail['filepath']
        return

    if frm not in from_to_mail:
        from_to_mail[frm] = {}

    try:
        recipients = mail['To'].replace("\n", "").replace("\r", "").split(",")
    except:
        print "Error: this email has no recipient ", mail['filepath']
        return

    for to in recipients:
        if to not in from_to_mail[frm]:
            from_to_mail[frm][to] = []
            from_to_mail[frm][to] += mail['Subject'] + "\n\n" + mail['body']


print "gathering all file paths"
if os.path.isfile('allFiles.pkl'):
    with open("allFiles.pkl", "r") as f:
        listOfAllFiles = cPickle.load(f)
else:
    listOfAllFiles = getListOfFiles("../maildir")
    with open("allFiles.pkl", "w") as f:
        cPickle.dump(listOfAllFiles, f)


print "parsing files"
table = {}
if os.path.isfile('parsedFiles.pkl'):
    with open("parsedFiles.pkl", "r") as f:
        table = cPickle.load(f)

count = -1
for filename in listOfAllFiles:
    count += 1
    if filename in table:
        print filename + " already in table"
        continue

    table[filename] = getParsedContent(filename)
    createStructure(filename)

    if count % 10000 == 0:
        print "Writing out file. Please don't kill me now"
        with open("parsedFiles.pkl", "w") as f:
            cPickle.dump(table, f)
        print "done, sleeping for 1 second"
        time.sleep(1)
        print "done sleeping"

with open("parsedFiles.pkl", "w") as f:
    cPickle.dump(table, f)

with open('from_to_mails.pkl', "w") as f:
    cPickle.dump(from_to_mail, f)

print "DONE!!! MOFO"

