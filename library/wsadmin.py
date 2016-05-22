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
short_description: This is an Ansible module for running Jython scripts using wsadmin
description:
  - This is an Ansible module for running Jython scripts using wsadmin
  - This module is NOT stateful
options:
  wasdir:
    required: false
    default: "/opt/IBM/WebSphere"
    description:
      - Path to installation location of WAS
  host:
    required: false
    default: "localhost"
    description:
      - Host name
  port:
    required: false
    default: 8879
    description:
      - SOAP port number
  node_name:
    required: true
    description:
      - Node name of this profile
  cell_name:
    required: false
    default: was_cell
    description:
      - Name of the cell
  username:
    required: true
    description:
      - WAS user name
  password:
    required: true
    description:
      - WAS user password
  script:
    required: true
    description:
      - Full or relative path to script
  params:
    required: false
    default: " "
    description:
      - Script parameters
"""

RETURN = """
msg:
    description: message of the result
    returned: in all cases
    type: string
    sample: "Script executed successfully: test.py"
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
    Main module function that runs a wsadmin script

    :return: Ansible module JSON state
    """
    module = AnsibleModule(
        argument_spec=dict(
            wasdir=dict(required=False, default="/opt/IBM/WebSphere"),
            host=dict(default="localhost", required=False),
            port=dict(default="8879", required=False),
            username=dict(required=True),
            password=dict(required=True),
            script=dict(required=True),
            params=dict(default=" ", required=False)
        )
    )

    params = module.params["params"]
    host = module.params["host"]
    port = module.params["port"]
    wasdir = module.params["wasdir"]
    username = module.params["username"]
    password = module.params["password"]
    script = module.params["script"]

    if not os.path.exists(wasdir):
        module.fail_json(msg="{0} does not exists".format(wasdir))

    child = subprocess.Popen(
        ["{0}/bin/wsadmin.sh -lang jython "
         "-conntype SOAP "
         "-host {1} "
         "-port {2} "
         "-username {3} "
         "-password {4} "
         "-f {5} "
         "{6}".format(
            wasdir,
            host,
            port,
            username,
            password,
            script,
            params
         )],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout_value, stderr_value = child.communicate()
    if child.returncode != 0:
        module.fail_json(
            msg="Failed executing wsadmin script: {0}".format(script),
            stdout=stdout_value,
            stderr=stderr_value
        )
    module.exit_json(
        changed=True,
        msg="Script executed successfully: {0}".format(script),
        stdout=stdout_value
    )

# import module snippets
from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
