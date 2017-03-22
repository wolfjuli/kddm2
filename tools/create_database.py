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

all_mails = {}
names = []
from_to_mail = {}
def createStructure(filename):
    mail = all_mails[filename]

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

    try:

        name_parts = ''.join([i for i in mail['X-From'] if i.isalpha() or i == " "]).split(" ") + \
                     ''.join([i for i in mail['X-To']   if i.isalpha() or i == " "]).split(" ")

        add = [n.tolower() for n in name_parts if n not in names and len(n) > 2]

    except:
        print "Error while trying to strip out names of mail (maybe no X-from or X-To?)"


print "gathering all file paths"
if os.path.isfile('allFiles.pkl'):
    with open("allFiles.pkl", "r") as f:
        listOfAllFiles = cPickle.load(f)
else:
    listOfAllFiles = getListOfFiles("../maildir")
    with open("allFiles.pkl", "w") as f:
        cPickle.dump(listOfAllFiles, f)


print "parsing files"
all_mails = {}
if os.path.isfile('all_mails.pkl'):
    with open("all_mails.pkl", "r") as f:
        all_mails = cPickle.load(f)

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

print "Striping mails"
all_stripped_mails = all_mails.copy()

for frm in all_stripped_mails:
    for to in all_stripped_mails[frm]:
        all_stripped_mails[frm][to] = " ".join(filter(lambda w: w.tolower() not in names, all_stripped_mails[frm][to].split()))

with open('all_stripped_mails.pkl', "w") as f:
    cPickle.dump(all_stripped_mails, f)


print "DONE!!! MOFO"

