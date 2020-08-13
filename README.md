# Ansible Collection - joelwking.pensando

The Pensando PSM (Policy Services Manager) platform is a policy and services manager based on a programmable, secure microservice-based infrastructure, providing policy management and infrastructure functions.

The objective of this project is to demonstrate using Ansible to programmatically manage (query, delete, create, update) then Network Security Policy configuration on the Policy Services Manager controller.

The security policy can be generated from a variety of sources, however the initial use case is to retrieve policy from Cisco Tetration using either the API or the network policy publisher. Refer to the https://github.com/joelwking/ansible-tetration repository.

## Playbooks
These playbooks are for testing, documentation and demonstration purposes. You may use them for reference and customize and modify as your workflow and business requirements dictate.

* `workflow_use_case.yml` this playbook was created to demonstrate a sample workflow use case. The playbook optionally retrieves policy from Tetration based on the application name and version. It writes the policy to disk as pretty printed JSON for review. It re-formats the policy for loading into the PSM. It queries the name of the existing network security policy, and fails if no policy exists on PSM. It adds an App using the policy. The name of the App is based on the application name, version and a timestamp, creating a unique App on the PSM. It references the `files/environments.yml` configuration file to determine what network addressing is associated with this application name. Finally, it appends the existing network security policy referencing the app and the source and destination addresses specified in the environment file.
* `tests/basic_functions.yml` is used for testing and examples of basic functionality.
* `playbooks/tetration_policy_source.yml` uses [`tetration_application`](https://github.com/joelwking/ansible-tetration/blob/master/library/tetration_application.py) to retrieve policy from the Cisco Tetration API, manipulates the data, and then calls `plugins/modules/network_security_policy.py` to apply policy to the PSM.
* `playbooks/tetration_app.yml` also uses `tetration_application` to retrieve policy and create apps on the PSM. One feature of this playbook, the version of the ADM run which generated the policy can be specified, and the playbook can create apps based on the application name and version. This enables having multiple versions in the PSM.

## Modules
These modules use the PSM API to query, delete and create/update the associated objects.

* `plugins/modules/network_security_policy.py`  manages network security policies.
* `plugins/modules/app.py` manages apps.
* `plugins/module_utils/Pensando.py` contains Python class(s) called by modules to handle common functions.

Module documentation is accessible by using `ansible-doc`,

```shell
$ ansible-doc joelwking.pensando.network_security_policy
```
or viewing the Python source code.

## Issues
Open issues and caveats listed in this section.
      
* *App names*: App names cannot include colons, e.g. `'app_name="TetlabBase:WordPress"'` is not valid. In Tetration, the app name can include a colon. 

## Author
Joel W. King  @joelwking
