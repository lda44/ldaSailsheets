from tkinter import *
import sqlite3

#####################################################################
# View and modify the Sail Plan Purpose Table
#
def editpurpose(mywin):
	#################################################################
	#
	# This function is meant to allow editing of the Sail Plan 
	# Purpose table.
	#
	# Also allows adding or deleting a purpose.
	#
	#################################################################

	#################################################################
	#
	# Functions required for editpurpose function, only
	#

	#################################################################
	# Common functions are here
	#
	def clear_all_frames():
		for stuff in mywin.winfo_children():
			if str(stuff) != ".!menu" and str(stuff) != ".!label":
				stuff.destroy()

	def fill_tree_from_purpose_table():
		global purpose_tree
		# Clear the tree view
		for record in purpose_tree.get_children():
			purpose_tree.delete(record)

		# Open the db and establish a cursor
		db = sqlite3.connect('Sailsheets.db')
		c = db.cursor()

		# query to pull the data from the boats table
		c.execute("""SELECT p_id, p_name, p_fee, p_type, p_ratetype, 
			p_account, p_clubops FROM Purpose ORDER BY p_name""")

		# fetch the data
		purposelist = c.fetchall()

		# Create striped row tags
		purpose_tree.tag_configure('oddrow', background='#D3D3D3') # light silver
		purpose_tree.tag_configure('evenrow', background='silver') # dark silver

		count = 0
		for purpose in purposelist:
			if count % 2 == 0:
				purpose_tree.insert(parent='', index='end', values=purpose, tags=('evenrow',))
			else:
				purpose_tree.insert(parent='', index='end', values=purpose, tags=('oddrow',))
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
		p_id_e.delete(0, END)
		p_name_e.delete(0, END)
		p_fee_e.delete(0, END)
		p_type_e.delete(0, END)
		p_ratetype_e.delete(0, END)
		p_account_e.delete(0, END)
		p_clubops_e.delete(0, END)
		return

	#################################################################
	# 
	# Add the record you just created to the db
	#
	def addpurpose():
		# open the database & create a cursor
		db = sqlite3.connect('Sailsheets.db')
		c = db.cursor()

		# Below is the table schema for Boats table
		"""CREATE TABLE Purpose (p_id int primary key,
			p_name text,
			p_fee real,
			p_type text,
			p_ratetype text,
			p_account text,
			p_clubops int);
		"""

		# execute a query to insert the record
		c.execute("""INSERT INTO Purpose VALUES
			(:pid, :pname, :pfee, :ptype, :pratetype, :paccount, :pclubops) """,
			{
			'pid': p_id_e.get(),
			'pname': p_name_e.get(),
			'pfee': p_fee_e.get(),
			'ptype': p_type_e.get(),
			'pratetype': p_ratetype_e.get(),
			'paccount': p_account_e.get(),
			'pclubops': p_clubops_e.get() 
			})

		# commit the change and close the database
		db.commit()
		db.close()

		# now clear the entry boxes
		clearboxes()
		# delete the tree values
		purpose_tree.delete(*purpose_tree.get_children())
		# repopulate the tree with the table's values
		fill_tree_from_purpose_table()
		return

	#################################################################
	#
	# Remove the selected record and delete from the table
	#
	def remove_1_purpose():
		x = purpose_tree.selection()[0] # x is the index, not the actual tuple
		purpose_tree.delete(x)

		# Open the database and create a cursor
		db = sqlite3.connect('Sailsheets.db')
		c = db.cursor()

		# execute the update query
		c.execute("DELETE FROM Purpose WHERE p_id=" + p_id_e.get())

		# Commit the change and close the database
		db.commit()
		db.close()

		# now clear the entry boxes
		clearboxes()
		# delete the tree values
		purpose_tree.delete(*purpose_tree.get_children())
		# repopulate the tree with the table's values
		fill_tree_from_purpose_table()

		messagebox.showinfo('',"Purpose deleted!")
		return

	#################################################################
	# 
	# Select the record you picked
	#
	def select_record(e):

		# Clear the boat record boxes
		clearboxes()

		# Grab the record number
		selected = purpose_tree.focus()

		# Grab record values
		values = purpose_tree.item(selected, 'values')

		# Output to entry boxes
		p_id_e.insert(0, values[0])
		p_name_e.insert(0, values[1])
		p_fee_e.insert(0, values[2])
		p_type_e.insert(0, values[3])
		p_ratetype_e.insert(0, values[4])
		p_account_e.insert(0, values[5])
		p_clubops_e.insert(0, values[6])
		return

	#################################################################
	# 
	# Save updated record
	#
	def update_record():
		# Grab the record number
		selected = purpose_tree.focus()

		# Save new data
		purpose_tree.item(selected, text="", values=(
			p_id_e.get(),
			p_name_e.get(),
			p_fee_e.get(),
			p_type_e.get(),
			p_ratetype_e.get(),
			p_account_e.get(),
			p_clubops_e.get() 
			))
		# Open the database and create a cursor
		db = sqlite3.connect('Sailsheets.db')
		c = db.cursor()

		# execute the update query
		c.execute("""UPDATE Purpose SET
			p_name= :pname,
			p_fee= :pfee,
			p_type= :ptype,
			p_ratetype= :pratetype,
			p_account= :paccount,
			p_clubops= :pclubops
			WHERE p_id= :pid""",
			{
			'pname': p_name_e.get(),
			'pfee': p_fee_e.get(),
			'ptype': p_type_e.get(),
			'pratetype': p_ratetype_e.get(),
			'paccount': p_account_e.get(),
			'pclubops': p_clubops_e.get() ,
			'pid': p_id_e.get(),
			})

		# Commit the change and close the database
		db.commit()
		db.close()

		# now clear the entry boxes
		clearboxes()
		# delete the tree values
		purpose_tree.delete(*purpose_tree.get_children())
		# repopulate the tree with the table's values
		fill_tree_from_purpose_table()
		return

	# A simple function to close frames and clear the window
	def closemyframes():
		purpose_label.destroy()
		purpose_frame.destroy()
		button_frame.destroy()
		record_frame.destroy()
		return

	# Create binding click function
	#
	def clicker(e):
		select_record()

	#################################################################
	# Start the function code here
	#
	global purpose_tree

	#first, clear any frames that may be on the screen
	clear_all_frames()

	# Add the style for the editing window
	style = ttk.Style()

	# Pick a theme
	style.theme_use("clam") # choices are default, alt, clam, vista

	# Let's put a label just under the title
	#
	purpose_label = Label(mywin, text = "Purpose Table Editing", fg="red", font=("Helvetica", 18))
	purpose_label.pack(pady=10)

	# Create the frame for the boat table
	#
	purpose_frame = Frame(mywin)
	purpose_frame.pack(pady=10)

	# create the scrollbar on the right
	#
	tree_scroll = Scrollbar(purpose_frame)
	tree_scroll.pack(side=RIGHT, fill=Y)

	# Create the Treeview
	#
	purpose_tree = ttk.Treeview(purpose_frame, yscrollcommand=tree_scroll.set, selectmode='extended')

	# Pack the treeview to the screen
	#
	purpose_tree.pack()

	# Configure the scrollbar
	#
	tree_scroll.config(command=purpose_tree.yview)

	# Define the columns
	#
	purpose_tree['columns'] = ("p_id", "p_name", "p_fee", 
		"p_type", "p_ratetype", "p_account", "p_clubops")

	# format columns
	#
	purpose_tree.column("#0", width=0, stretch=NO)
	purpose_tree.column("p_id", anchor=CENTER, width=40, minwidth=40)
	purpose_tree.column("p_name", anchor=W, width=175, minwidth=100)
	purpose_tree.column("p_fee", anchor=E, width=50, minwidth=50)
	purpose_tree.column("p_type", anchor=CENTER, width=70, minwidth=70)
	purpose_tree.column("p_ratetype", anchor=CENTER, width=90, minwidth=35)
	purpose_tree.column("p_account", anchor=W, width=175, minwidth=35)
	purpose_tree.column("p_clubops", anchor=CENTER, width=90, minwidth=35)

	# Create Headings
	#
	purpose_tree.heading("#0", text="", anchor=W)
	purpose_tree.heading("p_id", text="ID", anchor=CENTER)
	purpose_tree.heading("p_name", text="Name", anchor=W)
	purpose_tree.heading("p_fee", text="Fee", anchor=E)
	purpose_tree.heading("p_type", text = "Type", anchor=CENTER)
	purpose_tree.heading("p_ratetype", text="Rate Type", anchor=CENTER)
	purpose_tree.heading("p_account", text="Account", anchor=W)
	purpose_tree.heading("p_clubops", text="Club Ops", anchor=CENTER)

	# Now get the data from the Boats Table
	#
	fill_tree_from_purpose_table()

	# Record Frame for editing/adding boats
	#
	record_frame = LabelFrame(mywin, text="Purpose Record")
	record_frame.pack(fill="x", expand="yes", padx=20)

	# Labels & Entry Boxes
	#
	p_id_l = Label(record_frame, text="ID")
	p_id_l.grid(row=0, column=0, padx=10, pady=5)
	p_id_e = Entry(record_frame)
	p_id_e.grid(row=0, column=1, padx=10, pady=5)

	p_name_l = Label(record_frame, text="Name")
	p_name_l.grid(row=1, column=0, padx=10, pady=5)
	p_name_e = Entry(record_frame)
	p_name_e.grid(row=1, column=1, padx=10, pady=5)

	p_fee_l = Label(record_frame, text="Fee if fixed")
	p_fee_l.grid(row=3, column=0, padx=10, pady=5)
	p_fee_e = Entry(record_frame)
	p_fee_e.grid(row=3, column=1, padx=10, pady=5)

	p_type_l = Label(record_frame, text="Type")
	p_type_l.grid(row=2, column=0, padx=10, pady=5)
	p_type_e = Entry(record_frame)
	p_type_e.grid(row=2, column=1, padx=10, pady=5)

	p_ratetype_l = Label(record_frame, text="Rate Type")
	p_ratetype_l.grid(row=2, column=2, padx=10, pady=5)
	p_ratetype_e = Entry(record_frame)
	p_ratetype_e.grid(row=2, column=3, padx=10, pady=5)

	p_account_l = Label(record_frame, text="Account")
	p_account_l.grid(row=1, column=2, padx=10, pady=5)
	p_account_e = Entry(record_frame)
	p_account_e.grid(row=1, column=3, padx=10, pady=5)

	p_clubops_l = Label(record_frame, text="Club Ops Required? 1=Y, 0=N")
	p_clubops_l.grid(row=3, column=2, padx=10, pady=5)
	p_clubops_e = Entry(record_frame)
	p_clubops_e.grid(row=3, column=3, padx=10, pady=5)

	# Buttons for commands to modify the records
	#
	button_frame = LabelFrame(mywin, text="Commands for editing the record")
	button_frame.pack(fill="x", expand="yes", padx=20)

	clear_button = Button(button_frame, text="Clear Entries", command=clearboxes)
	clear_button.grid(row=0, column=0, padx=10, pady=10)

	addrecord = Button(button_frame, text="Add New Purpose", command=addpurpose)
	addrecord.grid(row=0, column=1, padx=10, pady=10)

	editrecord = Button(button_frame, text="Update Selected Purpose", command=update_record)
	editrecord.grid(row=0, column=2, padx=10, pady=10)

	removerecord = Button(button_frame, text="Remove Selected Purpose", command=remove_1_purpose)
	removerecord.grid(row=0, column=3, padx=10, pady=10)

	# This button removes all the frames and buttons and closes the db.
	#
	alldone = Button(button_frame, text="All done", command=clear_all_frames)
	alldone.grid(row=0, column=5, padx=10, pady=10)
	alldone.focus()

	# Bindings
	#
	purpose_tree.bind("<ButtonRelease-1>", select_record)

	return
