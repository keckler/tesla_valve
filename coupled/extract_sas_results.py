def extract_sas_results(fsascsv,time,outlet_temp,fcorecsv,flow):
    
    with open('PRIMAR4.csv') as sas_results:
            for row in sas_results:
                pass
    last_line = row
    fsascsv.write(last_line)
    
    step = int(last_line.split(',')[0])
    time.append(float(last_line.split(',')[3]))
    outlet_temp.append(float(last_line.split(',')[4]))
    flow.append(float(last_line.split(',')[5]))
    
    with open('WholeCore.csv') as sas_results:
        for row in sas_results:
            pass
    fcorecsv.write(row)

    return (step,time,outlet_temp,flow)