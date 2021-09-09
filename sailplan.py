from screeninfo import get_monitors
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter.ttk import Treeview, Style, Button, Entry
from tkcalendar import Calendar
from tkcalendar import DateEntry
import logging
import sqlite3
import datetime as dt
from datetime import timedelta

# Set up the logging system
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(__name__ + '.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


class sp_askokcancel(object):
	
	def __init__(self, title='', msg=''):
	#my_win, my_title, my_msg

	# Required Data of Init Function
		self.title = title      # Is title of titlebar
		self.msg = msg          # Is message to display
		self.b1 = 'Ok'          # Button 1 (outputs '1')
		self.b2 = 'Cancel'      # Button 2 (outputs '0')
		self.choice = ''        # it will be the return of messagebox according to button press


	# Creating Dialogue for messagebox
		self.root = Toplevel()

	# Removing titlebar from the Dialogue
		self.root.overrideredirect(True)

	# Setting Geometry
		screen_width = self.root.winfo_screenwidth()
		screen_height = self.root.winfo_screenheight()
		app_width = int((screen_width / 2) * .6)
		app_height = int(screen_height * .6)

		num_monitors = len(get_monitors())

		x = (screen_width / (2 * num_monitors)) - (app_width / 2) 
		y = (screen_height / 2) - (app_height / 2)

		self.root.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')

	# Creating TitleBar
		self.titlebar = Label(self.root,text=self.title,
						wraplength=app_width-10,
						bd=0,
						font=("Verdana",10,'bold'),
						justify=CENTER
						)
		self.titlebar.place(x=60, y=15)

	# Creating Label For message
		self.msg = Label(self.root,text=msg,
						wraplength=app_width-100,
						font=("Helvetica",9),
						justify=LEFT
						#anchor='nw'
						)
		self.msg.place(x=50,y=35)
			#,height=app_height*.9,width=app_width*.9)

	# Creating B1 
		self.B1 = Button(self.root,text=self.b1,command=self.click1)
		self.B1.place(x=(app_width / 2),y=app_height*.85,height=30,width=60)

	# Getting place_info of B1
		self.B1.info = self.B1.place_info()

	# Creating B2
		self.B2 = Button(self.root,text=self.b2,command=self.click2)
		self.B2.place(x=int(self.B1.info['x'])-(70*1),
						y=int(self.B1.info['y']),
						height=int(self.B1.info['height']),
						width=int(self.B1.info['width'])
						)

	# Making MessageBox Visible
		self.root.wait_window()

	# Function on pressing B1 == Ok button
	def click1(self):
		self.root.destroy() # Destroying Dialogue
		self.choice='1'     # Assigning Value

	# Function on pressing B2 == Cancel button
	def click2(self):
		self.root.destroy() # Destroying Dialogue
		self.choice='2'     # Assigning Value



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
	# - Close a sailplan & post to the Ledger File
	# 
	# Things that don't work:
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
		logger.info('Sailplan table queried.')
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
		logger.info('Clearboxes function called.')

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
		
		try:
			if str(values[9]) == '1':
				# change the edit state
				addrecord.config(state='disabled')
				delrecord.config(state='disabled')
				editrecord.config(state='normal')
			else:
				# change the edit state
				addrecord.config(state='disabled')
				delrecord.config(state='normal')
				editrecord.config(state='normal')
			logger.info('select_record function returned spid and sp_closed fields.')
			return [values[0], values[9]]
		except IndexError:
			logger.exception('Index error - usually means clicking on a blank tree.')
			return -1, 1 # assume spid is new and also closed so no harm
		finally:
			pass



		
	#################################################################
	# 
	# Select the record you picked
	#
	def _record(e):
		
		# Grab the record number
		selected = my_tree.focus()

		# Grab record values
		values = my_tree.item(selected, 'values')
		logger.info('_record function called.')
		return [values[0], values[9]]

		
	#################################################################
	# 
	# Select the record you picked
	#
	def edit_this_record(e):
		
		# Grab the record number
		selected = my_tree.focus()

		# Grab record values
		values = my_tree.item(selected, 'values')
		logger.info('Edit sailplan: #' + str(values[0]) + ' | Closed=' + str(values[9]))
		add_edit_record(values[0], values[9])


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

		#########################################################
		# Begin internal "add or edit a sailplan" functions here
		#
		class AutocompleteCombobox(ttk.Combobox):
			# This code snip lifted from stackoverflow, courtesy:
			"""
			Created by Mitja Martini on 2008-11-29.
			Updated by Russell Adams, 2011/01/24 to support Python 3 and Combobox.
			Updated by Dominic Kexel to use Tkinter and ttk instead of tkinter and tkinter.ttk
				Licensed same as original (not specified?), or public domain, whichever is less restrictive.
			""" 

			def set_completion_list(self, completion_list):
				"""Use our completion list as our drop down selection menu, arrows move through menu."""
				self._completion_list = sorted(completion_list, key=str.lower) # Work with a sorted list
				self._hits = []
				self._hit_index = 0
				self.position = 0
				self.bind('<KeyRelease>', self.handle_keyrelease)
				self['values'] = self._completion_list  # Setup our popup menu

			def autocomplete(self, delta=0):
				"""autocomplete the Combobox, delta may be 0/1/-1 to cycle through possible hits"""
				if delta: # need to delete selection otherwise we would fix the current position
					self.delete(self.position, END)
				else: # set position to end so selection starts where textentry ended
					self.position = len(self.get())
				# collect hits
				_hits = []
				for element in self._completion_list:
					if element.lower().startswith(self.get().lower()): # Match case insensitively
						_hits.append(element)
					# if we have a new hit list, keep this in mind
					if _hits != self._hits:
						self._hit_index = 0
						self._hits=_hits
					# only allow cycling if we are in a known hit list
					if _hits == self._hits and self._hits:
						self._hit_index = (self._hit_index + delta) % len(self._hits)
					# now finally perform the auto completion
					if self._hits:
						self.delete(0, END)
						self.insert(0,self._hits[self._hit_index])
						self.select_range(self.position, END)

			def handle_keyrelease(self, event):
				"""event handler for the keyrelease event on this widget"""
				if event.keysym == "Return" or event.keysym == "Tab":
					if str(self) == '.!labelframe3.!autocompletecombobox':
						logger.info(str(self) + ': Crew added')
						choosecrew(event)
					elif str(self) == '.!labelframe2.!autocompletecombobox2':
						logger.info(str(self) + ': Skipper added')
						set_skipper_id(event)
					else: 
						logger.info(str(self) + ': Nothing')
				if event.keysym == "BackSpace":
					self.delete(self.index(INSERT), END)
					self.position = self.index(END)
				if event.keysym == "Left":
					if self.position < self.index(END): # delete the selection
						self.delete(self.position, END)
					else:
						self.position = self.position-1 # delete one character
						self.delete(self.position, END)
				if event.keysym == "Right":
					self.position = self.index(END) # go to end (no selection)
				if len(event.keysym) == 1:
					self.autocomplete()
				# No need for up/down, we'll jump to the popup
				# list at the position of the autocompletion

		def makecrewtree(crewqry, mytree, sp_closed):
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
			if sp_closed !='1':
				mytree.tag_configure('oddrow', background='#D3D3D3') # light silver
				mytree.tag_configure('evenrow', background='gray') 
			else:
				mytree.tag_configure('oddrow', background='#D3D3D3', foreground='gray') # light silver
				mytree.tag_configure('evenrow', background='silver', foreground='gray') 
			return mytree



		def getcrewlist(spid, sp_closed):
			#
			# Open the db and establish a cursor
			try:
				db = sqlite3.connect('Sailsheets.db')
				c = db.cursor()
				if sp_closed != '1':
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
					logger.info('Crew table queried for open sailplan ' + str(spid) + '.')
				else:
					# query to pull the data from the Ledger table
					c.execute("""SELECT l_member_id, l_name, l_billto_id FROM Ledger 
						WHERE l_sp_id = :l_spid ORDER BY l_name""", {'l_spid': spid,})
					logger.info('Crew table queried for closed sailplan ' + str(spid) + '.')

				# fetch the data
				crewqry = c.fetchall()
				# commit and close the DB
				db.commit()
				db.close()
			except:
				logger.exception('Tried to access sailplan crew list.')
			else:
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
				'spnrob': len(getcrewlist(myspid, '0')),
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


		def checkin_sailplan(myspid):
			#
			# this function has to accomplish the following things for myspid:
			# 1. record the check in time from the system time
			# 2. compute the number of hours sailed
			# 3. compute the fees due to NPSC based on purpose
			# 4. compute the bill owed to MWR based on purpose
			# 5. record the sail plan as 'closed' in Sailplan table
			# 6. record the crew fees due to NPSC in the ledger table
			#
			def get_purpose_fees(mypurpose):
				db = sqlite3.connect('Sailsheets.db')
				c = db.cursor()
				c.execute("""SELECT * FROM Purpose WHERE p_name= :pname""",
					{'pname': mypurpose,})
				purpose_fees = c.fetchone()
				db.commit()
				db.close()
				return list(purpose_fees)
	

			def get_boat_rates(myboat):
				db = sqlite3.connect('Sailsheets.db')
				c = db.cursor()
				c.execute("""SELECT * FROM Boats WHERE boat_name= :bname""",
					{'bname': myboat,})
				boat_rates = c.fetchone()
				db.commit()
				db.close()
				return list(boat_rates)


			def get_settings():
				db = sqlite3.connect('Sailsheets.db')
				c = db.cursor()
				c.execute("SELECT * FROM Settings ")
				mysettings = c.fetchone()
				db.commit()
				db.close()
				return list(mysettings)


			def get_crew_list(spid):
				db = sqlite3.connect('Sailsheets.db')
				c = db.cursor()
				c.execute("""SELECT * FROM openspcrew 
					WHERE o_spid = :ospid""", {'ospid': spid,})
				crewqry = c.fetchall()
				db.commit()
				db.close()
				return crewqry


			def get_member_details(myid):
				db = sqlite3.connect('Sailsheets.db')
				c = db.cursor()
				c.execute("SELECT * FROM Members WHERE m_id = :mid", {'mid': myid,})
				memberdetails = c.fetchone()
				db.commit()
				db.close()
				return memberdetails


			def close_sailplan_record(sailplan):
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
					'spto': sailplan[1],
					'spskid': sailplan[2], 
					'spboat': sailplan[3], 
					'sppurp': sailplan[4], 
					'spdesc': sailplan[5], 
					'speta': sailplan[6], 
					'spti': sailplan[7], 
					'sphrs': sailplan[8],
					'spfee': sailplan[9],
					'spdue': sailplan[10],
					'spbill': sailplan[11],
					'spnrob': sailplan[12],
					'spcomp': sailplan[13],
					'spid': sailplan[0],
					})
				db.commit()
				db.close()
				return

			def write_fees_to_ledger(crewlist, sailplan):
				ledgerlist = []
				db = sqlite3.connect('Sailsheets.db')
				c = db.cursor()
				c.execute("""SELECT Ledger_id from Ledger where Ledger_id = (select max(Ledger_id) from Ledger)""")
				last_id = c.fetchone()[0]
				db.commit()
				db.close()

				for crew in crewlist:
					logger.info(str(last_id) + ': added to ledger')
					last_id += 1
					ledgerentry = (last_id, 
						sailplan[1][0:10], 
						crew[0], 
						crew[1],
						crew[3],
						sailplan[3] + ' - ' + sailplan[5],
						0,
						0,
						crew[4],
						crew[5],
						sailplan[4],
						sailplan[0],
						sailplan[7][10])
					ledgerlist.append(ledgerentry)

				db = sqlite3.connect('Sailsheets.db')
				c = db.cursor()
				c.executemany("""INSERT INTO Ledger VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
					ledgerlist)
				db.commit()
				db.close()
				return
			

			def cleanup_open_data(sp_id):
				# Remove the list of crew from the openspcrew table.

				db = sqlite3.connect('Sailsheets.db')
				c = db.cursor()
				c.execute("DELETE from openspcrew where o_spid = :spid", {'spid': sp_id,})
				db.commit()
				db.close()
				logger.info('Closed sailplan ' + str(sp_id) + ' crew removed from openspcrew table.')


			# Get the current date/time
			checkin_dt = dt.datetime.today().isoformat(sep=' ', timespec='seconds')
			
			# Query the sail plan from the table
			sailplan = list(get_sailplan_df(myspid))
			
			sailplan[7] = checkin_dt
			dt_checkin = dt.datetime.strptime(checkin_dt, '%Y-%m-%d %H:%M:%S')
			dt_timeout = dt.datetime.strptime(sailplan[1], '%Y-%m-%d %H:%M:%S')
			time_delta = (dt_checkin - dt_timeout) 
			minutes_sailed = time_delta.total_seconds()/60
			hours_sailed = time_delta.total_seconds()/60/60
			#print('\n', 'My time delta in hours: ', round(hours_sailed, 2), '\n')
			
			# first, check if the rental was less than the grace period
			# 
			grace_period = get_settings()[1]
			#print('Minutes: ', minutes_sailed, '\n', 'Grace: ', grace_period, '\n')
			purpose_fees = get_purpose_fees(sailplan[4])
			
			if minutes_sailed <= float(grace_period):
				messagebox.showinfo('', 'Sail less than minimum amount, no charge.')
				logger.info('Sailplan less than minimum amount, no charge: ' + str(sailplan[0]) + '-' + str(sailplan[3]))
				purpose_fees[3] = 'Not minimum sail'	
				
			sailplan[8] = round(hours_sailed, 1)
			sailplan[13] = 1
			
			boat_rates = get_boat_rates(sailplan[3])
			crewlist = get_crew_list(myspid)
			#print('Crew List of tuples:', '\n', crewlist)

			if purpose_fees[3] == 'Fixed':
				crewlist_w_fee = []
				is_club_ops = purpose_fees[6] 	# 0 = no, 1 = yes

				# collect the fixed rate from the purpose table
				#
				sailplan[9] = round(purpose_fees[2], 2)
				
				for crew in crewlist:
					# Club Ops Skippers paid by the Club
					#
					if is_club_ops == 1 and crew[3] == 1: 
						crew_w_fee = crew + (0,)
					else:
						crew_w_fee = crew + (sailplan[9],)

					crewlist_w_fee.append(crew_w_fee)
				
				# multiply total crew times fixed fee each = total collected
				# note for ASA classes this will be zero and are collected
				# separately when scheduled.
				#
				sailplan[10] = round(sailplan[12]*purpose_fees[2], 2) 
				
				# find the best rate
				#
				if hours_sailed % 24 * boat_rates[7] > boat_rates[8]: 
					best_rate = (1 - get_settings()[0]/100) * (
						((hours_sailed // 24 + 1) * boat_rates[8]))
				else: 
					best_rate = (1 - get_settings()[0]/100) * (
						(hours_sailed % 24 * boat_rates[7]) + 
						(hours_sailed // 24 * boat_rates[8]))
				# total amount to be paid to MWR
				#
				sailplan[11] = round(best_rate, 2)

			elif purpose_fees[3] == 'Hourly':
				# create a new list and append the old list of tuples
				# but with a computed fee for each crewmember
				# later this will be summed by billtoid to figure out
				# how much each member should be billed for the sail
				#
				crewlist_w_fee = []
				total_fees = 0
				mwr_bill = 0
				is_club_ops = purpose_fees[6] 	# 0 = no, 1 = yes

				for crew in crewlist:
					# get member details to determine proper rate
					crew_details = get_member_details(crew[4])
					if crew_details[4] == 'E-5 & Below':
						hour_col = 5
						daily_col = 6
					else:
						hour_col = 7
						daily_col = 8

					#
					# find the best rate
					#
					if hours_sailed % 24 * boat_rates[hour_col] > boat_rates[daily_col]: 
						crewfee = ((1 - get_settings()[0]/100) * (
							((hours_sailed // 24 + 1) * boat_rates[daily_col]))) / sailplan[12]
					else: 
						crewfee = ((1 - get_settings()[0]/100) * (
							(hours_sailed % 24 * boat_rates[hour_col]) + 
							(hours_sailed // 24 * boat_rates[daily_col]))) / sailplan[12]
					
					# Club Ops Skippers paid by the Club
					#
					if is_club_ops == 1 and crew[3] == 1: 
						crew_w_fee = crew + (0,)
					else:
						crew_w_fee = crew + (round(crewfee, 2),)
						total_fees += crewfee

					crewlist_w_fee.append(crew_w_fee)
					mwr_bill += crewfee
				
				# fee per person
				#
				sailplan[9] = round(total_fees/sailplan[12], 2)
				
				# total fee to be collected
				#
				sailplan[10] = round(total_fees, 2)
				
				# total amount to be paid to MWR
				#
				if sailplan[3].lower() == 'skyline':
					sailplan[11] = 0
				else:
					sailplan[11] = round(mwr_bill, 2)
			else:
				# this would be a free event
				#
				crewlist_w_fee = []
				for crew in crewlist:
					crew_w_fee = crew + (0,)
					crewlist_w_fee.append(crew_w_fee)
				
				sailplan[9] = 0 	# fee per person
				sailplan[10] = 0 	# total collected by NPSC
				sailplan[11] = 0 	# total due to MWR

			logger.info('Sailplan closed & written to ledger: ' + str(sailplan[0]) + '-' + str(sailplan[3]))

			# At this point we have:
			# 1. sailplan list of fields that needs to be written to the sailplan table
			# 2. Crew list of tuples w fees that needs to be written to the ledger
			close_sailplan_record(sailplan)
			write_fees_to_ledger(crewlist_w_fee, sailplan)
			cleanup_open_data(myspid)

			# now close the window and return to the screen
			sp_win.destroy()

			# repopulate the tree with the table's values
			q_sp_table(dt.datetime.today())
			return


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
				'spskid': 0, 
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
			#skip_n_combo.set(name_dict[float(sp_skid_e.get())])
			set_skipper_name(event)


		def set_skipper_id(event): 
			# confirms works 7/15
			global crew_tree
			skipname = skip_n_combo.get()
			if skipname == '': return
			skipid = float(id_dict[skipname])
			logger.debug(str(event) + ': Skipper - ' + skipname + ', ID: ' + str(skipid))
			#crewqry = getcrewlist(mysp_id, '0')
			if skipid in [x[0] for x in getcrewlist(mysp_id, '0')]:
				logger.info('Tried to add a duplicate Skipper.')
				sp_win.attributes('-topmost',0)
				messagebox.showinfo('ENTRY ERROR!', 'That Skipper is already listed.')
				sp_win.attributes('-topmost',1)
			else:
				sp_skid_e.config(state='normal')
				sp_skid_e.delete(0, END)
				sp_skid_e.insert(0, str(skipid))
				sp_skid_e.config(state='disabled')
				crewqry = add_crew(1, 1, skipname, skipid, skipid)
				crewlist = [x[1] for x in crewqry]
				crew_tree = makecrewtree(crewqry, crew_tree, 0)
			logger.info('Set Skipper ID function finished.')


		def set_skipper_name(event): 
			# Need to remove this and show it as read only.
			global crew_tree
			if sp_skid_e.get() == '': return
			skipid = sp_skid_e.get()
			skip_n_combo.set(name_dict[float(sp_skid_e.get())])
			#crewqry = getcrewlist(mysp_id, '0')
			if skipid in [x[0] for x in getcrewlist(mysp_id, '0')]:
				logger.info('Tried to add a duplicate Skipper.')
				sp_win.attributes('-topmost',0)
				messagebox.showinfo('', 'That Skipper is already listed.')
				sp_win.attributes('-topmost',1)
			else:
				crewqry = add_crew(1, 1, skip_n_combo.get(), skipid, skipid)
				crewlist = [x[1] for x in crewqry]
				crew_tree = makecrewtree(crewqry, crew_tree, 0)
			logger.info('Set Skipper Name function finished.')


		def choosecrew(event):
			# confirms works 7/15
			global crew_tree
			logger.debug(str(event) + ': Crew - ' + a_member_c.get() + ', ID: ' + str(id_dict[a_member_c.get()]))
			crewid = float(id_dict[a_member_c.get()])
			crewqry = getcrewlist(mysp_id, '0')
			if crewid in [x[0] for x in getcrewlist(mysp_id, '0')]:
				logger.info('Tried to add a duplicate crew member.')
				sp_win.attributes('-topmost',0)
				messagebox.showinfo('', 'That crew member is already listed.')
				sp_win.attributes('-topmost',1)
			else:
				crewqry = add_crew(1, 0, a_member_c.get(), crewid, crewid)
				crewlist = [x[1] for x in crewqry]
				crew_tree = makecrewtree(crewqry, crew_tree, 0)
			a_member_c.delete(0, END)
			logger.info('Choose crew function finished.')


		def chooseguest(event):
			# confirms works 7/15
			global crew_tree
			guestof_id = id_dict[a_guestof_c.get()]
			crewqry = add_crew(1, 0, a_guestname_e.get(), -1, guestof_id)
			crewlist = [x[1] for x in crewqry]
			crew_tree = makecrewtree(crewqry, crew_tree, 0)
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
			return getcrewlist(mysp_id, '0')


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
			return


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
			crewqry = getcrewlist(mysp_id, '0')
			crewlist = [x[1] for x in crewqry]
			crew_tree = makecrewtree(crewqry, crew_tree, 0)
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
		if sp_closed == '1': # the sail plan is closed so read only for the fields
			edit_state = 'disabled'
			add_state = 'disabled'
			new = 0
			logger.info('Sailplan ' + str(mysp_id) + ' reviewed.')
		else:
			edit_state = 'normal'
			add_state = 'normal'
			new = 0
			logger.info('Sailplan ' + str(mysp_id) + ' edited.')

		if mysp_id == -1:
			w_header = "Navy Patuxent Sailing Club"
			w_title = "RELEASE AND WAIVER OF LIABILITY, ASSUMPTION OF RISK, AND INDEMNITY AND PARENTAL CONSENT AGREEMENT"
			with open('LiabilityWaiver.txt') as f:
				w_contents = f.readlines()
			l_waiver = ''
			for x in w_contents: l_waiver += x

			if sp_askokcancel(w_title, l_waiver).choice != '1':
				return
			# create a blank record -- if the user cancels out this will get removed
			#
			mysp_id = newblanksailplan()
			new = 1 # this is a new record, used when canceling
			edit_state = "normal"
			add_state = "normal"
			logger.info('Sailplan ' + str(mysp_id) + ' to be added.')


		# Create a new window
		sp_win = Tk()
		sp_win.title("Sail Plan")
		#sp_win.overrideredirect(True)

		screen_width = sp_win.winfo_screenwidth()
		screen_height = sp_win.winfo_screenheight()
		app_width = int((screen_width / 2) * .39)
		app_height = int(screen_height * .60)

		x = (screen_width / (2 * len(get_monitors()))) - (app_width / 2) # screen_width / 4 for 2 monitors, /2 for 1
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
		crewlist = [x[1] for x in getcrewlist(mysp_id, 0)]
		
		
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
		
		crew_del_btn = Button(sp_win, text='Delete Crew', state=edit_state, 
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
		crew_tree = makecrewtree(getcrewlist(mysp_id, sp_closed), crew_tree, sp_closed)
		
		style = Style(mywin)
		disabled_bg = style.lookup("TEntry", "fieldbackground", ("disabled",))
		disabled_fg = style.lookup("TEntry", "foreground", ("disabled",))

		# Record Frame for editing/adding 
		#
		sailplan_frame = LabelFrame(sp_win, text="SailPlan Record")
		sailplan_frame.place(x=10, rely=.075)

		# Labels & Entry boxes for the record
		#
		# Top line of entries:
		#
		sp_boat_l = Label(sailplan_frame, text="Boat:")
		sp_boat_l.grid(row=0, column=0, sticky=W, padx=10)
		boat_combo = AutocompleteCombobox(sailplan_frame)
		boat_combo.set_completion_list(myboatlist)

		boat_combo.insert(0, mysailplan[3])
		boat_combo.grid(row=1, column=0, padx=10)
		boat_combo.config(state=edit_state)

		sp_skid_l = Label(sailplan_frame, text="Skipper Club # and Name:")
		sp_skid_l.grid(row=0, column=1, sticky=W, columnspan=2)
		sp_skid_e = Entry(sailplan_frame, width=10)
		sp_skid_e.insert(0, mysailplan[2])
		sp_skid_e.grid(row=1, column=1, sticky=W)
		sp_skid_e.focus()
		sp_skid_e.config(state='disabled')
		skip_n_combo = AutocompleteCombobox(sailplan_frame)
		skip_n_combo.set_completion_list(memberlist)

		if new != 1: skip_n_combo.set(name_dict[int(mysailplan[2])])
		skip_n_combo.grid(row=1, column=2, padx=10)
		skip_n_combo.config(state=edit_state)

		sp_purp_l = Label(sailplan_frame, text="Purpose:")
		sp_purp_l.grid(row=0, column=3, sticky=W)
		purp_combo = ttk.Combobox(sailplan_frame, value=mypurplist)
		if new != 1: purp_combo.insert(0, mysailplan[4])
		else: purp_combo.insert(0, 'Recreational Use') # Default
		purp_combo.grid(row=1, column=3)
		purp_combo.config(state=edit_state)

		# Second line of entries:
		#
		sp_to_l = Label(sailplan_frame, text="Time Checked Out:")
		sp_to_l.grid(row=2, column=0, columnspan=2, sticky=W, padx=10)
		sp_to_e = Entry(sailplan_frame, width=20, justify=LEFT, state='normal')
		if new == 1:
			sp_to_e.insert(0, dt.datetime.today().isoformat(sep=' ', timespec='seconds'))
		else: sp_to_e.insert(0, mysailplan[1])
		sp_to_e.grid(row=3, column=0, columnspan=2, sticky=W, padx=10)
		sp_to_e.config(state='disabled')
		
		sp_eta_l = Label(sailplan_frame, text="Est Return Time:")
		sp_eta_l.grid(row=2, column=1, columnspan=2, sticky=W)
		sp_eta_e = Entry(sailplan_frame, width=20, justify=LEFT)
		if new == 1:
			sp_eta_e.insert(0, 
			(dt.datetime.today() + timedelta(hours=4)).isoformat(sep=' ', timespec='seconds')) 
			# add 4 hours by default
		else: sp_eta_e.insert(0, mysailplan[6])
		sp_eta_e.grid(row=3, column=1, columnspan=2, sticky=W)
		sp_eta_e.config(state=edit_state)

		sp_ti_l = Label(sailplan_frame, text="Time Checked In:")
		sp_ti_l.grid(row=2, column=3, columnspan=2, sticky=W)
		sp_ti_e = Entry(sailplan_frame, width=20, justify=LEFT, state='normal')
		if sp_closed != '1': sp_ti_e.insert(0, sp_eta_e.get())
		else: sp_ti_e.insert(0, mysailplan[7])
		sp_ti_e.grid(row=3, column=3, columnspan=2, sticky=W)
		sp_ti_e.config(state='disabled')

		# Third line of entries:
		#
		sp_desc_l = Label(sailplan_frame, text="Description:")
		sp_desc_l.grid(row=4, column=0, sticky=W, padx=10, pady=5)
		sp_desc_e = Entry(sailplan_frame, justify=LEFT, width=55)
		sp_desc_e.insert(0, mysailplan[5])
		sp_desc_e.grid(row=4, column=1, columnspan=3, sticky=W)
		sp_desc_e.config(state=edit_state)

		# Add Club Member frame and entry boxes
		#
		add_member_frame = LabelFrame(sp_win, 
			text="Add a Club Member:")
		add_member_frame.place(x=10, rely=.375, anchor=W)
		#a_club_id_l = Label(add_member_frame, text=" ")
		#a_club_id_l.grid(row=0, column=0, sticky=W, padx=10)
		#a_club_id_e = Entry(add_member_frame, justify=LEFT, width=10)
		#a_club_id_e.grid(row=0, column=1, stick=W)
		#a_club_id_e.config(state=add_state)

		a_member_l = Label(add_member_frame, text="Name:")
		a_member_l.grid(row=1, column=0, sticky=W, padx=10)
		a_member_c = AutocompleteCombobox(add_member_frame)
		a_member_c.set_completion_list(memberlist)

		a_member_c.grid(row=1, column=1, padx=10, pady=5)
		a_member_c.config(state=add_state)

		# Add a Guest frame
		#
		add_guest_frame = LabelFrame(sp_win, 
			text="Add a Guest:")
		add_guest_frame.place(x=655, rely=.375, anchor=E)
		a_guestname_l = Label(add_guest_frame, text="Guest Name:")
		a_guestname_l.grid(row=0, column=0, sticky=W, padx=10)
		a_guestname_e = Entry(add_guest_frame, justify=LEFT, width=20)
		a_guestname_e.grid(row=0, column=1, stick=W, padx=10, pady=5)
		a_guestname_e.config(state=add_state)

		a_guestof_l = Label(add_guest_frame, text="Guest of:")
		a_guestof_l.grid(row=1, column=0, sticky=W, padx=10)
		a_guestof_c = ttk.Combobox(add_guest_frame, value= crewlist, 
			postcommand= lambda: a_guestof_c.configure(values=
				[x[1] for x in getcrewlist(mysp_id, sp_closed)]))
		a_guestof_c.grid(row=1, column=1, pady=5)
		a_guestof_c.config(state=add_state)

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
			state=edit_state, command=lambda: checkin_sailplan(mysp_id))
		check_in.grid(row=0, column=3, padx=10, pady=10)
		check_in.config(state=edit_state)

		# This button closes the sailplan window and saves the sailplan in OPEN state,
		# checking the boat OUT. State will be disabled for an edit, normal for new.
		#
		save_btn = Button(button_frame, text="Save Sail Plan", 
			command=lambda: update_sailplan(mysp_id))
		save_btn.grid(row=0, column=5, sticky=E, padx=10, pady=10)
		save_btn.config(state=edit_state)

		# Let's put a label at the top of the window
		sp_label = Label(sp_win, text = "Sail Plans", fg="blue", font=("Helvetica", 24))
		sp_label.place(relx=.5, anchor=N)

		if sp_closed == '1':
			a_member_c.unbind('<<ComboboxSelected>>')
			a_guestof_c.unbind('<<ComboboxSelected>>')
			sp_skid_e.unbind('<KeyPress-Return>')
			sp_skid_e.unbind('<KeyPress-Tab>')
			crew_tree.unbind('<ButtonRelease-1>')
			style.map("Treeview", 
	          fieldbackground=[("disabled", disabled_bg)],
	          foreground=[("disabled", "gray")],
	          background=[("disabled", disabled_bg)])
		else:
			sp_skid_e.bind('<KeyPress-Return>', set_skipper_name)
			sp_skid_e.bind('<KeyPress-Tab>', set_skipper_name)
			a_member_c.bind('<<ComboboxSelected>>', choosecrew)
			a_guestof_c.bind('<<ComboboxSelected>>', chooseguest)
			crew_tree.bind('<ButtonRelease-1>', select_crew)
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
			logger.info('Sail Plan ' + str(mysp_id) + ' deleted.')
			messagebox.showinfo('', "Sail Plan Deleted!")
		else:
			messagebox.showinfo('', "Sail Plan Complete, cannot delete!")
		
		return
	
	# Create binding click function
	#
	#def clicker(e):
	#	myinfo = select_record(e)


	def datepicker():
		global my_date
		my_date = cal.get_date()
		q_sp_table(dt.date.fromisoformat(my_date))
		addrecord.config(state='normal')
		delrecord.config(state='disabled')
		editrecord.config(state='disabled')
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

	delrecord = Button(button_frame, text="Delete Sail Plan", 
		state='disabled',
		command=remove_1_record)
	delrecord.grid(row=0, column=2, padx=10, pady=5)

	editrecord = Button(button_frame, text="Edit Sail Plan", 
		state='disabled',
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
	cal.bind("<Double-Button-1>", datepicker)
	my_tree.bind("<ButtonRelease-1>", select_record)
	my_tree.bind("<Double-Button-1>", edit_this_record)

	return
	
