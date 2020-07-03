import logging
import zipfile
import requests
from io import BytesIO
from requests.models import Response

import helpers

def backup_bundle(user_input,resources_list):
    """
    Based on the config value entered by user, retrieval of data action is decided.
    If config is "all", then you need to run for loop to backup all the config
    """
    if user_input['config'] == 'all':
        # Call the functions to get the data for each config/backup value
        for val in range( len( resources_list ) - 1 ):
            # Change the value of config/backup from all to each valid value in url_resource
            user_input['config'] = resources_list[val]
            # Set the request url to get the data
            req_url = set_request_url( user_input )
            # Get the list of required config
            res_list = get_list( user_input, req_url )
            if len(res_list) != 0:
                # Get the deployed revision of shared flow in particular env.
                # Then append it to res_data along with shared flow name
                res_data = get_deployed_revision( user_input, req_url, res_list )
                # Get shared flow bundle
                res_details = get_details( user_input, req_url, res_data )
                # Create the backup
                helpers.create_backup_bundle( user_input, res_details )
                print( "Backup Completed !!" )
            else:
                print("No {} found !".format( user_input['backup']))
    else:
        # Set the request url to get the data
        req_url = set_request_url( user_input )
        # Get the list of required config
        res_list = get_list( user_input, req_url )
        if len( res_list ) != 0:
            # Get the deployed revision of shared flow in particular env.
            # Then append it to res_data along with shared flow name
            res_data = get_deployed_revision( user_input, req_url, res_list )
            # Get shared flow bundle
            res_details = get_details(user_input, req_url, res_data)
            # Create the backup
            helpers.create_backup_bundle( user_input, res_details )
            print( "Backup Completed !!" )
        else:
            print( "No {} found !".format( user_input['backup'] ) )


def set_request_url( user_input ):
    """
    Set the request URL for the backup
    :param user_input:
    """
    # Extract the value from user_input to be passed in URL
    org, resource = user_input['org'], user_input['config']

    # Get the host from the config file
    host = helpers.load_config( key='host' )

    # Creating http request URL
    req_url = host + 'v1/organizations/' + org + '/' + resource

    return req_url


def get_list( user_input, req_url ):
    """
    Get the list of config in an environment of APIGEE ORG
    :param req_url:
    :param user_input:
    """
    res_list = []
    try:
        # Making HTTP call and saving the response
        response = requests.get( req_url, auth=(user_input['username'], user_input['pass']) )  # type: Response

        if response.status_code == 200 and len( response.json() ) > 0:
            # Extracting data from response object
            res_list = response.json()
            print( "{} count: {}".format( user_input['config'], len( res_list ) ) )
        elif response.status_code == 200 and len(response.json()) == 0:
            logging.error("There are no {} found. Status Code {}".format(user_input['config'], response.status_code))
        else:
            logging.error( "Error Occurred: {} Status code {}".format( user_input['config'], response.status_code ) )

    except Exception as e:
        logging.error( "Error Occurred :" + e )

    return res_list


def get_deployed_revision( user_input, req_url, res_list ):
    """
    Get the deployed revision of config in an environment of APIGEE ORG
    :param user_input:
    :param req_url:
    :param res_list:
    """
    res_data = []
    count = 0
    for value in res_list:
        # Making HTTP call and saving the response
        response = requests.get( req_url + '/' + value + '/deployments',
                                 auth=(user_input['username'], user_input['pass']) )  # type: Response

        if response.status_code == 200:
            # Extracting data from response object
            res = response.json()
            for val in res['environment']:
                # Check if env name is equal to the user input env.
                # If api is not deployed in any env, then the array will be empty
                if val['name'] == user_input['env']:
                    # Check if the revision is not an empty array.
                    # If api is not deployed in an env, then the array will be empty
                    if val['revision'] != []:
                        value_pair = (value, val['revision'][0]['name'])
                        res_data.append(value_pair)
                        count += 1

    print("{} deployed in {} : {}".format(user_input['config'], user_input['env'], count))

    return res_data


def get_details(user_input, req_url, res_data):
    """
    Get the zip bundle of config in an environment of APIGEE ORG
    :param user_input:
    :param req_url:
    :param res_data:
    """
    # Set the payload for request
    payload = {'format': 'bundle'}
    res_details = []
    for val in res_data:
        # Making HTTP call and saving the response
        response = requests.get( req_url + '/' + val[0] + '/revisions/' + val[1],
                                 auth=(user_input['username'], user_input['pass']), stream=True, params=payload )  # type: Response

        if response.status_code == 200:
            # Extracting data from response object
            file = zipfile.ZipFile(BytesIO(response.content))
            # Create the backup
            value_pair = (val[0], val[1], file)
            res_details.append(value_pair)
        else:
            logging.error("Could not download {}".format(val[0]))

    return res_details