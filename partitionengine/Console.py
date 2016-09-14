from getpass import *

#from babel.messages.catalog import Catalog

from CreateTemplate import *
from CreateTemplatePartition import *
from utils.wsautils import *
import ConfigParser


session = None


CONFIG_FILE=".saved-settings"
config = ConfigParser.RawConfigParser()


def print_helper(print_string=None, operationFailed=False, exception=None):
    string_out = ''
    if (operationFailed):
        string_out += ("\n" + "*"*100)
        string_out += ("\n**********************************Operation Failed**************************************************")
        
    else:
        string_out += ("\n" + "*"*100)
    string_out += ("\n" + print_string)
    string_out += ("\n" + "*"*100)
    print string_out
    logging.debug(string_out)
    if not (exception == None):
        logging.debug("Failure Reason:")
        logging.debug(exception)
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback_details = {
                         'filename': exc_traceback.tb_frame.f_code.co_filename,
                         'lineno'  : exc_traceback.tb_lineno,
                         'name'    : exc_traceback.tb_frame.f_code.co_name,
                         'type'    : exc_type.__name__,
                         'message' : exc_value.message, # or see traceback._some_str()
                        }
        del(exc_type, exc_value, exc_traceback)
        logging.debug(traceback.format_exc())
        
    return
        





finalSelectedOption = 0
def option_choser(queryString='Choose from Index',option_title='', indexLength=0,chosenOption = 0):
    logging.info('option_choser method invoked') 
    if chosenOption < 1 or chosenOption > indexLength:
        try:
            chosenOption = int(user_input('\n'+queryString, 'OPTIONS', option_title))#raw_input('\n' + queryString.ljust(30) + ':'))         
        except:
            print("Invalid Value!!! ")
        option_choser(queryString,option_title,indexLength,chosenOption)
    else:
        global finalSelectedOption
        finalSelectedOption = chosenOption   
    logging.debug("chosen option: " + str(chosenOption))
    return finalSelectedOption

def createPartitionIteratively(temp_name='', no_of_partitions=0, cpc_uri=''):
    logging.info('-> createPartitionIteratively for the templatename ' + temp_name + " number of Partitions: " + str(no_of_partitions) + " CPC URI: " + cpc_uri)
    partionList=dict();
    for num in range(0, no_of_partitions):
        print_helper("Creating Partition " + str(num+1), False)
        try:
            partition_unique_name,part_uri=createTemplatePartition(temp_name, session, cpc_uri, ''.join(random.choice(string.ascii_uppercase + string.digits) for num in range(4)))
        except Exception as ex:
            print_helper('Partition Creation failed while creating partition number' + num , True, str(ex))
        except:
            print_helper('Partition Creation failed while creating partition number' + num , True, str(sys.exc_info()[:2]))
        #partionList[partition_unique_name] = part_uri
    logging.info('<- createPartitionIteratively')
    return partionList

def createPartitionFromTemplate(cpc_name='', cpc_uri=''):
    logging.info('->createPartitionFromTemplate')
    partitionStatus=''
    try:
        template_dir_name = os.path.join(os.path.dirname(os.path.abspath(__file__)) , 'templates/cpc_' + cpc_name);
        logging.debug(template_dir_name)
        if not(os.path.isdir(template_dir_name)):
            print_helper("No Template File exists")
            return
        template_files = os.listdir(template_dir_name)
        logging.debug('template_files ' + str(template_files))
        
        print("\nChoose one of the below Templates:\n")
        
        for index in range(0, len(template_files)):
            print index + 1, '. '.ljust(10), os.path.splitext(template_files[index])[0]
        selected_template = option_choser("Select a template available to create partition:","TEMPLATE" ,len(template_files))
        
        temp_name = template_files[selected_template - 1]
        logging.debug("Selected Template..." + temp_name)
        
        no_of_partitions = option_choser('Enter the number of partitions to be created ',"PARTITIONCOUNT", 100)
        logging.debug('no_of_partitions' + str(no_of_partitions))
        
        template_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/cpc_' + cpc_name, temp_name)
        logging.debug('template_name ' + template_name)
        
        if not(os.path.isfile(template_name)):
            raise IOError("File not found: " + template_name)
        partitionList=createPartitionIteratively(template_name, no_of_partitions, cpc_uri)
        partitionStatus = 'Partition Created Successfully from template\n'
        for part in partitionList.keys():
        
            partitionStatus+= 'Partition Name: '+part+'\n'
            partitionStatus+= 'Partition URI: ' +partitionList[part]+'\n'
    except:
        print_helper('Partition Creation failed to create from given Template', True, str(sys.exc_info()[:2]))
    logging.info('<-createPartitionFromTemplate')    
    
    print_helper(partitionStatus, False)
    
    print_helper("Process Completed", False)    
    return

