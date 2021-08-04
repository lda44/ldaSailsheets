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

#####################################################################
# View and modify the Boats Table
#
def editboats(mywin):

	#################################################################
	#
	# This function is meant to allow editing of the Boats Table to
	# enable revising the details for each boat such as rental rates.
	#
	# Also allows adding or deleting a boat.
	#
	#################################################################

	def clear_all_frames():
		for stuff in mywin.winfo_children():
			if str(stuff) != ".!menu" and str(stuff) != ".!label":
				stuff.destroy()

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
		logger.info('Boat Tree updated.')

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
		logger.info('Added a new boat.')

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
		logger.info('Deleted a boat.')

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
		logger.info('Updated a boat record.')

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
	logger.info('Entered the editboats module.')
	global boat_tree

	#first, clear any frames that may be on the screen
	clear_all_frames()

	# Add the style for the editing window
	style = ttk.Style()

	# Pick a theme
	style.theme_use("clam") # choices are default, alt, clam, vista

	# Let's put a label just under the title
	#
	boat_label = Label(mywin, text = "Boats Table Editing", fg="red", font=("Helvetica", 18))
	boat_label.pack(pady=10)

	# Create the frame for the boat table
	#
	boat_frame = Frame(mywin)
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
	record_frame = LabelFrame(mywin, text="Boat Record")
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
	button_frame = LabelFrame(mywin, text="Commands for editing the record")
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

