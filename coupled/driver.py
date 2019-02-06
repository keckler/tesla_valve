#!/usr/bin/python

############################################################################
#drives the coupling between SAS and SAM to update reactivity according to 
#the height of the liquid poison
############################################################################

#####
#user inputs
#####

maxsteps = 10000
nominal_height = 0.005 #resting height of lithium column during steady-state
below_core_height = 0.2 #temperature increase needed for ARC system to reach bottom of active core
reactivity_curve_position = [0,    0.11808,    0.17712,    0.23616,    0.29684,    0.35588,    0.41492,    0.47396,    0.533,    0.59204,    0.65108,    0.71012,    0.76916,    0.82984,    0.88888,    0.94792,    1.00696,    1.066] #height of lithium column in active core
reactivity_curve = [0,    -0.0084,    -0.0392,    -0.0843,    -0.1423,    -0.2114,    -0.2894,    -0.3739,    -0.4622,    -0.5515,    -0.6392,    -0.7223,    -0.7983,    -0.8648,    -0.9198,    -0.9615,    -0.9886,    -1] #reactivity in dollars
dt = 0.01
initial_outlet_temp = 796

#adjust the reactivity curve positions for the region below the core
for i in range(0,len(reactivity_curve_position)):
    reactivity_curve_position[i] = reactivity_curve_position[i] + below_core_height - nominal_height

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
from glob import glob
from os import chdir
from os import getcwd
from os import listdir
from os import mkdir
from os import path
from shutil import copy
from shutil import copyfile
from subprocess import Popen
from sys import argv

from cleanupsas import cleanupsas
from cleanupsam import cleanupsam

#####
#locations of files
#####

sam_restart_template = 'restarter_sam_tmp.i'
sam_cumulative_csv = 'sam_cumulative_csv.csv'
sas_restart_template = 'restarter_sas_tmp.inp'
sas_cumulative_csv = 'sas_cumulative_csv.csv'
sas_core_csv = 'sas_core_csv.csv'

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

fcorecsv = open(sas_core_csv, 'w')
with open('WholeCore.csv') as core_results:
    for row in core_results:
        fcorecsv.write(row)

print('post processed')

cleanupsas()

#run sam once
print('running sam...')
p = Popen(['./run_sam_original.sh'])
p.wait()
print('done')

#extract liquid column height
fsamcsv = open(sam_cumulative_csv,'w')
with open('original_sam_csv.csv') as sam_results:
    for row in sam_results:
        fsamcsv.write(row)
last_line = row
liquid_height = float(last_line.split(',')[-12])

cleanupsam()

#print just finished time step
print('completed step = '+str(step)+', time = '+str(time[-1]))
print('\n')

#convert liquid height to reactivity
if liquid_height < reactivity_curve_position[0]:
    reactivity.append(0.0)
elif liquid_height < reactivity_curve_position[-1]:
    for i in range(1,len(reactivity_curve_position)):
        if liquid_height < reactivity_curve_position[i]:
            reactivity.append((liquid_height - reactivity_curve_position[i-1]) / (reactivity_curve_position[i] - reactivity_curve_position[i-1]) * (reactivity_curve[i] - reactivity_curve[i-1]) + reactivity_curve[i-1])
            break
else:
    reactivity.append(reactivity_curve[-1])

print('outlet temp = '+str(outlet_temp[-1])+'K, liquid height = '+str(liquid_height)+'m, reactivity = '+str(reactivity[-1])+'$')

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
            pass
    last_line = row
    fsascsv.write(last_line)
    
    step = int(last_line.split(',')[0])
    time.append(float(last_line.split(',')[3]))
    outlet_temp.append(float(last_line.split(',')[4]))

    with open('WholeCore.csv') as sas_results:
        for row in sas_results:
            pass
    fcorecsv.write(row)

    print('post processed')
    
    cleanupsas()
    
    #---sam---
    
    #open sam input file
    copy(sam_restart_template, 'restarter_sam.i')
    fsam = open('restarter_sam.i','a')
    
    #put new end time and restart file into SAM input
    fsam.write('end_time = '+str(time[-1])+'\n')
    fsam.write('restart_file_base = '+max(glob('rf_cp/*'),key=path.getctime).split('.')[0])#+'{:04d}'.format(step-1)+'\n')
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
    
    #extract liquid column height and write all results to cumulative csv file
    with open('restarter_sam_csv.csv') as sam_results:
        for row in sam_results:
            pass
    last_line = row
    fsamcsv.write(last_line)
    liquid_height = float(last_line.split(',')[-12])
    
    cleanupsam()
    
    #print just finished time step
    print('completed step = '+str(step)+', time = '+str(time[-1]))
    print('\n')
    
    #convert liquid height to reactivity
    if liquid_height < reactivity_curve_position[0]:
        reactivity.append(0.0)
    elif liquid_height < reactivity_curve_position[-1]:
        for i in range(1,len(reactivity_curve_position)):
            if liquid_height < reactivity_curve_position[i]:
                reactivity.append((liquid_height - reactivity_curve_position[i-1]) / (reactivity_curve_position[i] - reactivity_curve_position[i-1]) * (reactivity_curve[i] - reactivity_curve[i-1]) + reactivity_curve[i-1])
                break
    else:
        reactivity.append(reactivity_curve[-1])
    
    print('outlet temp = '+str(outlet_temp[-1])+'K, liquid height = '+str(liquid_height)+'m, reactivity = '+str(reactivity[-1])+'$')

fsascsv.close()
fsamcsv.close()
fcorecsv.close()