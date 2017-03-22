# !/usr/bin/env python2.7

import os


def getListOfFiles(root):

    ret = []
    for path, subdirs, files in os.walk(root):
        #print path

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

    lines = content.replace("\r", "").split("\n")
    isBody = 0
    mailBody = ""
    lastKey = ""
    print "mail has " + str(len(lines)) + " lines"
    for line in lines:
        if isBody == 1:
            mailBody += line + "\n"
            continue
        elif line == "":
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
    global names
    global all_mails
    global from_to_mail

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


    try:
        from_to_mail[frm][to] += mail['Subject'] + "\n\n" + mail['body']
    except Exception, e:
        print mail['filepath'] + ": could not save mail in table: "+ str(e)  + "\n"

    try:

        name_parts = ''.join([i for i in mail['X-From'] if i.isalpha() or i == " "]).split(" ") + \
                     ''.join([i for i in mail['X-To']   if i.isalpha() or i == " "]).split(" ")
        names += [n.lower() for n in name_parts if n not in names and len(n) > 2]


    except Exception, e:
        print mail['filepath'] + ": Error while trying to strip out names " + str(e)

