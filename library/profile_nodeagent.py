#!/usr/bin/python

#
# Author: Amir Mofasser <amir.mofasser@gmail.com>
#
# This is an Ansible module. Creates a WAS Node Agent profile
# ./manageprofiles.sh -create
# -profileName appsrv02
# -profilePath /var/apps/was7/profiles/appsrv02
# -templatePath /var/apps/was7/profileTemplates/managed
# -cellName appsrv02node02
# -hostName appsrv02.webspheretools.com
# -nodeName appsrv02node02
# -enableAdminSecurity true
# -adminUserName wasadmin
# -adminPassword wasadmin


import os
import pwd
import subprocess
import platform
import datetime

def check_profile_exist(name, wasdir):
    child = subprocess.Popen([wasdir + "/bin/manageprofiles.sh -listProfiles"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_value, stderr_value = child.communicate()
    if stdout_value.find(name) < 0:
        return True

def check_node_added(node_name, wasdir, dmgr_host, username, password):
    child = subprocess.Popen(['echo -ne "y \n" |' + wasdir + "/bin/wsadmin.sh -host " +dmgr_host + " -lang jython -username " + username + " -password " + password + " -c 'print AdminTask.listNodes()'"], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_value, stderr_value = child.communicate()
    if stdout_value.find(node_name) < 0:
        return True

def check_user_exist(serviceusername):
    try:
        pwd.getpwnam(serviceusername)
    except:
        return False
    else:
        return True

def chown_user_wasdir(serviceusername, wasdir):
    uid = pwd.getpwnam(serviceusername).pw_uid
    gid = grp.getgrnam(serviceusername).gr_gid
    for root, dirs, files in os.walk(wasdir):
        for momo in dirs:
            os.chown(os.path.join(root, momo), uid, gid)
        for momo in files:
            os.chown(os.path.join(root, momo), uid, gid)

def main():

    # Read arguments
    module = AnsibleModule(
        argument_spec = dict(
            state   = dict(default='present', choices=['present', 'absent']),
            wasdir  = dict(required=True),
            name    = dict(required=True),
            enableService    = dict(required=False, default=False, choices=BOOLEANS),
            serviceUserName    = dict(required=False),
            template    = dict(required=True),
            cell_name   = dict(required=False),
            host_name = dict(required=False),
            node_name = dict(required=False),
            username = dict(required=False),
            password = dict(required=False),
            dmgr_host = dict(required=False),
            dmgr_port = dict(required=False),
            federate = dict(required=False, default=False, choices=BOOLEANS)
        )
    )

    state = module.params['state']
    wasdir = module.params['wasdir']
    name = module.params['name']
    enableservice = module.params['enableService']
    serviceusername = module.params['serviceUserName']
    template = module.params['template']
    cell_name = module.params['cell_name']
    host_name = module.params['host_name']
    node_name = module.params['node_name']
    username = module.params['username']
    password = module.params['password']
    dmgr_host = module.params['dmgr_host']
    dmgr_port = module.params['dmgr_port']
    federate = module.params['federate']

    # Check if paths are valid
    if not os.path.exists(wasdir):
        module.fail_json(msg=wasdir + " does not exists")

    if state == 'present':
        # Check profile exist
        if check_profile_exist(name, wasdir):
            # Create a profile
            child = subprocess.Popen([wasdir + "/bin/manageprofiles.sh -create -profileName " + name + " -profilePath " + wasdir + "/profiles/" + name + " -templatePath " + wasdir + "/profileTemplates/" + template + " -cellName " + cell_name + " -hostName " + host_name + " -nodeName " + node_name + " -enableAdminSecurity true -adminUserName " + username + " -adminPassword " + password], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                module.fail_json(msg="Nodeagent profile creation failed", stdout=stdout_value, stderr=stderr_value)
            chown_user_wasdir(serviceusername, wasdir)
            # Federate the node
            if federate:
                # Check node federated
                if check_node_added(node_name, wasdir, dmgr_host,username, password):
                    child = subprocess.Popen([wasdir + "/bin/addNode.sh " + dmgr_host + " " + dmgr_port + " -conntype SOAP -username " + username + " -password " + password + " -profileName " + name], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout_value, stderr_value = child.communicate()
                    if child.returncode != 0:
                        module.fail_json(msg="Node federation failed", stdout=stdout_value, stderr=stderr_value)
                    chown_user_wasdir(serviceusername, wasdir)
            # Create service
            if enableservice:
                child = subprocess.Popen([wasdir + '/bin/wasservice.sh -add nodeagent -serverName nodeagent -profilePath "' + wasdir + '/profiles/' + name + '" -logRoot "' + wasdir + '/profiles/' + name + '/logs/nodeagent" ' + ' -restart true -startType automatic' ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout_value, stderr_value = child.communicate()
                if child.returncode != 0:
                    module.fail_json(msg="Nodeagent service creation failed", stdout=stdout_value, stderr=stderr_value)
            module.exit_json(changed=True, msg=name + " profile created successfully", stdout=stdout_value)
        else:
            if federate:
                if check_node_added(node_name, wasdir, dmgr_host,username, password):
                        child = subprocess.Popen([wasdir + "/bin/addNode.sh " + dmgr_host + " " + dmgr_port + " -conntype SOAP -username " + username + " -password " + password + " -profileName " + name], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout_value, stderr_value = child.communicate()
                        if child.returncode != 0:
                            module.fail_json(msg="Node federation failed", stdout=stdout_value, stderr=stderr_value)
                        chown_user_wasdir(serviceusername, wasdir)
                # Create service
                if enableservice:
                    child = subprocess.Popen([wasdir + '/bin/wasservice.sh -add nodeagent -serverName nodeagent -profilePath "' + wasdir + '/profiles/' + name + '" -logRoot "' + wasdir + '/profiles/' + name + '/logs/nodeagent" ' + ' -restart true -startType automatic' ], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout_value, stderr_value = child.communicate()
                    if child.returncode != 0:
                        module.fail_json(msg="Nodeagent service creation failed", stdout=stdout_value, stderr=stderr_value)
            module.exit_json(changed=False, msg=name + " profile exist")

    # Remove a profile
    if state == 'absent':
        if not check_profile_exist(name, wasdir):
            # Remove service
            if enableservice:
                child = subprocess.Popen([wasdir + '/bin/wasservice.sh -remove nodeagent'], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout_value, stderr_value = child.communicate()
                if child.returncode != 0:
                    module.fail_json(msg="Nodeagent service remove failed", stdout=stdout_value, stderr=stderr_value)
            # Unfederate node
            if federate:
                if not check_node_added(node_name, wasdir, dmgr_host,username, password):
                    child = subprocess.Popen([wasdir + "/bin/removeNode.sh " + dmgr_host + " " + dmgr_port + " -conntype SOAP -username " + username + " -password " + password + " -profileName " + name], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    stdout_value, stderr_value = child.communicate()
                    if child.returncode != 0:
                        module.fail_json(msg="Node remove failed", stdout=stdout_value, stderr=stderr_value)
            child = subprocess.Popen([wasdir + "/bin/manageprofiles.sh -delete -profileName " + name], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout_value, stderr_value = child.communicate()
            if child.returncode != 0:
                # manageprofiles.sh -delete will fail if the profile does not exist.
                # But creation of a profile with the same name will also fail if
                # the directory is not empty. So we better remove the dir forcefully.
                if not stdout_value.find("INSTCONFFAILED") < 0:
                    shutil.rmtree(wasdir + "/profiles/" + name, ignore_errors=True, onerror=None)
                elif not stdout_value.find("INSTCONFPARTIALSUCCESS") < 0:
                    shutil.rmtree(wasdir + "/profiles/" + name, ignore_errors=True, onerror=None)
                else:
                    module.fail_json(msg="Nodeagent profile removal failed", stdout=stdout_value, stderr=stderr_value)
            shutil.rmtree(wasdir + "/profiles/" + name, ignore_errors=True, onerror=None)
            module.exit_json(changed=True, msg=name + " profile removed successfully", stdout=stdout_value, stderr=stderr_value)
        else:
            module.exit_json(changed=False, msg=name + " profile alrady removed")

# import module snippets
from ansible.module_utils.basic import *
if __name__ == '__main__':
    main()
