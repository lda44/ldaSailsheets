# Sailsheets db funtions
#
# This file contains all of the db functions we will call, 
# specific to the Sailsheets app.
#

from tkinter import *
from tkinter import messagebox
import sqlite3
import datetime 
from pathlib import Path
import csv

def export_excel():
        # This function simply exports each of the tables into separate .csv files 
        # into a Backups directory that is at the same level as the Apps directory.
        #
    
    today = datetime.date.today()
    
    backuppath = './Backups/' + str(today.year)
    p = Path(backuppath) 
    
    if not Path(backuppath).exists():
        p.mkdir(parents=True)

    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
    
    
    # This query gets the list of tables in the db.
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list = c.fetchall()
    
    for table_name in table_list:
        table_name = table_name[0]
        
        c.execute("SELECT * FROM " + table_name)
        result = c.fetchall()    
        # open the backup file: a=append, r=readonly, w=write (new)
        
        with open(backuppath + '/' + str(today) + '_' + table_name + '.csv', 'w', newline='') as f:
            w = csv.writer(f, dialect='excel')
            for record in result:
                w.writerow(record)
              
    # commit the command and close the db
    db.commit()
    db.close()
    messagebox.showinfo('', "All tables exported to backup folder.")


