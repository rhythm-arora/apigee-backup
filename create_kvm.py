import getpass
import argparse
from base64 import b64encode
import logging
import requests
from requests.models import Response
import json

def user_args():
    """
    Takes input from user like email, password, org and env
    """
    try:
        # Construct the input argument parser
        ap = argparse.ArgumentParser()
        # Add the arguments to the parser
        ap.add_argument( "-u", "--username", required=True,
                         help="User Email" )
        ap.add_argument( "-o", "--org", required=True,
                         help="APIGEE Org Name" )
        ap.add_argument( "-c", "--copykvmenv", required=True,
                         help="Env from which you want to copy KVM" )
        ap.add_argument( "-n", "--kvmname", required=False,
                         help="Name of a KVM which you want to copy" )
        ap.add_argument( "-e", "--deploykvmenv", required=True,
                         help="Env in which you want to create KVM" )

        # The vars() function returns the __dict__ attribute of the given object.
        args = vars(ap.parse_args())

        if args['deploykvmenv'] in ('dev', 'test', 'sandbox', 'prod') and args['copykvmenv'] in ('dev', 'test', 'sandbox', 'prod'):

            # Prompt user to enter password
            user_pass = getpass.getpass(prompt='Password : ')

            # Create b64 encode string
            # Changing the value of global variables passcode and org
            args['passcode'] = b64encode( bytes( args['username'] + ':' + user_pass, "utf-8" ) ).decode( "ascii" )
        else:
            print('Incorrect value for environment. Try again')

    except Exception as e:
        logging.error( "Exception occurred", exc_info=True )

    return args



def get_kvm_list_source(user_input):
    """
    Get the list of all KVM in an environment (source) of APIGEE ORG
    """
    app_data = []
    try:
        env, org = user_input['copykvmenv'], user_input['org']
        # Creating http request to get app ids
        url = 'https://api.enterprise.apigee.com/v1/organizations/' + org + '/environments/' + env + '/keyvaluemaps'
        header = {'Authorization': 'Basic ' + user_input['passcode']}

        # Making HTTP call and saving the response
        response = requests.get( url, headers=header )  # type: Response

        # Extracting data from response object
        app_data = response.json()

    except Exception as e:
        logging.error( "Exception occurred : {}".format(response.status_code))


    return response, app_data


def get_kvm_details(user_input, kvm_list_source):
    """
    Get the values of all KVM from an environment (source) and store it in a list
    """
    kvm_details = []
    try:
        env, org = user_input['copykvmenv'], user_input['org']
        for kvm in kvm_list_source:
            # Creating http request to get app ids
            url = 'https://api.enterprise.apigee.com/v1/organizations/' + org +\
                  '/environments/' + env + '/keyvaluemaps/' + kvm
            header = {'Authorization': 'Basic ' + user_input['passcode']}

            # Making HTTP call and saving the response
            response = requests.get( url, headers=header )  # type: Response

            if response.status_code == 200:
                # Extracting data from response object
                app_data = response.json()
                kvm_details.append(app_data)
            else:
                print('Can not get KVM {} details'.format(kvm))

    except Exception as e:
        logging.error( "Exception occurred", exc_info=True )

    return kvm_details

def create_kvm_destination(user_input, kvm_details):
    """
    Creating the KVM in an environment (destination) of APIGEE
    """
    env, org = user_input['deploykvmenv'], user_input['org']
    confirm = input("Confirm if you want to create KVM in {} env? Yes or No : ".format(user_input['deploykvmenv']))
    if confirm.lower() == 'yes':
        try:
            print("Creating KVM in {} env\nUpdates\n*******".format(user_input['deploykvmenv']))

            for kvm in kvm_details:
                # Creating http request to get app ids
                url = 'https://api.enterprise.apigee.com/v1/organizations/' + org + \
                      '/environments/' + env + '/keyvaluemaps'
                header = {'Content-Type': 'application/json',
                          'Authorization': 'Basic ' + user_input['passcode']}

                body = json.dumps(kvm)

                # Making HTTP call and saving the response
                response = requests.post(url, headers=header, data=body)  # type: Response

                if response.status_code == 201:
                    print("KVM : {} , Encrypted : {}, Status : 'Success', StatusCode : 201".format(kvm['name'], kvm['encrypted']))
                elif response.status_code == 409:
                    print("KVM : {} , Encrypted : {}, Status : 'Failed', StatusCode : 409, Message : {}".format(kvm['name'], kvm['encrypted'], response.json()['message']))
                else:
                    print("KVM : {} , Encrypted : {}, Status : 'Failed', StatusCode : {}".format(kvm['name'], kvm['encrypted'], response.status_code))

        except Exception as e:
            logging.error( "Exception occurred", exc_info=True )

    else:
        print("Terminating the flow ! Come back later if you want to create KVM !")

def main():

    create_kvm = True
    while create_kvm:
        try:
            # Get input from user
            user_input = user_args()
            if user_input.__contains__('passcode'):
                print( "Getting KVM List" )
                # Get KVM List from the source APIGEE environment
                response, kvm_list_source = get_kvm_list_source(user_input)

                if response.status_code == 200 and len( kvm_list_source ) == 0:
                    print()
                    print("Can not find any KVM in {} env. Try again".format(user_input['copykvmenv']))
                    create_kvm = False
                elif response.status_code == 200:
                    print("Total KVMs found : {} in {} env".format(len(kvm_list_source), user_input['copykvmenv']))
                    print()
                    print("Now getting KVM data from {} env".format(user_input['copykvmenv']))

                    # Get KVM details
                    kvm_details = get_kvm_details(user_input, kvm_list_source)
                    print("Got KVM Details : Count : {}".format(len(kvm_details)))
                    print()

                    # Create KVM
                    create_kvm_destination(user_input, kvm_details)
                    create_kvm = False

                elif response.status_code == 401:
                    print( 'Status Code : ' + str( response.status_code ) + '. ' + 'Incorrect email or password.' )
                    create_kvm = False
                else:
                    print( 'Status Code : ' + str( response.status_code ) + '. ' + response.json()['message'] )
                    create_kvm = False

            else:
                create_kvm = False
        except:
            print("Good Bye")
            create_kvm = False



if __name__ == '__main__':
    main()