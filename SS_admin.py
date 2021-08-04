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

