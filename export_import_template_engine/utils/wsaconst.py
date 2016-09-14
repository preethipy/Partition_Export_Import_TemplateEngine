
WSA_CONST_VERSION = "1.1"  # Current version of the API constants

# Make a copy of the input array.  This copy contains lowercase versions of each
# array element that is not already lowercase.
def make_lowercase_copy(tokens):
    lower_tokens = []
    for token in tokens:
        lower_token = token.lower()
        #print "token: %s (%s)" % (token, lower_token)
        if lower_token not in tokens:
            lower_tokens.append(lower_token)
        #print "lower_tokens(%s): %s" % (len(lower_tokens), lower_tokens)
    return lower_tokens

# ??? FVT regression test framework to-do's
# - Need to add testcase_properties definition to all existing testcases.  Use this template
#   and replace the items in angle brackets with the appropriate strings:
#
#      testcase_properties = {TC_FULL_NAME : get_testcase_full_filename(),
#                             TC_COMPONENT : TC_COMPONENT_<component>,
#                             TC_ID : get_testcase_id(),
#                             TC_TITLE : '<title>',
#                             TC_URI : '<uri>',
#                             TC_MINIMUM_API_VERSION : TC_API_VERSION_<minimum_version>,
#                             TC_SCENARIO_TYPE : TC_SCENARIO_TYPE_<scenario_type>,
#                             TC_EXECUTION_TYPE : TC_EXECUTION_TYPE_<execution_type>,
#                             TC_CAPABILITIES : [<appropriate TC_CAPABILITY_<capability> values, OR empty array>]}
#
# x Consider reworking skeleton.py to follow the above model, so that future automated updates are easier,
#   and as many as possible of these properties can come from the FVT Lotus Notes database. [done]
#   x Consider adding code to the skeleton to fetch the minimum version out of testcase_properties for
#     use in a testcase environment check. [done]
#   x Need to fetch the component, id and title from testcase_properties as well, because they are used
#     in some print statements at the beginning of the testcase execution. [done]
# x Need a proper implementation of is_api_version_at_least(). [done]
# - Should probably add an is_api_version_at_most() method for potential use in the future.
# - Add a check for required testcase properties???  When?  --get-properties?  --check-properties?
#   - The list of required properties would be defined in a constant in wsaconst.py
# x Add support for creating a CSV file of testcases that meet specified criteria? ["done".  Not CSV though.  See runregress.py]
#   - Add --csv-file option to specify the output CSV filename
#   - If testcase meets requirements, *append* a line to the CSV file
#     - If file doesn't exist, create it by writing a header line that defines the columns
#       - column names and order would be defined in a constant in wsaconst.py
#   - Requires caller to erase any leftover CSV file before beginning this run
# x Add an option to runregress.py to specify a top directory to search for testcases to run 
#     and run all it finds that meet the requirements. [done]
#   x The requirements can be specified as a single complex string option which is passed
#     as a bunch of arguments to the testcase.  Maybe something like this:
#        runregress.py --top-dir <dir> --requirements "--component SVM --component VSM --scenario success --execution-type self-checking" [done]


# The name of the variable that defines a testcase's properties.  
# Each testcase must define this variable appropriately.
TESTCASE_PROPERTIES_VARIABLE_NAME = 'testcase_properties'

#############################################################################
# These constants define property names and values that are used to describe
# testcases.  They are intended for use in the definition of the 
# TESTCASE_PROPERTIES_VARIABLE_NAME dictionary in each testcase's source code.
# Some of them can be specified on the command line as testcase requirements.
#############################################################################
# Testcase filename, with full path information
TC_FULL_NAME = 'full_name'

# Testcase ID.  The numeric ID, typically found in the testcase filename, which is of the form:
# comp_id.py, where comp is the component and id is the testcase ID.
TC_ID = 'id'

# Testcase title
TC_TITLE = 'title'

# Primary URI being tested by this testcase
TC_URI = 'uri'

# API versions.  They must be defined in such a way that they can be meaningfully supported by the is_api_version_*() methods.
# Be sure to add any new ones to TC_API_VERSION_LIST.
TC_MINIMUM_API_VERSION = 'min_api_version'
TC_MAXIMUM_API_VERSION = 'max_api_version'
TC_API_VERSION_ZGRYPHON_GA2  = '1.1'
TC_API_VERSION_ZGRYPHON_GA2A = '1.2'
TC_API_VERSION_ZHELIX_GA1    = '1.3'
TC_API_VERSION_ZHELIX_GA2    = '1.4'
TC_API_VERSION_ZHELIX_GA2A   = '1.5'    # LI 1065 - Support for Shutdown and Power-off Tasks
TC_API_VERSION_ZSPHINX_GA1   = '1.6'
TC_API_VERSION_ZSPHINX_GA2   = '1.7'
TC_API_VERSION_ZMIDAS_GA1    = '1.8'
# List of all valid API versions, used for command line validation
TC_API_VERSION_LIST = [TC_API_VERSION_ZGRYPHON_GA2, TC_API_VERSION_ZGRYPHON_GA2A, TC_API_VERSION_ZHELIX_GA1, TC_API_VERSION_ZHELIX_GA2,
                       TC_API_VERSION_ZHELIX_GA2A, TC_API_VERSION_ZSPHINX_GA1, TC_API_VERSION_ZSPHINX_GA2,TC_API_VERSION_ZMIDAS_GA1]

