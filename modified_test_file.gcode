;
; MBL
;
M84 E ; turn off E motor
G29 ; mesh bed leveling
M104 S215 ; set extruder temp
G0 X120 Y95.5 Z30 F4800

M109 S215 ; wait for extruder temp
G1 Modified Z0.2 F720G92 E0

M569 S0 E ; set spreadcycle mode for extruder

;
; Extrude purge line
;

G1 Modified E2 F2400 ; deretraction

; move right
G1 Modified X152 E4.8 F1000; move down
G1 Modified Y94 E0.225 F1000; move left
M73 P1 R7
G1 Modified X120 E9.6 F800
G92 E0
M221 S100 ; set flow to 100%
G21 ; set units to millimeters
G90 ; use absolute coordinates
M83 ; use relative distances for extrusion
M900 K0.06 ; Filament gcode

M142 S36 ; set heatbreak target temp
M107
;LAYER_CHANGE
;Z:0.2
;HEIGHT:0.2
;BEFORE_LAYER_CHANGE
G92 E0.0
;0.2


G1 Modified E-.8 F2100G1 Modified Z.2 F720;AFTER_LAYER_CHANGE
;0.2
; printing object xyz-10mm-calibration-cube.stl id:0 copy 0
G1 Modified Z.4M73 P2 R7
G1 Modified X129.093 Y109.093 F12000G1 Modified Z.2 F720G1 Modified E.8 F1500M204 P600
;TYPE:Perimeter
;WIDTH:0.499999
G1 Modified F1200G1 Modified X120.907 Y109.093 E.31111G1 Modified X120.907 Y100.907 E.31111