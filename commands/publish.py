import json
import logging
import requests

from commands.helpers import create_backup_file, config


def backup_publish(user_input, resources_list):
    """
    Based on the item value by user, action on retrieving the data is decided.
    If item is "all", then you need to run for loop to backup all the items
    """
    if user_input["item"] == "all":
        # Call the functions to get the data for each item/backup value
        for val in range(len(resources_list) - 1):
            # Change the value of item from all to valid value in url_resource
            user_input["item"] = resources_list[val]
            # Set the request url to get the data
            req_url = set_request_url(user_input)
            # Setup header for request
            headers = {
                "Authorization": "Bearer " + user_input["access_token"]
            }
            res_details = get_details(user_input, req_url, headers)
            # Create the backup on system by writing all the data to file
            create_backup_file(user_input, res_details)
            print("Backup Completed !!")
    else:
        # Set the request url to get the data
        req_url = set_request_url(user_input)
        # Setup header for request
        headers = {
            "Authorization": "Bearer " + user_input["access_token"]
        }
        res_details = get_details(user_input, req_url, headers)
        # Create the backup on system by writing all the data to file
        create_backup_file(user_input, res_details)
        print("Backup Completed !!")


def set_request_url(user_input):
    """
    Set the request URL for the backup
    """
    # Extract the value from user_input to be passed in URL
    org, resource = user_input["org"], user_input["item"]

    # Get the host from the config file
    host = config(key="host")

    # Creating http request URL
    req_url = host + "/v1/organizations/" + org + "/" + resource

    return req_url


def get_details(user_input, req_url, headers, start_key='', limit=1000):
    """
    Get the details of item in an environment of APIGEE ORG
    """
    res_details = []
    pagination = True
    print("Getting {}..".format(user_input["item"]))

    while pagination:
        # setting values of payload
        payload = (("expand", "true"), ("count", limit), ('startKey', start_key))
        # Making HTTP call and saving the response
        response = requests.get(req_url,
                            headers=headers,
                            params=payload)  # type: Response

        # If the response is a success
        if response.status_code == 200:
            # Extracting data from response object
            res_data = response.json()
            # Extract the data from the array of item
            data = extract_data(user_input, res_data)
            # Appending the data into res_details array
            for obj in data:
                res_details.append(obj)

            # Check if length of data is equal to limit i.e. 1000
            if len(data) == limit:
                # Set start_key for pagination
                start_key = set_start_key(user_input, res_details)
                # Remove the last element from list
                res_details.pop()
            else:
                pagination = False
                print("{} count : {}".format(user_input['item'], len(res_details)))
        else:
            logging.error("Error Occurred: Status code %s", response.status_code)
            pagination = False

    return res_details


def set_start_key(user_input, res_details):
    """
    Set the pagination start key for different values of item
    """
    # If the item is developers
    if user_input['item'] == 'developers':
        # Return the startKey for pagination
        return res_details[-1]['email']
    # If the item is apiproducts
    elif user_input['item'] == 'apiproducts':
        # Return the startKey for pagination
        return res_details[-1]['name']
    # If the item is apps
    elif user_input['item'] == 'apps':
        # Return the startKey for pagination
        return res_details[-1]['appId']


def extract_data(user_input, res_data):
    """
    Extract the data from response based on item
    """
    if user_input['item'] == 'apiproducts':
        # Converting apiproducts to apiProduct key to extract the data
        # To know more about it, check the actual response of Management API
        return res_data[user_input["item"][:3] +
                        user_input["item"][3:-1].capitalize()]
    else:
        # Converting apps/developers to app/developer key to extract the data
        return res_data[user_input["item"][:-1]]
