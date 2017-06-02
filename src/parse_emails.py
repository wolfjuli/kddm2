#!/usr/bin/python

from nltk.stem.snowball import SnowballStemmer
from sklearn import preprocessing
import pickle

from DBHelper import DBHelper
from mail_functions import *


def stem(row):
    stemmer = SnowballStemmer("english")
    names = row[0].lower().split("@")[0].split(".") + row[1].lower().split("@")[0].split(".")
    text = strip(row[2].lower(), names)
    words = [stemmer.stem(word) for word in text.split()]
    return " ".join(words)


def parse_mails(minFromMails = 1000):
    db = DBHelper()
    db.execute("SET group_concat_max_len = 18446744073709547520")
    results = db.execute("""
        select x.from, x.to, m.txt from
        (select z.mailId id, GROUP_CONCAT(y.paragraph separator ' ') txt
        from mail_paragraphs z
        join sha_paragraphs y
        on z.pid = y.id
        where z.deleted = 0
        group by z.mailId) m
        join
        (select a.mailId as id, a.from, a.to
        from from_to_mail a
        where a.from in
            (select aut.from
            from from_to_mail aut
            where aut.from rlike "^[A-Za-z0-9.-]+@enron.com$"
            group by aut.from
            having count(aut.from) > {})) x
        on m.id = x.id""".format(minFromMails))

    authors, recipients, emails, cnt, progress = [], [], [], 0, 0

    print("\n### PARSING EMAILS ###")
    filecount = db.rowcount
    for row in results:
        cnt += 1
        emails.append(stem(row))
        authors.append(row[0])
        recipients.append(row[1])

        tmp_progress = int(cnt*100 / filecount)
        if tmp_progress % 10 == 0 and progress != tmp_progress:
            progress = tmp_progress
            print("-- {} / {} emails parsed ({} %)".format(cnt, filecount, progress))

    le = preprocessing.LabelEncoder()
    le.fit(authors+recipients)
    enc_authors = le.transform(authors)
    enc_recipients = le.transform(recipients)

    print("-- {} emails parsed".format(cnt))
    pickle.dump(emails, open("./data/word_data.pkl", "wb"))
    pickle.dump(enc_authors, open("./data/authors.pkl", "wb"))
    pickle.dump(enc_recipients, open("./data/recipients.pkl", "wb"))
    pickle.dump(le.classes_, open("./data/classes.pkl", "wb"))
    return emails, enc_authors, enc_recipients, le.classes_

if __name__ == "__main__":
    parse_mails()
