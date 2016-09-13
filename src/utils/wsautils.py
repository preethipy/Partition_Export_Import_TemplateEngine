#############################################################################
#
# Some utility classes and functions that may be useful for API Testing
#
# In order to import this module for use in testcases, set the PYTHONPATH
# environment variable to point to the directory where the modules are
# located.
#
# from wsaconst import *
# from wsautils import *
#
# The call to os.getenv can be used to retrieve any environment variable, so
# defining a variable that points to the Python common utilities directory
# could be established in a test environment startup script, then referenced
# above in the sys.path.append method call ...
#
#############################################################################

from wsaconst import *
import wsaglobals  # True global variables

import httplib
import pprint
import json
import optparse  # use argparse with Python 2.7.x ...
from optparse import make_option
from optparse import OptionGroup
import string

import sys
import threading
import time
import traceback
import types
import ssl
import os
import re
import __main__

import logging
import logging.config

class progress_bar_loading(threading.Thread):

    def run(self):
            global stop
            global kill
            global progress_str
            print progress_str + '....  ',
            sys.stdout.flush()
            i = 0
            while stop != True:
                    if (i % 4) == 0: 
                        sys.stdout.write('\b/')
                    elif (i % 4) == 1: 
                        sys.stdout.write('\b-')
                    elif (i % 4) == 2: 
                        sys.stdout.write('\b\\')
                    elif (i % 4) == 3: 
                        sys.stdout.write('\b|')

                    sys.stdout.flush()
                    time.sleep(0.2)
                    i += 1

            if kill == True: 
                print '\b\b\b\b ABORT!'
            else: 
                print '\b\b done!'
            return
        
    def stop(self):
        global stop
        stop = True
        
    def configure(self,progress_string='Processing'):
        global progress_str
        progress_str = progress_string
        global stop
        stop = False
        
        

progress_str = "Processing"
kill = False      
stop = False

def initializeLogging():
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%a, %d %b %Y %H:%M:%S',
                        filename='logs/console.log',
                        filemode='w')





WSA_UTILS_VERSION = "1.1"  # Current version of the API utilities

#############################################################################
# Determine which, if any, ActiveMQ clients are installed.  Set global flags
# for later use.
#############################################################################
# Try STOMP
try:
    import stomp
    stomp_present = True
except ImportError:
    # print "STOMPPY not installed or not supported"
    stomp_present = False

# Try PyActiveMQ
try:
    import pyactivemq
    pyactivemq_present = True
except ImportError:
    # print "Pyactivemq not installed or not supported"
    pyactivemq_present = False

#############################################################################
# Exceptions
#############################################################################

# General exception raised when api errors occur ...
class ApiException(Exception) :

    def __init__(self, text, response=None, keys=None) :
        Exception.__init__(self, text)
        self.text = text  # Message text of exception
        self.response = response  # Response object, if applicable
        self.keys = keys  # Keys in error, only used by validate_response and
                                 # validate_dictionary methods

    def __str__(self) :

        text = self.text
        keys = self.keys
        resp = self.response

        result = []
        result.append('ApiException caught ...\n\n')
        result.append('MESSAGE :\n')
        result.append(text)
        result.append('\n')

        if resp is None or not hasattr(resp, 'body'):
            if keys is not None :
                result.append(keys)
        else :
            body = resp.body
            message = body[ 'message' ]     if 'message'     in body else None
            status = body[ 'http-status' ] if 'http-status' in body else None
            reason = body[ 'reason' ]      if 'reason'      in body else None
            uri = body[ 'request-uri' ] if 'request-uri' in body else None
            result.append('\nReturn Code = ')
            if status is not None and reason is not None :
                result.append(status)
                result.append('.')
                result.append(reason)
            else :
                result.append(str(resp.status))
            result.append(' ')
            result.append(resp.reason)
            if message is not None :
                result.append('\nResponse Message = ')
                result.append(message)
            if keys is not None :
                result.append(' : ')
                result.append(keys)
            if uri is not None :
                result.append('\nRequest URI = ')
                result.append(uri)
            result.append('\n\n')
            result.append(resp)

        result.append('\n\nStack Trace :\n')
        stack = traceback.format_tb(sys.exc_info()[2])
        result.append(''.join([ s for s in stack ]))

        return ''.join([ str(s) for s in result ])


#############################################################################
#
# Fatal exception ... used for non-API errors ...
#
# @parm text      - message text
# @parm response  - response from HTTP request.  This can be either an
#                   httplib.HTTPResponse or wsautils.Response object
# @parm traceback - stack trace, usually taken from a caught exception
#                   since it will differ from the stack trace created
#                   when the ApiFatalException is created.
# @parm request   - a wsautils.Request object representing the information
#                   sent via an HTTP request.  Since testcase writers do not
#                   generally have access to the HTTP request, this parameter
#                   should be considered internal to wsautils only.
# @parm other     - additional, relevant data provided by the testcase writer
#                   that may help with diagnostics.
#
#############################################################################

class ApiFatalException(Exception) :

    def __init__(self, text, response=None, traceback=None, other=None, request=None) :
        Exception.__init__(self, text)
        self.text = text  # Message text for exception
        self.response = response
        self.traceback = traceback
        self.other = other
        self.request = request

    def __str__(self) :

        result = []
        result.append('ApiFatalException caught\n\n')
        result.append('MESSAGE :\n')
        result.append(self.text)
        result.append('\n\n')

        if self.response is None and self.request is not None :
            result.append('REQUEST :\n')
            result.append(self.request)
            result.append('\n\n')

        if self.response is not None :
            result.append('RESPONSE :\n')
            if isinstance(self.response, httplib.HTTPResponse) :
                result.append(Response(self.response.status,
                                         self.response.reason,
                                         self.response.getheaders(),
                                         self.response.read()))
            else :
                result.append(self.response)

            result.append('\n\n')

        # Append the stack trace created when raising this exception ...
        result.append('TRACEBACK (most recent stack) :\n')
        stack = traceback.format_tb(sys.exc_info()[2])
        result.append(''.join([ s for s in stack ]))
        result.append('\n')

        # If present, this should be the stack trace created by the
        # 'caught' exception that was wrapped inside the ApiFatalException
        if self.traceback is not None :
            result.append('TRACEBACK (from caught exception) :\n')
            stack = traceback.format_tb(self.traceback)
            result.append(''.join([ s for s in stack ]))
            result.append('\n')

        if self.other is not None :
            result.append('OTHER :\n')
            result.append(self.other)
            result.append('\n')

        return ''.join([ str(s) for s in result ]).strip()


#############################################################################
# Request Class
#############################################################################

class Request :

    """This class encapsulates an HTTP request"""

    def __init__(self, operation, uri, headers, body) :
        self.operation = operation
        self.uri = uri
        self.headers = headers
        self.body = body

    def __str__(self) :
        l = []
        l.append('Request Operation : ')
        l.append(str(self.operation))
        l.append('\nRequest URI       : ')
        l.append(str(self.uri))

        l.append('\nRequest Headers   : ')
        if self.headers == None:
            l.append('None')
        else:
            l.append(json.dumps(self.headers, sort_keys=True, indent=1, separators=(',', ':')))

        l.append('\nRequest Body      : ')
        if self.body == None:
            l.append('None')
        else:
            l.append(json.dumps(json.loads(self.body), sort_keys=True, indent=1, separators=(',', ':')))

        return ''.join([ s for s in l ])


#############################################################################
#
# Response Class
#
# This class models an HTTP response object.  The response headers will be
# converted to a Python dictionary and the response body will be processed
# through the JSON parser if the content-type header is 'application/json'.
#
# If the 'content-type' indicates the body is a json-formatted string and
# the subsequent call to json.loads fails to parse the body, an
# ApiFatalException with be raised.  The response will be added to the
# exception, but the body will the unparse HTTP response body.
#
#############################################################################

class Response :

    """This class encapsulates an HTTP response"""

    #########################################################################
    # Init
    #########################################################################

    # Initialize a response
    def __init__(self, status, reason, headers, body, request=None) :

        # ##print '====================== begin body ====================================================='
        # ##print body
        # ##print '====================== end body ======================================================='
        self.status = status  # HTTP response status
        self.reason = reason  # HTTP response reason
        self.headers = dict(headers)  # HTTP response headers
        self.body = body  # HTTP response body
        self.request = request  # HTTP request
        self.bodyIsJSON = False  # Indicates whether the saved response body is a parsed JSON string

        if body is not None and len(body) > 0 :
            if self.headers[ CONTENT_TYPE ].startswith(WSA_CONTENT_JSON) :
                try :
                    # Parse the body and save the parsed version
                    self.body = json.loads(body)
                    self.bodyIsJSON = True  # Body is now a parsed JSON string
                except :
                    raise ApiFatalException(''.join([ str(s) for s in sys.exc_info()[1].args ]), response=self)
            else :
                self.body = body
        else :
            self.body = '{}'
            self.bodyIsJSON = True  # Body is a parsed JSON string (an empty body)

    # Print out a string representation of the response
    def __str__(self) :
        l = []
        if self.request is not None :
            l.append(self.request)
            l.append('\n\n')
        l.append('Response Status  : ')
        l.append(self.status)
        l.append('\nResponse Reason  : ')
        l.append(self.reason)

        l.append('\nResponse Headers : ')
        if self.headers == None:
            l.append('None')
        else:
            l.append(json.dumps(self.headers, sort_keys=True, indent=1, separators=(',', ':')))

        l.append('\nResponse Body    : ')
        if self.bodyIsJSON:
            l.append(json.dumps(self.body, sort_keys=True, indent=1, separators=(',', ':')))
            if 'stack' in self.body:
                l.append('\n\nstack (again, but in a more programmer-friendly format):\n')
                l.append(self.body[ 'stack' ])
        else:
            l.append(str(self.body))


        return ''.join([ str(s) for s in l ])


#############################################################################
#
# Session Class
#
# This class represents a persistent HTTP connection to an HMC.  As such,
# when the test code is finished with the HTTP connection, the close
# method should be called to ensure resources are cleaned up.
#
# Currently, only JSON-formatted request bodies are supported.  Addtional
# formats can be added in the future, as needed.
#
# The additional_options argument may be used to define any additional command
# line options to be permitted for this Session.  See parse_standard_options()
# for more details.  The option values may be referenced via the "opts" member
# of the Session object.  For example, if an option was defined with dest='sr_name':
#      name = session.opts.sr_name
#
# If the testcase script defines any positional arguments, their Usage information
# should be specified on the additional_arguments_usage_info argument.  See
# parse_standard_options() for more details.  The command line arguments can
# be referenced via the "args" member of the Session object, for example,
# to access the first testcase-specific positional argument:
#      property_name = session.args[session.arg_start_index + 0]
#
# Note that the __init__ method calls parse_standard_options(), which uses os._exit(rc)
# in some cases rather than the more common sys.exit(rc).  See the prolog of
# parse_standard_options for more details.
#############################################################################

class Session :

    """This class supports connecting to an Ensemble HMC via HTTP"""

    #########################################################################
    # Init
    #########################################################################

    def __init__(self, host=None, port=None, user=None, pwd=None, additional_options=None, additional_arguments_usage_info=None, amq_client=None, amq_socket_type=None) :
        """Initialize an instance of the Session class"""
        # Save any additional command line option definitions so that they're available
        # when the command line is re-parsed if another session is established.
        wsaglobals.global_saved_additional_options = additional_options
