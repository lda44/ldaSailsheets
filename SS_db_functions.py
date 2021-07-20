# Sailsheets db funtions
#
# This file contains all of the db functions we will call, 
# specific to the Sailsheets app.
#

import sqlite3
from tkinter import *
import csv

def export_excel():
        # This function simply exports each of the tables into separate .csv files 
        # into a Backups directory that is at the same level as the Apps directory.
        #
    

    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
    
    
    # This query gets the list of tables in the db.
    c.execute("SELECT name FROM sqlite_master WHERE type='table';")
    table_list = c.fetchall()
    
    import datetime
    today = datetime.date.today()
    
    for table_name in table_list:
        table_name = table_name[0]
        
        c.execute("SELECT * FROM " + table_name)
        result = c.fetchall()    
        # open the backup file: a=append, r=readonly, w=write (new)
        
        with open('./Backups/' + str(today) + '_' + table_name + '.csv', 'w', newline='') as f:
            w = csv.writer(f, dialect='excel')
            for record in result:
                w.writerow(record)
              
    # commit the command and close the db
    db.commit()
    db.close()


def show_all():

    # connect to the db and create the cursor
    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
    c.execute("SELECT * FROM Boats")
    #c.execute("SELECT * FROM Boats WHERE Boats_Class = 'D'")
    #print(c.fetchone())
    #print(c.fetchmany(2))
    
    boatlist = c.fetchall()
    #print()

    boats = ""
    for item in boatlist:
    #    print("\t", item[1], "\t", item[3])
        boats += "\t" + item[1] + "\t" + item[3] + "\n"
    
    new = Toplevel()
    new.title("Show Table")
    new.geometry("240x350")
    
    query_label = Label(new, text=boats)
    query_label.grid(row=0, column=0, columnspan=2)
    
    new.mainloop()

    # commit the command and close the db
    db.commit()
    db.close()
    #print()
 

def add_one_boat(Boats_Id, Boats_Type, Boats_Class, 
        Boats_Name, Boats_QualRequired, Boats_E5HourRate, BoatsE5DayRate, 
        Boats_HourRate, Boats_DayRate, Boats_NpscHourRate, BoatsNpscDayRate, 
        Boats_Down, Boats_DownDescription, Boats_Retired):
    # connect to the db and create the cursor
    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
    c.execute("INSERT INTO Boats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
        (Boats_Id, Boats_Type, Boats_Class, 
        Boats_Name, Boats_QualRequired, Boats_E5HourRate, BoatsE5DayRate, 
        Boats_HourRate, Boats_DayRate, Boats_NpscHourRate, BoatsNpscDayRate, 
        Boats_Down, Boats_DownDescription, Boats_Retired))
    
    # commit the command and close the db
    db.commit()
    db.close()
        
def add_many_boats(list):
    # connect to the db and create the cursor
    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
    c.execute("INSERT INTO Boats VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", 
        (Boats_Id, Boats_Type, Boats_Class, 
        Boats_Name, Boats_QualRequired, Boats_E5HourRate, BoatsE5DayRate, 
        Boats_HourRate, Boats_DayRate, Boats_NpscHourRate, BoatsNpscDayRate, 
        Boats_Down, Boats_DownDescription, Boats_Retired))
    
    

    # commit the command and close the db
    db.commit()
    db.close()

def del_one_boat(id):
    # connect to the db and create the cursor
    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
    c.execute("DELETE FROM Boats WHERE Boats_Id = " + id)
    
        # commit the command and close the db
    db.commit()
    db.close()
