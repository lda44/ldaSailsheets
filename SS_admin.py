from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import logging
import sqlite3
from pathlib import Path
import datetime as dt
from datetime import timedelta

import SS_reports
import updatemembers

# Set up the logging system
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(__name__ + '.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def clear_all_frames(mywin):
	for stuff in mywin.winfo_children():
		if str(stuff) != ".!menu" and str(stuff) != ".!label":
			stuff.destroy()

#####################################################################
# Update the members table from Club Express.
#
def a_update_members(mywin):

	###################################################################
	#
	# This function will ask the user for the location of the 
	# AllMembers.csv file that was extracted from Club Express.  
	#
	###################################################################
	importpath = './Transfer/'
	p = Path(importpath) 

	if not Path(importpath).exists():
		p.mkdir(parents=True)

	mywin.allmembersfile = filedialog.askopenfilename(initialdir='./Transfer',
		title='Open AllMembers.CSV file',
		filetypes=[("CSV Files", "*.csv")]
		)
	
	if mywin.allmembersfile != '':
		Success = updatemembers.UpdateMembers(mywin.allmembersfile)
		logger.info(mywin.allmembersfile + ' imported to Members Table.')
		messagebox.showinfo('', "Update completed")
	else:
		pass

#####################################################################
# Modify the Settings table
#
def editsettings(mywin):
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
			logger.info('Settings changed.')
			settings_frame.destroy()
		else:
			settings_frame.destroy()
		return

	#first, clear any frames that may be on the screen
	for stuff in mywin.winfo_children():
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
	settings_frame = Frame(mywin)
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
def monthly_reports(mywin):

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

		logger.info('Reports for ' + str(mymonth) + '-' + str(myyear) + ' created.')
		mo_combo.pack_forget()
		yr_combo.pack_forget()
		accept_btn.pack_forget()

	#first, clear any frames that may be on the screen
	clear_all_frames(mywin)

	# then create a combo box
	month_list = ['January', 'February', 'March',
		'April', 'May', 'June', 
		'July', 'August', 'September',
		'October', 'November', 'December']
	todaysdate = dt.datetime.today()
	thismonth = todaysdate.month
	thisyear = todaysdate.year
	years_list = [str(thisyear), str(thisyear-1), str(thisyear-2), str(thisyear-3)]
	mo_combo = ttk.Combobox(mywin, value=month_list)
	mo_combo.current(thismonth-1)
	mo_combo.pack(pady=10)
	yr_combo = ttk.Combobox(mywin, value=years_list)
	yr_combo.current(0)
	yr_combo.pack(pady=10)

	accept_btn = Button(mywin, text="Select", command=select)
	accept_btn.pack(pady=10)

	return

#####################################################################
# Member Usage Log
#
def member_usage_log(mywin):

	#################################################################
	#
	# This function creates an excel file with a log of all sailing
	# hours for the chosen member.
	# 
	#################################################################

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
			# if event.keysym == "Return":
			# 	choosecrew(event)
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

	def select():
		my_member_id = float(id_dict[name_combo.get()])

		Success = SS_reports.MemberUseLog(my_member_id)

		logger.info('Usage Log for ' + str(my_member_id) + ' created.')
		name_combo.pack_forget()
		accept_btn.pack_forget()
		
	#first, clear any frames that may be on the screen
	clear_all_frames(mywin)

	# then create a combo box
	mymembers = get_member_list()
	idlist = [x[0] for x in mymembers]
	memberlist = [i[1] for i in mymembers] 
	id_dict = {v: k for (k, v) in zip(idlist, memberlist)}
	name_dict = {k: v for (k, v) in zip(idlist, memberlist)}

	name_combo = AutocompleteCombobox(mywin)
	name_combo.set_completion_list(memberlist)
	name_combo.pack(padx=10, pady=10)
	
	accept_btn = Button(mywin, text="Select", command=select)
	accept_btn.pack(pady=10)

	return