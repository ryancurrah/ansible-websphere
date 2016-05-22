#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import subprocess
import platform
import datetime

DOCUMENTATION = """
---
module: ibmim
author: "Amir Mofasser <amir.mofasser@gmail.com>"
short_description: This is an Ansible module for installing or
                   uninstalling IBM Installation Manager
description:
  - This module will check if IBM Installation Manager is installed
  - This module will install the IBM Installation Manager in the desired directory
  - This module will remove the IBM Installation Manager
options:
  state:
    required: false
    default: "present"
    choices: ["present", "absent"]
    description:
      - Make sure IBM Installation Manager is present or absent
  src:
    required: true
    description:
      - Path to installation files for IBM Installation Manager
  dest:
    required: false
    default: "/opt/IBM/InstallationManager"
    description:
      - Path to installation directory of IBM Installation Manager
  logdir:
    required: false
    default: "/var/log/IBM/InstallationManager"
    description:
      - Path to IBM Installation Manager install logs
"""

RETURN = """
msg:
    description: message of the result
    returned: in all cases
    type: string
    sample: "IBM IM installed successfully"
stdout:
    description: output from running a command
    returned: success or failure, when needed
    type: string
    sample: "Some WebSphere related command output"
stderr:
    description: error output from running a command
    returned: failure, when needed
    type: string
    sample: "Some WebSphere related command error output"
"""


def im_is_installed(dest):
    """
    Checks if IBM Installation Manager is installed at the destination directory

    :param dest: IBM Installation Manager installation directory
    :return: True for installed or False for not installed
    """
    if not os.path.exists(dest):
        return False
    else:
        child = subprocess.Popen(
            ["{0}/eclipse/tools/imcl listInstalledPackages".format(dest)],
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout_value, stderr_value = child.communicate()
        if stdout_value.find("com.ibm.cic.agent") < 0:
            return False
    return True


def main():
    """
    Main module function that installs or removes IBM Installation Manager

    :return: Ansible module JSON state
    """
    # Read arguments
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["present", "absent"]),
            src=dict(required=True),
            dest=dict(required=False, default="/opt/IBM/InstallationManager"),
            logdir=dict(required=False, default="/var/log/IBM/InstallationManager")
        )
    )

    state = module.params["state"]
    src = module.params["src"]
    dest = module.params["dest"]
    logdir = module.params["logdir"]

    if state == "present":
        if module.check_mode:
            if im_is_installed(dest):
                module.exit_json(
                    changed=False,
                    msg="IBM IM already installed"
                )
            else:
                module.exit_json(
                    changed=True,
                    msg="IBM IM would be installed"
                )
        if not os.path.exists("{0}/install".format(src)):
            module.fail_json(msg="{0}/install not found".format(src))
        if not os.path.exists(logdir) and not os.listdir(logdir):
                os.makedirs(logdir)
        if not im_is_installed(dest):
            logfile = "{0}_ibmim_{1}.xml".format(
                platform.node(),
                datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            )
            child = subprocess.Popen(
                ["{0}/install "
                 "-acceptLicense "
                 "--launcher.ini {0}/silent-install.ini "
                 "-log {1}/{2} "
                 "-installationDirectory {3}".format(src, logdir, logfile, dest)],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg="IBM IM installation failed",
                    stderr=stderr_value,
                    stdout=stdout_value
                )
            module.exit_json(changed=True, msg="IBM IM installed successfully")
        else:
            module.exit_json(changed=False, msg="IBM IM already installed")

    if state == "absent":
        if module.check_mode:
            if im_is_installed(dest):
                module.exit_json(
                    changed=True,
                    msg="IBM IM would be uninstalled"
                )
            else:
                module.exit_json(
                    changed=False,
                    msg="IBM IM already uninstalled"
                )
        uninstall_dir = "/var/ibm/InstallationManager/uninstall/uninstallc"
        if not os.path.exists(uninstall_dir):
            module.exit_json(changed=False, msg="IBM IM already uninstalled")
        if not im_is_installed(dest):
            child = subprocess.Popen(
                [uninstall_dir],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout_value, stderr_value = child.communicate()

            if child.returncode != 0:
                module.fail_json(
                    msg="IBM IM uninstall failed",
                    stderr=stderr_value,
                    stdout=stdout_value
                )
            shutil.rmtree(dest, ignore_errors=True, onerror=None)
            module.exit_json(
                changed=True,
                msg="IBM IM uninstalled successfully",
                stdout=stdout_value
            )
        else:
            module.exit_json(changed=True, msg="IBM IM already uninstalled")

# import module snippets
from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
