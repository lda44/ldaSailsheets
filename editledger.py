#####################################################################
#
# Edit the Ledger Table.  This is meant for correcting errors only, 
# post completion of a sailplan and its posting to the ledger file.
#
# this should be used very rarely.
#
import sqlite3
from tkinter import *

def e_ledger(root):
    #################################################################
    #
    # This function is meant to allow editing of the Ledger Table 
    # to enable revising some details such as billing for members.
    #
    # This is NOT meant for wide usage 
    #
    #################################################################

	def clear_all_frames():
	    for stuff in root.winfo_children():
	        if str(stuff) != ".!menu" and str(stuff) != ".!label":
	            stuff.destroy()

    #################################################################
    #
    # Functions required for edit function, only
    #
	def querytable():

		# Declare the global variables to be modified here
		global my_tree

		# Clear the tree view
		for record in my_tree.get_children():
			my_tree.delete(record)

		# Open the db and establish a cursor
		db = sqlite3.connect('Sailsheets.db')
		c = db.cursor()

		# query to pull the data from the table
		c.execute("""SELECT ledger_id,
			l_date,
			l_member_id,
			l_name, 
			l_skipper,
			l_description,
			l_billto_id,
			l_fee,
			l_account,
			l_sp_id
			FROM Ledger ORDER BY ledger_id
			""")

		# fetch the data
		mylist = c.fetchall()

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
		l_id_e.delete(0, END)
		l_date_e.delete(0, END)
		l_mid_e.delete(0, END)
		l_name_e.delete(0, END)
		l_skip_e.delete(0, END)
		l_desc_e.delete(0, END)
		#l_mvol_e.delete(0, END)
		#l_cvol_e.delete(0, END)
		l_billto_e.delete(0, END)
		l_fee_e.delete(0, END)
		l_acct_e.delete(0, END)
		l_spid_e.delete(0, END)
		return

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
	    
		# Clear the boat record boxes
		clearboxes()

		# Grab the record number
		selected = my_tree.focus()

		# Grab record values
		values = my_tree.item(selected, 'values')

		# Output to entry boxes
		l_id_e.insert(0, values[0])
		l_date_e.insert(0, values[1])
		l_mid_e.insert(0, values[2])
		l_name_e.insert(0, values[3])
		l_skip_e.insert(0, values[4])
		l_desc_e.insert(0, values[5])
		l_billto_e.insert(0, values[6])
		l_fee_e.insert(0, values[7])
		l_acct_e.insert(0, values[8])
		l_spid_e.insert(0, values[9])
		return
	    
	#################################################################
	# 
	# Save updated record
	#
	def update_record():
		global my_tree

		# Grab the record number
		selected = my_tree.focus()

		# Save new data
		my_tree.item(selected, text="", values=(
			l_id_e.get(),
			l_date_e.get(),
			l_mid_e.get(),
			l_name_e.get(),
			l_skip_e.get(),
			l_desc_e.get(),
			l_billto_e.get(),
			l_fee_e.get(),
			l_acct_e.get(),
			l_spid_e.get(),
			))

		# Open the database and create a cursor
		db = sqlite3.connect('Sailsheets.db')
		c = db.cursor()

		# execute the update query
		c.execute("""UPDATE Ledger SET
			ledger_id = :lid,
			l_date = :ldate,
			l_member_id = :lmemid,
			l_name = :lname, 
			l_skipper = :lskip,
			l_description = :ldesc,
			l_billto_id = :lbillid,
			l_fee = :lfee,
			l_account = :lacct,
			l_sp_id = :lspid
			WHERE ledger_id= :lid""",
			{
			'lid': l_id_e.get(),
			'ldate': l_date_e.get(),
			'lmemid': l_mid_e.get(),
			'lname': l_name_e.get(),
			'lskip': l_skip_e.get(),
			'ldesc': l_desc_e.get(),
			'lbillid': l_billto_e.get(),
			'lfee': l_fee_e.get(),
			'lacct': l_acct_e.get(),
			'lspid': l_spid_e.get(),
			})

		# Commit the change and close the database
		db.commit()
		db.close()

		# now clear the entry boxes
		clearboxes()
		# delete the tree values
		my_tree.delete(*my_tree.get_children())
		# repopulate the tree with the table's values
		querytable()
		return

	# Create binding click function
	#
	def clicker(e):
		select_record()

	#################################################################
	# Start the function code here
	#
	global my_tree

	#first, clear any frames that may be on the screen
	clear_all_frames()

	# Add the style for the editing window
	style = ttk.Style()

	# Pick a theme
	style.theme_use("clam") # choices are default, alt, clam, vista

	# Let's put a label just under the title
	#
	my_label = Label(root, text = "Ledger Table Editing", fg="red", font=("Helvetica", 18))
	my_label.pack(pady=10)

	# Create the frame for the boat table
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

	# Pack the treeview to the screen
	#
	my_tree.pack()

	# Configure the scrollbar
	#
	y_tree_scroll.config(command=my_tree.yview)
	#x_tree_scroll.config(command=my_tree.xview)

	# Define the columns
	#
	my_tree['columns'] = ("l_id", "l_date", "l_member_id", "l_name",
		"l_skipper", "l_desc", "l_billto",
		"l_fee", "l_acct", "l_spid"
		)

	# format columns
	#
	my_tree.column("#0", width=0, stretch=NO)
	my_tree.column("l_id", anchor=CENTER, width=40, minwidth=20)
	my_tree.column("l_date", anchor=CENTER, width=100, minwidth=40)
	my_tree.column("l_member_id", anchor=CENTER, width=85, minwidth=50)
	my_tree.column("l_name", anchor=W, width=125, minwidth=75)
	my_tree.column("l_skipper", anchor=CENTER, width=80, minwidth=35)
	my_tree.column("l_desc", anchor=W, width=150, minwidth=35)
	#my_tree.column("l_mvol", anchor=CENTER, width=40, minwidth=15)
	#my_tree.column("l_cvol", anchor=CENTER, width=40, minwidth=15)
	my_tree.column("l_billto", anchor=CENTER, width=80, minwidth=35)
	my_tree.column("l_fee", anchor=E, width=60, minwidth=35)
	my_tree.column("l_acct", anchor=W, width=125, minwidth=35)
	my_tree.column("l_spid", anchor=CENTER, width=80, minwidth=35)
	#my_tree.column("l_uploaddate", anchor=CENTER, width=100, minwidth=40)

	# Create Headings
	#
	my_tree.heading("#0", text="")
	my_tree.heading("l_id", text="ID", anchor=CENTER)
	my_tree.heading("l_date", text="Sail Date", anchor=CENTER)
	my_tree.heading("l_member_id", text="Member#", anchor=CENTER)
	my_tree.heading("l_name", text="Name", anchor=W)
	my_tree.heading("l_skipper", text="Skipper?", anchor=CENTER)
	my_tree.heading("l_desc", text="Description", anchor=W)
	#my_tree.heading("l_mvol", text="MVol?", anchor=CENTER)
	#my_tree.heading("l_cvol", text="CVol?", anchor=CENTER)
	my_tree.heading("l_billto", text="Bill to ID", anchor=CENTER)
	my_tree.heading("l_fee", text="Fee", anchor=E)
	my_tree.heading("l_acct", text="Account", anchor=W)
	my_tree.heading("l_spid", text="Sail Plan#", anchor=CENTER)
	#my_tree.heading("l_uploaddate", text="Upload Date", anchor=CENTER)

	    # Now get the data from the Table
	#
	querytable()

	# Record Frame for editing/adding 
	#
	record_frame = LabelFrame(root, text="Ledger Record")
	#record_frame.columnconfigure(index=3, weight=2)
	record_frame.pack(fill="x", expand="yes", padx=20)

	# Labels & Entry boxes for the record
	#
	l_id_l = Label(record_frame, text="Ledger ID")
	l_id_l.grid(row=0, column=0, padx=5, pady=5)
	l_id_e = Entry(record_frame, width=6, justify=CENTER)
	l_id_e.grid(row=0, column=1, padx=5, pady=5)

	l_date_l = Label(record_frame, text="Sail Date")
	l_date_l.grid(row=0, column=4, padx=5, pady=5)
	l_date_e = Entry(record_frame, width=10, justify=CENTER)
	l_date_e.grid(row=0, column=5, padx=5, pady=5)

	l_mid_l = Label(record_frame, text="Member ID")
	l_mid_l.grid(row=1, column=0, padx=5, pady=5)
	l_mid_e = Entry(record_frame, width=6, justify=CENTER)
	l_mid_e.grid(row=1, column=1, padx=5, pady=5)

	l_name_l = Label(record_frame, text="Member Name")
	l_name_l.grid(row=1, column=2, padx=5, pady=5)
	l_name_e = Entry(record_frame, width=30, justify=LEFT)
	l_name_e.grid(row=1, column=3, padx=5, pady=5)

	l_skip_l = Label(record_frame, text="Skipper?")
	l_skip_l.grid(row=2, column=0, padx=5, pady=5)
	l_skip_e = Entry(record_frame, width=6, justify=CENTER)
	l_skip_e.grid(row=2, column=1, padx=5, pady=5)

	l_spid_l = Label(record_frame, text="SailPlan ID")
	l_spid_l.grid(row=3, column=0, padx=5, pady=5)
	l_spid_e = Entry(record_frame, width=6, justify=CENTER)
	l_spid_e.grid(row=3, column=1, padx=5, pady=5)

	l_billto_l = Label(record_frame, text="Bill to ID")
	l_billto_l.grid(row=4, column=0, padx=5, pady=5)
	l_billto_e = Entry(record_frame, width=6, justify=CENTER)
	l_billto_e.grid(row=4, column=1, padx=5, pady=5)

	l_desc_l = Label(record_frame, text="Description")
	l_desc_l.grid(row=2, column=2, padx=5, pady=5)
	l_desc_e = Entry(record_frame, width=30, justify=LEFT)
	l_desc_e.grid(row=2, column=3, padx=5, pady=5)

	l_acct_l = Label(record_frame, text="Account")
	l_acct_l.grid(row=3, column=2, padx=5, pady=5)
	l_acct_e = Entry(record_frame, width=30, justify=LEFT)
	l_acct_e.grid(row=3, column=3, padx=5, pady=5)

	#l_mvol_l = Label(record_frame, text="MWR Vol?")
	#l_mvol_l.grid(row=3, column=0, padx=5, pady=5)
	#l_mvol_e = Entry(record_frame, width=6, justify=CENTER)
	#l_mvol_e.grid(row=3, column=1, padx=5, pady=5, ipadx=5)

	#l_cvol_l = Label(record_frame, text="Club Vol?")
	#l_cvol_l.grid(row=4, column=0, padx=5, pady=5)
	#l_cvol_e = Entry(record_frame, width=6, justify=CENTER)
	#l_cvol_e.grid(row=4, column=1, padx=5, pady=5)

	#l_upload_l = Label(record_frame, text="Upload Date")
	#l_upload_l.grid(row=2, column=4, padx=5, pady=5)
	#l_upload_e = Entry(record_frame, width=10, justify=CENTER)
	#l_upload_e.grid(row=2, column=5, padx=5, pady=5)

	l_fee_l = Label(record_frame, text="Fee")
	l_fee_l.grid(row=4, column=4, padx=5, pady=5)
	l_fee_e = Entry(record_frame, width=6, justify=RIGHT)
	l_fee_e.grid(row=4, column=5, padx=5, pady=5)


	# Buttons for commands to modify the records
	#
	button_frame = LabelFrame(root, text="Commands for editing the record")
	button_frame.pack(fill="x", expand="yes", padx=20)

	clear_button = Button(button_frame, text="Clear Entries", command=clearboxes)
	clear_button.grid(row=0, column=0, padx=10, pady=10)

	#addrecord = Button(button_frame, text="Add New Record", command=add_record)
	#addrecord.grid(row=0, column=1, padx=10, pady=10)

	editrecord = Button(button_frame, text="Update Selected Record", command=update_record)
	editrecord.grid(row=0, column=2, padx=10, pady=10)

	# This button removes all the frames and buttons and closes the db.
	#
	alldone = Button(button_frame, text="All done", command=clear_all_frames)
	alldone.grid(row=0, column=5, padx=10, pady=10)
	alldone.focus()

	# Bindings
	#
	my_tree.bind("<ButtonRelease-1>", select_record)

	return

