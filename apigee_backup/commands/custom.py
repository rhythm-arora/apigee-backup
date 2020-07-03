import logging
import requests
from requests.models import Response

import helpers

def backup_custom(user_input, resources_list):
    """
    Based on the config value entered by user, retrieval of data action is decided.
    If config is "all", then you need to run for loop to backup for all the config values
    """
    if user_input['config'] == 'all':
        # Call the functions to get the data for each config/backup value
        for val in range(len(resources_list)-1):
            # Change the value of config/backup from all to each valid value in url_resource
            user_input['config'] = resources_list[val]
            # Set the request url to get the data
            req_url = set_request_url(user_input)
            # Get the list of required config
            res_list = get_list( user_input, req_url )
            # If we received the list with at least one value, then continue
            if len(res_list) != 0:
                # Get the details of required config by passing the list received in previous step
                res_details = get_details( user_input, req_url, res_list )
                # Create the backup by dumping all the data to json file and save it in the system
                helpers.create_backup_file( user_input, res_details )
                print( "Backup Completed !!" )
            else:
                print("No {} found !".format( user_input['backup']))

    else:
        # Set the request url to get the data
        req_url = set_request_url( user_input )
        # Get the list of config
        res_list = get_list( user_input, req_url )
        # If we received the list with at least one value, then continue
        if len( res_list ) != 0:
            # Get the details of required config by passing the list received in previous step
            res_details = get_details( user_input, req_url, res_list )
            # Create the backup by dumping all the data to json file and save it in the system
            helpers.create_backup_file( user_input, res_details )
            print( "Backup Completed !!" )
        else:
            print("No {} found !".format( user_input['backup']))

def set_request_url(user_input):
    """
    Set the request URL for the backup
    :param user_input:
    """
    # Extract the value from user_input to be passed in URL
    org, resource, env = user_input['org'], user_input['config'], user_input['env']

    # Get the host from the config file
    host = helpers.load_config(key='host')

    # Creating http request URL
    req_url = host + 'v1/organizations/' + org + '/environments/' + env + '/' + resource

    return req_url


def get_list(user_input, req_url):
    """
    Get the list of config in an environment of APIGEE ORG
    :param req_url:
    :param user_input:
    """
    res_list = []
    try:
        # Making HTTP call and saving the response
        response = requests.get( req_url, auth=(user_input['username'], user_input['pass']))  # type: Response
        if response.status_code == 200 and len(response.json()) > 0:
            # Extracting data from response object
            res_list = response.json()
            print("{} count: {}".format(user_input['config'],len(res_list)))
        elif response.status_code == 200 and len(response.json()) == 0:
            logging.error("There are no {} found. Status Code {}".format(user_input['config'], response.status_code))
            quit()
        else:
            logging.error( "Error Occurred: Status code {}".format( response.status_code ) )
            quit()

    except Exception as e:
        print( e )
        logging.error( "Error Occurred" )

    return res_list


def get_details(user_input, req_url, res_list):
    """
    Get the details of config in an environment of APIGEE ORG
    :param user_input:
    :param req_url:
    :param res_list:
    """
    res_details = []

    for value in res_list:

        # Making HTTP call and saving the response
        response = requests.get( req_url+'/'+value, auth=(user_input['username'], user_input['pass']) )  # type: Response

        if response.status_code == 200:
            # Extracting data from response object
            res_data = response.json()
            res_details.append( res_data )
        else:
            logging.error( 'Error Occurred: Status code {} for {} {}'.format( response.status_code, value, user_input['config'] ) )

    return res_details


