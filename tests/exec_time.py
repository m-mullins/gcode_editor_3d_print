import timeit

# Time the execution
number_of_executions = 500

GCODE_FILENAME = "xyz-10mm-calibration-cube_0.4n_0.2mm_PLA_MK4_8m.gcode"
GCODE_INPUT_FOLDER = "input/"
GCODE_PATH = "../" + GCODE_INPUT_FOLDER + GCODE_FILENAME

PARAMETER_FILENAME = 'parametre_impression_3d.txt'
PARAMETER_FOLDER = "parameter/"
PARAMETER_PATH = "../" + PARAMETER_FOLDER + PARAMETER_FILENAME

exec_time_find_layer = timeit.timeit(setup="from gcode_editor import find_layer_info",
                                     stmt=f"find_layer_info('{GCODE_PATH}')",
                                     globals=globals(),
                                     number=number_of_executions)

print(exec_time_find_layer/number_of_executions)

exec_time_gcode_editor = timeit.timeit(setup="from gcode_editor import gcode_editor",
                                       stmt=f"gcode_editor('{GCODE_PATH}', '{PARAMETER_PATH}')",
                                       globals=globals(),
                                       number=number_of_executions)

print(exec_time_gcode_editor/number_of_executions)
