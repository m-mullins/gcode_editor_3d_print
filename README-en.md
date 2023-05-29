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

1. Go to the GitHub ["Releases"] page (https://github.com/m-mullins/gcode_editor_3d_print/releases).

2. Unzip the zip archive into the folder of your choice.

You should then have the following gcode_editor folder :

````graphql
└──gcode_editor/
  ├─ input/ - # Folder for storing G-code files to be edited
  │  └─ xyz-10mm...
  ├─ output/ - # Folder for storing new G-code files after been edited
  ├─ parameter/ - # Folder for storing parameter files
  │  └─ parametre...
  ├─ README.md - # French README file
  ├─ readme/
  │  └─ README-dev.md - # README file for developers
  │  └─ README-dev-en.md - # English README file for developers
  │  └─ README-en.md - # English README file
  ├─ requirements.txt
  └─ xyz-10mm-calibration-cube.stl - # 3D object used as an example
````

3. Open a command terminal and go to the folder where you unzipped the archive.

Example :
````commandline
cd Desktop/*/*/gcode_editor
````

4. Run Python, then install the modules required for the program.

````commandline
python
pip install -r requirements.txt
````

5. Test that the program works correctly using the example files.

````python
import gcode_editor as gce
gce.gcode_editor("example_imput", "example_parameter")
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
the last layer to belong to that phase. Using the example below, if there are 100 layers, then phase 3 groups together 
layers 21 to 50. The last phase must be associated with 100%.

Example :
````text
Phase 000 (%) : 0
Phase 001 (%) : 20
Phase 002 (%) : 50
Phase 003 (%) : 100
````

#### Temperature

This section describes the evolution of the nozzle temperature during each phase. The temperature trend is linear
in each phase. We start with the temperature input for the previous phase and stop at the temperature input for 
the current phase. Temperatures should be in degrees Celsius. This G-code editor does not impose any restrictions on 
temperatures. We leave it to the user to choose a setting that is consistent with limitations of their printing 
equipment.

Example :
````text
Phase 000 (°C) : 180 
Phase 001 (°C) : 190 
Phase 002 (°C) : 210 
Phase 003 (°C) : 230
````

#### Printing speed

This sections describes the evolution of the nozzle speed during each of the phases. Similarly to temperature, the 
speed trend is linear for each phase. The change in speed should be described as a percentage.

Example :
````text
Phase 000 (%) : 90 
Phase 001 (%) : 100 
Phase 002 (%) : 110
Phase 003 (%) : 130
````


#### Extrusion

This section describes whether over-extrusion or under-extrusion is required during each phase. In other words, the 
quantity of raw material leaving the nozzle is modified. The intensity of this variation should be indicated as a 
percentage. This adjustment can be used to alleviate the problem of swelling at the nozzle. This phenomenon is 
affected by the temperature and the printing speed, so it's important to take these two other factors into account 
when setting the extrusion parameters.

Example :
````text
En attente
````

#### Shift position

This section describes the offset of the workpiece on the print bed along the X and Y axes of the nozzle, i.e. in the 
horizontal plane. These offsets should correspond to variations in millimetres. This variation is not associated with 
a phase, but with the whole workpiece.  All G-code instructions will be adjusted to allow the workpiece to be shifted.

Example :
````text
En attente
````

#### Warming up

In this section you specify if you wish to enable or disable the addition of a warm-up phase after printing each layer.
This mechanism is designed to promote better bonding between the layers. A value of 0 indicates this mechanism is 
deactivated, any other integer value will activate it.

Example :
````text
Heating : 1
````
