# coding: UTF-8
import sys
import codecs
import csv
import git
from git import Repo

class Repos:
    def __init__(self,path,sample_path):
        self.path = path
        self.sample_path = sample_path

    def clone(self):
        with open(self.sample_path) as seed:
            reader = csv.reader(seed)
            next(reader, None)
            for line in reader:
                fullname = str(line[2])
                clone_url = "https://github.com/"+fullname+".git"
                temp_path = self.path + str(line[1]) + "/"
                print "*********** cloning "+fullname+" :"
                Repo.clone_from(clone_url, temp_path)