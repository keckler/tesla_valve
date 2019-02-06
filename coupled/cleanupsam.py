def cleanupsam():
    
    from os import remove

    try:
        remove('original_sam_out_displaced.e')
        remove('original_sam_csv.csv')
    except OSError:
        remove('restarter_sam_out_displaced.e')
        remove('restarter_sam_csv.csv')
