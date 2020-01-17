# -*- coding:UTF-8 -*-

import requests
import urllib3
import json
import time
import os
import sys
import subprocess
import lxml
import random
import paramiko

########################################################################################################################
# Globals
########################################################################################################################
# CBAM url and CBAM client
# Following is for cbam 10.75.44.14
# cbam_url = 'https://10.75.44.14'
# client_id = 'cbam_rest'
# client_secret = '5b895f51-fbec-46b9-bf98-8bd5ab6c859d'
# gui_client_id = 'lcm'
# gui_client_passwd = '-Assured1111'
# Following is for cbam 10.75.44.20
cbam_url = 'https://10.75.44.20'
client_id = 'cbam_rest'
client_secret = 'ed5683fb-2af7-45b5-be63-78b4e4c37bf5'
gui_client_id = 'lcm'
gui_client_passwd = '-Assured11'

working_dir = r'D:\Programs\JetBrains\PycharmProjects\py37projects\lcm_auto_cbam_restful'
sig_data_dir = working_dir + r'\data\sig-plane'
media_data_dir = working_dir + r'\data\media-plane'

vnflcm_base_path = cbam_url + '/vnflcm/v1'
vnfpkgm_base_path = cbam_url + '/vnfpkgm/v1'

operationState_list = ['STARTING', 'FAILED', 'ROLLED_BACK', 'PROCESSING', 'COMPLETED']
operation_list = ['MODIFY_INFO', 'INSTANTIATE', 'TERMINATE', 'SCALE', 'OTHER']
operationName_list = ['custom:backup']

########################################################################################################################
def print_response(response):
    print('response: ', response)
    print('response.headers: ', response.headers)
    print('response.text: ', response.text)

def dump_response_data(response, funcname):
    print('Now at function:', funcname)
    data = json.loads(response.text)
    print(data)

def ssh_command_passwd(cmd, ip, login, passwd):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, port=22, username=login, password=passwd)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    res, err = stdout.read(), stderr.read()
    result = res if res else err
    ssh.close()
    # print(result.decode())
    return result.decode()

def ssh_command_pubkey(cmd, ip, login, privkey):
    private_key = paramiko.RSAKey.from_private_key_file(privkey)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, port=22, username=login, pkey=private_key)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    res, err = stdout.read(), stderr.read()
    result = res if res else err
    ssh.close()
    # print(result.decode())
    return result.decode()

def ssh_command(cmd, ip, login, pass_key, type):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    if type == 'passwd':
        ssh.connect(hostname=ip, port=22, username=login, password=pass_key)
    elif type == 'pubkey':
        private_key = paramiko.RSAKey.from_private_key_file(pass_key)
        ssh.connect(hostname=ip, port=22, username=login, pkey=private_key)
    stdin, stdout, stderr = ssh.exec_command(cmd)
    res, err = stdout.read(), stderr.read()
    result = res if res else err
    ssh.close()
    return result.decode()

