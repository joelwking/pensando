README
------

This directory holds the API credential file from Tetration `api_credentials.json` and a credential file `gui_credentials.yml` with the hostname, userid and password of the Tetration GUI. Playbook `tetration_app.yml` only requires the `host` variable. Username and password are only for reference.

```yaml
#
#  Specify the hostname of the Tetration used for policy
#
atc_tetration:
    username: admin                       # for reference only, only host and API keys required
    password: foo!bar                     # for reference only, only host and API keys required
    host: atctetration01.wwtatc.local

```