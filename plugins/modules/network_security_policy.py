#!/usr/bin/python
#
#     Copyright (c) 2020 World Wide Technology, LLC
#     All rights reserved.
#
#     linter: flake8
#         [flake8]
#         max-line-length = 160
#         ignore = E402
#
DOCUMENTATION = '''
---
module: network_security_policy

short_description: Create, update, query or delete a Network Security Policy

version_added: "2.9"

description:
    - A Network Security Policy contains firewall rules such as 'to' and 'from', 'ports', 'protocols, etc.
    - and is applied to the Pensando policy and services manager (PSM). These policies are propagated to
    - the Distributed Service Card (DSC) by the PSM. This module programatically manages the policy using the
    - API of the PSM.

options:
    tenant:
        description:
            - Name of the tenant
        required: false
        default: 'default'

    namespace:
        description:
            - Name of the Namespace
        required: false
        default: 'default'

    policy_name:
        description:
            - Name of the network security policy (only one network security policy is currently allowed)
            - The default is a null string, which indicates return all policies
        required: false
        default: ''

    attach_tenant:
        description:
            - A Network Security Policy rule is typically deployed tenant-wide. Specify True to enable.
        required: false
        default: true

    rules:
        description:
            - A list of dictionary objects which define the firewall rules to be applied to the PSM
        required: false

    state:
        description:
            - Use 'present' or 'absent' to add or remove
            - Use 'query' for listing the current policy
        required: false
        default: 'present'

    operation:
        description:
          - Use 'replace' to replace all entries of an existing policy
          - Use 'append' to append the provided rules to an existing policy
        required: false
        default: 'replace'

    username:
        description:
            - Username used to authenticate with the PSM
        required: false
        default: 'admin'

    password:
        description:
            - Password used to authenticate with the PSM
        required: true

    hostname:
        description:
            - Hostname (or IP address) of the Pensando Policy and Service Manager (PSM)
        required: true

    api_version:
        description:
            - Optionally specify the API version
        required: false
        default: 'v1'


author:
    - Joel W. King (@joelwking)
'''

EXAMPLES = '''

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

- name: Query Policy
  network_security_policy:
      hostname: psm.example.net
      username: admin
      password: '{{ password }}'
      state: query

- name: Delete Policy
  network_security_policy:
      hostname: psm.example.net
      username: admin
      password: '{{ password }}'
      state: absent
      policy_name: foo


'''
#
#  System imports
#
import requests
#
#  Ansible core import
#
from ansible.module_utils.basic import AnsibleModule
#
# Collection import
#
import ansible_collections.joelwking.pensando.plugins.module_utils.Pensando as Pensando


def main():
    """
        Main logic
    """
    module = AnsibleModule(
        argument_spec=dict(
            hostname=dict(required=True),
            api_version=dict(required=False, default='v1'),
            username=dict(required=True),
            password=dict(required=True, no_log=True),
            state=dict(required=False, default='present'),
            operation=dict(required=False, default='replace'),
            tenant=dict(required=False, default='default'),
            rules=dict(required=False, type='list'),
            attach_tenant=dict(required=False, default=True, type='bool'),
            policy_name=dict(required=False, default=''),
            namespace=dict(required=False, default='default')
            ),
            check_invalid_arguments=True,
            add_file_common_args=True,
            supports_check_mode=False
        )

    psm = Pensando.Pensando(hostname=module.params.get('hostname'),
                            username=module.params.get('username'),
                            password=module.params.get('password'),
                            api_version=module.params.get('api_version')
                           )

    login = psm.login(tenant=module.params.get('tenant'))
    if not login.ok:
        module.fail_json(msg='{}:{}'.format(login.status_code, login.text))

    if module.params.get('state') == 'query':
        policy = psm.query_policy()
        if policy.ok:
            module.exit_json(changed=False, policy=policy.json())
        else:
            module.fail_json(msg='{}:{}'.format(policy.status_code, policy.text))

    elif module.params.get('state') == 'absent':
        url = '/configs/security/{}/networksecuritypolicies/{}'.format('{}', module.params.get('policy_name'))
        policy = psm.rate_limit('DELETE', url)
        if policy.status_code == requests.codes.NOT_FOUND:
            module.exit_json(changed=False, policy=policy.json())
        elif policy.ok:
            module.exit_json(changed=True, policy=policy.json())

    elif module.params.get('state') == 'present':
        policy = psm.manage_policy(module.params)
        if policy.ok:
            module.exit_json(changed=psm.changed, policy=policy.json())
        else:
            module.fail_json(msg='{}:{}'.format(policy.status_code, policy.text))

    else:
        module.fail_json(msg='Unknown state specified, must be "query", "absent", or "present"')

    module.fail_json(msg='Unexpected failure:{}:{}'.format(policy.status_code, policy.text))


if __name__ == '__main__':
    main()
