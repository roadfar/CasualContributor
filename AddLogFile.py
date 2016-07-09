__author__ = 'houxiang'

import os
import git
import csv


basepath = "/Users/dreamteam/Documents/git_repos"

def addLogFile(path):
    if os.path.isdir(path):
        try:
            os.chdir(path)
            logfile_path = path + "/logfile"
            if os.path.isfile(logfile_path):
                os.remove(logfile_path)
            os.system("git log -p --all --before={2016-03-01} >> logfile")
            print path + " add logfile successfully!"
        except:
            print "add lgofile failed !"
    else:
        print "this path is not a file !"


def app(seedfile):
    with open(seedfile) as seed:
        reader = csv.reader(seed)
        next(reader,None)
        for line in reader:
            proj_id = line[0]
            proj_name = line[1]
            proj_lang = line[11]
            path = basepath+"/"+proj_lang+"/"+proj_name
            addLogFile(path)



if __name__ == "__main__":
    app("/Users/dreamteam/Documents/study/sonar/script/js_top10.csv")