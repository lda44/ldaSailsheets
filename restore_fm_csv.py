from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox
import csv
import logging
import sqlite3
from pathlib import Path

#####################################################################
#
# This module simply updates tables from an export of the csv files
#
# Duplicate records are ignored so if ledger ID is already in the ledger
# file, then the imported record is ignored.  Same for sailplan ID.
#

# Set up the logging system
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler('restore_fm_csv.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

def update_ledger(ledgerfile):
	"""\
	CREATE TABLE IF NOT EXISTS "Ledger"(
		ledger_id int PRIMARY KEY, 
	    l_date text,
	    l_member_id int,
	    l_name text, 
	    l_skipper int,
	    l_description text,
	    l_mwrvol int,
	    l_clubvol int,
	    l_billto_id int,
	    l_fee real,
	    l_account text,
	    l_sp_id int,
	    l_uploaddate text
	    );
	"""

	db = sqlite3.connect('Sailsheets.db')
	c = db.cursor()

	# get the last row ID#
	c.execute('SELECT * FROM Ledger ORDER BY ledger_id DESC LIMIT 1')
	result = c.fetchone()
	last_id = result[0]
	logger.debug('Fetched last ID from Ledger: ' + str(last_id))

	# Open the csv file and read each line, then if ledger ID > last_id, import it
	with open(ledgerfile, 'r', newline='') as f:
		r = csv.DictReader(f, delimiter='\t')
		for row in r:
			if int(row['idLedger']) > last_id:
				logger.debug('Reading row: ' + str(row))
				c.execute("""INSERT INTO Ledger (ledger_id, 
					l_date,
					l_member_id,
					l_name, 
					l_skipper,
					l_description,
					l_mwrvol,
					l_clubvol,
					l_billto_id,
					l_fee,
					l_account,
					l_sp_id,
					l_uploaddate
					)
					VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
					""", 
					(
					int(row['idLedger']),
					row['Date'],
					float(row['idMember']),
					row['Name'],
					int(row['Skipper']),
					row['Description'],
					row['MWRVolunteer'],
					row['ClubVolunteer'],
					float(row['idBillTo']),
					float(row['Fee']),
					row['Account'],
					int(row['idSailPlan']),
					row['UploadDate'],)
					)
				logger.debug('Inserted ledger record: ' + str(row['idLedger']))


	# Commit the changes to the db and then close the db
	db.commit()
	db.close()
	return 1


def update_sailplan(sailplanfile):
	db = sqlite3.connect('Sailsheets.db')
	c = db.cursor()

# get the last row ID#
	c.execute('SELECT * FROM SailPlan ORDER BY sp_id DESC LIMIT 1')
	result = c.fetchone()
	last_id = result[0]
	logger.debug('Fetched last ID from Sailplan: ' + str(last_id))

	# Open the csv file and read each line, then if ledger ID > last_id, import it
	with open(sailplanfile, 'r', newline='') as f:
		r = csv.DictReader(f, delimiter='\t')
		for row in r:
			if int(row['idSailPlan']) > last_id:
				logger.debug('Reading row: ' + str(row))
				c.execute("""INSERT INTO SailPlan (sp_id,
					sp_timeout,
					sp_skipper_id,
					sp_sailboat, 
					sp_purpose,
					sp_description,
					sp_estrtntime,
					sp_timein,
					sp_hours,
					sp_feeeach,
					sp_feesdue,
					sp_mwrbilldue,
					sp_billmembers,
					sp_completed
					)
					VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
					""", 
					(int(row['idSailPlan']),
					row['TimeOut'],
					float(row['SkippersNum']),
					row['Sailboat'],
					row['Purpose'],
					row['Description'],
					row['EstReturnTime'],
					row['TimeIn'],
					float(row['HoursUsed']),
					float(row['FeeEach']),
					float(row['NPSCFeesDue']),
					float(row['MWRBill']),
					int(row['BillableMembers']),
					int(row['Completed']),)
					)
				logger.debug('Inserted SailPlan record: ' + str(row['idSailPlan']))

	# Commit the changes to the db and then close the db
	db.commit()
	db.close()
	return 1


def main():
	mywin = Tk()

	mywin.ledgerfile = filedialog.askopenfilename(initialdir='./Backups/2021/2021-08-04_Backup_CSV_Files',
		title='Open ledger.CSV file',
		filetypes=[("CSV Files", "*.csv")]
		)
	
	if mywin.ledgerfile != '':
		Success = update_ledger(mywin.ledgerfile)
		logger.info(mywin.ledgerfile + ' imported to Ledger Table.')
		
	mywin.sailplanfile = filedialog.askopenfilename(initialdir='./Backups/2021/2021-08-04_Backup_CSV_Files',
		title='Open sailplan.CSV file',
		filetypes=[("CSV Files", "*.csv")]
		)
	
	if mywin.sailplanfile != '':
		Success = update_sailplan(mywin.sailplanfile)
		logger.info(mywin.sailplanfile + ' imported to Sailplan Table.')
	

if __name__ == '__main__':
    main()