# Testcase capabilities.  These define API/HMC/SE "capabilities" that are tested by certain testcases.
# They can be, for example, MCF bundles, line items, parts of line items, ODTs, MCFs, MCLs, optional facilities, etc...
# Be sure to add any new ones to TC_CAPABILITY_LIST.
TC_CAPABILITIES = 'capabilities'
TESTCASE_CAPABILITIES = TC_CAPABILITIES  # ??? Temp duplicate of TC_CAPABILITIES until FVT API database is updated to use TC_CAPABILITIES
TC_CAPABILITY_ZVM           = 'ZVM'  # This testcase requires a z/VM system
TC_CAPABILITY_IEDN          = 'IEDN'
TC_CAPABILITY_QDIO          = 'QDIO'
TC_CAPABILITY_VSWITCH       = 'VIRTUAL SWITCH'
TC_CAPABILITY_PRSM          = 'PRSM'
TC_CAPABILITY_XHYP          = 'X86'
TC_CAPABILITY_POWERVM       = 'POWER-VM'
#TC_CAPABILITY_BLADEXHYP     = 'X86-BLADE'
#TC_CAPABILITY_BLADEPOWER    = 'POWER-BLADE'
TC_CAPABILITY_BLADEISAOPT   = 'ISAOPT-BLADE'
TC_CAPABILITY_BLADEDPXI50Z  = 'DPXI50Z-BLADE'
TC_CAPABILITY_ZAWARE  = 'ZAWARE'
TC_CAPABILITY_ZBX  = 'ZBX'
TC_CAPABILITY_ZFX  = 'ZFX'
TC_CAPABILITY_ZHYP  = 'ZHYP'
TC_CAPABILITY_ZXN  = 'ZXN' # For zExtension nodes - zFX Mod 001 & zBX Mod 004 nodes
TC_CAPABILITY_ZBXMOD004 = 'ZBXMOD004'
# List of all valid capabilities, used for command line validation
TC_CAPABILITY_LIST = [TC_CAPABILITY_ZVM, TC_CAPABILITY_IEDN, TC_CAPABILITY_QDIO, TC_CAPABILITY_VSWITCH, TC_CAPABILITY_PRSM, TC_CAPABILITY_XHYP, 
                      TC_CAPABILITY_POWERVM, TC_CAPABILITY_BLADEISAOPT, TC_CAPABILITY_BLADEDPXI50Z, TC_CAPABILITY_ZAWARE]
TC_CAPABILITY_LIST.extend(make_lowercase_copy(TC_CAPABILITY_LIST))  # Add lowercase versions as needed, for command line convenience


# Testcase components
# Be sure to add any new ones to TC_COMPONENT_LIST.
TC_COMPONENT = 'component'
TC_COMPONENT_CONS = 'CONS'  #CreateTemplate
TC_COMPONENT_CPC  = 'CPC'   #Central Processor Complex
TC_COMPONENT_CREC = 'CREC'  #Capacity Records
TC_COMPONENT_EAM  = 'EAM'   #Enterprise Availability Management
TC_COMPONENT_EM   = 'EM'    #Energy Management
TC_COMPONENT_EMM  = 'EMM'   #Ensemble Membership Management
TC_COMPONENT_EMF  = 'EMF'   #Ensemble Measurement Facility
TC_COMPONENT_GPRO = 'GPRO'  #Group Profiles
TC_COMPONENT_GRP  = 'GRP'   #Groups
TC_COMPONENT_GS   = 'GS'    #General Services
TC_COMPONENT_HVM  = 'HVM'   #Hypervisor Virtualization Management
TC_COMPONENT_IOM  = 'IOM'   #I/O Configuration Management
TC_COMPONENT_IPRO = 'IPRO'  #Image Activation Profiles
TC_COMPONENT_IS   = 'IS'    #Inventory Service
TC_COMPONENT_LGR  = 'LGR'   #Live Guest Relocation
TC_COMPONENT_LPAR = 'LPAR'  #Logical Partition
TC_COMPONENT_LPRO = 'LPRO'  #Load Activation Profile
TC_COMPONENT_MDM  = 'MDM'   #Monitors Dashboard Metric Groups
TC_COMPONENT_MS   = 'MS'    #Metrics Service
TC_COMPONENT_NVM  = 'NVM'   #Network Virtualization Management
TC_COMPONENT_PPM  = 'PPM'   #Workloads and Performance Management
TC_COMPONENT_RPRO = 'RPRO'  #Reset Activation Profiles
TC_COMPONENT_SEC  = 'SEC'   #Security and User Management
TC_COMPONENT_SVM  = 'SVM'   #Storage Virtualization Management
TC_COMPONENT_VSM  = 'VSM'   #Virtual Server Management
TC_COMPONENT_zBX  = 'zBX'   #zEnterprise Blade Extension
TC_COMPONENT_ZFX  = 'ZFX'   #zEnterprise Flex System
TC_COMPONENT_ZXN  = 'ZXN'   #zNode for both zFX and zBX nodes
TC_COMPONENT_HVM_2 = 'HVM_2'#hvm for prsm2
TC_COMPONENT_SVM_2 = 'SVM_2'#svm for prsm2
TC_COMPONENT_VSM_2 = 'VSM_2'#vsm for prsm2
TC_COMPONENT_CPC_2 = 'CPC_2'#cpc for prsm2
TC_COMPONENT_NVM_2 = 'NVM_2'#nvm for prsm2

