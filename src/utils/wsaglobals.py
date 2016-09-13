# Global variables for use by wsaconst and friends
# 
# Change history:
# - 2014/07/17 L. Brocious      Initial version.  Added for "temporary object" support.
# - 2015/02/16 L. Brocious      Add "temporary session" support.

# This is the list of additional command line options (those defined in addition
# to the "standard" options) defined for the current testcase execution.  This is
# saved when the Session is created and is used only to allow successful re-parsing
# of the command line when additional sessions are created during testcase execution
# (typically during scenario setup and cleanup).
global global_saved_additional_options
global_saved_additional_options = None

# The list of all registerd "temporary objects".  This list is managed by the 
# register_temporary_object() and deregister_temporary_object() methods.  All
# objects in this list are deleted by default during session shutdown.
global global_temporary_objects_list
global_temporary_objects_list = []

# The list of all known "admin" sessions.  Such privileged sessions are typically needed
# during scenario setup and cleanup.  For performance reasons, they are cached here and
# reused if needed.  This list is managed by get_admin_session() and delete_all_admin_sessions().
global global_admin_sessions
global_admin_sessions = dict()


# The list of all registerd "temporary sessions".  A temporary session is associated
# with a temporary user and is intended for testcase scripts that perform authorization
# testing.  All sessions in this list are deleted by default during shutdown of the
# testcase's main session (via the standard session_shutdown(session) call before exit).
global global_temporary_sessions
global_temporary_sessions = []
