import urllib2
import sys
import codecs
import json
import MySQLdb

conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='******',db='github')
cur = conn.cursor()
cur.execute("select author,sha from commits where author_id is null")
commits = cur.fetchall()
print len(commits)
for commit in commits:
    if commit[0] is not None:
        temp = eval(commit[0])
        if temp is not None:
            author_id = temp['id']
            print str(author_id)
            try:
                cur.execute("update commits set author_id = '%s' where sha = '%s';" % (str(author_id),str(commit[1])))
                conn.commit()
            except MySQLdb.Error, e:
                print "Mysql Error!", e;
        else:
            print "find a none commit"