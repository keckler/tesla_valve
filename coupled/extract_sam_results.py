def extract_sam_results(fsamcsv,version):

    if version == 'original':
        file = 'original_sam_csv.csv'
    elif version == 'restart':
        file = 'restarter_sam_csv.csv'

    with open(file) as sam_results:
        for row in sam_results:
            pass
    last_line = row
    fsamcsv.write(last_line)
    liquid_height = float(last_line.split(',')[-12])

    return liquid_height