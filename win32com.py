import win32com.client
from win32com.client.dynamic import Dispatch
import time 
 

conn = win32com.client.Dispatch(r'ADODB.Connection')    
DSN = "Provider=PIOLEDB.1;Data Source=10.57.8.229;Integrated Security=SSPI;Persist Security Info=False"
conn.Open(DSN)    
 
recordset = win32com.client.Dispatch(r'ADODB.Recordset')    
recordset.Cursorlocation = 3
recordset.Open("select tag, value from pisnapshot", conn)
 
if recordset.RecordCount > 0:    
    print("You have a total of {0} tags, and these are their values\n".format( recordset.RecordCount ))   
    print("Tag, Snapshot Value")
    print("---------------------\n")
    while not recordset.EOF:
       source = {field.Name : field.value for field in recordset.Fields}
       print("{tag}, {value}".format(**source))  
       recordset.MoveNext()
else:    
    print("There are no tags")   
conn.Close()
 
 