#       print 'in Session init: global_saved_additional_options=%s' % wsaglobals.global_saved_additional_options
        opts, args = parse_standard_options(additional_options, additional_arguments_usage_info)  # Read in command line arguments and options, if any ...
        self.opts = opts  # Keep all parsed options for anyone that might need them
        self.args = args  # Keep all parsed arguments for anyone that might need them
        self.arg_start_index = 0  # The index of the first test-case specific argument, if any.
                                    # There are currently no "standard" arguments, so all arguments
                                    # are, in effect, test-case specific; thus this index is 0.

        # Save values from the command line or our caller, as appropriate
        self.__host = opts.host if host is None else host
        self.__port = opts.port if port is None else port
        self.__user = opts.user if user is None else user
        self.__pass = opts.pwd  if pwd  is None else pwd
        self.__amq_client = opts.amq_client if amq_client is None else amq_client
        self.__amq_socket_type = opts.amq_socket_type if amq_socket_type is None else amq_socket_type
        self.__api_version_override = opts.api_version_override
        self.__get_properties = opts.get_properties
        self.__check_properties = opts.check_properties
        self.__run_if_applicable = opts.run_if_applicable
        self.__required_version = opts.required_version
        self.__required_capabilities = opts.required_capabilities
        self.__required_components = opts.required_components
        self.__required_scenario_types = opts.required_scenario_types
        self.__required_execution_types = opts.required_execution_types

        self.__args = args

        self.__connection = None  # Persistent HTTP connection
        self.__session = None  # Session id
        self.__topic = None  # Topic id for ActiveMQ notifications
                                   #
        self.__api_version = None  # WSA API version supported by HMC
        self.__hmc_name = None  # Name of the connected HMC
        self.__hmc_version = None  # Version of the connected HMC
        self.__jobtopic = None  # Topic id for ActiveMQ JOB Notifications
        self.__api_features = None  # List of available WS API features
                                   #
        self.__consumer = None  # ActiveMQ notification consumer
        self.__callback = None  # Callback method for notification messages


        #########################################################################
        # If no ActiveMQ client was specified, choose one based on what's installed
        # and available if possible.  Then, if no SSL preference was specified,
        # select a sensible one based on the ActiveMQ client.  Then, set the ActiveMQ
        # port to the appropriate port number.
        #########################################################################
        # Determine the client type
        if self.__amq_client is None:
            if stomp_present == True:  # STOMP is installed; use it
                self.__amq_client = AMQ_CLIENT_STOMP
            elif pyactivemq_present == True:  # No STOMP, but PyActiveMQ is installed; use it
                self.__amq_client = AMQ_CLIENT_PYACTIVEMQ
            else:  # None installed, so just go with the default here; errors will be surfaced later if an AMQ client is actually required.
                self.__amq_client = WSA_DEFAULT_AMQ_CLIENT

        # Use PyActiveMQ ActiveMQ client
        if self.__amq_client == AMQ_CLIENT_PYACTIVEMQ:
            if self.__amq_socket_type is None:
                self.__amq_socket_type = SOCKET_TYPE_NON_SSL  # Not specified, so set default

            if self.__amq_socket_type == SOCKET_TYPE_SSL:  # Sensible?  Current versions of pyactivemq don't support SSL
                self.__amq_port = WSA_ACTIVEMQ_PORT_SSL
            else:
                self.__amq_port = WSA_ACTIVEMQ_PORT_NON_SSL

        # Use STOMP ActiveMQ client
        else:
            if self.__amq_socket_type is None:
                self.__amq_socket_type = SOCKET_TYPE_SSL  # Not specified, so set default

            if self.__amq_socket_type == SOCKET_TYPE_SSL:
                self.__amq_port = WSA_STOMP_PORT_SSL
            else:
                self.__amq_port = WSA_STOMP_PORT_NON_SSL

#       print "pyactivemq_present = " + str(pyactivemq_present)
#       print "stomp_present = " + str(stomp_present)
#       print "leaving parse_standard_options() with"
#       print "\t self.__amq_client=" + str(self.__amq_client)
#       print "\t self.__amq_socket_type=" + str(self.__amq_socket_type)
#       print "\t self.__amq_port=" + str(self.__amq_port)
#       print "\t self.__get_properties=" + str(self.__get_properties)


    #########################################################################
    # Open connection to HMC
    #########################################################################

    def open(self) :

        """Create a persistent HTTP connection to an HMC, then logon"""

        body = json.dumps({ 'userid':self.__user, 'password':self.__pass })

        # Issue the Logon request
        response = self.__executeRequest(WSA_COMMAND_POST, WSA_URI_LOGON, body, WSA_CONTENT_JSON)

        # Check the status code to be sure logon succeeded before trying to validate
        # the response details.  For example, the response body might not even be a dictionary.
        if response.status != 200:
            raise ApiFatalException('Logon failed', response)


#       print '****************'
#       print response.request
#       print '****************'
#       print response.request.headers
#       print '****************'
#       print response.headers
#       print '****************'



        # Parse and validate the response to the Logon request.  Save info for later use.

        if 'job-notification-topic' in response.body.keys():
            self.__jobtopic = str(response.body[ 'job-notification-topic' ])
            validate_response(response, WSA_LOGON_VALIDATE_JOB)
        else :
            validate_response(response, WSA_LOGON_VALIDATE)

        self.__session = str(response.body[ 'api-session'        ])
        self.__topic = str(response.body[ 'notification-topic' ])

        if 'api-features' in response.body.keys():
            self.__api_features = response.body[ 'api-features' ]  # List of strings
        
        # Now issue an API Version request and validate the response
        response = self.get(WSA_URI_VERSION)
        validate_response(response, WSA_VERSION_VALIDATE)

        # Parse and save this session's version information
        ver = []
        ver.append(str(response.body[ 'api-major-version' ]))
        ver.append('.')
        ver.append(str(response.body[ 'api-minor-version' ]))

        self.__api_version = "".join(ver)
        self.__hmc_name = response.body[ 'hmc-name' ]
        self.__hmc_version = response.body[ 'hmc-version' ]

        # print "Topic ID: \t%s"     % self.__topic
        # print "Job Topic ID: \t%s" % self.__jobtopic
        # print "API version: \t%s"  % self.__api_version
        # print "API features: \t%s" % self.__api_features

        return self.__connection


    #########################################################################
    # Close connection to HMC
    #########################################################################

    def close(self) :
        """Logoff from the HMC, then close the HTTP connection"""

# # TODO : Close ActiveMQ consumer, too?

        if self.__connection is not None :
            try :
                # Logoff active session, if needed ...
                if self.__session is not None :
                    response = self.delete(WSA_URI_LOGOFF)
                    if response.status != 204 :
                        raise ApiFatalException('Unexpected response status during logoff', response=response)
            finally :
                try :
                   # Close the HTTP session
                   self.__connection.close()
                finally :
                    if self.__consumer is not None and self.__consumer.isRunning() :
                        self.__consumer.stop()


    #########################################################################
    # Get
    #
    # Note : If the headers parameter is passed, ALL the required HTTP
    #        request headers must be included.  No defaults will be added.
    #      : Specify return_full_response=False to prevent this method from
    #        reading the response body and closing the HTTP(S) connection.
    #        See __executeRequest for more information.
    #########################################################################

    def get(self, uri, headers=None, return_full_response=True) :
        """Execute an HTTP GET operation"""
        return self.__executeRequest(WSA_COMMAND_GET, uri, None, None, headers, return_full_response)


    #########################################################################
    # Put
    #
    # Note : If the headers parameter is passed, ALL the required HTTP
    #        request headers must be included.  No defaults will be added.
    #      : Specify return_full_response=False to prevent this method from
    #        reading the response body and closing the HTTP(S) connection.
    #        See __executeRequest for more information.
    #########################################################################

    def put(self, uri, body, headers=None, return_full_response=True) :
        """
        Execute an HTTP PUT operation
        NOTE: Request body is assumed to be JSON format
        """
        return self.__executeRequest(WSA_COMMAND_PUT, uri, body, WSA_CONTENT_JSON, headers, return_full_response)


    #########################################################################
    # Post
    #
    # Note : If the headers parameter is passed, ALL the required HTTP
    #        request headers must be included.  No defaults will be added.
    #      : Specify return_full_response=False to prevent this method from
    #        reading the response body and closing the HTTP(S) connection.
    #        See __executeRequest for more information.
    #########################################################################

    def post(self, uri, body, headers=None, return_full_response=True) :
        """
        Execute an HTTP POST operation
        NOTE: Request body is assumed to be JSON format
        """
        return self.__executeRequest(WSA_COMMAND_POST, uri, body, WSA_CONTENT_JSON, headers, return_full_response)


    #########################################################################
    # Delete
    #
    # Note : If the headers parameter is passed, ALL the required HTTP
    #        request headers must be included.  No defaults will be added.
    #      : Specify return_full_response=False to prevent this method from
    #        reading the response body and closing the HTTP(S) connection.
    #        See __executeRequest for more information.
    #########################################################################

    def delete(self, uri, headers=None, return_full_response=True) :
        """Execute an HTTP DELETE operation"""
        return self.__executeRequest(WSA_COMMAND_DELETE, uri, None, None, headers, return_full_response)


    #########################################################################
    # Host
    #########################################################################

    def host(self) :
        """Return the host"""
        return self.__host


    #########################################################################
    # Port
    #########################################################################

    def port(self) :
        """Return the port"""
        return self.__port


    #########################################################################
    # Userid
    #########################################################################

    def userid(self) :
        """Return the userid"""
        return self.__user


    #########################################################################
    # Password
    #########################################################################

    def password(self) :
        """Return the password"""
        return self.__pass


    #########################################################################
    # Session
    #########################################################################

    def session(self) :
        """Return the active session identifier"""
        return self.__session


    #########################################################################
    # Topic and job topic
    #########################################################################

    def topic(self) :
        """Return the active topic identifier"""
        return self.__topic


    def jobtopic(self) :
        """Return the active job topic identifier"""
        return self.__jobtopic


    #########################################################################
    # Values related to the FVT regression tools
    #########################################################################

    def api_version_override(self) :
        """Return the API version value from the command line"""
        return self.__api_version_override

    def get_properties(self) :
        """Return the OPTION_GET_PROPERTIES setting"""
        return self.__get_properties
    def check_properties(self) :
        """Return the OPTION_CHECK_PROPERTIES setting"""
        return self.__check_properties
    def run_if_applicable(self) :
        """Return the OPTION_RUN_IF_APPLICABLE setting"""
        return self.__run_if_applicable

    def required_version(self) :
        """Return the testcase required_version"""
        return self.__required_version

    def required_capabilities(self) :
        """Return the testcase required_capabilities"""
        return self.__required_capabilities
    def required_components(self) :
        """Return the testcase required_components"""
        return self.__required_components
    def required_scenario_types(self) :
        """Return the testcase required_scenario_types"""
        return self.__required_scenario_types
    def required_execution_types(self) :
        """Return the testcase required_execution_types"""
        return self.__required_execution_types


    #########################################################################
    # API Version
    #########################################################################

    def api_version(self) :
        """Return the reported API version supported by the HMC"""
        return self.__api_version


    #########################################################################
    # API Features
    #########################################################################

    def api_features(self) :
        """Return the reported API features supported by the HMC"""
        return self.__api_features


    #########################################################################
    # HMC Name
    #########################################################################

    def hmc_name(self) :
        """Return the name of the connected HMC"""
        return self.__hmc_name


    #########################################################################
    # HMC Version
    #########################################################################

    def hmc_version(self) :
        """Return the version of the connected HMC"""
        return self.__hmc_version


    #########################################################################
    # Register and start receiving general notification messages
    #########################################################################

    def start_receiving_messages(self, callback=None) :
        # print "in start_receiving_messages(); amq_client=" + str(self.__amq_client)+ "; port=" + str(self.__amq_port)
        self.start_message_consumer(self.__topic, callback)  # Start receiving messages for the general notification topic


    #########################################################################
    # Register and start receiving job notification messages
    #########################################################################

    def start_receiving_job_messages(self, callback=None) :
        # print "in start_receiving_job_messages(); amq_client=" + str(self.__amq_client)+ "; port=" + str(self.__amq_port)
        self.start_message_consumer(self.__jobtopic, callback)  # Start receiving messages for the job notification topic


    #########################################################################
    # Register and start receiving audit log notification messages
    #########################################################################

    def start_receiving_audit_messages(self, callback=None) :
        # print "in start_receiving_audit_messages(); amq_client=" + str(self.__amq_client)+ "; port=" + str(self.__amq_port)
        topic = get_notification_topic(self, 'audit')  # Get the topic name and make sure user is authorized to connect to it
        if topic == None:  # User is not authorized to connect to this topic
            raise ApiException('The API user is not authorized to connect to the audit notification topic')
        self.start_message_consumer(topic, callback)  # Start receiving messages for the audit notification topic


    #########################################################################
    # Register and start receiving security log notification messages
    #########################################################################

    def start_receiving_security_messages(self, callback=None) :
        # print "in start_receiving_security_messages(); amq_client=" + str(self.__amq_client)+ "; port=" + str(self.__amq_port)
        topic = get_notification_topic(self, 'security')  # Get the topic name and make sure user is authorized to connect to it
        if topic == None:  # User is not authorized to connect to this topic
            raise ApiException('The API user is not authorized to connect to the security notification topic')
        self.start_message_consumer(topic, callback)  # Start receiving messages for the security notification topic


    #########################################################################
    # Register and start receiving messages for the specified topic
    #########################################################################

    def start_message_consumer(self, topic, callback=None) :
        try :
            # print "in start_message_consumer(); amq_client=" + str(self.__amq_client)+ "; port=" + str(self.__amq_port)

            if (self.__amq_client == AMQ_CLIENT_PYACTIVEMQ):  # Use PyActiveMQ ActiveMQ consumer.  It supports only non-SSL connections
                if pyactivemq_present == False:
                    raise ApiFatalException("Cannot use PyActiveMQ ActiveMQ client - pyactivemq module is not installed")
                self.__consumer = PyActiveMQ_Consumer(self.__host,
                                            self.__amq_port,
                                            self.__user,
                                            self.__pass,
                                            topic,
                                            (True if self.__amq_socket_type == SOCKET_TYPE_SSL else False),
                                            callback)
            else:  # Use STOMP ActiveMQ consumer.  It supports both SSL and non-SSL connections
                if stomp_present == False:
                    raise ApiFatalException("Cannot use STOMP ActiveMQ client - stomp module is not installed")
                self.__consumer = STOMP_Consumer(self.__host,
                                            self.__amq_port,
                                            self.__user,
                                            self.__pass,
                                            topic,
                                            (True if self.__amq_socket_type == SOCKET_TYPE_SSL else False),
                                            callback)

            # print "About to start() the message consumer"
            self.__consumer.start()
        except :
            raise ApiFatalException(sys.exc_info()[1].args)



    #########################################################################
    # Stop receiving notification messages
    #########################################################################

    def stop_receiving_messages(self) :
        self.__consumer.stop()


    #########################################################################
    # Determine whether any notification messages have been received
    #########################################################################

    def has_messages(self) :
        return self.__consumer.has_messages()

    #########################################################################
    # Retrieve existing notification messages ... empty message queue
    #########################################################################

    def get_received_messages(self) :
        return self.__consumer.get_messages()


    #########################################################################
    # Retrieve raw notification messages ... empty message queue
    # Should be used for debug only ...
    #########################################################################

    def get_raw_messages(self) :
        return self.__consumer.get_raw_messages()


    #########################################################################
    #
    # __executeRequest (package private method)
    #
    # This method is private to the class and NOT called directly.
    #
    # Currently, the supported content types are :
    #
    #    None and 'application/json'
    #
    # Specify return_full_response=False to prevent this method from reading
    # response body and closing the HTTP(S) connection.  This allows the
    # caller to read the response as it sees fit, for example, one byte at a
    # time.  In this case, the caller is responsible for closing the HTTP(S)
    # connection.  The read_response_streamed method in this class can be used
    # to read the response body one byte at a time and then close the connection.
    #
    #########################################################################

    def __executeRequest(self, operation, uri, body, content, headers=None, return_full_response=True) :

        """Execute an HTTP request"""

        request = None
        response = None

        try :

            # Build up the default HTTP headers
            if headers is None :
                requestHeaders = {}
                requestHeaders[ 'Accept' ] = '*/*'
                if content in WSA_SUPPORTED_CONTENT :
                    requestHeaders[ WSA_HEADER_CONTENT ] = content
                if body is not None :
                    requestHeaders[ WSA_HEADER_CONTENT_LENGTH ] = len(body)
                if self.__session is not None :
                    requestHeaders[ WSA_HEADER_RQ_SESSION ] = self.__session
            else :
                requestHeaders = headers.copy()

            request = Request(operation, uri, requestHeaders, body)

            # **MHB**
            # Persistent connections, both SSL and non-SSL, are being closed after sitting
            # idle for 15-30 seconds.  As a workaround, create a new HTTP connection for
            # each request until a solution can be found ...
            if self.__port == WSA_PORT_SSL :
                # Beginning with Python 2.7.9, SSL connections are more secure and require a valid
                # X509 certificate signed by a trusted CA.  Since the HMC uses a self-signed certificate,
                # we revert to previous Python behavior by explicitly requesting an unverified context.
                # This is generally not advisable, for obvious reasons, but it is acceptable in the
                # development and test environments in which these API test utilities are intended to
                # be used.
                if sys.hexversion < 0x020709F0:  # Prior to 2.7.9; use default behavior
                    self.__connection = httplib.HTTPSConnection(self.__host, self.__port)
                else:  # 2.7.9 or later; specifically request prior behavior
                    self.__connection = httplib.HTTPSConnection(self.__host, self.__port, context=ssl._create_unverified_context())
                    print ""
                    
            else :
                self.__connection = httplib.HTTPConnection(self.__host, self.__port)

            try :
                self.__connection.request(operation, uri, body, requestHeaders)
                response = self.__connection.getresponse()
                # If we're returning the full Response object, then read the response body and construct a Response object;
                # otherwise, we just return the response from the HTTP(S)Connection object.
                if return_full_response is True :
                    result = Response(response.status, response.reason, response.getheaders(), response.read(), request)
                else :
                    result = response
            finally :
                # If we're returning the full Response object, then we've already read the response and can close out HTTP(S) connection.
                # Otherwise, leave it open for later reading by, for example, read_response_streamed().  Callers that specify
                # return_full_response=False are responsible for closing this connection.
                if return_full_response is True :
                    self.__connection.close()

        except (ApiFatalException, ApiFatalException) :
            raise
        except :
            text = self.buildExceptionMessage()
            raise ApiFatalException(text, response=response, traceback=sys.exc_info()[2])

        return result


    def buildExceptionMessage(self) :
        name = sys.exc_info()[0]
        args = []
        for arg in sys.exc_info()[1].args :
            if len(str(arg)) > 0 :
                args.append(arg)
                args.append(' ')
        text = ''.join([ str(s) for s in args ]).strip()
        return str(name) + ' ' + text


    #########################################################################
    #
    # read_response_streamed method
    #
    # Use this method to read the response to a request that was issued via
    # __executeRequest with return_full_response==False.  This method will
    # read the response one byte at a time and then close the connection.
    #
    # The response argument is the response as returned from
    # self.__connection.getresponse().
    #
    #########################################################################

    def read_response_streamed(self, response):
        try :
            print "\nAbout to read the response one byte at a time...\n"
            responseString = ""
            chunk = response.read(1)
            while (chunk != ""):
                responseString += chunk
                sys.stdout.write(chunk)
                chunk = response.read(1)

        finally :
            self.__connection.close()

        return responseString


