# coding: UTF-8
import urllib2
import sys
import codecs
import json
import MySQLdb

class Issues:
    def __init__(self,conn,cur,repo_id,repo_fullname):
        self.conn = conn
        self.cur = cur
        self.repo_id = repo_id
        self.repo_fullname = repo_fullname
    #84bcaa2aba96644d2604f86da91baa0105c15cfa adaccd3708619221656a9e13fc77bd8e5270c70a
    def get_issues(self,page_num):
        print "***************** getting issues of " + self.repo_fullname
        try:
            for number in range(page_num,10000):
                url = "https://api.github.com/repos/%s/issues?state=all&per_page=100&page=%d&access_token=6ac08b18aa04a36b602957be808a813900487173"%(self.repo_fullname,number)
                print number
                request_content = urllib2.Request(url)
                issue_content = urllib2.urlopen(request_content).read()
                if issue_content=="[]":
                    break
                else:
                    issues = json.loads(issue_content)
                    for issue in issues:
                        url = issue['url']
                        labels_url = issue['labels_url']
                        comments_url = issue['comments_url']
                        events_url = issue['events_url']
                        html_url = issue['html_url'].encode("utf-8")
                        issue_id = issue['id']
                        number = issue['number']
                        title = issue['title'].encode("utf-8")
                        user = issue['user']
                        labels = issue['labels']
                        state = issue['state']
                        locked = issue['locked']
                        if(issue['assignee']!=None):
                            assignee_id = issue['assignee']['id']
                        else:
                            assignee_id = '0'
                        milestone = issue['milestone']
                        comments = issue['comments']
                        created_at = issue['created_at'].replace("T"," ").replace("Z","")
                        updated_at = issue['updated_at'].replace("T"," ").replace("Z","")
                        if(issue['closed_at']!=None):
                            closed_at = issue['closed_at'].replace("T"," ").replace("Z","")
                        else:
                            closed_at = '0'
                        if(issue.has_key('pull_request')):
                            pull_request='1'
                        else:
                            pull_request='0'
                        if issue['body'] == None:
                            body = ""
                        else:
                            body = issue['body'].encode("utf-8")
                        author_id = issue['user']['id']

                        value = (str(self.repo_id),str(url),str(labels_url),str(comments_url),str(events_url),str(html_url),str(issue_id),str(number),str(title),str(user),str(labels),str(state),str(locked),str(assignee_id),str(milestone),str(comments), \
                                 str(created_at),str(updated_at),str(closed_at),str(pull_request),str(body),str(author_id))
                        try:
                            self.cur.execute("insert into issues (repo_id,url,labels_url,comments_url,events_url,html_url,issue_id,number,title,user,labels,state,locked,assignee_id,milestone,comments, \
                                 created_at,updated_at,closed_at,pull_request,body,author_id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",value)
                            self.conn.commit()
                        except MySQLdb.Error, e:
                            print "Mysql Error!", e;
                            print value
                    if len(issues)<100:
                        print len(issues)
                        break
        except Exception as e:
            print e

    def get_issue_comments(self,page_num):
        print "***************** getting issue_comments of " + self.repo_fullname
        try:
            for number in range(page_num, 10000):
                url = "https://api.github.com/repos/%s/issues/comments?per_page=100&page=%d&access_token=84bcaa2aba96644d2604f86da91baa0105c15cfa" % (self.repo_fullname, number)
                print number
                request_content = urllib2.Request(url)
                issue_content = urllib2.urlopen(request_content).read()
                if issue_content == "[]":
                    break
                else:
                    issues = json.loads(issue_content)
                    for issue in issues:
                        comment_id = issue['id']
                        issue_url = issue['issue_url']
                        sub_str = "https://api.github.com/repos/" + self.repo_fullname + "/issues/"
                        start=len(str(sub_str))
                        end=len(issue_url)
                        issue_num = issue_url[start:end]
                        created_at = issue['created_at'].replace("T", " ").replace("Z", "")
                        author_id = issue['user']['id']
                        author_login = issue['user']['login']
                        if issue['body'] == None:
                            body = ""
                        else:
                            body = issue['body'].encode("utf-8")
                        # print starred _at
                        value = (str(self.repo_id), str(comment_id), str(issue_num), created_at, author_id, author_login, body)

                        try:
                            self.cur.execute("insert into issue_comments (repo_id,comment_id,issue_num,created_at,author_id,author_login,body) values (%s,%s,%s,%s,%s,%s,%s)",value)
                            self.conn.commit()
                        except MySQLdb.Error, e:
                            print "Mysql Error!", e;
                            print value
                    if len(issues) < 100:
                        print len(issues)
                        break
        except Exception as e:
            print e
