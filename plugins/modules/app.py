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
module: app

short_description: Create, update, query or delete an App

version_added: "2.9"

description:
    - An App is a network service defined either by a "protocol, port" pair, or by an application level
    - gateway (i.e. "ALG"). This module programatically manages the policy using the API of the PSM.

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

    app_name:
        description:
            - Name of the App
        required: True

    alg:
        description:
            - Application level gateway specification
        required: false

    proto_ports:
        description:
            - List of protocol, port pairs
        required: false

    state:
        description:
            - Use 'present' or 'absent' to add or remove
            - Use 'query' for listing the current policy
        required: false
        default: 'present'

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

  
  module_defaults:
    app:
      hostname: 10.255.40.39
      username: admin
      password: '{{ password }}'
      api_version: v1
      tenant: default
      namespace: default

  tasks:
    - name: Query app
      app:
        state: query

    - name: Delete app
      app:
        state: absent
        app_name: SAMPLE

    - name: Create app
      app:
        state: present
        app_name: SAMPLE
        proto_ports:
            - protocol: icmp                 # This is valid
            - protocol: icmp                 # This is valid
              ports: ""
            - protocol: tcp
              ports: "21"
            - protocol: tcp
              ports: "137-138"
            - protocol: udp
              ports: "8000,8001,8002"

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
            username=dict(required=True,),
            password=dict(required=True, no_log=True),
            state=dict(required=False, default='present'),
            tenant=dict(required=False, default='default'),
            alg=dict(required=False, type='list', default=[]),
            proto_ports=dict(required=False, type='list', default=[]),
            app_name=dict(required=False, default='default'),
            namespace=dict(required=False, default='default')
            ),
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
        url = '/configs/security/{}/apps'
        policy = psm.rate_limit('GET', url)
        if policy.ok:
            module.exit_json(changed=False, policy=policy.json())
        else:
            module.fail_json(msg='{}:{}'.format(policy.status_code, policy.text))

    elif module.params.get('state') == 'absent':
        url = '/configs/security/{}/apps/{}'.format('{}', module.params.get('app_name'))
        policy = psm.rate_limit('DELETE', url)
        if policy.status_code == requests.codes.NOT_FOUND:
            module.exit_json(changed=False, policy=policy.json())
        elif policy.ok:
            module.exit_json(changed=True, policy=policy.json())

    elif module.params.get('state') == 'present':
        policy = psm.manage_app(module.params)
        if policy.ok:
            module.exit_json(changed=psm.changed, policy=policy.json())
        else:
            module.fail_json(msg='{}:{}'.format(policy.status_code, policy.text))

    else:
        module.fail_json(msg='Unknown state specified, must be "query", "absent", or "present"')

    module.fail_json(msg='Unexpected failure:{}:{}'.format(policy.status_code, policy.text))


if __name__ == '__main__':
    main()
