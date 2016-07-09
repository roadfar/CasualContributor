# coding: UTF-8
import urllib2
import sys
import codecs
import json
import MySQLdb

class Pull_requests:
    def __init__(self,conn,cur,repo_id,repo_fullname):
        self.conn = conn
        self.cur = cur
        self.repo_id = repo_id
        self.repo_fullname = repo_fullname

    def get_pull_requests(self):
        print "***************** getting prs of " + self.repo_fullname
        try:
            result_list=[]
            for number in range(1,10000):
                url = "https://api.github.com/repos/%s/pulls?per_page=100&page=%d&access_token=adaccd3708619221656a9e13fc77bd8e5270c70a"%(self.repo_fullname,number)
                print number
                request_content = urllib2.Request(url)
                issue_content = urllib2.urlopen(request_content).read()
                if issue_content=="[]":
                    break
                else:
                    issues = json.loads(issue_content)
                    for issue in issues:
                        url = issue['url']
                        pull_request_id = issue['id']
                        html_url = issue['html_url'].encode("utf-8")
                        diff_url = issue['diff_url']
                        patch_url = issue['patch_url']
                        issue_url = issue['issue_url']
                        number = issue['number']
                        state = issue['state']
                        locked = issue['locked']
                        title = issue['title'].encode("utf-8")
                        user = issue['user']
                        body = issue['body'].encode("utf-8")
                        created_at = issue['created_at'].replace("T"," ").replace("Z","")
                        updated_at = issue['updated_at'].replace("T"," ").replace("Z","")
                        merge_commit_sha = issue['merge_commit_sha']
                        commits_url = issue['commits_url']
                        review_comments_url = issue['review_comments_url']
                        review_comment_url = issue['review_comment_url']
                        comments_url = issue['comments_url']
                        statuses_url = issue['statuses_url']
                        _links = issue['_links']

                        if(issue['closed_at']!=None):
                            closed_at = issue['closed_at'].replace("T"," ").replace("Z","")
                        else:
                            closed_at = '0'

                        if(issue['merged_at']!=None):
                            merged_at = issue['merged_at'].replace("T"," ").replace("Z","")
                        else:
                            merged_at = '0'

                        if(issue['assignee']!=None):
                            assignee = issue['assignee']['id']
                        else:
                            assignee = '0'

                        if(issue['milestone']!=None):
                            milestone = issue['milestone']
                        else:
                            milestone = '0'

                        value = (str(self.repo_id),str(url),str(pull_request_id),html_url,diff_url,patch_url,issue_url,str(number),str(state),str(locked), \
                                str(title), str(user), str(body), created_at, updated_at, merge_commit_sha, commits_url, review_comments_url, review_comment_url, \
                                comments_url, statuses_url, str(_links), str(closed_at), str(merged_at), str(assignee), str(milestone))
                        try:
                            self.cur.execute("insert into pull_requests (repo_id,url,pull_request_id,html_url,diff_url,patch_url,issue_url,number,state,locked, \
                                title, user, body, created_at, updated_at, merge_commit_sha, commits_url, review_comments_url, review_comment_url, \
                                comments_url, statuses_url, _links, closed_at, merged_at, assignee, milestone) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",value)
                            self.conn.commit()
                        except MySQLdb.Error, e:
                            print "Mysql Error!", e;
                            print value
                    if len(issues)<100:
                        print len(issues)
                        break
        except Exception as e:
            print e