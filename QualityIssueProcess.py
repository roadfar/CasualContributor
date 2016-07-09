import os
import subprocess
import logging
import csv
import datetime
import json
import re
import urllib2
import MySQLdb
import pymysql

repo_base_path= "/Users/dreamteam/Documents/git_repos"

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='app.log',
                filemode='w')



conn = MySQLdb.connect(host='127.0.0.1',user='root',passwd='******',db='sonar')
cur = conn.cursor()

#put the commitors logs
email_list=[]
#put the lines of code made by contributors
contributor_efforts={}
#commits need tobe scaned
commits_need_scaned=[]


def commit_logs():
    cmd_log = ["git",
               "log",
               "--all",
               "--pretty=oneline"]
    proc = subprocess.Popen(cmd_log,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    stdout,stderr = proc.communicate()

    #commit_log = os.system("git log --pretty=oneline ")
    return stdout

def reset_history(log_index):
    #reset one version
    flag = os.system("git reset --hard "+ log_index)
    return flag

def sonar_measure():
    #sonar do the job in the root file
    simple_file_path = '.'
    #sonar=os.system("sonar-runner")
    #use the sonar to measure one version of the project
    sonar_cmd = 'sonar-runner -Dsonar.projectKey=my:' +project_id+\
                                'n_buggy'+' -Dsonar.projectName='+repo_name\
                                +' -Dsonar.projectVersion=1.0 -Dsonar.sources='+simple_file_path+\
                                ' -Dsonar.sourceEncoding=UTF-8 -Dsonar.language'+langugeHandler(project_lang)

    os.system(sonar_cmd)

def get_indexs():
    #put commits logs
    log_indexs=[]
    logs=commit_logs()
    log_arr = logs.split("\n")
    for line in log_arr:
        if line != " ":
            strs = line.split(" ")
            log_indexs.append(strs[0])
    log_indexs.reverse
    return log_indexs

def run(start):
    #get_indexs()
    log_indexs = get_indexs()
    # length = len(log_indexs)
    print "the count of all commits is" + str(len(log_indexs))
    for index in range(start,len(commits_need_scaned)):
        print "*************************************"+ str(index) +" the limit is "+str(len(commits_need_scaned))

        flag = reset_history(commits_need_scaned[index])
        if flag == 0:
            sonar_measure()
            updateIntroIssue()
            updateCommitSha(commits_need_scaned[index])


#get the effort of every commitors
def commit_effort_count():
    #git log --pretty='%aN' | sort | uniq -c | sort -k1 -n -r
    state = os.popen("git log --pretty='%aE' | sort | uniq -c | sort -k1 -n -r").read()
    writer=csv.writer(file('code_effort.csv','wb'))
    writer.writerow(['contributor','commit_count','add','removed','total'])

    tmp_arr = state.split("\n")
    for line in tmp_arr:
        csv_line=[]
        line = line.strip()
        arr = line.split(" ")
        if len(arr) == 2:
            email = line.split(" ")[1]
            csv_line.append(email)
            commit_count = line.split(" ")[0]
            csv_line.append(commit_count)
            code_efforts = os.popen("git log --author="+email+" --pretty=tformat: --numstat | awk '{ add += $1 ; subs += $2 ; loc += $1 - $2 } END { printf \"added lines: \%s removed lines : \%s total lines: \%s\\n\",add,subs,loc }' - ").read()
            add_remove_total = re.findall(r"\d+\.?\d*",code_efforts)
            print add_remove_total
            for num in add_remove_total:
                csv_line.append(num)
            writer.writerow(csv_line)


def get_need_scan_commits():
    log_indexs = get_indexs()
    commits_and_changed_files = {}
    #get index to do the git command
    for line in log_indexs:
        state = os.popen("git show "+line+" --stat").read()
       # print state
        tmp_arr =[]
        for item in state.split("\n"):
            if "|" in item:
                change_files = item.split("|")[0].strip()
                logging.info(change_files)
                tmp_arr.append(change_files)
        commits_and_changed_files[line] = tmp_arr
    pre_change_files = []

    for index,log in list(enumerate(log_indexs)):
        if index == len(log_indexs)-1:
            commits_need_scaned.append(log)
        elif index == 0:
            pre_change_files.extend(commits_and_changed_files[log])
            pre_commit = log
            continue
        change_files = commits_and_changed_files[log]
        if interlist(change_files,pre_change_files)==[]:
            pre_change_files.extend(change_files)
            pre_commit = log
        else:
            commits_need_scaned.append(pre_commit)
            pre_commit = log
            pre_change_files=change_files
    # print commits_need_scaned
    # print len(commits_need_scaned)
    # print len(log_indexs)

def interlist(a,b):
    ret = [val for val in a if val in b]
    return ret

#change the language to the way of sonar
def langugeHandler(project_lang):
    if project_lang == 'JavaScript':
        return 'js'
    elif project_lang == 'Python':
        return 'py'
    elif project_lang == 'Ruby':
        return 'rb'
    elif project_lang == 'Java':
        return 'java'

def updateIntroIssue():
    try:
        result = cur.execute("select kee from issues where commit_sha is null ;")
        issue_keys = cur.fetchall()
    except MySQLdb.Error, e:
        print "Mysql Error!", e;
    for issue_key in issue_keys:
        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
        url = "http://localhost:9000/api/issues/show?key=%s" % str(issue_key[0])
        request_content = urllib2.Request(url=url, headers=headers)
        try:
            issue_html = urllib2.urlopen(request_content)
            issue_content = issue_html.read()
            if issue_content=="[]":
                break
            else:
                issue = json.loads(issue_content)
                componentEnabled = issue['issue']['componentEnabled']
                if 'line' in issue['issue'].keys() and componentEnabled is True:
                    line = issue['issue']['line']
                    component = issue['issue']['component']
                    file = issue['issue']['componentLongName']
                    git_url = "http://localhost:9000/api/sources/scm?key=%s&from=%s&to=%s" % (str(component),str(line),str(line))
                    commit_req = urllib2.Request(url=git_url, headers=headers)
                    commit_html = urllib2.urlopen(commit_req)
                    commit_content = commit_html.read()
                    if commit_content !="[]":
                        git_info = json.loads(commit_content)
                        if len(git_info['scm']) > 0:
                            intro_sha = git_info['scm'][0][3]
                            intro_date = git_info['scm'][0][2]
                            intro_date = timeZoneTrans(intro_date)
                            updateCommitInfo(str(issue_key[0]),str(intro_sha),str(intro_date),str(file),str(line))
                    else:
                        print "can not get git info!"
                else:
                    print "component or line is not enabled"
                    continue
        except urllib2.HTTPError,e:
            print "************************ Error retrieving data:"
            print e.code
            print e.read()

def timeZoneTrans(str):
    mstr = str.replace('T',' ')
    time = mstr[0:19]
    zone = mstr[20:24]
    date_time = datetime.datetime.strptime(time,'%Y-%m-%d %H:%M:%S')
    delta_time_zone = divmod(int(zone),100)[0]
    if delta_time_zone > 0 and divmod(abs(delta_time_zone),10)[0] == 0:
        #like +0800
        b_date = date_time-datetime.timedelta(hours=divmod(abs(delta_time_zone),10)[1])
    elif delta_time_zone > 0 and divmod(abs(delta_time_zone),10)[0] > 0:
        #like +1000
        b_date = date_time-datetime.timedelta(hours=delta_time_zone)
    elif delta_time_zone < 0 and divmod(abs(delta_time_zone),10)[0] == 0:
        #like -0100
        b_date = date_time+datetime.timedelta(hours=divmod(abs(delta_time_zone),10)[1])
    elif delta_time_zone < 0 and divmod(abs(delta_time_zone),10)[0] > 0:
        #like -1000
        b_date = date_time + datetime.timedelta(hours=abs(delta_time_zone))
    return datetime.datetime.strftime(b_date,'%Y-%m-%d %H:%M:%S')

#update the column of commit sha
def updateCommitInfo(kee,intro_sha,intro_date,intro_file,line):

    try:
        cur.execute("update issues set intro_sha = '%s', intro_date='%s', intro_file='%s',intro_line='%s' where kee = '%s';" % (intro_sha,intro_date,intro_file,line,kee))
        conn.commit()
    except MySQLdb.Error, e:
        print "Mysql Error!", e;

#update the column of commit sha
def updateCommitSha(commit_sha):

    try:
        cur.execute("update issues set commit_sha = '%s' where commit_sha is null;" % commit_sha)
        conn.commit()
    except MySQLdb.Error, e:
        print "Mysql Error!", e;

def updateRepo_id(repo_id):
    try:
        cur.execute("update issues set repo_id = '%s' where repo_id is null;" % repo_id)
        # logging.info("mysql status is "+str(result))
        conn.commit()
    except MySQLdb.Error, e:
        print "Mysql Error!", e;

def app(seed_file):
     with open(seed_file) as seed:
        reader = csv.reader(seed)
        next(reader, None)
        for line in reader:
            print line[0]
            global project_id,repo_name,project_lang
            project_id = line[0]
            repo_name = line[1]
            project_lang = line[11]
            #compose the project path
            path = repo_base_path + "/"+project_lang+"/"+repo_name
            #check if the path is right
            if os.path.isdir(path):
                os.chdir(path)
            else:
                print path+" is wrong !please check it again !"
            #get the code efforts of every contributor
            # commit_effort_count()
            #first get the commits which we need to measure
            get_need_scan_commits()
            #reset to one version and measure
            run(0)
            updateRepo_id(str(project_id))


if __name__ == '__main__':
    app('/Users/dreamteam/Documents/study/sonar/script/negative_contributor_measurement/python_top10.csv')