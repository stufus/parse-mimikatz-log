#!/usr/bin/env python
import tempfile
import argparse
import time
import pprint
import re
import sys
import os
import sqlite3

def process_input(sql,lines):
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

def create_db(filename):
    if filename == '':
	    db_file = tempfile.NamedTemporaryFile(delete=False)
	    db_filename = db_file.name+'.'+time.strftime('%Y%m%d%H%M%S')+'.mimikatz.db'
	    db_file.close()
    else:
        db_filename = filename

	sql = sqlite3.connect(filename)
	build_db_schema(sql)
    return sql

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--database', action='store', help='The location of the SQLite database. If this is not specified, a new one will be created. If it is specified and the file exists, it will be opened and used. If a name is specified that does not exist, it will be created.')
	parser.add_argument('--input', action='store', help='The mimikatz log file to read. If not specified, STDIN will be used.')
	args = parser.parse_args()
	
    if 'database' in args:
        if os.path.isfile(args['database']:
            sql, db_filename = sqlite3.connect(args['database'])
	        sys.stdout.write("Opening database: "+db_filename+"\n")
        else:
	        sys.stdout.write("New database created: "+db_filename+"\n")
            sql, db_filename = create_db(args['database'])
    else:
	    sys.stdout.write("No database file specified; new database created: "+db_filename+"\n")
        sql, db_filename = create_db(args['database'])

	lines = sys.stdin.readlines()
	process_input(lines)
	
	sql.close()
	sys.exit(0)
