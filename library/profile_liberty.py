#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import subprocess


DOCUMENTATION = """
---
module: profile_liberty
author: "Amir Mofasser <amir.mofasser@gmail.com>"
short_description: This is an Ansible module for creating a WAS Liberty server
description:
  - This is an Ansible module for creating a WAS Liberty server
options:
  state:
    required: false
    default: "present"
    choices: ["present", "absent"]
    description:
      - Make sure WAS Liberty server is present or absent
  libertydir:
    required: false
    default: "/opt/IBM/Liberty"
    description:
      - Path to installation location of Liberty
  name:
    required: true
    description:
      - Name of the profile
"""

RETURN = """
msg:
    description: message of the result
    returned: in all cases
    type: string
    sample: "TEST profile created successfully"
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
    Main module function that creates or removes a WAS Liberty Server

    :return: Ansible module JSON state
    """
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["present", "absent"]),
            libertydir=dict(default="/opt/IBM/Liberty", required=True),
            name=dict(required=True),
        ),
        supports_check_mode=True
    )

    state = module.params["state"]
    libertydir = module.params["libertydir"]
    name = module.params["name"]
    server_dir = "{0}/usr/servers/{1}".format(libertydir, name)

    def raise_on_path_not_exist(path):
        """
        Raises a module failure exception if path does not exist

        :param path: File path
        :return: None
        """
        if not os.path.exists(path):
            module.fail_json(msg="{0} does not exists".format(path))

    if state == "present":
        if module.check_mode:
            if not os.path.exists(libertydir):
                module.exit_json(
                    changed=False,
                    msg="module would not run {0} does not exist".format(libertydir)
                )
            elif os.path.exists(server_dir):
                module.exit_json(
                    changed=False,
                    msg="{0} server already exist".format(name)
                )
            else:
                module.exit_json(
                    changed=True,
                    msg="{0} server would be created".format(name)
                )
        raise_on_path_not_exist(libertydir)
        child = subprocess.Popen(
            ["{0}/bin/server create {1}".format(libertydir, name)],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if child.returncode != 0:
            module.fail_json(
                msg="Failed to create liberty server {0}".format(name),
                stdout=stdout_value,
                stderr=stderr_value
            )
        module.exit_json(
            changed=True,
            msg="{0} server created successfully".format(name),
            stdout=stdout_value
        )

    if state == "absent":
        if module.check_mode:
            if not os.path.exists(libertydir):
                module.exit_json(
                    changed=False,
                    msg="module would not run {0} does not exist".format(libertydir)
                )
            elif os.path.exists(server_dir):
                module.exit_json(
                    changed=False,
                    msg="{0} server already exist".format(name)
                )
            else:
                module.exit_json(
                    changed=True,
                    msg="{0} server would be created".format(name)
                )
        raise_on_path_not_exist(libertydir)
        if os.path.exists(server_dir):
            shutil.rmtree(
                "{0}/usr/servers/{1}".format(libertydir, name),
                ignore_errors=True,
                onerror=None
            )
            module.exit_json(
                changed=True,
                msg="{0} server removed successfully".format(name)
            )
        module.exit_json(
            changed=False,
            msg="{0} server already removed".format(name)
        )

# import module snippets
from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
