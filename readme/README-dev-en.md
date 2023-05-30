# gcode_editor_3d_print

[![fr](https://img.shields.io/badge/lang-fr-blue.svg)](https://github.com/m-mullins/gcode_editor_3d_print/blob/main/readme/README-dev.md)

This README is intended for developers who would like to take over this project. We describe here the information 
that, in our opinion, would be useful to work on this project. For explanations about how to use this G-code 
editor, please refer to the [README-en](README-en.md) file.

## Dependencies

This is being developed in python 3.9.5 and has not been tested with other iterations. Following is the list of the 
modules used and their versions.

### Packages :

`numpy 1.24.3`

## Project description

The `gcode_editor.py` code is a Python program for editing G-code files used in 3D printing. It takes as input a G-code 
file and a parameters file created by the user. Then, it makes various modifications to the G-code according to these 
parameters.

## Structure du projet

The project repository is organised as follows:

````graphql
└──gcode_editor/
  ├─ input/ - # Folder for storing G-code files to be edited
  │  └─ 10mm_test_cube_0.4n_0.2mm_PLA_MK4_7m.gcode
  │  └─ xyz-10mm-calibration-cube_0.4n_0.2mm_PLA_MK4_8m.gcode
  ├─ output/ - # Folder for storing new G-code files after been edited
  │  └─ modified-10mm_test_cube_0.4n_0.2mm_PLA_MK4_7m.gcode
  │  └─ modified-xyz-10mm-calibration-cube_0.4n_0.2mm_PLA_MK4_8m.gcode  
  ├─ parameter/ - # Folder for storing parameter files
  │  └─ example_parameter.txt
  │  └─ example_parameter_bis.txt
  ├─ readme/
  │  └─ README-dev.md - # README file for developers
  │  └─ README-dev-en.md - # English README file for developers
  │  └─ README-en.md - # English README file
  ├─ tests/
  │  └─ exec_time.py
  ├─ check.py
  ├─ gcode_editor.py # Main Python file
  ├─ README.md - # French README file
  ├─ requirements.txt
  └─ xyz-10mm-calibration-cube.stl - # 3D object used as an example
````

### Main files

- `gcode_editor.py` et `check.py`: The main files containing the source code.
- `example_parameter.txt` : An example of parameters file used to define changes to be made to G-code. To understand how
this file is structured and how it should be modified by the user, please refer to the [README](../README md) file.

## How `gcode_editor.py` works

Here is an explanation of how the `gcode_editor.py` program works. We will present the control flow of the main 
function `gcode_editor()`. Functions used to edit G-code are described in detail in the section: 
[G-code editing functions](#g-code-editing-functions)

1. Reading the parameter file :
   - `extract_values_from_file()` : The parameter file is read to get all the parameters entered by the user in Numpy
   lists.

2. Checking parameters :
   - `check_parameter()` : Check that the parameters entered by the user respect the constraints imposed.

3. Get information on layers :
   - `find_layer_info()` : We read the input G-code file once to obtain the layer information.

4. Iteration on G-code file lines :
   1. Comment line :
      1. Comment starting with ";LAYER_CHANGE" :
         - Increment the current layer counter.
      2. Comment starting with ";BEFORE_LAYER_CHANGE" :
         - `set_heating_path()` and `edit_heating_gcode()` : Add G-code instructions to warm up the previous layer.
         - `add_temperature_setup()` : Add G-code instructions to modify nozzle temperature.
      3. Comment starting with ";TYPE:External perimeter" : 
         - Detect the external perimeter printing and collect coordinates of linear movements.
      4. Comment starting with ";WIPE_START" :
         - Detect end of external perimeter printing and stop collecting coordinates.
   2. G-code instruction :
      - `find_phase()` : Identify the current phase and our progress in that phase.
      - Apply modification functions to the G-code instruction. :
        1. G-code instruction starting with G1 :
           - `modify_speed()` : Modify nozzle speed.
           - `modify_extrusion_amounts()` : Modify extrusion intensity.
           - `shift_position()` : Offset the position of the workpiece along the X and Y axes on the print bed.
        2.  G-code instruction starting with M104 or M109 :
           - `modify_temperature()` : Modify nozzle temperature.

5. Write the line in a new file.

## G-code editing functions

The adjustments requested by the user in the parameter file are intended to modify the G-code instructions in order to 
carry out the tasks described above. We will explain the approach we have adopted for modifying a line, which we believe
should be retained if you wish to add new editing functions.

Functions minimal signature : modify_gcode_line(modified_line_parts, parameter_array)

- Arguments :
  - modified_line_parts (list) :  A split G code string.
  - parameter_array (numpy array) : User parameters in the form of a list of numpy arrays
  - phase_num (int) : The number of the current phase (Optional).
  - phase_pct (float) : The current height vs total part height in percent (Optional)
- Return : None

We use these functions as follows

1. Split the G-code instruction : `line.split('')`
2. Tag the instruction as modified.
3. Successive application of functions `modify_...()`. Given that we are modifying a list, it is not necessary to 
retrieve a new string after each function. 
4. Create a new G-code instruction with : `" ".join(modified_line_parts)`
     
## Additional notes

- The `check.py` file is used to perform some basic checks on the parameter file entered by the user. For example, that 
speeds and temperatures are not negative. However, our code leaves it up to the user to check that their parameters are 
consistent with the capabilities of their printer, because we don't have this information. However, we currently 
display 'Warning' messages for values that exceed the typical usage ranges we have found on the Internet. In this way, 
we can highlight an abnormally high value which could be a typing error, but which is nonetheless valid. For example, a 
temperature of 1000°C.
- The code is structured and modular, making it easy to add new features or modify existing ones in `gcode_editor.py`.
- If you have any questions or suggestions for improvement, please do not hesitate to contact the development team.


