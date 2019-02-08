def tau_to_Hw(tau):

    tau_table = [1.0, 1.3, 1.4, 1.6, 2.1, 3.4, 6.2, 27.9]
    Hw_table = [5E3, 5E3, 4E3, 3E3, 2E3, 1E3, 5E2, 1E2]

    if tau < tau_table[0]:
        print('ERROR: tau is smaller than the smallest tabulated value!')
    elif tau < tau_table[-1]:
        for i in range(1,len(tau_table)):
            if tau < tau_table[i]:
                Hw = (tau - tau_table[i-1]) / (tau_table[i] - tau_table[i-1]) * (Hw_table[i] - Hw_table[i-1]) + Hw_table[i-1]
                break
    else:
        print('ERROR: tau is larger than the largest tabulated value!')

    return Hw