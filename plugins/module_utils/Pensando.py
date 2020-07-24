#!/usr/bin/python
#
#     Copyright (c) 2020 World Wide Technology, LLC
#     All rights reserved.

import time
import json
import requests
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


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
                              "meta": {"name": params.get('policy_name'),
                                       "tenant": params.get('tenant'),
                                       "namespace": params.get('namespace')
                                      },
                              "spec": {"attach-tenant": params.get('attach_tenant'),
                                       "rules": params.get('rules')
                                      }
                              }
                            )

        policy = self.rate_limit('POST', url, data=payload)

        if policy.status_code == requests.codes.conflict:                   # already exists!
            self.changed = False
            # TODO Query the existing policy?
        else:
            self.changed = True

        return policy

    def manage_app(self, params):
        """
            Logic to apply or update an App

            TODO this method is only prelimiary code !!!
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

        payload = json.dumps(payload)
        app = self.rate_limit('POST', url, data=payload)

        if app.status_code == requests.codes.bad_request:                # payload is incorrect
            self.changed = False
        if app.status_code == requests.codes.conflict:                   # already exists!
            self.changed = False
            # TODO Query the existing policy?
        else:
            self.changed = True

        return app

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