#############################################################################
#
# Class PyActiveMQ_Consumer - Private class ... do not use directly ...
#
# This class sets up an ActiveMQ message consumer using a PyActiveMQ client.
#
# It requires a callback function that will be invoked upon receiving each
# new message from the ActiveMQ server.  The callback function takes exactly
# two arguments, the topic registered when the Consumer is created and the
# incoming message from the server.
#
# Typical usage :
#
#    Create a Consumer object.
#    Call Consumer.start to begin consuming messages.
#    Cause one or more notification events to fire.
#    Loop on Consumer.isRunning to wait for consumer thread to timeout.
#    Verify the accuracy of the notification messages.
#
#############################################################################

class PyActiveMQ_Consumer() :
    # Only define the internals of this class if PyActiveMQ is installed, due to references to the pyactivemq module
    if (pyactivemq_present == True):
        """Private class ... do not use directly"""

        class __MessageListener(pyactivemq.MessageListener):

            def __init__(self, topic, callback):
                pyactivemq.MessageListener.__init__(self)
                self.topic = topic
                self.callback = callback

            def onMessage(self, message):
                try :
                    self.callback(self.topic, message)
                except :
                    print traceback.print_exc()


        def __init__(self, host, port, username, password, topic, use_ssl, callback=None) :

            """This is the constructor ... all parameters required, exception callback"""

            self.messageLock = threading.Lock()  # Control access to message queue

            self.running = False

            self.host = host
            self.port = port
            self.username = username
            self.password = password
            self.topic = topic
            self.use_ssl = use_ssl

            if callback is None :
                self.callback = self.__callback
                self.messages = []
                self.raw_messages = []
            else :
                self.callback = callback

            self.url = 'tcp://' + str(self.host) + ':' + str(self.port)

            self.factory = pyactivemq.ActiveMQConnectionFactory(self.url)
            self.factory.username = self.username;
            self.factory.password = self.password;
            print("Creating PyActiveMQ consumer over " + ("SSL" if self.use_ssl is True else "non-SSL") + " socket " + (str(port)) + " to %s for topic %s" % (self.host, self.topic))
            self.connection = self.factory.createConnection()
            self.session = self.connection.createSession()
            self.consumer = self.session.createConsumer(self.session.createTopic(self.topic), "")
            self.listener = self.__MessageListener(self.topic, self.callback)
            self.consumer.messageListener = self.listener


        def start(self) :
            """Start consuming messages from the ActiveMQ server.  Returns immediately"""
            self.connection.start()


            self.running = True

        def stop(self) :
            """Stop consuming messages from the ActiveMQ server"""
            time.sleep(2)

            self.connection.close()
            self.running = False

        def isRunning(self) :
            """Connection still active?"""
            return self.running

        def has_messages(self) :
            """Test whether any messages have been received"""
            self.messageLock.acquire()
            try :
                return len(self.messages) > 0
            finally :
                self.messageLock.release()

        def get_messages(self) :
            """Get the current list of received messages ... the list is cleared"""
            self.messageLock.acquire()
            try :
                result = list(self.messages)
                self.messages = []
                return result
            finally :
                self.messageLock.release()

        def get_raw_messages(self) :
            """Get the list of raw messges received so far ... the list is cleared"""
            self.messageLock.acquire()
            try :
                result = list(self.raw_messages)
                self.raw_messages = []
                return result
            finally :
                self.messageLock.release()

        def __toDictionary(self, message) :
            """Convert a raw message to a dictionary"""
            if message is None : return None

            result = {}
            result[ 'expiration' ] = message.expiration
            result[ 'timestamp'  ] = message.timestamp
            result[ 'text'       ] = message.text if len(message.text) > 0 else None

            # Fetch each property in the message and put it into the dictionary.  Treat each
            # property as a string, unless specifically identified otherwise.  Use the 
            # appropriate getXXXProperty() method to fetch the value from the raw message.
            for property in message.propertyNames :
                string_type = True  # Assume a standard string type, not handled yet
                # See if this is one of the non-string properties
                for property_name, property_type in nonstring_message_properties:
                    if not string_type:  # Known not to be a string; already handled
                        break
                    if property == property_name:  # Some non-string type; handle specially
                        # ##print "Fetching " + property_name + " as type " + property_type
                        if property_type == 'long':
                            try:
                                result[ property ] = message.getLongProperty(property)
                                string_type = False  # Non-string type; handled
                            except :  # Failed conversion; ignore and leave it as a string...
                                print "\n********** error fetching '" + property + "' property as type " + property_type + " from incoming notification message! ***********"
                                print "Treating it as type string\n"
                                traceback.print_exc()
                                # (Allow this code path to continue and attempt to fetch it as a string...)
                if string_type:
                    try :
                        # ##print "Fetching " + property_name + " as type string"
                        result[ property ] = message.getStringProperty(property)
                    except :
                        print "\n********** error fetching '" + property + "' property as type string from incoming notification message! ***********\n"
                        traceback.print_exc()
                        result[ property ] = None

                # ##print "property name: " + property + "; value=" + str(result[property]) + "; type=" + str(type(result[property]))

            return result

        def __callback(self, topic, message) :
            """The default callback method to receive incoming messages"""
            self.messageLock.acquire()
            try :
                if message is not None :
                    self.messages.append(self.__toDictionary(message))
                    self.raw_messages.append(message)
            finally :
                self.messageLock.release()

        def __execute(self, connection) :
            """Start listening for messages - deprecated"""
            try :
                self.running = True
                connection.start()
                while self.running :
                    time.sleep(1)
            finally :
                self.running = False
                connection.close()


#############################################################################
#
# Class STOMP_Consumer - Private class ... do not use directly ...
#
# This class sets up an ActiveMQ message consumer using a STOMP client.
#
# It requires a callback function that will be invoked upon receiving each
# new message from the ActiveMQ server.  The callback function takes exactly
# two arguments, the topic registered when the Consumer is created and the
# incoming message from the server.
#
# Typical usage :
#
#    Create a Consumer object.
#    Call Consumer.start to begin consuming messages.
#    Cause one or more notification events to fire.
#    Loop on Consumer.isRunning to wait for consumer thread to timeout.
#    Verify the accuracy of the notification messages.
#
#############################################################################

