import urllib2
import sys
import codecs
import json
import MySQLdb
#commit_comments process
conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='******',db='github')
cur = conn.cursor()
cur.execute("select id,user from commit_comments")
commit_comments = cur.fetchall()
print len(commit_comments)
for commit in commit_comments:
    temp = eval(commit[1])
    user_id = temp['id']
    print str(commit[0])
    try:
        cur.execute("update commit_comments set author_id = '%s' where id = '%s';" % (str(user_id),str(commit[0])))
        conn.commit()
    except MySQLdb.Error, e:
        print "Mysql Error!", e;
