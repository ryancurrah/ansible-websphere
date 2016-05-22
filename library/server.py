#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import subprocess
import platform
import datetime


DOCUMENTATION = """
---
module: profile_server
author: "Amir Mofasser <amir.mofasser@gmail.com>"
short_description: This is an Ansible module for Stopping or Starting an Application Server
description:
  - This is an Ansible module for Stopping or Starting an Application Server
options:
  state:
    required: false
    default: "started"
    choices: ["started", "stopped"]
    description:
      - Start or stop Application server
  username:
    required: true
    description:
      - WAS user name
  password:
    required: true
    description:
      - WAS user password
  wasdir:
    required: false
    default: "/opt/IBM/WebSphere"
    description:
      - Path to installation location of WAS
"""

RETURN = """
msg:
    description: message of the result
    returned: in all cases
    type: string
    sample: "TEST stopped successfully"
stdout:
    description: output from running a command
    returned: success or failure, when needed
    type: string
    sample: "Some command execution output"
stderr:
    description: error output from running a command
    returned: failure, when needed
    type: string
    sample: "Some command execution error output"
"""


def main():
    """
    Main module function that stops or starts and Application Server

    :return: Ansible module JSON state
    """
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default='started', choices=['started', 'stopped']),
            name=dict(required=True),
            username=dict(required=True),
            password=dict(required=True),
            wasdir=dict(required=True)
        )
    )

    state = module.params['state']
    name = module.params['name']
    username = module.params['username']
    password = module.params['password']
    wasdir = module.params['wasdir']

    if not os.path.exists(wasdir):
        module.fail_json(msg="{0} does not exists".format(wasdir))

    if state == 'stopped':
        child = subprocess.Popen(
            ["{0}/bin/stopServer.sh {1} "
             "-profileName {1} "
             "-username {2} "
             "-password {3}".format(
                wasdir,
                name,
                username,
                password
             )],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            if not stderr_value.find("appears to be stopped") < 0:
                module.fail_json(
                    msg="{0} stop failed".format(name),
                    stdout=stdout_value,
                    stderr=stderr_value
                )
        module.exit_json(
            changed=True,
            msg="{0} stopped successfully".format(name),
            stdout=stdout_value
        )

    if state == 'started':
        child = subprocess.Popen(
            ["{0}/bin/startServer.sh {1} "
             "-profileName {1} "
             "-username {2} "
             "-password {3}".format(
                wasdir,
                name,
                username,
                password
             )],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            module.fail_json(
                msg="{0} start failed".format(name),
                stdout=stdout_value,
                stderr=stderr_value
            )
        module.exit_json(
            changed=True,
            msg="{0} started successfully".format(name),
            stdout=stdout_value
        )

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
