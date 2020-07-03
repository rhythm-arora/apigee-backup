# apigee-backup

Use this tool to take backup of configuration information and entities from Apigee Edge organization/environment.


## Backup Configurations

Below are the configurations/entities for which you can take the backup,

- bundle
    - apis
    - sharedflows
- custom
    - keyvaluemaps
    - targetservers
    - keystores
    - virtualhosts
    - references
- publish
    - apiproducts
    - apps
    - developers


## Installing the Tool

- Downlaod and Install Python
    > <https://www.python.org/downloads/>

- To get the tool, clone this repository.
    > https://github.com/rhythm-arora/APIGEE.git

- Development Setup

    Setup pipenv
    ```
    pip install pipenv
    pipenv shell
    ```

    Install project dependencies
    ```
    pip install --dev
    ```

## Using the tool

Once you install the tool , you can run it to get the data for your org/env.

Following command needs to be run,

1)
```
python index.py -u <username> -o <org> -b <backup>
```

- ArgumentValues:

    a) username - APIGEE username Ex: xyz@gmail.com

    b) org - APIGEE oranization name Ex: myorg

    c) backup - APIGEE configuration you want to take backup. 
    Acceptable Values: 

        - custom 
        - publish 
        - bundle

2) Next, you will be asked to enter your APIGEE password.
```
Password :
```
3) If username and password is correct, then you will be asked further questions like env and config based on backup value provided.


## Backup Folder Structure

The following folder structure with data will be created in your current directory.

- backup (Directory)
    - {org} (Directory)
        - bundle (Directory)
            - sharedflows_{env}_{datetime} (Directory)
                - sharedflow-1
                - sharedflow-2
            - apis_{env}_{datetime} (Directory)
                - api-1
                - api-2
        - custom (Directory)
            - keyvaluemaps_{env}_{datetime}
            - targetservers_{env}_{datetime}
            - keystores_{env}_{datetime}
            - virtualhosts_{env}_{datetime}
            - references_{env}_{datetime}
        - publish (Directory)
            - apiproducts_{env}_{datetime}
            - developers_{env}_{datetime}
            - apps_{env}_{datetime}
    - {org}
        - bundle
        - custom
        - publish
    

## Project Files

- index.py

    Main file

- config.json

    This is the configuration file used by python code.

- reuirements.text

    Information about what all modules are being used for this tool

- helpers.py

    In this, the all helping methods are defined are which used to perform particular action

- commands
    - bundle.py

        This is code file for taking backup for, config=bundle
    - custom.py

        This is code file for taking backup for, config=publish
    - publish.py
    
        This is code file for taking backup for, config=publish