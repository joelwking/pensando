README
------

This directory contains temporary data files for playbook execution and policy downloaded from Tetration for demonstration. Also included are credential / variable files.

## Credentials
The file format of the `passwords.yml` file should include at least the following:

```yaml
#
pensando_psm:
    username: admin
    host: psm.example.net
    password: "PSM_password"

```

However, you may include additional variables which you which encrypted.

## Policy files
One, or more, policy files (which may be encrypted) are stored in this directory for reference and demonstration purposes. These files represent policy downloaded from Tetration by module `tetration_application.py` located at https://github.com/joelwking/ansible-tetration/tree/master/library. These policy file(s) are decrypted by including the `--ask-vault-pass` option when executing playbooks or by manually decrypting the file with Ansible vault.

## Environments file
The file `environments.yml` is used to define the network addressing for applications in the PSM. This file provides a mapping between the name of an application, the environment (e.g. *test*, *dev*, *prod*) and the associated source and destination IP network addressing to be associated with an App in the PSM.

The playbook `playbooks/workflow_use_case.yml` references the sample `environments.yml` file. Note that if an application is not specified in the file, default values will be used as defined in the file. 