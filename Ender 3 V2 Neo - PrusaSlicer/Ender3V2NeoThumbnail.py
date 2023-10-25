# This script converts the default PrusaSlicer thumbnail header to the format expected by the Ender 3 V2 Neo
# by CrealityExperts - no copyrights, share freely

import re, sys, os

#the first argument will always be the temporary gcode file prusaslicer generates.  The script applies the updates directly to this temporary file
gcode_filename = sys.argv[1]

with open(gcode_filename, "r") as f:
    lines = f.readlines()
    f.close()

#Prepare header values
document = "".join(lines)
ph = re.search('; generated by (.*)\n', document)
if ph is not None : document = document.replace(ph[0], "")

time = 0
match = re.search('; estimated printing time \(normal mode\) = (.*)\n', document)
if match is not None :
  h = re.search('(\d+)h',match[1])
  h = int(h[1]) if h is not None else 0
  m = re.search('(\d+)m',match[1])
  m = int(m[1]) if m is not None else 0
  s = re.search('(\d+)s',match[1])
  s = int(s[1]) if s is not None else 0
  time = h*3600+m*60+s

match = re.search('; filament used \[mm\] = ([0-9.]+)', document)
filament = float(match[1])/1000 if match is not None else 0

match = os.getenv('SLIC3R_LAYER_HEIGHT')
layer = float(match) if match is not None else 0

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
;TIME:{:d}
;Filament used: {:.6f}
;Layer height: {:.2f}
;MINX:1
;MINY:1
;MINZ:1
;MAXX:1
;MAXY:1
;MAXZ:1
;POSTPROCESSED

""".format(time, filament, layer)
first_non_comment_index = next(i for i,string in enumerate(lines) if not string.startswith(";") and string.strip() != "")
lines = lines[:first_non_comment_index] + curaText.splitlines(True) + lines[first_non_comment_index:]

data = "".join(lines)
data = data.replace("thumbnail_JPG", "jpg")

try:
    # save the updated file
    with open(gcode_filename , "w") as of:
        of.write(data)
        of.close()
except:
    print('Error writing output file')
    input()
finally:
    of.close()
    f.close()