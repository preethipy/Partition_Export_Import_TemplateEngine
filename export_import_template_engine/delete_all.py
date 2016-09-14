'''
Created on Apr 13, 2016

@author: sowmya
'''
from utils.wsautils import *

session= session_startup(host='9.12.38.77')
cpc_uri = list_cpcs(session)[0]['object-uri']
part = session.get(cpc_uri+'/partitions')
print part

for partition in part.body['partitions']:
    print session.delete(partition['object-uri'])
