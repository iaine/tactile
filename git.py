'''
   deals with local git operations
'''

import subprocess

class GitRepo():
    def __init__(self):
        self.git = 'git'

    def add(self, reponame):
        '''
            Adds all data in the repository
        '''
        self.cmd = ' add ' + reponame + '/*'
        return self.cmd

    def commit(self, repo, commitmsg=None):
        '''
           Create a generic commit message
        '''
        
        if commitmsg is not None:
            self.cmd = commitmsg
        else:
            self.cmd = "Commit " + repo

        return self.cmd

    def remote(self, reponame):

         self.cmd = "remote add origin git@github.com:iaine/"+ reponame + ".git"
         return self.cmd

    def push (self):
         self.cmd = "push origin master"
         return self.cmd

    def runprocess(self):
        try:
            p = subprocess.check_output(self.git + " " + self.cmd, shell=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as cpe:
            print(cpe.cmd)