class STOMP_Consumer() :
    """Private class ... do not use directly"""

    class __STOMPInternalListener():

            def __init__(self, topic, callback):
                self.callback = callback
                self.topic = topic

            def on_connecting(self, host_and_port):

                print "Started connecting to broker..."

            def on_connected(self, headers, message):

                print "Now connected to broker: %s" % message

            def on_disconnected(self, headers, message):

                print "No longer connected to broker: %s" % message

            def on_error(self, headers, message):

                print "Received an error: %s" % message

            def on_message(self, headers, message):
                # This method processes an HMC APi notificaiton message which
                # always have header fields, and may optionally contain a body
                # that is a string containing a JSON object.

                try :
                    # print "inside on_message block"
                    # print "H is", headers
                    # print "M is",message
                    
                    # If this is a Property Change notification or a Status Change notification, put the body into
                    # a header named 'text'.  That's where PyActiveMQ puts it, and this hides that difference from
                    # other places in our Test utilities and the testcase programs themselves.
                    if (headers['notification-type'] == 'property-change' or headers['notification-type'] == 'status-change' or headers['notification-type'] == 'log-entry'):
                        headers['text'] = message

                    self.callback(self.topic, headers)
                except :
                    print traceback.print_exc()




    def __init__(self, host, port, username, password, topic, use_ssl, callback=None) :

        """This is the constructor ... all parameters required, exception callback"""

        self.messageLock = threading.Lock()  # Control access to message queue

        self.running = False

        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.topic = topic
        self.use_ssl = use_ssl

        if callback is None :
            self.callback = self.__callback
            self.messages = []
            self.raw_messages = []
        else :
            self.callback = callback

        self._dest = "/topic/" + self.topic
        print("Creating STOMP consumer over " + ("SSL" if self.use_ssl is True else "non-SSL") + " socket " + (str(port)) + " to %s for topic %s" % (self.host, self.topic))
        self.connection = stomp.Connection([(self.host, self.port)], self.username,
                                            self.password, use_ssl=self.use_ssl,
                                            ssl_version=ssl.PROTOCOL_SSLv23)

        self._internal_listener = self.__STOMPInternalListener(self.topic, self.callback)
        self.connection.set_listener('', self._internal_listener)


    def start(self) :
        """Start consuming messages from the ActiveMQ server.  Returns immediately"""
        self.connection.start()
        self.connection.connect(wait=True)
        time.sleep(10)
        self.connection.subscribe(destination=self._dest, ack="auto")

        self.running = True

    def stop(self) :
        """Stop consuming messages from the ActiveMQ server"""
        time.sleep(2)

        self.connection.stop()
        self.running = False

    def isRunning(self) :
        """Connection still active?"""
        return self.running

    def has_messages(self) :
        """Test whether any messages have been received"""
        self.messageLock.acquire()
        try :
            return len(self.messages) > 0
        finally :
            self.messageLock.release()

    def get_messages(self) :
        """Get the current list of received messages ... the list is cleared"""
        self.messageLock.acquire()
        try :
            result = list(self.messages)
            self.messages = []
            return result
        finally :
            self.messageLock.release()

    def get_raw_messages(self) :
        """Get the list of raw messges received so far ... the list is cleared"""
        self.messageLock.acquire()
        try :
            result = list(self.raw_messages)
            self.raw_messages = []
            return result
        finally :
            self.messageLock.release()

    def __toDictionary(self, message) :
        """Convert a raw message to a dictionary"""
        if message is None : return None
        result = message
        return result

    def __callback(self, topic, message) :
        """The default callback method to receive incoming messages"""
        self.messageLock.acquire()
        try :
            if message is not None :

                # Regardless of the type specified by the HMC code that builds the JMS message, 
                # the properties always seem to arrive as strings.  Convert the non-string
                # properties to their proper type here.
                for property_name, property_type in nonstring_message_properties:
                    try:
                        if property_type == 'long':
                            # ##print "Converting " + property_name + " to " + property_type
                            message[property_name] = long(message[property_name])
                    except ValueError:  # Failed conversion; ignore and leave it as a string...
                        print "\n********** error converting '" + property_name + "' property to type " + property_type + " from incoming notification message! ***********"
                        print "Leaving it as type " + str(type(message[property_name])) + "\n"

                self.messages.append(self.__toDictionary(message))
                self.raw_messages.append(message)
        finally :
            self.messageLock.release()

    def __execute(self, connection) :
        """Start listening for messages - deprecated"""
        try :
            self.running = True
            connection.start()
            while self.running :
                time.sleep(1)
        finally :
            self.running = False
            connection.close()

#############################################################################
# Miscellaneous Functions
#############################################################################

#############################################################################
#
# Function parse_standard_options
#
# Parses command line options
#
# Standard options available to all testcases are :
#
#    --addr = IP address of the target HMC
#    --port = Port number to connect to on the target HMC
#    --user = Logon userid to use on the target HMC
#    --pass = Logon password to use on the target HMC
#    --amq-client = ActiveMQ client to use for notification messages
#    --amq-socket-type = Type of socket to use for ActiveMQ messages; either ssl or non-ssl
#    --api-version = Version of the API being tested.  Use this to override the version 
#                    information reported by the API framework.
#    
#    These options are provided primarily to support the FVT regression testing tools.  They are
#    available to all testcases:
#    --get-properties = a request to return the testcase's properties
#    --check-properties = a request to check the testcase's properties against the specified required properties
#    --run-if-applicable = a request to check the testcase's properties and then run the testcase if all requirements are met
#    --min-version = required minimum version
#    --max-version = required maximum version
#    --capability = required capability; may be specified multiple times
#    --component = required component; may be specified multiple times
#    --scenario  = required scenario type; may be specified multiple times
#    --execution-type = required execution type; may be specified multiple times
#
# NOTE : Currently, if ommitted, these values will default to :
#
#    Logon to R32 HMC ( 9.60.15.48 ) on the default WSA SSL port with user ensadmin
#    An ActiveMQ client is chosen based on what is installed; STOMP over SSL is preferred.
#
# The additional_options argument may be used to define any additional command
# line options to be permitted.  It is a list of Option objects created via
# the make_option() function in the optparse library.  For example:
#     additional_opts = [
#         make_option("--srname", dest="storage_resource_name", type="string", default="tempSR", help='The name of the storage resource to be created.  Default is %default.'),
#         make_option("--count", dest="iteration_count", metavar="COUNT", type="int", help='The number of iterations to run'),
#         make_option("--treat", dest="dessert", type="choice", choices=["candy", "soda", "fudge"], help='Your dessert choice')
#         make_option("--verbose", "-v", dest="verbose", action="store_true", default=False, help="Specify this option to get lots of output.  Default is %default."),
#         ]
#         
# Those option definitions are then passed to session_startup():
#       # Create a session and parse the command line, including our additional options
#       session = session_startup(additional_options=additional_opts)
#
# Note that it is permissible to override any of the standard options by specifying them in additional_options.
#
# If the testcase script defines any positional arguments, their Usage information
# should be specified on the additional_arguments_usage_info argument.  For example,
#      my_args_usage_info = "property_name timeout_seconds"
#
# To see the usage and help information on the command line, issue:
#         "<script_name> -h" or "<script_name> --help"
#               
# Note that this method uses os._exit(rc) in some cases rather than the more
# common sys.exit(rc).  os._exit(rc) makes a quick exit from the testcase
# script without raising any exception, including SystemExit.  This makes
# for a cleaner exit sequence in these special situations.  Note, however,
# that it also bypasses any finally block; this should be OK, since no
# session has been created yet and there is most likely no resource cleanup
# necessary at this point in testcase execution.
#
#############################################################################

def parse_standard_options(additional_options=None, additional_arguments_usage_info=None) :
    # Define the standard options
    option_list = [
       make_option(OPTION_ADDR, dest='host', type='string', default=DEFAULT_ADDR,
           help='The IP address or hostname of the target HMC.  Default=%default'),
       make_option(OPTION_PORT, dest='port', type='int', default=DEFAULT_PORT,
           help='The TCP/IP port number on which to connect to the target HMC for Web Services API requests.  Default=%default'),
       make_option(OPTION_USER, dest=OPTION_USER_DEST, type='string', default=WSA_DEFAULT_USERID,
           help='The HMC userid to use for the API request.  Default=%default'),
       make_option(OPTION_PASS, dest=OPTION_PASS_DEST, type='string', default=WSA_DEFAULT_PASSWORD,
           help='The login password for the HMC userid to use for the API request.  Default is the default user\'s standard password.'),
       make_option('--amq-client', dest='amq_client', type='choice', choices=[AMQ_CLIENT_PYACTIVEMQ, AMQ_CLIENT_STOMP],
           help='ActiveMQ client: %s or %s.  Default is %s unless it is not installed and %s is installed.'
               % (AMQ_CLIENT_PYACTIVEMQ, AMQ_CLIENT_STOMP, AMQ_CLIENT_STOMP, AMQ_CLIENT_PYACTIVEMQ)),
       make_option('--amq-socket-type', dest='amq_socket_type', type='choice', choices=[SOCKET_TYPE_SSL, SOCKET_TYPE_NON_SSL],
           help='ActiveMQ socket type: %s or %s.  Default depends on the ActiveMQ client: %s for %s; %s for %s.'
               % (SOCKET_TYPE_SSL, SOCKET_TYPE_NON_SSL, SOCKET_TYPE_SSL, AMQ_CLIENT_STOMP, SOCKET_TYPE_NON_SSL, AMQ_CLIENT_PYACTIVEMQ)),
       make_option(OPTION_API_VERSION, dest='api_version_override', metavar='API_VERSION', type='string',
           help='The version information for the API implementation being tested.  Specify this to override the version level reported by the API framework on the target HMC.'),
       # for force tags
       make_option("--include", type='string', default=""),
       make_option("--exclude", type='string', default=""),
       make_option("--variablefile", type='string', default=""),
       make_option("--outputdir", type='string', default=""),
        
       ]

    # Define our usage statement
    usage_info = "%prog [options]"  # There are no standard command line arguments, only options

    # Add any additional testcase-specific options
    if additional_options is not None:
        option_list.extend(additional_options)
    

    # Add any additional testcase-specific usage information
    if additional_arguments_usage_info is not None:
        usage_info += " " + additional_arguments_usage_info
    # Create a parser with the options
    parser = optparse.OptionParser(option_list=option_list, usage=usage_info, conflict_handler="resolve")

    # Define a group of options intended for use by the FVT regression bucket and then add the specific option definitions to the group.
    # This group will appear separate from the other command line options in the usage and help information.
    FVT_option_group = OptionGroup(parser, 'Function Verification Test (FVT) regression test options', 'These options are intended primarily for use by the FVT regression tools.'
        + '  Only one of %s, %s or %s may be specified.' % (OPTION_GET_PROPERTIES, OPTION_CHECK_PROPERTIES, OPTION_RUN_IF_APPLICABLE)
        + '  Some options may each be specified more than once.  If so, a testcase need only support one of the specified values in order to satisfy that requirement.'
        + '  These options are: %s, %s, %s and %s' % (OPTION_CAPABILITY, OPTION_COMPONENT, OPTION_SCENARIO, OPTION_EXECUTION_TYPE))
    
    # The type of operation to perform.  Only 1 of these should be specified.
    FVT_option_group.add_option(make_option(OPTION_GET_PROPERTIES, dest='get_properties', action='store_true', default=False,
        help='Denotes a request to return the testcase properties.  These are defined by the %s variable in the testcase source code.' % TESTCASE_PROPERTIES_VARIABLE_NAME))
    FVT_option_group.add_option(make_option(OPTION_CHECK_PROPERTIES, dest='check_properties', action='store_true', default=False,
        help='Denotes a request to check testcase properties against the required testcase properties specified on the command line.'))
    FVT_option_group.add_option(make_option(OPTION_RUN_IF_APPLICABLE, dest='run_if_applicable', metavar='APPLICABLE', action='store_true', default=False,
        help='Denotes a request to check properties as if %s were specified and then, if the testcase meets the specified requirements, actually execute the testcase.' % OPTION_CHECK_PROPERTIES))
    # Required API version
    FVT_option_group.add_option(make_option(OPTION_REQUIRED_VERSION, dest='required_version', metavar='VERSION', type='choice', choices=TC_API_VERSION_LIST,
        help='A required testcase property: the required API version.  The testcase must support this API level.'
             '  That is, this level must be between the testcase\'s supported minimum and maximum levels, inclusive.  Valid values are: %s' % TC_API_VERSION_LIST))
    # Testcase properties that can have multiple values.  If a property is specified more than once on the command line, a testcase is
    # considered to meet that criterion if it includes at least one of the specified values.  That is, they are logically OR'd together.
    # Then the different properties are AND'd together.
    FVT_option_group.add_option(make_option(OPTION_CAPABILITY, dest='required_capabilities', metavar='CAPABILITY', action='append', choices=TC_CAPABILITY_LIST,
        help='A required testcase property: a capability.  May be specified multiple times.  Valid values are: %s' % TC_CAPABILITY_LIST))
    FVT_option_group.add_option(make_option(OPTION_COMPONENT, dest='required_components', metavar='COMPONENT', action='append', choices=TC_COMPONENT_LIST,
        help='A required testcase property: a component.  May be specified multiple times.  Valid values are: %s' % TC_COMPONENT_LIST))
    FVT_option_group.add_option(make_option(OPTION_SCENARIO, dest='required_scenario_types', metavar='SCENARIO_TYPE', action='append', choices=TC_SCENARIO_TYPE_LIST,
        help='A required testcase property: a scenario.  May be specified multiple times.  Valid values are: %s' % TC_SCENARIO_TYPE_LIST))
    FVT_option_group.add_option(make_option(OPTION_EXECUTION_TYPE, dest='required_execution_types', metavar='EXECUTION_TYPE', action='append', choices=TC_EXECUTION_TYPE_LIST,
        help='A required testcase property: an execution type.  May be specified multiple times.  Valid values are: %s' % TC_EXECUTION_TYPE_LIST))

    # Add the group of FVT regression bucket options
    parser.add_option_group(FVT_option_group)

    (opts, args) = parser.parse_args()

    #
    # The command line options have been parsed and validated.  Some of them will be handled
    # here.  These are the FVT regression run options.  Individual testcases don't even need
    # to know that these options exist.  Handle them and then exit the testcase directly (not
    # even "finally:" blocks are executed).  If none of these special options was specified,
    # return the option and argument collections to the caller for handling of the other
    # options and arguments, if any.
    #

    # Determine and validate the type of request specified on the command line, if any
    get_properties_request = opts.get_properties
    check_properties_request = opts.check_properties
    run_if_applicable_request = opts.run_if_applicable
    option_count = ((1 if get_properties_request else 0)
                  + (1 if check_properties_request else 0)
                  + (1 if run_if_applicable_request else 0))

    if (option_count > 1):  # Only 0 (they're all optional) or 1 of these options may be specified at a time
        print 'At most 1 of the following options may be specified: %s, %s, %s' % (OPTION_GET_PROPERTIES, OPTION_CHECK_PROPERTIES, OPTION_RUN_IF_APPLICABLE)
        os._exit(WSA_EXIT_INVALID_COMMAND_LINE)  # Make a direct exit

    # Fetch the testcase properties from the testcase source code itself
    testcase_props = getattr(__main__, TESTCASE_PROPERTIES_VARIABLE_NAME, None)

    # Certain requests need the testcase properties.  Make sure they are defined.
    if get_properties_request or check_properties_request or run_if_applicable_request:
        if testcase_props is None:
            print "The testcase source code does not define the %s variable" % TESTCASE_PROPERTIES_VARIABLE_NAME
            os._exit(WSA_EXIT_MISSING_TESTCASE_PROPERTIES)  # Make a direct exit

    # Handle a request to display the testcase properties
    if get_properties_request:
        print GET_PROPERTIES_BEGIN_MARKER
        print "%s=\n%s" % (TESTCASE_PROPERTIES_VARIABLE_NAME, pprint.pformat(testcase_props))
        print GET_PROPERTIES_END_MARKER
        os._exit(WSA_EXIT_GET_PROPERTIES_SUCCESS)  # Make a direct exit

    # Handle requests that need to check the testcase properties against the required properties.
    if check_properties_request or run_if_applicable_request:
        # Check all simple string properties.  Some may have been specified multiple times on the command line.
        properties_to_check = [(testcase_props, TC_CAPABILITIES, opts.required_capabilities),
                               (testcase_props, TC_COMPONENT, opts.required_components),
                               (testcase_props, TC_SCENARIO_TYPE, opts.required_scenario_types),
                               (testcase_props, TC_EXECUTION_TYPE, opts.required_execution_types),
                              ]

        for property in properties_to_check:
            # print 'checking %s' % property[1]
            if check_testcase_requirement(property[0], property[1], property[2]) is False:
                print "The testcase does not support any required value for the '%s' property, supplied values are " % (property[1]), (property[2])
                os._exit(WSA_EXIT_REQUIREMENT_NOT_MET)  # Doesn't meet this requirement, so exit.  Make a direct exit.
    
        # If a required API version was specified, check it now by making sure it is within the
        # range defined by the testcase's minimum supported version and its maximum supported version
        # (if defined).  First make sure its minimum supported version is <= the requirement.
        required_version = opts.required_version
        if required_version is not None:
            if TC_MINIMUM_API_VERSION not in testcase_props.keys():
                print "The testcase properties do not define the %s property" % (TC_MINIMUM_API_VERSION)
                os._exit(WSA_EXIT_PROPERTY_NOT_DEFINED)  # Make a direct exit

            available_minimum_version = testcase_props[TC_MINIMUM_API_VERSION]  # Get the value of this testcase property
            # print "required & supported min versions: %s, %s" % (required_version, available_minimum_version)
            # if required_minimum_version < available_minimum_version:
            if not is_version_at_most(required_version, available_minimum_version):  # required < supported min
                print "The testcase does not support the %s required API version; the testcase supports a minimum version of %s" % (required_version, available_minimum_version)
                os._exit(WSA_EXIT_REQUIREMENT_NOT_MET)  # Make a direct exit

        # If a required maximum version was specified and the testcase provides it, check it now.  This is
        # an optional property that is not expected to be used very often.  It is intended to denote a
        # testcase that has become obsolete at a certain API level.  Make sure the testcase's maximum
        # supported version is >= the requirement.
        if required_version is not None and TC_MAXIMUM_API_VERSION in testcase_props.keys():
            available_maximum_version = testcase_props[TC_MAXIMUM_API_VERSION]  # Get the value if this testcase property
            # print "required & supported max versions: %s, %s" % (required_maximum_version, available_maximum_version)
            # if required_version > available_maximum_version:
            if not is_version_at_most(available_maximum_version, required_version):  # required > supported max
                print "The testcase does not support the %s required API version; the testcase supports a maximum version of %s" % (required_version, available_maximum_version)
                os._exit(WSA_EXIT_REQUIREMENT_NOT_MET)  # Make a direct exit

        # If we're only checking testcase requirements, all requirements are met and we're done!
        # If this is a run-if-applicable request, all requirements have been met, so continue and
        # actually execute the testcase.
        if check_properties_request:   
            print "The testcase meets the specified requirements"
            os._exit(WSA_EXIT_CHECK_PROPERTIES_SUCCESS)  # Make a direct exit

    return (opts, args)