# List of all valid components, used for command line validation
TC_COMPONENT_LIST = [TC_COMPONENT_CONS, TC_COMPONENT_CPC, TC_COMPONENT_CREC, TC_COMPONENT_EAM, TC_COMPONENT_EM, TC_COMPONENT_EMM,
                     TC_COMPONENT_GPRO, TC_COMPONENT_GRP, TC_COMPONENT_GS, TC_COMPONENT_HVM, TC_COMPONENT_IPRO, TC_COMPONENT_IS,
                     TC_COMPONENT_LPAR, TC_COMPONENT_LPRO, TC_COMPONENT_MDM, TC_COMPONENT_MS, TC_COMPONENT_NVM, TC_COMPONENT_PPM,
                     TC_COMPONENT_RPRO, TC_COMPONENT_SVM, TC_COMPONENT_VSM, TC_COMPONENT_SEC,TC_COMPONENT_zBX, 
                     TC_COMPONENT_HVM_2, TC_COMPONENT_SVM_2,TC_COMPONENT_NVM_2,TC_COMPONENT_VSM_2,TC_COMPONENT_CPC_2]
TC_COMPONENT_LIST.extend(make_lowercase_copy(TC_COMPONENT_LIST))    # Add lowercase versions as needed, for command line convenience


# Testcase scenario type
# Be sure to add any new ones to TC_SCENARIO_TYPE_LIST.
TC_SCENARIO_TYPE = 'scenario_type'
TC_SCENARIO_TYPE_AUTHORIZATION = 'authorization'
TC_SCENARIO_TYPE_FAILURE       = 'failure'
TC_SCENARIO_TYPE_NOTIFICATION  = 'notification'
TC_SCENARIO_TYPE_SUCCESS       = 'success'
# List of all valid scenario types, used for command line validation
TC_SCENARIO_TYPE_LIST = [TC_SCENARIO_TYPE_AUTHORIZATION, TC_SCENARIO_TYPE_FAILURE, TC_SCENARIO_TYPE_NOTIFICATION, TC_SCENARIO_TYPE_SUCCESS]
TC_SCENARIO_TYPE_LIST.extend(make_lowercase_copy(TC_SCENARIO_TYPE_LIST))    # Add lowercase versions as needed, for command line convenience

# Testcase execution type
# Be sure to add any new ones to TC_EXECUTION_TYPE_LIST.
TC_EXECUTION_TYPE = 'execution_type'
TC_EXECUTION_TYPE_DISRUPTIVE               = 'disruptive'
TC_EXECUTION_TYPE_MANUAL                   = 'manual'
TC_EXECUTION_TYPE_SELF_CHECKING            = 'self-checking'
TC_EXECUTION_TYPE_SELF_CHECKING_EXCLUSIVE  = 'self-checking-exclusive'
TC_EXECUTION_TYPE_SELF_CHECKING_WITH_SETUP = 'self-checking-with-setup'
TC_EXECUTION_TYPE_SUBTEST                  = 'subtest'
# List of all valid execution types, used for command line validation
TC_EXECUTION_TYPE_LIST = [TC_EXECUTION_TYPE_DISRUPTIVE, TC_EXECUTION_TYPE_MANUAL, TC_EXECUTION_TYPE_SELF_CHECKING,
                          TC_EXECUTION_TYPE_SELF_CHECKING_EXCLUSIVE, TC_EXECUTION_TYPE_SELF_CHECKING_WITH_SETUP, TC_EXECUTION_TYPE_SUBTEST]
TC_EXECUTION_TYPE_LIST.extend(make_lowercase_copy(TC_EXECUTION_TYPE_LIST))  # Add lowercase versions as needed, for command line convenience

# Marker lines for output of --get-properties requests
GET_PROPERTIES_BEGIN_MARKER = "***%s begin***" % (TESTCASE_PROPERTIES_VARIABLE_NAME)
GET_PROPERTIES_END_MARKER = "***%s end***" % (TESTCASE_PROPERTIES_VARIABLE_NAME)


#############################################################################
# Miscellaneous constants
#############################################################################

# Flag to indicate whether ODT Z9474 is applied to the target system.  It changes some
# characteristics of notification messages.  This flag allows the message validation
# code to react accordingly.
Z9474_applied = True


