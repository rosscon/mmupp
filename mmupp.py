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
CONFIG_KEY_DIP_POST_PAUSE    = ';mmupp:dip_post_pause'

CONFIG_KEY_RAMMING_TEMP      = ';mmupp:ramming_temp'


"""
Config reset keys
"""
CONFIG_KEY_DIP_DISTANCE_RST      = ';mmupp:rst:dip_distance'
CONFIG_KEY_DIP_INSERT_SPEED_RST  = ';mmupp:rst:dip_insert_speed'
CONFIG_KEY_DIP_RETRACT_SPEED_RST = ';mmupp:rst:dip_retract_speed'
CONFIG_KEY_DIP_POST_PAUSE_RST    = ';mmupp:rst:dip_post_pause'

CONFIG_KEY_RAMMING_TEMP_RST      = ';mmupp:rst:ramming_temp'


"""
Values
"""
DIP_DISTANCE = -1
DIP_INSERT_SPEED = 2000
DIP_RETRACT_SPEED = 4000
DIP_POST_PAUSE = 8000

RAMMING_TEMP = -1


DIP_DISTANCE_PREV = -1
DIP_INSERT_SPEED_PREV = 2000
DIP_RETRACT_SPEED_PREV = 4000
DIP_POST_PAUSE_PREV = 8000

RAMMING_TEMP_PREV = -1


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
        DIP_DISTANCE_PREV = DIP_DISTANCE
        DIP_DISTANCE = float(line.split('=')[1])
    
    elif line.startswith(CONFIG_KEY_DIP_INSERT_SPEED):
        DIP_INSERT_SPEED_PREV = DIP_INSERT_SPEED
        DIP_INSERT_SPEED = float(line.split('=')[1])
   
    elif line.startswith(CONFIG_KEY_DIP_RETRACT_SPEED):
        DIP_RETRACT_SPEED_PREV = DIP_RETRACT_SPEED
        DIP_RETRACT_SPEED = float(line.split('=')[1])
    
    elif line.startswith(CONFIG_KEY_DIP_POST_PAUSE):
        DIP_POST_PAUSE_PREV = DIP_POST_PAUSE
        DIP_POST_PAUSE = int(line.split('=')[1])
    
    elif line.startswith(CONFIG_KEY_RAMMING_TEMP):
        RAMMING_TEMP_PREV = RAMMING_TEMP
        RAMMING_TEMP = float(line.split('=')[1])
        
        
    """
    Check for any config resets
    """
    if line.startswith(CONFIG_KEY_DIP_DISTANCE_RST):
        DIP_DISTANCE = DIP_DISTANCE_PREV
    
    elif line.startswith(CONFIG_KEY_DIP_INSERT_SPEED_RST):
        DIP_INSERT_SPEED = DIP_INSERT_SPEED_PREV
   
    elif line.startswith(CONFIG_KEY_DIP_RETRACT_SPEED_RST):
        DIP_RETRACT_SPEED = DIP_RETRACT_SPEED_PREV
    
    elif line.startswith(CONFIG_KEY_DIP_POST_PAUSE_RST):
        DIP_POST_PAUSE = DIP_POST_PAUSE_PREV
    
    elif line.startswith(CONFIG_KEY_RAMMING_TEMP_RST):
        RAMMING_TEMP = RAMMING_TEMP_PREV
    


    """
    Dipping
    Check if previous lines are cooling moves prior to cuurent line being extraction
    """    
    # Check if current line is a retraction
    if re.match(r"G1 E-[0-9]", line):
        
        # Check if previous two lines are cooling moves, identified by having
        # an extract followed immediatly by a retract
        if re.match(r"G1.*E-[0-9]", lines[i-1]) and re.match(r"G1.*E[0-9]", lines[i-2]):
            
            if DIP_DISTANCE > 0:
                # Add dip
                dip_insert = "G1 E" + str(DIP_DISTANCE) + " F" + str(DIP_INSERT_SPEED)
                dip_retract = "G1 E-" + str(DIP_DISTANCE) + " F" + str(DIP_RETRACT_SPEED)
                new_lines.append(";MMUPP: DIP ADDED")
                new_lines.append(dip_insert)
                new_lines.append(dip_retract)
                
                # Repeat last cooling moves
                new_lines.append(lines[i-2])
                new_lines.append(lines[i-1])
                new_lines.append(lines[i-2])
                new_lines.append(lines[i-1])
                new_lines.append(lines[i-2])
                new_lines.append(lines[i-1])
                
                if DIP_POST_PAUSE > 0:
                    new_lines.append("G4 P" + str(DIP_POST_PAUSE))
                
                
                
    """
    Ramming temp
    """
    # Check for toolchange start
    if "; CP TOOLCHANGE START" in line and RAMMING_TEMP > 0:
        new_lines.append(";MMUPP: RAMMING TEMP ADDED")
        new_lines.append("M109 R" + str(RAMMING_TEMP))
        
    if "; CP TOOLCHANGE LOAD" in line:
        
        print(i)
        i_1 = (i + 1)
        print(i_1)
        i_2 = (i_1 + 1)
        print(i_2)
        
        if 'G1' not in lines[i_1]:
            print (lines[i_1])
            i_1 = (i_1 + 1)
            i_2 = (i_1 + 1)
            
        while 'G1' not in lines[i_2]:
            print (lines[i_2])
            i_2 = i_2 + 1
        
        cmd1_extrude_amount = re.findall('E\d*\.?\d+', lines[i_1])[0]
        cmd2_extrude_amount = re.findall('E\d*\.?\d+', lines[i_2])[0]
        
        print (cmd1_extrude_amount)
        print (cmd2_extrude_amount)
        
        total_extrude = float(cmd1_extrude_amount[1:]) + float(cmd2_extrude_amount[1:])
        
        print (total_extrude)
        
        REAMAINDER = 5.0
        
        cmd1_new_extrude_amount = str(total_extrude - REAMAINDER)
        
        lines[i_1] = lines[i_1].replace(cmd1_extrude_amount, 'E' + cmd1_new_extrude_amount)
        lines[i_2] = lines[i_2].replace(cmd2_extrude_amount, 'E' + str(REAMAINDER))
        
        print()
        
        
    
    
    new_lines.append(line)




"""
Write back to gcode file
"""
with open(gcode_file, "w") as file:    
    for line in new_lines:    
        file.write(line + "\n")