#############################################################################
#
# This method provides a simple method to validate the response from an HTTP
# request.
#
# @param rs - the Response object returned by one of the Session methods,
#             such as Session.get, for example.
# @param vm - validation map that can contain on or more of the following:
#             status       : the expected status code from the operation
#             content-type : the expected content type in the response
#             required     : a list of required properties in the
#                            response body
#             optional     : a list of optional properties in the
#                            response body
#
# An example validation map :
#  { 'status':200,
#    'content-type':'application/json',
#    'required':[],
#    'optional':[] }
#
# All validation map parameters are optional.  Parameters that are not
# present in the map will not be used as part of the validation test.
#
# @return True is validation is successful, False otherwise
#
#############################################################################

def validate_response(rs, vm) :

    if vm is None : return True  # Nothing to validate in this case ...

    if rs is None or not isinstance(rs, Response) :
        raise ApiFatalException('Response missing or invalid', response=rs)

    # Validate the status
    if 'status' in vm and rs.status != vm[ 'status' ] :
        raise ApiException('Invalid status ' + str(rs.status) + ' ' + str(rs.reason), response=rs)

    # Validate the content type
    content = rs.headers[ WSA_HEADER_CONTENT ] if WSA_HEADER_CONTENT in rs.headers else None
    if WSA_HEADER_CONTENT in vm :
        if content is None or not content.startswith(vm[ WSA_HEADER_CONTENT ]) :
            raise ApiException('Invalid content type ' + str(content), response=rs)

    if content is not None and content.startswith(WSA_CONTENT_JSON) :
        req = vm[ 'required' ] if 'required' in vm else None
        opt = vm[ 'optional' ] if 'optional' in vm else None
        try :
            validate_dictionary(rs.body, req, opt)
        except ApiException as exception :
            exception.response = rs
            raise exception

    return True




# Verify the response is consistent with No Content (204)
# @param response Response object
def validate_no_content_response (response) :
    print
    print 'Validating that Response is a proper No Content (204) response'
    if response.status != 204 :
        print_response(response)
        raise Exception('Failed: Expected No Content status 204, got ' + str(response.status))
    if response.headers.get(WSA_HEADER_CONTENT) != None :
        print_response(response)
        raise Exception('Failed: Expected no content-type header for 204 response, got ' + str(response.headers.at(WSA_HEADER_CONTENT)))
    if (response.body != None) and (response.body != '') and (response.body != '{}') :  # Response object returns {} for no content?
        print_response(response)
        raise Exception('Failed: Expected no content in body, got ' + str(response.body))
# end validate_no_content_response

#############################################################################
#
#############################################################################

def validate_dictionary(dict, req, opt) :

    if dict is None or type(dict) is not types.DictType :
        raise ApiFatalException('Dictionary missing or invalid type')

    if req is None : req = []
    if opt is None : opt = []

    if req == [] and opt == [] : return True

    allKeys = set(dict.keys())
    reqKeys = set(req)
    result = reqKeys.difference(allKeys)
    if len(result) > 0 :
        raise ApiException('Missing required keys', keys=sorted(list(result)))

    optKeys = set(opt)
    result = allKeys.difference(reqKeys).difference(optKeys)
    if len(result) > 0 :
        raise ApiException('Extraneous keys found', keys=sorted(list(result)))

    return True


#############################################################################
# Return a list of all ensembles, after first validating the response
#############################################################################

def list_ensembles(session) :
    ensembles = None
    response = session.get(WSA_URI_ENSEMBLES)
    validate_response(response, WSA_LIST_ENSEMBLES_VALIDATE)
    for ensemble in response.body[ 'ensembles' ] :
        validate_dictionary(ensemble, WSA_LIST_ENSEMBLE_REQUIRED, [])
    return response.body[ 'ensembles' ]


#############################################################################
# Update the ensemble properties 
# ensemble_uri : the uri of the ensemble to be updated (str)
# request_body : request body containing the fields to update (dict)
#############################################################################

def update_ensemble(session, ensemble_uri, request_body):
    response = None
    print 'ensemble update body: ' + json.dumps(request_body)
    response = session.post(ensemble_uri, json.dumps(request_body))
    print 'Ensemble update response status: ' + str(response.status)
    return response


#############################################################################
# Return information about the ensemble on the system
#############################################################################

def get_ensemble_info(session) :
    print '\nGet the ensemble information'
    ensembles = list_ensembles(session)
    if len(ensembles) == 0 :
        raise Exception('No ensemble defined on system')
    ensemble_info = ensembles[0]
    ensemble_uri = ensemble_info['object-uri']
    print 'Ensemble uri is [' + ensemble_uri + ']'
    return ensemble_uri, ensemble_info


#############################################################################
# Return all the properties of the specified ensemble
#############################################################################

def get_ensemble_properties(session, ensemble) :
    response = session.get(ensemble[ 'object-uri' ])
    if api_effective_version(session) == TC_API_VERSION_ZSPHINX_GA1 :
        validate_response(response, WSA_GET_ENSEMBLE_VALIDATE_NODES)
    else :
        validate_response(response, WSA_GET_ENSEMBLE_VALIDATE)
    return response.body


#############################################################################
# Return all the properties of the ensemble identified by its URI
#############################################################################

def get_ensemble_properties_by_uri(session, ensemble_uri) :
    response = session.get(ensemble_uri)
    if api_effective_version(session) == TC_API_VERSION_ZSPHINX_GA1 :
        validate_response(response, WSA_GET_ENSEMBLE_VALIDATE_NODES)
    else :
        validate_response(response, WSA_GET_ENSEMBLE_VALIDATE)
    return response.body


#############################################################################
# Return a list of all cpcs, afer first validating the response
#############################################################################

def list_cpcs(session) :
    cpcs = None
    response = session.get(WSA_URI_CPCS)
    if response.status != 200:
        raise ApiException("ERROR: status=" + response.status + ", uri=" + WSA_URI_CPCS)
    strCPCs = str(response)
    cpcCount = strCPCs.count('object-uri')
    if cpcCount == 0 :
        raise ApiException('No cpcs defined on system')
    validate_response(response, WSA_LIST_CPCS_VALIDATE)
    for cpc in response.body[ 'cpcs' ] :
        validate_dictionary(cpc, WSA_LIST_CPC_REQUIRED, [])
    cpcs = response.body['cpcs']
    return cpcs
    

#############################################################################
# Return either the default CPC or the first cpc found in the operating state
#############################################################################

def get_operating_cpc(session) :
    print '\nGet the operating cpc'
    cpcs = list_cpcs(session)
    if len(cpcs) == 0 :
        raise Exception('No cpcs defined on system')
    # # See how many cpcs we have
    strCPCs = str(cpcs)
    n = strCPCs.count('object-uri')
    cpc_name = ''
    # # See if we have a default CPC name to find
    if DEFAULT_CPC_NAME != '' :
        # # Find the default cpc
            for i in range(0, n):
                if (cpcs[i]['name'] == DEFAULT_CPC_NAME) & (cpcs[i]['status'] == 'operating') :
                    cpc_uri = cpcs[i]['object-uri']
                    cpc_name = cpcs[i]['name']
                    print '------> cpc name: ' + cpc_name + '   uri:  ' + cpc_uri
                    break
    # # If default CPC is not found and operating, look for the first operating CPC
    if cpc_name == '' :
        # # Find an operating cpc
        for i in range(0, n):
            if (cpcs[i]['status'] == 'operating') :
                cpc_uri = cpcs[i]['object-uri']
                cpc_name = cpcs[i]['name']
                print '------> cpc name: ' + cpc_name + '   uri:  ' + cpc_uri
                break
    # # Make sure we found an operating cpc
    if cpc_name == '' :
        raise Exception('No operating cpcs defined on system')
    else :
        # cpc_uri = cpcs[0]['object-uri']
        return cpc_uri
    
    
#############################################################################
# Return either the default CPC or the first cpc found
#############################################################################

def get_cpc_new(session) :
    print '\nGet the operating cpc'
    cpcs = list_cpcs(session)
    if len(cpcs) == 0 :
        raise Exception('No cpcs defined on system')
    targetCpc = None
    for cpc in cpcs :
        if cpc['name'] == APA_TESTENV_CPC_UNDER_TEST :
            targetCpc = cpc
            break
    if targetCpc is None :
        raise ApiFatalException("Unable to find a required CPC, exiting")    
    cpc_uri = targetCpc['object-uri']
    return cpc_uri


##########################################################################################
# Return either the default virtualization host or the first found in the operating state
##########################################################################################