#############################################################################
# "Temporary object" support.  These are constants that support the creation
# (via the various object-specific "create_temporary_<object-type>()" methods)
# and deletion of "temporary" objects.
#############################################################################

# System-defined users, used for admin-type operations during testcase scenario setup
# and cleanup.  These constants are intended for use as values for the KEY_ADMIN_USERID 
# property in the temporary_object_types_info collection and on calls to get_admin_session(userid).
ACCESS_ADMINISTRATOR =      'ACSADMIN'
ADVANCED_OPERATOR =         'ADVANCED'
ENSEMBLE_ADMINISTRATOR =    'ENSADMIN'
ENSEMBLE_OPERATOR =         'ENSOPERATOR'
SYSTEM_OPERATOR =           'OPERATOR'
SERVICE_REPRESENTATIVE =    'SERVICE'
SYSTEM_PROGRAMMER =         'SYSPROG'
PEDEBUG =                   'PEDEBUG'

# These constants identify the kinds of objects that are supported by the
# "temporary object" support in wsautils.  Each type must be added to the
# temporary_object_types_deletion_order list in the appropriate position,
# and it must also be added to the temporary_object_types_info collection
# so it can be identified and handled properly.
TEMP_OBJ_TYPE_USER =                'user'
TEMP_OBJ_TYPE_USER_ROLE =           'role'
TEMP_OBJ_TYPE_USERID_PATTERN =      'userid-pattern'
TEMP_OBJ_TYPE_PASSWORD_RULE =       'password-rule'
TEMP_OBJ_TYPE_LDAP_SERVER_CONFIG =  'ldap'
TEMP_OBJ_TYPE_CUSTOM_GROUP =        'group'
TEMP_OBJ_TYPE_VIRTUAL_SERVER =      'virtual-server'
TEMP_OBJ_TYPE_WORKLOAD_RESOURCE_GROUP = 'workload-resource_group'
TEMP_OBJ_TYPE_WORKLOAD_ELEMENT_GROUP = 'workload-element_group'

# An ordered list of object types supported as "temporary objects".  This list defines
# the order in which the temporary objects are deleted at the end of testcase execution.
temporary_object_types_deletion_order = [TEMP_OBJ_TYPE_USERID_PATTERN,  # must be before User (specifically, before type=template Users are deleted)
                                         TEMP_OBJ_TYPE_USER,
                                         TEMP_OBJ_TYPE_USER_ROLE,       # must be after User
                                         TEMP_OBJ_TYPE_CUSTOM_GROUP,    # must be after User Role and User
                                         TEMP_OBJ_TYPE_PASSWORD_RULE,   # must be after User
                                         TEMP_OBJ_TYPE_LDAP_SERVER_CONFIG,  # must be after patterns
                                         TEMP_OBJ_TYPE_VIRTUAL_SERVER,
                                         TEMP_OBJ_TYPE_WORKLOAD_ELEMENT_GROUP,
                                         TEMP_OBJ_TYPE_WORKLOAD_RESOURCE_GROUP, # must be after Workload Element Groups
                                        ]

# Keys for info in the temporary_object_types_info map
KEY_ADMIN_USERID = 'admin_userid'   # Key for the name of the system-defined user that has administration privileges for this type of object
KEY_URI_PREFIX =   'uri_prefix'     # Key for the initial constant part of the URI that identifies an object this type

# Map of information about the object types that are supported as "temporary objects"
temporary_object_types_info = dict({TEMP_OBJ_TYPE_USER :                {KEY_ADMIN_USERID : ACCESS_ADMINISTRATOR, KEY_URI_PREFIX : '/api/users/'}, 
                                    TEMP_OBJ_TYPE_USER_ROLE :           {KEY_ADMIN_USERID : ACCESS_ADMINISTRATOR, KEY_URI_PREFIX : '/api/user-roles/'},
                                    TEMP_OBJ_TYPE_USERID_PATTERN :      {KEY_ADMIN_USERID : ACCESS_ADMINISTRATOR, KEY_URI_PREFIX : '/api/console/user-patterns/'},
                                    TEMP_OBJ_TYPE_PASSWORD_RULE :       {KEY_ADMIN_USERID : ACCESS_ADMINISTRATOR, KEY_URI_PREFIX : '/api/console/password-rules/'},
                                    TEMP_OBJ_TYPE_LDAP_SERVER_CONFIG :  {KEY_ADMIN_USERID : ACCESS_ADMINISTRATOR, KEY_URI_PREFIX : '/api/console/ldap-server-definitions/'},
                                    TEMP_OBJ_TYPE_CUSTOM_GROUP :        {KEY_ADMIN_USERID : ACCESS_ADMINISTRATOR, KEY_URI_PREFIX : '/api/groups/'},
                                    TEMP_OBJ_TYPE_VIRTUAL_SERVER :      {KEY_ADMIN_USERID : ENSEMBLE_ADMINISTRATOR, KEY_URI_PREFIX : '/api/virtual-servers/'},
                                    TEMP_OBJ_TYPE_WORKLOAD_RESOURCE_GROUP   : {KEY_ADMIN_USERID : ENSEMBLE_ADMINISTRATOR, KEY_URI_PREFIX : '/api/workload-resource-groups/'},
                                    TEMP_OBJ_TYPE_WORKLOAD_ELEMENT_GROUP    : {KEY_ADMIN_USERID : ENSEMBLE_ADMINISTRATOR, KEY_URI_PREFIX : '/api/workload-element-groups/'},
                                  })


