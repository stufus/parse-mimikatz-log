#!/usr/bin/env python

import re

def match_param(line,param):
    var = None

    if param in ['objectSid','sIDHistory','objectGUID']:
        var = re.match('^'+param+'::\s([^$]+)\s*$', line.strip())

    if var != None:
        return var.group(1).strip()

    return None

def update_struct(struct,name,val):
    if val==None:
        return False

    if not name in struct:
        struct[name] = []
    struct[name].append(val)
    return True

    for p in ldap_params:
        update_struct(current_dn, p, match_param(line,p))


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
for line in lines:

    main_count += 1
    percentage_count = "{0:.0f}%".format(float(main_count)/num_lines * 100)
    sys.stdout.write("\r  Reading line "+str(main_count)+"/"+str(num_lines)+" ("+percentage_count+")")
    sys.stdout.flush()

    var = re.match('^\s+(Username|Domain|NTLM|SHA1|Password)\s+:\s+(.+)\s*$', line.strip())
    # If it starts with DN, its a new "block"
    val = match_param(line,'dn')
    if val != None:
        process_struct(current_dn,sql)
        current_dn = {}
        current_dn['dn'] = val
        continue
