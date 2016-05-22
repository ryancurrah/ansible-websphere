#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import subprocess
import platform
import datetime


DOCUMENTATION = """
---
module: liberty_server
author: "Amir Mofasser <amir.mofasser@gmail.com>"
short_description: This is an Ansible module for starting or stopping Liberty Server
description:
  - This module will start or stop a liberty server
options:
  state:
    required: false
    default: "started"
    choices: ["started", "stopped"]
    description:
      - Stop or start Liberty Server
  name:
    required: true
    description:
      - Name of the app server
  libertydir:
    required: true
    description:
      - Path to binary files of the application server
"""


def main():
    """
    Main module function that starts or stops Liberty Server

    :return: Ansible module JSON state
    """
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="started", choices=["started", "stopped"]),
            name=dict(required=True),
            libertydir=dict(required=True)
        )
    )

    state = module.params["state"]
    name = module.params["name"]
    libertydir = module.params["libertydir"]

    if not os.path.exists(libertydir):
        module.fail_json(msg="{0} does not exists".format(libertydir))

    if state == "stopped":
        child = subprocess.Popen(
            ["{0}/bin/server stop {1}".format(libertydir, name)],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            if not stderr_value.find("is not running") < 0:
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

    if state == "started":
        child = subprocess.Popen(
            ["{0}/bin/server start {1}".format(libertydir, name)],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            if not stderr_value.find("is running with process") < 0:
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
if __name__ == "__main__":
    main()
