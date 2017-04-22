#!/usr/bin/env python3
from DBHelper import DBHelper
import numpy as np
import time
from datetime import timedelta, datetime

db = DBHelper()
db.execute("SET group_concat_max_len = 18446744073709547520")

print("Fetching codes")
results = db.execute("""
    SELECT mailId, GROUP_CONCAT(pid SEPARATOR ',') as sha, count(*) c
    from kddm2.mail_paragraphs
    where deleted = 0
    group by mailId
    having c > 1
    """)
totalemails = db.rowcount

cnt, sum, dt, mails = 0, 0, 0, []
base = [r[1] for r in results]

print("Finding redundancies in {} emails.".format(totalemails))
t = time.perf_counter()
now = datetime.now()

for i, row in enumerate(results):
    c = base.count(row[1])
    if c > 1:
        cnt += 1
        sum += c-1
        mails.append(row[0])

    if not i%10000 and i > 0:
        if mails != []:
            db.execute("update mail_paragraphs set deleted = 1 where mailId in ({})"
                           .format(','.join(np.array(mails).astype(str))), True)
        mails = []
        dt = time.perf_counter() - t
        etc = now + timedelta(seconds=(dt * totalemails / i))

        print("{:>6} ({:>2}%) email checked, {:>6} redundant mails in {:>6} other mails found. Elapsed time: {:3.1f} min, ETC: {}"
              .format(i, int(100*i/totalemails), cnt, sum, dt/60, etc.strftime('%H:%M:%S')))

if mails != []:
    db.execute("update mail_paragraphs set deleted = 1 where mailId in ({})"
            .format(','.join(np.array(mails).astype(str))), True)

print("{} redundant mails in {} other mails found. Elapsed time: {:3.1f} min".format(cnt, sum, dt/60))