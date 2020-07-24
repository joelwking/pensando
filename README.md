# Ansible Collection - joelwking.pensando

The Pensando PSM (Policy Services Manager) platform is a policy and services manager based on a programmable, secure microservice-based infrastructure, providing policy management and infrastructure functions.

The objective of this project is to demonstrate using Ansible to programmatically manage (query, delete, create, update) then Network Security Policy configuration on the Policy Services Manager controller.

The security policy can be generated from a variety of sources, however the initial use case is to retrieve policy from Cisco Tetration using either the API or the network policy publisher. Refer to the https://github.com/joelwking/ansible-tetration repository.

## Playbooks
* `tests/basic_functions.yml` is used for testing and examples of basic functionality.
* `playbooks/tetration_policy_source.yml` uses [`tetration_application`](https://github.com/joelwking/ansible-tetration/blob/master/library/tetration_application.py) to retrieve policy from the Cisco Tetration API, manipulates the data, and then calls `plugins/modules/network_security_policy.py` to apply policy to the PSM.
* `playbooks/tetration_app.yml` also uses `tetration_application` to retrieve policy and create apps on the PSM. One feature of this playbook, the version of the ADM run which generated the policy can be specified, and the playbook can create apps based on the application name and version. This enables having multiple versions in the PSM.

## Modules
These modules use the PSM API to query, delete and create/update the associated objects.

* `plugins/modules/network_security_policy.py`  manages network security policies.
* `plugins/modules/app.py` manages apps.
* `plugins/module_utils/Pensando.py` is a Python class called by modules to handle common functions.


Module documentation is accessible by using `ansible-doc`,

```shell
$ ansible-doc joelwking.pensando.network_security_policy
```
or viewing the Python source code.

## Issues
Open issues and code enhancements are described in this section. Be aware this is **alpha** code, meaning not all functionality has been tested and implemented. 

* *Duplicate ports*: Data returned from the Tetration API includes both `absolute_policies` and `default_policies`. Default policies are the artifact of an Application Dependency Mapping (ADM) run. Absolute policies are manually (or via the API) configured. Ports and protocols are reported based on the traffic observations from one or more hosts defined. The API will return duplicate ports and protocols when simply extracting output from the API when the consumer and provider filter IDs are ignored. The PSM API does not optimize (summarize) the ports and protocols. There are duplicate entries applied. Needed is a module/lookup/plugin to create unique entries. *!! resolved by adding method remove_dups to Pensando.py !!*

* *ICMP*: ICMP packets have no concept of a port number. If you specify a port, it must be null, or, don't include 'port' field in the payload for ICMP. *!! Fixed by https://github.com/joelwking/ansible-tetration/pull/3 !!*
```
400:{"kind":"Status","result":{"Str":"Request validation failed"},"message":["Can not specify ports for ICMP protocol","port unspecified must be an integer value"],"code":400,"object-ref":{"tenant":"default","namespace":"default","kind":"App","name":"SAMPLE"}}
```
```yaml
        proto_ports:
            - protocol: icmp                 # This is valid
            - protocol: icmp                 # This is valid
              ports: ""
            - protocol: icmp                 # This will fail.
              ports: "unspecified"
```        
* *App names*: App names cannot include colons, e.g. `'app_name="TetlabBase:WordPress" app_version=latest'` is not valid. In Tetration, the app name can include a colon. 

* *Port Ranges*: Tetration allows the user to create `absolute_policies` with a starting port higher than the ending port. The PSM API will not permit this mis-configuration. *!! Fixed by https://github.com/joelwking/ansible-tetration/pull/3 !!*

```
400:{"kind":"Status","result":{"Str":"Request validation failed"},"message":["Invalid port range 21-20. first number bigger than second"],"code":400,"object-ref":{"tenant":"default","namespace":"default","kind":"App","name":"SAMPLE"}}

```
```yaml
        proto_ports:
            - protocol: tcp
              ports: "21-20"                #  first number cannot be higher than second
```

* *PERMIT|DENY*: Must filter on action in rules. *!! resolved by adding `- item["action"] == "ALLOW"` to playbooks !!*

* *Pretty Print Output JSON files*: *!! resolved by adding `to_nice_json(indent=2)` to copy module. !!*

## Author
Joel W. King  @joelwking
