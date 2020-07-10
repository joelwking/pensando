#!/usr/bin/python
#
#     Copyright (c) 2020 World Wide Technology, LLC 
#     All rights reserved. 

DOCUMENTATION = '''
---
module: network_security_policy

short_description: Create, update, query or delete a Network Security Policy 

version_added: "2.9"

description:
    - A Network Security Policy contains firewall rules such as 'to' and 'from', 'ports', 'protocols, etc.
    - and is applied to the Pensando policy and services manager (PSM). These policies are proprogated to
    - the Distributed Service Card (DSC) by the PSM. This module programatically manages the policy using the 
    - API of the PSM. 

options:
    tenant:
        description:
            - Name of the tenant
        required: true
        default: 'default'

    namespace:
        description:
            - Name of the Namespace
        required: false
        default: 'default'

    policy_name:
        description:
            - Name of the network security policy (only one network security policy is currently allowed)
        required: false
        default: 'default'

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

    username:
        description:
            - Username used to authenticate with the database
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

import time
import json
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()

from ansible.module_utils.basic import AnsibleModule

class Pensando(object):
    """
        class to manage the connection with the Pensando Policy and Service Manager (PSM)
        In documentation, you may see this referred to by the codename 'Venice'
    """
    def __init__(self, api_version=None, password=None, username=None, hostname=None, rate_limit_retry=4):
        """
        """
        self.rate_limit_retry = rate_limit_retry   # Number of attempts to issue the command before assuming the 429 is persistent

        self.api_version = api_version
        self.hostname = hostname
        self.username = username
        self.password = password
        #
        self.changed = False
        self.cookie = None
        self.headers = {'content-type':'application/json'}
        self.verify = False

    def login(self, tenant='default'):
        """
            To access and execute API calls against a Venice cluster, the client must first authenticate itself.
            This done via the login API endpoint. Once the client has made a successful login, it will
            receive a cookie (Session ID) in the header “Set-Cookie” of the response from the login call.
            The header contains the cookie name, “sid”, value, expiry time, and other info.

            The cookie is used to authenticate each API call made to Venice. The client will need to provide
            the cookie in the header in all subsequent requests to Venice.
        """

        payload = json.dumps(dict(username=self.username, password=self.password, tenant=tenant))

        r = requests.request('POST', 'https://{}/{}/login'.format(self.hostname, self.api_version), headers=self.headers, data=payload, verify=self.verify)

        if r.ok:
            self.cookie = dict(sid=r.cookies.get('sid'))

        return r


    def rate_limit(self, verb, url, **kwargs):
        """
            Policy from ADM runs can be large, provide logic to handle rate limit errors
            As this method handles all API calls, it also provides a single point to swap out 'requests'.
        """
        url = 'https://{}' + url
        url = url.format(self.hostname, self.api_version)

        for _ in range(self.rate_limit_retry):
            r = requests.request(verb, url, verify=self.verify, cookies=self.cookie, **kwargs)
            if r.status_code == requests.codes.TOO_MANY_REQUESTS:
                time.sleep(int(r.headers.get("Retry-After", 1)))    # TODO, verify, this is from Meraki
            else:
                return r
        return r

    def manage_policy(self, params):
        """
            Logic to apply or update an existing policy
            We expect 'rules' to be a list of dictionaries with the correct keywork and values

            TODO this method is only prelimiary code !!!
        """
        
        url = '/configs/security/{}/networksecuritypolicies'

        payload = json.dumps({"kind": "NetworkSecurityPolicy",
                              "api-version": params.get('api_version'),
                              "meta": {
                                "name": params.get('policy_name'),
                                "tenant": params.get('tenant'),
                                "namespace": params.get('namespace')
                                },
                              "spec": {
                                "attach-tenant": params.get('attach_tenant'),
                                "rules": params.get('rules')
                                }
                             }
                            )

        policy = self.rate_limit('POST', url, data=payload)

        if policy.status_code == requests.codes.conflict:                   # already exists!
            self.changed = False
            ### Query the existing policy?
        
        else:
            self.changed = True

        return policy

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
        rules=dict(required=False, type='list'),
        attach_tenant=dict(required=False, default=True, type='bool'),
        policy_name=dict(required=False, default='default'),
        namespace=dict(required=False, default='default')
        ),
    check_invalid_arguments=True,
    add_file_common_args=True,
    supports_check_mode=False
    )

    psm = Pensando(hostname=module.params.get('hostname'),
                   username=module.params.get('username'),
                   password=module.params.get('password'),
                   api_version=module.params.get('api_version')
                   )

    login = psm.login(tenant=module.params.get('tenant'))
    if not login.ok:
        module.fail_json(msg='{}:{}'.format(login.status_code, login.text))

    if module.params.get('state') == 'query':
        url = '/configs/security/{}/networksecuritypolicies'
        policy = psm.rate_limit('GET', url)
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
        module.fail_json(msg='unknown state specified')

    module.fail_json(msg='Unexpected failure:{}:{}'.format(policy.status_code, policy.text))
    

if __name__ == '__main__':
    main()