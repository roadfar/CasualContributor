# coding: UTF-8
import sys
import codecs
import json
import MySQLdb
import datetime
import urllib2
import git
import gitdb
import time
import re
import csv
import os

reload(sys)
sys.setdefaultencoding('utf-8')



def getAllGitAuthors(repo):
    path = '/Users/dreamteam/Documents/git_repos/Java/'+repo
    if os.path.isdir(path):
        os.chdir(path)
    else:
        print path+" is wrong !please check it again !"
    state = os.popen("git log --all --before={2016-3-1} --pretty='%aE=%an' | sort | uniq -c | sort -k1 -n -r").read()
    author_list = state.split("\n")
    # authors = unicode(str(repo_git.log('--before={2016-03-01} --pretty="%an %ae" '))).encode("utf-8")
    # author_list = authors.split('\n')
    author_results = []
    for author in author_list:
        author = author.split('=')
        if len(author) == 2:
            email = author[0].split(' ')[1]
            name = str(author[1]).replace("'","").replace(",","")
            author_results.append((name,email))
    print repo+":"+str(len(author_results))+"---------------------------------"
    return author_results

def getAllGithubUsers(cur,repo_id,deadline):

    cur.execute("select distinct user from commit_comments where repo_id = '%d' and created_at < '%s';" % (repo_id,deadline))
    commit_comment_authors = cur.fetchall()
    results = []
    for author in commit_comment_authors:
        temp = eval(author[0])
        results.append(temp['login'])

    cur.execute("select distinct author_login from issue_comments where repo_id = '%d' and created_at < '%s';" % (repo_id,deadline))
    issue_comment_authors = cur.fetchall()
    for author in issue_comment_authors:
        if author[0] not in results:
            results.append(author[0])

    cur.execute("select distinct user from issues where repo_id = '%d' and created_at < '%s';" % (repo_id,deadline))
    issue_authors = cur.fetchall()
    results = []
    for author in issue_authors:
        temp = json.loads(str(author[0]))
        if temp['login'] not in results:
            results.append(temp['login'])

    cur.execute("select commit, author from commits where repo_id = '%d' ;" % repo_id)
    commit_authors = cur.fetchall()
    for author in commit_authors:
        if len(author[1]) > 1:
            #pay attention to the unicode of commit message
            commit = json.loads(unicode(str(author[0]),"ISO-8859-1"))
            author = json.loads(str(author[1]))
            deadline = datetime.datetime.strptime(str(deadline), '%Y-%m-%d %H:%M:%S')
            commit_time = datetime.datetime.strptime(str(commit['author']['date']).replace("T"," ").replace("Z",""), '%Y-%m-%d %H:%M:%S')
            if (deadline - commit_time).total_seconds() > 0 and author['login'] not in results:
                results.append(author['login'])
    return results

# connect the gihub users and the git users:eamil and name
# def getConnectedUsers(repo_id, repo_name):

def updateUsers(conn,cur,repo_id,deadline):
    authors = getAllGithubUsers(cur,repo_id,deadline)
    for author in authors:
        url = "https://api.github.com/users/%s?access_token=adaccd3708619221656a9e13fc77bd8e5270c70a" % str(author)
        request_content = urllib2.Request(url)
        author_url = urllib2.urlopen(request_content).read()
        if author_url != "[]":
            author_json = json.loads(author_url)
            login = author_json['login']
            user_id = author_json['id']
            type = author_json['type']
            name = author_json['name']
            company = author_json['company']
            blog = author_json['blog']
            location = author_json['location']
            email = author_json['email']
            hireable = author_json['hireable']
            bio = author_json['bio']
            created_at = author_json['created_at'].replace("T"," ").replace("Z","")
            value = (str(login),str(user_id),str(type),str(name),str(company),str(blog),str(location),str(email),str(hireable),str(bio),str(created_at))
            print value
            try:
                cur.execute("insert into users (login,user_id,type,name,company,blog,location,email,hireable,bio,created_at) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",value)
                conn.commit()
            except MySQLdb.Error, e:
                print "Mysql Error!", e;

def getCoUsers(conn,cur,repo_id,repo_name,deadline):
    # github_users = getAllGithubUsers(cur,repo_id,deadline)
    git_users = getAllGitAuthors(repo_name)
    # matched_set = []

    #connect by commit
    cur.execute("select commit, author_id from commits where repo_id = '%s' and author_id is not null;" % str(repo_id))
    commits = cur.fetchall()
    for commit in commits:
        #pay attention to the unicode of commit message
        # commit_temp = json.loads(unicode(str(commit[0]),"ISO-8859-1"))
        commit_temp = eval(str(commit[0]))
        author_id = str(commit[1])
        deadline = datetime.datetime.strptime(str(deadline), '%Y-%m-%d %H:%M:%S')
        commit_time = datetime.datetime.strptime(str(commit_temp['author']['date']).replace("T"," ").replace("Z",""), '%Y-%m-%d %H:%M:%S')
        if (deadline - commit_time).total_seconds() > 0:
            updateUserGitInfo(conn,cur,author_id,str(commit_temp['author']['name']),str(commit_temp['author']['email']));
    #connect by name and eamil
    try:
        cur.execute("select name,email,user_id from users where repo_id = '%s' and git_name is null or git_email is null" % repo_id)
        user_infos = cur.fetchall()
        for user_info in user_infos:
            if user_info[0] != 'None' or user_info[1] != 'None':
                for git_user in git_users:
                    github_name = str(user_info[0]).replace('"','').replace(' ','')
                    github_email = str(user_info[1]).replace('"','').replace(' ','')
                    git_name = str(git_user[0]).replace('"','').replace(' ','')
                    git_email = str(git_user[1]).replace('"','').replace(' ','')
                    if github_name == git_name or github_email == git_email:
                        print "find a user connected by name or email:******"
                        print github_name+"-"+git_name+"; "+git_email+"-"+github_email
                        updateUserGitInfo(conn,cur,str(user_info[2]),str(git_user[0]).replace('"',''),str(git_user[1]).replace('"',''))
    except MySQLdb.Error, e:
        print "Mysql Error!", e;


def updateUserGitInfo(conn,cur,user_id,git_name,git_email):
    try:
        # print git_name + " "+ git_email+ " "+user_id
        git_name = git_name.replace("'","").replace(",","")
        git_email = git_email.replace("'","").replace(",","")
        cur.execute("update users set git_name = '%s', git_email = '%s' where user_id = '%s';" % (git_name , git_email, user_id))
        conn.commit()
    except MySQLdb.Error, e:
        print "Mysql Error!", e;

conn = MySQLdb.connect(host='127.0.0.1', user='root', passwd='******', db='github')
cur = conn.cursor()
# updateUsers(conn,cur,2862290,'2016-01-01 00:00:00')
# authors = getAllGithubUsers(cur,2862290,'2016-01-01 00:00:00')niteshkhatri

with open('/Users/dreamteam/Documents/study/sonar/script/negative_contributor_measurement/python_top10.csv') as seed:
    reader = csv.reader(seed)
    next(reader, None)
    for line in reader:
        getCoUsers(conn,cur,line[0],line[1],'2016-03-01 00:00:00')
