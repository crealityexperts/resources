# This script converts the default PrusaSlicer thumbnail header to the format expected by the Ender 3 V2 Neo
# by CrealityExperts - no copyrights, share freely

import re, sys

#the first argument will always be the temporary gcode file prusaslicer generates.  The script applies the updates directly to this temporary file
gcode_filename = sys.argv[1]

with open(gcode_filename, "r") as f:
    lines = f.readlines()
    f.close()

# fix the formatting of the first line
# starting format: 
# ; thumbnail_JPG begin 200x200 19704
# # desired format: 
# ; jpg begin 200*200 14778 3 197 500
start_index = next((i for i, line in enumerate(lines) if "thumbnail_JPG" in line), None)
if start_index is not None:
    lines = lines[start_index:]
    match = re.search(r"\d+$", lines[0])
    if match:
        number = int(match.group())
        new_number = int(number * 3/4)
        lines[0] = lines[0].replace(str(number), str(new_number)).replace('x','*').replace('\n','') + " 3 197 500\n"


# The Ender 3 V2 Neo expects these lines to be present before the actual GCode starts
    curaText = """;FLAVOR:Marlin
;TIME:0
;Filament used: 0m
;Layer height: 0
;MINX:1
;MINY:1
;MINZ:1
;MAXX:1
;MAXY:1
;MAXZ:1
;POSTPROCESSED
"""
first_non_comment_index = next(i for i,string in enumerate(lines) if not string.startswith(";") and string.strip() != "")
lines = lines[:first_non_comment_index] + curaText.splitlines(True) + lines[first_non_comment_index:]

data = "".join(lines)
data = data.replace("thumbnail_JPG", "jpg")

# save the updated file
with open(gcode_filename , "w") as of:
    of.write(data)
    of.close()
