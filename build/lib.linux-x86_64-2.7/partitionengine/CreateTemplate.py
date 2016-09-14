
import ast
import json
import os
from utils.wsautils import *


roce_nic_writable_properties = ['description','device-number','name','network-adapter-port-uri']
vfn_writable_properties = ['description','device-number','name','adapter-uri']
vs_nic_writable_properties = ['description','device-number','name','virtual-switch-uri']
writable_properties = [u'ifl-processing-weight-capped', u'minimum-cp-processing-weight',  u'maximum-ifl-processing-weight', u'access-problem-state-counter-set', u'ifl-processors',  u'cp-absolute-processor-capping-value',  u'reserve-resources', u'maximum-memory', u'boot-timeout', u'boot-os-specific-parameters',  u'processor-management-enabled', u'boot-device', u'access-basic-sampling', u'cp-absolute-processor-capping',  u'boot-record-lba', u'permit-cross-partition-commands', u'acceptable-status', u'maximum-cp-processing-weight', u'minimum-ifl-processing-weight',   u'access-global-performance-data', u'cp-processing-weight-capped', u'permit-aes-key-import-functions',  u'ifl-absolute-processor-capping-value', u'initial-ifl-processing-weight', u'access-extended-counter-set',  u'initial-cp-processing-weight', u'access-crypto-activity-counter-set', u'initial-memory', u'access-basic-counter-set', u'name', u'boot-configuration-selector', u'description', u'cp-processors',  u'access-diagnostic-sampling',u'permit-des-key-import-functions', u'processor-mode',u'ifl-absolute-processor-capping', u'access-coprocessor-group-set']
hba_writable_properties = ['description','device-number','name','adapter-port-uri']
boot_device = {'storage-adapter':['boot-logical-unit-number','boot-world-wide-port-name','boot-storage-device'],'network-adapter':['boot-network-device'],'ftp':['boot-ftp-host','boot-ftp-insfile','boot-ftp-password','boot-ftp-username'],'iso-image':['boot-iso-image-name','boot-iso-ins-file'],'removable-media':['boot-removable-media', 'boot-removable-media-type']}
global nic_device_uri
global hba_device_uri
    
class Object:
    def to_JSON(self):
        return json.dumps(self, default=lambda o: o.__dict__, 
            sort_keys=True, indent=4)
class Payload(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)
        
        
def getNicList(session,ob,ob1):
    logging.info('->getNicList')
    nic_list = []
    global nic_device_uri
    for nic in getattr(ob,'nic-uris'):
        logging.debug(str(nic))
        response = session.get(nic)
        
        logging.debug(str(response.body))
        nic_ob1= Payload(json.dumps(response.body))
        nic_ob = Object()
        for key in nic_ob1.__dict__.keys():
            if response.body['type'] == 'roce':
                if key in roce_nic_writable_properties:
                    logging.debug(str(getattr(nic_ob1,key)))
                    setattr(nic_ob,key,getattr(nic_ob1,key))
            else:
                #print key
                if key in vs_nic_writable_properties:
                    setattr(nic_ob,key,getattr(nic_ob1,key))
            if key == 'element-uri':
                if getattr(ob, 'boot-device') == 'network-adapter' and getattr(nic_ob1, key) == nic_device_uri:
                    setattr(ob1, 'nic-boot-device-number', getattr(nic_ob1, 'device-number')) 
        nic_list.append(nic_ob)
        
        logging.debug(str(nic_list));
        logging.info('<-getNicList')
    return nic_list 

def getHbaList(session,ob,ob1):
    logging.info('->getHbaList')
    hba_list = []
    global hba_device_uri
    for hba in getattr(ob,'hba-uris'):
        response = session.get(hba)
        hba_ob = Object()
        hba_ob1= Payload(json.dumps(response.body))
        for key in hba_ob1.__dict__.keys():
            if key in hba_writable_properties:
                setattr(hba_ob,key,getattr(hba_ob1,key))
            if key == 'element-uri':
                if getattr(ob, 'boot-device') == 'storage-adapter' and getattr(hba_ob1, key) == hba_device_uri:
                    setattr(ob1, 'hba-boot-device-number', getattr(hba_ob1, 'device-number')) 
        hba_list.append(hba_ob)
    logging.info('<-getHbaList')
    return hba_list 

def getVfnList(session,ob):
    logging.info('->getVfnList')
    vfn_list = []
    for vfn in getattr(ob,'virtual-function-uris'):
        response = session.get(vfn)
        vfn_ob = Object()
        vfn_ob1= Payload(json.dumps(response.body))
        for key in vfn_ob1.__dict__.keys():
            if key in vfn_writable_properties:
                setattr(vfn_ob,key,getattr(vfn_ob1,key))
    
        vfn_list.append(vfn_ob)
    logging.info('<-getVfnList')
    return vfn_list 

def setBootDevice(ob,ob1):
    logging.info('->setBootDevice')
    global hba_device_uri
    global nic_device_uri
    if getattr(ob, 'boot-device') == 'storage-adapter':
        hba_device_uri = getattr(ob, 'boot-storage-device')
            
    if getattr(ob, 'boot-device') == 'network-adapter':
        nic_device_uri = getattr(ob, 'boot-network-device')
           
    if getattr(ob, 'boot-device') in boot_device.keys():
        for boot_property in boot_device[getattr(ob, 'boot-device')]:
            setattr(ob1,boot_property,getattr(ob, boot_property))
    logging.info('<-setBootDevice')
    return
                
def getPartitionTemplate(session,inv_response,partition_list):
    logging.info('Retriving the partition info and loading into template....')
    logging.info('->getPartitionTemplate')
    ob1 = Object()
    ob = Payload(json.dumps(inv_response))
    for key in ob.__dict__.keys():
        if key in writable_properties:
            setattr(ob1,key,getattr(ob,key))
        if key == 'crypto-configuration':
            setattr(ob1,'cryptos',getattr(ob,key))
    setBootDevice(ob, ob1)
    nic_list = getNicList(session,ob,ob1)
    hba_list = getHbaList(session, ob,ob1)
    vfn_list = getVfnList(session, ob)
    setattr(ob1,'nics',nic_list)
    setattr(ob1,'virtual-functions',vfn_list)
    setattr(ob1,'hbas',hba_list)
    partition_list.append(ob1)
    logging.info('<-getPartitionTemplate')
    return partition_list
        
def createTemplate(session,inv_response,cpc_name,partition_name = None):
    logging.info('->createTemplate')
    logging.debug(str(inv_response))
    partition_list = []
    complete = Object()
    for partition in inv_response:
            response = session.get(partition['object-uri'])
            complete = Object()
            partition_list = getPartitionTemplate(session, response.body, partition_list) 
            
    setattr(complete,'partition',partition_list)  
    if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/templates'):
        os.mkdir(os.path.dirname(os.path.abspath(__file__))+'/templates')
    if partition_name == None:
        if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/templates/base_'+cpc_name):
            os.mkdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates/base_'+cpc_name))
        file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates/base_'+cpc_name,'base_template.json')
    else:
        if not os.path.exists(os.path.dirname(os.path.abspath(__file__))+'/templates/cpc_'+cpc_name):
            os.mkdir(os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates/cpc_'+cpc_name))
        file_name = os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates/cpc_'+cpc_name,partition_name+'_template.json')
    file = open(file_name,'w+')        
    file.write(complete.to_JSON())
    file.close()
    logging.info('template created successfully...')
    logging.info('<-createTemplate')
    
    return file_name
