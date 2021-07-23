from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import Calendar, DateEntry
import sqlite3
import datetime as dt
from datetime import timedelta
import LiabilityWaiver


#####################################################################
# 
# Sail Plan
#
def sailplanmenu(mywin):
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
	# Common functions are here
	#
	def clear_all_frames():
		for stuff in mywin.winfo_children():
			if str(stuff) != ".!menu" and str(stuff) != ".!label":
				stuff.destroy()

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

		#########################################################
		# Begin internal "add or edit a sailplan" functions here
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
			skipid = sp_skid_e.get()
			skip_n_combo.set(name_dict[float(sp_skid_e.get())])
			crewqry = add_crew(1, 1, skip_n_combo.get(), skipid, skipid)
			crewlist = [x[1] for x in crewqry]
			crew_tree = makecrewtree(crewqry, crew_tree)


		def choosecrew(event):
			# confirms works 7/15
			global crew_tree
			crewid = float(id_dict[a_member_c.get()])
			a_club_id_e.insert(0, crewid)
			crewqry = add_crew(1, 0, a_member_c.get(), crewid, crewid)
			crewlist = [x[1] for x in crewqry]
			crew_tree = makecrewtree(crewqry, crew_tree)
			a_member_c.delete(0, END)
			a_club_id_e.delete(0, END)


		def chooseguest(event):
			# confirms works 7/15
			global crew_tree
			guestof_id = id_dict[a_guestof_c.get()]
			crewqry = add_crew(1, 0, a_guestname_e.get(), -1, guestof_id)
			crewlist = [x[1] for x in crewqry]
			crew_tree = makecrewtree(crewqry, crew_tree)
			a_guestname_e.delete(0, END)
			a_guestof_c.delete(0, END)


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
		# Main code for the add edit sailplan module is here
		#
		#########################################################
		#
		# the following are variables passed to the function when executed. 
		# Once testing is complete, the function will be altered to have thise
		# as input variables to the function so that it can execute both 
		# add and edit of the sailplan.  
		#   
		global edit_state, add_state, crew_tree, crewlist

		#mysp_id = -1 # -1 = new sailplan, all others are edit to existing sailplan
		#sp_closed = 0 # 1 = the sailplan is closed, 0 = the sailplan is still open
		#
		if mysp_id == -1:
			if messagebox.askokcancel(LiabilityWaiver.w_header, LiabilityWaiver.w_title) != 1:
				return
			# create a blank record -- if the user cancels out this will get removed
			#
			mysp_id = newblanksailplan()
			new = 1 # this is a new record, used when canceling
			edit_state = "disabled"
			add_state = "disabled"
		else:
			edit_state = "normal"
			new = 0

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

		sp_date = dt.datetime.today().isoformat(sep=' ', timespec='seconds') 
		# date for ledger file based on sp_datein; 
		# not recorded until complete?

		#populate the drop down lists from the tables
		#
		myboatlist = get_boat_list()
		mypurplist = get_purpose_list()
		mymembers = get_member_list()
		idlist = [x[0] for x in mymembers]
		memberlist = [i[1] for i in mymembers] 
		id_dict = {v: k for (k, v) in zip(idlist, memberlist)}
		name_dict = {k: v for (k, v) in zip(idlist, memberlist)}

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
		#	state=edit_state, command=update_sailplan)
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
	my_label = Label(mywin, text = "Sail Plans", fg="red", font=("Helvetica", 18))
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
	cal_frame = Frame(mywin)
	cal_frame.pack(pady=5)

	cal = Calendar(cal_frame, firstweekday='sunday', date_pattern='yyyy-mm-dd',
		showweeknumbers=FALSE, selectmode='day')
	cal.pack(pady=5)
	
	calbtn = Button(cal_frame, text="Select Date", command=datepicker)
	calbtn.pack(pady=5)

	# Buttons for commands to modify the records
	#
	button_frame = LabelFrame(mywin, text="Commands for Sail Plans")
	button_frame.columnconfigure(3, weight=5)
	button_frame.pack(fill="x", padx=80)

	# -1 means this is a new sailplan number
	# 0 in the second column means it's still open
	addrecord = Button(button_frame, text="Add Sail Plan", command=lambda: add_edit_record(-1, 0))
	addrecord.grid(row=0, column=1, padx=10, pady=5)
	#addrecord.focus()

	delrecord = Button(button_frame, text="Delete Sail Plan", command=remove_1_record)
	delrecord.grid(row=0, column=2, padx=10, pady=5)

	editrecord = Button(button_frame, text="Edit Sail Plan", 
		state='normal',
		command=lambda: add_edit_record(select_record(0)[0], select_record(0)[1]))
	editrecord.grid(row=0, column=3, columnspan=5, sticky=E, padx=10, pady=5)

	# This button removes all the frames and buttons and closes the db.
	#
	#alldone = Button(button_frame, text="Quit", command=mywin.quit)
	#alldone.grid(row=0, column=4, padx=10, pady=5)
	#alldone.focus()	

	# Create the frame for the sailplan table
	#
	my_frame = Frame(mywin)
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
	
