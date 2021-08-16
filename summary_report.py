import logging
import sqlite3
import datetime as dt
from pathlib import Path
from datetime import date
import csv

# Set up the logging system
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:%(name)s:%(levelname)s:%(message)s')
file_handler = logging.FileHandler(__name__ + '.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def ReportSummary():
    d = dt.datetime.today()
    mymonth = d.month
    if mymonth/10 < 1: rpt_month = '0' + str(mymonth)
    else: rpt_month = str(mymonth)
    myyear = d.year
    rpt_yr_mo = str(myyear) + '-' + rpt_month
    print(rpt_yr_mo)

    month_list = ['January', 'February', 'March',
                    'April', 'May', 'June', 
                    'July', 'August', 'September',
                    'October', 'November', 'December']

    reportpath = './Reports/' + str(d.year)
    p = Path(reportpath) 
    
    if not Path(reportpath).exists():
        p.mkdir(parents=True)

    db = sqlite3.connect('Sailsheets.db')
    c = db.cursor()

    c.execute("""SELECT strftime('%Y', sp_timeout) as s_year, strftime('%m', sp_timeout) as s_month, 
        Boats.boat_class AS boatclass, round(sum(SailPlan.sp_hours),1) AS hours
        FROM SailPlan 
        JOIN Boats on SailPlan.sp_sailboat=Boats.boat_Name
        WHERE SailPlan.sp_sailboat!='Skyline' and strftime('%Y-%m', sp_timeout) != :rpt_date
        GROUP BY s_year, s_month, boatclass
        ORDER BY s_year, s_month, boatclass
        """, {'rpt_date': rpt_yr_mo,})

    logger.info('Fetched data for MWR Boat Usage History.')

    usagetable = c.fetchall()

    db.commit()
    db.close()

    myreportname = reportpath + '/' + rpt_month + '-' + month_list[mymonth-1] + ' ' + str(d.year) + ' History - MWR' + '.csv'

    with open(myreportname, 'w', newline='') as f:
        w = csv.writer(f, dialect='excel')
        w.writerow(["Report period: ", month_list[mymonth-1], myyear])
        w.writerow([" "])
        w.writerow(["Year", "Month", "Hours - A/B", "Hours - C", "Hours - D", "Total Hours"])
        w.writerow([" "])
        
        # Baseline the groupings
        #
        firstrecord = usagetable[0]
        r_year = int(firstrecord[0])
        r_month = int(firstrecord[1])
        r_class = firstrecord[2]
        
        # Set the totals to zero 
        #
        hrs_A_total = 0
        hrs_A_grand_total = 0
        hrs_C_total = 0
        hrs_C_grand_total = 0
        hrs_D_total = 0
        hrs_D_grand_total = 0
        hrs_Month_total = 0
        hrs_Month_grand_total = 0
        hrs_year_total = 0
        hrs_grand_total = 0

        revenue_NPSC_total = 0
        revenue_NPSC_grand_total = 0
        revenue_MWR_total = 0
        revenue_MWR_grand_total = 0
        revenue_grand_total = 0
        
        """
        Record tuple: [s_year, s_month, boatclass, hours]
        """
        for record in usagetable:
            if int(record[0]) == r_year and int(record[1]) == r_month:
                if str(record[2]) == 'A/B': 
                    hrs_A_total += float(record[3])
                    hrs_Month_total += float(record[3])
                elif str(record[2]) == 'C': 
                    hrs_C_total += float(record[3])
                    hrs_Month_total += float(record[3])
                elif str(record[2]) == 'D':
                    hrs_D_total += float(record[3])
                    hrs_Month_total += float(record[3])
                myrow = ([str(r_year), month_list[r_month-1], 
                    str(round(hrs_A_total,1)),
                    str(round(hrs_C_total,1)),
                    str(round(hrs_D_total,1)),
                    str(round(hrs_Month_total,1))])
            elif int(record[0]) == r_year and int(record[1]) != r_month:
                w.writerow(myrow)
                hrs_A_grand_total += hrs_A_total
                hrs_C_grand_total += hrs_C_total
                hrs_D_grand_total += hrs_D_total
                hrs_Month_grand_total += hrs_Month_total
                hrs_year_total += hrs_Month_grand_total
                hrs_A_total = 0
                hrs_C_total = 0
                hrs_D_total = 0
                hrs_Month_total = 0
                hrs_Month_grand_total = 0
                r_month = int(record[1])

                if str(record[2]) == 'A/B': 
                    hrs_A_total += float(record[3])
                    hrs_Month_total += float(record[3])
                elif str(record[2]) == 'C': 
                    hrs_C_total += float(record[3])
                    hrs_Month_total += float(record[3])
                elif str(record[2]) == 'D':
                    hrs_D_total += float(record[3])
                    hrs_Month_total += float(record[3])
                myrow = ([str(r_year), month_list[r_month-1], 
                    str(round(hrs_A_total,1)),
                    str(round(hrs_C_total,1)),
                    str(round(hrs_D_total,1)),
                    str(round(hrs_Month_total,1))])
            elif int(record[0]) != r_year:
                w.writerow(myrow)
                hrs_A_grand_total += hrs_A_total
                hrs_C_grand_total += hrs_C_total
                hrs_D_grand_total += hrs_D_total
                hrs_Month_grand_total += hrs_Month_total
                hrs_year_total += hrs_Month_grand_total
                hrs_grand_total += hrs_year_total
                w.writerow([" ", " ", " ", " ", " ", "Yearly Total:", str(round(hrs_year_total, 1))])
                w.writerow([" "])

                hrs_A_total = 0
                hrs_C_total = 0
                hrs_D_total = 0
                hrs_Month_total = 0
                hrs_Month_grand_total = 0
                hrs_year_total = 0

                r_month = int(record[1])
                r_year = int(record[0])

                if str(record[2]) == 'A/B': 
                    hrs_A_total += float(record[3])
                    hrs_Month_total += float(record[3])
                elif str(record[2]) == 'C': 
                    hrs_C_total += float(record[3])
                    hrs_Month_total += float(record[3])
                elif str(record[2]) == 'D':
                    hrs_D_total += float(record[3])
                    hrs_Month_total += float(record[3])
                myrow = ([str(r_year), month_list[r_month-1], 
                    str(round(hrs_A_total,1)),
                    str(round(hrs_C_total,1)),
                    str(round(hrs_D_total,1)),
                    str(round(hrs_Month_total,1))])
            
        w.writerow(myrow)
        w.writerow([" "])
        w.writerow([" ", " ", " ", " ", " ", " ", "Grand Total:", str(round(hrs_grand_total, 1))])
        w.writerow([" "])
    

if __name__ == '__main__':
    ReportSummary()
