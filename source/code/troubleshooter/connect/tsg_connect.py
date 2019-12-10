import subprocess

from tsg_errors           import tsg_error_info, get_input, print_errors
from install.tsg_install  import check_installation
from install.tsg_checkoms import get_oms_version
from .tsg_checkendpts     import check_internet_connect, check_agent_service_endpt, \
                                 check_log_analytics_endpts
from .tsg_checke2e        import check_e2e



# get onboarding error codes
def get_onboarding_err_codes():
    onboarding_err_codes = {0 : "No errors found"}
    with open("files/Troubleshooting.md", 'r') as ts_doc:
        section = None
        for line in ts_doc:
            line = line.rstrip('\n')
            if (line == ''):
                continue
            if (line.startswith('##')):
                section = line[3:]
                continue
            if (section == 'Onboarding Error Codes'):
                parsed_line = list(map(lambda x : x.strip(' '), line.split('|')))[1:-1]
                if (parsed_line[0] in ['Error Code', '---']):
                    continue
                onboarding_err_codes[parsed_line[0]] = parsed_line[1]
                continue
            if (section=='Onboarding Error Codes' and line.startswith('#')):
                break
    return onboarding_err_codes

# ask if user has seen onboarding error code
def ask_onboarding_error_codes():
    print("--------------------------------------------------------------------------------")
    # TODO: add smth about where / how to see if user encountered error code in onboarding
    answer = get_input("Do you have an onboarding error code? (y/n)", ['y','yes','n','no'],\
                       "Please type either 'y'/'yes' or 'n'/'no' to proceed.")
    if (answer.lower() in ['y','yes']):
        onboarding_err_codes = get_onboarding_err_codes()
        poss_ans = list(onboarding_err_codes.keys()) + ['none']
        err_code = get_input("Please input the error code", poss_ans,\
                             "Please enter an error code (an integer) to get the error \n"\
                                "message, or type 'none' to continue with the troubleshooter.")
        if (err_code != 'none'):
            print("\nError {0}: {1}\n".format(err_code, onboarding_err_codes[err_code]))
            answer1 = get_input("Would you like to continue with the troubleshooter? (y/n)",\
                                ['y','yes','n','no'],
                                "Please type either 'y'/'yes' or 'n'/'no' to proceed.")
            if (answer1.lower() in ['n','no']):
                print("Exiting troubleshooter...")
                print("================================================================================")
                return 1
    print("Continuing on with troubleshooter...")
    print("--------------------------------------------------------------------------------")
    return 0



# Verify omsadmin.conf exists / not empty
def check_omsadmin():
    omsadmin_path = "/opt/microsoft/omsagent/bin/omsadmin.sh"
    try:
        with open(omsadmin_path) as omsadmin_file:
            if (omsadmin_file == ""):
                tsg_error_info.append((omsadmin_path,))
                # TODO: copy contents into it upon asking?
                return 117
            return 0
    except IOError:
        tsg_error_info.append(('file', omsadmin_path))
        return 113



def check_connection(err_codes=True):
    print("CHECKING CONNECTION...")

    success = 0

    if (err_codes):
        if (ask_onboarding_error_codes() == 1):
            return 1

    # check if installed correctly
    print("Checking if installed correctly...")
    if (get_oms_version() == None):
        print_errors(110, reinstall=False)
        print("Running the installation part of the troubleshooter in order to find the issue...")
        print("================================================================================")
        return check_installation(err_codes=False)

    # check omsadmin.conf
    print("Checking if omsadmin.conf created correctly...")
    checked_omsadmin = check_omsadmin()
    if (checked_omsadmin != 0):
        print_errors(checked_omsadmin, reinstall=False)
        print("Running the installation part of the troubleshooter in order to find the issue...")
        print("================================================================================")
        return check_installation(err_codes=False)

    # check general internet connectivity
    print("Checking if machine is connected to the internet...")
    checked_internet_connect = check_internet_connect()
    if (checked_internet_connect != 0):
        return print_errors(checked_internet_connect, reinstall=False)

    # check if agent service endpoint connected
    print("Checking if agent service endpoint is connected...")
    checked_as_endpt = check_agent_service_endpt()
    if (checked_as_endpt != 0):
        return print_errors(checked_as_endpt, reinstall=False)

    # check if log analytics endpoints connected
    print("Checking if log analytics endpoints are connected...")
    checked_la_endpts = check_log_analytics_endpts()
    if (checked_la_endpts != 0):
        return print_errors(checked_la_endpts, reinstall=False)

    # check if queries are successful
    print("Checking if queries are successful...")
    checked_e2e = check_e2e()
    if (check_e2e == 1):
        return 1
    else:
        success = checked_e2e

    return success

    
