#!/usr/bin/python

############################################################################
#drives the coupling between SAS and SAM to update reactivity according to 
#the height of the liquid poison
############################################################################

#####
#imports
#####

from os import chdir
from os import getcwd
from os import listdir
from os import mkdir
from os import remove
from shutil import copy
from shutil import copyfile
from shutil import move
from subprocess import Popen
from sys import argv

#####
#locations of files
#####

sas_exec = '/Users/keckler/Documents/work/codes/mini-5.1/bin/mini-5.1-Darwin.x'
sam_exec = 'sam-opt'
sas_post_processer = ''
sas_input_original = 'original.inp'
sas_input_restart = ''
sas_restart = ''
sam_input = ''

#####
#convert liquid level to reactivity
#####

pos_tab = []
reac_tab = []

#####
#run codes iteratively
#####

#run original sas input
p = Popen(['./run_sas_original.sh'])
p.wait()

try:
    remove('SAS.log')
    remove('SAS.pid')
except (OSError):
    pass

remove('PRIMAR4.dat')
remove('CHANNEL.dat')
move('RESTART.dat','RESTART.bin')

print('ran original sas input')

#extract core outlet temp
