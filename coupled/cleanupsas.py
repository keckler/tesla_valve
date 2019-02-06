def cleanupsas():
    
    from os import remove
    from shutil import move

    try:
        remove('SAS.log')
        remove('SAS.pid')
    except (OSError):
        pass
    remove('PRIMAR4.dat')
    remove('PRIMAR4.csv')
    remove('CHANNEL.dat')
    remove('WholeCore.csv')
    move('RESTART.dat','RESTART.bin')
