def run_sam(version):

    from subprocess import Popen

    print('running sam...')
    if version == 'original':
        p = Popen(['./run_sam_original.sh'])
    elif version == 'restart':
        p = Popen(['./run_sam_restart.sh'])
    p.wait()
    print('done')