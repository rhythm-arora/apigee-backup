import os
import json
import getpass
import logging
import argparse
from os import path
import inquirer


def get_mfa():
    """
    Prompt user for MFA
    """
    # Prompt user to enter mfa
    return input("Enter MFA: ")


def find_token(home, token_file, key):
    """
    Search for existing tokens in file
    """
    try:
        # Opening JSON file
        with open(home + token_file) as f:
            data = json.loads(f.read())
        return data[key]
    except:
        return None


def config(key):
    """
    Get the required values from config.json file
    """
    with open("config.json") as json_file:
        json_data = json.load(json_file)
        value = json_data[key]

    return value


def user_args(backup_options):
    """
    Takes input from user like username, org and backup options
    """
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


def other_details(user_input, env_list, resources_list):
    """
    Ask the user for further input like, environment and item that user wants to backup
    """
    if user_input["backup"] in ("configuration", "bundle"):
        questions = [
            inquirer.List("env", message="Select the env name", choices=env_list, ),
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
    """
    Build request URL
    """
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
    """
    # Convert the data into a JSON string
    res_json = json.dumps(res_details)

    try:
        if user_input["backup"] == "publish":
            # Set file path
            file_path = (
                    os.getcwd() + "/backup/" + user_input["org"] + "/" + user_input["backup"] + "/"
            )
        else:
            # Set file path
            file_path = (
                    os.getcwd() + "/backup/" + user_input["org"] + "/" + user_input["backup"] + "/" + user_input[
                "env"] + "/"
            )

        # If file path does not exists, then create the directory
        if not path.exists(file_path):
            os.makedirs(file_path)

        # Set the filename
        file_name = user_input["item"] + ".json"

        # Write the data to file
        with open(file_path + file_name, "w") as file:
            file.write(res_json)

    except Exception as e:
        logging.error(e)


def create_backup_bundle(user_input, res_details):
    """
    Download the bundle to the file location
    """
    for val in res_details:

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
                    + user_input["item"]
                    + "/"
                    + user_input["env"]
                    + "/"
            )

            # If file path does not exists, then create the directory
            if not path.exists(file_path):
                os.makedirs(file_path)

            # Set the file name
            filename = val[0]

            # Extract the zip files for all the data
            file.extractall(file_path + filename)

        except Exception as e:
            logging.error(e)
