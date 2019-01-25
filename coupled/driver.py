#!/usr/bin/python

############################################################################
#drives the coupling between SAS and SAM to update reactivity according to 
#the height of the liquid poison
############################################################################

#####
#imports
#####

from csv import reader
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

#sas_exec = '/Users/keckler/Documents/work/codes/mini-5.1/bin/mini-5.1-Darwin.x'
#sam_exec = 'sam-opt'
#sas_post_processor = '/Users/keckler/Documents/work/codes/mini-5.1/plot/PRIMAR4toCSV-Darwin.x'
sas_input_restart = ''
sas_restart = ''
sam_input_template = 'tesla_valve_tmp.i'

#####
#run codes iteratively
#####

#run original sas input
print('running original sas...')
p = Popen(['./run_sas_original.sh'])
p.wait()
print('ran original sas input')

#extract core outlet temp
p = Popen(['./post_process_sas.sh'])
p.wait()
print('post processed')
with open('PRIMAR4.csv') as sas_results:
    for row in sas_results:
        pass
last_line = row
time = float(last_line.split(',')[3])
outlet_temp = float(last_line.split(',')[5])

#clean up
try:
    remove('SAS.log')
    remove('SAS.pid')
except (OSError):
    pass
remove('PRIMAR4.dat')
remove('CHANNEL.dat')
move('RESTART.dat','RESTART.bin')

#open sam input file
copy(sam_input_template, 'tesla_valve.i')
fsam = open('tesla_valve.i','a+')

#put new end time into SAM
fsam.write('end_time = '+str(time)+'\n')
fsam.write('[]\n')
fsam.write('\n')

#put outlet temp into sam
fsam.write('[Functions]\n')
fsam.write('[./heat_fcn]\n')
fsam.write('type = PiecewiseLinear\n')
fsam.write("x = '0 1'\n")
fsam.write("y = '783 783'\n")
fsam.write("[../]\n")
fsam.write('[]')

fsam.close()

#run sam once
print('running sam...')
p = Popen(['./run_sam.sh'])
p.wait()
print('ran sam')

#extract liquid column height
with open('tesla_valve_csv.csv') as sam_results:
    for row in sam_results:
        pass
last_line = row
liquid_height = float(last_line.split(',')[-12])

#clean up
remove('tesla_valve_out_displaced.e')

#print just finished time step
print('time = '+str(time))

#convert liquid height to reactivity
nominal_height = 0.05
max_height = 3.0
max_reactivity = 1
if liquid_height < nominal_height:
    reactivity = 0.0
elif liquid_height < max_height:
    reactivity = (liquid_height - nominal_height) / (max_height - nominal_height) * max_reactivity
else:
    reactivity = max_reactivity

print(reactivity)