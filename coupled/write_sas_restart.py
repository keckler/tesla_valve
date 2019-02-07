def write_sas_restart(fsas,step,reactivity,time,dt):

    fsas.write('INPCOM     1     0     1\n')
    fsas.write('    11     1'+str(step+1)+'\n')
    fsas.write('    -1\n')
    fsas.write('POWINA    12     1     1\n')
    fsas.write('    29     2'+'{:>12.5e}'.format(reactivity[-2])+'{:>12.5e}'.format(reactivity[-1])+'\n')
    fsas.write('    49     2'+'{:>12.5e}'.format(time[-1])+'{:>12.5e}'.format(time[-1]+dt)+'\n')
    fsas.write('    -1\n')
    fsas.write('ENDJOB    -1\n')