def get_operating_virtualization_host(session, virtualization_hosts) :
    print '\nGet the operating virtualization host'
    virtualization_host_name = None
    for virtualization_host in virtualization_hosts :
        if virtualization_host[ 'name' ] == DEFAULT_VIRTUALIZATION_HOST_NAME :
            if  virtualization_host[ 'status' ] == 'operating' :
                virtualization_host_name = virtualization_host[ 'name' ]
                break
    if virtualization_host_name is None :
        for virtualization_host in virtualization_hosts :
            if (virtualization_host[ 'status' ] == 'operating') & (virtualization_host[ 'type' ] == 'zvm')  :
                virtualization_host_name = virtualization_host[ 'name' ]
                break
    # # Make sure we found an operating virtualization host
    if virtualization_host_name is None :
        raise ApiFatalException('No zvm virtualization host present in the Ensemble or is not in the right state to perform this test')
    else :
        return virtualization_host


#############################################################################
# Return a list of virtualization-host-info objects for all virtualization
# hosts managed by the specified ensemble that match the optional query
# filter, after first validating the response
#############################################################################

def list_virtualization_hosts_by_ensemble(session, ensemble_info, query=None) :
    return list_virtualization_hosts_by_ensemble_uri(session, ensemble_info['object-uri'], query)


#############################################################################
# Return a list of virtualization-host-info objects for all virtualization
# hosts managed by the specified ensemble that match the optional query
# filter, after first validating the response
#############################################################################

def list_virtualization_hosts_by_ensemble_uri(session, ensemble_uri, query=None) :
    response = None
    response = session.get(ensemble_uri + "/nodes?name=" + WSA_DEFAULT_ZBX_NAME)
    nodes = response.body['nodes']
    node_uri = nodes[0]['element-uri']
    if query is None :
        response = session.get(node_uri + '/virtualization-hosts')
    else :
        response = session.get(node_uri + '/virtualization-hosts?' + query)
    validate_response(response, WSA_LIST_VIRT_HOSTS_VALIDATE)
    for host in response.body[ 'virtualization-hosts' ] :
        validate_dictionary(host, WSA_LIST_VIRT_HOST_REQUIRED, [])
    return response.body[ 'virtualization-hosts' ]


#############################################################################
# Returns the URI and a virtualization-host-info object for an arbitrary
# (or specific, if virtualization_host_name is specified) virtualization
# host of the specified type, managed by the specified ensemble.  Raises
# an Exception if none is found.
#############################################################################

def find_virtualization_host(session, virtualization_host_type, ensemble_uri=None, virtualization_host_name=None):
    print '\nSearching the ensemble for a virtualization_host of type ' + virtualization_host_type
    typefilter = 'type=%s' % (virtualization_host_type)

    # Get the ensemble name, and uri if not provided
    if ensemble_uri is None:
        ensemble_uri, ensemble_info = get_ensemble_info(session)
        ensemble_name = ensemble_info['name']
    else:
        ensemble_properties = get_ensemble_properties_by_uri(session, ensemble_uri)
        ensemble_name = ensemble_properties['name']
    
    # virtualization_hosts = list_virtualization_hosts_by_ensemble_uri(session, ensemble_uri, 'name=ZBX51.*&'+typefilter)
    response = session.get(ensemble_uri + "/nodes?name=" + WSA_DEFAULT_ZBX_NAME)
    nodes = response.body['nodes']
    if len(nodes) == 0 :
        raise Exception('No suitable node (name=' + WSA_DEFAULT_ZBX_NAME + ') is defined in ensemble ' + ensemble_name)
    node_uri = nodes[0]['element-uri']
    response = session.get(node_uri + "/virtualization-hosts?" + typefilter)
    virtualization_hosts = response.body['virtualization-hosts']
    if len(virtualization_hosts) == 0 :
        raise Exception('No ' + virtualization_host_type + ' virtualization hosts defined in ensemble ' + ensemble_name)

    # Set the virtualization host name to search for, if any
    vh_name = None
    if virtualization_host_name is None:
        # If we're looking for a zvm virtualization host on the R32 ensemble, restrict Test usage to a specific virtualization host
        if virtualization_host_type == 'zvm':
            if ensemble_name == ENSEMBLE_NAME_R32:
                vh_name = PREFERRED_ZVM_VIRTUALIZATION_HOST_R32
    else:
        vh_name = virtualization_host_name

    virtualization_host_info = None  # Assume no appropriate virtualization host will be found
    if vh_name is None:
        virtualization_host_info = virtualization_hosts[0]  # Use the first one (arbitrary choice)
    else:
        for virtualization_host in virtualization_hosts:  # Iterate over all vh info objects that match the desired vh type
            if virtualization_host['name'] == vh_name:  # Found it
                virtualization_host_info = virtualization_host
        if virtualization_host_info is None:
            raise Exception('No ' + virtualization_host_type + ' virtualization host with name ' + vh_name + ' is defined in ensemble ' + ensemble_name)

    virtualization_host_uri = virtualization_host_info['object-uri']
    print 'Virtualization host uri is [' + virtualization_host_uri + ']; name is [' + virtualization_host_info['name'] + ']'
    return virtualization_host_uri, virtualization_host_info


#############################################################################
# Returns the URI and a virtualization-host-info object for a specified
# virtualization host managed by the specified ensemble.  Raises
# an Exception if none is found.
#############################################################################

def find_virtualization_host_by_name(session, virtualization_host_name, ensemble_uri=None):
    print '\nSearching the ensemble for a virtualization_host of name ' + virtualization_host_name
    namefilter = 'name=%s' % (virtualization_host_name)

    # Get the ensemble name, and uri if not provided
    if ensemble_uri is None:
        ensemble_uri, ensemble_info = get_ensemble_info(session)
        ensemble_name = ensemble_info['name']
    else:
        ensemble_properties = get_ensemble_properties_by_uri(session, ensemble_uri)
        ensemble_name = ensemble_properties['name']

    # virtualization_hosts = list_virtualization_hosts_by_ensemble_uri(session, ensemble_uri, query=namefilter)
    response = session.get(ensemble_uri + "/nodes?name=" + WSA_DEFAULT_ZBX_NAME)
    nodes = response.body['nodes']
    node_uri = nodes[0]['element-uri']
    response = session.get(node_uri + "/virtualization-hosts?" + namefilter)
    virtualization_hosts = response.body['virtualization-hosts']
    if len(virtualization_hosts) == 0 :
        raise Exception('No ' + virtualization_host_name + ' virtualization hosts defined in ensemble ' + ensemble_name)

    virtualization_host_info = virtualization_hosts[0]
    virtualization_host_uri = virtualization_host_info['object-uri']

    print 'Virtualization host uri is [' + virtualization_host_uri + ']; name is [' + virtualization_host_info['name'] + ']'
    return virtualization_host_uri, virtualization_host_info


#############################################################################
# Returns the URI of a virtual server object with the specified name owned
# by the specified virtualization host.  If return_response is True, then
# the response object is always returned; otherwise, the URI is returned
# or an exception is raised.
#############################################################################

def find_virtual_server_in_virtualization_host(session, virtualization_host_uri, virtual_server_name, return_response=False) :
    # Find the VS within the specified VH
    response = session.get(virtualization_host_uri + "/virtual-servers?name=" + virtual_server_name)
    if response.status != 200:
        msg = "An error occurred fetching virtual server information for the virtualization host"
        print msg
        if return_response :
            return response
        else :
            print response
            raise Exception(msg)

    virtual_servers = response.body["virtual-servers"]
    if len(virtual_servers) == 0 :
        msg = "The virtualization host has no virtual server with name " + virtual_server_name
        print msg
        if return_response :
            return response
        else :
            print response
            raise Exception(msg)

    if return_response :
        return response
    else :
        return virtual_servers[0]["object-uri"]


#############################################################################
# Startup method to create session and logon ...
# Connection parameters (host, port, user, and pwd) should not be overridden
# by test scripts unless there is an explicit need (eg log in under different
# users to verify access permission)
# @param host - IP address of the target HMC (str)
# @param port - Port number to connection on the target HMC (int)
# @param user - Logon userid to use on the target HMC (str)
# @param pwd  - Logon password to use on the target HMC(str)
# @param additional_options - any additional command line option definitions.
#               See parse_standard_options() and the Session class for more details.
#               (list of Option objects created via make_option())
# @param additional_arguments_usage_info - Usage information for any additional
#               command line arguments.  See parse_standard_options() and the
#               Session class for more details. (str)
# @param amq-client - ActiveMQ client to use for notification messages
# @param amq-socket-type - Type of socket to use for ActiveMQ messages;
#               either ssl or non-ssl
#
# Note that the Session __init__ method calls parse_standard_options(), which 
# uses os._exit(rc) in some cases rather than the more common sys.exit(rc).
# See the prolog of parse_standard_options for more details.
#############################################################################

#############################################################################
# Find the object with a given name from a list of objects
#############################################################################
def find_object_by_name(session, object_list, object_name) :
    result = None
    for obj in object_list :
        if type(obj['name']) is unicode :
            obj_name = obj['name'].encode('utf-8')
        if (obj_name == object_name) :
            result = obj
    return result


def session_startup(host=None, port=None, user=None, pwd=None, verbose=False, additional_options=None, additional_arguments_usage_info=None, amq_client=None, amq_socket_type=None) :
    session = Session(host, port, user, pwd, additional_options, additional_arguments_usage_info, amq_client, amq_socket_type)

    # Now open the session by establishing an HTTP connection to the target HMC
    if verbose :
        print 'Connecting to', session.host(), session.port(), 'as', session.userid(), 'at', get_time_stamp()
    session.open()
    if verbose :
        print 'Session ID: \t%s' % session.session()

    return session


#############################################################################
# Determine if the API version being tested is at least as recent (high) as
# the specified API version.  The version information for the API implementation
# being tested comes from the API framework itself (GET /api/version) unless it
# has been overridden via the --api-version command line option.  The version
# strings are expected to be in dotted decimal notation (e.g., '1.1', '1.3.2').
#
# This method is intended for use by testcases that test function that was
# added or changed in an incompatible fashion after the initial API release.
# The testcase can use this function in order to know what behavior to expect
# from the API(s) it is testing.
# 
# Returns:
#    True if it is; False otherwise
#############################################################################

def is_api_version_at_least(session, version_to_check):
    api_version = api_effective_version(session)
    # print 'api version = %s' % api_version
    # return (api_version >= version_to_check)  #??? Need to do a real implementation of this that can handle all valid version formats!  (For example, need to be able to compare "1.2" and "1.12")
    return is_version_at_least(version_to_check, api_version)


# See is_api_version_at_least() above for description
def is_version_at_least(version_to_check, api_version):
    # Split each version string into its numeric parts
    api_version_parts = api_version.split('.')
    version_to_check_parts = version_to_check.split('.')

    # Make sure both version strings are in dotted decimal format.  If not, we can't perform
    # a meaningful numeric comparison, so just do a straight string comparison.
    pattern = '[0-9]+(\.[0-9]+)*$'  # n[.n]*   e.g. '1.2', '2.3.25.7', '2.0'
    if re.match(pattern, version_to_check) is None or re.match(pattern, api_version) is None:
        print "is_version_at_least: ill-formed version number; must be dotted decimal format.  Using a simple string comparison."
        return (api_version >= version_to_check)

    # Iterate over the numeric parts of the input version number and compare them to the
    # corresponding parts of the session's API version number.  Once an inequality is found,
    # we know which is greater.
    for i in xrange(len(version_to_check_parts)):
        version_to_check_part = int(version_to_check_parts[i])
        if len(api_version_parts) >= i + 1:
            api_version_part = int(api_version_parts[i])
        else:  # Not enough parts in api_version; supply a 0
            api_version_part = 0
        if version_to_check_part < api_version_part:
            return True
        elif version_to_check_part > api_version_part:
            return False
        # Equal, need to look at next part, if any


    # We checked all of the numeric parts of the input version number without finding
    # an inequality.  This means that either the versions are completely equal or 
    # version_to_check has fewer parts, which means that it cannot be greater than
    # api_version.  Thus it must be <=, so we return True.
    return True


#############################################################################
# Determine if the API version being tested is exactly the same as
# the specified API version.  The version information for the API implementation
# being tested comes from the API framework itself (GET /api/version) unless it
# has been overridden via the --api-version command line option.
# 
# Returns:
#    True if it is; otherwise, False.
#############################################################################

def is_api_version_exactly(session, version_to_check):
    api_version = api_effective_version(session)
    # print 'api version = %s' % api_version
    return (api_version == version_to_check)


#############################################################################
# Determine if the API version being tested is at most as recent (high) as
# the specified API version.  The version information for the API implementation
# being tested comes from the API framework itself (GET /api/version) unless it
# has been overridden via the --api-version command line option.  The version
# strings are expected to be in dotted decimal notation (e.g., '1.1', '1.3.2').
#
# This method is intended for use by testcases that test function that was
# removed or changed in an incompatible fashion at some point.  The testcase
# can use this function in order to know what behavior to expect from the
# API(s) it is testing.
# 
# Returns:
#    True if it is; False otherwise
#############################################################################

def is_api_version_at_most(session, version_to_check):
    api_version = api_effective_version(session)
    return is_version_at_most(version_to_check, api_version)


