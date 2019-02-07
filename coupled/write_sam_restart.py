def write_sam_restart(fsam,time,outlet_temp):

    from glob import glob
    from os import path

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