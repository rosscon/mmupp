#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Post processing script intended for use with MMU2S and Prucaslicer
"""

"""
Config keys
"""
CONFIG_KEY_DIP_DISTANCE      = ';mmupp:dip_distance'
CONFIG_KEY_DIP_INSERT_SPEED  = ';mmupp:dip_insert_speed'
CONFIG_KEY_DIP_RETRACT_SPEED = ';mmupp:dip_retract_speed'

CONFIG_KEY_RAMMING_TEMP      = ';mmupp:ramming_temp'


"""
Values
"""
DIP_DISTANCE = -1
DIP_INSERT_SPEED = 2000
DIP_RETRACT_SPEED = 4000

RAMMING_TEMP = -1


"""
Load input GCODE file into memory
"""
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("input_file", nargs="+")
args = parser.parse_args()
gcode_file = args.input_file[0]

with open(gcode_file) as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]


new_lines = [
    "; PROCESSED WITH MMUPP"
    ]



"""
Process line by line
"""
import re

for i in range(len(lines)):
    
    line = lines[i]
    
    """
    Check for any config changes in line
    """
    if line.startswith(CONFIG_KEY_DIP_DISTANCE):
        DIP_DISTANCE = float(line.split('=')[1])
    elif line.startswith(CONFIG_KEY_DIP_INSERT_SPEED):
        DIP_INSERT_SPEED = float(line.split('=')[1])
    elif line.startswith(CONFIG_KEY_DIP_RETRACT_SPEED):
        DIP_RETRACT_SPEED = float(line.split('=')[1])
    elif line.startswith(CONFIG_KEY_RAMMING_TEMP):
        RAMMING_TEMP = float(line.split('=')[1])
    


    """
    Dipping
    Check if previous lines are cooling moves prior to cuurent line being extraction
    """    
    # Check if current line is a retraction
    if re.match(r"G1 E-[0-9]", line):
        
        # Check if previous two lines are cooling moves, identified by having
        # an extract followed immediatly by a retract
        if re.match(r"G1.*E-[0-9]", lines[i-1]) and re.match(r"G1.*E[0-9]", lines[i-2]):
            
            if (DIP_DISTANCE > 0):
                # Add dip
                dip_insert = "G1 E" + str(DIP_DISTANCE) + " F" + str(DIP_INSERT_SPEED)
                dip_retract = "G1 E-" + str(DIP_DISTANCE) + " F" + str(DIP_RETRACT_SPEED)
                new_lines.append(";MMUPP: DIP ADDED")
                new_lines.append(dip_insert)
                new_lines.append(dip_retract)
                
                
                
    """
    Ramming temp
    """
    # Check for toolchange start
    if "; CP TOOLCHANGE START" in line and RAMMING_TEMP > 0:
        new_lines.append(";MMUPP: RAMMING TEMP ADDED")
        new_lines.append("M109 R" + str(RAMMING_TEMP))
    
    
    new_lines.append(line)




"""
Write back to gcode file
"""
with open(gcode_file, "w") as file:    
    for line in new_lines:    
        file.write(line + "\n")



