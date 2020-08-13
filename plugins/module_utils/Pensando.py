#!/usr/bin/python
#
#     Copyright (c) 2020 World Wide Technology, LLC
#     All rights reserved.

import time
import json
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


class ConnectionError(object):
    """
        Class to allow the return of an object when Connection Errors are encountered
    """
    def __init__(self, status_code=504, text='Timeout'):
        self.ok = False
        self.status_code = status_code
        self.text = text


class Pensando(object):
    """
        Class to manage the connection with the Pensando Policy and Service Manager (PSM)
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
        self.headers = {'content-type': 'application/json'}
        self.verify = False

    def login(self, tenant='default'):
        """
            To access and execute API calls against a Venice cluster, the client must first authenticate itself.
            This done via the login API endpoint. Once the client has made a successful login, it will
            receive a cookie (Session ID) in the header 'Set-Cookie' of the response from the login call.
            The header contains the cookie name, 'sid', value, expiry time, and other info.

            The cookie is used to authenticate each API call made to Venice. The client will need to provide
            the cookie in the header in all subsequent requests to Venice.
        """

        payload = json.dumps(dict(username=self.username, password=self.password, tenant=tenant))

        try:
            r = requests.request('POST', 'https://{}/{}/login'.format(self.hostname, self.api_version), headers=self.headers, data=payload, verify=self.verify)
        except requests.ConnectionError as e:
            return ConnectionError(text='Timeout in Login: {}'.format(e))           

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

            try:
                r = requests.request(verb, url, verify=self.verify, cookies=self.cookie, **kwargs)
            except requests.ConnectionError as e:
                return ConnectionError(text='Timeout in rate_limit: {}'.format(e))

            if r.status_code == requests.codes.TOO_MANY_REQUESTS:
                time.sleep(int(r.headers.get("Retry-After", 1)))    # TODO, verify, this is from Meraki
            else:
                return r
        return r

    def query_policy(self, policy_name=None):
        """
            Query the network security policy, returning the policy object
            If you provide a trailing slash on the url, you will get a 404 NOTFOUND,
            if you don't provide a trailing slash, you will get a list of policies in 'items'
            If you provide a trailing slash and a policy name, you will get the single policy requested
        """
        url = '/configs/security/{}/networksecuritypolicies'

        if policy_name:
            url = '/configs/security/{}/networksecuritypolicies{}'.format('{}', '/'+ policy_name)
        
        return self.rate_limit('GET', url)

    def manage_policy(self, params):
        """
            Logic to apply or update an existing policy
            We expect 'rules' to be a list of dictionaries with the correct keyword and values

            Error code 409  when issuing a POST with an existing policy "already exists in cache"
                       412  when issuing a POST and a policy by a different name exists "exceeds max allowed polices 1"

            Note: the URL does not need to specify the policy name when POST, but must when PUT
        """

        url = '/configs/security/{}/networksecuritypolicies'

        payload = {"kind": "NetworkSecurityPolicy",
                   "api-version": params.get('api_version'),
                   "meta": {"name": params.get('policy_name'),
                            "tenant": params.get('tenant'),
                            "namespace": params.get('namespace')
                           },
                    "spec": {"attach-tenant": params.get('attach_tenant'),
                             "rules": params.get('rules')
                            }
                  }

        policy = self.rate_limit('POST', url, data=json.dumps(payload))

        if policy.status_code == requests.codes.OK:                            # POST worked policy doesn't exist
            self.changed = True
            return policy

        if policy.status_code == requests.codes.CONFLICT:                      # 409 already exists!
            policy = self.query_policy(policy_name=params.get('policy_name'))  # query to return existing policy

            if policy.status_code == requests.codes.OK:
                payload = self.policy_payload(params, payload, policy)
                self_link = policy.json()['meta']['self-link']                 # pull the resource from self-link
                policy = self.rate_limit('PUT', self_link, data=json.dumps(payload))

                if policy.status_code == requests.codes.OK:
                    self.changed = True
            
        return policy

    def policy_payload(self, params, payload, policy):
        """
            Either replace or append the policy, if replace, we have already set the data provided by the user
            Use the existing rules and append the rules provided by the user
        """
        if params.get('operation') == 'append':

            rules = policy.json()['spec']['rules']
            rules.extend(payload['spec']['rules'])
            payload['spec']['rules'] = rules

        return payload

    def manage_app(self, params):
        """
            Logic to apply or update an App

            TODO this method is only preliminary code !!!
        """

        url = '/configs/security/{}/apps'

        payload = {"kind": "App",
                   "api-version": params.get('api_version'),
                   "meta": {"name": params.get('app_name'),
                            "tenant": params.get('tenant'),
                            "namespace": params.get('namespace')
                           },
                    "spec": {}
                  }

        if params.get('alg'):
            payload['spec']['alg'] = params.get('alg')
        if params.get('proto_ports'):
            payload['spec']['proto-ports'] = self.remove_dups(params.get('proto_ports'))

        # Verify the user specified 'alg' or 'proto_ports', (both is also acceptable)
        if len(payload['spec']) == 0:
            pass                      # Allow POST to fail, with RC=400 ["app doesn't have at least one of ProtoPorts and ALG"]

        if self.existing_app(params.get('app_name')):
            pass                      # Allow POST to fail, with RC=409 ["already exists in cache"]

        app = self.rate_limit('POST', url, data=json.dumps(payload))

        if app.status_code == requests.codes.bad_request:                # payload is incorrect
            self.changed = False
        if app.status_code == requests.codes.conflict:                   # already exists!
            self.changed = False
        else:
            self.changed = True

        return app

    def existing_app(self, app_name):
        """
            Query the specified app name.
            Return the requests object or False if the app does not exist
        """
        url = '/configs/security/{}/apps/{}'.format('{}', app_name)
        app = self.rate_limit('GET', url)
        if app.ok:
            return app

        return False

    def remove_dups(self, policy):
        """
            Policy from Tetration may have duplicate entries, eliminate the duplicate ports and protocols
            Input: a list of dictionaries
            Returns: unique list
        """
        unique = set()
        result = []

        for row in policy:
            unique.add(tuple(row.items()))

        for row in unique:
            result.append(dict(row))

        return result