def createPartitionFromPartition(cpc_name='', cpc_uri=''):
    logging.info('->createPartitionFromPartition')
    try:
        part = session.get(cpc_uri + '/partitions')
        partitions = part.body['partitions']
        for  index in range(0, len(partitions)):
            print index + 1, '  ', partitions[index]['name']
        partition_option = option_choser('Select partition by index','PARTITION_INDEX', len(partitions))
        
        partition_name = partitions[partition_option - 1]['name']
        no_of_partitions = option_choser('Enter the number of partitions to be created ','NUMPARTS', 100)
        logging.debug('no_of_partitions' + str(no_of_partitions))
        
        p = progress_bar_loading()
        p.configure("Fetching Partition Inventory...")
        p.start() 
                
        temp_name = createTemplate(session,[partitions[partition_option - 1]], cpc_name, partition_name)
        logging.debug('template_name '+ temp_name)
        
        time.sleep(1)
        p.stop()      
        
        time.sleep(2)
        
        if not(os.path.isfile(temp_name)):
            raise IOError("File not found: " + temp_name)
        
        createPartitionIteratively(temp_name, no_of_partitions, cpc_uri)
    except:
        print_helper('Partition Creation failed to create from chosen partition ' + partition_name, True, str(sys.exc_info()[:2]))
        time.sleep(1)
        p.stop() 
    logging.info('<-createPartitionFromPartition')
    
    print_helper("Successfully Completed", False)    
    return

def exportPartition(cpc_name="",cpc_uri=""):
    logging.info('->exportPartition')
    try:
        part = session.get(cpc_uri + '/partitions')
        partitions = part.body['partitions']
	p = progress_bar_loading()
        p.configure("Fetching Partition Inventory...")
        p.start()
        
	temp_name = createTemplate(session,partitions, cpc_name)
        #p = progress_bar_loading()
        #p.configure("Fetching Partition Inventory...")
        #p.start() 
        #time.sleep(1)
        p.stop()
        time.sleep(2)   
        logging.debug('template_name '+ temp_name)
        
        if not(os.path.isfile(temp_name)):
            raise IOError("Partition Inventory is not exported to the file " + temp_name)
    except:
        print_helper('Partition Export failed', True, str(sys.exc_info()[:2]))
        time.sleep(1)
        p.stop() 
    logging.info('<-exportPartition')
    
    print_helper("Successfully Completed", False)    
    return

def importPartition(cpc_name='', cpc_uri=''):
    logging.info('->importPartition')
    try:
        template_name = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/base_' + cpc_name, 'base_template.json')
        logging.debug('template_name '+ template_name)
        if not(os.path.isfile(template_name)):
            raise IOError("File not found: " + template_name)
        createTemplatePartition(template_name, session, cpc_uri)
    except:
        print_helper("Sorry! There is no backup inventory for the CPC selected", True, str(sys.exc_info()[:2]))
    logging.info('<-importPartition')
    
    print_helper("Successfully Completed", False)    
    return

def readConfig():
    config.read('savedsettings.cfg')
    return config

