import urllib2
import sys
import codecs
import json
import MySQLdb
#commit_comments process
conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='******',db='github')
cur = conn.cursor()
cur.execute("select issue_id,user from issues")
issues = cur.fetchall()
print len(issues)
for issue in issues:
    temp = eval(issue[1])
    user_id = temp['id']
    print str(issue[0])
    try:
        cur.execute("update issues set author_id = '%s' where issue_id = '%s';" % (str(user_id),str(issue[0])))
        conn.commit()
    except MySQLdb.Error, e:
        print "Mysql Error!", e;
