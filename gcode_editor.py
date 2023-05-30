import numpy as np
import re

from check import check_parameter


def extract_values_from_file(parameter_file_path):
    """This function extracts the parameters that were entered by the user in the parameter file

    Parameters
    ----------
    parameter_file_path : The relative path of the parameter file to parse.

    Returns
    -------
    extracted_data : Extracted parameters in a list of numpy arrays for each type of parameter.
    number_phases : Number of phases.
    """

    # Extract the content from the file
    with open(parameter_file_path, 'r') as file:
        content = file.read()

    # Split the content for each type of parameter
    sections = content.split('------------------------------------------------------------------')

    # Remove leading/trailing whitespaces and empty sections
    sections = [section.strip() for section in sections if section.strip()]

    # Initialize extracted parameters
    extracted_data = []

    # Iterate through each section of parameter
    for section in sections:

        # Split each section into multiple lines and remove leading/trailing whitespaces
        phase_lines = section.split('\n')
        phase_lines = [line.strip() for line in phase_lines if line.strip()]

        # Initialise list
        values = []

        # Extract the data for each line that starts with "Phase"
        for line in phase_lines:

            if line.startswith('#'):
                # Comment line. Skip
                continue
            else:
                # Split the line in multiple parts
                line_parts = line.split(':')
                key = line_parts[0]
                value = line_parts[1]

                # Parameter associated with a phase
                if line.startswith('Phase'):

                    # Extract the number of phases
                    phase_number = int(key.split(' ')[1])

                    try:
                        # Append phase number and value to the array
                        values.append((phase_number, float(value)))
                    except Exception as e:
                        # Stop execution and indicates to the user the parameter is the wrong type
                        print(f"{e} : Invalid input, cannot be converted into a float. Stop execution")
                        exit()

                # Global parameter used for the whole workpiece.
                else:
                    # Append phase number and value to the array
                    try:
                        values.append(float(value))
                    except Exception as e:
                        print(f"{e} : Invalid input, cannot be converted into a float. Stop execution")
                        exit()

        # Append array to the list of arrays
        extracted_data.append(np.array(values))

    return extracted_data


def find_layer_info(gcode_file_path):
    """Given a G-code file sliced with software like PrusaSlicer, this function will parse the G-code and return the
    layer information.

    Parameters
    ----------
    gcode_file_path : The relative path of the G code file to parse.

    Returns
    -------
    layer_height  : Height of each layer.
    total_height  : Total height of the part.
    layer_count   : Total amount of layers.
    """

    # Initialize variables
    layer_height = 0
    layer_count = 0

    # Open G-code and read each line individually
    with open(gcode_file_path, "r") as file:
        for line in file:

            # Extract layer height
            if line.startswith("; layer_height"):
                layer_height = float(line.split("=")[1])
            
            # Extract amount of layers
            elif line.startswith(";LAYER_CHANGE"):
                layer_count += 1

    # Calculate total height
    total_height = layer_height * layer_count

    return layer_height, total_height, layer_count


def find_phase(height_pct, parameter_array):
    """Given the user parameters and current height percentage vs total height, this function will determine in which
     phase we are and of far in the phase we are (in percent).

    Parameters
    ----------
    height_pct : The current height vs total part height in percent.
    parameter_array : User parameters in the form of a list of numpy arrays.

    Returns
    -------
    phase_counter : Current phase at our layer height.
    phase_pct : How far we are in the current phase in percent.
    """

    # Calculate number of phases
    num_phases = len(parameter_array[0])

    # Iterate through the phases
    phase_data = parameter_array[0]

    # Initialize variables
    phase_counter, phase_pct = 0, 0

    for i in range(1, num_phases):

        # Get the start and end percentages for the current phase
        phase_start = phase_data[i-1, 1]
        phase_end = phase_data[i, 1]

        # Check if the height_pct is within the current phase
        if phase_start <= height_pct <= phase_end:
            phase_counter = i
            phase_pct = (height_pct-phase_start) / (phase_end-phase_start)

    return phase_counter, phase_pct


