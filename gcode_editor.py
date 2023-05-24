from timeit import timeit
import numpy as np
import re

def extract_values_from_file(file_name):
    # This function extracts the parameters that were entered by the user in the text file parametre_impression_3d.txt
    # --- Input ---
    # file_name         : the parameters file name to parse
    # --- Output ---
    # extracted_data    : extracted parameters in a list of np arrays for each type of parameter
    # number_phases     : number of phases inputed

    # Extract the content from the file
    with open(file_name, 'r') as file:
        content = file.read()

    # Split the content for each type of parameter
    sections = content.split('------------------------------------------------------------------')

    # Remove leading/trailing whitespaces and empty sections
    sections = [section.strip() for section in sections if section.strip()]

    # Initialize extracted parameters
    extracted_data = []

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
    # Given a gcode file sliced with prusa slicer, this function will parse the gcode and return the layer information 
    # --- Input ---
    # gcode_file    : the gcode file name to parse
    # --- Output ---
    # layer_height  : height of each layer
    # total_height  : total height of the part
    # layer_count   : total amount of layers

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
    # Given the user parameters and current height percentage vs total height, 
    # this function will determine in what phase we are and of far in the phase we are (in percent) 
    # --- Input ---
    # height_pct        : the current height vs total part height in percent
    # parameter_array   : user parameters in the form of a list of np arrays
    # --- Output ---
    # phase_counter     : current phase at our layer height
    # phase_pct         : how far we are in the current phase in percent
    
    # Calculate number of phases
    num_phases = len(parameter_array)

    # Initialize phase counter
    phase_counter = 1

    # Debug
    if height_pct == 98:
        print(height_pct)

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
        if height_pct >= phase_start and height_pct <= phase_end:
            # x = height_pct-phase_start
            # xp = phase_data[:, 1]
            # fp = phase_data[:, 0]
            # phase_pct = np.interp(x,xp,fp) * 100.0
            phase_pct = (height_pct-phase_start) / (phase_end-phase_start)
            return phase_counter, phase_pct

    # Return nothing if conditions not met
    return None, None


def modify_speed(modified_line_parts,parameter_array,phase_num,phase_pct):

    # Check if we are not in phase 0
    if phase_num > 0:

        # Iterate through each argument in the line
        for i in range(len(modified_line_parts)):

            # Check if its a speed argument *********** Make it extract only nums instead of str ***************
            if modified_line_parts[i].startswith("F"):

                # Extract current speed
                current_speed = re.findall(r'\d+', modified_line_parts[i])
                current_speed = int(current_speed[0])
                # current_speed = int(modified_line_parts[i][1:])

                # Calculate speed multiplier
                mult_start = parameter_array[2][phase_num-1,1]
                mult_end = parameter_array[2][phase_num,1]
                speed_mult = (mult_end-mult_start)*phase_pct + mult_start

                # Apply speed multiplier
                new_speed = current_speed * speed_mult/100

                # Apply new speed to line
                modified_line_parts[i] = "F" + str(new_speed)

    modified_line_parts = modified_line_parts

    return modified_line_parts

def modify_line(line):
    # This function will add a suffix comment to a gcode line
    # --- Input ---
    # line      : the line to modify
    # --- Output ---
    # line      : the modified line

    # Add suffix
    line.append(" ;Modified")

    return line

def gcode_editor():
    # This script will call all other function from this file to modify the gcode according to the input parameter file
    # The function will save the modified gcode to a new file with prefix "modified_" followed by the original file name

    # Initialize constants
    GCODE_FILE_NAME = "xyz-10mm-calibration-cube_0.4n_0.2mm_PLA_MK4_8m.gcode"
    PARAMETER_FILE = 'parametre_impression_3d.txt'

    # Extract data from the parameter text file to a list of np arrays
    parameters = extract_values_from_file(PARAMETER_FILE)
    parameter_array = parameters[0]
    number_phases = parameters[1]

    # Find the layer height info
    layer_info = find_layer_info(GCODE_FILE_NAME)
    layer_height = layer_info[0]
    total_height = layer_info[1]
    total_layers = layer_info[2]

    # Initialize output file
    output_file_path = "modified_" + GCODE_FILE_NAME

    # Initialize counters and variables
    layer_counter = 0
    line_counter = 0
    height_pct = 0

    # Read file
    with open(GCODE_FILE_NAME, "r") as input_file:
        lines = input_file.readlines()

    # Process each line individually
    modified_lines = []
    for line in lines:

        # Update line counter
        line_counter += 1
        
        # Validate if the gcode line operation is a G1
        if line.startswith("G1"):
            
            # Convert line to a list
            line_parts = line.split()

            # Find the current phase and how far we are in the phase
            phase_num, phase_pct = find_phase(height_pct, parameter_array)

            # ************************************ Apply line modifications here ************************************
            # modified_line_parts = modify_line(line_parts)    

            # Apply speed modifications
            modified_line_parts = modify_speed(modified_line_parts,parameter_array,phase_num,phase_pct)

            # Reformat line to text
            modified_line = " ".join(modified_line_parts)

            # Append modified line to the modified lines list
            modified_lines.append(modified_line)

        # Update layer counter
        elif line.startswith(";LAYER_CHANGE"):
            layer_counter += 1

            # Update the percentage of current height to total height
            height_pct = (layer_counter / total_layers) * 100

        # If the line is not one to modify, append it without modification
        else:
            modified_lines.append(line)

    # Write the modified lines to the output file
    with open(output_file_path, "w") as output_file:
        output_file.writelines(modified_lines)



gcode_editor()

# # Time the execution
# number_of_executions = 500
# GCODE_FILENAME = "xyz-10mm-calibration-cube_0.4n_0.2mm_PLA_MK4_8m.gcode"
# execution_time = timeit("find_layer_info(GCODE_FILENAME)",globals=globals(),number=number_of_executions) / number_of_executions
# # execution_time = timeit("gcode_editor()",globals=globals(),number=number_of_executions) / number_of_executions
# print(execution_time)
