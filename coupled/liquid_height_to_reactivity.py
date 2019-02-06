def liquid_height_to_reactivity(liquid_height, reactivity_curve_position, reactivity_curve, reactivity):
    if liquid_height < reactivity_curve_position[0]:
        reactivity.append(0.0)
    elif liquid_height < reactivity_curve_position[-1]:
        for i in range(1,len(reactivity_curve_position)):
            if liquid_height < reactivity_curve_position[i]:
                reactivity.append((liquid_height - reactivity_curve_position[i-1]) / (reactivity_curve_position[i] - reactivity_curve_position[i-1]) * (reactivity_curve[i] - reactivity_curve[i-1]) + reactivity_curve[i-1])
                break
    else:
        reactivity.append(reactivity_curve[-1])

    return reactivity