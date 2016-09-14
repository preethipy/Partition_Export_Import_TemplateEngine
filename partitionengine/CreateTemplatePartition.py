
import ast
import json
import random

from utils.wsautils import *

import sys
import time
import threading





def remove(body,keys_list):
    for key in keys_list:
        if key in body.keys():
            del body[key]

def createTemplatePartition(temp_filename,session,cpc,partition_unique_name=None):
    logging.info('==>>################# createTemplatePartition invoked#################')
    logging.debug('Template file name: '+ temp_filename)
    logging.debug('cpc uri: '+ cpc)
    logging.debug('Partition unique name: '+ str(partition_unique_name))
    temp_file = open(temp_filename,'r')
    json_text = temp_file.read()
    ip = json.loads((json_text))
    ip_body = ip['partition']
    p = progress_bar_loading()
    try:
        for partition in ip_body:
            body = {'processor-mode':partition['processor-mode'], 'initial-memory':partition['initial-memory'],'maximum-memory':partition['maximum-memory']}
            if partition_unique_name != None:
                body.update({'name':partition['name']+'_'+str(partition_unique_name)})
            else:
                body.update({'name':partition['name']})
            if partition['cp-processors'] != 0:
                body.update({'cp-processors':partition['cp-processors']})
            else:
                body.update({'ifl-processors':partition['ifl-processors']})
                
            p = progress_bar_loading()
            p.configure("Creating Partition")
            p.start()
            response = session.post(cpc+'/partitions',json.dumps(body))
            time.sleep(1)
            p.stop()
            time.sleep(2)
            logging.debug("Respose from partitions Post request" + str(response)) 
            
            
            part_uri = response.body['object-uri']
            logging.debug("Partition URI from newly created partition" + part_uri)
            
            
            p = progress_bar_loading()
            p.configure("Creating VNics")
            p.start()   
            for nic in partition['nics']:
                logging.info("Iterating through nic URIS")            
                response = session.post(part_uri+'/nics',json.dumps(nic))            
                logging.debug("Respose from nics Post request" + str(response)) 
                
                if (partition['boot-device'] == 'network-adapter') and (nic['device-number'] == partition['nic-boot-device-number']) :            
                    nicRes = response.body['element-uri']
                    partition['boot-network-device'] = nicRes
            time.sleep(1)
            p.stop()
            time.sleep(2)
             
             
            p = progress_bar_loading()
            p.configure("Creating HBAs")
            p.start()       
            for hba in partition['hbas']:
                logging.info("Iterating through hba URIS")
                
                response = session.post(part_uri+'/hbas',json.dumps(hba))
                
                logging.debug("Respose from hbas Post request" + str(response)) 
                
                if (partition['boot-device'] == 'storage-adapter') and (hba['device-number'] == partition['hba-boot-device-number']) :            
                    hbaRes = response.body['element-uri']
                    partition['boot-storage-device'] = hbaRes
                 
            time.sleep(1)
            p.stop()
            time.sleep(2)
                
            
            p = progress_bar_loading()
            p.configure("Creating VirtualFunctions")
            p.start()       
            for vfn in partition['virtual-functions']:
                logging.info("Iterating through virtual-functions URIS")
                
                response = session.post(part_uri+'/virtual-functions',json.dumps(vfn))
                
                
                logging.debug("Respose from virtual-functions Post request" + str(response))
            time.sleep(1)
            p.stop()
            time.sleep(2)
            
            p = progress_bar_loading()
            p.configure("Configuring Cryptos")
            p.start()
            if partition['cryptos'] != None:
                logging.info("Adding crypto configurations")
                
                response = session.post(part_uri+'/operations/increase-crypto-configuration',json.dumps(partition['cryptos']))
            time.sleep(1)
            p.stop()
            time.sleep(2)
                
            remove(partition,['nics','hbas','virtual-functions','name','hba-boot-device-number','nic-boot-device-number','cryptos'])
            logging.debug("Removed unwanted attributes")
            
            p = progress_bar_loading()
            p.configure("\nUpdating Partition Properties")        
            p.start()
            response = session.post(part_uri,json.dumps(partition))        
            time.sleep(1)
            p.stop()
            time.sleep(2)
            logging.debug("Response from Update Partition request"+ str(response))
            
            
            p = progress_bar_loading()
            p.configure("Retrieve and Verify Partition Properties")        
            p.start()
            response = session.get(part_uri)            
            time.sleep(1)
            p.stop()
            time.sleep(2)
            
            if(response.status == 200):
                sys.stdout.write("Partition: " + response.body['name']+" Created Successfully" )
            logging.debug("Partition Properties"+ str(response))
    except:
        time.sleep(1)
        p.stop()
        raise
        
    logging.info('<<=########## createTemplatePartition invoked#########')
    return partition_unique_name,part_uri