# See is_api_version_at_most() above for description
def is_version_at_most(version_to_check, api_version):
    # Split each version string into its numeric parts
    api_version_parts = api_version.split('.')
    version_to_check_parts = version_to_check.split('.')

    # Make sure both version strings are in dotted decimal format.  If not, we can't perform
    # a meaningful numeric comparison, so just do a straight string comparison.
    pattern = '[0-9]+(\.[0-9]+)*$'  # n[.n]*   e.g. '1.2', '2.3.25.7', '2.0'
    if re.match(pattern, version_to_check) is None or re.match(pattern, api_version) is None:
        print "is_version_at_most: ill-formed version number; must be dotted decimal format.  Using a simple string comparison."
        return (api_version <= version_to_check)

    # Iterate over the numeric parts of the session's API version number and compare them to the
    # corresponding parts of the input version number.  Once an inequality is found,
    # we know which is greater.
    for i in xrange(len(api_version_parts)):
        api_version_part = int(api_version_parts[i])
        if len(version_to_check_parts) >= i + 1:
            version_to_check_part = int(version_to_check_parts[i])
        else:  # Not enough parts in version_to_check; supply a 0
            version_to_check_part = 0
        if api_version_part < version_to_check_part:
            return True
        elif api_version_part > version_to_check_part:
            return False
        # Equal, need to look at next part, if any


    # We checked all of the numeric parts of the API version number without finding
    # an inequality.  This means that either the versions are completely equal or 
    # api_version has fewer parts, which means that it cannot be greater than
    # version_to_check.  Thus it must be <=, so we return True.
    return True

# Return the "effective" version (the version reported by the HMC itself, or the override
# value from the command line (if specified).
def api_effective_version(session):
    return session.api_version() if session.api_version_override() is None else session.api_version_override()

#############################################################################
# Determine if the specified WS API feature is available to the current session.
# 
# Returns:
#    True if the feature is available; otherwise, False.
#############################################################################

def is_feature_available(session, feature):
    features = session.api_features()
    return (features is not None and feature in features)


#############################################################################
# Check the supplied testcase properties to see if they meet at least one of
# the required values for the specified property.  This is effectively a
# logical OR of the required property values.
# 
# Returns:
#    True if the testcase supports at least one of the required property
#    values; otherwise, False.
#############################################################################

def check_testcase_requirement(testcase_properties, property_name, required_properties):
    if required_properties is None:
        required_found = True
    else:
        # Check required property; these are OR'd together
        required_found = False  # Something is required; assume we don't have it

        if property_name in testcase_properties.keys():
            available = testcase_properties[property_name]
            for r in required_properties :
                # Many requirement values are accepted in upper or lower case, so 
                # convert everything to lowercase before looking for a match.
                # We currently support testcase properties whose values are of
                # type string or list.
                # if r.upper() in available:
                if type(available) is types.StringType:  # A string
                    if r.lower() == available.lower():
                        required_found = True
                        break
                else:  # Assume a list
                    if r.lower() in make_lowercase_copy(available):
                        required_found = True
                        break
        else:
            print "The testcase properties do not define the %s property" % (property_name)

    return required_found


#############################################################################
# Exit test code cleanly ...
# By default, all "temporary" objects are deleted, and any "admin sessions"
# and "temporary sessions" are shutdown after the specified session is shutdown.
#############################################################################

def session_shutdown(session, verbose=True, delete_temporary_objects=True, delete_admin_sessions=True, delete_temporary_sessions=True) :
    if session is not None :
        if verbose :
            print 'Disconnecting from', session.hmc_name(), 'at', session.host(), session.port(), 'as', session.userid(), 'at', get_time_stamp()
        try :
            session.close()
        except (ApiException, ApiFatalException) as exception :
            print
            print 'Exception raised during shutdown ...'
            print exception
            print


    # Delete temporary sessions first, in case one is for a temporary user that we're
    # about to delete in delete_all_temporary_objects().
    if delete_temporary_sessions:
        delete_all_temporary_sessions()

    if delete_temporary_objects:
        delete_all_temporary_objects()

    if delete_admin_sessions:
        delete_all_admin_sessions()


#############################################################################
# This function returns True if value is a number, False otherwise.
#############################################################################

def isNumeric(value) :
    try :
        float(value)
    except (ValueError) :
        return False
    return True


#############################################################################
#
# This function prints out data as formatted columns.
#
# Formatting is simple : Strings will be left-justified
#                        Numbers will be right-justified
#
# Input :
#
#   The keys parameter is a list of keys whose values should be printed
#   The data parameter is a list of dictionaries
#
# No error checking is done currently ...
#
# Example :
#
#    keys = [ 'name', 'status', 'type' ]
#    data = [ { 'name':'abc',     'type':'foo',    'status':'operating',     'count':1    },
#             { 'name':'abcde',   'type':'bar',    'status':'not_operating', 'count':10   },
#             { 'name':'ab',      'type':'foobar', 'status':'status_check',  'count':100  },
#             { 'name':'abcdefg', 'type':'fubar',  'status':'starting',      'count':1000 } ]
#
#    prettyPrint( data, keys ) will print ...
#
#       abc     operating     foo
#       abcde   not_operating bar
#       ab      status_check  foobar
#       abcdefg starting      fubar
#
#############################################################################

def prettyPrint(data, keys) :
    if data is None or len(data) == 0 : return
    if keys is None or len(keys) == 0 : return
    width = {}
    for key in keys :
        width[ key ] = max([ len(str(row[ key ])) for row in data ])
    for row in data :
        for key in keys :
            if isNumeric(row[ key ]) :
                print str(row[ key ]).rjust(width[ key ]),
            else :
                print str(row[ key ]).ljust(width[ key ]),
        print


# Print a Response object with formatted headers and body
# @param response - API response (Response)
def print_response(response, sort_body=True) :
    if response is None or response.__class__ is not Response :
        raise ApiFatalException('response is missing or invalid type')
    print 'Response Status  : ' + str(response.status)
    print 'Response Reason  : ' + str(response.reason)
    print 'Response Headers :'
    print json.dumps(response.headers, sort_keys=sort_body, indent=1, separators=(',', ':'))
    print 'Response Body    :'
    print json.dumps(response.body, sort_keys=sort_body, indent=1, separators=(',', ':'))
    if 'stack' in response.body:
        print 'stack (again, but in a more programmer-friendly format):'
        print response.body['stack']
    return
# end print_response


# Print information in a formatted fashion from a response object and an optional response body.
# This is useful for streamed responses; see return_full_response in wsautils.py and the 
# read_response_streamed() function.
def print_response_info(response, response_body=None) :
    print 'Response Status  : ' + str(response.status)
    print 'Response Reason  : ' + str(response.reason)
    print 'Response Headers :'
    print json.dumps(dict (response.getheaders()), indent=1, separators=(',', ':'))
    print 'Response Body    :'
    if response_body is None:
        print json.dumps(response.read(), indent=1, separators=(',', ':'))
    else:
        body = json.loads(response_body)
        print json.dumps(body, indent=1, separators=(',', ':'))
    return
   # end print_response_info


# Print a line(s) between separator lines so that they stand out among the testcase output.
# Optional text can be included in the separator line that precedes the lines and the one 
# that follows the lines.  The length and composition of the separator line can by customized
# with input parameters.
def print_between_separator_lines(lines, header_text=None, footer_text=None, length=90, box_char="=", blank_lines=1):
    if header_text == None:
        line = ""
    else:
        box_char_count = (length - len(header_text) - 2) / 2
        line = "%s %s " % (box_char * box_char_count, header_text)  # Leading box chars and header text

    header_line = "%s%s%s" % ("\n"*blank_lines, line, box_char * (length - len(line)))  # Add the blank lines and trailing box chars
    print header_line

    # Write all of the input lines
    for line in lines:
        print line
    
    if footer_text == None:
        line = ""
    else:
        box_char_count = (length - len(footer_text) - 2) / 2
        line = "%s %s " % (box_char * box_char_count, footer_text)  # Leading box chars and footer text

    footer_line = "%s%s%s" % (line, box_char * (length - len(line)), "\n"*blank_lines)  # Add the trailing box chars and blank lines
    print footer_line


#############################################################################
#
# Filter a list of dictionaries based on keys and values
#
# This function is a "generator", meaning its output should be wrapped
# in a list in order to iterate over the results.
#
# The following snippet will return all the dictionaries in the list that
# contain the key 'foo'.
#
# data = [ { 'foo':'foo1', 'bar':'bar1' }, { 'bar':'bar2', 'baz':'baz1' } ]
# func = lambda k, v : k == 'foo'
# print list( filter_dictionary( data, func ) )
#
# The following snippet will return all the dictionaries in the list that
# contain the key 'bar' with the value of 'bar2'
#
# data = [ { 'foo':'foo1', 'bar':'bar1' }, { 'bar':'bar2', 'baz':'baz1' } ]
# func = lambda k, v : k == 'bar' and v == 'bar2'
# print list( filter_dictionary( data, func ) )
#
#############################################################################

def filter_list(data, predicate=lambda k, v: True) :
    for d in data:
         for k, v in d.items():
               if predicate(k, v):
                    yield d

#########################################################################
# Determine the Output body, response, and reason code
#
# NOTE : The Response object has been updated to raise an
# ApiFatalException if the HTTP headers indicate a content type of json,
# but the response body fails to parse with json.loads.
# This negates the need for 'determine' to check for a malformed body
# with a subsequent return code of '2'.
#########################################################################

def determine(response, status_code, reason_code) :

    status = response.status
    if 'http-status' in response.body :
        status = response.body[ 'http-status' ]
    reason = None
    if 'reason' in response.body :
        reason = response.body[ 'reason' ]
    if status == status_code and reason == reason_code :
        return(0)
    else :
        return(1)
    
# added by lv start
def determine_with_raise_exception(response, status_code, reason_code) :

    status = response.status
    if 'http-status' in response.body :
        status = response.body[ 'http-status' ]
    reason = None
    if 'reason' in response.body :
        reason = response.body[ 'reason' ]
    if status == status_code :
        if reason == reason_code :
            return (0)
        else: 
            raise ApiException('expected reason code' + str(reason_code) + ' not seen')
    else :
        raise ApiException('expected status code' + str(status_code) + ' not seen')
# added by lv end


#########################################################################
# Get the current time, formatted
#########################################################################
def get_time_stamp() :
    return time.strftime("%Y%m%d %H:%M:%S %z", time.localtime())
# end get_time_stamp


#########################################################################
# Get the fully-qualified filename of the current testcase
#########################################################################

def get_testcase_full_filename ():
    return sys.argv[0]


#########################################################################
# Get the testcase ID for the current testcase, based on its filename,
# or for a specified filename.
# The expected format for testcase filenames is
#           <comp>_<id>.py
# where <comp> is the component (e.g., svm, vsm, lpar) and <id> is the
# testcase ID number.  For example, vsm_3588.py
#########################################################################

def get_testcase_id (filename=None):
    name = get_testcase_full_filename() if filename == None else filename
    basename = os.path.basename(name)  # Just the filename, no path
    (name, ext) = os.path.splitext(basename)  # Separate name from extension (e..g, svm_3588)
    parts = string.split(name, '_')  # Split at underscore (e.g., 'svm', '3588')
    id = parts[len(parts) - 1]  # ID is the last one of the parts
    return id




def get_files_from_se(remote_files, local_zip_file):
    return
# Get the name of the user's notification topic for a specified topic type
#
# Inputs:
# - requested_topic_type: the type of topic to find.  Must be a valid topic type as
#                         returned by the Get Notification Topics operation:
#                         'object', 'job', 'audit' or 'security'.
#
# Returns: the name of the topic, or None if there is no such topic for the user (e.g.,
#          the user is not authorized to connect to it).
#
# Any failure is reported via an exception
def get_notification_topic(session, requested_topic_type):
    """Get the name of the user's notification topic for the specified topic type"""

    # Make sure the targetted HMC supports the request required to fetch the notification topics
    if not is_api_version_at_least(session, TC_API_VERSION_ZSPHINX_GA1):
        raise ApiFatalException('The targetted HMC (effective version %s) does not support audit or security notifications; must be version %s or later' % (api_effective_version(session), TC_API_VERSION_ZSPHINX_GA1))

    valid_topic_types = ['object', 'job', 'audit', 'security']
    if requested_topic_type not in valid_topic_types:
        raise ApiException("get_notification_topic(): Invalid topic type: " + requested_topic_type)
    true_topic_type = requested_topic_type + "-notification"  # The name returned by Get Notification Topics

    # Issue a Get Notification Topics request to get all of the user's authorized topics
    uri = "/api/sessions/operations/get-notification-topics"
    response = session.get(uri)
    if response.status != 200:
        raise ApiException("Get Notification Topics operation failed", response)
    topics = response.body['topics']

    if len(topics) == 0:  # No topics!  Should never happen, per the doc
        print 'User is not authorized for any notification topics - this should never happen!'
        return None

    # Iterate over the user's authorized topics looking for the specified one
    for topic in topics:
        topic_type = topic['topic-type']
        topic_name = topic['topic-name']
#       print 'Topic type: %s, topic_name: %s' % (topic_type, topic_name)
        if topic_type == true_topic_type:  # Found it
            return topic_name

    # Not found
    return None