def evaluate_extrude_ratio(parameter_array):
    """

    Parameters
    ----------
    parameter_array : User parameters in the form of a list of numpy arrays.

    Returns
    -------
    extrude_ratio_array : An array of correction ratio for each phase to use to edit G-code.
    """

    # Get useful values
    temperature_array = parameter_array[1][:, 1]
    speed_ratio_array = parameter_array[2][:, 1]
    user_extrude_correction = float(parameter_array[3])

    # Compute mean for temperature and speed
    temp_mean = np.mean(temperature_array)
    speed_mean = np.mean(speed_ratio_array)

    # Compute theoretical expansion in each phase according to temperature and speed parameter
    theory_expansion = ((speed_ratio_array/speed_mean)*100 - (temperature_array/temp_mean)*100)/2

    # Find the worst expansion (absolute value)
    worst_abs_expansion = np.max(np.abs(theory_expansion))

    # Compute new correction ration for extrusion
    extrude_ratio_array = user_extrude_correction*(theory_expansion/worst_abs_expansion)

    return extrude_ratio_array


def modify_speed(modified_line_parts, parameter_array, phase_num, phase_pct):
    """Modify speed inside a G code line according to user parameters.

    Parameters
    ----------
    modified_line_parts : A split G code string.
    parameter_array : user parameters in the form of a list of numpy arrays
    phase_num : The number of the current phase
    phase_pct : the current height vs total part height in percent

    Returns
    -------

    """

    # Check if we are not in phase 0
    if phase_num > 0:

        # Iterate through each argument in the line
        for i in range(len(modified_line_parts)):

            # Check if it is a speed argument *********** Make it extract only nums instead of str ***************
            if modified_line_parts[i].startswith("F"):

                # Extract current speed
                current_speed = re.findall(r'\d+', modified_line_parts[i])
                current_speed = int(current_speed[0])

                # Calculate speed multiplier
                mult_start = parameter_array[2][phase_num-1, 1]
                mult_end = parameter_array[2][phase_num, 1]
                speed_mult = (mult_end-mult_start)*phase_pct + mult_start

                # Apply speed multiplier
                new_speed = current_speed * speed_mult/100

                # Apply new speed to line
                modified_line_parts[i] = "F" + str(new_speed)


def modify_temperature(modified_line_parts, parameter_array, phase_num, phase_pct):
    """Modify temperature inside a G code line according to user parameters

    Parameters
    ----------
    modified_line_parts : A split G code string.
    parameter_array : user parameters in the form of a list of numpy arrays
    phase_num : The number of the current phase
    phase_pct : the current height vs total part height in percent

    Returns
    -------
    new_line : A new string which represents the modified G code line

    """

    # Check if we are not in phase 0
    if phase_num > 0:

        # Calculate new temp
        temp_start = parameter_array[1][phase_num - 1, 1]
        temp_end = parameter_array[1][phase_num, 1]
        new_temp = (temp_end - temp_start) * phase_pct + temp_start

        # Apply new temp to line
        if modified_line_parts[0].startswith("M104"):
            re.sub(r'[S]\d+', f's{new_temp}', modified_line_parts[1])
        else:  # M109
            re.sub(r'[R]\d+', f'R{new_temp}', modified_line_parts[1])


def add_temperature_setup(output_file, parameter_array, phase_num, phase_pct):
    # Check if we are not in phase 0
    if phase_num > 0:

        # Calculate new temp
        temp_start = parameter_array[1][phase_num - 1, 1]
        temp_end = parameter_array[1][phase_num, 1]
        new_temp = (temp_end - temp_start) * phase_pct + temp_start
        output_file.write("M104 S{:.3f}\n".format(new_temp))
        output_file.write("M109 R{:.3f}\n".format(new_temp))


def modify_extrusion_amounts(modified_line_parts, extrude_ratio_array, phase_num):
    """Modify the extrusion amounts inside a G code line according to user parameters, according speed and temperature

    Parameters
    ----------
    modified_line_parts : A split G code string.
    extrude_ratio_array : An array of correction ratio for each phase to use to edit G-code.
    phase_num : The number of the current phase.

    Returns
    -------

    """

    # Modify the extrusion amounts for each line to be modified (for gcode line with "G1 E")
    for i in range(1, len(modified_line_parts)):
        if modified_line_parts[i].startswith("E"):
            extrusion_value = float(modified_line_parts[i][1:])
            modified_line_parts[i] = "E" + "{:.3f}".format(extrusion_value * (100 + extrude_ratio_array[phase_num])/100)


