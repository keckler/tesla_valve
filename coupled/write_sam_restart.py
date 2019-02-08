def write_sam_restart(time,outlet_temp,sam_restart_template,Hw):

    from glob import glob
    from os import path
    from shutil import copy

    copy(sam_restart_template, 'restarter_sam.i')
    fsam = open('restarter_sam.i','a')

    #put new end time and restart file into SAM input
    fsam.write('end_time = '+str(time[-1])+'\n')
    fsam.write('restart_file_base = '+max(glob('rf_cp/*'),key=path.getctime).split('.')[0]+'\n')
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
    fsam.write('[]\n')
    fsam.write('\n')

    #put heat source with updated Hw to represent changing tau
    fsam.write("[Components]\n")
    fsam.write("[./heat_source]\n")
    fsam.write("type = PBCoupledHeatStructure\n")
    fsam.write("HS_BC_type = 'Coupled Temperature'\n")
    fsam.write("#Ts_init = 783\n")
    fsam.write("dim_hs = 1\n")
    fsam.write("elem_number_radial = 1\n")
    fsam.write("heat_source_solid = 0\n")
    fsam.write("length = 0.1\n")
    fsam.write("material_hs = steel\n")
    fsam.write("name_comp_left = upper_reservoir\n")
    fsam.write("eos_left = potassium_eos\n")
    fsam.write("Hw_left = "+str(Hw)+"\n")
    fsam.write("T_bc_right = heat_fcn\n")
    fsam.write("orientation = '0 0 -1'\n")
    fsam.write("position = '0 0 3.15'\n")
    fsam.write("width_of_hs = 1E-3\n")
    fsam.write("[../]\n")
    fsam.write("[]\n")

    fsam.close()