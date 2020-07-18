import os
import sys
import json
import getpass
import logging
import argparse
from os import path
from datetime import datetime
import requests
import inquirer

from requests.models import Response


def config(key):
    """
    Get the required values from config.json file
    :param key:
    """
    with open("config.json") as json_file:
        json_data = json.load(json_file)
        value = json_data[key]

    return value


def user_args(backup_options):
    """
    Takes input from user like username, org and backup options
    """
    try:
        # Construct the input argument parser
        ap = argparse.ArgumentParser()
        # Add the arguments to the parser
        ap.add_argument("-u", "--username", required=True, help="User Email")
        ap.add_argument("-o", "--org", required=True, help="APIGEE Org Name")
        ap.add_argument(
            "-b",
            "--backup",
            required=True,
            choices=backup_options,
            help="Options for backup i.e. configuration, publish or bundle",
        )

        # The vars() function returns the __dict__ attribute of the given object
        args = vars(ap.parse_args())

        # Prompt user to enter password
        user_pass = getpass.getpass(prompt="Password : ")
        args["pass"] = user_pass
        return args

    except:
        logging.error("Exception occurred", exc_info=True)


def get_env_list(user_input):
    """
        Based on organisation provided by user, get the environment list from APIGEE
        :param user_input:
        """
    # Creating http request to get env list
    url = (
        "https://api.enterprise.apigee.com/v1/organizations/"
        + user_input["org"]
        + "/environments/"
    )

    # Making HTTP call and saving the response
    response = requests.get(
        url, auth=(user_input["username"], user_input["pass"])
    )  # type: Response

    if response.status_code == 200 and len(response.json()) > 0:
        # Returning data from response object
        return response.json()
    else:
        logging.error("Error Occurred: Status code %s", response.status_code)
        sys.exit(-1)


def other_details(user_input, env_list, resources_list):
    """
    Ask the user for further input like, environment and item that user wants to backup
    :param user_input:
    :param env_list:
    :param resources_list:
    """
    if user_input["backup"] in ("configuration", "bundle"):
        questions = [
            inquirer.List("env", message="Select the env name", choices=env_list,),
            inquirer.List(
                "item",
                message="Select the item name you want to take backup",
                choices=resources_list,
            ),
        ]
    else:
        questions = [
            inquirer.List(
                "item",
                message="Select the item name you want to take backup",
                choices=resources_list,
            ),
        ]

    answers = inquirer.prompt(questions)

    return answers


def build_req_url(org, resource, env=""):
    host = config("host")
    if env != "":
        env_part = f"/e/{env}"
    else:
        env_part = ""
    api_endpoint = f"{host}/v1/o/{org}{env_part}/{resource}"
    return api_endpoint


def create_backup_file(user_input, res_details):
    """
    Create JSON File for the data received
    :param user_input:
    :param res_details:
    """
    # Get Current Date Time
    now = datetime.now()

    # Convert the data into a JSON string
    res_json = json.dumps(res_details)

    # Set file path
    file_path = (
        os.getcwd() + "/backup/" + user_input["org"] + "/" + user_input["backup"] + "/"
    )

    # If file path does not exists, then create the directory
    if not path.exists(file_path):
        os.makedirs(file_path)

    # Set the filename
    if user_input["backup"] == "publish":
        file_name = user_input["item"] + "_" + now.strftime("%d-%m-%YT%H%M") + ".json"
    else:
        file_name = (
            user_input["env"]
            + "_"
            + user_input["item"]
            + "_"
            + now.strftime("%d-%m-%YT%H%M")
            + ".json"
        )

    # Write the data to file
    with open(file_path + file_name, "w") as file:
        file.write(res_json)


def create_backup_bundle(user_input, res_details):
    """
    Download the bundle to the file location
    :param user_input:
    :param res_details:
    """
    for val in res_details:
        now = datetime.today()

        # Save the value of zip object in file variable
        file = val[2]
        try:
            # Set file path
            file_path = (
                os.getcwd()
                + "/backup/"
                + user_input["org"]
                + "/"
                + user_input["backup"]
                + "/"
                + user_input["env"]
                + "_"
                + user_input["item"]
                + "_"
                + now.strftime("%d-%m-%YT%H%M")
                + "/"
            )

            # If file path does not exists, then create the directory
            if not path.exists(file_path):
                os.makedirs(file_path)

            # Set the file name
            filename = val[0] + "_rev_" + val[1]

            # Extract the zip files for all the data
            file.extractall(file_path + filename)
        except Exception as e:
            logging.error(e)
