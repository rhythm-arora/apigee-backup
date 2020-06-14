import logging
from base64 import b64encode
import requests
from requests.models import Response
import csv
from datetime import datetime
import getpass
import argparse

passcode=''
org=''

def user_args():
    """
    Takes input from user like email, password, org and api product name
    """
    global passcode, org

    try:
        # Construct the input argument parser
        ap = argparse.ArgumentParser()
        # Add the arguments to the parser
        ap.add_argument( "-u", "--username", required=True,
                         help="User Email" )
        ap.add_argument( "-o", "--org", required=True,
                         help="APIGEE Org Name" )
        ap.add_argument( "-p", "--apiproduct", required=True,
                         help="APIGEE API Product Name" )

        # The vars() function returns the __dict__ attribute of the given object.
        args = vars(ap.parse_args())

        # Prompt user to enter password
        user_pass = getpass.getpass(prompt='Password : ')

        # Create b64 encode string
        # Changing the value of global variables passcode and org
        passcode = b64encode( bytes( args['username'] + ':' + user_pass, "utf-8" ) ).decode( "ascii" )
        org = args['org']

    except Exception as e:
        logging.error( "Exception occurred", exc_info=True )

    return args


def get_app_ids(api_product):
    """
    This function will take the API Product(input from user) and the passcode(generated by
    b64encode email and password given by user input).
    It will call the API to get the app_ids associated with the API Product and then return the
    response and app id list.
    In case of error, app list is appended with status code
    """

    count = 1000
    start_key = ''
    app_list = []

    while count == 1000:
        try:
            # Creating http request to get app ids
            url = 'https://api.enterprise.apigee.com/v1/organizations/' + org + '/apiproducts/' + api_product
            payload = (('query', 'list'), ('entity', 'apps'), ('count', '1000'), ('startkey', start_key))
            header = {'Authorization': 'Basic ' + passcode}

            # Making HTTP call and saving the response
            response = requests.get(url, headers=header, params=payload)  # type: Response

            # Success, iterate over app_data and append the data to app_list variable
            if response.status_code == 200:

                # Extracting data from response object
                app_data = response.json()

                # Setting the count variable to check if next call is required or not.
                # If, the count is 1000 then only we make the next call else stop
                count = len(app_data)

                # Setting the start_key as last element of response for next call
                start_key = app_data[-1]

                for i in app_data:
                    app_list.append(i)
            else:
                return response, app_list
                break

        except:
            return response, app_list


    return response, app_list


def get_developer_ids(app_ids):
    """
    For all the App Ids received, it will fetch developer_ids , creationDate, appName
    and displayName. It will create a developer_list and send the response back.
    In case of error, developer list is appended with status code
    """

    developer_list = []
    count = 0

    for app_id in app_ids:
        try:
            # Creating http request to get app ids
            url = 'https://api.enterprise.apigee.com/v1/organizations/' + org + '/apps/' + app_id
            header = {'Authorization': 'Basic ' + passcode}

            # Making HTTP call and saving the response
            response = requests.get(url, headers=header)  # type: Response

            if response.status_code == 200:

                # Extracting data from response object
                app_data = response.json()

                # Extracting required fields from response
                developer_id = app_data['developerId']
                creation_date = datetime.fromtimestamp(app_data['createdAt']/1000).strftime('%Y-%m-%d')
                app_name = app_data['name']

                # Check for Display Name else set as Empty String
                if len(app_data['attributes']) > 0 and app_data['attributes'][0]['name'] == 'DisplayName':
                    app_display_name = app_data['attributes'][0]['value']
                else:
                    app_display_name = ''

                # Creating value pair of the extracted data
                value_pair = (developer_id, creation_date, app_name, app_display_name)

                # Append the value pair to developer list
                developer_list.append(value_pair)
                count += 1
                print('Developer ids count : ', count)

            else:
                print("Not able to get data for " + app_id + " appId.")

        except:
            print("Not able to get data for " + app_id + " appId.")

    return developer_list


def get_developer_details(developer_ids):
    """
    For all the Developer Ids received, it will fetch developer details.
    It will create a developer_details and send the response back
    In case of error, developer details is appended with status code
    """

    developer_details = []

    # Iteration for all developer ids to get developer details
    for i in developer_ids:
        try:
            # Creating http request to get developer details
            id = i[0]
            url = 'https://api.enterprise.apigee.com/v1/organizations/' + org + '/developers/' + id
            header = {'Authorization': 'Basic ' + passcode}

            # Making HTTP call and saving the response
            response = requests.get(url, headers=header)  # type: Response

            # Extracting data from response object
            developer_data = response.json()

            # Check if response was successful
            if response.status_code == 200:
                developer_data.update({'creationDate' : i[1]})
                developer_data.update({'appName' : i[2]})
                developer_data.update({'displayName' : i[3]})
                developer_details.append(developer_data)
            else:
                print("Not able to get data for " + id + " developerId.")

        except:
            print("Not able to get data for " + id + " developerId.")

    return developer_details


def create_csv(developer_details, api_product):

    filename = api_product + '_' + 'developer_list' + '.csv'
    f = csv.writer(open(filename, 'a', newline='', encoding='utf-8'))
    f.writerow((["app_name", "app_display_name", "developer_first_name",
                 "developer_last_name", "email", "user_name",
                 "createdAt", "status", "developer_id"]))
    try:

        for dev_id in developer_details:
            try:
                f.writerow([dev_id["appName"], dev_id["displayName"], dev_id["firstName"],
                            dev_id["lastName"], dev_id["email"], dev_id["userName"], dev_id["creationDate"],
                            dev_id["status"], dev_id["developerId"]])
            except Exception as e:
                print( e )
                print("Unable to write data for " +  dev_id['developerId'] )
    except:
        print("Something went wrong ! Try Again ! Sorry !")


def main():

    get_data = True

    while get_data:
        try:

            # Get user input arguments
            user_input = user_args()

            # Extract API Product from user input
            api_product = user_input['apiproduct']

            # get developers apps id's subscribed to api_product
            response, app_ids = get_app_ids(api_product)

            if response.status_code == 200 and len(app_ids) != 0:
                print()
                print('Total Apps Ids found for ' + api_product + ' : ' + str( len(app_ids)))
                print('Now starting next step....\nGet Developer Ids from App Details')

                # Get Developer Ids
                developer_ids = get_developer_ids(app_ids)

                if len(developer_ids) != 0:
                    print()
                    print('Got Developer Ids.. \nGetting Developer Details')

                    # Get Developer Details
                    developer_details = get_developer_details(developer_ids)

                    if len(developer_details) != 0:
                        print("Got Developers Details.. \nStaring final step.. \nCreating CSV")

                        # Creating CSV
                        create_csv(developer_details, api_product)
                        print()
                        print("Your CSV file is ready! Cheers!")
                        get_data = False;
                    else:
                        print( 'Unable to retrieve developer details. Try again later !' )
                        get_data = False;
                else:
                    print('Unable to retrieve app data. Try again later !')
                    get_data = False;
            elif response.status_code == 200 and len(app_ids) == 0:
                print()
                print("There are no apps registered for " + api_product + ".")
                get_data = False
            elif response.status_code == 401:
                print('Status Code : ' + str(response.status_code) + '. ' + 'Incorrect email or password.')
                get_data = False;
            else:
                print('Status Code : ' + str(response.status_code) + '. ' + response.json()['message'])
                get_data = False;
        except Exception as e:
            print(e)
            print('Something went wrong. Try Again !')
            get_data = False;


if __name__ == '__main__':
    main()