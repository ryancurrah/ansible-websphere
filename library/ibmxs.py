#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import subprocess
import platform
import datetime
import shutil


DOCUMENTATION = """
---
module: ibmxs
author: "Maksim fominov <mfominov@gmail.com>"
short_description: This is an Ansible module for installing or
                   uninstalling IBM WebSphere Extreme Scale Server
description:
  - This module will check if IBM WebSphere Extreme Scale Server is installed
  - This module will install the IBM WebSphere Extreme Scale Server binaries in the desired directory
  - This module will remove the IBM WebSphere Extreme Scale Server
options:
  state:
    required: false
    default: "present"
    choices: ["present", "absent"]
    description:
      - Make sure IBM WebSphere Extreme Scale Server is present or absent
  ibmim:
    required: false
    default: "/opt/IBM/InstallationManager"
    description:
      - Path to installation directory of IBM Installation Manager
  dest:
    required: false
    default: "/opt/IBM/ExtremeScale"
    description:
      - Path to installation directory of IBM WebSphere Application Server
  im_shared:
    required: false
    description:
      - Path to Installation Manager shared resources folder
  repo:
    required: true
    description:
      - URL or path to the installation repository used by Installation Manager to install WebSphere products
  offering:
    required: false
    default: "com.ibm.websphere.WXS.v86"
    choices: ["com.ibm.websphere.WXS.v86", "com.ibm.websphere.WXS.was7.v86",
              "com.ibm.websphere.WXS.was8.v86", "com.ibm.websphere.WXSCLIENT.v86",
              "com.ibm.websphere.WXSCLIENT.was7.v86", "com.ibm.websphere.WXSCLIENT.was8.v86"]
    description:
      - Name of the offering which you want to install
  logdir:
    required: false
    default: "/var/log/IBM/ExtremeScale"
    description:
      - Path of installation log file
"""


def xs_is_installed(ibmim, offering):
    """
    Checks if IBM WebSphere Extreme Scale Server is installed

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
    Main module function that installs or removes IBM WebSphere Extreme Scale Server

    :return: Ansible module JSON state
    """
    offerings = [
        "com.ibm.websphere.WXS.v86",
        "com.ibm.websphere.WXS.was7.v86",
        "com.ibm.websphere.WXS.was8.v86",
        "com.ibm.websphere.WXSCLIENT.v86",
        "com.ibm.websphere.WXSCLIENT.was7.v86",
        "com.ibm.websphere.WXSCLIENT.was8.v86"
    ]

    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["present", "absent"]),
            ibmim=dict(required=False, default="/opt/IBM/InstallationManager"),
            dest=dict(required=False, default="/opt/IBM/ExtremeScale"),
            repo=dict(required=True),
            offering=dict(default="com.ibm.websphere.WXS.v86", choices=offerings),
            logdir=dict(required=False, default="/var/log/IBM/ExtremeScale")
        )
    )

    state = module.params["state"]
    ibmim = module.params["ibmim"]
    dest = module.params["dest"]
    repo = module.params["repo"]
    offering = module.params["offering"]
    logdir = module.params["logdir"]

    if not os.path.exists("{0}/eclipse".format(ibmim)):
        module.fail_json(msg="{0}/eclipse not found".format(ibmim))

    if state == "present":
        if not xs_is_installed(ibmim, offering):
            child = subprocess.Popen(
                ["{0}/eclipse/tools/imcl install {1} "
                 "-repositories {2} "
                 "-installationDirectory {3} "
                 "-acceptLicense".format(
                    ibmim,
                    offering,
                    repo,
                    dest
                 )],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(
                    msg="XS install failed",
                    stdout=stdout_value,
                    stderr=stderr_value
                )
            module.exit_json(changed=True, msg="XS installed successfully", stdout=stdout_value)
        else:
            module.exit_json(changed=False, msg="XS already installed")

    if state == "absent":
        if not os.path.exists(logdir) and not os.listdir(logdir):
            os.makedirs(logdir)
        if xs_is_installed(ibmim, offering):
            logfile = "{0}_xs_{1}.xml".format(
                platform.node(),
                datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
            )
            child = subprocess.Popen(
                ["{0}/eclipse/tools/imcl uninstall {1} "
                 "-installationDirectory {2} "
                 "-log {3}/{4}".format(
                    ibmim,
                    offering,
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
                module.fail_json(msg="XS uninstall failed", stdout=stdout_value, stderr=stderr_value)
            shutil.rmtree(dest, ignore_errors=False, onerror=None)
            module.exit_json(changed=True, msg="XS uninstalled successfully", stdout=stdout_value)
        else:
            module.exit_json(changed=False, msg="XS already uninstalled")

# import module snippets
from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