def updateConfig(params=None):
    with open('savedsettings.cfg', 'wb') as configfile:
        config.write(configfile)
    return

def user_input(inputStr='',section='',parameter='', password=False):
    config = readConfig()
    
    userinput=''
    
    try: 
        value=config.get(section, parameter)
    except ConfigParser.NoSectionError:
        if not section == '':
            config.add_section(section)
        value = ''
    except:
        value = ''    
    if password:
        userinput=getpass(inputStr.ljust(15) + ':')        
    else:
        userinput=raw_input(inputStr +' ['+ value + ']'.ljust(15) + ':')
        
    if not userinput == '':
        value = userinput
       
    if not parameter=='':
        config.set(section,parameter,value)
    updateConfig()
    return value 



def main():
    initializeLogging()
    logging.info('Starting the PartitionManagementTemplating Tool')
    print "*"*100
    print "Capture and replay partition creation".center(100)
    print "*"*100   
    
            
    hmc_ip = user_input('Enter HMC IP', 'BASE_PARAMS', 'HMC_IP')#raw_input('Enter HMC IP ['+ config.get('BASE_PARAMS', 'HMC_IP') + ']'.ljust(30) + ':')
    hmc_user = user_input('Enter Username', 'BASE_PARAMS', 'HMC_USER')#raw_input('Enter Username ['+ config.get('BASE_PARAMS', 'HMC_USER') + ']'.ljust(30) + ':')
    hmc_password = user_input('Enter Password','','',True)#('Enter Password'.ljust(30) + ':')
    
    #hmc_ip = '9.152.151.49'
    #hmc_user = 'pedebug'
    #hmc_password = 'password'
    # print hmc_password
    logging.debug('hmc_ip: '+hmc_ip+' hmc_user '+hmc_user+' hmc_password '+hmc_password)
    cpcs = []
    global session
    try:
        
        p = progress_bar_loading()
        p.configure("Establishing session")
        p.start()     
        session = session_startup(host=hmc_ip, user=hmc_user, pwd=hmc_password)
        logging.debug("Printing the session details... /n"+ str(session))
        time.sleep(2)
        p.stop()
        
        p = progress_bar_loading()
        p.configure("Fetching CPC List")
        p.start()
        cpcs = list_cpcs(session)
        p.stop()        
        time.sleep(2)
        
        logging.debug("Printing the cpcs... /n"+ str(cpcs))
    except ApiFatalException as ex:
        print_helper("Sorry! Session could not be established. Please verify the IP, HMC Username/Password", True)
        time.sleep(1)
        p.stop() 
        return
    
    print "****************************************************************************************************"
    if len(cpcs) > 0:        
        print "List of CPCs available"
    else:
        print_helper("No CPCs managed by the HMC!!!")
        return
    
    
    for  index in range(0, len(cpcs)):
        print index + 1, '  ', cpcs[index]['name']
    
    try:
        cpc_option = option_choser("Select cpc by index from the given list",'CPCSEL', len(cpcs))
    
        cpc_uri = cpcs[cpc_option - 1]['object-uri']
        cpc_name = cpcs[cpc_option - 1]['name']
        print_helper('CPC ' + cpc_name + ' is selected')
        print("Choose one of the below options:")
        options = '\n1.  create n partitions from existing templates?\n2.  create a partition based on another partition?\n3.  Export Partition Inventory?\n4.  Import Partition Inventory? '
        print options
        selected_option = option_choser('Select an option by index','FLAVOR', 4)
    
    
        if selected_option == 1:
            createPartitionFromTemplate(cpc_name, cpc_uri)
            
        elif selected_option == 2:
            createPartitionFromPartition(cpc_name, cpc_uri)
            
        elif selected_option == 3:
            exportPartition(cpc_name, cpc_uri)
            
        if selected_option == 4:
            importPartition(cpc_name, cpc_uri)
    except:
        print_helper('Process Failed ', True, str(sys.exc_info()[:2]))
   
main()
