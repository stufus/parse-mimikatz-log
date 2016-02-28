#!/usr/bin/env python
import pprint
import re
import sys
import os

source_filename = sys.argv[1]
if not os.path.isfile(source_filename):
    err("Unable to read "+source_filename+". Make sure this is a valid file.\n")
    sys.exit(2)

f = open(source_filename,"r")
lines = f.readlines()
sys.stdout.write(".done\n")
f.close()

main_count = 0 
num_lines = len(lines)
current_dn = {}
for line in lines:

    main_count += 1
    percentage_count = "{0:.0f}%".format(float(main_count)/num_lines * 100)
    sys.stdout.write("\r  Processing line "+str(main_count)+"/"+str(num_lines)+" ("+percentage_count+")")
    sys.stdout.flush()
    
    val = re.match('^\s*\*\s+Username\s+:\s+(.+)\s*$', line.strip())
    if val != None:
        pprint.pprint(current_dn)
        sys.stdout.write("\n")
        current_dn = {}
        current_dn['username'] = val.group(1).strip()
        continue

    val = re.match('^\s*\*\s+(Domain|NTLM|SHA1|Password)\s+:\s+(.+)\s*$', line.strip())
    if val != None:
        current_dn[val.group(1).strip()] = val.group(2).strip()
