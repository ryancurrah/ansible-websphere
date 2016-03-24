#!/usr/bin/python

#
# Author: Amir Mofasser <amir.mofasser@gmail.com>
#
# This is an Anible module. Installs/Uninstall IBM Installation Manager
#

import os
import subprocess
import platform
import datetime

def check_im_installed(dest):
    child = subprocess.Popen([dest + "/eclipse/tools/imcl listInstalledPackages"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_value, stderr_value = child.communicate()
    if stdout_value.find("com.ibm.cic.agent*") < 0:
            return True
        else:
            return

def main():

    # Read arguments
    module = AnsibleModule(
        argument_spec = dict(
            state   = dict(default='present', choices=['present', 'absent']),
            src     = dict(required=True),
            dest    = dict(required=False),
            logdir  = dict(required=False)
        )
    )

    state = module.params['state']
    src = module.params['src']
    dest = module.params['dest']
    logdir = module.params['logdir']

    if state == 'present':

        # Check if paths are valid
        if not os.path.exists(src+"/install"):
            module.fail_json(msg=src+"/install not found")
        if not os.path.exists(logdir):
            if not os.listdir(logdir):
                os.makedirs(logdir)

        if not check_im_installed(dest):
            logfile = platform.node() + "_ibmim_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".xml"
            child = subprocess.Popen([src + "/install -acceptLicense --launcher.ini " + src + "/silent-install.ini -log " + logdir + "/" + logfile + " -installationDirectory " + dest ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(msg="IBM IM installation failed", stderr=stderr_value, stdout=stdout_value)
        # Module finished
        if not check_im_installed(dest):
            module.exit_json(changed=False, msg="IBM IM already installed")
        else:
            module.exit_json(changed=True, msg="IBM IM installed successfully")

    if state == 'absent':
        uninstall_dir = "/var/ibm/InstallationManager/uninstall/uninstallc"
        if not os.path.exists("/var/ibm/InstallationManager/uninstall/uninstallc"):
            module.fail_json(msg=uninstall_dir + " does not exist")
        if not check_im_installed(dest):
            child = subprocess.Popen([uninstall_dir], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(msg="IBM IM uninstall failed", stderr=stderr_value, stdout=stdout_value)
            shutil.rmtree(dest, ignore_errors=True, onerror=None)
        # Module finished
        if not check_im_installed(dest):
            module.exit_json(changed=False, msg="IBM IM already uninstalled")
        else:
            module.exit_json(changed=True, msg="IBM IM uninstalled successfully", stdout=stdout_value)

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
