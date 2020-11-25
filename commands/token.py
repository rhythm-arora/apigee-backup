import json
import logging
import os
import sys
import requests
from colorama import Fore, Style

from commands.helpers import config, get_mfa, find_token

# Set file path and name to store token file
home = str(os.path.expanduser("~"))
token_file = '\\apigee-edge-token.json'


def get_env_list(user_input):
    """
    Based on organisation provided by user, get the environment list from APIGEE
    """
    fail = True
    while fail:
        # Creating http request to get env list
        url = (
                "https://api.enterprise.apigee.com/v1/organizations/"
                + user_input["org"]
                + "/environments/"
        )

        # Setup header for request
        headers = {
            "Authorization": "Bearer " + user_input["access_token"]
        }

        # Making HTTP call and saving the response
        response = requests.get(url,
                            headers=headers)  # type: Response

        if response.status_code == 200 and len(response.json()) > 0:
            # Returning data from response object
            fail = False
            return response.json()
        elif response.status_code == 401:
            print("Access token invalid or expired!")
            # Generate new access token using refresh token
            refresh_token(user_input)
        else:
            fail = False
            logging.error("Error Occurred: Can not fetch environment list: Status code %s", response.status_code)
            print(Style.RESET_ALL)
            sys.exit(-1)


def generate_token(user_input):
    """
    Generate Access Token to access APIs
    """
    # Get MFA
    user_input["mfa"] = get_mfa()

    # Get token URL from config file
    url = config(key="token_url")

    # Setup header for request
    headers = {
        "Authorization": "Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json;charset=utf-8"
    }

    # setting values of payload
    payload = "username=" + user_input["username"] \
              + "&password=" + user_input["pass"] \
              + "&grant_type=password&mfa_token=" \
              + user_input["mfa"]

    print("Generating new access token...", end="")

    # Making HTTP call and saving the response
    response = requests.post(url, headers=headers, params=payload)  # type: Response

    # Check the status of the api response
    if response.status_code == 200:

        print(Fore.GREEN + "Done")

        # Extract the response body
        response_data = response.json()

        # Save the response in system file
        with open(home+token_file, 'w') as file:
             file.write(json.dumps(response_data))

        # add access_token in user_input object to used in api calls
        user_input["access_token"] = response_data["access_token"]

    else:
        print(Fore.RED + "Failed")
        logging.error("Error Generating Access Token: Status code %s", response.status_code)
        print(Style.RESET_ALL)
        sys.exit(-1)


def get_token(user_input):
    """
    Check if token is present, set in user_input object else generate a new one by
    calling generate_token
    """
    # Get token from file
    access_token = find_token(home, token_file, key="access_token")

    # Check if access token is present, then set it to user_input
    # else generate it by calling API endpoint
    if not access_token:
        print("Access Token not present")
        generate_token(user_input)
    else:
        print("Access Token present")
        user_input["access_token"] = access_token


def refresh_token(user_input):
    """
    Generate new token refresh_token. If refresh_token is expired, call
    generate_token for new token
    """
    # Get refresh token
    refresh_token = find_token(home, token_file, key="refresh_token")

    if refresh_token:
        # Get token URL from config file
        url = config(key="token_url")

        # Setup header for request
        headers = {
            "Authorization": "Basic ZWRnZWNsaTplZGdlY2xpc2VjcmV0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json;charset=utf-8"
        }

        # setting values of payload
        payload = "refresh_token=" + refresh_token \
                  + "&grant_type=refresh_token"

        print("Generate new access token using refresh token...", end="")

        # Making HTTP call and saving the response
        response = requests.post(url, headers=headers, params=payload)  # type: Response

        # Check the status of the api response
        if response.status_code == 200:
            print(Fore.LIGHTGREEN_EX + "Done")

            # Extract the response body
            response_data = response.json()
            # Save the response in system file
            with open(home + token_file, 'w') as file:
                file.write(json.dumps(response_data))
            # Set access_token value in user_input
            user_input["access_token"] = response_data["access_token"]

        elif response.status_code == 401:
            print(Fore.RED + "Failed")
            print("Refresh token invalid or expired!", Style.RESET_ALL)

            # Generate new access token and refresh token
            print("Generate new access token and refresh token..")
            generate_token(user_input)

            print(Style.RESET_ALL)
        else:
            logging.error("Error Occurred: Status code %s", response.status_code)
            print(Style.RESET_ALL)
            sys.exit(-1)
    else:
        print("Refresh token not present!")
        # Generate new access token and refresh token
        print("Generate new access token and refresh token..")
        generate_token(user_input)
