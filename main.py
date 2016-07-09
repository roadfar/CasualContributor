import urllib2
import sys
import codecs
import json
import MySQLdb
from issues import Issues
from commits import Commits
from users import Users
import csv

from repos import Repos
import commits
import issues
from selenium import webdriver


def run(conn,cur,repo_id,repo_name,repo_fullname,deadline):
    try:
        # mIssues = Issues(conn,cur,repo_id,repo_fullname)
        # mIssues.get_issues(1)
        # mIssues.get_issue_comments(1)
        # mCommits = Commits(conn,cur,repo_id,repo_fullname)
        # mCommits.get_commits(1)
        # mCommits.get_commit_comments(1)
        mUsers = Users(conn,cur,repo_id,repo_name,repo_fullname,deadline)
        # # starts from 0
        # mUsers.updateUsers(0)
        # mUsers.connectUser()
        mUsers.getFollowerAndStar(0)
    except MySQLdb.Error, e:
        print "Mysql Error!", e;
    cur.close()
    conn.close()

def updateUser():
    conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='******',db='github')
    cur = conn.cursor()
    with open("/Users/dreamteam/Documents/study/sonar/results/oss developer evaluation/update_star_num.csv") as seed:
        reader = csv.reader(seed)
        next(reader,None)
        mUsers = Users(conn,cur,1,'1','1',"2016-03-01 00:00:00")
        for line in reader:
            mUsers.getFollowerAndStar(str(line[1]))

def updateGreenhand():
    conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='******',db='github')
    cur = conn.cursor()
    with open("/Users/dreamteam/Documents/study/sonar/results/oss developer evaluation/classified.csv") as seed:
        reader = csv.reader(seed)
        next(reader,None)
        for line in reader:
            print "updating " + line[0]
            user_id = str(line[1])
            repo_id = str(line[3])
            if line[9] == '2':
                green_hand = '0'
            else:
                green_hand = '1'
            try:
                cur.execute("update users set green_hand = '%s' where user_id = '%s' and repo_id = '%s';" % (green_hand,user_id,repo_id))
                conn.commit()
            except MySQLdb.Error, e:
                print "Mysql Error!", e;

# def updateStayedTime():
    # conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='******',db='github')
    # cur = conn.cursor()
    # with open("/Users/dreamteam/Documents/study/sonar/results/oss developer evaluation/update_stayed_time.csv") as seed:
    #     reader = csv.reader(seed)
    #     next(reader,None)
    #     for line in reader:
    #         print "updating " + line[1]
    #         user_id = str(line[2])
    #         repo_id = str(line[14])
    #         #select min and max time of commit
    #         try:
    #             cur.execute("select MIN(created_at),MAX(created_at) from commits where author_id = '%s' and repo_id = '%s';" % (user_id,repo_id))
    #             commit_time = cur.fetchall()
    #
    #             if line[9] == '2':
    #                 green_hand = '0'
    #             else:
    #                 green_hand = '1'
    #             try:
    #                 cur.execute("update users set green_hand = '%s' where user_id = '%s' and repo_id = '%s';" % (green_hand,user_id,repo_id))
    #                 conn.commit()
    #         except MySQLdb.Error, e:
    #             print "Mysql Error!", e;

def getPersonMainCasual():
    conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='******',db='github')
    cur = conn.cursor()
    writer=csv.writer(file('/Users/dreamteam/Documents/study/sonar/results/oss developer evaluation/new/person_main_casual.csv','wb'))
    with open("/Users/dreamteam/Documents/study/sonar/results/oss developer evaluation/new/co_author.csv") as seed:
        reader = csv.reader(seed)
        next(reader,None)
        for line in reader:
            gqi_main = 0
            gqi_casual = 0
            main = 0
            casual = 0
            email = str(line[0])
            try:
                cur.execute("select users.user_id,users.CCGN,users.long_term,users.repo_id,users.GQI,repos_filter.language from users,repos_filter where users.CCGN >0 and users.git_email = '%s' and users.repo_id = repos_filter.id;" % email)
                results = cur.fetchall()
                for result in results:
                #     if result[2] == 0:
                #         gqi_casual = gqi_casual + float(result[4])/float(result[1])
                #         casual = casual + 1
                #     elif result[2] == 1:
                #         gqi_main = gqi_main + float(result[4])/float(result[1])
                #         main = main + 1
                # if main > 0 and casual > 0:
                #     row = (float(gqi_casual)/casual,float(gqi_main)/main)
                    writer.writerow(result)
            except MySQLdb.Error, e:
                print "Mysql Error!", e;




if __name__ == '__main__':

    # updateUser()
    # getPersonMainCasual()
    # run(conn,cur,int(line[0]),str(line[1]),str(line[2]),"2016-03-01 00:00:00")
    # run(conn,cur,5152285,"okhttp","square/okhttp","2016-03-01 00:00:00")
    mRepos = Repos("/Users/dreamteam/Documents/git_repos/JavaScript/","/Users/dreamteam/Documents/study/sonar/script/JavaScript_Top_20.csv")
    mRepos.clone()
