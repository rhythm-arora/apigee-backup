from commands import backup_publish, backup_bundle, backup_configuration
from commands.helpers import load_value, user_args, get_env_list, other_details

import logging
import sys

def define_action(user_input, answers, resources_list):
    """
    Based on user input for backup options, respective functions are called to take the backup
    :param user_input:
    :param answers:
    :param resources_list:
    """
    if user_input["backup"] == "configuration":
        user_input["item"] = answers["item"]
        user_input["env"] = answers["env"]
        backup_configuration(user_input, resources_list)
    elif user_input["backup"] == "publish":
        user_input["item"] = answers["item"]
        backup_publish(user_input, resources_list)
    elif user_input["backup"] == "bundle":
        user_input["item"] = answers["item"]
        user_input["env"] = answers["env"]
        backup_bundle(user_input, resources_list)
    else:
        logging.error("Unexpected Input !")
        sys.exit(-1)


def main():

    # Get backup options list from the config file
    backup_options = load_value(key="options")

    # Get input from user
    user_input = user_args(backup_options)

    # Get environment names as per org name given by user
    env_list = get_env_list(user_input)

    # Get the list of supported resources from config.json file
    resources_list = load_value(key=user_input["backup"])

    # Prompt user to give other details, like env and backup config name
    answers = other_details(user_input, env_list, resources_list)

    # Define the action based on user input for backup
    define_action(user_input, answers, resources_list)


if __name__ == "__main__":
    main()
