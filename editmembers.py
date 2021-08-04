#####################################################################
#
# Edit the members table
#
from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import logging
import sqlite3

# Set up the logging system
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(__name__ + '.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def editmembers(mywindow):
    #################################################################
    #
    # This function is meant to allow editing of the Members Table 
    # to enable revising the list of Members.  This is NOT meant to be
    # the primary method of updating the membership table, but simply
    # a means of making revisions to a few records.  Examples would be:
    # - Adding a new member who wants to rent a boat.
    # - Correcting an expiration date when someone re-ups late.
    # 
    #
    #################################################################

    #################################################################
    #
    # Functions required for edit members function, only
    #
    def querymembertable():
        """
        CREATE TABLE IF NOT EXISTS "Members"(m_id int, 
        m_name text,
        m_status text,
        m_expdate text,
        m_type text,
        m_prime text);
        """

        # Declare the global variables to be modified here
        global member_tree

        # Clear the tree view
        for record in member_tree.get_children():
            member_tree.delete(record)

        # Open the db and establish a cursor
        db = sqlite3.connect('Sailsheets.db')
        c = db.cursor()

        # query to pull the data from the boats table
        c.execute("""SELECT m_id, m_name, m_status, m_expdate, m_type, m_prime 
            FROM Members ORDER BY m_id
            """)

        # fetch the data
        memberlist = c.fetchall()

        # Create striped row tags
        member_tree.tag_configure('oddrow', background='#D3D3D3') # light silver
        member_tree.tag_configure('evenrow', background='silver') # dark silver

        count = 0
        for member in memberlist:
            if count % 2 == 0:
                member_tree.insert(parent='', index='end', values=member, tags=('evenrow',))
            else:
                member_tree.insert(parent='', index='end', values=member, tags=('oddrow',))
            count += 1
        
        # commit and close the DB
        db.commit()
        db.close()
        logger.info('Updated the member tree.')
        return

    #################################################################
    # 
    # Clear the entry boxes
    #
    def clearboxes():
        # Clear entry boxes
        m_id_e.delete(0, END)
        m_name_e.delete(0, END)
        m_status_e.delete(0, END)
        m_expdate_e.delete(0, END)
        m_type_e.delete(0, END)
        m_prime_e.delete(0, END)
        

    #################################################################
    # 
    # Add the record you just created to the db
    #
    def add_record():
        # open the database & create a cursor
        db = sqlite3.connect('Sailsheets.db')
        c = db.cursor()

        # Below is the table schema for the table
        """CREATE TABLE IF NOT EXISTS "Members"(m_id int, 
            m_name text,
            m_status text,
            m_expdate text,
            m_type text,
            m_prime text);
        """

        # execute a query to insert the record
        c.execute("""INSERT INTO Members VALUES
            (:m_id, :m_name, :m_status, :m_expdate, :m_type, :m_prime) """,
            {
            'm_id': m_id_e.get(),
            'm_name': m_name_e.get(),
            'm_status': m_status_e.get(),
            'm_expdate': m_expdate_e.get(),
            'm_type': m_type_e.get(),
            'm_prime': m_prime_e.get(),
            })
        
        # commit the change and close the database
        db.commit()
        db.close()
        logger.info('Added a member to the table.')

        # now clear the entry boxes
        clearboxes()
        # delete the tree values
        member_tree.delete(*member_tree.get_children())
        # repopulate the tree with the table's values
        querymembertable()
        return

    #################################################################
    # 
    # Select the record you picked
    #
    def select_record(e):
        
        # Clear the boat record boxes
        clearboxes()
        
        # Grab the record number
        selected = member_tree.focus()

        # Grab record values
        values = member_tree.item(selected, 'values')

        # Output to entry boxes
        m_id_e.insert(0, values[0])
        m_name_e.insert(0, values[1])
        m_status_e.insert(0, values[2])
        m_expdate_e.insert(0, values[3])
        m_type_e.insert(0, values[4])
        m_prime_e.insert(0, values[5])
        

    #################################################################
    # 
    # Save updated record
    #
    def update_record():
        # Grab the record number
        selected = member_tree.focus()

        # Save new data
        member_tree.item(selected, text="", values=(
            m_id_e.get(),
            m_name_e.get(),
            m_status_e.get(),
            m_expdate_e.get(),
            m_type_e.get(),
            m_prime_e.get(),
            ))
        # Open the database and create a cursor
        db = sqlite3.connect('Sailsheets.db')
        c = db.cursor()
        
        # execute the update query
        c.execute("""UPDATE Members SET
            m_name = :mname,
            m_status = :mstatus,
            m_expdate = :mexp,
            m_type = :mtype,
            m_prime = :mprime
            WHERE m_id= :mid""",
            {
            'mname': m_name_e.get(),
            'mstatus': m_status_e.get(),
            'mexp': m_expdate_e.get(),
            'mtype': m_type_e.get(),
            'mprime': m_prime_e.get(),
            'mid': m_id_e.get(),
            })
        
        # Commit the change and close the database
        db.commit()
        db.close()
        logger.info('Updated a member record.')

        # now clear the entry boxes
        clearboxes()
        # delete the tree values
        member_tree.delete(*member_tree.get_children())
        # repopulate the tree with the table's values
        querymembertable()
        return

    # Create binding click function
    #
    def clicker(e):
        select_record()


    def clear_all_frames():
        for stuff in mywindow.winfo_children():
            if str(stuff) != ".!menu" and str(stuff) != ".!label":
                stuff.destroy()


    #################################################################
    # Start the function code here
    #
    logger.info('Entered the editmembers module.')

    global member_tree

    # Add the style for the editing window
    style = ttk.Style()

    # Pick a theme
    style.theme_use("clam") # choices are default, alt, clam, vista

    # Ensure the window is clear
    #
    clear_all_frames()

    # Let's put a label just under the title
    #
    member_label = Label(mywindow, text = "Members Table Editing", fg="red", font=("Helvetica", 18))
    member_label.pack(pady=10)

    # Create the frame for the boat table
    #
    member_frame = Frame(mywindow)
    member_frame.pack(pady=10)

    # create the scrollbar on the right
    #
    tree_scroll = Scrollbar(member_frame)
    tree_scroll.pack(side=RIGHT, fill=Y)

    # Create the Treeview
    #
    member_tree = ttk.Treeview(member_frame, yscrollcommand=tree_scroll.set, selectmode='extended')

    # Pack the treeview to the screen
    #
    member_tree.pack()

    # Configure the scrollbar
    #
    tree_scroll.config(command=member_tree.yview)

    # Define the columns
    #
    member_tree['columns'] = ("m_id", "m_name", "m_status", 
        "m_expdate", "m_type", "m_prime")

    # format columns
    #
    member_tree.column("#0", width=0, stretch=NO)
    member_tree.column("m_id", anchor=CENTER, width=80, minwidth=40)
    member_tree.column("m_name", anchor=W, width=200, minwidth=100)
    member_tree.column("m_status", anchor=CENTER, width=80, minwidth=50)
    member_tree.column("m_expdate", anchor=CENTER, width=100, minwidth=75)
    member_tree.column("m_type", anchor=W, width=175, minwidth=35)
    member_tree.column("m_prime", anchor=CENTER, width=80, minwidth=35)
    
    # Create Headings
    #
    member_tree.heading("#0", text="", anchor=W)
    member_tree.heading("m_id", text="ID", anchor=CENTER)
    member_tree.heading("m_name", text="Name", anchor=W)
    member_tree.heading("m_status", text="Status", anchor=CENTER)
    member_tree.heading("m_expdate", text = "Exp Date", anchor=CENTER)
    member_tree.heading("m_type", text = "Type", anchor=W)
    member_tree.heading("m_prime", text="Primary?", anchor=CENTER)
    
    # Now get the data from the Boats Table
    #
    querymembertable()

    # Record Frame for editing/adding boats
    #
    record_frame = LabelFrame(mywindow, text="Membership Record")
    record_frame.pack(fill="x", expand="yes", padx=20)

    # Labels
    #
    m_id_l = Label(record_frame, text="ID")
    m_id_l.grid(row=0, column=0, padx=10, pady=5)
    m_id_e = Entry(record_frame)
    m_id_e.grid(row=0, column=1, padx=10, pady=5)
    
    m_name_l = Label(record_frame, text="Name (Ln, Fn)")
    m_name_l.grid(row=0, column=2, padx=10, pady=5)
    m_name_e = Entry(record_frame)
    m_name_e.grid(row=0, column=3, padx=10, pady=5)

    m_status_l = Label(record_frame, text="Status")
    m_status_l.grid(row=0, column=4, padx=10, pady=5)
    m_status_e = Entry(record_frame)
    m_status_e.grid(row=0, column=5, padx=10, pady=5)

    m_expdate_l = Label(record_frame, text="Exp Date")
    m_expdate_l.grid(row=2, column=0, padx=10, pady=5)
    m_expdate_e = Entry(record_frame)
    m_expdate_e.grid(row=2, column=1, padx=10, pady=5)
    
    m_type_l = Label(record_frame, text="Member Type")
    m_type_l.grid(row=3, column=0, padx=10, pady=5)
    m_type_e = Entry(record_frame)
    m_type_e.grid(row=3, column=1, padx=10, pady=5)
    
    m_prime_l = Label(record_frame, text="Primary?")
    m_prime_l.grid(row=4, column=0, padx=10, pady=5)
    m_prime_e = Entry(record_frame)
    m_prime_e.grid(row=4, column=1, padx=10, pady=5)
    
    # Buttons for commands to modify the records
    #
    button_frame = LabelFrame(mywindow, text="Commands for editing the record")
    button_frame.pack(fill="x", expand="yes", padx=20)

    clear_button = Button(button_frame, text="Clear Entries", command=clearboxes)
    clear_button.grid(row=0, column=0, padx=10, pady=10)

    addrecord = Button(button_frame, text="Add New Member", command=add_record)
    addrecord.grid(row=0, column=1, padx=10, pady=10)

    editrecord = Button(button_frame, text="Update Selected Member", command=update_record)
    editrecord.grid(row=0, column=2, padx=10, pady=10)

    # This button removes all the frames and buttons and closes the db.
    #
    alldone = Button(button_frame, text="All done", command=clear_all_frames)
    alldone.grid(row=0, column=5, padx=10, pady=10)
    alldone.focus()

    # Bindings
    #
    member_tree.bind("<ButtonRelease-1>", select_record)
    
    return
