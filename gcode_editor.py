from timeit import timeit

def extract_values_from_file(file_name):
    # This function extracts the parameters that were entered by the user in the text file parametre_impression_3d.txt
    # The function returns the parameters in a list of dictionaries

    # Extract the content from the file
    with open(file_name, 'r') as file:
        content = file.read()

    # Split the content for each type of parameter
    sections = content.split('------------------------------------------------------------------')

    # Remove leading/trailing whitespaces and empty sections
    sections = [section.strip() for section in sections if section.strip()]

    # Initialize extracted parameters
    extracted_data = []


    for section in sections:
        # Split each section in multiple lines and remove leading/trailing whitespaces
        phase_lines = section.split('\n')
        phase_lines = [line.strip() for line in phase_lines if line.strip()]

        # Initialise dictionary
        phase_values = {} 

        # Extract the data for each line that starts with phase
        for line in phase_lines:
            if line.startswith('Phase'):
                # Split the line in multiple parts
                phase_parts = line.split(':')
                # Remove leading/trailing whitespaces on both parts
                phase_key = phase_parts[0].strip()
                phase_value = phase_parts[1].strip()
                # Insert values in a dictionary
                phase_values[phase_key] = float(phase_value)
                # # Extract the number of phases
                # number_phases = int(phase_key.split('Phase ')[1].split(' (')[0])

        # Append dictionary to list of dictionaries
        extracted_data.append(phase_values)

    # Remove the first empty section
    extracted_data.pop(0)

    return extracted_data

def modify_line(line):
    # Test line modification function
    line[1] = "Modified " + line[1]
    return line

def gcode_editor():

    # Extract data from the parameter text file to a list of dictionaries
    parameter_file = 'parametre_impression_3d.txt'
    parameter_dico = extract_values_from_file(parameter_file)

    # # Print the extracted data
    # for section_data in parameter_dico:
    #     print(section_data)
    #     print('-' * 50)

    # Open the input file
    # input_file_path = "test_file.gcode"
    input_file_path = "xyz-10mm-calibration-cube_0.4n_0.2mm_PLA_MK4_8m.gcode"
    output_file_path = "modified_" + input_file_path

    with open(input_file_path, "r") as input_file:
        lines = input_file.readlines()

    # Process the lines
    modified_lines = []
    for line in lines:
        
        # Validate if the gcode line operation is a G1
        if line.startswith("G1"):
            
            # Convert line to a list
            line_parts = line.split()

            # ************************************ Apply line modifications here ************************************
            modified_line_parts = modify_line(line_parts) 
            modified_line = " ".join(modified_line_parts)

            # Append modified line to the modified lines list
            modified_lines.append(modified_line)
        
        # If the line is not one to modify, append it without modification
        else:
            modified_lines.append(line)

    # Write the modified lines to the output file
    with open(output_file_path, "w") as output_file:
        output_file.writelines(modified_lines)



gcode_editor()

# # Time the execution
# number_of_executions = 500
# execution_time = timeit("gcode_editor()",globals=globals(),number=number_of_executions) / number_of_executions
# print(execution_time)