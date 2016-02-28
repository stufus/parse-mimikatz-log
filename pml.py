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
    
    build = False
    if filename == None:
        # If the filename was not specified, create a new file with a temporary name
        # and build the schema.
        db_file = tempfile.NamedTemporaryFile(delete=False)
        db_filename = db_file.name+'.'+time.strftime('%Y%m%d%H%M%S')+'.mimikatz.db'
        db_file.close()
        build = True
    else:
        # The name was provided. 
        db_filename = filename
        if not os.path.isfile(db_filename):
            # If the name does not exist, rebuild the schema
            build = True

    sql = sqlite3.connect(db_filename)

    if build == True:
        build_db_schema(sql)

    return sql, db_filename

def display_totals(sql):
    c = sql.cursor()
    c.execute("select count(*) from creds")
    print "        Sets of credentials: "+str(c.fetchone()[0])
    c.execute("select count(distinct username) from view_usercreds")
    print "    Unique 'user' usernames: "+str(c.fetchone()[0])
    c.execute("select count(distinct password) from view_usercreds")
    print "    Unique 'user' passwords: "+str(c.fetchone()[0])
    return

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Basic parser for mimikatz \'logonPasswords\' log files.')
    parser.add_argument('-d', '--database', action='store', help='The location of the SQLite database. If this is not specified, a new one will be created. If it is specified and the file exists, it will be opened and used. If a name is specified that does not exist, it will be created.')
    parser.add_argument('-i', '--input', action='store', required=True, help='The mimikatz log file to read. Specify \'-\' to read from STDIN.')
    args = vars(parser.parse_args())
    
    if 'database' in args and args['database'] != None:
        if os.path.isfile(args['database']):
            sql = sqlite3.connect(args['database'])
            sys.stdout.write("Opening database: "+args['database']+"\n")
        else:
            sql, db_filename = create_db(args['database'])
            sys.stdout.write("New database created: "+db_filename+"\n")
    else:
        sql, db_filename = create_db(None)
        sys.stdout.write("No database file specified; new database created: "+db_filename+"\n")

    if 'input' in args and args['input'] != None and os.path.isfile(args['input']):
        sys.stdout.write("Reading from: "+args['input']+"\n")
        f = open(args['input'], 'r')
        lines = f.readlines()
        f.close()
    elif args['input'] == '-':
        sys.stdout.write("Reading from STDIN")
        lines = sys.stdin.readlines()

    sys.stdout.write("\n")
    process_input(sql,lines)
    sys.stdout.write("\n\n")
    
    display_totals(sql)
    sql.close()
    sys.exit(0)
