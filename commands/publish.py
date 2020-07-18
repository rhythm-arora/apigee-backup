from commands.helpers import create_backup_file, load_value

import logging
import requests
from requests.models import Response

def backup_publish(user_input, resources_list):
    """
    Based on the item value entered by user, action on retrieving the data is decided.
    If item is "all", then you need to run for loop to backup all the items
    """
    if user_input["item"] == "all":
        # Call the functions to get the data for each item/backup value
        for val in range(len(resources_list) - 1):
            # Change the value of item/backup from all to each valid value in url_resource
            user_input["item"] = resources_list[val]
            # Set the request url to get the data
            req_url = set_request_url(user_input)
            res_details = get_details(user_input, req_url)
            # Create the backup by dumping all the data to json file and save it in the system
            create_backup_file(user_input, res_details)
            print("Backup Completed !!")
    else:
        # Set the request url to get the data
        req_url = set_request_url(user_input)
        res_details = get_details(user_input, req_url)
        # Create the backup by dumping all the data to json file and save it in the system
        create_backup_file(user_input, res_details)
        print("Backup Completed !!")


def set_request_url(user_input):
    """
    Set the request URL for the backup
    :param user_input:
    """
    # Extract the value from user_input to be passed in URL
    org, resource = user_input["org"], user_input["item"]

    # Get the host from the config file
    host = load_value(key="host")

    # Creating http request URL
    req_url = host + "v1/organizations/" + org + "/" + resource

    return req_url


def get_details(user_input, req_url):
    """
    Get the details of item in an environment of APIGEE ORG
    :param user_input:
    :param req_url:
    """
    res_details = []
    payload = (("expand", "true"), ("count", "1000"))
    print("Getting {}..".format(user_input["item"]))
    # Making HTTP call and saving the response
    response = requests.get(
        req_url, auth=(user_input["username"], user_input["pass"]), params=payload
    )  # type: Response

    if response.status_code == 200:
        # Extracting data from response object
        res_data = response.json()
        res_details.append(res_data)
    else:
        logging.error("Error Occurred: Status code %s", response.status_code)

    return res_details
