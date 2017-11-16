'''
   deals with local git operations
'''

import subprocess

class GitRepo():
    def __init__(self, changedir):
        self.git = 'git'
        self.dir = changedir

    def init(self):
        self.cmd = "init "
        self.runprocess()

    def add(self):
        '''
            Adds all data in the repository
        '''
        self.cmd = 'add --all'
        self.runprocess()

    def commit(self, repo, commitmsg=None):
        '''
           Create a generic commit message
        '''
        
        if commitmsg is not None:
            self.cmd = commitmsg
        else:
            self.cmd = "commit -am '{0}'".format(repo)

        self.runprocess()

    def remote(self, reponame):

         self.cmd = "remote add origin git@github.com:iaine/"+ reponame + ".git"
         self.runprocess()

    def push (self):
         self.cmd = "push origin master"
         self.runprocess()

    def runprocess(self):
        try:
            p = subprocess.check_output(self.git + " " + self.cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as cpe:
            print(cpe.cmd)
