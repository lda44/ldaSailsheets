import sqlite3
import datetime 
from datetime import date
import csv

def UpdateMembers(allmembersfile):
    #####################################################################
    # 
    # This module reads the AllMembers.csv file exported from Club Express
    # and compares each member in that file to the Members table in the db.
    # If any records are not identical, the Members table is then updated
    # to reflect what is in the AllMembers.csv file because that is the 
    # official membership record.
    #
    # The following fields should match:
    #   Members usagetable  AllMembers.csv (field/column #)
    #    m_id int           member_number (A)
    #    m_name text        last_name (C) + ', ' + first_name (B)
    #    m_status text      status (AD)
    #    m_expdate text     date_expired (AB)
    #    m_type text        membership_type (AE)
    #    m_prime text       primary_member (AI)

    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
        
    """CREATE TABLE Members (m_id int primary key,
        m_name text,
        m_status text,
        m_expdate text,
        m_type text,
        m_prime text,
        m_suspended int, not used set to 0
        m_debt int, not used set to 0
        m_ignore int); not used set to 0
    CREATE TABLE Settings (discount int, pw text, delay int);
    """

    #####################################################################
    # Create a new table to be used to update the members
    # This table will be populated by importing the AllMembers.CSV file
    #
    c.execute('DROP TABLE IF EXISTS UpdateMembers')
    
    c.execute("""CREATE TABLE UpdateMembers(m_id int, 
        m_name text,
        m_status text,
        m_expdate text,
        m_type text,
        m_prime text)
        """)

    # Open the AllMembers csv file and put the data into memory
    with open(allmembersfile, 'r', newline='') as f:
        r = csv.DictReader(f)
        to_db = [(i['member_number'], 
            i['last_name'] + ', ' + i['first_name'],
            i['status'],
            i['date_expired'],
            i['membership_type'],
            i['primary_member']) for i in r]

    # insert each record into the new table
    c.executemany("""INSERT INTO UpdateMembers (m_id, 
        m_name, 
        m_status, 
        m_expdate, 
        m_type, 
        m_prime
        )
        VALUES (?, ?, ?, ?, ?, ?);
        """, to_db)

    # Remove some records we know get pulled down.
    c.execute("DELETE FROM UpdateMembers WHERE m_name = 'REMOVED, NAME'")

    # Delete the old Members table
    c.execute("DROP TABLE IF EXISTS Members")

    # Rename the new table to Members
    c.execute("ALTER TABLE UpdateMembers RENAME TO Members")

    # Commit the changes to the db and then close the db
    db.commit()
    db.close()


