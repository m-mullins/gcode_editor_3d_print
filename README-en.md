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