# Map of URI prefixes to the name of the system-defined user that has administrator permissions for objects with that URI prefix.
# This map is used to locate/create an API session with administrator permissions for the URI prefix.
# Note that these prefixes must be listed from most-specific to least-specific, since they are searched in order.
# It is recommended to include a trailing slash only on URI prefixes that require it in order for it to be a valid URI.
# (Some URI prefixes can be used in their entirety on List operations, and thus should not include a trailing slash;
# if needed, two entries can be included: one with a trailing slash and one without).
# TODO: add support for expressions or wildcards for objects that contain multiple IDs (e.g., element objects often have multiple IDs)
uri_admin_info = dict({'/api/ensembles' : ENSEMBLE_ADMINISTRATOR,
                       '/api/console/hardware-messages' : SYSTEM_PROGRAMMER,
                       '/api/console/users' : ACCESS_ADMINISTRATOR,
                       '/api/console/user-roles' : ACCESS_ADMINISTRATOR,
                       '/api/console/tasks' : ACCESS_ADMINISTRATOR,
                       '/api/console/user-patterns' : ACCESS_ADMINISTRATOR,
                       '/api/console/password-rules' : ACCESS_ADMINISTRATOR,
                       '/api/console/ldap-server-definitions' : ACCESS_ADMINISTRATOR,
                       '/api/users/' : ACCESS_ADMINISTRATOR,
                       '/api/user-roles/' : ACCESS_ADMINISTRATOR,
                     })
#############################################################################
# ActiveMQ
# Note that the HMC must be configured to explicitly use the non-SSL ports.
#############################################################################

# PyActiveMQ ports
WSA_ACTIVEMQ_PORT_NON_SSL = 61616
WSA_ACTIVEMQ_PORT_SSL     = 61617

# STOMP ports
WSA_STOMP_PORT_NON_SSL = 61613
WSA_STOMP_PORT_SSL = 61612

# Supported ActiveMQ clients
# These constants are used as command line option values.
AMQ_CLIENT_PYACTIVEMQ = 'pyactivemq'
AMQ_CLIENT_STOMP = 'stomp'
WSA_DEFAULT_AMQ_CLIENT = AMQ_CLIENT_STOMP

# ActiveMQ socket types.
# These constants are used as command line option values.
SOCKET_TYPE_SSL = 'ssl'
SOCKET_TYPE_NON_SSL = 'non-ssl'

#############################################################################
# Test systems information
#############################################################################
### R32 ensemble
# The name of the ensemble on the primary FVT test system.  This can be used
# in testcases with certain prerequisites/restrictions that are known to
# exist on R32.
ENSEMBLE_NAME_R32 = 'R32Ensemble'
DEFAULT_ENSEMBLE_NAME = 'ZBX51'
DEFAULT_CPC_NAME = 'S32'
DEFAULT_VIRTUALIZATION_HOST_NAME = 'B.1.12'
DEFAULT_VIRTUAL_SERVER_NAME = 'APIVM1'
DEFAULT_LPAR_NAME = 'APIVM1'
PREFERRED_ZVM_VIRTUALIZATION_HOST_R32 = 'APIVM1'
IP_ADDRESS_R32_HMC = 'Y.Y.Y.Y'         # (R32 is no longer available for API testing)
IP_ADDRESS_R32_ALT_HMC = '9.60.14.45'     # (R32 is no longer available for API testing)
FAMILIAR_NAME_R32_HMC = 'S32'          # The familiar name for the HMC/SE/Ensemble, not necessarily the HMC's hostname

# Ichabod ensemble
IP_ADDRESS_ICHABOD_HMC = '9.60.14.63'
FAMILIAR_NAME_ICHABOD_HMC = 'ICHABOD'  # The familiar name for the HMC/SE/Ensemble, not necessarily the HMC's hostname

#===============================================================================
# Constant file to run the Testcase : lpar_5433
# 
LPAR_CPC_NAME = 'APIVM1'
LPAR_NAME     = 'VMALT' # remove the postfix '1' from the lpar name.
LPAR_NAME_ONE = 'VMALT1'
LPAR_NAME_TWO = 'VMALT2'
LPAR_NAME_THREE = 'VMALT3'
#===============================================================================

#############################################################################
# API URIs
#############################################################################

# Log onto an HMC
WSA_URI_LOGON   = '/api/session'

# Log off of an HMC
WSA_URI_LOGOFF  = '/api/session/this-session'

