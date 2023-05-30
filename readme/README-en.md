# gcode_editor_3d_print

[![fr](https://img.shields.io/badge/lang-fr-blue.svg)](https://github.com/m-mullins/gcode_editor_3d_print/blob/main/README.md)

This README file is intended for users of the Gcode editor project. For developers interested in taking over this 
project, please refer to the [README-dev-en](README-dev-en.md) file.

## Introduction

<p align="justify">
G-code is a numerical control programming language specific to CNC (Computer Numerical Control) machines. This 
programming can now be highly automated with the help of software such as PrusaSlicer, which can generate G-code 
instructions directly from 3D models (STL, OBJ, AMF).

The aim of this program is to edit the G-code instructions generated from such software in order to take into account 
the adjustments desired by the user. The parameters of the G-code instructions will thus be modified according to the 
parameters entered by the user, which we will describe later. Another purpose of this program is to improve the weld 
between the different layers of 3D printing by adding a heating phase for the bottom layer before printing a new layer.
</p>

## Usage

This section explains how to get this G-code editor and install the necessary Python modules. 
You can go straight to the [Usage](#usage) section if you wish.

Prerequisites: Install [Python](https://www.python.org/downloads/) (Versions tested 3.9.5, 3.11.3).

1. Go to the GitHub ["Releases"] page (https://github.com/m-mullins/gcode_editor_3d_print/releases) and download the
*Source code (zip)* archive from the *Assets* tab.

2. Unzip the zip archive into the folder of your choice.

You should then have the following gcode_editor folder :

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
  ├─ check.py
  ├─ gcode_editor.py # Main Python file
  ├─ README.md - # French README file
  ├─ requirements.txt
  └─ xyz-10mm-calibration-cube.stl - # 3D object used as an example
````

3. Open a command terminal and go to the folder where you unzipped the archive.

Example :
````commandline
cd Desktop/*/*/gcode_editor
````

4. Install the modules required for the program, then run Python.

````commandline
pip install -r requirements.txt
python
````

5. Test that the program works correctly using the example files.

````python
import gcode_editor as gce
gce.gcode_editor("input/xyz-10mm-calibration-cube_0.4n_0.2mm_PLA_MK4_8m.gcode", "parameter/example_parameter.txt")
````

## Usage

### Generation of G-code files

Using tools such as [PrusaSlicer](https://www.prusa3d.com/page/prusaslicer_424/), generate the *.gcode* file for your 3D
object. Then place this file in the *input/* folder. A file is provided to be used as an example.

### Création du fichier de paramétrage

To use this G-code editor, you first need to create a settings file. An example can be found in the *parameter/* 
folder. This file is divided into 6 sections.

#### Phase identification

Successive layers of the 3D object are gathered in phase. These phases are then associated with parameters of
temperature, speed and extrusion. Each phase is linked to a percentage (of the total number of layers) which indicates 
the last layer to belong to that phase. Using the example below, the layers are grouped into 3 phases. If there are 100 
layers, then the third phase groups layers 70 to 100.

Example :
````text
Phase 0 (%) : 0
Phase 1 (%) : 40
Phase 2 (%) : 70
Phase 3 (%) : 100
````

Warning: The first and last phases must be set to 0% and 100% respectively.

#### Temperature

This section describes the evolution of the nozzle temperature during each phase. The temperature trend is linear
in each phase. We start with the temperature input for the previous phase and stop at the temperature input for 
the current phase. Temperatures should be in degrees Celsius.

Example :
````text
Phase 0 (deg C) : 190
Phase 1 (deg C) : 200
Phase 2 (deg C) : 210
Phase 3 (deg C) : 220
````

Warning : This G-code editor imposes few restrictions on temperatures. We leave it to the user to choose a setting that 
is consistent with limitations of their printing equipment.

#### Printing speed

This sections describes the evolution of the nozzle speed during each of the phases. Similarly to temperature, the 
speed trend is linear for each phase. The change in speed should be described as a percentage.

Example :
````text
Phase 0 (%) : 50
Phase 1 (%) : 30
Phase 2 (%) : 40
Phase 3 (%) : 60
````

Warning: Like the temperature, this G-code editor imposes few restrictions. We simply check that the percentages are 
positive. We leave it to the user to choose a setting that is consistent with the limitations of their printing 
equipment.

#### Extrusion

This section specifies the absolute limit of the correction factors applied to the extrusion of the part (under or 
over extrusion). In other words, the quantity of raw material leaving the nozzle will be modified. This parameter 
indicates that the correction factors applied to each phase will be in the range 
[100-Correction (%); 100+Correction (%)]. These factors are calculated by the program and should be used to alleviate 
the problem of swelling at the nozzle. This phenomenon is affected by the temperature and the printing speed. This 
parameter must be indicated as a percentage.

Example :
````text
Correction (%) : 5
````

Warning: Deleting this line or adding uncommented lines in this section will be treated as an error.

#### Shift position

This section describes the offset of the workpiece on the print bed along the X and Y axes of the nozzle, i.e. in the 
horizontal plane. These offsets should correspond to variations in millimetres. This variation is not associated with 
a phase, but with the whole workpiece.  All G-code instructions will be adjusted to allow the workpiece to be shifted.

Example :
````text
Shift_X (mm) : 2
Shift_Y (mm) : 3
````

Warning: Deleting these lines or adding uncommented lines in this section will be treated as an error.

#### Warming up

In this section you specify if you wish to enable or disable the addition of a warm-up phase after printing each layer.
This mechanism is designed to promote better bonding between the layers. A value of 0 indicates this mechanism is 
deactivated, any other integer value will activate it.

Example :
````text
Heating : 1
````

Warning: Deleting this line or adding uncommented lines in this section will be treated as an error.

The Python file *check.py* contains functions for checking your parameters. These are called at the start of the
*gcode_editor* program. However, you can also check your parameters without running the main program, as follows:

````python
import gcode_editor as gce
import check
check.check_parameter(gce.extract_values_from_file("parameter/example_parameter_bis.txt"))
````