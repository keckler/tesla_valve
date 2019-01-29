#!/usr/bin/python

############################################################################
#drives the coupling between SAS and SAM to update reactivity according to 
#the height of the liquid poison
############################################################################

#####
#user inputs
#####

maxsteps = 10000
nominal_height = 0.005
max_height = 3.0
max_reactivity = -1
dt = 0.01
initial_outlet_temp = 783

#####
#initializations
#####

time = [0.0] #vector to store previous time steps
outlet_temp = [initial_outlet_temp] #vector to store previous outlet temps
reactivity = [0.0] #vector to store previous ARC insertion reactivities calculated by SAM

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
sam_restart_template = 'restarter_sam_tmp.i'
sas_restart_template = 'restarter_sas_tmp.inp'
sas_cumulative_csv = 'sas_cumulative_csv.csv'

#####
#print header
#####
print('#########################################################################')
print('SAS-SAM coupled calculation')
print('#########################################################################')

#####
#first run of each code
#####

#run original sas input
print('running original sas...')
p = Popen(['./run_sas_original.sh'])
p.wait()
print('done')

#extract core outlet temp and save sas results to new csv file
p = Popen(['./post_process_sas.sh'])
p.wait()
fsascsv = open(sas_cumulative_csv, 'w')
with open('PRIMAR4.csv') as sas_results:
    for row in sas_results:
        fsascsv.write(row)
last_line = row
step = int(last_line.split(',')[0])
time.append(float(last_line.split(',')[3]))
outlet_temp.append(float(last_line.split(',')[4]))
print('post processed')

#clean up
try:
    remove('SAS.log')
    remove('SAS.pid')
except (OSError):
    pass
remove('PRIMAR4.dat')
remove('CHANNEL.dat')
move('RESTART.dat','RESTART.bin')

#run sam once
print('running sam...')
p = Popen(['./run_sam_original.sh'])
p.wait()
print('done')

#extract liquid column height
with open('original_sam_csv.csv') as sam_results:
    for row in sam_results:
        pass
last_line = row
liquid_height = float(last_line.split(',')[-12])

#clean up
remove('original_sam_out_displaced.e')

#print just finished time step
print('completed step = '+str(step)+', time = '+str(time[-1]))
print('\n')

#convert liquid height to reactivity
if liquid_height < nominal_height:
    reactivity.append(0.0)
elif liquid_height < max_height:
    reactivity.append((liquid_height - nominal_height) / (max_height - nominal_height) * max_reactivity)
else:
    reactivity.append(max_reactivity)

print('outlet temp = '+str(outlet_temp[-1])+'K, reactivity = '+str(reactivity[-1]))

#####
#run sas and sam iteratively
#####
while step < maxsteps:
    #---sas---
    
    #open sas restart file
    copy(sas_restart_template, 'restarter.inp')
    fsas = open('restarter.inp', 'a')
    
    #edit sas restart file
    fsas.write('INPCOM     1     0     1\n')
    fsas.write('    11     1'+str(step+1)+'\n')
    fsas.write('    -1\n')
    fsas.write('POWINA    12     1     1\n')
    fsas.write('    29     2'+'{:>12.5e}'.format(reactivity[-2])+'{:>12.5e}'.format(reactivity[-1])+'\n')
    fsas.write('    49     2'+'{:>12.5e}'.format(time[-1])+'{:>12.5e}'.format(time[-1]+dt)+'\n')
    fsas.write('    -1\n')
    fsas.write('ENDJOB    -1\n')
    fsas.close()
    
    #run restart
    print('running sas...')
    p = Popen(['./run_sas_restart.sh'])
    p.wait()
    print('done')
    
    #extract core outlet temp and save sas results to new csv file
    p = Popen(['./post_process_sas.sh'])
    p.wait()
    with open('PRIMAR4.csv') as sas_results:
        for row in sas_results:
            fsascsv.write(row)
    last_line = row
    step = int(last_line.split(',')[0])
    time.append(float(last_line.split(',')[3]))
    outlet_temp.append(float(last_line.split(',')[4]))
    print('post processed')
    
    #clean up
    try:
        remove('SAS.log')
        remove('SAS.pid')
    except (OSError):
        pass
    remove('PRIMAR4.dat')
    remove('CHANNEL.dat')
    move('RESTART.dat','RESTART.bin')
    
    #---sam---
    
    #open sam input file
    copy(sam_restart_template, 'restarter_sam.i')
    fsam = open('restarter_sam.i','a')
    
    #put new end time and restart file into SAM input
    fsam.write('end_time = '+str(time[-1])+'\n')
    fsam.write('restart_file_base = rf_cp/0001')#+'{:04d}'.format(step-1)+'\n')
    fsam.write('[]\n')
    fsam.write('\n')
    
    #put outlet temp into sam
    fsam.write('[Functions]\n')
    fsam.write('[./heat_fcn]\n')
    fsam.write('type = PiecewiseLinear\n')
    fsam.write("x = '")
    for t in time:
        fsam.write(' '+str(t))
    fsam.write("'\n")
    fsam.write("y = '")
    for t in outlet_temp:
        fsam.write(' '+str(t))
    fsam.write("'\n")
    fsam.write("[../]\n")
    fsam.write('[]')
    fsam.close()
    
    #run sam once
    print('running sam...')
    p = Popen(['./run_sam_restart.sh'])
    p.wait()
    print('done')
    
    #extract liquid column height
    with open('restarter_sam_csv.csv') as sam_results:
        for row in sam_results:
            pass
    last_line = row
    liquid_height = float(last_line.split(',')[-12])
    
    #clean up
    remove('restarter_sam_out_displaced.e')
    
    #print just finished time step
    print('completed step = '+str(step)+', time = '+str(time[-1]))
    print('\n')
    
    #convert liquid height to reactivity
    if liquid_height < nominal_height:
        reactivity.append(0.0)
    elif liquid_height < max_height:
        reactivity.append((liquid_height - nominal_height) / (max_height - nominal_height) * max_reactivity)
    else:
        reactivity.append(max_reactivity)

    #reactivity = -0.1
    
    print('outlet temp = '+str(outlet_temp[-1])+'K, reactivity = '+str(reactivity[-1]))

fsascsv.close()
