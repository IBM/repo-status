# repo-status
Script to report on the status badges of repos in a provided organization.

## Usage
Before running this script, please ensure that you have a valid GitHub access token in the environment variable `GH_TOKEN` in order to authenticate with the GitHub API. See the [GitHub Documentation](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) on access tokens for more information.

```
python3 status.py -u https://api.github.com -o <ORGANIZATION_NAME>
```
OR
```
python3 status.py -u https://api.github.<ENTERPRISE>.com -o <ORGANIZATION_NAME>
```