# Retrieve the API version
WSA_URI_VERSION = '/api/version'

# List all ensembles
WSA_URI_ENSEMBLES      = '/api/ensembles'

# Retrieve properties of a specific ensemble
WSA_URI_ENSEMBLE       = '/api/ensembles/{0}'

# Retrieve all CPCs
WSA_URI_CPCS           = '/api/cpcs'

# Retrieve all virtualization hosts of a specific ensemble
WSA_URI_VIRT_HOSTS_ENS = '/api/ensembles/{0}/virtualization-hosts'

# Retrieve all virtualization hosts of a specific cpc
WSA_URI_VIRT_HOSTS_CPC = '/api/cpcs/{0}/virtualization-hosts'

# Retrieve all properties of a specific virtualization host
WSA_URI_VIRT_HOST      = '/api/virtualization-hosts/{0}'


#############################################################################
# Testcase exit return codes
#############################################################################

# Exit return code for successful testcase execution
WSA_EXIT_SUCCESS = 0

# Exit return code for an API error
WSA_EXIT_ERROR_API = 1

# Exit return code for an unexpected error such as a communication failure
WSA_EXIT_ERROR_UNCAUGHT = 2

# Exit return code for successful --get-properties request
WSA_EXIT_GET_PROPERTIES_SUCCESS = WSA_EXIT_SUCCESS

# Exit return code for successful --check-properties request
WSA_EXIT_CHECK_PROPERTIES_SUCCESS = WSA_EXIT_SUCCESS

# Exit return code for an invalid command line (e.g., an invalid combination of options)
WSA_EXIT_INVALID_COMMAND_LINE = 5

# Exit return code for an error due to missing testcase properties
WSA_EXIT_MISSING_TESTCASE_PROPERTIES = 6

# Exit return code indicating that a specific testcase property is not defined
WSA_EXIT_PROPERTY_NOT_DEFINED = 7

# Exit return code indicating that a testcase requirement was not met
WSA_EXIT_REQUIREMENT_NOT_MET = 8


WSA_EXIT_ERROR_CLEANUP = 9
#############################################################################
# HTTP Request and Response
# Note that the HMC must be configured to explicitly use the non-SSL port.
#############################################################################

# Non-SSL HTTP Port ... need HTTPConnection ...
WSA_PORT_NON_SSL = 6167

# SSL HTTP Port ... needs HTTPSConnection ...
WSA_PORT_SSL     = 6794

# HTTP GET command
WSA_COMMAND_GET    = 'GET'

# HTTP DELETE command
WSA_COMMAND_DELETE = 'DELETE'

# HTTP POST command
WSA_COMMAND_POST   = 'POST'

# HTTP PUT command
WSA_COMMAND_PUT    = 'PUT'

# Header for content type ... both request and response
WSA_HEADER_CONTENT    = 'content-type'
WSA_HEADER_CONTENT_TYPE   = WSA_HEADER_CONTENT  # Synonym with better name
WSA_HEADER_CONTENT_LENGTH = 'content-length'

# Header for API session ... request header only
WSA_HEADER_RQ_SESSION = 'x-api-session'

# Header for API session ... response header only
WSA_HEADER_RS_SESSION = 'api-session'

# Response headers (these are published in the examples in the WS API customer book)
WSA_HEADER_RESP_SERVER = 'server'
WSA_HEADER_RESP_CACHE_CONTROL = 'cache-control'
WSA_HEADER_RESP_DATE = 'date'
WSA_HEADER_RESP_LOCATION = 'location'
WSA_HEADER_RESP_TRANSFER_ENCODING = 'transfer-encoding'

WSA_CONTENT_JSON = 'application/json'
WSA_CONTENT_XML  = 'application/xml'
WSA_CONTENT_ZIP  = 'application/zip'

# Currently supported content types
WSA_SUPPORTED_CONTENT = [ WSA_CONTENT_JSON, WSA_CONTENT_XML, WSA_CONTENT_ZIP ]

#############################################################################
# Common property names
#############################################################################
PROPERTY_OBJECT_URI   = 'object-uri'
PROPERTY_NAME         = 'name'
PROPERTY_DESCRIPTION  = 'description'
PROPERTY_LPAR_NAME    = 'lpar-name'
PROPERTY_ID           = 'partition-id'
PROPERTY_TYPE         = 'type'
PROPERTY_ADAPTER_ID   = 'adapter-id'
PROPERTY_ADAPTER_PORT = 'adapter-port'
PROPERTY_PORT_INDEX   = 'port-index'



#############################################################################
# Command line option names
#############################################################################
OPTION_ADDR = '--addr'
OPTION_PORT = '--port'
OPTION_USER = '--user'
OPTION_PASS = '--pass'
OPTION_GET_PROPERTIES = '--get-properties'
OPTION_CHECK_PROPERTIES = '--check-properties'
OPTION_RUN_IF_APPLICABLE = '--run-if-applicable'
OPTION_CAPABILITY = '--capability'
OPTION_COMPONENT = '--component'
OPTION_SCENARIO = '--scenario'
OPTION_EXECUTION_TYPE = '--execution-type'
#OPTION_MIN_VERSION = '--min-version'    # (Replaced by OPTION_REQUIRED_VERSION)
#OPTION_MAX_VERSION = '--max-version'    # (Replaced by OPTION_REQUIRED_VERSION)
OPTION_REQUIRED_VERSION = '--required-version'
OPTION_API_VERSION = '--api-version'


