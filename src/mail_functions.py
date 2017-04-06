# !/usr/bin/env python2.7

import os
import re
import nltk

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

def stripNames(text):
    """
    Strips all names of text, so "Hello Julian Wolf" becomes "Hello " (just works for english language)
    :param text: The text which will be transformed
    :return: guess what? text without names
    """

    tokens = nltk.word_tokenize(text)
    ret = text
    for name in [n[0] for n in nltk.pos_tag(tokens) if (n[1] == "NNP" or n[1] == "NNPS") and len(n[0]) > 1]:
        ret = ret.replace(name, "")

    return ret


def getParsedName(xAddress):
    """
    Returns an object with the fields firstName,middleNames, lastName,fullName,eMail of the given sender line as presented in the X-From or X-To line of mails. If multiple addresses are provided, please split them up beforehand, this function just works on a single user
    :param xAddress: the address line of a single person as presented in the x-from field
    :return: {firstName: string, lastName: string, fullName: string, eMail: string}
    """

    """
    Corner Cases:

    Andrea.P.Williams
        No Spaces. regex is eager - no meaningfull lastname. Better replace all dots with space in names before regexing


    """



    #Cases (ln = Last name, fn0 = first name, mn1..n = middle names 1..n):
    #Baughman Jr., Don </O=ENRON/OU=NA/CN=RECIPIENTS/CN=DBAUGHM> = ln mn1..n, fn0 <AD crap>
    #Baughman Jr., Don <don.baughman@enron.com> = ln mn1..n, fn0 <eMail>
    #ENL Member Services <ecenter@energynewslive.com> = fn0 mn1..n ln <eMail>
    #confirm@paypal.com = eMail
    #Richard Hrabal = fn0..n ln
    #"support@edgar-online.com" <support@edgar-online.com>@ENRON = "eMail" <eMail>@crap

    regex_email = "([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
    regex_murica_name = "([A-Za-z]+)([\ A-Za-z.]*),([\ A-Za-z]+)"
    regex_normal_name = "([A-Za-z]+)([\ A-Za-z.]*)([A-Za-z]+)"

    parts = xAddress.split(" <")


