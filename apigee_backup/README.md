# APIGEE-Scripts
This repo will have python scripts related to APIGEE

## Get Developer Details
This will get the developer details for a particular API Product

## Create KVM
This will copy all the KVM from particular env and create in another.

Use the below command to run the code:

```
python create_kvm.py -u <username> -o <org> -c <source_env> -e <destination_env>
```

## APIGEE Backup Config
This will take the backup of your APIGEE configuration items per environment.

Use the below command to run the code:

```
python apigee_config_backup.py -u <username> -o <org> -e <env> -b <backup_config>
```

- backup_config values:

    - kvms
    - targetservers
    - keytruststores
    - vhosts
    - references
    - all

    
## Development Setup

Setup pipenv
```
pip install pipenv
pipenv shell
```

Install project dependencies
```
pip install --dev
```
