#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import subprocess
import platform
import datetime
import shutil


DOCUMENTATION = """
---
module: ibmwas
author: "Amir Mofasser <amir.mofasser@gmail.com>"
short_description: This is an Ansible module for installing or
                   uninstalling IBM WebSphere Application Server
description:
  - This module will check if IBM WebSphere Application Server is installed
  - This module will install the IBM WebSphere Application Server binaries in the desired directory
  - This module will remove the IBM WebSphere Application Server
options:
  state:
    required: false
    default: "present"
    choices: ["present", "absent"]
    description:
      - Make sure IBM WebSphere Application Server is present or absent
  ibmim:
    required: false
    default: "/opt/IBM/InstallationManager"
    description:
      - Path to installation directory of IBM Installation Manager
  dest:
    required: false
    default: "/opt/IBM/WebSphere"
    description:
      - Path to installation directory of IBM WebSphere Application Server
  im_shared:
    required: true
    description:
      - Path to Installation Manager shared resources folder
  repo:
    required: true
    description:
      - URL or path to the installation repository used by Installation Manager to install WebSphere products
  offering:
    required: false
    default: "com.ibm.websphere.ND.v85"
    choices: ["com.ibm.websphere.ND.v85", "com.ibm.websphere.IHS.v85",
              "com.ibm.websphere.PLG.v85", "com.ibm.websphere.WCT.v85",
              "com.ibm.websphere.liberty.IBMJAVA.v70", "com.ibm.websphere.liberty.v85"]
    description:
      - Name of the offering which you want to install
  ihs_port:
    required: false
    default: 8080
    description:
      - Port for IBM HTTP Server
  logdir:
    required: false
    default: "/var/log/IBM/WebSphere"
    description:
      - Path of installation log file
"""

RETURN = """
msg:
    description: message of the result
    returned: in all cases
    type: string
    sample: "WAS ND installed successfully"
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


def was_is_installed(ibmim, offering):
    """
    Checks if IBM WebSphere Application Server is installed

    :param ibmim: IBM Installation Manager installation directory
    :param offering: Name of the offering which you want to install
    :return: True for installed or False for not installed
    """
    child = subprocess.Popen(
        ["{0}/eclipse/tools/imcl listInstalledPackages".format(ibmim)],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout_value, stderr_value = child.communicate()
    if stdout_value.find(offering) < 0:
        return False
    return True


def main():
    """
    Main module function that installs or removes IBM WebSphere Application Server

    :return: Ansible module JSON state
    """
    offerings = [
        "com.ibm.websphere.ND.v85",
        "com.ibm.websphere.IHS.v85",
        "com.ibm.websphere.PLG.v85",
        "com.ibm.websphere.WCT.v85",
        "com.ibm.websphere.liberty.IBMJAVA.v70",
        "com.ibm.websphere.liberty.v85"
    ]

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["present", "absent"]),
            ibmim=dict(required=False, default="/opt/IBM/InstallationManager"),
            dest=dict(required=False, default="/opt/IBM/WebSphere"),
            im_shared=dict(required=True),
            repo=dict(required=True),
            offering=dict(default="com.ibm.websphere.ND.v85", choices=offerings),
            ihs_port=dict(default=8080),
            logdir=dict(required=False, default="/var/log/IBM/WebSphere")
        ),
        supports_check_mode=True
    )

    state = module.params["state"]
    ibmim = module.params["ibmim"]
    dest = module.params["dest"]
    im_shared = module.params["im_shared"]
    repo = module.params["repo"]
    ihs_port = module.params["ihs_port"]
    offering = module.params["offering"]
    logdir = module.params["logdir"]
    eclipse_dir = "{0}/eclipse".format(ibmim)

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
            if not os.path.exists(eclipse_dir):
                module.exit_json(
                    changed=False,
                    msg="module would not run {0} does not exist".format(eclipse_dir)
                )
            elif was_is_installed(ibmim, offering):
                module.exit_json(
                    changed=False,
                    msg="WAS ND already installed"
                )
            else:
                module.exit_json(
                    changed=True,
                    msg="WAS ND would be installed"
                )
        raise_on_path_not_exist(eclipse_dir)
        if not was_is_installed(ibmim, offering):
            child = subprocess.Popen(
                ["{0}/eclipse/tools/imcl install {1} "
                 "-repositories {2} "
                 "-installationDirectory {3} "
                 "-sharedResourcesDirectory {4} "
                 "-acceptLicense "
                 "-properties user.ihs.httpPort={5}".format(
                    ibmim,
                    offering,
                    repo,
                    dest,
                    im_shared,
                    ihs_port
                 )],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg="WAS ND install failed",
                    stdout=stdout_value,
                    stderr=stderr_value
                )
            module.exit_json(
                changed=True,
                msg="WAS ND installed successfully",
                stdout=stdout_value
            )
        else:
            module.exit_json(changed=False, msg="WAS ND already installed")

    if state == "absent":
        if module.check_mode:
            if not os.path.exists(eclipse_dir):
                module.exit_json(
                    changed=False,
                    msg="module would not run {0} does not exist".format(eclipse_dir)
                )
            elif was_is_installed(ibmim, offering):
                module.exit_json(
                    changed=True,
                    msg="WAS ND would be uninstalled"
                )
            else:
                module.exit_json(
                    changed=False,
                    msg="WAS ND already uninstalled"
                )
        raise_on_path_not_exist(eclipse_dir)
        if not os.path.exists(logdir) and not os.listdir(logdir):
            os.makedirs(logdir)
        if was_is_installed(ibmim, offering):
            logfile = "{0}_wasnd_{1}.xml".format(
                platform.node(),
                datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            )
            child = subprocess.Popen(
                ["{0}/eclipse/IBMIM "
                 "--launcher.ini {0}/eclipse/silent-install.ini "
                 "-input {1}/uninstall/uninstall.xml "
                 "-log {2}/{3}".format(
                    ibmim,
                    dest,
                    logdir,
                    logfile
                 )],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg="WAS ND uninstall failed",
                    stdout=stdout_value,
                    stderr=stderr_value
                )
            shutil.rmtree(dest, ignore_errors=False, onerror=None)
            module.exit_json(
                changed=True,
                msg="WAS ND uninstalled successfully",
                stdout=stdout_value
            )
        else:
            module.exit_json(changed=False, msg="WAS ND already uninstalled")

# import module snippets
from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