# Issue the provided request and return the response along with a string containing 
# the formatted request and response.  This formatted version is suitable for inclusion
# in the HMC Web Services API external customer publication.  It contains:
# - the caption text for the request example
# - the HTTP method and full request URI
# - certain request headers
# - the request body, if any, alphabetized, nicely formatted and indented
# - the caption text for the response example
# - the HTTP status code and its meaning (e.g., "201 (Created)")
# - certain response headers
# - the response body, if any, alphabetized, nicely formatted and indented
#
# The operation_name should be the full name by which the operation is known in the external book
# The URI may contain query parms.  This is handy for limiting the size of the response body
# for List <class> operations.  It is OK to publish these, but not necessary.
# The request_body is a dictionary (and is optional).
def capture_example_for_book(session, operation_name, uri, method="get", request_body=None):
    indent_amount = 3
    request_headers_to_publish_get = [WSA_HEADER_RQ_SESSION]
    request_headers_to_publish_post = [WSA_HEADER_RQ_SESSION,
                                       WSA_HEADER_CONTENT_TYPE,
                                       WSA_HEADER_CONTENT_LENGTH]
    request_headers_to_publish_delete = [WSA_HEADER_RQ_SESSION]
    response_headers_to_publish = [WSA_HEADER_RESP_SERVER,
                                   WSA_HEADER_RESP_TRANSFER_ENCODING,  # "chunked" is of interest
                                   WSA_HEADER_RESP_LOCATION,
                                   WSA_HEADER_RESP_CACHE_CONTROL,
                                   WSA_HEADER_RESP_DATE,
                                   WSA_HEADER_CONTENT_TYPE,
                                   WSA_HEADER_CONTENT_LENGTH]

    if method == 'get':
        request_headers_to_publish = request_headers_to_publish_get
        response = session.get(uri)
    elif method == 'post':
        request_headers_to_publish = request_headers_to_publish_post
        response = session.post(uri, json.dumps(request_body))
    elif method == 'delete':
        request_headers_to_publish = request_headers_to_publish_delete
        response = session.delete(uri)

    request_headers = response.request.headers
    response_headers = response.headers

    # First format the request URI, filtered headers and body
    formatted_request_response = "\n\n%s: Request\n\n" % operation_name
    formatted_request_response += "\n%s %s %s" % (method.upper(), uri, "HTTP/1.1")

    for header_name in request_headers_to_publish:
        formatted_request_response += "\n%s: %s" % (header_name, request_headers[header_name])

    if request_body != None:
        formatted_request_body = json.dumps(request_body, sort_keys=True, indent=indent_amount, separators=(',', ':'))
        formatted_request_response += "\n" + formatted_request_body

    #------- end request, begin response --------
    # Noe format the filtered response headers and the response body
    formatted_request_response += "\n\n%s\n\n%s: Response\n\n" % (20 * '-', operation_name)
    formatted_request_response += "\n%s %s" % (response.status, response.reason)

    for header_name in response_headers_to_publish:
        if header_name in response_headers.keys():
            formatted_request_response += "\n%s: %s" % (header_name, response_headers[header_name])

    if response.status == 204 or response.body == None:
        formatted_response_body = "\n<No response body>"
    else:  # There is a response body; make it look pretty
        formatted_response_body = json.dumps(response.body, sort_keys=True, indent=indent_amount, separators=(',', ':'))
    formatted_request_response += "\n" + formatted_response_body

    # Formatting is complete

#   # Make sure the request succeeded; assume any 2xx indicates success
#   if response.status < 200 or response.status > 299:
#       print_response(response)
#       raise ApiException("The request appears to have failed.  URI '%s' returned HTTP status code %d (%s)" % (uri, response.status, response.reason))

    # Return the complete Response object and the formatted request/response string
    return response, formatted_request_response


#########################################################################
#                  "Temporary object" support
#########################################################################

# Add a temporary object to the registry.  All objects in the registry will
# be deleted by default when the session is shutdown.  The object must be
# of a type that is supported by the "temporary object" support.
# See the temporary_object_types_deletion_order and temporary_object_types_info
# constants in wsaconst.py.
def register_temporary_object(temporary_object_uri):
    if temporary_object_uri is not None:
        if is_supported_temporary_object_type(temporary_object_uri):
            wsaglobals.global_temporary_objects_list.append(temporary_object_uri)
        else:
            raise ApiFatalException('URI "%s" does not designate an object of a type that is supported by the "temporary object" support in wsautils' % temporary_object_uri)


# Remove a temporary object from the registry
def deregister_temporary_object(temporary_object_uri):
    if temporary_object_uri is not None:
        wsaglobals.global_temporary_objects_list.remove(temporary_object_uri)


# Gets a copy of the list of all registered temporary objects.
# Use register_temporary_object() and deregister_temporary_object()
# to update this list if needed.
def get_temporary_objects_list():
    return list(wsaglobals.global_temporary_objects_list)  # Return a copy


# Determine if the specified URI designates an object of a type that is supported
# by the "temporary object" support.
def is_supported_temporary_object_type(uri):
    if uri is None or not isinstance(uri, types.StringTypes):  # Not a string (likely to be a Response object from a failed request...)
        return False
    
    for info_entry in temporary_object_types_info.values():
        uri_prefix = info_entry[KEY_URI_PREFIX]
        if uri.startswith(uri_prefix):  # It's a supported type
            return True
    return False


# Delete all temporary objects in the registry.  This method is intended to be
# called during session shutdown immediately before testcase exit.
def delete_all_temporary_objects():
    temporary_objects_list = get_temporary_objects_list()  # Get a copy to iterate over; the real list gets updated
    if temporary_objects_list is not None and len(temporary_objects_list) > 0:  # There are temporary objects to be deleted
        print '\nTemporary objects to delete: %d' % len(temporary_objects_list)

        # Iterate over all supported object types and delete all instances of each type,
        # then move on to the next type
        for object_type in temporary_object_types_deletion_order:  # Go in a certain order, since it sometimes matters
            info_entry = temporary_object_types_info[object_type]  # Get handling info about the current object type
            uri_prefix = info_entry[KEY_URI_PREFIX]
#           print 'Looking for temporary objects with a URI prefix of "%s"' % uri_prefix
            
            # Iterate over all temporary objects in the registry, searching for those
            # of the type we're currently handling.  Delete each as it is found and 
            # remove it from the registry.
            for uri in temporary_objects_list:
                if uri is not None and uri.startswith(uri_prefix):  # Its type matches the type we're handling now
                    try:
                        admin_user = info_entry[KEY_ADMIN_USERID]

                        admin_session = get_admin_session(admin_user)

                        print 'Using %s to delete temporary object: %s' % (admin_user, uri)
                        response = admin_session.delete(uri)
                        if response.status != 204:
                            print '\nError deleting temporary object: %s\n%s' % (uri, response)

                        deregister_temporary_object(uri)  # Remove it from the list of temporary objects, since we've deleted it
#                       print 'There are %d temporary objects left to delete' % len(wsaglobals.global_temporary_objects_list)
                    except:
                        print 'Caught exception!!'
                        traceback.print_exc()
                        print 'Continuing with any remaining temporary objects...'
        print

    # Get a current copy of the list; check to see if it's empty (it should be)
    temporary_objects_list = get_temporary_objects_list()
    if len(temporary_objects_list) > 0:  # Hmmmm, must have had an error trying to delete something; tell the user
        print '\n\n!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!'
        print 'Not all temporary objects were deleted.  There are still %d temporary objects in the registry.' % len(temporary_objects_list)
        print '\n%s\n' % temporary_objects_list
        print '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n'


# Get a Session authenticated as the specified userid.  This method is intended for use when
# a priviledged (admin-type) user is required for performing scenario setup in the beginning
# of a testcase (e.g., creating objects, setting properties)and at the end when that setup is
# being undone (e.g., deleting temporary objects, resetting properties back to original values).
# These sessions are cached and can be reused.  They are cleaned up automatically during testcase
# exit.  There are constants for the standard system-defined  userids (e.g., 
# ACCCES_ADMINISTRATOR, ENSEMBLE_ADMINISTRATOR) in wsaconst.py.
def get_admin_session(admin_userid):
    if admin_userid in wsaglobals.global_admin_sessions:
        admin_session = wsaglobals.global_admin_sessions[admin_userid]
#       print 'fetched cached session: %s' % admin_session
    else:
        admin_session = session_startup(user=admin_userid, additional_options=wsaglobals.global_saved_additional_options)
        wsaglobals.global_admin_sessions.update({admin_userid : admin_session})
#       print 'created and cached new session: %s' % admin_session

#   print 'There are %d admin sessions' % len(wsaglobals.global_admin_sessions)
#   print 'Returning admin session for admin user %s: %s' % (admin_userid, admin_session)
    return admin_session


# Get a Session object authenticated as the system-defined user that is appropriate for performing
# administrative operations relative to the specified URI.  If no specific administrator has been
# identified in the uri_admin_info map, then a session authenticated as PEDEBUG is returned.
# These sessions are cached and can be reused.  They are cleaned up automatically during testcase exit.
def get_admin_session_for_uri(uri):
    admin_session = None
    # See if the specified URI has an associated administrator userid
    for uri_prefix in uri_admin_info:
        if uri.startswith(uri_prefix):
            admin_session = get_admin_session(uri_admin_info[uri_prefix])
    if admin_session == None:
        admin_session = get_admin_session(PEDEBUG)
    return admin_session


# Delete all (cached) admin sessions created by get_admin_session().
# This method is intended to be called during session shutdown immediately before testcase exit.
def delete_all_admin_sessions():
    admin_sessions = dict(wsaglobals.global_admin_sessions)  # Make a copy to iterate over; the real list gets updated
    if admin_sessions is not None and len(admin_sessions) > 0:  # There are admin sessions to be deleted
        print '\nAdmin sessions to shutdown: %d' % len(admin_sessions)
        for admin_user_name in admin_sessions.keys():
            try:
                admin_session = admin_sessions[admin_user_name]
                print 'Shutting down session for admin user: %s' % admin_user_name
                # Shutdown this admin session.  Specify options on the session_shutdown() call so that
                # it only deletes this session and nothing else, because we don't want to interfere with
                # the very deliberate order in which the various objects and sessions are cleaned up.
                session_shutdown(admin_session, delete_temporary_objects=False, delete_admin_sessions=False, delete_temporary_sessions=False)  # Delete just the session, and nothing else
                del wsaglobals.global_admin_sessions[admin_user_name]  # Remove it from the list of admin sessions
            except:
                print 'Caught exception!!'
                traceback.print_exc()
                print 'Continuing with any remaining admin sessions...'

#   print 'There are now %d admin sessions' % len(wsaglobals.global_admin_sessions)


# Delete all temporary sessions in the registry.  This method is intended to be
# called during session shutdown immediately before testcase exit.
def delete_all_temporary_sessions():
    temporary_sessions = get_temporary_sessions()  # Make a copy to iterate over; the real list gets updated
    if temporary_sessions is not None and len(temporary_sessions) > 0:  # There are admin sessions to be deleted
        print '\nTemporary sessions to shutdown: %d' % len(temporary_sessions)
        for temporary_session in temporary_sessions:
            try:
                print 'Shutting down temporary session for user: %s' % temporary_session.userid()
                # Shutdown this temporary session.  Specify options on the session_shutdown() call so that
                # it only deletes this session and nothing else, because we don't want to interfere with
                # the very deliberate order in which the various objects and sessions are cleaned up.
                session_shutdown(temporary_session, delete_temporary_objects=False, delete_admin_sessions=False, delete_temporary_sessions=False)
                wsaglobals.global_temporary_sessions.remove(temporary_session)  # Remove it from the list of temporary sessions
            except:
                print 'Caught exception!!'
                traceback.print_exc()
                print 'Continuing with any remaining temporary sessions...'



# Gets a copy of the list of all registered temporary sessions.
def get_temporary_sessions():
    return list(wsaglobals.global_temporary_sessions)  # Return a copy

def start_receiving_messages(session):
    session.start_receiving_messages()
    
def stop_receiving_messages(session):
    session.stop_receiving_messages()
    msgs = session.get_received_messages()
    print msgs
    return msgs

def create_python_list(item):
    return [item]

def create_python_dict(prop, value):
    return {prop:value}

"""
Generic function that finds an object of type ObjectType by its attribute.    
The function looks for a objectToFind which is a string type by it's attribute.
Params: Field Name refers to properties like name, status etc
        objectType refers to objects like cpcs, groups, members etc
        FielddNameValue is the string that is searched for in the listOfDictionaries 
"""
def verify_object_in_list_by_attribute(listOfDictionaries, fieldNameValue, objectType, fieldName):
    verifyIn = False
    for myObject in listOfDictionaries.body[objectType]:
        if myObject[fieldName] == fieldNameValue:
            verifyIn = True
            break
    return verifyIn

def get_partition_list(session, cpc):
    response = session.get(cpc, '/partitions')
    for partition in response.body['partitions']:
        print partition['name']
    return response.body['partitions']
    
