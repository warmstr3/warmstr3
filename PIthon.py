
import sys
sys.path.append(r'C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0') 
import clr
clr.AddReference('OSIsoft.AFSDK')

from OSIsoft.AF import *
from OSIsoft.AF.PI import *
from OSIsoft.AF.Asset import *
from OSIsoft.AF.Data import *
from OSIsoft.AF.Time import *
from OSIsoft.AF.Search import *

def connect_to_Server(serverName):
    piServers = PIServers()
    global piServer
    piServer = piServers[serverName]
    piServer.Connect(False)

def get_tag_snapshot(tagname):
    tag = PIPoint.FindPIPoint(piServer, tagname)
    lastData = tag.Snapshot()
    return lastData.Value, lastData.Timestamp    
    
'''  
def get_tag_quaity(tagname):
    tag = PIPoint.FindPIPoint(piServer, tagname)
    lastData = tag.Snapshot()
    return lastData.Value.  
'''