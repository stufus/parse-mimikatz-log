#!/usr/bin/env python
import tempfile
import time
import pprint
import re
import sys
import os
import sqlite3

# Build the SQL database schema
def build_db_schema(sql):
    
    c = sql.cursor()

    # Create the tables
    c.execute('''CREATE TABLE creds 
        ('domain' TEXT, 'username' TEXT, 'password' TEXT, 'ntlm' TEXT, 'sha1' TEXT, PRIMARY KEY ('domain','username','password','ntlm','sha1'))
        ''')

    c.execute('''CREATE VIEW view_usercreds AS select distinct domain,username,password from creds where password != '' and username != '' and substr(username,-1) != '$' ''')
    sql.commit()
    return

def insert_into_db(sql,current):
    c = sql.cursor()
    
    fields = ['Domain','Username','NTLM','SHA1','Password']
    for f in fields:
        if f in current:
            if current[f] == '(null)':
                current[f] = ''
        else:
            current[f] = ''

    if current['Username'] != '' and (current['Password'] != '' or current['NTLM'] != ''):
        c.execute('replace into creds (domain,username,password,ntlm,sha1) VALUES (?,?,?,?,?)', 
            [current['Domain'],current['Username'],current['Password'],current['NTLM'],current['SHA1']])

    sql.commit()
    return

sys.stdout.write("Creating database: ")
db_file = tempfile.NamedTemporaryFile(delete=False)
db_filename = db_file.name+'.'+time.strftime('%Y%m%d%H%M%S')+'.mimikatz.db'
db_file.close()
sql = sqlite3.connect(db_filename)
build_db_schema(sql)
sys.stdout.write(db_filename+"\n")

lines = sys.stdin.readlines()

main_count = 0 
num_lines = len(lines)
current = {}
for line in lines:

    main_count += 1
    percentage_count = "{0:.0f}%".format(float(main_count)/num_lines * 100)
    sys.stdout.write("\r  Processing line "+str(main_count)+"/"+str(num_lines)+" ("+percentage_count+")")
    sys.stdout.flush()
    
    val = re.match('^\s*\*\s+Username\s+:\s+(.+)\s*$', line.strip())
    if val != None:
        insert_into_db(sql,current)
        current = {}
        current['Username'] = val.group(1).strip()
        continue

    val = re.match('^\s*\*\s+(Domain|NTLM|SHA1|Password)\s+:\s+(.+)\s*$', line.strip())
    if val != None:
        current[val.group(1).strip()] = unicode(val.group(2), errors='ignore')

sql.close()
sys.exit(0)
