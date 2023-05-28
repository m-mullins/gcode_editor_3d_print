import numpy as np
import re


def extract_values_from_file(file_name):
    """This function extracts the parameters that were entered by the user in the text file parametre_impression_3d.txt

    Parameters
    ----------
    file_name : the parameters file name to parse

    Returns
    -------
    extracted_data : extracted parameters in a list of np arrays for each type of parameter
    number_phases : number of phases inputed
    """

    # Extract the content from the file
    with open(file_name, 'r') as file:
        content = file.read()

    # Split the content for each type of parameter
    sections = content.split('------------------------------------------------------------------')

    # Remove leading/trailing whitespaces and empty sections
    sections = [section.strip() for section in sections if section.strip()]

    # Initialize extracted parameters
    extracted_data = []

    phase_number = 0

    # Iterate through each section of parameter
    for section in sections:
        # Split each section in multiple lines and remove leading/trailing whitespaces
        phase_lines = section.split('\n')
        phase_lines = [line.strip() for line in phase_lines if line.strip()]

        # Initialise list
        phase_values = []

        # Extract the data for each line that starts with "Phase"
        for line in phase_lines:
            if line.startswith('Phase'):

                # Split the line in multiple parts
                phase_parts = line.split(':')

                # Remove leading/trailing whitespaces on both parts
                phase_key = phase_parts[0].strip()
                phase_value = phase_parts[1].strip()

                # Extract the number of phases
                phase_number = int(phase_key.split('Phase ')[1].split(' (')[0])

                # Append phase number and value to array
                phase_values.append((phase_number, float(phase_value)))

        # Append array to list of arrays
        extracted_data.append(np.array(phase_values))

    # Remove the first empty section
    extracted_data.pop(0)

    return extracted_data, phase_number


def find_layer_info(gcode_file):
    """Given a gcode file sliced with prusa slicer, this function will parse the gcode and return the layer information

    Parameters
    ----------
    gcode_file : the gcode file name to parse

    Returns
    -------
    layer_height  : height of each layer
    total_height  : total height of the part
    layer_count   : total amount of layers
    """

    # Initialize variables
    layer_height = None
    total_height = None
    layer_count = 0

    # Open gcode and read each line individually
    with open(gcode_file, "r") as file:
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
    """Given the user parameters and current height percentage vs total height, this function will determine in what
     phase we are and of far in the phase we are (in percent).

    Parameters
    ----------
    height_pct : the current height vs total part height in percent
    parameter_array : user parameters in the form of a list of np arrays

    Returns
    -------
    phase_counter : current phase at our layer height
    phase_pct : how far we are in the current phase in percent
    """

    # Calculate number of phases
    num_phases = len(parameter_array)

    # Initialize phase counter
    phase_counter = 1

    # Iterate through the phases
    for i in range(num_phases):
        phase_counter = i + 1
        phase_data = parameter_array[0]

        # # Check if it's the last phase
        # if phase_counter == num_phases:
        #     phase_pct = 100.0
        #     return phase_counter, phase_pct

        # Get the start and end percentages for the current phase
        phase_start = phase_data[phase_counter-1, 1]
        phase_end = phase_data[phase_counter, 1]

        # Check if the height_pct is within the current phase
        if phase_start <= height_pct <= phase_end:
            # x = height_pct-phase_start
            # xp = phase_data[:, 1]
            # fp = phase_data[:, 0]
            # phase_pct = np.interp(x,xp,fp) * 100.0
            phase_pct = (height_pct-phase_start) / (phase_end-phase_start)
            return phase_counter, phase_pct

    # Return nothing if conditions not met
    return None, None


