# apigee-backup
![](demo.gif)

Use this tool to take backup of configuration item and entities from Apigee Edge organization/environment.


## Backup Configurations

Below are the configurations/entities for which you can take the backup,

- `bundle`: apis, sharedflows
- `configuration`: keyvaluemaps, targetservers, keystores, virtualhosts, references
- `publish`: apiproducts, apps, developers

## Installing the Tool

1. Download and Install Python 3.7.x
    > <https://www.python.org/downloads/>

2. Run the below commands to clone the repo and use the tool
```
git clone https://github.com/rhythm-arora/apigee-backup.git
cd apigee-backup
pip install pipenv
pipenv shell
pipenv install
```

## Usage

`python index.py [-h] -u USERNAME -o ORG -b {configuration,publish,bundle}`

## Limitations

This tool currently does not support git bash on Windows. Try running it from cmd on Windows

