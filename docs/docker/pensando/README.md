README
------

Instructions for building and running a demonstration environment.

## Build
Build a Docker image using the currently published code. You can either clone the repo or issue a `wget` command to save a copy of the Docker file relative to your current directory in `pensando/Dockerfile`.

Build the image.
```bash
docker build -f ./pensando/Dockerfile -t joelwking/pensando:1.0 .
```

## Run
Run the image, and attach to the container.
```bash
docker run -it joelwking/pensando:1.0
```
Once attached to the container, enter the `playbooks` directory.
```bash
cd pensando/playbooks
```
## Modify credentials
The credential files are encrypted with Ansible vault. Decrypt the sample `passwords.yml` file, so you can modify the file and provide your own username, passwords and the hostname (or IP address) of the Pensando PSM.

Authorized users will be provided with the vault password 'out of band'. Specify the vault password when prompted.

```bash
ansible-vault decrypt files/passwords.yml
Vault password:
Decryption successful
```

Exit the container, leaving the container running, detach from the running container, use ^P^Q (hold Ctrl , press P , press Q , release Ctrl ).

Copy the decrypted `passwords.yml` file to your local system.  Substitute your container ID for `518fc666d90a`.
```bash
$ docker cp 518fc666d90a:/collections/ansible_collections/joelwking/pensando/playbooks/files/passwords.yml passwords.yml
```
Using your favorite text editor, edit the file on your local system.
```bash
vi passwords.yml
```
Modify the values for your target PSM. You may use an IP address rather than a hostname.
```
#
pensando_psm:
    username: admin
    host: psm.pensando.io
    password: "changeme"
```
Save the file and copy it back to the running container.
```
$ docker cp passwords.yml  518fc666d90a:/collections/ansible_collections/joelwking/pensando/playbooks/files/passwords.yml
```

## Run the Demonstration
Attach to the running container, substitute your container ID for `518fc666d90a`.
```bash
$ docker attach 518fc666d90a
```
Run the demonstration playbook. A sample policy file from the WWT Advanced Technology Center Tetration instance is provided. It also has been encrypted with Ansible vault, but can be decrypted using the Ansible vault credential. The sample file is named `PolicyPubApp.json`, additional files can also be used. The playbook uses this file by default.

Logon your PSM instance and navigate to the `Security -> Apps`.

Execute the playbook.
```bash
ansible-playbook ./tetration_app.yml  --skip-tags tetration --ask-vault-pass
```
The following is an abbreviated output from a successful execution.

```bash
[WARNING]: running playbook inside collection joelwking.pensando
Vault password:
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match
'all'

PLAY [localhost] *********************************************************************************************************

TASK [Read Tetration policy from disk] ***********************************************************************************
ok: [localhost]

TASK [Create list of protocols and ports] ********************************************************************************
ok: [localhost] => (item={u'confidence': 0.95, u'ether_type': u'ip', u'proto': u'tcp', u'consumer_filter_name': u'EPG-DEV-PUBWIN1', u'proto-ports': {u'protocol': u'tcp', u'ports': u'22-22'}, u'provider_filter_name': u'Default:cluster', u'priority': 100, u'action': u'ALLOW', u'ports': {u'to': 22, u'from': 22}})

TASK [Delete app] ********************************************************************************************************
changed: [localhost]

TASK [Add app] ***********************************************************************************************************
changed: [localhost]

PLAY RECAP ***************************************************************************************************************
localhost                  : ok=4    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```
Review the policy on the PSM GUI.

You can exit and terminate the container simply by existing shell. Remember to delete the clear text `passwords.yml` file on your local system.

## Author
Joel W. King @joelwking