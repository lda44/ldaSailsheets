# Sailsheets
NavyPaxSail Sailsheets program. Using Git/GitHub to maintain and archive the source code.
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