def modify_speed(modified_line_parts, parameter_array, phase_num, phase_pct):
    """Modify speed inside a G code line according to user parameters.

    Parameters
    ----------
    modified_line_parts : A split G code string
    parameter_array : user parameters in the form of a list of np arrays
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


def modify_temperature(line, parameter_array, phase_num, phase_pct):
    """Modify temperature inside a G code line according to user parameters

    Parameters
    ----------
    line : A string which represents a G code line
    parameter_array : user parameters in the form of a list of np arrays
    phase_num : The number of the current phase
    phase_pct : the current height vs total part height in percent

    Returns
    -------
    new_line : A new string which represents the modified G code line

    """

    new_line = line

    # Check if we are not in phase 0
    if phase_num > 0:

        # Calculate new temp
        temp_start = parameter_array[1][phase_num - 1, 1]
        temp_end = parameter_array[1][phase_num, 1]
        new_temp = (temp_end - temp_start) * phase_pct + temp_start

        # Apply new temp to line
        if line.startswith("M104"):
            new_line = re.sub(r'[S]\d+', f's{new_temp}', line)
        else:  # M109
            new_line = re.sub(r'[R]\d+', f'R{new_temp}', line)

    return new_line

def modify_extrusion_amounts(modified_line_parts, parameter_array, phase_num, phase_pct):
    """Modify the extrusion amounts inside a G code line according to user parameters, according speed and temperature

    Parameters
    ----------
    modified_line_parts : A string which represents a G code line already modified according speed and temperature
    parameter_array : user parameters in the form of a list of np arrays, contains the percent of over/under extrusion
    phase_num : The number of the current phase
    phase_pct : the current height vs total part height in percent

    Returns
    -------
    new_line : A new string which represents the modified G code line, with the extrusion amounts adjusted in percent
               in the current phase

    """

    # Calculate the over/under extrusion percentage using phase parameters
    sur_extrusion_pct = parameter_array[3][phase_num]

    # Calculate the modified percentage of extrusion amounts
    extrusion_mod_pct = 100 + (phase_pct - 100) * (sur_extrusion_pct - 100) / 100

    # Modify the extrusion amounts for each line to be modified (for gcode line with "G1 E")
    for i in range(1, len(modified_line_parts)):
        if modified_line_parts[i].startswith("G1 E"):
            extrusion_value = float(modified_line_parts[i][1:])
            modified_line_parts[i] = "G1 E" + str(extrusion_value * extrusion_mod_pct / 100)

    # Reformat line to text
    new_line = " ".join(modified_line_parts)

    # Return modified line
    return new_line

def shift_position(modified_line_parts, parameter_array, phase_num, phase_pct):
    """Shift the part position in the X and Y axes according to user parameters

    Parameters
    ----------
    modified_line_parts : A string which represents a G code line already modified
    parameter_array : user parameters in the form of a list of np arrays, contains the X and Y values to shift position
    phase_num : The number of the current phase
    phase_pct : the current height vs total part height in percent

    Returns
    -------
    new_line : A new string which represents the modified G code line, with the new X and Y position value

    """

    # Extract the X and Y shift value for the current phase
    shift_values = parameter_array[4][phase_num].split(" et ")
    shift_x = float(shift_values[0].split("=")[1])
    shift_y = float(shift_values[1].split("=")[1])

    # Apply the shift by adding the shift value on X and Y line coordinates
    for i in range(len(modified_line_parts)):
        if modified_line_parts[i].startswith("G1 X"):
            x_value = float(modified_line_parts[i][1:])
            modified_line_parts[i] = "G1 X" + str(x_value + shift_x)
        elif modified_line_parts[i].startswith("G1 Y"):
            y_value = float(modified_line_parts[i][1:])
            modified_line_parts[i] = "G1 Y" + str(y_value + shift_y)

    # Reformat line to text
    new_line = " ".join(modified_line_parts)

    # Return modified line
    return new_line

def get_coordinate(line):
    """Get coordinate X, Y from G code line

    Parameters
    ----------
    line : a line of G code

    Returns
    -------
    [x_coord, y_coord] : list of coordinates or None

    """

    x_coord = re.findall(r'[X]\d+', line)
    y_coord = re.findall(r'[Y]\d+', line)

    if x_coord and y_coord:
        x_coord = int(x_coord[0][1:])
        y_coord = int(y_coord[0][1:])
        return [x_coord, y_coord]
    else:
        return None


def set_heating_path(coord_array):
    """Calculate the coordinates of points/ends of parallel lines for the heating phase.

    Parameters
    ----------
    coord_array : numpy array which contains X, Y coordinates of external perimeter

    Returns
    -------
    upper_coord : upper coordinates of parallel line
    lower_coord : lower coordinates of parallel line

    """
    x_max, y_max = np.max(coord_array, axis=0)
    x_min, y_min = np.min(coord_array, axis=0)

    # We extend perimeter by 5%
    x_offset = 5*(x_max - x_min)/100
    y_offset = 5*(y_max - y_min)/100

    x_max, x_min = x_max+x_offset, x_min-x_offset
    y_max, y_min = y_max+y_offset, y_min-y_offset

    # We define a "grid"
    nb_parallel_line = round((y_max - y_min)/0.4)

    upper_coord = np.linspace((x_max, y_min), (x_max, y_max), nb_parallel_line)
    lower_coord = np.linspace((x_min, y_min), (x_min, y_max), nb_parallel_line)

    return upper_coord.round(decimals=3), lower_coord.round(decimals=3)


def edit_heating_gcode(output_file, upper_coord, lower_coord):
    """Write G code associate to heating phase. It generates code which moves the die along parallel lines without
    extrusion in order to heat up the last printed layer.

    Parameters
    ----------
    output_file : file to write G code
    upper_coord : upper coordinates of parallel line
    lower_coord : lower coordinates of parallel line

    Returns
    -------

    """

    output_file.write(";PRE_HEATING_PHASE\n")

    for i in range(len(upper_coord)):
        if i % 2 == 0:
            # Go from upper to lower
            output_file.write(f"G92 X{upper_coord[i][0]} Y{upper_coord[i][1]} E0.0\n")  # Set starting position
            output_file.write(f"G1 X{lower_coord[i][0]} Y{lower_coord[i][1]}\n")  # Linear move of the die
        else:
            # Go from lower to upper
            output_file.write(f"G92 X{lower_coord[i][0]} Y{lower_coord[i][1]} E0.0\n")  # Set starting position
            output_file.write(f"G1 X{upper_coord[i][0]} Y{upper_coord[i][1]}\n")  # Linear move of the die

    output_file.write(";END_PRE_HEATING_PHASE\n")


def tag_modified_line(line):
    """This function will add a suffix comment to a gcode line

    Parameters
    ----------
    line : the line to modify

    Returns
    -------

    """

    # Add suffix
    line.append(" ;Modified\n")


def gcode_editor(gcode_file_path, parameter_file_path):
    """This script will call all other function from this file to modify the gcode according to the input parameter file
    The function will save the modified gcode to a new file with prefix "modified_" followed by the original file name.

    Parameters
    gcode_file_path : The relative path of the G code file to edit.
    parameter_file_path : The relative path of the parameters file to use for the edition.

    Returns
    -------

    """

    # Extract data from the parameter text file to a list of np arrays
    parameters = extract_values_from_file(parameter_file_path)
    parameter_array = parameters[0]
    number_phases = parameters[1]   # Unused

    # Find the layer height info
    layer_info = find_layer_info(gcode_file_path)
    layer_height = layer_info[0]    # Unused
    total_height = layer_info[1]    # Unused
    total_layers = layer_info[2]

    # Initialize output file
    output_file_path = re.sub("input/", "output/modified-", gcode_file_path)

    # Initialize counters and variables
    layer_counter = 0
    line_counter = 0  # Unused
    height_pct = 0
    external_coord = False
    data_coord = []

    # Read file
    with open(gcode_file_path, "r") as input_file, open(output_file_path, "w") as output_file:

        # Process each line individually
        for line in input_file:

            # Update line counter
            line_counter += 1  # Unused

            modified_line = line  # Unchanged line are also rewrite

            # A comment line. We used some of them for control.
            if line[0] == ";":

                if line.startswith(";LAYER_CHANGE"):
                    # Heat current layer before start the next
                    if layer_counter > 0:
                        upper, lower = set_heating_path(np.array(data_coord))
                        edit_heating_gcode(output_file, upper, lower)

                    # Update layer counter
                    layer_counter += 1

                    # Update the percentage of current height to total height
                    height_pct = (layer_counter / total_layers) * 100

                # Get external perimeter coordinates for future heating phase
                elif line.startswith(";TYPE:External perimeter"):
                    external_coord = True
                    data_coord = []  # Comment

                # Detect end of external perimeter
                elif line.startswith(";WIPE_START"):
                    external_coord = False

            # A normal G code line. We have to edit some of them.
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

                    # Reformat line to text
                    modified_line = " ".join(modified_line_parts)

                    # ********************************* Get data for heating *********************************

                    if external_coord and (coord := get_coordinate(line)):  # Opérateur de Walrus
                        data_coord.append(coord)

                # M104 or M109
                if line.startswith(("M104", "M109")):

                    # ********************************* Apply line modifications here *********************************

                    # Apply temperature modifications
                    modified_line = modify_temperature(line, parameter_array, phase_num, phase_pct)

                    # Tag line modified by our gcode editor
                    tag_modified_line(modified_line)

                # G1 E (modify temperature, speed, extrusion amount and position if line contains gcode "G1 E")
                if line.startswith("G1 E"):

                    # ********************************* Apply line modifications here *********************************

                    # Convert line to a list
                    modified_line_parts = line.split()

                    # Tag line modified by our gcode editor
                    tag_modified_line(modified_line_parts)

                    # Apply extrusion amounts modification
                    modified_line = modify_extrusion_amounts(modified_line_parts, parameter_array, phase_num,
                                                             phase_pct)

                # G1 X/Y (modify X and Y axes position according shifting value)
                if line.startswith(("G1 X", "G1 Y")):

                    # ********************************* Apply line modifications here *********************************

                    # Convert line to a list
                    modified_line_parts = line.split()

                    # Tag line modified by our gcode editor
                    tag_modified_line(modified_line_parts)

                    # Apply the position modification
                    modified_line = shift_position(modified_line_parts, parameter_array, phase_num, phase_pct)

            # Write the modified lines to the output file
            output_file.write(modified_line)

    print(f"Edition Finished. Find the new G code file {output_file_path}.")