def shift_position(modified_line_parts, shift_x, shift_y):
    """Shift the part position in the X and Y axes according to user parameters.

    Parameters
    ----------
    modified_line_parts : A split G code string.
    shift_x : The shift of the workpiece on X axis.
    shift_y : The shift of the workpiece on Y axis.

    Returns
    -------

    """

    # Apply the shift by adding the shift value on X and Y line coordinates
    for i in range(len(modified_line_parts)):
        if modified_line_parts[i].startswith("X"):
            x_value = float(modified_line_parts[i][1:])
            modified_line_parts[i] = "X" + "{:.3f}".format(x_value + shift_x)
        elif modified_line_parts[i].startswith("Y"):
            y_value = float(modified_line_parts[i][1:])
            modified_line_parts[i] = "Y" + "{:.3f}".format(y_value + shift_y)


def get_coordinate(line):
    """Get coordinate X, Y from a G-code line.

    Parameters
    ----------
    line : A line of G-code.

    Returns
    -------
    [x_coord, y_coord] : A list of coordinates or None

    """

    # Try to extract X and Y values from the line
    x_coord = re.findall(r'[X]\d+', line)
    y_coord = re.findall(r'[Y]\d+', line)

    # If coordinates found convert into floats
    if x_coord and y_coord:
        x_coord = float(x_coord[0][1:])
        y_coord = float(y_coord[0][1:])
        return [x_coord, y_coord]
    else:
        return None


def set_heating_path(coord_array):
    """Compute coordinates of points/ends of the parallel lines for the heating phase.

    Parameters
    ----------
    coord_array : A numpy array which contains X, Y coordinates of all instructions related to the external perimeter.

    Returns
    -------
    upper_coord : An array which contains upper coordinates of parallel line.
    lower_coord : An array which contains lower coordinates of parallel line.
    """

    # Find extremum values for coordinates, these extremums are used to describe a perimeter that covers the layer.
    x_max, y_max = np.max(coord_array, axis=0)
    x_min, y_min = np.min(coord_array, axis=0)

    # We extend this perimeter by 5%
    x_offset = 5*(x_max - x_min)/100
    y_offset = 5*(y_max - y_min)/100

    x_max, x_min = x_max+x_offset, x_min-x_offset
    y_max, y_min = y_max+y_offset, y_min-y_offset

    # We create a "grid" of points that will be used to define the parallel lines that the nozzle must
    # follow for the heating phase.
    nb_parallel_line = round((y_max - y_min)/0.4)
    upper_coord = np.linspace((x_max, y_min), (x_max, y_max), nb_parallel_line)
    lower_coord = np.linspace((x_min, y_min), (x_min, y_max), nb_parallel_line)

    return upper_coord.round(decimals=3), lower_coord.round(decimals=3)


def edit_heating_gcode(output_file, upper_coord, lower_coord):
    """Write G code associate to heating phase. It generates code which moves the die along parallel lines without
    extrusion in order to heat up the last printed layer.

    Parameters
    ----------
    output_file : The file in which to write G-code instructions.
    upper_coord : An array which contains upper coordinates of parallel line.
    lower_coord : An array which contains lower coordinates of parallel line.

    Returns
    -------

    """

    # A comment to indicate the start of the heating phase
    output_file.write(";HEATING_PHASE\n")

    # Parallels lines are on X axis
    for i in range(len(upper_coord)):
        if i % 2 == 0:
            output_file.write(f"G0 X{upper_coord[i][0]} Y{upper_coord[i][1]}\n")  # Linear move of the die
            # Go from upper to lower
            output_file.write(f"G0 X{lower_coord[i][0]} Y{lower_coord[i][1]}\n")  # Linear move of the die
        else:
            output_file.write(f"G0 X{lower_coord[i][0]} Y{lower_coord[i][1]}\n")  # Linear move of the die
            # Go from lower to upper
            output_file.write(f"G0 X{upper_coord[i][0]} Y{upper_coord[i][1]}\n")  # Linear move of the die

    # A comment to indicate the end of the heating phase
    output_file.write(";END_HEATING_PHASE\n")


def tag_modified_line(line):
    """This function will add a suffix comment to a G-code line.

    Parameters
    ----------
    line : A line of G-code to modify.

    Returns
    -------

    """

    # Add suffix
    line.append(" ;Modified\n")


