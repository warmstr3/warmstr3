
# Import Libaries
import adodbapi
import sys, os
import csv
import matplotlib.pyplot as plt
import datetime

# Define Variables
timestep= " 15m "
output = {}
today=str()
now = datetime.datetime.now()
today=now.strftime("%Y-%m-%d")

# Configure PI OLEDB Connection
server = "10.57.8.229" # Corp PI
database = "pipoint"
time_out = 30
connstr = "Provider=PIOLEDB.1;Data Source="+server+";Initial Catalog="+database+";Integrated Security=SSPI;Persist Security Info=False"
conn = adodbapi.connect(connstr,timeout=time_out)
cursor = conn.cursor()


# Prints a list of 3ph station regs where the 1hr average voltage is outside of the BW            
#################################################

csvfile=open('StuckRegs_'+today+'.csv','w',newline='')
file=csv.writer(csvfile)
file.writerow (["3ph Regs"])
file.writerow (["bc_tag","bc","bw_tag","bw","1hr avg Voltage"])
print("bc_tag                 ","  BC   ","bw_tag                "," BW   ","                ","1hr avg Voltage")
#3ph regs
cursor.execute("SELECT tag,time, value FROM piarchive..piavg WHERE tag LIKE '%.ppv' AND value != 'None' AND time BETWEEN ' -15m ' AND ' * ' AND timestep = '" + timestep + "'")
for row in cursor.fetchall():
        ppv=float(row[2])
        reg=row[0][:-3]
        bw_tag=reg+"FBW3"
        bc_tag=reg+"FBC3"
        ppv_tag=reg+"PPV"
        cursor.execute("SELECT tag, time, value FROM piarchive..piavg WHERE tag = '"+bc_tag+"' AND time BETWEEN ' -15m ' AND ' * ' AND timestep = '" + timestep + "'")
        for row in cursor.fetchall():
                bc=float(row[2])
                cursor.execute("SELECT tag, time, value FROM piarchive..piavg WHERE tag = '"+bw_tag+"' AND time BETWEEN ' -15m ' AND ' * ' AND timestep = '" + timestep + "'")
                for row in cursor.fetchall():
                        bw=float(row[2])
                        if (ppv > bc + bw/2):
                                if ppv_tag in output:
                                        continue
                                else:
                                        output[ppv_tag] =  ppv
                                        file.writerow ([bc_tag,bc,bw_tag,bw,ppv])
                                        print(bc_tag,"=",bc," ",bw_tag,"=",bw," CTRL Voltage=  ",ppv)
                        elif (ppv < bc-bw/2):
                                if ppv_tag in output:
                                       continue
                                else:
                                        output[ppv_tag] =  ppv
                                        file.writerow ([bc_tag,bc,bw_tag,bw, ppv])
                                        print(bc_tag,"=",bc," ",bw_tag,"=",bw," CTRL Voltage=  ",ppv)

        
 
csvfile.close()               
        
#print(output)


 
