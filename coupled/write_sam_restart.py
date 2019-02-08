def write_sam_restart(time,outlet_temp,sam_restart_template):

    from glob import glob
    from os import path
    from shutil import copy

    copy(sam_restart_template, 'restarter_sam.i')
    fsam = open('restarter_sam.i','a')

    #put new end time and restart file into SAM input
    fsam.write('end_time = '+str(time[-1])+'\n')
    fsam.write('restart_file_base = '+max(glob('rf_cp/*'),key=path.getctime).split('.')[0])
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