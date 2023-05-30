import numpy as np


def print_warning(message):
    print("Warning : "+message)


def print_error(message):
    print("Error : "+message)


def check_index(data_index):
    """Check that indexes are sorted properly.

    Parameters
    ----------
    data_index : An array related to phase index.

    Returns
    -------
    is_correct : True or False.

    """

    is_correct = True

    for i in range(len(data_index)):
        if int(data_index[i]) != i:
            print_error(f"Wrong index. You have use {data_index[i]} instead of {i}")
            is_correct = False
            break

    return is_correct


def check_phase(data_phases, nb_phases):
    """Check some constraints on phase description.

    Parameters
    ----------
    data_phases : An array related to phase description.
    nb_phases : Number of phases.

    Returns
    -------
    is_correct : True or False.

    """

    array = np.array(data_phases)
    list_index = array[:, 0]
    list_values = array[:, 1]

    is_correct = check_index(list_index)
    if is_correct:
        if list_values[0] != 0:
            print_error("The first phase must be set to 0 %")
            is_correct = False
        elif list_values[-1] != 100:
            print_error("The last phase must be set to 100 %")
            is_correct = False
        else:
            for i in range(1, nb_phases-1):
                if list_values[i] <= list_values[i-1]:
                    print_error("A phase should have a greater percentage value thane its predecessor")
                    is_correct = False
                    break

    return is_correct


def check_temperature(data_temperature, nb_phases):
    """Check some constraints on temperature description.

    Parameters
    ----------
    data_temperature : An array related to temperature description.
    nb_phases : Number of phases.

    Returns
    -------
    is_correct : True or False.

    """

    array = np.array(data_temperature)
    list_index = array[:, 0]
    list_values = array[:, 1]
    is_correct = False

    if len(array) < nb_phases:
        print_error("Some phases are not described in temperature.")
    elif len(array) > nb_phases:
        print_error("There are more phases described in temperature than existant phases.")
    else:
        is_correct = check_index(list_index)
        if is_correct:
            for i in range(0, nb_phases):
                if -273.15 > list_values[i]:
                    print_error("Impossible value for degree Celsius")
                    is_correct = False
                # According to classic data find on Web
                elif 180 > list_values[i]:
                    print_warning(f"Your temperature {list_values[i]} °C seems to be low")
                # According to classic data find on Web
                elif 220 < list_values[i]:
                    print_warning(f"Your nozzle temperature {list_values[i]} °C seems to be high")

    return is_correct


def check_speed(data_speed, nb_phases):
    """Check some constraints on speed description.

    Parameters
    ----------
    data_speed : An array related to speed description.
    nb_phases : Number of phases.

    Returns
    -------
    is_correct : True or False.

    """

    array = np.array(data_speed)
    list_index = array[:, 0]
    list_values = array[:, 1]
    is_correct = False

    if len(array) < nb_phases:
        print_error("Some phases are not described in temperature.")
    elif len(array) > nb_phases:
        print_error("There are more phases described in temperature than existant phases.")
    else:
        is_correct = check_index(list_index)
        if is_correct:
            for i in range(0, nb_phases):
                if 0 > list_values[i]:
                    print_error("Impossible negative speed")
                    is_correct = False

    return is_correct


def check_extrude(data_extrude):
    """Check some constraints on the extrude ratio parameter.

    Parameters
    ----------
    data_extrude : An array of parameters related to extrude ratios.


    Returns
    -------
    is_correct : True or False.

    """

    is_correct = False
    nb_parameters = len(data_extrude)

    if nb_parameters == 0:
        print_error("No parameter set for shifting position.")
    elif nb_parameters != 1:
        print_error("Incorrect parameters for extrusion. Only one line required. Use the following scheme :\n"
                    "Correction (%) : 0")
    else:
        is_correct = True

    return is_correct


def check_shift_pos(data_shift):
    """Check some constraints on shift position parameters.

    Parameters
    ----------
    data_shift : An array of parameters related to the shift in the position of the workpiece.

    Returns
    -------
    is_correct : True or False.

    """

    is_correct = False
    nb_parameters = len(data_shift)

    if nb_parameters == 0:
        print_error("No parameter set for shifting position.")
    elif nb_parameters != 2:
        print_error("Incorrect parameters for shifting position. Use the following scheme :\n"
                    "Shift_x (mm) : 0\nShift_y (mm) : 0")
    else:
        is_correct = True

    return is_correct


def check_heating(data_heating):
    """Check some constraints on the heating phase parameter.

    Parameters
    ----------
    data_heating : An array of parameters related to the heating phase.

    Returns
    -------
    is_correct : True or False.

    """

    is_correct = False
    nb_parameters = len(data_heating)

    if nb_parameters == 0:
        print_error("No parameter set for the heating phase.")
    elif nb_parameters != 1:
        print_error("Several parameters input for the heating phase. Keep only one")
    else:
        value = int(data_heating[0])
        if value != float(data_heating[0]):
            print_warning("You enter a float value for the heating parameter. It has been converted into int with a"
                          "lossy conversion.")
        if not 0 <= value <= 1:
            print_warning("Any non-zero value activate the heating phase. However, we recommend to use 1 for an "
                          "easier understanding")
        is_correct = True

    return is_correct


check_func = {
    0: check_phase,
    1: check_temperature,
    2: check_speed,
    3: check_extrude,
    4: check_shift_pos,
    5: check_heating
}


def check_parameter(parameter_array):
    """Check there is no nonsensical values in the parameters file.

    Parameters
    ----------
    parameter_array : The extracted values from the parameters file.

    Returns
    -------
    is_correct : True or False.

    """
    list_boolean = []

    nb_phases = len(parameter_array[0])

    for i in range(len(parameter_array)):
        if i < 3:
            list_boolean.append(check_func[i](parameter_array[i], nb_phases))
        else:
            list_boolean.append(check_func[i](parameter_array[i]))

    return False not in list_boolean
