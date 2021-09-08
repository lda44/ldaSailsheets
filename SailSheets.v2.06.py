#####################################################################
#
'''\
    NavyPaxSail Sailsheets application

        VERSION 2

    This app is for stand alone use at the Clubhouse. This version 
    fixes bugs in VERSION 1 and replaces the older C++ code and 
    libraries with Python code and libraries for easier maintenance
    in the future.

    All paths used by this app are:
        Main:   /home/NPSC
        App:    /home/NPSC/SailSheets
        Report: /home/NPSC/SailSheets/Reports
        Backup: /home/NPSC/SailSheets/Backups
        Import: /home/NPSC/SailSheets/Transfer

    For versioning X.YY.ZZ:
        X = schema changes or changes in business process (major outcomes)
        YY = changes in functionality, but business process flow does not change
        ZZ = bug fixes but no changes in functionality (aka just making it work as intended)

    This app uses sqlite3, tkinter, and tkcalendar
    Ensure these are installed on the linux box if using for the first 
    time.
 

    Program Structure:
        Main module
            Admin module (admin use only)
                Edit Settings
                Edit Members table
                Edit Boats table
                Edit Purpose table
                Import AllMembers.csv from Club Express
                Export all tables to Excel(csv format)
                Create monthly reports
                    Boat Usage (includes NPSC boats)
                    Boat Usage (excludes NPSC boats)
                    Member Usage w rental fees for upload to Club Express
           Sail Plan module (all users)

PLEASE NOTE:
    The app checks the user (logged in via Linux) and if NPSC_Admin 
    allows all functions to be available.  If not NPSC_Admin (any 
    other user -- should be NPSC_Sailor) the app will only allow
    Sail Plan entry/edit.  
\
 '''

#####################################################################
#
# First task is to import any necessary libraries
# All of these libraries are part of base Python v3

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar, DateEntry
import sqlite3
import datetime as dt
from datetime import timedelta
import logging
import os
import pwd

# the following library if installed via pip: pip install screeninfo
from screeninfo import get_monitors

# next import the separate modules of the Sailsheets app
import SS_admin
import SS_db_functions
import editmembers
import editboats
import editpurpose
import editledger
import LiabilityWaiver
import SS_reports
import sailplan
import updatemembers

def main():
    # Insert the Main code here
    # Declare any global variables -- need to eliminate global variables
    global root

    # Set up the logging system
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
    file_handler = logging.FileHandler(__name__ + '.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Start with the main window (aka root)
    root = Tk()
    root.title("Welcome to Sailsheets")
    root.overrideredirect(True)
    # set the default window size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    
    num_monitors = len(get_monitors())

    app_width = int((screen_width / num_monitors) * .70)
    app_height = int(screen_height * .80)

    
    x = (screen_width / (2 * num_monitors)) - (app_width / 2) # screen_width / 4 for 2 monitors, /2 for 1
    y = (screen_height / 2) - (app_height / 2)

    root.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

    # Deterime if the user is NPSC_Admin or NPSC_Sailor.
    # 
    # if the user is NPSC_Admin then all the menus are enabled.  
    # Otherwise the menus are disabled and the only function is the
    # Sail Plan creation (check out and check in).
    #
    my_user = pwd.getpwuid(os.getuid()).pw_name
    #my_user = 'NPSC_Sailor' # used for testing
    my_user = 'npscadmin' # used for testing
    logger.info(my_user + ' logged in')
        
    if my_user == 'npscadmin':
        admin_state = "normal"
        main_banner = "ADMIN -- Navy Patuxent Sailing Club -- ADMIN"
        main_color = "blue"
    else:
        admin_state = "disabled"
        main_banner = "Navy Patuxent Sailing Club"
        main_color = "blue"


    # Create our menus
    my_menu = Menu(root)
    root.config(menu=my_menu)


    # Creae menu items
    # File menu just contains the exit command
    file_menu = Menu(my_menu)
    my_menu.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Exit", command=root.quit)

    # Admin menu are those admin items that are gross updates
    admin_menu = Menu(my_menu)
    my_menu.add_cascade(label="Admin", menu=admin_menu, state=admin_state)

    admin_menu.add_command(label="Update Membership", 
        command=lambda: SS_admin.a_update_members(root))

    admin_menu.add_command(label="Backup ALL to Excel", 
        command=lambda: SS_db_functions.export_excel())


    # Edit menu are those admin items that "edit" single records
    edit_menu = Menu(my_menu)
    my_menu.add_cascade(label="Edit", menu=edit_menu, state=admin_state)

    edit_menu.add_command(label="Boats", 
        command=lambda: editboats.editboats(root))

    edit_menu.add_command(label="Sail Plan Purpose", 
        command=lambda: editpurpose.editpurpose(root))

    edit_menu.add_command(label="Member Data", 
        command=lambda: editmembers.editmembers(root))

    edit_menu.add_command(label="Settings", 
        command=lambda: SS_admin.editsettings(root))

    edit_menu.add_separator()

    edit_menu.add_command(label="Sail Plans", 
        command=lambda: sailplan.sailplanmenu(root))

    edit_menu.add_command(label="Ledger Table (raw)", 
        command=lambda: editledger.e_ledger(root))


    # These are the monthly reports
    reports_menu = Menu(my_menu)
    my_menu.add_cascade(label="Reports", menu=reports_menu, state=admin_state)
    reports_menu.add_command(label="Create Monthly Reports", 
        command=lambda: SS_admin.monthly_reports(root))
    reports_menu.add_command(label="Create Member Use Log", 
        command=lambda: SS_admin.member_usage_log(root))


    # Let's put a label at the top of the window
    my_label = Label(root, text = main_banner, fg=main_color, font=("Helvetica", 24))
    my_label.pack()


    # If the user is not the admin, then just show the sail plan menu
    if my_user != 'npscadmin':
        sailplan.sailplanmenu(root)

    root.mainloop()

if __name__ == '__main__':
    main()
#
#
# End of application.
###########################################################