# Command line destination variable names
OPTION_ADDR_DEST = 'host'
OPTION_PORT_DEST = 'port'
OPTION_USER_DEST = 'user'
OPTION_PASS_DEST = 'pwd'

#############################################################################
# Command line default values
#############################################################################
DEFAULT_ADDR = '9.56.198.64'#'9.152.151.49'# '9.12.38.189' #'9.56.192.214' # '9.60.15.124'# ''9.56.192.214' #  '9.60.31.100'#'9.152.151.49' #'9.56.192.214' #'9.152.151.49' #'9.60.31.168'#'9.60.31.170'#'9.12.38.183'    # A dummy default, to force the user to specify --addr.  (R32 is no longer available)
#DEFAULT_ADDR = '9.60.15.62'  #p15
#DEFAULT_ADDR = '9.60.14.63'   #Ichabod
#DEFAULT_ADDR = '9.56.196.93'
DEFAULT_PORT = WSA_PORT_SSL
WSA_DEFAULT_USERID   = 'ensadmin'
WSA_DEFAULT_PASSWORD = 'password'

#############################################################################
# API feature strings.  These identify optional WS API features that may be
# available on the HMC.  A list of available features is included in the 
# response to the API Version and Logon requests.  The available features
# are specified in files in the /console/data/webapi/features/ directory on
# the HMC.
#############################################################################
FEATURE_GET_FILES_FROM_SE = 'internal-get-files-from-se' # Internal-use only API to fetch a specified file(s) from an SE

#############################################################################
# Response Validation
#############################################################################

STATUS       = 'status'
CONTENT_TYPE = 'content-type'
REQUIRED     = 'required'
OPTIONAL     = 'optional'


STATUS_200     = ( STATUS, 200 )
STATUS_201     = ( STATUS, 201 )
STATUS_202     = ( STATUS, 202 )
STATUS_204     = ( STATUS, 204 )
CONTENT_JSON   = ( CONTENT_TYPE, WSA_CONTENT_JSON )
REQUIRED_EMPTY = ( REQUIRED, [] )
OPTIONAL_EMPTY = ( OPTIONAL, [] )
OPTIONAL_API1DOT4 = ( OPTIONAL, ['acceptable-avail-status','avail-policies','avail-status','element-groups','perf-policies','absolute-ziip-capping','workload-element-groups','shutdown-timeout', 'shutdown-timeout-source','gpmp-network-adapter'] )
OPTIONAL_PASSWORD_EXPIRES = (OPTIONAL, ['password-expires'])


# Logon and Version #########################################################

__ver_required       = ( REQUIRED, [ 'api-major-version', 'api-minor-version', 'hmc-name', 'hmc-version' ] )
__ver_optional       = ( OPTIONAL, [ 'api-features' ] )
__logon_required     = ( REQUIRED, [ 'api-major-version', 'api-minor-version', 'api-session', 'notification-topic' ] )
__logon_required_job = ( REQUIRED, [ 'api-major-version', 'api-minor-version', 'api-session', 'notification-topic','job-notification-topic' ] )
__logon_optional     = ( OPTIONAL, [ 'password-expires', 'api-features' ] )

# Validate response from 'Get Version' operation
WSA_VERSION_VALIDATE   = dict( [ STATUS_200, CONTENT_JSON, __ver_required, __ver_optional ] )

# Validate response from 'Logon' operation
WSA_LOGON_VALIDATE     = dict( [ STATUS_200, CONTENT_JSON, __logon_required, __logon_optional ] )
WSA_LOGON_VALIDATE_JOB     = dict( [ STATUS_200, CONTENT_JSON, __logon_required_job, __logon_optional ] )

# Ensembles #################################################################

__list_ensembles_required = ( REQUIRED, [ 'ensembles' ] )

__get_ensemble_required   = ( REQUIRED, [ 'acceptable-status',
                                            'class',
                                            'cpu-perf-mgmt-enabled-power-vm',
                                            'cpu-perf-mgmt-enabled-zvm',
                                            'description',
                                            'has-unacceptable-status',
                                            'is-locked',
                                            'mac-prefix',
                                            'management-enablement-level',
                                            'name',
                                            'object-id',
                                            'object-uri',
                                            'parent',
                                            'power-consumption',
                                            'power-rating',
                                            'reserved-mac-address-prefixes',
                                            'status',
                                            'unique-local-unified-prefix' ] )