def gcode_editor(gcode_file_path, parameter_file_path):
    """This function will call all other functions from this file to modify the G-code according to the input parameter
    file. The function will save the modified G-code in a new file with prefix "modified_" followed by the original
    file name.

    Parameters
    gcode_file_path : The relative path of the G code file to edit.
    parameter_file_path : The relative path of the parameters file to use for the edition.

    Returns
    -------

    """

    # Extract data from the parameter text file to a list of numpy arrays
    parameter_array = extract_values_from_file(parameter_file_path)

    # Check there are no nonsensical values in parameters (Example a negative speed)
    if check_parameter(parameter_array):

        # Get parameter related to the heating phase
        activate_heating = parameter_array[-1]

        # Get parameter related to shift position
        shift_x = parameter_array[4][0]
        shift_y = parameter_array[4][1]

        # Get extrude ratio array
        extrude_ratio_array = evaluate_extrude_ratio(parameter_array)

        # Find the layer height info
        layer_info = find_layer_info(gcode_file_path)
        layer_height = layer_info[0]    # Unused
        total_height = layer_info[1]    # Unused
        total_layers = layer_info[2]

        # Initialize output file
        output_file_path = re.sub("input/", "output/modified-", gcode_file_path)

        # Read file
        with open(gcode_file_path, "r") as input_file, open(output_file_path, "w") as output_file:

            # Initialize counters and variables
            layer_counter = 0
            height_pct = 0
            external_coord = False
            data_coord = []

            # Process each line individually
            for line in input_file:

                modified_line = line  # Unchanged line are also rewrite

                # A comment. We used some of them for control.
                if line[0] == ";":

                    if line.startswith(";LAYER_CHANGE"):
                        # Heat current layer before start the next
                        if layer_counter > 0 and activate_heating:
                            upper, lower = set_heating_path(np.array(data_coord))
                            edit_heating_gcode(output_file, upper, lower)
                            data_coord = []  # Now we are sure a new layer starts, thus we reset data_coord

                        # Update layer counter
                        layer_counter += 1

                        # Update the percentage of current height to total height
                        height_pct = (layer_counter / total_layers) * 100

                    elif line.startswith(";BEFORE_LAYER_CHANGE"):
                        # Add a G-code instruction to set temperature. These instructions are not always existent for each
                        # layer
                        add_temperature_setup(output_file, parameter_array, phase_num, phase_pct)

                    # Detect external perimeter and enable to get coordinates for future heating phase
                    elif line.startswith(";TYPE:External perimeter") and activate_heating:
                        external_coord = True

                    # If we meet this comment, we are sure that external perimeter is finished.
                    # It's not a perfect method because it seems some movements associated to external perimeter
                    # are outside this section for unknown reasons
                    elif external_coord and line.startswith(";WIPE_START"):
                        external_coord = False

                # A normal G-code line. We have to edit some of them.
                else:
                    # Find the current phase and how far we are in the phase
                    phase_num, phase_pct = find_phase(height_pct, parameter_array)

                    # Validate if the gcode line operation is a G1
                    if line.startswith("G1"):

                        # ********************************* Apply line modifications here *********************************

                        # Convert line to a list
                        modified_line_parts = line.split()

                        # Tag line modified by our gcode editor
                        tag_modified_line(modified_line_parts)

                        # Apply speed modifications
                        modify_speed(modified_line_parts, parameter_array, phase_num, phase_pct)

                        # Apply extrusion amounts modification
                        modify_extrusion_amounts(modified_line_parts, extrude_ratio_array, phase_num)

                        # Apply shift position modification
                        shift_position(modified_line_parts, shift_x, shift_y)

                        # Reformat line to text
                        modified_line = " ".join(modified_line_parts)

                        # ********************************* Get data for heating *********************************

                        if external_coord and (coord := get_coordinate(modified_line)):  # Opérateur de Walrus
                            data_coord.append(coord)

                    # If there is already a line to set temperature we modify its value
                    if line.startswith(("M104", "M109")):

                        # ********************************* Apply line modifications here *********************************

                        # Convert line to a list
                        modified_line_parts = line.split()

                        # Tag line modified by our gcode editor
                        tag_modified_line(modified_line_parts)

                        # Apply temperature modifications
                        modify_temperature(modified_line_parts, parameter_array, phase_num, phase_pct)

                        # Reformat line to text
                        modified_line = " ".join(modified_line_parts)

                # Write the modified lines to the output file
                output_file.write(modified_line)

        print(f"Edition finished. Find the new G code file {output_file_path}.")

    else:
        print(f"Edition canceled. Please check your parameters file.")