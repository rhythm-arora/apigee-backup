from commands.helpers import create_backup_bundle, config

import logging
import zipfile
from io import BytesIO
from requests.models import Response
import json
import requests


def backup_bundle(user_input, resources_list):
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
            # Setup header for request
            headers = {
                "Authorization": "Bearer " + user_input["access_token"]
            }
            # Get the list of required item
            res_list = get_list(user_input, req_url, headers)

            if len(res_list) != 0:
                # Get the deployed revision of shared flow in particular env.
                # Then append it to res_data along with shared flow name
                res_data = get_deployed_revision(user_input, req_url, res_list, headers)

                if len(res_data) != 0:
                    # Get shared flow bundle
                    res_details = get_details(user_input, req_url, res_data, headers)
                    # Create the backup
                    create_backup_bundle(user_input, res_details)
                    print("Backup Completed !!")
            else:
                print("No {} found !".format(user_input["item"]))
    else:
        # Set the request url to get the data
        req_url = set_request_url(user_input)

        # Setup header for request
        headers = {
            "Authorization": "Bearer " + user_input["access_token"]
        }

        # Get the list of required item
        res_list = get_list(user_input, req_url, headers)
        if len(res_list) != 0:
            # Get the deployed revision of shared flow in particular env.
            # Then append it to res_data along with shared flow name
            res_data = get_deployed_revision(user_input, req_url, res_list, headers)
            # Get shared flow bundle
            res_details = get_details(user_input, req_url, res_data, headers)
            # Create the backup
            create_backup_bundle(user_input, res_details)
            print("Backup Completed !!")
        else:
            print("No {} found !".format(user_input["item"]))


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


def get_list(user_input, req_url, headers):
    """
    Get the list of item in an environment of APIGEE ORG
    """

    res_list = []
    try:
        # Making HTTP call and saving the response
        response = requests.get(req_url,
                            headers=headers) # type: Response

        if response.status_code == 200 and len(response.json()) > 0:
            # Extracting data from response object
            res_list = response.json()
            print("{} count: {}".format(user_input["item"], len(res_list)))
        elif response.status_code == 200 and len(response.json()) == 0:
            logging.error(
                "There are no %s found. Status Code %s",
                user_input["item"],
                response.status_code,
            )
        else:
            logging.error(
                "Error Occurred: %s Status code %d",
                user_input["item"],
                response.status_code,
            )

    except Exception as e:
        logging.error("Error Occurred :%s", e)

    return res_list


def get_deployed_revision(user_input, req_url, res_list, headers):
    """
    Get the deployed revision of item in an environment of APIGEE ORG
    """
    res_data = []
    count = 0
    for value in res_list:
        # Making HTTP call and saving the response
        response = requests.get(req_url + "/" + value + "/deployments",
                            headers=headers)  # type: Response

        if response.status_code == 200:
            # Extracting data from response object
            res = response.json()
            for val in res["environment"]:
                # Check if env name is equal to the user input env.
                # If api is not deployed in any env, then the array will be empty
                if val["name"] == user_input["env"]:
                    # Check if the revision is not an empty array.
                    # If api is not deployed in an env, then the array will be empty
                    if val["revision"] != []:
                        value_pair = (value, val["revision"][0]["name"])
                        res_data.append(value_pair)
                        count += 1

    print("{} deployed in {} : {}".format(user_input["item"], user_input["env"], count))

    return res_data


def get_details(user_input, req_url, res_data, headers):
    """
    Get the zip bundle of item in an environment of APIGEE ORG
    """
    # Set the payload for request
    payload = {"format": "bundle"}
    res_details = []
    for val in res_data:
        # Making HTTP call and saving the response
        response = requests.get(req_url + "/" + val[0] + "/revisions/" + val[1],
                            headers=headers,
                            stream=True,
                            params=payload)  # type: Response

        if response.status_code == 200:
            # Extracting data from response object
            file = zipfile.ZipFile(BytesIO(response.content))
            # Create the backup
            value_pair = (val[0], val[1], file)
            res_details.append(value_pair)
        else:
            logging.error("Could not download %s", val[0])

    return res_details
