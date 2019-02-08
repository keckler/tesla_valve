def normalized_flow_to_tau(normalized_flow,tau0):

    import math

    tau = tau0 * ( 4.24 * math.exp(-26.44*normalized_flow) + 2.074 * math.exp(-0.729*normalized_flow) )

    return tau