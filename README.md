# apigee-backup
![](demo.gif)

Use this tool to take backup of configuration item and entities from Apigee Edge organization/environment.

Note: Support MFA for APIGEE management APIs


## Backup Configurations

Below are the configurations/entities for which you can take the backup,

- `bundle`: apis, sharedflows
- `configuration`: keyvaluemaps, targetservers, keystores, virtualhosts, references, caches
- `publish`: apiproducts, apps, developers

## Installing the Tool

1. Download and Install Python
    > <https://www.python.org/downloads/>

2. Run the below commands to clone the repo and use the tool
```
git clone https://github.com/rhythm-arora/apigee-backup.git
cd APIGEE
pip install pipenv
pipenv shell
```

## Usage

`python index.py [-h] -u USERNAME -o ORG -b {configuration,publish,bundle}`

## Limitations

This tool currently does not support git bash on Windows. Try running it from cmd on Windows

