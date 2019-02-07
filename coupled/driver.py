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
from os import chdir
from os import getcwd
from os import listdir
from os import mkdir
from shutil import copy
from shutil import copyfile
from subprocess import Popen
from sys import argv

from cleanupsas import cleanupsas
from cleanupsam import cleanupsam
from liquid_height_to_reactivity import liquid_height_to_reactivity
from write_sas_restart import write_sas_restart
from extract_sas_results import extract_sas_results
from write_sam_restart import write_sam_restart

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
fcorecsv = open(sas_core_csv, 'w')
[step,time,outlet_temp] = extract_sas_results(fsascsv,time,outlet_temp,fcorecsv)
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

reactivity = liquid_height_to_reactivity(liquid_height, reactivity_curve_position, reactivity_curve, reactivity)

print('outlet temp = '+str(outlet_temp[-1])+'K, liquid height = '+str(liquid_height)+'m, reactivity = '+str(reactivity[-1])+'$')

#####
#run sas and sam iteratively
#####
while step < maxsteps:
    #---sas---
    
    #open sas restart file
    copy(sas_restart_template, 'restarter.inp')
    fsas = open('restarter.inp', 'a')
    write_sas_restart(fsas,step,reactivity,time,dt)
    fsas.close()
    
    #run restart
    print('running sas...')
    p = Popen(['./run_sas_restart.sh'])
    p.wait()
    print('done')
    
    #extract core outlet temp and save sas results to new csv file
    p = Popen(['./post_process_sas.sh'])
    p.wait()
    [step,time,outlet_temp] = extract_sas_results(fsascsv,time,outlet_temp,fcorecsv)
    print('post processed')
    
    cleanupsas()
    
    #---sam---
    
    #open sam input file
    copy(sam_restart_template, 'restarter_sam.i')
    fsam = open('restarter_sam.i','a')
    write_sam_restart(fsam,time,outlet_temp)
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
    
    reactivity = liquid_height_to_reactivity(liquid_height, reactivity_curve_position, reactivity_curve, reactivity)
    
    print('outlet temp = '+str(outlet_temp[-1])+'K, liquid height = '+str(liquid_height)+'m, reactivity = '+str(reactivity[-1])+'$')

fsascsv.close()
fsamcsv.close()
fcorecsv.close()