# Ansible Collection - joelwking.pensando

The Pensandos PSM platform is a policy and services manager that is based on a programmable, secure microservice-based infrastructure, providing policy management and infrastructure functions.

The objective of this project is to demonstrate using Ansible to programmatically manage (query, delete, create, update) then Network Security Policy configuration on the Policy Services Manager controller.

The security policy can be generated from a variety of sources, however the initial use case is to retrieve policy from Cisco Tetration using either the API or the network policy publisher. Refer to the https://github.com/joelwking/ansible-tetration repository.

## Playbooks
  * `tests/basic_functions.yml` is used for testing and examples of basic functionality.
  * `playbooks/tetration_policy_source.yml` uses [`tetration_application`](https://github.com/joelwking/ansible-tetration/blob/master/library/tetration_application.py) to retrieve policy from the Cisco Tetration API, manipulates the data, and then calls `plugins/modules/network_security_policy.py` to apply policy to the PSM.

## Module 
`plugins/modules/network_security_policy.py` is used to interface with the PSM API to manage policy.

```bash
$ ansible-doc joelwking.pensando.network_security_policy
> NETWORK_SECURITY_POLICY    (/collections/ansible_collections/joelwking/pensando/plugins/modules/network_security_policy)

        A Network Security Policy contains firewall rules such as 'to' and 'from',
        'ports', 'protocols, etc. and is applied to the Pensando policy and services
        manager (PSM). These policies are propagated to the Distributed Service Card
        (DSC) by the PSM. This module programatically manages the policy using the API of
        the PSM.

  * This module is maintained by The Ansible Community
OPTIONS (= is mandatory):

- api_version
        Optionally specify the API version
        [Default: v1]

- attach_tenant
        A Network Security Policy rule is typically deployed tenant-wide. Specify True to
        enable.
        [Default: True]

= hostname
        Hostname (or IP address) of the Pensando Policy and Service Manager (PSM)


- namespace
        Name of the Namespace
        [Default: default]

= password
        Password used to authenticate with the PSM


- policy_name
        Name of the network security policy (only one network security policy is currently
        allowed)
        [Default: default]

- rules
        A list of dictionary objects which define the firewall rules to be applied to the
        PSM
        [Default: (null)]

- state
        Use 'present' or 'absent' to add or remove
        Use 'query' for listing the current policy
        [Default: (null)]

= tenant
        Name of the tenant
        [Default: default]

- username
        Username used to authenticate with the database
        [Default: admin]


AUTHOR: Joel W. King (@joelwking)
        METADATA:
          status:
          - preview
          supported_by: community


EXAMPLES:

- network_security_policy:
      hostname: psm.example.net
      username: admin
      password: '{{ password }}'
      api_version: v1
      tenant: default
      namespace: default
      state: present
      policy_name: quarantine
      rules:
        - action: deny
          from-ip-addresses:
            - 198.51.100.0/24
          proto-ports:
            - ports: '123'
              protocol: udp
          to-ip-addresses:
            - 192.0.2.0/24


```

## Author
    Joel W. King  @joelwking
