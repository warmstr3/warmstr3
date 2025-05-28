# Import Libaries

import sys
sys.path.append(r'C:\Program Files (x86)\PIPC\AF\PublicAssemblies\4.0') 
import clr
clr.AddReference('OSIsoft.AFSDK')

from OSIsoft.AF import *
from OSIsoft.AF.PI import *
from OSIsoft.AF.Asset import *
from OSIsoft.AF.Data import *
from OSIsoft.AF.Time import *

import PIconnect as PI
from PIconnect.PIConsts  import SummaryType

'''doesn't work
#PI.load_SDK()

with PI.AFDatabase() as database:
    print(database.server_name)
'''    
# Connect to PI Server

pi_server = PIServers()[0]  # Replace with your server name
#pi_server.Connect()

# Get the tag/PI Point
print(pi_server.Name)
pi_point = PIPoint.FindPIPoint(pi_server, "*121288*")  # Replace with tag
#points = pi_server.search("*121288*        MW.MV")
for point in points:
    # Get current value
    value = point.CurrentValue

    # Print value and quality info
    print(f"Value: {value.Value}")
    print(f"Timestamp: {value.Timestamp}")
    print(f"Status: {value.Status}")     # AFValueStatus enum (e.g., Good, Bad)
    print(f"IsGood: {value.IsGood}")     # Boolean
    print(f"Substatus: {value.Substatus}")  # More detail if needed

    
with PI.AFDatabase() as database:
    key = next(iter(database.children))
    element = database.children[key]
    attribute = next(iter(element.attributes.values()))
    data = attribute.summary('*-14d', '*', SummaryType.MAXIMUM | SummaryType.MINIMUM)
    print(data)