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

#####################################################################
#
# First task is to import any necessary libraries
# tkinter is a library to doing a gui front end
# sqlite3 is a library for working with a sqlite db

from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar, DateEntry
import sqlite3
import datetime as dt
from datetime import timedelta
import os
import pwd
import SS_db_functions
import SS_reports
import updatemembers
import editmembers
import editpurpose
import editledger
import LiabilityWaiver

# Insert the Main code here
# Declare any global variables (these are used in other functions but not passed)
global root

# Start with the main window (aka root)
root = Tk()
root.title("Welcome to Sailsheets")

# set the default window size
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
app_width = int((screen_width / 2) * .70)
app_height = int(screen_height * .80)

x = (screen_width / 4) - (app_width / 2) # screen_width / 4 for 2 monitors, /2 for 1
y = (screen_height / 2) - (app_height / 2)

root.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

#####################################################################
# Common functions are here
#
def clear_all_frames():
    for stuff in root.winfo_children():
        if str(stuff) != ".!menu" and str(stuff) != ".!label":
            stuff.destroy()

#####################################################################
# 
# Sail Plan
#
def sailplanmenu():
    # what works on 7/19:
    #
    # - Add a sailplan.  
    # - Edit a sailplan
    # -- add crewmembers
    # -- add guests
    # -- delete crewmembers or guests
    # - Delete an open sailplan and its crewlist
    # 
    # Things that don't work:
    # - Close a sailplan & post to the Ledger File
    # - Disabling fields we don't want user to change
    # 
    # 
    
    #################################################################
    #
    # Functions required for the sailplanmenu function, only
    #
    def q_sp_table(mydate):
        
        # This function first clears the sailplan treeview then 
        # repopulates the treeview with the sailplans for the date
        # provided.
        #
        # Declare the global variables to be modified here
        global my_tree

        #mdt1 = '2021-07-01'
        #mdt2 = '2021-07-02'

        # Clear the tree view
        for record in my_tree.get_children():
            my_tree.delete(record)

        # Based on date received in mydate, let's build a query to
        # pull in sail plan data for just that date
        #
        mdt1 = mydate.isoformat()[:10]
        mdt2 = (mydate + timedelta(days=1)).isoformat()[:10]
        #print('Query Table: ' + mdt1 + '\t' + mdt2 + '\n')

        # Open the db and establish a cursor
        db = sqlite3.connect('Sailsheets.db')
        c = db.cursor()

        # query to pull the data from the table
        c.execute("""SELECT sp_id, sp_timeout, sp_skipper_id, Members.m_name as skipper, 
            sp_sailboat, sp_purpose, sp_description, sp_estrtntime, sp_timein, sp_completed 
            FROM SailPlan JOIN Members ON sp_skipper_id=Members.m_id
            WHERE sp_timeout >= :qdt1 AND sp_timeout < :qdt2"""
            , {'qdt1': mdt1, 'qdt2': mdt2,})
        
        # fetch the data
        mylist = c.fetchall()
        #print('My SP List:' + '\n' + str(mylist))

        # Create striped row tags
        my_tree.tag_configure('oddrow', background='#D3D3D3') # light silver
        my_tree.tag_configure('evenrow', background='silver') # dark silver

        count = 0
        for stuff in mylist:
            if count % 2 == 0:
                my_tree.insert(parent='', index='end', values=stuff, tags=('evenrow',))
            else:
                my_tree.insert(parent='', index='end', values=stuff, tags=('oddrow',))
            count += 1
        
        # commit and close the DB
        db.commit()
        db.close()
        
        return

    #################################################################
    # 
    # Clear the entry boxes
    #
    def clearboxes():
        # Clear entry boxes
        sp_id_e.delete(0, END)
        sp_to_e.delete(0, END)
        sp_skid_e.delete(0, END)
        sp_boat_e.delete(0, END)
        sp_purp_e.delete(0, END)
        sp_desc_e.delete(0, END)
        sp_eta_e.delete(0, END)
        sp_ti_e.delete(0, END)
        sp_comp_e.delete(0, END)

    #################################################################
    # 
    # Add the record you just created to the db
    #
    # NEVER DO THIS IN THE SAILPLAN TABLE!!!

    #################################################################
    # 
    # Select the record you picked
    #
    def select_record(e):
        
        # Grab the record number
        selected = my_tree.focus()

        # Grab record values
        values = my_tree.item(selected, 'values')
        return [values[0], values[9]]

        
    #################################################################
    # 
    # Add or edit the sail plan
    #
    def add_edit_record(mysp_id, sp_closed):
        """\
            options for mysp_id are -1 (new), or the sailplan ID
            options for sp_closed are 0 (still open) or 1 (closed)
                if the sp is closed, then the information will only
                be displayed, and editable fields are no longer 
                editable.

        """ 
        global my_tree, my_date
        
        #################################################################
        # Schema:
        #
        """ CREATE TABLE IF NOT EXISTS "SailPlan" (sp_id INTEGER PRIMARY KEY, 
        sp_timeout text,
        sp_skipper_id real,
        sp_sailboat text,
        sp_purpose text,
        sp_description text,
        sp_estrtntime text,
        sp_timein text,
        sp_hours real,
        sp_feeeach real,
        sp_feesdue real,
        sp_mwrbilldue real,
        sp_billmembers int,
        sp_completed int);
        """

        # test using any sp_id > 3550

        # Create a new window
        sp_win = Tk()
        sp_win.title("Sail Plan")
        screen_width = sp_win.winfo_screenwidth()
        screen_height = sp_win.winfo_screenheight()
        app_width = int((screen_width / 2) * .39)
        app_height = int(screen_height * .60)

        x = (screen_width / 4) - (app_width / 2) # screen_width / 4 for 2 monitors, /2 for 1
        y = (screen_height / 2) - (app_height / 2)

        sp_win.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

        # the following are variables passed to the function when executed. 
        # Once testing is complete, the function will be altered to have thise
        # as input variables to the function so that it can execute both 
        # add and edit of the sailplan.  
        #   
        global edit_state, add_state, crew_tree

        #mysp_id = -1 # -1 = new sailplan, all others are edit to existing sailplan
        #sp_closed = 0 # 1 = the sailplan is closed, 0 = the sailplan is still open
        sp_date = dt.datetime.today().isoformat(sep=' ', timespec='seconds') 
        # date for ledger file based on sp_datein; 
        # not recorded until complete?

        if mysp_id == -1:
            edit_state = "disabled"
            add_state = "disabled"
        else:
            edit_state = "normal"


        #########################################################
        # Begin internal "add a sailplan" functions here
        #
        def makecrewtree(crewqry, mytree):
            # Clear the tree view
            for record in mytree.get_children():
                mytree.delete(record)
            count = 0
            for stuff in crewqry:
                if count % 2 == 0:
                    mytree.insert(parent='', index='end', values=stuff, tags=('evenrow',))
                else:
                    mytree.insert(parent='', index='end', values=stuff, tags=('oddrow',))
                count += 1

            # Create striped row tags
            mytree.tag_configure('oddrow', background='#D3D3D3') # light silver
            mytree.tag_configure('evenrow', background='white') 

            return mytree



        def getcrewlist(spid):
            #
            # Open the db and establish a cursor
            db = sqlite3.connect('Sailsheets.db')
            c = db.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS "openspcrew"(o_id real, 
                o_name text,
                o_spid int,
                o_skipper int,
                o_billtoid real
                )
                """)
            # query to pull the data from the table
            c.execute("""SELECT o_id, o_name, o_billtoid FROM openspcrew 
                WHERE o_spid = :ospid ORDER BY o_name""", {'ospid': spid,})
            # fetch the data
            crewqry = c.fetchall()
            # commit and close the DB
            db.commit()
            db.close()
            return crewqry



        def get_boat_list():
            # Open the db and establish a cursor
            db = sqlite3.connect('Sailsheets.db')
            c = db.cursor()

            # query to pull the data from the boats table
            c.execute("""SELECT boat_name FROM Boats WHERE Retired=0 ORDER BY boat_name""")

            # fetch the data
            myboatlist = [x[0] for x in c.fetchall()]

            # commit and close the DB
            db.commit()
            db.close()
            return myboatlist


        def get_purpose_list():
            # Open the db and establish a cursor
            db = sqlite3.connect('Sailsheets.db')
            c = db.cursor()

            # query to pull the data from the boats table
            c.execute("""SELECT p_name FROM Purpose ORDER BY p_name""")

            # fetch the data
            mypurplist = [x[0] for x in c.fetchall()]

            # commit and close the DB
            db.commit()
            db.close()
            return mypurplist


        def get_member_list():
            # Open the db and establish a cursor
            db = sqlite3.connect('Sailsheets.db')
            c = db.cursor()

            # query to pull the data from the boats table
            c.execute("""SELECT m_id, m_name FROM Members WHERE m_status = 'Active' ORDER BY m_name""")

            # fetch the data
            memberlist = c.fetchall()

            # commit and close the DB
            db.commit()
            db.close()
            return memberlist


        def getskipid(my_id):
            if my_id == '':
                return 0
            else:
                # Open the db and establish a cursor
                db = sqlite3.connect('Sailsheets.db')
                c = db.cursor()

                # query to pull the data from the boats table
                c.execute("""SELECT m_id FROM Members 
                    WHERE m_id = :mid""", {'mid': float(my_id)})

                # fetch the data
                skip_id = c.fetchone()
                
                # commit and close the DB
                db.commit()
                db.close()

                return skip_id


        def setskippername():
            pass

        def get_name(my_id):
            if my_id == '':
                return ''
            else:
                # Open the db and establish a cursor
                db = sqlite3.connect('Sailsheets.db')
                c = db.cursor()
                # query to pull the data from the boats table
                c.execute("""SELECT m_name FROM Members 
                    WHERE m_id = :mid""", {'mid': float(my_id)})

                # fetch the data
                my_name = c.fetchone()
                
                # commit and close the DB
                db.commit()
                db.close()

                return my_name[0]


        def update_sailplan(myspid):
            # pull data from entry boxes and save to the sp table
            # as an open sail plan
            #
            db = sqlite3.connect('Sailsheets.db')
            c = db.cursor()
            c.execute("""UPDATE SailPlan set
                sp_timeout = :spto, 
                sp_skipper_id = :spskid, 
                sp_sailboat = :spboat, 
                sp_purpose = :sppurp, 
                sp_description = :spdesc, 
                sp_estrtntime = :speta, 
                sp_timein = :spti, 
                sp_hours = :sphrs, 
                sp_feeeach = :spfee, 
                sp_feesdue = :spdue, 
                sp_mwrbilldue = :spbill, 
                sp_billmembers = :spnrob, 
                sp_completed = :spcomp
                WHERE sp_id= :spid""",
                {
                'spto': sp_to_e.get(),
                'spskid': sp_skid_e.get(), 
                'spboat': boat_combo.get(), 
                'sppurp': purp_combo.get(), 
                'spdesc': sp_desc_e.get(), 
                'speta': sp_eta_e.get(), 
                'spti': '', 
                'sphrs': 0,
                'spfee': 0,
                'spdue': 0,
                'spbill': 0,
                'spnrob': len(getcrewlist(myspid)),
                'spcomp': 0,
                'spid': myspid,
                })
            
            # Commit the change and close the database
            db.commit()
            db.close()

            # now close the window and return to the screen
            sp_win.destroy()

            # repopulate the tree with the table's values
            q_sp_table(dt.date.fromisoformat(my_date))

            return


        def checkin_sailplan():
            pass

        def get_sailplan_df(myspid):
            #
            # pull data from sp table for use in the entry boxes 
            #
            db = sqlite3.connect('Sailsheets.db')
            c = db.cursor()
            c.execute("""SELECT * FROM SailPlan WHERE sp_id= :spid""",
                {'spid': myspid,})
            sailplan = c.fetchone()
            
            # Commit the change and close the database
            db.commit()
            db.close()
            return sailplan


        def newblanksailplan(): 
            db = sqlite3.connect('Sailsheets.db')
            c = db.cursor()

            # execute the update query
            c.execute("""INSERT INTO SailPlan (sp_timeout, sp_skipper_id, 
                sp_sailboat, sp_purpose, sp_description, sp_estrtntime, 
                sp_timein, sp_hours, sp_feeeach, sp_feesdue, sp_mwrbilldue, 
                sp_billmembers, sp_completed)
                VALUES (:spto, :spskid, :spboat, :sppurp, :spdesc, :speta, 
                :spti, :sphrs, :spfee, :spdue, :spbill, :spnrob, :spcomp)
                """,
                {
                'spto': dt.datetime.today().isoformat(sep=' ', timespec='seconds'),
                'spskid': 1, 
                'spboat': '', 
                'sppurp': '', 
                'spdesc': '', 
                'speta': (dt.datetime.today() + timedelta(hours=4)).isoformat(sep=' ', timespec='seconds'), 
                'spti': '', 
                'sphrs': 0,
                'spfee': 0,
                'spdue': 0,
                'spbill': 0,
                'spnrob': 0,
                'spcomp': 0
                })
            db.commit()
            db.close()
            return c.lastrowid


        def enter_press(event): 
            if sp_skid_e.get() == '': return
            skip_n_combo.set(name_dict[float(sp_skid_e.get())])


        def set_skipper(event): 
            # confirms works 7/15
            global crew_tree
            if sp_skid_e.get() == '': return
            skip_n_combo.set(name_dict[float(sp_skid_e.get())])
            crewlist = [x[1] for x in add_crew(1, 1, skip_n_combo.get(), 
                sp_skid_e.get(), sp_skid_e.get())]
            crew_tree = makecrewtree(crewlist, crew_tree)


        def choosecrew(event):
            # confirms works 7/15
            global crew_tree
            crewid = float(id_dict[a_member_c.get()])
            a_club_id_e.insert(0, crewid)
            crewqry = add_crew(1, 0, a_member_c.get(), crewid, crewid)
            crewlist = [x[1] for x in crewqry]
            crew_tree = makecrewtree(crewqry, crew_tree)


        def chooseguest(event):
            # confirms works 7/15
            global crew_tree
            guestof_id = id_dict[a_guestof_c.get()]
            crewqry = add_crew(1, 0, a_guestname_e.get(), -1, guestof_id)
            crewlist = [x[1] for x in crewqry]
            crew_tree = makecrewtree(crewqry, crew_tree)


        def add_crew(event, skip, crewname, crewid, billid):
            # confirms works 7/15
            db = sqlite3.connect('Sailsheets.db')
            c = db.cursor()

            c.execute("""CREATE TABLE IF NOT EXISTS "openspcrew"(o_id real, 
                o_name text,
                o_spid int,
                o_skipper int,
                o_billtoid real
                )
                """)

            c.execute("""INSERT INTO openspcrew VALUES
                (:id, :name, :spid, :skipper, :billto) """,
                {
                'id': crewid,
                'name': crewname,
                'spid': mysp_id,
                'skipper': skip,
                'billto': billid,
                })

            db.commit()
            db.close()
            return getcrewlist(mysp_id)


        def cancelediting(new, myspid):
            # confirms works 7/16
            if new == 1:
                db = sqlite3.connect('Sailsheets.db')
                c = db.cursor()

                c.execute("DELETE FROM SailPlan WHERE sp_id='" + str(myspid) + "'")
        
                c.execute("DELETE FROM openspcrew WHERE o_spid='" + str(myspid) + "'")
        
                db.commit()
                db.close()
            sp_win.destroy()


        def select_crew(event):
            crew_del_btn.configure(state='normal')


        def del_crew():
            global crew_tree
            selected = crew_tree.focus()
            crewname = crew_tree.item(selected, 'values')[1]
            db = sqlite3.connect('Sailsheets.db')
            c = db.cursor()
            c.execute("DELETE FROM openspcrew WHERE o_name='" + crewname + "'")
            db.commit()
            db.close()
            crew_del_btn.configure(state='disabled')
            crewqry = getcrewlist(mysp_id)
            crewlist = [x[1] for x in crewqry]
            crew_tree = makecrewtree(crewqry, crew_tree)
            return 



        #########################################################
        # 
        # Main code for the add sailplan module is here
        #
        #########################################################
        #
        #populate the drop down lists from the tables
        global crewlist
        myboatlist = get_boat_list()
        mypurplist = get_purpose_list()
        mymembers = get_member_list()
        idlist = [x[0] for x in mymembers]
        memberlist = [i[1] for i in mymembers] 
        id_dict = {v: k for (k, v) in zip(idlist, memberlist)}
        name_dict = {k: v for (k, v) in zip(idlist, memberlist)}

        # create a blank record -- if the user cancels out this 
        # will get removed
        #
        if mysp_id == -1: 
            if messagebox.askokcancel(LiabilityWaiver.w_header, LiabilityWaiver.w_title) != 1:
                return
            mysp_id = newblanksailplan()
            new = 1 # this is a new record, used when canceling
        else: 
            new = 0
        
        mysailplan = get_sailplan_df(mysp_id)
        #mycrewlist = getcrewlist(mysp_id)
        crewlist = [x[1] for x in getcrewlist(mysp_id)]
        

        
        #########################################################
        # Frame for the crew list
        #
        # The crew list frame simply lists all persons on the boat.  
        #
        crew_frame = LabelFrame(sp_win, text="Crew List")

        # create the scrollbar on the right
        #
        tree_scroll = Scrollbar(crew_frame)
        tree_scroll.pack(side=RIGHT, fill=Y)

        # Create the Treeview
        #
        crew_tree = ttk.Treeview(crew_frame, yscrollcommand=tree_scroll.set, selectmode='extended')
        crew_frame.place(x=10, rely=.44)
        crew_tree.bind('<ButtonRelease-1>', select_crew)
        crew_del_btn = Button(sp_win, text='Delete Crew', state='disabled', 
            command=del_crew)
        crew_del_btn.place(relx=.6, rely=.5)

        # Configure the scrollbar
        #
        tree_scroll.config(command=crew_tree.yview)

        # Define the columns
        #
        crew_tree['columns'] = ("c_id", "c_name", "c_billto_id")

        # Pack the treeview to the screen
        #
        crew_tree.pack(side=LEFT)

        # format columns
        #
        crew_tree.column("#0", width=0, stretch=NO)
        crew_tree.column("c_id", anchor=CENTER, width=80, minwidth=40)
        crew_tree.column("c_name", anchor=W, width=200, minwidth=100)
        crew_tree.column("c_billto_id", anchor=CENTER, width=80, minwidth=50)

        # Create Headings
        #
        crew_tree.heading("#0", text="", anchor=W)
        crew_tree.heading("c_id", text="Club #", anchor=CENTER)
        crew_tree.heading("c_name", text="Name", anchor=W)
        crew_tree.heading("c_billto_id", text="Bill to:", anchor=CENTER)

        # Populate the tree & crewlist
        #
        crew_tree = makecrewtree(getcrewlist(mysp_id), crew_tree)
        
        # Record Frame for editing/adding 
        #
        sailplan_frame = LabelFrame(sp_win, text="SailPlan Record")
        sailplan_frame.place(x=10, rely=.075)

        # Labels & Entry boxes for the record
        #
        # Consider using .place instead of .grid
        #
        # Initial version for testing functionality allows full 
        # editing of all fields.  Final version will disable 
        # fields we don't want the user to modify, and will
        # disable fields to read only for all fields once the 
        # sailplan is closed.
        #
        # Top line of entries:
        #
        sp_boat_l = Label(sailplan_frame, text="Boat:")
        sp_boat_l.grid(row=0, column=0, sticky=W, padx=10)
        boat_combo = ttk.Combobox(sailplan_frame, value=myboatlist)
        boat_combo.insert(0, mysailplan[3])
        boat_combo.grid(row=1, column=0, padx=10)

        sp_skid_l = Label(sailplan_frame, text="Skipper Club # and Name:")
        sp_skid_l.grid(row=0, column=1, sticky=W, columnspan=2)
        sp_skid_e = Entry(sailplan_frame, width=10)
        sp_skid_e.insert(0, mysailplan[2])
        sp_skid_e.grid(row=1, column=1, sticky=W)
        sp_skid_e.focus()
        skip_n_combo = ttk.Combobox(sailplan_frame, value=memberlist)
        #skip_n_combo.insert()
        skip_n_combo.grid(row=1, column=2, padx=10)

        sp_purp_l = Label(sailplan_frame, text="Purpose:")
        sp_purp_l.grid(row=0, column=3, sticky=W)
        purp_combo = ttk.Combobox(sailplan_frame, value=mypurplist)
        purp_combo.insert(0, mysailplan[4])
        #purp_combo.current(8) # Rec sailing?
        purp_combo.grid(row=1, column=3)

        # Second line of entries:
        #
        sp_to_l = Label(sailplan_frame, text="Time Checked Out:")
        sp_to_l.grid(row=2, column=0, columnspan=2, sticky=W, padx=10)
        sp_to_e = Entry(sailplan_frame, width=20, justify=LEFT, state='normal')
        if new == 1:
            sp_to_e.insert(0, dt.datetime.today().isoformat(sep=' ', timespec='seconds'))
        else: sp_to_e.insert(0, mysailplan[1])
        sp_to_e.config(disabledforeground="black", readonlybackground='white')
        sp_to_e.grid(row=3, column=0, columnspan=2, sticky=W, padx=10)
        
        sp_eta_l = Label(sailplan_frame, text="Est Return Time:")
        sp_eta_l.grid(row=2, column=1, columnspan=2, sticky=W)
        sp_eta_e = Entry(sailplan_frame, width=20, justify=LEFT)
        if new == 1:
            sp_eta_e.insert(0, 
            (dt.datetime.today() + timedelta(hours=4)).isoformat(sep=' ', timespec='seconds')) 
            # add 4 hours by default
        else: sp_eta_e.insert(0, mysailplan[6])
        sp_eta_e.grid(row=3, column=1, columnspan=2, sticky=W)

        sp_ti_l = Label(sailplan_frame, text="Time Checked In:")
        sp_ti_l.grid(row=2, column=3, columnspan=2, sticky=W)
        sp_ti_e = Entry(sailplan_frame, width=20, justify=LEFT, state='normal')
        sp_ti_e.grid(row=3, column=3, columnspan=2, sticky=W)

        # Third line of entries:
        #
        sp_desc_l = Label(sailplan_frame, text="Description:")
        sp_desc_l.grid(row=4, column=0, sticky=W, padx=10, pady=5)
        sp_desc_e = Entry(sailplan_frame, justify=LEFT, width=55)
        sp_desc_e.insert(0, mysailplan[5])
        sp_desc_e.grid(row=4, column=1, columnspan=3, sticky=W)

        # Add Club Member frame and entry boxes
        #
        add_member_frame = LabelFrame(sp_win, 
            text="Add a Club Member:")
        add_member_frame.place(x=10, rely=.375, anchor=W)
        a_club_id_l = Label(add_member_frame, text="Club #:")
        a_club_id_l.grid(row=0, column=0, sticky=W, padx=10)
        a_club_id_e = Entry(add_member_frame, justify=LEFT, width=10)
        a_club_id_e.grid(row=0, column=1, stick=W)
        a_member_l = Label(add_member_frame, text="Name:")
        a_member_l.grid(row=1, column=0, sticky=W, padx=10)
        a_member_c = ttk.Combobox(add_member_frame, value=memberlist)
        a_member_c.grid(row=1, column=1, pady=5)

        # Add a Guest frame
        #
        add_guest_frame = LabelFrame(sp_win, 
            text="Add a Guest:")
        add_guest_frame.place(x=670, rely=.375, anchor=E)
        a_guestname_l = Label(add_guest_frame, text="Guest Name:")
        a_guestname_l.grid(row=0, column=0, sticky=W, padx=10)
        a_guestname_e = Entry(add_guest_frame, justify=LEFT, width=10)
        a_guestname_e.grid(row=0, column=1, stick=W)
        a_guestof_l = Label(add_guest_frame, text="Guest of:")
        a_guestof_l.grid(row=1, column=0, sticky=W, padx=10)
        a_guestof_c = ttk.Combobox(add_guest_frame, value= crewlist, 
            postcommand= lambda: a_guestof_c.configure(values=
                [x[1] for x in getcrewlist(mysp_id)]))
        a_guestof_c.grid(row=1, column=1, pady=5)

        # Buttons for commands to modify the record
        #
        button_frame = LabelFrame(sp_win, 
            text="Commands for canceling or saving the Sailplan")
        button_frame.place(x=10, rely=.98, anchor=SW)

        # This button closes the sailplan window and does nothing.
        #
        cancel_button = Button(button_frame, text="Cancel", 
            command=lambda: cancelediting(new, mysp_id))
        cancel_button.grid(row=0, column=0, padx=10, pady=10)

        # This button closes the sailplan window.
        #
        #close_sp = Button(button_frame, text="Update Plan", 
        #    state=edit_state, command=update_sailplan)
        #close_sp.grid(row=0, column=2, padx=10, pady=10)

        # This button closes the sailplan window and checks the boat in.
        #
        check_in = Button(button_frame, text="Check In", 
            state=edit_state, command=checkin_sailplan)
        check_in.grid(row=0, column=3, padx=10, pady=10)

        # This button closes the sailplan window and saves the sailplan in OPEN state,
        # checking the boat OUT. State will be disabled for an edit, normal for new.
        #
        save_btn = Button(button_frame, text="Save Sail Plan", 
            command=lambda: update_sailplan(mysp_id))
        save_btn.grid(row=0, column=5, sticky=E, padx=10, pady=10)
        #ok_btn.focus()

        # Let's put a label at the top of the window
        sp_label = Label(sp_win, text = "Sail Plans", fg="blue", font=("Helvetica", 24))
        sp_label.place(relx=.5, anchor=N)

        sp_skid_e.bind('<KeyPress-Return>', set_skipper)
        sp_skid_e.bind('<KeyPress-Tab>', set_skipper)
        a_member_c.bind('<<ComboboxSelected>>', choosecrew)
        a_guestof_c.bind('<<ComboboxSelected>>', chooseguest)
        #sp_win.bind('<ButtonRelease-1>', select_item)

        sp_win.mainloop()
        return

    #################################################################
    #
    # Remove the selected record and delete from the table
    #
    def remove_1_record():
        global my_tree
        selected = my_tree.focus()
        #print(str(int(my_tree.item(selected, 'values')[9])))
        if int(my_tree.item(selected, 'values')[9]) == 0: #sail plan is not completed
            x = my_tree.selection()[0] # x is the index, not the actual tuple
            mysp_id = my_tree.item(selected, 'values')[0]
            my_tree.delete(x)
            
            # Open the database and create a cursor
            db = sqlite3.connect('Sailsheets.db')
            c = db.cursor()
            
            # execute the update query
            c.execute("DELETE FROM SailPlan WHERE sp_id='" + str(mysp_id) + "'")
            c.execute("DELETE FROM openspcrew WHERE o_spid='" + str(mysp_id) + "'")
            
            # Commit the change and close the database
            db.commit()
            db.close()

            # now clear the entry boxes
            #clearboxes()
            # delete the tree values
            my_tree.delete(*my_tree.get_children())
            # repopulate the tree with the table's values
            q_sp_table(dt.date.fromisoformat(my_date))

            messagebox.showinfo('', "Sail Plan Deleted!")
        else:
            messagebox.showinfo('', "Sail Plan Complete, cannot delete!")
        
        return
    
    # Create binding click function
    #
    def clicker(e):
        myinfo = select_record(e)

    def datepicker():
        global my_date
        my_date = cal.get_date()
        q_sp_table(dt.date.fromisoformat(my_date))
        return 

    #################################################################
    # 
    # Sail Plan module main code here
    #
    global my_tree, my_date

    #first, clear any frames that may be on the screen
    clear_all_frames()

    # Let's put a label just under the title
    #
    my_label = Label(root, text = "Sail Plans", fg="red", font=("Helvetica", 18))
    my_label.pack(pady=5)

  
    #my_date = StringVar()
    todaysdate = dt.datetime.today()
    #thisday = todaysdate.day
    #thismonth = todaysdate.month
    #thisyear = todaysdate.year
    my_date = todaysdate.isoformat()[:10]
    #print('Main function: ' + str(my_date))

    # Add the style for the editing window
    style = ttk.Style()

    # Pick a theme
    style.theme_use("clam") # choices are default, alt, clam, vista

    # Create the frame for the calendar
    #
    cal_frame = Frame(root)
    cal_frame.pack(pady=5)

    cal = Calendar(cal_frame, firstweekday='sunday', date_pattern='yyyy-mm-dd',
        showweeknumbers=FALSE, selectmode='day')
    cal.pack(pady=5)
    
    calbtn = Button(cal_frame, text="Select Date", command=datepicker)
    calbtn.pack(pady=5)

    # Buttons for commands to modify the records
    #
    button_frame = LabelFrame(root, text="Commands for Sail Plans")
    button_frame.columnconfigure(3, weight=5)
    button_frame.pack(fill="x", padx=80)

    # -1 means this is a new sailplan number
    # 0 in the second column means it's still open
    addrecord = Button(button_frame, text="Add Sail Plan", command=lambda: add_edit_record(-1, 0))
    addrecord.grid(row=0, column=1, padx=10, pady=5)
    addrecord.focus()

    delrecord = Button(button_frame, text="Delete Sail Plan", command=remove_1_record)
    delrecord.grid(row=0, column=2, padx=10, pady=5)

    editrecord = Button(button_frame, text="Edit Sail Plan", 
        state='normal',
        command=lambda: add_edit_record(select_record(0)[0], select_record(0)[1]))
    editrecord.grid(row=0, column=3, columnspan=5, sticky=E, padx=10, pady=5)

    # This button removes all the frames and buttons and closes the db.
    #
    #alldone = Button(button_frame, text="Quit", command=root.quit)
    #alldone.grid(row=0, column=4, padx=10, pady=5)
    #alldone.focus()    

    # Create the frame for the sailplan table
    #
    my_frame = Frame(root)
    my_frame.pack(pady=10)

    # create the scrollbars on the right and bottom
    #
    y_tree_scroll = Scrollbar(my_frame)
    y_tree_scroll.pack(side=RIGHT, fill=Y)
    #x_tree_scroll = Scrollbar(my_frame)
    #x_tree_scroll.pack(side=BOTTOM, fill=Y)

    # Create the Treeview
    #
    my_tree = ttk.Treeview(my_frame, yscrollcommand=y_tree_scroll.set, selectmode='extended')


    # Configure the scrollbar
    #
    y_tree_scroll.config(command=my_tree.yview)
    
    # Define the columns
    #
    my_tree['columns'] = ("sp_id", "sp_timeout", "sp_skipper_id", "sp_skipper",
        "sp_sailboat", "sp_purpose", "sp_description", "sp_estrtntime", 
        "sp_timein", "sp_completed"
        )

    # format columns
    #
    my_tree.column("#0", width=0, stretch=NO)
    my_tree.column("sp_id", width=0, stretch=NO)
    my_tree.column("sp_timeout", anchor=CENTER, width=150, minwidth=100)
    my_tree.column("sp_skipper_id", width=0, stretch=NO)
    my_tree.column("sp_skipper", width=100, minwidth=50)
    my_tree.column("sp_sailboat", anchor=W, width=100, minwidth=75)
    my_tree.column("sp_purpose", anchor=W, width=175, minwidth=35)
    my_tree.column("sp_description", anchor=W, width=200, minwidth=35)
    my_tree.column("sp_estrtntime", anchor=CENTER, width=150, minwidth=35)
    my_tree.column("sp_timein", anchor=CENTER, width=150, minwidth=35)
    my_tree.column("sp_completed", width=0, stretch=NO)

    # Create Headings
    #
    my_tree.heading("#0", text="")
    my_tree.heading("sp_id", text="")
    my_tree.heading("sp_timeout", text="Time Out", anchor=CENTER)
    my_tree.heading("sp_skipper_id", text="")
    my_tree.heading("sp_skipper", text="Skipper", anchor=W)
    my_tree.heading("sp_sailboat", text="Boat", anchor=W)
    my_tree.heading("sp_purpose", text="Purpose", anchor=W)
    my_tree.heading("sp_description", text="Description", anchor=W)
    my_tree.heading("sp_estrtntime", text="Est Return", anchor=CENTER)
    my_tree.heading("sp_timein", text="Time In", anchor=CENTER)
    my_tree.heading("sp_completed", text="")
    
    # Now get the data from the Table
    #
    q_sp_table(dt.date.fromisoformat(my_date))

    # Pack the treeview to the screen
    #
    my_tree.pack()
    
    # Bindings
    #
    cal.bind("<ButtonRelease-1>", datepicker)
    my_tree.bind("<ButtonRelease-1>", select_record)

    return
    
#####################################################################
# Update the members table from Club Express.
#
def a_update_members():

    ###################################################################
    #
    # This function will ask the user for the location of the 
    # AllMembers.csv file that was extracted from Club Express.  
    #
    ###################################################################
    root.allmembersfile = filedialog.askopenfilename(initialdir='../NPSCTransfer',
        title='Open AllMembers.CSV file',
        filetypes=[("CSV Files", "*.csv")]
        )
    if root.allmembersfile != 'None':
        Success = updatemembers.UpdateMembers(root.allmembersfile)
    else:
        pass

#####################################################################
# Export or dump all the data to flat files.
#
def a_exportdata():
    ###################################################################
    #
    # This function simply calls the db function to dump all the tables
    # into CSV files.  Eventually this will dump the files into real
    # Excel files, so no additional conversions will be required by the
    # Treasurer. This is meant to create a backup of the data.
    #
    ###################################################################
    SS_db_functions.export_excel()
    
#####################################################################
# View and modify the Boats Table
#
def editboats():

    #################################################################
    #
    # This function is meant to allow editing of the Boats Table to
    # enable revising the details for each boat such as rental rates.
    #
    # Also allows adding or deleting a boat.
    #
    #################################################################

    #################################################################
    #
    # Functions required for editboats function, only
    #
    def queryboatstable():
        
        # Declare the global variables to be modified here
        global boat_tree

        # Clear the tree view
        for record in boat_tree.get_children():
            boat_tree.delete(record)

        # Open the db and establish a cursor
        db = sqlite3.connect('Sailsheets.db')
        c = db.cursor()

        # query to pull the data from the boats table
        c.execute("""SELECT boat_id, boat_type, boat_class, boat_name, 
            E5HourRate, E5DayRate, HourRate, DayRate, NPSCHourRate, 
            NPSCDayRate, Down, Retired FROM Boats ORDER BY boat_id
            """)

        # fetch the data
        boatlist = c.fetchall()

        # Create striped row tags
        boat_tree.tag_configure('oddrow', background='#D3D3D3') # light silver
        boat_tree.tag_configure('evenrow', background='silver') # dark silver

        count = 0
        for boat in boatlist:
            if count % 2 == 0:
                boat_tree.insert(parent='', index='end', values=boat, tags=('evenrow',))
            else:
                boat_tree.insert(parent='', index='end', values=boat, tags=('oddrow',))
            count += 1
        
        # commit and close the DB
        db.commit()
        db.close()

    #################################################################
    # 
    # Clear the entry boxes
    #
    def clearboxes():
        # Clear entry boxes
        b_id_e.delete(0, END)
        b_type_e.delete(0, END)
        b_class_e.delete(0, END)
        b_name_e.delete(0, END)
        b_E5H_e.delete(0, END)
        b_E5D_e.delete(0, END)
        b_MH_e.delete(0, END)
        b_MD_e.delete(0, END)
        b_NH_e.delete(0, END)
        b_ND_e.delete(0, END)
        b_down_e.delete(0, END)
        b_retired_e.delete(0, END)


    #################################################################
    # 
    # Add the record you just created to the db
    #
    def addboat():
        # open the database & create a cursor
        db = sqlite3.connect('Sailsheets.db')
        c = db.cursor()

        # Below is the table schema for Boats table
        """CREATE TABLE Boats (boat_id int primary key,
            boat_type text,
            boat_class text,
            boat_name text,
            QualRequired int,
            E5HourRate real,
            E5DayRate real,
            HourRate real,
            DayRate real,
            NPSCHourRate real,
            NPSCDayRate real,
            Down int,
            DownDescription text,
            Retired int);
        """

        # execute a query to insert the record
        c.execute("""INSERT INTO Boats VALUES
            (:b_id, :b_t, :b_c, :b_n, :qual, :e5h, :e5d, :h_r, :d_r, 
            :n_h, :n_d, :stored, :downdescription, :retired) """,
            {
            'b_id': b_id_e.get(),
            'b_t': b_type_e.get(),
            'b_c': b_class_e.get(),
            'b_n': b_name_e.get(),
            'qual': 'Not Used',
            'e5h': b_E5H_e.get(),
            'e5d': b_E5D_e.get(),
            'h_r': b_MH_e.get(),
            'd_r': b_MD_e.get(),
            'n_h': b_NH_e.get(),
            'n_d': b_ND_e.get(),
            'stored': b_down_e.get(),
            'downdescription': 'Transferred or sold',
            'retired': b_retired_e.get()
            })
        
        # commit the change and close the database
        db.commit()
        db.close()

        # now clear the entry boxes
        clearboxes()
        # delete the tree values
        boat_tree.delete(*boat_tree.get_children())
        # repopulate the tree with the table's values
        queryboatstable()
        return

    #################################################################
    #
    # Remove the selected record and delete from the boats table
    #
    def remove_1_boat():
        x = boat_tree.selection()[0] # x is the index, not the actual tuple
        boat_tree.delete(x)
        
        # Open the database and create a cursor
        db = sqlite3.connect('Sailsheets.db')
        c = db.cursor()
        
        # execute the update query
        c.execute("DELETE FROM Boats WHERE boat_id=" + b_id_e.get())
        
        # Commit the change and close the database
        db.commit()
        db.close()

        # now clear the entry boxes
        clearboxes()
        # delete the tree values
        boat_tree.delete(*boat_tree.get_children())
        # repopulate the tree with the table's values
        queryboatstable()

        messagebox.showinfo("Boat deleted!")
        return
    
    #################################################################
    # 
    # Delete multiple records and remove them from the boats table
    #
    # Not used in this function but may be added in future
    #
    def remove_selected_boats():
        x = boat_tree.selection()
        for record in x:
            boat_tree.delete(record)
        refreshtreeview()
        return
        
    #################################################################
    # 
    # Select the record you picked
    #
    def select_record(e):
        
        # Clear the boat record boxes
        clearboxes()
        
        # Grab the record number
        selected = boat_tree.focus()

        # Grab record values
        values = boat_tree.item(selected, 'values')

        # Output to entry boxes
        b_id_e.insert(0, values[0])
        b_type_e.insert(0, values[1])
        b_class_e.insert(0, values[2])
        b_name_e.insert(0, values[3])
        b_E5H_e.insert(0, values[4])
        b_E5D_e.insert(0, values[5])
        b_MH_e.insert(0, values[6])
        b_MD_e.insert(0, values[7])
        b_NH_e.insert(0, values[8])
        b_ND_e.insert(0, values[9])
        b_down_e.insert(0, values[10])
        b_retired_e.insert(0, values[11])


    #################################################################
    # 
    # Save updated record
    #
    def update_record():
        # Grab the record number
        selected = boat_tree.focus()

        # Save new data
        boat_tree.item(selected, text="", values=(
            b_id_e.get(),
            b_type_e.get(),
            b_class_e.get(),
            b_name_e.get(),
            b_E5H_e.get(),
            b_E5D_e.get(),
            b_MH_e.get(),
            b_MD_e.get(),
            b_NH_e.get(),
            b_ND_e.get(),
            b_down_e.get(),
            b_retired_e.get()
            ))
        # Open the database and create a cursor
        db = sqlite3.connect('Sailsheets.db')
        c = db.cursor()
        
        # execute the update query
        c.execute("""UPDATE Boats SET
            boat_type = :b_t,
            boat_class = :b_c,
            boat_name = :b_n,
            E5HourRate = :e5h,
            E5DayRate = :e5d,
            HourRate = :h_r,
            DayRate = :d_r,
            NPSCHourRate = :n_h, 
            NPSCDayRate = :n_d,
            Down = :stored,
            Retired = :retired
            WHERE boat_id= :b_id""",
            {
            'b_t': b_type_e.get(),
            'b_c': b_class_e.get(),
            'b_n': b_name_e.get(),
            'e5h': b_E5H_e.get(),
            'e5d': b_E5D_e.get(),
            'h_r': b_MH_e.get(),
            'd_r': b_MD_e.get(),
            'n_h': b_NH_e.get(),
            'n_d': b_ND_e.get(),
            'stored': b_down_e.get(),
            'retired': b_retired_e.get(),
            'b_id': b_id_e.get(),
            })
        
        # Commit the change and close the database
        db.commit()
        db.close()

        # now clear the entry boxes
        clearboxes()
        # delete the tree values
        boat_tree.delete(*boat_tree.get_children())
        # repopulate the tree with the table's values
        queryboatstable()
        return

    # Create binding click function
    #
    def clicker(e):
        select_record()

    #################################################################
    # Start the function code here
    #
    global boat_tree

    #first, clear any frames that may be on the screen
    clear_all_frames()

    # Add the style for the editing window
    style = ttk.Style()

    # Pick a theme
    style.theme_use("clam") # choices are default, alt, clam, vista
    '''
    # Hard code some colors
    style.configure("Treeview", 
        background="silver",
        foreground="black",
        rowheight=25,
        fieldbackground="silver"
        )

    # change selected color
    style.map("Treeview", 
        background=[('selected', 'blue')])
    '''

    # Let's put a label just under the title
    #
    boat_label = Label(root, text = "Boats Table Editing", fg="red", font=("Helvetica", 18))
    boat_label.pack(pady=10)

    # Create the frame for the boat table
    #
    boat_frame = Frame(root)
    boat_frame.pack(pady=10)

    # create the scrollbar on the right
    #
    tree_scroll = Scrollbar(boat_frame)
    tree_scroll.pack(side=RIGHT, fill=Y)

    # Create the Treeview
    #
    boat_tree = ttk.Treeview(boat_frame, yscrollcommand=tree_scroll.set, selectmode='extended')

    # Pack the treeview to the screen
    #
    boat_tree.pack()

    # Configure the scrollbar
    #
    tree_scroll.config(command=boat_tree.yview)

    # Define the columns
    #
    boat_tree['columns'] = ("boat_id", "boat_type", "boat_class", 
        "boat_name", "E5HourRate", "E5DayRate", "HourRate", "DayRate", 
        "NPSCHourRate", "NPSCDayRate", "Down", "Retired")

    # format columns
    #
    boat_tree.column("#0", width=0, stretch=NO)
    boat_tree.column("boat_id", anchor=CENTER, width=40, minwidth=40)
    boat_tree.column("boat_type", anchor=W, width=100, minwidth=100)
    boat_tree.column("boat_class", anchor=CENTER, width=50, minwidth=50)
    boat_tree.column("boat_name", anchor=W, width=100, minwidth=75)
    boat_tree.column("E5HourRate", anchor=E, width=50, minwidth=35)
    boat_tree.column("E5DayRate", anchor=E, width=65, minwidth=35)
    boat_tree.column("HourRate", anchor=E, width=70, minwidth=35)
    boat_tree.column("DayRate", anchor=E, width=85, minwidth=35)
    boat_tree.column("NPSCHourRate", anchor=E, width=80, minwidth=35)
    boat_tree.column("NPSCDayRate", anchor=E, width=90, minwidth=35)
    boat_tree.column("Down", anchor=CENTER, width=50, minwidth=50)
    boat_tree.column("Retired", anchor=CENTER, width=50, minwidth=50)
    
    # Create Headings
    #
    boat_tree.heading("#0", text="", anchor=W)
    boat_tree.heading("boat_id", text="ID", anchor=CENTER)
    boat_tree.heading("boat_type", text="Boat Type", anchor=W)
    boat_tree.heading("boat_class", text="Class", anchor=CENTER)
    boat_tree.heading("boat_name", text = "Boat Name", anchor=W)
    boat_tree.heading("E5HourRate", text="E5 Hr", anchor=E)
    boat_tree.heading("E5DayRate", text="E5 Day", anchor=E)
    boat_tree.heading("HourRate", text="MWR Hr", anchor=E)
    boat_tree.heading("DayRate", text="MWR Day", anchor=E)
    boat_tree.heading("NPSCHourRate", text="NPSC Hr", anchor=E)
    boat_tree.heading("NPSCDayRate", text="NPSC Day", anchor=E)
    boat_tree.heading("Down", text="Dwn?", anchor=CENTER)
    boat_tree.heading("Retired", text="Ret?", anchor=CENTER)
    
    # Now get the data from the Boats Table
    #
    queryboatstable()

    # Record Frame for editing/adding boats
    #
    record_frame = LabelFrame(root, text="Boat Record")
    record_frame.pack(fill="x", expand="yes", padx=20)

    # Labels
    #
    b_id_l = Label(record_frame, text="ID")
    b_id_l.grid(row=0, column=0, padx=10, pady=5)
    b_id_e = Entry(record_frame)
    b_id_e.grid(row=0, column=1, padx=10, pady=5)
    
    b_down_l = Label(record_frame, text="Storage 0=N 1=Y")
    b_down_l.grid(row=0, column=2, padx=10, pady=5)
    b_down_e = Entry(record_frame)
    b_down_e.grid(row=0, column=3, padx=10, pady=5)

    b_retired_l = Label(record_frame, text="Gone 0=N 1=Y")
    b_retired_l.grid(row=0, column=4, padx=10, pady=5)
    b_retired_e = Entry(record_frame)
    b_retired_e.grid(row=0, column=5, padx=10, pady=5)

    b_type_l = Label(record_frame, text="Type")
    b_type_l.grid(row=2, column=0, padx=10, pady=5)
    b_type_e = Entry(record_frame)
    b_type_e.grid(row=2, column=1, padx=10, pady=5)
    
    b_class_l = Label(record_frame, text="Class")
    b_class_l.grid(row=3, column=0, padx=10, pady=5)
    b_class_e = Entry(record_frame)
    b_class_e.grid(row=3, column=1, padx=10, pady=5)
    
    b_name_l = Label(record_frame, text="Name")
    b_name_l.grid(row=4, column=0, padx=10, pady=5)
    b_name_e = Entry(record_frame)
    b_name_e.grid(row=4, column=1, padx=10, pady=5)
    
    b_E5H_l = Label(record_frame, text="E5 Hourly Rate")
    b_E5H_l.grid(row=2, column=2, padx=10, pady=5)
    b_E5H_e = Entry(record_frame)
    b_E5H_e.grid(row=2, column=3, padx=10, pady=5)
    
    b_E5D_l = Label(record_frame, text="E5 Daily Rate")
    b_E5D_l.grid(row=2, column=4, padx=10, pady=5)
    b_E5D_e = Entry(record_frame)
    b_E5D_e.grid(row=2, column=5, padx=10, pady=5)
    
    b_MH_l = Label(record_frame, text="MWR Hourly Rate")
    b_MH_l.grid(row=3, column=2, padx=10, pady=5)
    b_MH_e = Entry(record_frame)
    b_MH_e.grid(row=3, column=3, padx=10, pady=5)
    
    b_MD_l = Label(record_frame, text="MWR Daily Rate")
    b_MD_l.grid(row=3, column=4, padx=10, pady=5)
    b_MD_e = Entry(record_frame)
    b_MD_e.grid(row=3, column=5, padx=10, pady=5)
    
    b_NH_l = Label(record_frame, text="NPSC Hourly Rate")
    b_NH_l.grid(row=4, column=2, padx=10, pady=5)
    b_NH_e = Entry(record_frame)
    b_NH_e.grid(row=4, column=3, padx=10, pady=5)
    
    b_ND_l = Label(record_frame, text="NPSC Daily Rate")
    b_ND_l.grid(row=4, column=4, padx=10, pady=5)
    b_ND_e = Entry(record_frame)
    b_ND_e.grid(row=4, column=5, padx=10, pady=5)

    # Buttons for commands to modify the records
    #
    button_frame = LabelFrame(root, text="Commands for editing the record")
    button_frame.pack(fill="x", expand="yes", padx=20)

    clear_button = Button(button_frame, text="Clear Entries", command=clearboxes)
    clear_button.grid(row=0, column=0, padx=10, pady=10)

    addrecord = Button(button_frame, text="Add New Boat", command=addboat)
    addrecord.grid(row=0, column=1, padx=10, pady=10)

    editrecord = Button(button_frame, text="Update Selected Boat", command=update_record)
    editrecord.grid(row=0, column=2, padx=10, pady=10)

    removerecord = Button(button_frame, text="Remove Selected Boat", command=remove_1_boat)
    removerecord.grid(row=0, column=3, padx=10, pady=10)

    # This button removes all the frames and buttons and closes the db.
    #
    alldone = Button(button_frame, text="All done", command=clear_all_frames)
    alldone.grid(row=0, column=5, padx=10, pady=10)
    alldone.focus()

    # Bindings
    #
    boat_tree.bind("<ButtonRelease-1>", select_record)
    
    return

#####################################################################
# Modify the Settings table
#
def editsettings():
    #################################################################
    #
    # This function is meant to allow editing of the settings for the 
    # App.
    #
    # There are only 2 settings:
    # 1. Club discount percentage (10%)
    # 3. Grace period for boat rental, in case the boat is down (30 mins)
    #
    # Note: the admin password has been removed as it was not secure.
    #
    #################################################################
    
    def makechange(mydiscount, mygrace):
        new_discount = int(discount_box.get())
        new_grace = int(grace_box.get())
        
        if (mydiscount != new_discount or mygrace != new_grace):
            db = sqlite3.connect('Sailsheets.db')
            c = db.cursor()
            c.execute("DROP TABLE Settings")
            c.execute("CREATE TABLE if not exists Settings (discount int, delay int)")
            c.execute("INSERT OR REPLACE INTO Settings(discount, delay) VALUES (?, ?)", 
                (new_discount, new_grace))
            db.commit()
            db.close()
            settings_frame.destroy()
        else:
            settings_frame.destroy()
            return

    #first, clear any frames that may be on the screen
    for stuff in root.winfo_children():
        if str(stuff) != ".!menu" and str(stuff) != ".!label":
            stuff.destroy()

    # get the data from the table
    #
    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()
    c.execute("SELECT * FROM Settings")
    setlist = c.fetchone()
    db.close()

    mydiscount = setlist[0]
    #mypw = setlist[1]
    mygrace = setlist[1]

    # create the frame
    #
    settings_frame = Frame(root)
    settings_frame.pack(pady=20)

    # add labels
    discount = Label(settings_frame, text="Club Discount")
    discount.grid(row=0, column=0)

    grace = Label(settings_frame, text="Grace period (minutes)")
    grace.grid(row=0, column=2)

    # Entry boxes
    discount_box = Entry(settings_frame, width=5, justify=CENTER)
    discount_box.insert(0, mydiscount)
    discount_box.grid(row=1, column=0)

    grace_box = Entry(settings_frame, width=5, justify=CENTER)
    grace_box.insert(0, mygrace)
    grace_box.grid(row=1, column=2)

    # Buttons
    change_settings = Button(settings_frame, text="Ok", 
        command=lambda: makechange(mydiscount, mygrace))
    change_settings.grid(row=4, column=1, pady=10)

    return

#####################################################################
# Monthly reports
#
def monthly_reports():

    #################################################################
    #
    # This function creates 3 Excel Files from the DB tables for a
    # month and year (default is previous month):
    #
    # 1. Member usage report for creating bills in Club Express
    # 2. Boat usage report WITH Skyline -- NPSC Use only
    # 3. Boat usage report WITHOUT Skyline -- for MWR Use
    # 
    #################################################################

    global mymonth, myyear, thisyear, todaysdate

    def select():
        mymonth = month_list.index(mo_combo.get()) + 1
        myyear = thisyear - years_list.index(yr_combo.get())

        Report1 = SS_reports.ReportUsage(mymonth, myyear, 1)
        Report2 = SS_reports.ReportUsage(mymonth, myyear, 0)
        Report3 = SS_reports.ReportMemberUse(mymonth, myyear)

        mo_combo.pack_forget()
        yr_combo.pack_forget()
        accept_btn.pack_forget()

    #first, clear any frames that may be on the screen
    clear_all_frames()

    # then create a combo box
    month_list = ['January', 'February', 'March',
        'April', 'May', 'June', 
        'July', 'August', 'September',
        'October', 'November', 'December']
    todaysdate = dt.datetime.today()
    thismonth = todaysdate.month
    thisyear = todaysdate.year
    years_list = [str(thisyear), str(thisyear-1), str(thisyear-2), str(thisyear-3)]
    mo_combo = ttk.Combobox(root, value=month_list)
    mo_combo.current(thismonth-1)
    mo_combo.pack(pady=10)
    yr_combo = ttk.Combobox(root, value=years_list)
    yr_combo.current(0)
    yr_combo.pack(pady=10)

    accept_btn = Button(root, text="Select", command=select)
    accept_btn.pack(pady=10)

    return

def e_members():
    for stuff in root.winfo_children():
        if str(stuff) != ".!menu" and str(stuff) != ".!label":
            stuff.destroy()
    editmembers.editmembers(root)

#####################################################################
#
# Main code starts here
#
# Deterime if the user is NPSC_Admin or NPSC_Sailor.
# 
# if the user is NPSC_Admin then all the menus are enabled.  
# Otherwise the menus are disabled and the only function is the
# Sail Plan creation (check out and check in).
#
my_user = pwd.getpwuid(os.getuid()).pw_name
#my_user = 'NPSC_Sailor' # used for testing
my_user = 'npscadmin' # used for testing

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
file_menu = Menu(my_menu)
my_menu.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Exit", command=root.quit)

admin_menu = Menu(my_menu)
my_menu.add_cascade(label="Admin", menu=admin_menu, state=admin_state)
admin_menu.add_command(label="Update Membership", command=a_update_members)
admin_menu.add_command(label="Backup ALL to Excel", command=a_exportdata)

edit_menu = Menu(my_menu)
my_menu.add_cascade(label="Edit", menu=edit_menu, state=admin_state)
edit_menu.add_command(label="Boats", command=editboats)
edit_menu.add_command(label="Sail Plan Purpose", 
    command=lambda: editpurpose.editpurpose(root))
edit_menu.add_command(label="Member Data", 
    command=lambda: editmembers.editmembers(root))
edit_menu.add_command(label="Settings", command=editsettings)
edit_menu.add_separator()
edit_menu.add_command(label="Sail Plans", command=sailplanmenu)
edit_menu.add_command(label="Ledger Table (raw)", 
    command=lambda: editledger.e_ledger(root))

reports_menu = Menu(my_menu)
my_menu.add_cascade(label="Reports", menu=reports_menu, state=admin_state)
reports_menu.add_command(label="Create Monthly Reports", command=monthly_reports)

# Let's put a label at the top of the window
my_label = Label(root, text = main_banner, fg=main_color, font=("Helvetica", 24))
my_label.pack()

if my_user != 'npscadmin':
    sailplanmenu()

root.mainloop()



#
#
# End of application.
###########################################################