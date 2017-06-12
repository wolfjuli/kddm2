#!/usr/bin/python

from sklearn import preprocessing
import pickle

from DBHelper import DBHelper
from helper_functions import *


def parse_mails(min_mails = 100):
    db = DBHelper()
    print("\n### RETRIEVING DATA FROM DATABASE ###")
    db.execute("SET group_concat_max_len = 18446744073709547520")
    results = db.execute("""
    select x.from, x.to, m.txt
    from
      (select z.mailId id, GROUP_CONCAT(y.paragraph separator ' ') txt
       from mail_paragraphs z
         join sha_paragraphs y
           on z.pid = y.id
       where z.deleted = 0
       group by z.mailId) m
      join
        (select a.mailId as id, a.from, a.to
         from from_to_mail a
         join (select aut.from f, aut.to t
                from from_to_mail aut
                where aut.from rlike "^[A-Za-z0-9.-]+@enron.com$"
                and aut.to rlike "^[A-Za-z0-9.-]+@enron.com$"
                and mailId in
                  (select mailId from mail_paragraphs where deleted = 0)
                group by f, t
                having count(*) > {0}) b
        on a.from = b.f
        and a.to = b.t) x
    on m.id = x.id;
    """.format(min_mails))

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

    print("-- {} emails from/to {} addresses parsed".format(cnt, len(le.classes_)))
    pickle.dump(emails, open("./data/word_data.pkl", "wb"))
    pickle.dump(np.array(enc_authors), open("./data/authors.pkl", "wb"))
    pickle.dump(np.array(enc_recipients), open("./data/recipients.pkl", "wb"))
    pickle.dump(np.array(le.classes_), open("./data/classes.pkl", "wb"))
    return emails, enc_authors, enc_recipients, le.classes_

if __name__ == "__main__":
    parse_mails()
