#!/usr/bin/env python3

from DBHelper import DBHelper
import numpy as np
import time
from datetime import timedelta, datetime

db = DBHelper()
db.execute("SET group_concat_max_len = 18446744073709547520")

print("Fetching codes")
results = db.execute("""
    SELECT mailId, pid
    from mail_paragraphs
    where deleted = 0
    order by mailid, sortorder 
    """)

ms = {}
ps = {}
mailParas = {}
for res in results:
    if res[0] not in ms:
        ms[res[0]] = []

    if res[0] not in mailParas:
        mailParas[res[0]] = ""

    if res[1] not in ps:
        ps[res[1]] = set()

    ms[res[0]].append(res[1])
    ps[res[1]].add(res[0])
    mailParas[res[0]] += str(res[1]) + ","


totalemails = len(ms.keys())
now = datetime.now()
t = time.perf_counter()

print("Start parsing mails ({} mails and {} paragraphs)".format(len(ms.keys()), len(ps.keys())))
i, cnt, sum = 0, 0, 0

db.flush()

for i, m in enumerate(ms):
    #find smallest paragraph and build list of mails

    tms = {}
    matchmails = []
    smallestP, small = -1, 1000
    for p in ms[m]:
        for tm in ps[p]:
            if tm == m:
                continue
            if tm not in tms:
                tms[tm] = 0

            tms[tm] += 1
            if tms[tm] == len(ms[m]):
                matchmails.append(tm)

    matchmails = [mail for mail in matchmails if mailParas[m] in mailParas[mail]]

    if len(matchmails):


        cnt += 1
        sum += len(matchmails)

        sql = "update mail_paragraphs set deleted = 1 where mailId in ({}) and pid in ({})".format(
            ','.join(np.array(matchmails).astype(str)), ",".join(np.array(ms[m]).astype(str))
        )
        try:
            db.execute(sql)
        except Exception as e:
            print("Error in query: {}".format(str(e)))
            print(sql)

    if not i % 10000 and i > 0:

        db.flush()

        dt = time.perf_counter() - t
        etc = now + timedelta(seconds=(dt * totalemails / i))

        print(
            "{:>6} ({:>2}%) email checked, {:>6} redundant mails in {:>6} other mails found. Elapsed time: {:3.1f} min, ETC: {}"
                .format(i, int(100 * i / totalemails), cnt, sum, dt / 60, etc.strftime('%H:%M:%S')))


db.flush()