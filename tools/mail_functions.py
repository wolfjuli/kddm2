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
        mailcontent = f.read()


    lines = mailcontent.replace("\r", "").split("\n")
    isBody = 0
    mailBody = ""
    lastKey = ""
    # print "mail has " + str(len(lines)) + " lines"
    for line in lines:
        if isBody == 1:
            mailBody += line + "\n"
            continue
        elif line == "":
            isBody = 1
            continue

        parts = line.split(": ")

        if len(parts) < 2 or line.startswith('	') or line.startswith(' '):
            #print "corrupt line in header in '" + filefullpath + "', last key: " + lastKey + ", line: " + line
            key = lastKey
            ret[lastKey] += "\n" + ": ".join(parts)
            #print "value now: " + ret[lastKey]
        else:
            key = parts[0]
            del parts[0]
            ret[key] = ": ".join(parts)

        lastKey = key


    ret['body'] = mailBody
    ret['filepath'] = filefullpath

    return ret


