from commands import publish, bundle, custom
import helpers
import logging


def define_action(user_input,  answers, resources_list):
    """
    Based on user input for backup, resp functions are called to take the backup
    :param user_input:
    :param answers:
    :param resources_list:
    """
    if user_input['backup'] == 'custom':
        user_input['config'] = answers['config']
        user_input['env'] = answers['env']
        custom.backup_custom(user_input,resources_list)
    elif user_input['backup'] == 'publish':
        user_input['config'] = answers['config']
        publish.backup_publish(user_input,resources_list)
    elif user_input['backup'] == 'bundle':
        user_input['config'] = answers['config']
        user_input['env'] = answers['env']
        bundle.backup_bundle(user_input,resources_list)
    else:
        logging.error("Unexpected Input !")
        quit(-1)


def main():

    # Get backup options list from the config file
    backup_options = helpers.load_config(key='options')

    # Get input from user
    user_input = helpers.user_args(backup_options)

    # Get environment names as per org name given by user
    env_list = helpers.get_env_list(user_input)

    # Get the list of supported resources from config.json file
    resources_list = helpers.load_config( key=user_input['backup'])

    # Prompt user to give other details, like env and backup config name
    answers = helpers.other_details(user_input, env_list, resources_list)

    # Define the action based on user input for backup
    define_action( user_input,  answers, resources_list )


if __name__ == '__main__':
    main()