# Get token
def get_token():
    headers = {'Accept': '*/*', 'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    address = cbam_url + '/auth/realms/cbam/protocol/openid-connect/token'
    verify = False
    response = requests.post(address, data=data, headers=headers, verify=verify)
    data = json.loads(response.text)
    token = response.json()["access_token"]
    return 'bearer ' + token

# This is to get vnf list
def get_vnfs():
    token_bear = get_token()
    headers = {'Authorization': token_bear}
    url_vnf = cbam_url + '/vnflcm/v1' + '/vnf_instances'
    address = url_vnf
    verify = False
    response = requests.get(address, headers=headers, verify=verify)
    data = json.loads(response.text)
    for vnf in data:
        print('\n Now is: ', vnf['name'])
        for i, j in vnf.items():
            print(i, ':', j)

def get_vnf_packages():
    token_bear = get_token()
    headers = {'Authorization': token_bear}
    address = cbam_url + '/vnfpkgm/v1' + '/vnf_packages'
    verify = False
    response = requests.get(address, headers=headers, verify=verify)
    dump_response_data(response, 'get_vnf_packages')

class SetUps(object):
    pass

class CleanUps(object):
    pass

########################################################################################################################
# VNF Packages
class VnfPkgs(object):
    def __init__(self):
        self.vnfpkg_baseload = sig_data_dir + 'Nokia_sig_SBC-VNF_Package.zip'
        self.vnfpkg_sutoload = sig_data_dir + 'Nokia_sig_SBC-VNF_Package-SUToLoad.zip'
        self.vnfpkg_cssutoload = sig_data_dir + 'Nokia_sig_SBC-VNF_Package-CSSUToLoad.zip'
        self.vnfpkgs_list = []

    def get_vnfpkgs(self):
        self.vnfpkgs_list = []
        token_bear = get_token()
        headers = {'Authorization': token_bear}
        address = cbam_url + '/vnfpkgm/v1' + '/vnf_packages'
        verify = False
        response = requests.get(address, headers=headers, verify=verify)
        data = json.loads(response.text)
        if len(data) != 0:
            for vp in data:
                vnfpkg = VnfPkg()
                vnfpkg.id = vp['id']
                vnfpkg.vnfdId = vp['vnfdId']
                vnfpkg.vnfProvider = vp['vnfProvider']
                vnfpkg.vnfProductName = vp['vnfProductName']
                vnfpkg.vnfSoftwareVersion = vp['vnfSoftwareVersion']
                vnfpkg.vnfdVersion = vp['vnfdVersion']
                vnfpkg.onboardingState = vp['onboardingState']
                vnfpkg.operationalState = vp['operationalState']
                vnfpkg.userDefinedData = vp['userDefinedData']
                vnfpkg._links = vp['_links']
                self.vnfpkgs_list.append(vnfpkg)

    def dump_vnfpkgs(self):
        if len(self.vnfpkgs_list) != 0:
            for vp in self.vnfpkgs_list:
                vp.dump_vnfpkg()

    def upload_vnfpkg(self, version = '37.28.06'):
        vnfpkg = ''
        if version == sigVersion:
            vnfpkg = self.vnfpkg_baseload
        elif version == sigVersion_SU:
            vnfpkg = self.vnfpkg_sutoload
        print('vnfpkg: ', vnfpkg)
        # To-do: add check if the vnfpkg has already been uploaded
        token_bear = get_token()
        # First POST vnf_packages to generate one new vnf pkg
        headers = {'Authorization': token_bear}
        address = cbam_url + '/vnfpkgm/v1' + '/vnf_packages'
        verify = False
        response = requests.post(address, headers=headers, verify=False)
        if response.status_code != 201:
            print('vnfpkg creation failed.')
            exit(1)
        data = json.loads(response.text)
        id = data['id']
        print('New vnfpkg id: ', id)
        #Then PUT content to content of new vnf pkg
        address = cbam_url + '/vnfpkgm/v1' + '/vnf_packages/' + id + '/package_content'
        headers = {'Authorization': token_bear, 'Content-Type': 'application/octet-stream'}
        response = requests.put(
            address,
            data=open(vnfpkg, 'rb'),
            headers=headers,
            verify=verify)
        if response.status_code != 202:
            print('vnfpkg content upload failed.')
            # Here need to delete the newly created vnf pkg
            headers = {'Authorization': token_bear}
            address = cbam_url + '/vnfpkgm/v1' + '/vnf_packages/' + id
            requests.delete(address, headers=headers, verify=verify)
            exit(1)
        print('VNF PKG uploaded successfully.')

    def get_vnfpkg_by_swversion(self, swversion):
        self.get_vnfpkgs()
        for vp in self.vnfpkgs_list:
            if vp.vnfSoftwareVersion.endswith(swversion):
                print('id in get_vnfpkg_by_swversion: ', vp.id)
                return vp.id

    def delete_vnfpkg_by_swversion(self, swversion):
        id = self.get_vnfpkg_by_swversion(swversion)
        self.delete_vnfpkg_by_id(id)

    def delete_vnfpkg_by_id(self, id):
        token_bear = get_token()
        headers = {'Authorization': token_bear}
        address = cbam_url + '/vnfpkgm/v1' + '/vnf_packages/' + id
        print('address: ', address)
        verify = False
        response = requests.get(address, headers=headers, verify=verify)
        data = json.loads(response.text)
        print('The vnfpkg to be deleted: ', data)
        requests.delete(address, headers=headers, verify=verify)

# VNF Package
class VnfPkg(object):
    def __init__(self):
        self.id = ''
        self.vnfdId = ''
        self.vnfProvider = ''
        self.vnfProductName = ''
        self.vnfSoftwareVersion = ''
        self.vnfdVersion = ''
        self.onboardingState = ''
        self.operationalState = ''
        self.userDefinedData = ''
        self._links = ''

    def get_id(self):
        return self.id

    def get_vnfdId(self):
        return self.vnfdId

    def get_vnfProductName(self):
        return self.vnfProductName

    def get_vnfSoftwareVersion(self):
        return self.vnfSoftwareVersion

    def get_vnfdVersion(self):
        return self.vnfdVersion

    def dump_vnfpkg(self):
        print('id: ', self.id)
        print('vnfdId: ', self.vnfdId)
        print('vnfProvider: ', self.vnfProvider)
        print('vnfProductName: ', self.vnfProductName)
        print('vnfSoftwareVersion: ', self.vnfSoftwareVersion)
        print('vnfdVersion: ', self.vnfdVersion)
        print('onboardingState: ', self.onboardingState)
        print('operationalState: ', self.operationalState)
        print('userDefinedData: ', self.userDefinedData)
        print('_links: ', self._links)
        print('\n')

########################################################################################################################
# Signaling plane VNF
class SigVnf(object):
    def __init__(self, vnfdId, name='sbclcm-sig-plane', description = 'SBC LCM Sig-Plane VNF for Auto Test via CBAM REST APIs'):
        self.name = name
        self.description = description
        self.vnfdId = vnfdId
        self.id = ''
        self.opStatus = ''
        self.operationState = ''
        self.scaleLevel = 1
        self.maxScaleLevel = 5
        self.vnfcInstanceId_List = []
        self.instantiate_file = sig_data_dir + r'\LCM_instantiate_params.json'
        self.cssu_instantiate_file = sig_data_dir + r'\cssu_LCM_instantiate_params.json'
        self.vnflcm_base_path = cbam_url + '/vnflcm/v1'
        self.vnflcm_instances = self.vnflcm_base_path + '/vnf_instances/'
        self.vnfpkgm_base_path = cbam_url + '/vnfpkgm/v1'
        self.vnflcm_create = vnflcm_base_path + '/vnf_instances'

    def set_vnflcm_apis(self):
        self.operationState             = vnflcm_base_path + '/vnf_lcm_op_occs'
        self.vnflcm_create              = vnflcm_base_path + '/vnf_instances'
        self.vnflcm_instantiate         = self.vnflcm_instances + self.id + '/instantiate'
        self.vnflcm_terminate           = self.vnflcm_instances + self.id + '/terminate'
        self.vnflcm_delete              = self.vnflcm_instances + self.id
        self.vnflcm_get                 = self.vnflcm_instances + self.id
        self.vnflcm_modify              = self.vnflcm_instances + self.id
        self.vnflcm_scale               = self.vnflcm_instances + self.id + '/scale'
        self.vnflcm_heal                = self.vnflcm_instances + self.id + '/heal'
        self.vnflcm_upgrade             = self.vnflcm_instances + self.id + '/upgrade'
        self.vnflcm_custom_backup       = self.vnflcm_instances + self.id + '/custom/backup'
        self.vnflcm_custom_connect      = self.vnflcm_instances + self.id + '/custom/connect_SBC_Media_VNF'
        self.vnflcm_custom_disconnect   = self.vnflcm_instances + self.id + '/custom/disconnect_SBC_Media_VNF'
        self.vnflcm_custom_dbrestore    = self.vnflcm_instances + self.id + '/custom/DB_Restore'
        self.vnflcm_custom_upgrade_precheck     = self.vnflcm_instances + self.id + '/custom/upgrade_precheck'
        self.vnflcm_custom_upgrade_1_apply      = self.vnflcm_instances + self.id + '/custom/upgrade_1_apply'
        self.vnflcm_custom_upgrade_2_activate   = self.vnflcm_instances + self.id + '/custom/upgrade_2_activate'
        self.vnflcm_custom_upgrade_3_commit     = self.vnflcm_instances + self.id + '/custom/upgrade_3_commit'
        self.vnflcm_custom_upgrade_archive      = self.vnflcm_instances + self.id + '/custom/upgrade_archive'

    def write_status(self):
        pass

    def get_vnfdId(self):
        return self.vnfdId

    def get_id(self):
        return self.id

    def set_id(self, id):
        self.id = id

    def create_vnf(self):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        response = requests.post(
            self.vnflcm_create,
            headers=headers,
            json={
                "vnfdId": self.vnfdId,
                "vnfInstanceName": self.name,
                "vnfInstanceDescription": self.description
            },
            verify=False)
        if response.status_code != 201:
            print('create_vnf failed. Error out.')
            exit(1)
        # data = json.loads(response.text)
        dump_response_data(response, 'create_vnf')
        # get vnf ID
        data = json.loads(response.text)
        self.id = data['id']
        print('create_vnf:id: ', self.get_id())
        # Now it's time to set rest api interfaces since we have got id
        self.set_vnflcm_apis()

    #MODIFY use PATCH
    def modify_auto_backup_vnf(self, periodInSeconds=86220, enabled=False):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        response = requests.patch(
            self.vnflcm_modify,
            headers=headers,
            json={
                "vnfConfigurableProperties": {
                    "operation_triggers": {
                        "auto_backup": {
                            "periodInSeconds": periodInSeconds,
                            "enabled": enabled
                        }
                    }
                }
            },
            verify=False)
        if response.status_code == 202:
            print('Modify auto_backup successful: ' + 'periodInSeconds:' +
                  str(periodInSeconds) + ';enabled:' + str(enabled))
        else:
            print('Modify auto_backup failed. Error out.')
            exit(1)

    def modify_auto_scale_vnf(self, periodInSeconds=600, enabled=False):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        response = requests.patch(
            self.vnflcm_modify,
            headers=headers,
            json={
                "vnfConfigurableProperties": {
                    "operation_triggers": {
                        "auto_scale": {
                            "periodInSeconds": periodInSeconds,
                            "enabled": enabled
                        }
                    }
                }
            },
            verify=False)
        if response.status_code == 202:
            print('Modify auto_scale successful: ' + 'periodInSeconds:' +
                  str(periodInSeconds) + ';enabled:' + str(enabled))
        else:
            print('Modify auto_scale failed. Error out.')
            exit(1)

    def instantiate_vnf(self):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        parameters = json.load(open(self.instantiate_file, "rb"))
        response = requests.post(self.vnflcm_instantiate, headers=headers, json=parameters, verify=False)
        if response.status_code == 202:
            print('instantiate_vnf successful.')
        else:
            print('instantiate_vnf failed. Error out.')
            exit(1)

    def cssu_instantiate_vnf(self):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        parameters = json.load(open(self.cssu_instantiate_file, "rb"))
        response = requests.post(self.vnflcm_instantiate, headers=headers, json=parameters, verify=False)
        if response.status_code == 202:
            print('cssu_instantiate_vnf successful.')
        else:
            print('cssu_instantiate_vnf failed. Error out.')
            exit(1)

    def terminate_vnf(self):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        response = requests.post(
            self.vnflcm_terminate,
            headers=headers,
            json={
                "terminationType": "FORCEFUL"
            },
            verify=verify)
        if response.status_code == 202:
            print('Sig Plane Terminate started')
        else:
            print('Sig Plane Terminate failed. exit.')
            exit(1)

    def delete_vnf(self):
        token_bear = get_token()
        headers = {"Authorization": token_bear}
        verify = False
        response = requests.delete(self.vnflcm_delete, headers=headers, verify=verify)

    def upgrade_vnf(self, vnfdId):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        response = requests.post(
            self.vnflcm_upgrade,
            headers=headers,
            json={
                "vnfdId": vnfdId,
                "apiVersion": "4.0"
            },
            verify=verify)
        if response.status_code == 202:
            print('Sig Plane Upgrade- Change Package Version Started')
        else:
            print('Sig Plane Upgrade- Change Package Version Failed. Exit.')
            exit(1)

    def get_vnf(self):
        token_bear = get_token()
        headers = {"Authorization": token_bear}
        verify = False
        response = requests.get(self.vnflcm_get, headers=headers, verify=verify)
        if response.status_code == 200:
            data = json.loads(response.text)
            # print(data)
            return data

    def get_vnfcInstanceId_List(self):
        data = self.get_vnf()
        for vnfcinfo in data['instantiatedVnfInfo']['vnfcResourceInfo']:
            self.vnfcInstanceId_List.append(vnfcinfo['id'])
        print('vnfcInstanceId_List: ', self.vnfcInstanceId_List)

    def backup_vnf(self, additionalParam):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        response = requests.post(
            self.vnflcm_custom_backup,
            headers=headers,
            json={
                "additionalParams": additionalParam
            },
            verify=verify)
        if response.status_code != 202:
            print('Sig Plane Backup Failed.')
            exit(1)

    def connect_sbc_media_vnf(self, additionalParam):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        response = requests.post(
            self.vnflcm_custom_connect,
            headers=headers,
            json={
                "additionalParams": additionalParam
            },
            verify=verify)
        if response.status_code != 202:
            print('Sig Plane Connect sbc Media VNF Failed.')
            exit(1)

    def disconnect_sbc_media_vnf(self, additionalParam):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        response = requests.post(
            self.vnflcm_custom_disconnect,
            headers=headers,
            json={
                "additionalParams": additionalParam
            },
            verify=verify)
        if response.status_code != 202:
            print('Sig Plane Disconnect sbc Media VNF Failed.')
            exit(1)

    def dbrestore_vnf(self, additionalParam):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        response = requests.post(
            self.vnflcm_custom_dbrestore,
            headers=headers,
            json={
                "additionalParams": additionalParam
            },
            verify=verify)
        if response.status_code != 202:
            print('Sig Plane DB restore Failed.')
            exit(1)

    def heal_vnf(self, vnfcInstanceId=None, cause='Sig Plane VM Heal: OAM.NOKIA-LCP-VMA'):
        if vnfcInstanceId is None:
            vnfcInstanceId = ['OAM.NOKIA-LCP-VMA']
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        response = requests.post(
            self.vnflcm_heal,
            headers=headers,
            json={
                "cause": cause,
                "vnfcInstanceId": vnfcInstanceId,
                "additionalParams": {"monitorRetries": 90, "monitorDelay": 20}
            },
            verify=verify)
        if response.status_code != 202:
            print('Sig Plane Scale Failed: ', vnfcInstanceId)
            exit(1)

    def scale_vnf(self, scaleType='SCALE_OUT', step=1, aspectId="sc_Aspect"):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        response = requests.post(
            self.vnflcm_scale,
            headers=headers,
            json={
                "type": scaleType,
                "aspectId": aspectId,
                "numberOfSteps": step
            },
            verify=verify)
        if response.status_code != 202:
            print('Sig Plane Scale Failed: ' + scaleType)
            exit(1)

    def get_scaleStatus(self):
        data = self.get_vnf()
        scaleStatus = data['instantiatedVnfInfo']['scaleStatus']
        print('scaleStatus: ', scaleStatus)
        for ss in scaleStatus:
            if ss['aspectId'] == 'sc_Aspect':
                self.scaleLevel=ss['scaleLevel']
                self.maxScaleLevel=ss['maxScaleLevel']
                print('scaleLevel: ' + str(self.scaleLevel))
                print('maxScaleLevel: ' + str(self.maxScaleLevel))

    def upgrade_precheck(self):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        # Need to carry empty data in requests.post, otherwise will fail
        response = requests.post(self.vnflcm_custom_upgrade_precheck, json={}, headers=headers, verify=verify)
        if response.status_code != 202:
            print('Sig Plane Upgrade Precheck Failed.')
            exit(1)

    def upgrade_1_apply(self, additionalParam):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        response = requests.post(
            self.vnflcm_custom_upgrade_1_apply,
            headers=headers,
            json={
                "additionalParams": additionalParam
            },
            verify=verify)
        if response.status_code != 202:
            print('Sig Plane Upgrade 1 Apply Failed.')
            exit(1)

    def upgrade_2_activate(self):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        # Need to carry empty data in requests.post, otherwise will fail
        response = requests.post(self.vnflcm_custom_upgrade_2_activate, json={}, headers=headers, verify=verify)
        if response.status_code != 202:
            print('Sig Plane Upgrade 2 Activate Failed.')
            exit(1)

    def upgrade_3_commit(self):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        # Need to carry empty data in requests.post, otherwise will fail
        response = requests.post(self.vnflcm_custom_upgrade_3_commit, json={}, headers=headers, verify=verify)
        if response.status_code != 202:
            print('Sig Plane Upgrade 3 Commit Failed.')
            exit(1)

    def upgrade_archive(self, additionalParam):
        token_bear = get_token()
        headers = {"Authorization": token_bear, "Content-Type": "application/json"}
        verify = False
        response = requests.post(
            self.vnflcm_custom_upgrade_archive,
            headers=headers,
            json={
                "additionalParams": additionalParam
            },
            verify=verify)
        if response.status_code != 202:
            print('Sig Plane Upgrade Archive Failed.')
            exit(1)

    def get_latestOperationState(self):
        token_bear = get_token()
        headers = {"Authorization": token_bear}
        verify = False
        response = requests.get(self.operationState, headers=headers, verify=verify, timeout=10)
        if response.status_code == 200:
            data = json.loads(response.text)
            return data[0]['operationState']
        else:
            print('Failed to get Latest Operation Status.')
            return None

    # operation: 'MODIFY_INFO', 'INSTANTIATE', 'OTHER',
    def get_operationState(self, operation, operationName):
        self.opStatus = ''
        token_bear = get_token()
        headers = {"Authorization": token_bear}
        verify = False
        response = requests.get(self.operationState, headers=headers, verify=verify, timeout=10)
        if response.status_code == 200:
            data = json.loads(response.text)
            for item in data:
                # Need to find a way to use operationName
                if (item['vnfInstanceId'] == self.id) and (item['operation'] == operation):
                    self.opStatus = item['operationState']
                    break
        return self.opStatus

# Media plane VNF
class MediaVnf(object):
    def __init__(self, vnfdId):
        self.vnfdId = vnfdId
        pass

########################################################################################################################
# Signaling plane VNF LCM Tests
class MediaVnfLcmTestDriver(object):
    def __init__(self, mediavnf):
        self.mediavnf = mediavnf
        pass

# Signaling plane VNF LCM Tests
class SigVnfLcmTestDriver(object):
    def __init__(self, sigvnf):
        # Need to determine which is sig plane vnf
        # Need to get all vnfs and decide
        self.getvnfs = cbam_url + '/vnflcm/v1' + '/vnf_instances/'
        self.status_file = working_dir + '.sig_status'
        self.sigvnf = sigvnf
        self.sig_id = ''
        self.fixed_scm_ip = '10.75.44.10,10.75.44.11'
        # centos is for pubkey login
        self.backup_server_login_pubkey = 'centos'
        self.local_private_key = r'C:\Users\shawnx\.ssh\id_rsa'
        # root is for passwd login
        self.backup_server_login_passwd = 'root'
        self.backup_server_passwd_passwd = 'newsys'
        self.backup_server_ip = '10.75.44.7'
        self.backup_server_dir = '/var/www/html/sbclcm-auto/'
        self.cssu_zip = 'cssu_archive.zip'
        self.backup_zip = 'backup.zip'
        self.backup_server1 = 'centos@10.75.44.7:/var/www/html/sbclcm-auto/'
        self.backup_server2 = 'centos@10.75.44.7:/var/www/html/sbclcm-auto/'
        self.backup_server_creds1 = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAvX/4YeeQcBqR2sjW18T8WbiAVdnVIs4ZNNlTEG+Ps6OFeQFm\nUBwXvtqbetitEhAAU2OT4ivuh+B20KM/WHM6r57URA1qgNK8Sk9tLUiZRvMDkDR8\nWpAEQSw0fvkO91J93q9Siu3h2uhiKtB1ARESb5DcayttXg0fr9U5hmT/mD5MJ/nC\npfE5ByuHzmWSJo9Vya+YM0UBZnja38vhfc8mAeJ0pxQVxkoL4KzYF2JJAqIzH9tw\nkJLfZbNlxQtOKRCSRWtdcCHckfS0/BISf9f0jdG9h15q3vvKc0j+dXCJny5jfgCc\nHl2+e4RYK3evvJPWQNSZ/+iMZqn1SyligpbKXQIDAQABAoIBABtfsAach73Z6LXd\nC0Px/a4MO+Wq6OH1Oajrt9cI9o4xkedP73KlDD0SoSEWybFxRErHeKZUSEmygBdV\nbaIeSxzxaaJG+dqQFoj5fkDrWtDn69zZ6BjA8wxjEVZCLgpGDU6srtTI1jZkGUIs\nCKrVx378QwrsJAlRBgHFYGDsmAtqvLetbMm272K/hz2e4jxMf08LcDx1fUgDO+hD\naMjzVmbIYNbFftLQD/yG+DgtvP7f728yoG8gNXC0shPqetHtfnwCbJ3H1ju9svGW\nDFYzrBwZZZMY0nTAWjY/DXSS1ORrq7LXSIPKf/3kobfMU67ugeC6NrEsncdIKvIE\n/yVKTrUCgYEA4iMKFeRdIWjzijg3Iie6k09vduTH+nsELDKjzHqcyPmEBisidFQA\nFMjJO8+jh+KKusqYEDp1l4qHLbtN1hatKZV6PwfcmPITA+uczZa9Z3YAKsI1GAOi\n0GUmjmoElOGc1I+k55fWAt48hWRoPd4vrlGaAw8otIdiSXHdpwdb3rsCgYEA1oZa\nH7R4j757Ny47NHIPsXsfZwyD2TTU+oOIDOPvBWN6GuU70N5ZW21529mwLKbr5e2H\n9ofMhSJQkXlg6e6F5wmj7Q0n+mGNoPeNoq7bRB1gHelODs4vAnnVNz2vCGt0uqSd\n+UoemidWKm8RFNAG8yS9uoQrk7sZpA5MYHrJBccCgYBELqxrzV8HI83Kbwiwk6n9\noIXLI0/ohg7MBLi+fnmnXxQfiAHrcShVG/UQw5pa7kNF7q/KtNWfy3TWpRLi6hNr\n5lXli0lIFDUHiZLNqhWRjFKgkc3QX8hHbTgi2HRpL11J+cWOzokIdFlrHssPXF6k\nAJafNYLga7GG034xTla04QKBgAK5Meu1HtK0WFwa+iVwTUKzjXKBdisLwKhtgwym\n2CH5YVN2FYxRRlEi0qk32kS22cfRfChlEPOfu+Yc5F4T6R9FwA8CW7+R/XpNqj6m\neaIjvVSj4ZnOhEpDwbEx10cEFjdIX7kKd9j9JtrjDhR1j6EGlmIHy4XUmj66771J\n0cOBAoGBAJyXMkKKbsSGDGYoyzazVjLYzIqmC2tOnYkHHl3heEZN/LkphPuLdbcj\n2pk2wlqskZ2LQxnylJDgIIA6rJBoLvBj5Xo+9EN7uidHHv+8JGBy4FPcDNl2O5RR\nLbiaAVSQNQNm+hku9e0XH0+YFrCP+0Q8D9DGYzhupslAzJEyoz3R\n-----END RSA PRIVATE KEY-----'
        self.backup_server_creds2 = self.backup_server_creds1
        self.su_deft_url = 'http://10.75.44.7/deft_R37.28.XX_R37.28.XX.zip'
        self.su_deft_key = '13582'
        self.su_to_image = 'nokia-SBC_sig-RHEL7-R37.28.06.0020.x86_64.qcow2'
        self.su_to_version = 'R37.28.06.0020'
        # Following are additionalParams for various operations
        self.additinalParams_Backup_Local = {
            'backupServer1': '',
            'backup_server_credentials1': '',
            'backupServer2': '',
            'backup_server_credentials2': ''
        }
        self.additinalParams_Backup_Remote_1 = {
            'backupServer1': self.backup_server1,
            'backup_server_credentials1': '',
            'backupServer2': '',
            'backup_server_credentials2': ''
        }
        self.additinalParams_Backup_Remote_2 = {
            'backupServer1': '',
            'backup_server_credentials1': '',
            'backupServer2': self.backup_server2,
            'backup_server_credentials2': ''
        }
        self.additinalParams_Backup_Remote_12 = {
            'backupServer1': self.backup_server1,
            'backup_server_credentials1': '',
            'backupServer2': self.backup_server2,
            'backup_server_credentials2': ''
        }
        self.additinalParams_Backup_Remote_Creds_1 = {
            'backupServer1': self.backup_server1,
            'backup_server_credentials1': self.backup_server_creds1,
            'backupServer2': '',
            'backup_server_credentials2': ''
        }
        self.additinalParams_Backup_Remote_Creds_2 = {
            'backupServer1': '',
            'backup_server_credentials1': '',
            'backupServer2': self.backup_server2,
            'backup_server_credentials2': self.backup_server_creds2
        }
        self.additinalParams_Backup_Remote_Creds_12 = {
            'backupServer1': self.backup_server1,
            'backup_server_credentials1': self.backup_server_creds1,
            'backupServer2': self.backup_server2,
            'backup_server_credentials2': self.backup_server_creds2
        }
        self.additinalParams_Connection = {
            'FixedScmIpAddress': self.fixed_scm_ip,
            'LcmUser': 'cloud-user',
            'ApplUser': 'diag',
            'ApplUserPw': '-assured'
        }
        self.additinalParams_Disconnection = {
            'FixedScmIpAddress': self.fixed_scm_ip,
            'LcmUser': 'cloud-user'
        }
        self.additinalParams_DBRestore = {
            'backupInfo': self.backup_server1 + self.backup_zip,
            'restore_media_plane': 'ALL'
        }
        self.additinalParams_Upgrade1Apply = {
            'upgradeImageName': self.su_to_image,
            'upgradeVersion': self.su_to_version,
            'upgradeDeftKey': self.su_deft_key,
            'upgradeDeftUrl': self.su_deft_url
        }
        self.additinalParams_UpgradeArchive = {
            'upgradeDeftKey': self.su_deft_key,
            'upgradeDeftUrl': self.su_deft_url,
            'upgradeVersion': self.su_to_version,
            'upgradeServer': self.backup_server1,
            'upgradeServerCredentials': '',
        }
        self.additinalParams_UpgradeArchive_Creds = {
            'upgradeDeftKey': self.su_deft_key,
            'upgradeDeftUrl': self.su_deft_url,
            'upgradeVersion': self.su_to_version,
            'upgradeServer': self.backup_server1,
            'upgradeServerCredentials': self.backup_server_creds1,
        }

    def set_vnf(self):
        # This is to set vnf info for existing VNF
        pass

    def restore_vnf(self):
        # This is to restore info of sig VNF
        self.sig_id = self.get_vnf_id()
        self.sigvnf.set_id(self.sig_id)
        self.sigvnf.set_vnflcm_apis()

    def get_vnf_id(self):
        token_bear = get_token()
        headers = {'Authorization': token_bear}
        verify = False
        response = requests.get(self.getvnfs, headers=headers, verify=verify)
        if response.status_code == 200:
            data = json.loads(response.text)
            for vnf in data:
                # Fow now, use vnfProductName to determine if this is sig plane vnf
                if vnf['vnfProductName'] == 'SBC':
                    print('get_vnfs: sig vnf id: ', vnf['id'])
                    return vnf['id']
        else:
            print('Failed to get_vnf_id')
            exit(1)

    def get_vnf_info(self):
        # For now, assume there is only one sig plane VNF
        pass

    def create_instantiate(self):
        self.sigvnf.create_vnf()
        self.sigvnf.instantiate_vnf()
        self.sigvnf.get_vnf()

    def terminate(self):
        self.sigvnf.terminate_vnf()

    def delete(self):
        self.sigvnf.delete_vnf()

    def change_package_version(self, vnfdId):
        self.sigvnf.upgrade_vnf(vnfdId)

    def get_vnfcInstanceId_List_4Heal(self):
        self.sigvnf.get_vnfcInstanceId_List()
        return self.sigvnf.vnfcInstanceId_List

    def heal(self, vnfcInstanceId=None, cause='Sig Plane VM Heal: OAM.NOKIA-LCP-VMA'):
        if vnfcInstanceId is None:
            vnfcInstanceId = ['OAM.NOKIA-LCP-VMA']
        self.sigvnf.heal_vnf(vnfcInstanceId, cause)

    def get_scale_status(self):
        self.sigvnf.get_scaleStatus()
        return self.sigvnf.scaleLevel, self.sigvnf.maxScaleLevel

    def scale(self, scaleType='SCALE_OUT', step=1, aspectId="sc_Aspect"):
        self.sigvnf.get_scaleStatus()
        scaleLevel = self.sigvnf.scaleLevel
        maxScaleLevel = self.sigvnf.maxScaleLevel
        if scaleType == 'SCALE_OUT':
            if scaleLevel == maxScaleLevel:
                print('Sig Plane maxScaleLevel has been reached, no action.')
                return
            elif scaleLevel < maxScaleLevel:
                self.sigvnf.scale_vnf(scaleType='SCALE_OUT')
        elif scaleType == 'SCALE_IN':
            if scaleLevel == 1:
                print('Sig Plane min SC number has been reached, no action.')
                return
            elif scaleLevel <= maxScaleLevel:
                self.sigvnf.scale_vnf(scaleType='SCALE_IN')

    def modify_auto_scale(self, periodInSeconds=600, enabled=False):
        self.sigvnf.modify_auto_scale_vnf(periodInSeconds, enabled)

    def modify_auto_backup(self, periodInSeconds=86220, enabled=False):
        self.sigvnf.modify_auto_backup_vnf(periodInSeconds, enabled)

    def custom_backup(self, additionalParam):
        self.sigvnf.backup_vnf(additionalParam)

    def custom_connect_SBC_Media_VNF(self, additionalParam):
        self.sigvnf.connect_sbc_media_vnf(additionalParam)

    def custom_disconnect_SBC_Media_VNF(self, additionalParam):
        self.sigvnf.disconnect_sbc_media_vnf(additionalParam)

    def custom_dbrestore(self, additionalParam):
        self.sigvnf.dbrestore_vnf(additionalParam)

    def custom_upgrade_precheck(self):
        self.sigvnf.upgrade_precheck()

    def custom_upgrade_1_apply(self, additionalParam):
        self.sigvnf.upgrade_1_apply(additionalParam)

    def custom_upgrade_2_activate(self):
        self.sigvnf.upgrade_2_activate()

    def custom_upgrade_3_commit(self):
        self.sigvnf.upgrade_3_commit()

    def custom_upgrade_archive(self, additionalParam):
        self.sigvnf.upgrade_archive(additionalParam)

    def cssu_create_instantiate(self):
        self.sigvnf.create_vnf()
        self.sigvnf.cssu_instantiate_vnf()
        self.sigvnf.get_vnf()

    def prep_backup_zip(self):
        # This has been implemented by prep_backup_cssu_archive_zip
        pass

    # After upgrade archive, the su_archive.zip file will be put at: /var/www/html/sbclcm-auto/
    # Rename it to cssu_archive.zip
    # ssh_command_passwd(cmd, ip, login, passwd):
    def prep_cssu_archive_zip_passwd(self):
        cmd = 'ls ' + self.backup_server_dir
        ip = self.backup_server_ip
        login = self.backup_server_login_passwd
        passwd = self.backup_server_passwd_passwd
        result = ssh_command_passwd(cmd, ip, login, passwd)
        if 'su_archive_R' in result:
            rlist = result.split()
            for r in rlist:
                if 'su_archive_R' in r:
                    cmd = 'mv ' + self.backup_server_dir + r + ' ' + self.backup_server_dir + 'cssu_archive.zip'
                    print(cmd)
                    ssh_command_passwd(cmd, ip, login, passwd)
                    cmd = 'chmod 777 ' + self.backup_server_dir + 'cssu_archive.zip'
                    print(cmd)
                    ssh_command_passwd(cmd, ip, login, passwd)

    def prep_cssu_archive_zip_pubkey(self):
        cmd = 'ls ' + self.backup_server_dir
        ip = self.backup_server_ip
        login = self.backup_server_login_pubkey
        privkey = self.local_private_key
        result = ssh_command_pubkey(cmd, ip, login, privkey)
        if 'su_archive_R' in result:
            rlist = result.split()
            for r in rlist:
                if 'su_archive_R' in r:
                    cmd = 'mv ' + self.backup_server_dir + r + ' ' + self.backup_server_dir + 'cssu_archive.zip'
                    print(cmd)
                    ssh_command_pubkey(cmd, ip, login, privkey)
                    cmd = 'chmod 777 ' + self.backup_server_dir + 'cssu_archive.zip'
                    print(cmd)
                    ssh_command_pubkey(cmd, ip, login, privkey)

    # Need to set the type to either 'passwd' or 'pubkey'
    # Then call ssh_command(cmd, ip, login, pass_key, type):
    def prep_cssu_archive_zip(self, type='passwd'):
        cmd = 'ls ' + self.backup_server_dir
        ip = self.backup_server_ip
        if type == 'passwd':
            login = self.backup_server_login_passwd
            passwd_key = self.backup_server_passwd_passwd
        elif type == 'pubkey':
            login = self.backup_server_login_pubkey
            passwd_key = self.local_private_key
        else:
            print('Only type passwd and pubkey supprted. Error out.')
            exit(1)
        result = ssh_command(cmd, ip, login, passwd_key, type)
        if 'su_archive_R' in result:
            rlist = result.split()
            for r in rlist:
                if 'su_archive_R' in r:
                    cmd = 'mv ' + self.backup_server_dir + r + ' ' + self.backup_server_dir + 'cssu_archive.zip'
                    print(cmd)
                    ssh_command(cmd, ip, login, passwd_key, type)
                    cmd = 'chmod 777 ' + self.backup_server_dir + 'cssu_archive.zip'
                    print(cmd)
                    ssh_command(cmd, ip, login, passwd_key, type)

    # This is combined version
    def prep_backup_cssu_zip(self, sshtype='passwd', ziptype='backup'):
        match_str = ''
        newzip = ''
        ip = self.backup_server_ip
        if ziptype == 'backup':
            match_str = '_LCP'
            newzip = self.backup_zip
        elif ziptype == 'cssu':
            match_str = 'su_archive_R'
            newzip = self.cssu_zip
        else:
            print('Only type backup and cssu supprted for ziptype. Error out.')
            exit(1)
        if sshtype == 'passwd':
            login = self.backup_server_login_passwd
            passwd_key = self.backup_server_passwd_passwd
        elif sshtype == 'pubkey':
            login = self.backup_server_login_pubkey
            passwd_key = self.local_private_key
        else:
            print('Only type passwd and pubkey supprted for sshtype. Error out.')
            exit(1)
        cmd = 'ls ' + self.backup_server_dir
        result = ssh_command(cmd, ip, login, passwd_key, sshtype)
        if match_str in result:
            rlist = result.split()
            for r in rlist:
                if match_str in r:
                    cmd = 'mv ' + self.backup_server_dir + r + ' ' + self.backup_server_dir + newzip
                    print(cmd)
                    ssh_command(cmd, ip, login, passwd_key, sshtype)
                    cmd = 'chmod 777 ' + self.backup_server_dir + newzip
                    print(cmd)
                    ssh_command(cmd, ip, login, passwd_key, sshtype)

    def check_latestOpState(self, timeout=30):
        status = self.sigvnf.get_latestOperationState()
        if status is not None:
            return status

    def wait_processing(self, timeout=30):
        print('wait_processing')
        wait = 0
        while wait < timeout:
            status = self.check_latestOpState()
            if status in ['PROCESSING', 'STARTING']:
                time.sleep(60)
                wait = wait + 1
            else:
                break

    def check_opstatus(self, operation='INSTANTIATE', operationName='', timeout=30):
        wait = 0
        while wait < timeout:
            status = self.sigvnf.get_operationState(operation, operationName)
            if status == 'PROCESSING':
                print('Sig Plane VNF ' + operation + ' ' + operationName + ' PROCESSING')
                print('Wait for 60 secs...')
            elif status == 'FAILED':
                print('Sig Plane VNF ' + operation + ' ' + operationName + ' FAILED')
                exit(1)
            elif status == 'ROLLED_BACK ':
                print('Sig Plane VNF ' + operation + ' ' + operationName + ' ROLLED_BACK')
                exit(2)
            elif status == 'COMPLETED':
                print('Sig Plane VNF ' + operation + ' ' + operationName + ' COMPLETED')
                return 0
            else:
                print('Sig Plane VNF ' + operation + ' ' + operationName + ' status: ' + status)
            # Check status every 60 secs
            time.sleep(60)
            wait = wait + 1

########################################################################################################################
# Sig VNF Package Operations
def sigvnf_UploadVnfpkg(swVersion):
    vnfpkgs = VnfPkgs()
    vnfpkgs.get_vnfpkgs()
    vnfpkgs.upload_vnfpkg(swVersion)
    vnfpkgs.get_vnfpkgs()
    vnfpkgs.dump_vnfpkgs()

def sigvnf_DeleteVnfpkg(swVersion):
    vnfpkgs = VnfPkgs()
    vnfpkgs.get_vnfpkgs()
    vnfpkgs.dump_vnfpkgs()
    vnfpkgs.delete_vnfpkg_by_swversion(swVersion)

########################################################################################################################
# This is the upper caller
# It use vnfdId to identify which vnf to operation on
# It's stateless by its best
class LcmTestDriver(object):
    def __init__(self, vnfdId):
        self.vnfdId = vnfdId

    def setup_sigDriver(self):
        self.sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId=self.vnfdId))
        self.sigDriver.restore_vnf()
        self.sigDriver.wait_processing()

    def setup_mediaDriver(self):
        self.mediaDriver = MediaVnfLcmTestDriver(MediaVnf(vnfdId=self.vnfdId))

    def sigvnf_CreateInstantiate(self):
        print('In Func:', sys._getframe().f_code.co_name)
        # For CreateInstantiate, cann't use setup_sigDriver as vnf is not created yet
        # use SigVnfLcmTestDriver directly
        self.sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId=self.vnfdId))
        self.sigDriver.create_instantiate()
        self.sigDriver.check_opstatus(operation='INSTANTIATE', operationName='', timeout=90)

    def sigvnf_Terminate(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.terminate()
        self.sigDriver.check_opstatus(operation='TERMINATE', operationName='', timeout=10)

    def sigvnf_Delete(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.delete()

    def sigvnf_Modify_DisableAutoScale(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.modify_auto_scale(enabled=False)
        self.sigDriver.check_opstatus(operation='MODIFY_INFO', operationName='', timeout=10)

    def sigvnf_Modify_EnableAutoScale(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.modify_auto_scale(enabled=True)
        self.sigDriver.check_opstatus(operation='MODIFY_INFO', operationName='', timeout=10)

    def sigvnf_Modify_DisableAutoBackup(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.modify_auto_backup(enabled=False)
        self.sigDriver.check_opstatus(operation='MODIFY_INFO', operationName='', timeout=10)

    def sigvnf_Modify_EnableAutoBackup(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.modify_auto_backup(enabled=True)
        self.sigDriver.check_opstatus(operation='MODIFY_INFO', operationName='', timeout=10)

    def sigvnf_ScaleOut(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.scale(scaleType='SCALE_OUT')
        self.sigDriver.check_opstatus(operation='SCALE', operationName='', timeout=60)

    def sigvnf_ScaleIn(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.scale(scaleType='SCALE_IN')
        self.sigDriver.check_opstatus(operation='SCALE', operationName='', timeout=60)

    def sigvnf_ScaleOutToMax(self):
        pass

    def sigvnf_ScaleInToInit(self):
        pass

    def sigvnf_Scale_OutIn(self):
        # First to scale out SC to max number: 5
        # then scale in SC to initial count: depends on initial deployment
        # The system initial count at: /storage/auto_scale/initial_sys_config.json
        # To-do: add func to parser the file and get initial SC count
        # For now, use 1 as initial count
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        initial_count = 1
        max_count = 5
        current_count, max_count = self.sigDriver.get_scale_status()
        print('current_count, max_count: ', current_count, ' ', max_count)
        while current_count < max_count:
            self.sigDriver.scale(scaleType='SCALE_OUT')
            self.sigDriver.check_opstatus(operation='SCALE', operationName='', timeout=60)
            current_count, max_count = self.sigDriver.get_scale_status()
        while current_count > initial_count:
            self.sigDriver.scale(scaleType='SCALE_IN')
            self.sigDriver.check_opstatus(operation='SCALE', operationName='', timeout=60)
            current_count, max_count = self.sigDriver.get_scale_status()

    def sigvnf_Heal_Single(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        vnfcInstanceId_List = self.sigDriver.get_vnfcInstanceId_List_4Heal()
        print('vnfcInstanceId_List: ', vnfcInstanceId_List)
        # Single VM heal, for all VMs, one VM each time
        for vnfcid in vnfcInstanceId_List:
            print('Start to Heal: ', vnfcid)
            self.sigDriver.heal(vnfcInstanceId=[vnfcid], cause='Sig Plane VM Heal: ' + vnfcid)
            self.sigDriver.check_opstatus(operation='HEAL', operationName='', timeout=60)

    def sigvnf_Heal_Multiple(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        vnfcInstanceId_List = self.sigDriver.get_vnfcInstanceId_List_4Heal()
        if not vnfcInstanceId_List:
            print('Failed to get vnfcInstanceId_List, Error out.')
            exit(1)
        print('vnfcInstanceId_List:', vnfcInstanceId_List)
        maxHealListLength = int(len(vnfcInstanceId_List) / 2)
        start = 2
        end = maxHealListLength + 1
        healList = []
        for healNum in range(start, end):
            while len(healList) < healNum:
                num = random.randint(0, len(vnfcInstanceId_List) - 1)
                duplicated = False
                vnfc = vnfcInstanceId_List[num]
                if vnfc not in healList:
                    for vnfc_tmp in healList:
                        if vnfc[0:10] == vnfc_tmp[0:10]:
                            # duplicated vnfc, not insert in healList
                            duplicated = True
                            break
                    if not duplicated:
                        healList.append(vnfc)
            print('Multiple Heal: healNum:', healNum, ';healList:', healList)
            print('Start to Heal: ', healList)
            self.sigDriver.heal(vnfcInstanceId=healList, cause='Sig Plane Multiple VM Heal: ' + str(healList))
            self.sigDriver.check_opstatus(operation='HEAL', operationName='', timeout=60)

    def sigvnf_Backup(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        for ap in [
            self.sigDriver.additinalParams_Backup_Local,
            # self.sigDriver.additinalParams_Backup_Remote_1,
            # self.sigDriver.additinalParams_Backup_Remote_2,
            # self.sigDriver.additinalParams_Backup_Remote_12,
            self.sigDriver.additinalParams_Backup_Remote_Creds_1,
            self.sigDriver.additinalParams_Backup_Remote_Creds_2,
            self.sigDriver.additinalParams_Backup_Remote_Creds_12
        ]:
            self.sigDriver.custom_backup(ap)
            self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:backup', timeout=20)
            self.sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='backup')

    def sigvnf_Backup_Local(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_backup(self.sigDriver.additinalParams_Backup_Local)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:backup', timeout=20)
        self.sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='backup')

    def sigvnf_Backup_Remote1(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_backup(self.sigDriver.additinalParams_Backup_Remote_1)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:backup', timeout=20)
        self.sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='backup')

    def sigvnf_Backup_Remote2(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_backup(self.sigDriver.additinalParams_Backup_Remote_2)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:backup', timeout=20)
        self.sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='backup')

    def sigvnf_Backup_Remote12(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_backup(self.sigDriver.additinalParams_Backup_Remote_12)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:backup', timeout=20)
        self.sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='backup')

    def sigvnf_Backup_Remote_Creds1(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_backup(self.sigDriver.additinalParams_Backup_Remote_Creds_1)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:backup', timeout=20)
        self.sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='backup')

    def sigvnf_Backup_Remote_Creds2(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_backup(self.sigDriver.additinalParams_Backup_Remote_Creds_2)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:backup', timeout=20)
        self.sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='backup')

    def sigvnf_Backup_Remote_Creds12(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_backup(self.sigDriver.additinalParams_Backup_Remote_Creds_12)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:backup', timeout=20)
        self.sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='backup')

    def sigvnf_ConnectSbcMediaVnf(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_connect_SBC_Media_VNF(self.sigDriver.additinalParams_Connection)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:connect_SBC_Media_VNF', timeout=20)

    def sigvnf_DisconnectSbcMediaVnf(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_disconnect_SBC_Media_VNF(self.sigDriver.additinalParams_Disconnection)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:disconnect_SBC_Media_VNF', timeout=20)

    # The pubkey needs to be setup before DB restore as this is the only way
    def sigvnf_DBRestore(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_dbrestore(self.sigDriver.additinalParams_DBRestore)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:DB_Restore', timeout=60)

    def sigvnf_DR(self):
        pass

    # For UpgradePrecheck, Upgrade1Apply, Upgrade2Activate, Upgrade3Commit,
    # assume the VNF package has been changed by ChangePackageVersion,
    # so use sig_vnfdId_SUToLoad as vnfdId
    # For ChangePackageVersion, need to pass in the vnfdId of the TO load
    def sigvnf_ChangePackageVersion(self, vnfdId_SU):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.change_package_version(vnfdId_SU)
        # Change Package version consists of: UPGRADE then MODIFY_INFO
        self.sigDriver.check_opstatus(operation='MODIFY_INFO', operationName='', timeout=10)
        time.sleep(60)

    def sigvnf_UpgradePrecheck(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_upgrade_precheck()
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_precheck', timeout=20)

    def sigvnf_Upgrade1Apply(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_upgrade_1_apply(self.sigDriver.additinalParams_Upgrade1Apply)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_1_apply', timeout=90)

    def sigvnf_Upgrade2Activate(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_upgrade_2_activate()
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_2_activate', timeout=30)

    def sigvnf_Upgrade3Commit(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_upgrade_3_commit()
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_3_commit', timeout=90)

    def sigvnf_UpgradeArchive(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        for ap in [self.sigDriver.additinalParams_UpgradeArchive,
                   self.sigDriver.additinalParams_UpgradeArchive_Creds
                   ]:
            self.sigDriver.custom_upgrade_archive(ap)
            self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_archive', timeout=20)
            self.sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='cssu')

    def sigvnf_UpgradeArchive_Pubkey(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_upgrade_archive(self.sigDriver.additinalParams_UpgradeArchive)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_archive', timeout=20)
        self.sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='cssu')

    def sigvnf_UpgradeArchive_Creds(self):
        print('In Func:', sys._getframe().f_code.co_name)
        self.setup_sigDriver()
        self.sigDriver.custom_upgrade_archive(self.sigDriver.additinalParams_UpgradeArchive_Creds)
        self.sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_archive', timeout=20)
        self.sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='cssu')

    def sigvnf_CSSUInstantiate(self):
        print('In Func:', sys._getframe().f_code.co_name)
        # For CreateInstantiate, cann't use setup_sigDriver as vnf is not created yet
        # use SigVnfLcmTestDriver directly
        self.sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId=self.vnfdId))
        self.sigDriver.cssu_create_instantiate()
        self.sigDriver.check_opstatus(operation='INSTANTIATE', operationName='', timeout=90)

    ##########################################
    # Following are test suites out of the box
    ##########################################
    def sigvnf_tests_alpha(self):
        self.sigvnf_CreateInstantiate()
        self.sigvnf_Modify_DisableAutoBackup()
        self.sigvnf_Modify_DisableAutoScale()
        self.sigvnf_ConnectSbcMediaVnf()
        self.sigvnf_DisconnectSbcMediaVnf()
        self.sigvnf_ConnectSbcMediaVnf()
        self.sigvnf_ScaleOut()
        self.sigvnf_ScaleIn()
        self.sigvnf_ScaleOut()
        self.sigvnf_Heal_Single()
        self.sigvnf_Backup()
        self.sigvnf_DBRestore()

    def sigvnf_tests_beta(self):
        self.sigvnf_CreateInstantiate()
        self.sigvnf_Modify_DisableAutoBackup()
        self.sigvnf_Modify_DisableAutoScale()
        self.sigvnf_ConnectSbcMediaVnf()
        self.sigvnf_DisconnectSbcMediaVnf()
        self.sigvnf_ConnectSbcMediaVnf()
        self.sigvnf_Scale_OutIn()
        self.sigvnf_ScaleOutToMax()
        self.sigvnf_Heal_Single()
        self.sigvnf_Heal_Multiple()
        self.sigvnf_Backup()
        self.sigvnf_DR()
        self.sigvnf_DBRestore()
        self.sigvnf_Terminate()
        self.sigvnf_Delete()

    def sigvnf_tests_gamma(self):
        self.sigvnf_ScaleOut()
        self.sigvnf_ScaleIn()

    def sigvnf_tests_cimcb(self):
        # self.sigvnf_CreateInstantiate()
        self.sigvnf_Modify_DisableAutoBackup()
        self.sigvnf_Modify_DisableAutoScale()
        self.sigvnf_ConnectSbcMediaVnf()
        self.sigvnf_Backup_Remote_Creds1()

    def sigvnf_tests_td(self):
        self.sigvnf_Terminate()
        self.sigvnf_Delete()

    def sigvnf_tests_cimcdb(self):
        self.sigvnf_Modify_DisableAutoBackup()
        self.sigvnf_Modify_DisableAutoScale()
        self.sigvnf_ConnectSbcMediaVnf()
        self.sigvnf_DisconnectSbcMediaVnf()
        self.sigvnf_ConnectSbcMediaVnf()
        self.sigvnf_Backup()

    def sigvnf_tests_bkup(self):
        self.sigvnf_Backup_Remote_Creds1()

    def sigvnf_tests_br(self):
        self.sigvnf_Backup_Remote_Creds1()
        # self.sigvnf_Backup_Remote_Creds12()
        self.sigvnf_DBRestore()

    def sigvnf_tests_heal(self):
        # self.sigvnf_Heal_Single()
        self.sigvnf_Heal_Multiple()

    def sigvnf_tests_scale(self):
        self.sigvnf_Scale_OutIn()
        self.sigvnf_ScaleOutToMax()
        self.sigvnf_ScaleInToInit()

    def sigvnf_tests_chgpkvern(self, vnfdId_SU):
        self.sigvnf_ChangePackageVersion(vnfdId_SU)

    def sigvnf_tests_su(self):
        self.sigvnf_UpgradePrecheck()
        self.sigvnf_Upgrade1Apply()
        self.sigvnf_Upgrade2Activate()
        self.sigvnf_Upgrade3Commit()

    def sigvnf_tests_ua(self):
        self.sigvnf_UpgradeArchive()

    def sigvnf_tests_ua_td(self):
        self.sigvnf_UpgradeArchive()
        self.sigvnf_Terminate()
        self.sigvnf_Delete()

    def sigvnf_tests_cssu(self):
        self.sigvnf_CSSUInstantiate()

########################################################################################################################
# Upper caller Test Suite
########################################################################################################################
def TS_sigvnf_tests_alpha():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_alpha()

def TS_sigvnf_tests_beta():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_beta()

def TS_sigvnf_tests_gamma():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_gamma()

def TS_sigvnf_tests_td():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_td()

def TS_sigvnf_tests_cimcb():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_cimcb()

def TS_sigvnf_tests_bkup():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_bkup()

def TS_sigvnf_tests_br():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_br()

def TS_sigvnf_tests_heal():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_heal()

def TS_sigvnf_tests_scale():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_scale()

def TS_sigvnf_tests_su():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_chgpkvern(sig_vnfdId_SU)
    lcmDriver = LcmTestDriver(sig_vnfdId_SU)
    lcmDriver.sigvnf_tests_su()

def TS_sigvnf_tests_cssu():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_ua_td()
    lcmDriver = LcmTestDriver(sig_vnfdId_SU)
    lcmDriver.sigvnf_tests_cssu()

# Create -> Instantiation -> Modify Auto Operations -> Connection2Media -> Backup
# -> UpgradeArchive -> Terminate -> Delete -> CSSU Instantiation
def TS_sigvnf_tests_cimcb_cssu():
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_cimcb()
    lcmDriver = LcmTestDriver(sig_vnfdId)
    lcmDriver.sigvnf_tests_ua_td()
    lcmDriver = LcmTestDriver(sig_vnfdId_SU)
    lcmDriver.sigvnf_tests_cssu()

########################################################################################################################
# Setup env variables
def setup_env():
    # Disable following warning:
    # D:\Program Files (x86)\Python37-32\lib\site-packages\urllib3\connectionpool.py:1004:
    # InsecureRequestWarning: Unverified HTTPS request is being made.
    # Adding certificate verification is strongly advised.
    # See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
    urllib3.disable_warnings()

# Here use software version and vnfdId to identify vnf
# To-do: use vnf name to identify vnf
def setup_vnfdIds():
    # First to find vnfdId for both signaling plane and media plane
    global sig_vnfdId
    global media_vnfdId
    global sig_vnfdId_SU
    global media_vnfdId_SU
    global sigVersion
    global sigVersion_SU
    global mediaVersion
    global mediaVersion_SU

    sig_vnfdId = ''
    media_vnfdId = ''
    sig_vnfdId_SU = ''
    media_vnfdId_SU = ''
    sigVersion = '37.28.06'
    sigVersion_SU = '37.28.06.0020'
    mediaVersion = 'an100052'
    mediaVersion_SU = 'an100053'

    vnfpkgs = VnfPkgs()
    vnfpkgs.get_vnfpkgs()
    vnfpkgs.dump_vnfpkgs()

    # Determine vnfdId via svnfSoftwareVersion
    # For sig plane, example of vnfSoftwareVersion:
    #'vnfSoftwareVersion': 'sbclcm01~37.28.06'
    # 'vnfSoftwareVersion': 'sbclcm01~37.28.06.0020'
    if vnfpkgs.vnfpkgs_list:
        for vp in vnfpkgs.vnfpkgs_list:
            if vp.vnfProductName == 'SBC':
                if vp.vnfSoftwareVersion.endswith(sigVersion):
                    # This is sig plane vnfp. Normal case for sig plane
                    sig_vnfdId = vp.vnfdId
                    print('Sig Plane vnfdId: ', sig_vnfdId)
                    print('Sig Plane vnfSoftwareVersion: ', vp.vnfSoftwareVersion)
                elif vp.vnfSoftwareVersion.endswith(sigVersion_SU):
                    # This is sig plane vnfp. SU case for sig plane
                    sig_vnfdId_SU = vp.vnfdId
                    print('Sig Plane vnfdId_SU: ', sig_vnfdId_SU)
                    print('Sig Plane vnfSoftwareVersion for SUTOLoad: ', vp.vnfSoftwareVersion)
            elif vp.vnfProductName == 'SBC-media':
                if vp.vnfSoftwareVersion.endswith(mediaVersion):
                    # This is media plane vnfp. Normal case for media plane
                    media_vnfdId = vp.vnfdId
                    print('Media Plane vnfdId: ', media_vnfdId)
                    print('Media Plane vnfSoftwareVersion: ', vp.vnfSoftwareVersion)
                elif vp.vnfSoftwareVersion.endswith(mediaVersion_SU):
                    # This is media plane vnfp. SU case for media plane
                    media_vnfdId_SU = vp.vnfdId
                    print('Media Plane vnfdId_SU: ', media_vnfdId_SU)
                    print('Media Plane vnfSoftwareVersion for SUTOLoad: ', vp.vnfSoftwareVersion)
            else:
                print('Currently supported vnfProductName is SBC or SBC-media.')
                exit(1)

########################################################################################################################
# Main
# To-do list:
# - request timeout and maxretries
# - form instantiate.json with additionalParams, vim passwd
# - setup ssh key for backup use
# - DR
########################################################################################################################
if __name__ == '__main__':

    setup_env()

    setup_vnfdIds()

    # TS_sigvnf_tests_cimcb_cssu()

    # TS_sigvnf_tests_cimcb()
    # TS_sigvnf_tests_br()
    # TS_sigvnf_tests_su()

    # TS_sigvnf_tests_gamma()

    TS_sigvnf_tests_heal()













