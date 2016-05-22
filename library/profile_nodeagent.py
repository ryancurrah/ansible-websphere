#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import pwd
import subprocess
import platform
import datetime


DOCUMENTATION = """
---
module: profile_nodeagent
author: "Amir Mofasser <amir.mofasser@gmail.com>"
short_description: This is an Ansible module for creating a WAS Deployment Manager profile
description:
  - This is an Ansible module for creating a WAS Deployment Manager profile
options:
  state:
    required: false
    default: "present"
    choices: ["present", "absent"]
    description:
      - Make sure WAS Deployment Manager profile is present or absent
  wasdir:
    required: false
    default: "/opt/IBM/WebSphere"
    description:
      - Path to installation location of WAS
  name:
    required: true
    description:
      - Name of the profile
  template:
    required: true
    description:
      - WAS template profile
  host_name:
    required: true
    description:
      - Host Name
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
    required: false
    default: wasadmin
    description:
      - Administrative user name of the deployment manager
  password:
    required: false
    default: wasadmin
    description:
      - Administrative user password of the deployment manager
  dmgr_host:
    required: true
    description:
      - Host name of the Deployment Manager
  dmgr_port:
    required: false
    description:
      - SOAP port number of the Deployment Manager
  federate:
    required: false
    description:
      - Wether the node should be federated to a cell. If true, cell name cannot be the same as the cell name of the deployment manager.
  enable_service:
    required: false
    choices: [true, false]
    description:
      - Enable the profile service
  service_username:
    required: false
    description:
      - Service username
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


def profile_exist(name, wasdir):
    """
    Checks if WAS Node Agent profile exists

    :param name: Profile name
    :param wasdir: Path to installation location of WAS
    :return: True for exists or False for not exists
    """
    child = subprocess.Popen(
        ["{0}/bin/manageprofiles.sh -listProfiles".format(wasdir)],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout_value, stderr_value = child.communicate()
    if stdout_value.find(name) < 0:
        return False
    return True


def node_added(node_name, wasdir, dmgr_host, username, password):
    """
    Check if the Node Agent was added to the Deployment Manager

    :param node_name: Name of the node
    :param wasdir: Path to installation location of WAS
    :param dmgr_host: Deployment manager host name
    :param username: WAS user name
    :param password: WAS user password
    :return: True for exists or False for not exists
    """
    child = subprocess.Popen(
        ["echo -ne 'y \n' | "
         "{0}/bin/wsadmin.sh "
         "-host {1} "
         "-lang jython "
         "-username {2} "
         "-password {3} "
         "-c 'print AdminTask.listNodes()'".format(
            wasdir,
            dmgr_host,
            username,
            password
         )],
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    stdout_value, stderr_value = child.communicate()
    if stdout_value.find(node_name) < 0:
        return False
    return True


def chown_user_wasdir(service_username, wasdir):
    """
    Recursively changes ownership of the WebSphere
    directory to the service username and group

    :param service_username: The service username
    :param wasdir: Path to installation location of WAS
    :return: None
    """
    uid = pwd.getpwnam(service_username).pw_uid
    gid = grp.getgrnam(service_username).gr_gid
    for root, dirs, files in os.walk(wasdir):
        for momo in dirs:
            os.chown(os.path.join(root, momo), uid, gid)
        for momo in files:
            os.chown(os.path.join(root, momo), uid, gid)


def main():
    """
    Main module function that creates or removes a WAS Node agent profile

    :return: Ansible module JSON state
    """
    module = AnsibleModule(
        argument_spec=dict(
            state=dict(default="present", choices=["present", "absent"]),
            wasdir=dict(required=False, default="/opt/IBM/WebSphere"),
            name=dict(required=True),
            template=dict(required=True),
            host_name=dict(required=True),
            node_name=dict(required=True),
            cell_name=dict(required=False, default="was_cell"),
            username=dict(required=False, default="wasadmin"),
            password=dict(required=False, default="wasadmin"),
            dmgr_host=dict(required=True),
            dmgr_port=dict(default="8879", required=False),
            federate=dict(required=False, default=False, type="bool"),
            enable_service=dict(required=False, default=False, type="bool"),
            service_username=dict(required=False),
        ),
        supports_check_mode=True
    )

    state = module.params["state"]
    wasdir = module.params["wasdir"]
    name = module.params["name"]
    template = module.params["template"]
    cell_name = module.params["cell_name"]
    host_name = module.params["host_name"]
    node_name = module.params["node_name"]
    username = module.params["username"]
    password = module.params["password"]
    dmgr_host = module.params["dmgr_host"]
    dmgr_port = module.params["dmgr_port"]
    federate = module.params["federate"]
    enable_service = module.params["enable_service"]
    service_username = module.params["service_username"]

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
            if not os.path.exists(wasdir):
                module.exit_json(
                    changed=False,
                    msg="module would not run {0} does not exist".format(wasdir)
                )
            elif profile_exist(name, wasdir):
                module.exit_json(
                    changed=False,
                    msg="{0} profile already exist".format(name)
                )
            else:
                module.exit_json(
                    changed=True,
                    msg="{0} profile would be created".format(name)
                )
        raise_on_path_not_exist(wasdir)
        if not profile_exist(name, wasdir):
            child = subprocess.Popen(
                ["{0}/bin/manageprofiles.sh -create "
                 "-profileName {1} "
                 "-profilePath {0}/profiles/{1} "
                 "-templatePath {0}/profileTemplates/{2} "
                 "-cellName {3} "
                 "-hostName {4} "
                 "-nodeName {5} "
                 "-enableAdminSecurity true "
                 "-adminUserName {6} "
                 "-adminPassword {7}".format(
                    wasdir,
                    name,
                    template,
                    cell_name,
                    host_name,
                    node_name,
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
                    msg="Nodeagent profile creation failed",
                    stdout=stdout_value,
                    stderr=stderr_value
                )
            chown_user_wasdir(service_username, wasdir)

            if federate and not node_added(node_name, wasdir, dmgr_host, username, password):
                child = subprocess.Popen(
                    ["{0}/bin/addNode.sh {1} {2} "
                     "-conntype SOAP "
                     "-username {3} "
                     "-password {4} "
                     "-profileName {5}".format(
                        wasdir,
                        dmgr_host,
                        dmgr_port,
                        username,
                        password,
                        name
                     )],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout_value, stderr_value = child.communicate()
                if child.returncode != 0:
                    module.fail_json(
                        msg="Node federation failed",
                        stdout=stdout_value,
                        stderr=stderr_value
                    )
                chown_user_wasdir(service_username, wasdir)

            if enable_service:
                child = subprocess.Popen(
                    ["{0}/bin/wasservice.sh "
                     "-add nodeagent "
                     "-serverName nodeagent "
                     "-profilePath {0}/profiles/{1} "
                     "-logRoot {0}/profiles/{1}/logs/nodeagent "
                     "-restart true "
                     "-startType automatic".format(
                        wasdir,
                        name
                     )],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout_value, stderr_value = child.communicate()
                if child.returncode != 0:
                    module.fail_json(
                        msg="Nodeagent service creation failed",
                        stdout=stdout_value,
                        stderr=stderr_value
                    )
            module.exit_json(
                changed=True,
                msg="{0} profile created successfully".format(name),
                stdout=stdout_value
            )
        else:
            if federate and not node_added(node_name, wasdir, dmgr_host, username, password):
                child = subprocess.Popen(
                    ["{0}/bin/addNode.sh {1} {2} "
                     "-conntype SOAP "
                     "-username {3} "
                     "-password {4} "
                     "-profileName {5}".format(
                        wasdir,
                        dmgr_host,
                        dmgr_port,
                        username,
                        password,
                        name
                     )],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout_value, stderr_value = child.communicate()
                if child.returncode != 0:
                    module.fail_json(
                        msg="Node federation failed",
                        stdout=stdout_value,
                        stderr=stderr_value
                    )
                    chown_user_wasdir(service_username, wasdir)
                if enable_service:
                    child = subprocess.Popen(
                        ["{0}/bin/wasservice.sh "
                         "-add nodeagent "
                         "-serverName nodeagent "
                         "-profilePath {0}/profiles/{1} "
                         "-logRoot {0}/profiles/{1}/logs/nodeagent "
                         "-restart true "
                         "-startType automatic".format(
                            wasdir,
                            name
                         )],
                        shell=True,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    stdout_value, stderr_value = child.communicate()
                    if child.returncode != 0:
                        module.fail_json(
                            msg="Nodeagent service creation failed",
                            stdout=stdout_value,
                            stderr=stderr_value
                        )
                module.exit_json(
                    changed=True,
                    msg="{0} profile already exist and was federated".format(name)
                )
            module.exit_json(
                changed=False,
                msg="{0} profile exist".format(name)
            )

    if state == "absent":
        if not os.path.exists(wasdir):
            module.exit_json(
                changed=False,
                msg="module would not run {0} does not exist".format(wasdir)
            )
        elif profile_exist(name, wasdir):
            module.exit_json(
                changed=True,
                msg="{0} profile would be removed".format(name)
            )
        else:
            module.exit_json(
                changed=True,
                msg="{0} profile already removed".format(name)
            )
        raise_on_path_not_exist(wasdir)
        if profile_exist(name, wasdir):
            if enable_service:
                child = subprocess.Popen(
                    ["{0}/bin/wasservice.sh -remove nodeagent".format(wasdir)],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout_value, stderr_value = child.communicate()
                if child.returncode != 0:
                    module.fail_json(
                        msg="Nodeagent service remove failed",
                        stdout=stdout_value,
                        stderr=stderr_value
                    )
            if federate and node_added(node_name, wasdir, dmgr_host, username, password):
                child = subprocess.Popen(
                    ["{0}/bin/removeNode.sh {1} {2} "
                     "-conntype SOAP "
                     "-username {3} "
                     "-password {4} "
                     "-profileName {5}".format(
                        wasdir,
                        dmgr_host,
                        dmgr_port,
                        username,
                        password,
                        name
                     )],
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                stdout_value, stderr_value = child.communicate()
                if child.returncode != 0:
                    module.fail_json(
                        msg="Node remove failed",
                        stdout=stdout_value,
                        stderr=stderr_value
                    )
            child = subprocess.Popen(
                ["{0}/bin/manageprofiles.sh "
                 "-delete "
                 "-profileName {1}".format(wasdir, name)],
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout_value, stderr_value = child.communicate()
            # Creation of a profile with the same name will fail if the
            # directory is not empty. So we better remove the dir forcefully.
            shutil.rmtree(
                "{0}/profiles/{1}".format(wasdir, name),
                ignore_errors=True,
                onerror=None
            )
            module.exit_json(
                changed=True,
                msg="{0} profile removed successfully".format(name),
                stdout=stdout_value,
                stderr=stderr_value
            )
        else:
            module.exit_json(changed=False, msg="{0} profile already removed".format(name))

# import module snippets
from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
