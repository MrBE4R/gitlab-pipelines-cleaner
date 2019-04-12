# gitlab-pipelines-cleaner

Python project to cleanup pipelines in gitlab

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

This project has been tested on CentOS 7.6 with GitLab 11.5.* and OpenLDAP and Active Directory.

```
Python        : 3.4.9
pip3          : 8.1.2
python-gitlab : 1.6.0
```

### Installing

You could either install requirements system wide or use virtual environment / conda, choose your poison.

To get this up and running you just need to do the following :

* Clone the repo
```bash
git clone https://github.com/MrBE4R/gitlab-pipelines-cleaner
```
* Install requirements
```bash
pip3 install -r ./gitlab-pipelines-cleaner/requirements.txt
```
* Edit config.json with youe values
```bash
EDITOR ./gitlab-pipelines-cleaner/config.json
```
* Start the script and enjoy your sync users and groups being synced
```bash
cd ./gitlab-pipelines-cleaner && ./gitlab-pipelines-cleaner.py
```

You should get something like this :
```bash
Initializing gitlab-pipelines-cleaner.
Done.
Updating logger configuration
Done.
[Timestamp] [INFO] Connecting to GitLab
[Timestamp] [INFO] Done.
[Timestamp] [INFO] Going through all groups and projects
[Timestamp] [INFO] Deleting pipeline <pipeline id> for project <project name>
[Timestamp] [INFO] Deleting pipeline <pipeline id> for project <project name>
[Timestamp] [INFO] Deleting pipeline <pipeline id> for project <project name>
[Timestamp] [INFO] Deleting pipeline <pipeline id> for project <project name>
```

You could add the script in a cron to run it periodically.
## Deployment

How to configure config.json
```json5

{
  "log_level": "INFO",                         // The log level.
  "log":"/tmp/gitlab-pipelines-cleaner.log",   // Where to store the log file. If not set, will log to stdout.
  "gitlab": {
    "api": "",                                 // Url of your GitLab.
    "private_token": "",                       // Token generated in GitLab for an user with admin access.
    "oauth_token": "",
    "groups": [],                              // List of groups to clean up. If empty, all groups are cleaned up.
    "projects": [],                            // List of project to clean up. If empty, all projects are cleaned up.
    "status_autodelete":[],                    // List of pipeline status to clean up. If empty pipeline in any status are cleaned up.
    "to_keep": 1                               // Number of pipelines to keep
  }
}
```
You should use ```private_token``` or ```oauth_token``` but not both. Check [the gitlab documentation](https://docs.gitlab.com/ce/user/profile/personal_access_tokens.html#creating-a-personal-access-token) for how to generate the personal access token.

```status_autodelete``` can be a list with the following status ```running```, ```pending```, ```success```, ```failed```, ```canceled```, ```skipped``` .
See <https://docs.gitlab.com/ee/api/pipelines.html> for an updated list of pipeline status
## TODO

- [ ] Implement time based selection (cleanup only if older than XXX)
- [ ] Make to_keep work for each status in status_autodelete
- [ ] Your suggestions
## Built With

* [Python](https://www.python.org/)
* [python-ldap](https://www.python-ldap.org/en/latest/)

## Contributing

Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Jean-François GUILLAUME (Jeff MrBear)** - *Initial work* - [MrBE4R](https://github.com/MrBE4R)

See also the list of [contributors](https://github.com/MrBE4R/gitlab-ldap-sync/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