__get_ensemble_optional   = ( OPTIONAL, [ 'alt-hmc-name',
                                            'alt-hmc-ipv4-address',
                                            'alt-hmc-ipv6-address',
                                          'cpu-perf-mgmt-enabled-x-hyp',
                                            'cpu-perf-mgmt-enabled-x-hyp',  #temporarily resumed by lv, for zHelixGA2 testing, but notice it is not running on lower version

                                            'load-balancing-enabled',
                                            'load-balancing-ip-addresses',
                                            'load-balancing-port',
                                            'max-nodes',
                                            'max-cpc-nodes',
                                            'max-zbx-nodes' ] )

# Validate response from 'List Ensembles' operation
WSA_LIST_ENSEMBLES_VALIDATE = dict( [ STATUS_200, CONTENT_JSON, __list_ensembles_required, OPTIONAL_EMPTY ] )

# Required keys for each ensemble returned by 'List Ensembles' operation
WSA_LIST_ENSEMBLE_REQUIRED  = [ 'name', 'object-uri', 'status' ]

# Validate response from 'Get Ensemble Properties' operation
WSA_GET_ENSEMBLE_VALIDATE   = dict( [ STATUS_200, CONTENT_JSON, __get_ensemble_required,   __get_ensemble_optional ] )


# CPCs ######################################################################

__list_cpcs_required = ( REQUIRED, [ 'cpcs' ] )

# Validate response from 'List CPCs' operation
WSA_LIST_CPCS_VALIDATE = dict( [ STATUS_200, CONTENT_JSON, __list_cpcs_required, OPTIONAL_EMPTY ] )

# Required keys for each cpc returned by 'List CPCs' operation
WSA_LIST_CPC_REQUIRED  = [ 'name', 'object-uri', 'status' ]

# Required keys for 'Get CPC Properties' operation
__get_cpc_properties_required  = ( REQUIRED, [ 'name',
                                               'object-uri',
                                               'type',
                                               'status' ] )

# Validate response from 'Get CPC Properties' operation
WSA_GET_CPC_PROPERTIES_VALIDATE = dict( [ STATUS_200, CONTENT_JSON, __get_cpc_properties_required, OPTIONAL_EMPTY ] )


# Virtualization Hosts ######################################################

__list_virt_hosts_required = ( REQUIRED, [ 'virtualization-hosts' ] )

# Validate response from 'List Virtualization Hosts' operation
WSA_LIST_VIRT_HOSTS_VALIDATE = dict( [ STATUS_200, CONTENT_JSON, __list_virt_hosts_required, OPTIONAL_EMPTY ] )

# Required keys for each virtualization host returned by 'List Virtualization Hosts' operation
WSA_LIST_VIRT_HOST_REQUIRED  = [ 'name', 'object-uri', 'status', 'type' ]

# Wait period for all zvm tests
WAIT_PERIOD_FOR_ZVM_TEST = 30 

# These are the properties of a notification message that are not of type string.
# When an incoming message is received, it is used to populate a dictionary of
# key-value pairs.  Most of the properties are strings, but some are not and require
# special handling.  Identify them here along with their datatype.  The addition of
# a new type here will require corresponding changes where this list is processed.
if Z9474_applied:
    nonstring_message_properties = [
                                    ('global-sequence-nr', 'long'), 
                                    ('session-sequence-nr', 'long'),
                                   ]
else:
    nonstring_message_properties = [
                                   ]


#added by lv start
APA_TESTENV_CPC_UNDER_TEST = 'BLUECORE'

__list_virt_servers_required = ( REQUIRED, [ 'virtual-servers' ] )

# Validate response from 'List Virtualization Hosts' operation
WSA_LIST_VIRT_SERVERS_VALIDATE = dict( [ STATUS_200, CONTENT_JSON, __list_virt_servers_required, OPTIONAL_EMPTY ] )

__list_virt_server_groups_required = ( REQUIRED, [ 'virtual-server-groups' ] )

WSA_LIST_VIRT_SERVER_GROUPS_VALIDATE = dict( [ STATUS_200, CONTENT_JSON, __list_virt_server_groups_required, OPTIONAL_EMPTY ] )
#added by lv end

#adding the constants need for Ensemble properties for node properties
__get_ensemble_required_nodes   = ( REQUIRED, [ 'acceptable-status',
                                            'class',
                                            'cpu-perf-mgmt-enabled-power-vm',
                                            'cpu-perf-mgmt-enabled-zvm',
                                            'description',
                                            'has-unacceptable-status',
                                            'is-locked',
                                            'mac-prefix',
                                            'management-enablement-level',
                                            'name',
                                            'object-id',
                                            'object-uri',
                                            'parent',
                                            'power-consumption',
                                            'power-rating',
                                            'reserved-mac-address-prefixes',
                                            'status',
                                            'unique-local-unified-prefix',
                                            'max-cpc-nodes',
                                            'max-nodes',
                                            'max-zbx-nodes' ] )


WSA_GET_ENSEMBLE_VALIDATE_NODES   = dict( [ STATUS_200, CONTENT_JSON, __get_ensemble_required_nodes,   __get_ensemble_optional ] )
WSA_DEFAULT_ZBX_NAME = 'ZBX2'