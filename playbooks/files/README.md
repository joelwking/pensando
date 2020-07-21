README
------

This directory contains temporary data files for playbook execution and policy downloaded from Tetration for demonstration. Also included are credential / variable files.

The file format of the `passwords.yml` file should include at least the following:

```yaml
#
pensando_psm:
    username: admin
    host: psm.example.net
    password: "PSM_password"

```

However, you may include additional variables which you which encrypted.

One, or more, policy files (which may be encrypted) are stored in this directory for reference and demonstration purposes. These files represent policy downloaded from Tetration by module `tetration_application.py` located at https://github.com/joelwking/ansible-tetration/tree/master/library. These policy file(s) are decrypted by including the `--ask-vault-pass` option when executing playbooks or by manually decrypting the file with Ansible vault.