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
# CBAM url and CBAM client
cbam_url = 'https://10.75.44.14'
url = 'https://10.75.44.14'
client_id = 'cbam_rest'
client_secret = '5b895f51-fbec-46b9-bf98-8bd5ab6c859d'
gui_client_id = 'lcm'
gui_client_passwd = '-Assured1111'

working_dir = 'D:\\Programs\\JetBrains\\PycharmProjects\\py37projects\\lcm_auto_cbam_restful\\'
sig_data_dir = working_dir + 'data\\sig-plane\\'

vnflcm_base_path = '/vnflcm/v1'
vnfpkgm_base_path = '/vnfpkgm/v1'

########################################################################################################################
def print_response(response):
    print('response: ', response)
    print('response.headers: ', response.headers)
    print('response.text: ', response.text)

def dump_response_data(response, funcname):
    print('Now is at function:', funcname)
    data = json.loads(response.text)
    print(data)
    print('\n')

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
    url_vnf = url + '/vnflcm/v1' + '/vnf_instances'
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
        if version == sigVersion_BaseLoad:
            vnfpkg = self.vnfpkg_baseload
        elif version == sigVersion_SUToLoad:
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
    def __init__(self, vnfdId, name='sbclcm-sig-plane', description = 'SBC LCM signaling plane VNF for Auto Test via CBAM REST API'):
        self.name = name
        self.description = description
        self.vnfdId = vnfdId
        self.id = ''
        self.opStatus = ''
        self.operationState = ''
        self.scaleLevel = 1
        self.maxScaleLevel = 5
        self.vnfcInstanceId_List = []
        self.instantiate_file = 'D:\\Programs\\JetBrains\\PycharmProjects\\py37projects\\lcm_auto_cbam_restful\\data\\sig-plane\\LCM_instantiate_params.json'
        self.cssu_instantiate_file = 'D:\\Programs\\JetBrains\\PycharmProjects\\py37projects\\lcm_auto_cbam_restful\\data\\sig-plane\\cssu_LCM_instantiate_params.json'
        self.vnflcm_create              = cbam_url + '/vnflcm/v1' + '/vnf_instances'
        self.vnflcm_instantiate         = ''
        self.vnflcm_terminate           = ''
        self.vnflcm_delete              = ''
        self.vnflcm_upgrade             = ''
        self.vnflcm_get                 = ''
        self.vnflcm_modify              = ''
        self.vnflcm_scale               = ''
        self.vnflcm_heal                = ''
        self.vnflcm_custom_backup       = ''
        self.vnflcm_custom_connect      = ''
        self.vnflcm_custom_disconnect   = ''
        self.vnflcm_custom_dbrestore    = ''
        self.vnflcm_custom_upgrade_precheck     = ''
        self.vnflcm_custom_upgrade_1_apply      = ''
        self.vnflcm_custom_upgrade_2_activate   = ''
        self.vnflcm_custom_upgrade_3_commit     = ''
        self.vnflcm_custom_upgrade_archive      = ''

    def set_vnflcm_apis(self):
        self.operationState             = cbam_url + '/vnflcm/v1' + '/vnf_lcm_op_occs'
        self.vnflcm_create              = cbam_url + '/vnflcm/v1' + '/vnf_instances'
        self.vnflcm_instantiate         = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/instantiate'
        self.vnflcm_terminate           = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/terminate'
        self.vnflcm_delete              = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id
        self.vnflcm_get                 = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id
        self.vnflcm_modify              = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id
        self.vnflcm_scale               = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/scale'
        self.vnflcm_heal                = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/heal'
        self.vnflcm_upgrade             = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/upgrade'
        self.vnflcm_custom_backup       = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/custom/backup'
        self.vnflcm_custom_connect      = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/custom/connect_SBC_Media_VNF'
        self.vnflcm_custom_disconnect   = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/custom/disconnect_SBC_Media_VNF'
        self.vnflcm_custom_dbrestore    = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/custom/DB_Restore'
        self.vnflcm_custom_upgrade_precheck     = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/custom/upgrade_precheck'
        self.vnflcm_custom_upgrade_1_apply      = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/custom/upgrade_1_apply'
        self.vnflcm_custom_upgrade_2_activate   = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/custom/upgrade_2_activate'
        self.vnflcm_custom_upgrade_3_commit     = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/custom/upgrade_3_commit'
        self.vnflcm_custom_upgrade_archive      = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/custom/upgrade_archive'

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
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
        verify = False
        response = requests.post(
            self.vnflcm_create,
            headers=headers,
            json={
                "vnfdId": self.vnfdId,
                "vnfInstanceName": self.name,
                "vnfInstanceDescription": self.description
            },
            verify=verify)
        # data = json.loads(response.text)
        dump_response_data(response, 'create_vnf')
        # get vnf ID
        data = json.loads(response.text)
        self.id = data['id']
        print(self.get_id())
        # Now it's time to set rest api interfaces
        # since we have got id
        self.set_vnflcm_apis()

    #MODIFY use PATCH
    def modify_auto_backup_vnf(self, periodInSeconds=86220, enabled=False):
        token_bear = get_token()
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
        verify = False
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
            verify=verify)
        if response.status_code == 202:
            print('Modify auto_backup successful: ' + 'periodInSeconds:' + str(periodInSeconds) + ';enabled:' + str(enabled))
        else:
            print('Modify auto_backup failed. exit.')
            exit(1)

    def modify_auto_scale_vnf(self, periodInSeconds=600, enabled=False):
        token_bear = get_token()
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
        verify = False
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
            verify=verify)
        if response.status_code == 202:
            print('Modify auto_scale successful: ' + 'periodInSeconds:' + str(periodInSeconds) + ';enabled:' + str(enabled))
        else:
            print('Modigy auto_scale failed. exit.')
            exit(1)

    def instantiate_vnf(self):
        token_bear = get_token()
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
        verify = False
        parameters = json.load(open(self.instantiate_file, "rb"))
        response = requests.post(self.vnflcm_instantiate, headers=headers, json=parameters, verify=verify)

    def cssu_instantiate_vnf(self):
        token_bear = get_token()
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
        verify = False
        parameters = json.load(open(self.cssu_instantiate_file, "rb"))
        response = requests.post(self.vnflcm_instantiate, headers=headers, json=parameters, verify=verify)

    def terminate_vnf(self):
        token_bear = get_token()
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
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
        headers = {'Authorization': token_bear}
        verify = False
        response = requests.delete(self.vnflcm_delete, headers=headers, verify=verify)

    def upgrade_vnf(self, vnfdId):
        token_bear = get_token()
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
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
        headers = {'Authorization': token_bear}
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
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
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
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
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
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
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
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
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
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
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
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
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
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
        verify = False
        # Need to carry empty data in requests.post, otherwise will fail
        response = requests.post(self.vnflcm_custom_upgrade_precheck, json={}, headers=headers, verify=verify)
        if response.status_code != 202:
            print('Sig Plane Upgrade Precheck Failed.')
            exit(1)

    def upgrade_1_apply(self, additionalParam):
        token_bear = get_token()
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
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
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
        verify = False
        # Need to carry empty data in requests.post, otherwise will fail
        response = requests.post(self.vnflcm_custom_upgrade_2_activate, json={}, headers=headers, verify=verify)
        if response.status_code != 202:
            print('Sig Plane Upgrade 2 Activate Failed.')
            exit(1)

    def upgrade_3_commit(self):
        token_bear = get_token()
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
        verify = False
        # Need to carry empty data in requests.post, otherwise will fail
        response = requests.post(self.vnflcm_custom_upgrade_3_commit, json={}, headers=headers, verify=verify)
        if response.status_code != 202:
            print('Sig Plane Upgrade 3 Commit Failed.')
            exit(1)

    def upgrade_archive(self, additionalParam):
        token_bear = get_token()
        headers = {'Authorization': token_bear, "Content-Type": "application/json"}
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
        headers = {'Authorization': token_bear}
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
        headers = {'Authorization': token_bear}
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
    pass

########################################################################################################################
# Data
operationState_list = ['STARTING', 'FAILED', 'ROLLED_BACK', 'PROCESSING', 'COMPLETED']
operation_list = ['MODIFY_INFO', 'INSTANTIATE', 'TERMINATE', 'SCALE', 'OTHER']
operationName_list = ['custom:backup']
backup_server_creds = '-----BEGIN RSA PRIVATE KEY-----\nMIIEowIBAAKCAQEAvX/4YeeQcBqR2sjW18T8WbiAVdnVIs4ZNNlTEG+Ps6OFeQFm\nUBwXvtqbetitEhAAU2OT4ivuh+B20KM/WHM6r57URA1qgNK8Sk9tLUiZRvMDkDR8\nWpAEQSw0fvkO91J93q9Siu3h2uhiKtB1ARESb5DcayttXg0fr9U5hmT/mD5MJ/nC\npfE5ByuHzmWSJo9Vya+YM0UBZnja38vhfc8mAeJ0pxQVxkoL4KzYF2JJAqIzH9tw\nkJLfZbNlxQtOKRCSRWtdcCHckfS0/BISf9f0jdG9h15q3vvKc0j+dXCJny5jfgCc\nHl2+e4RYK3evvJPWQNSZ/+iMZqn1SyligpbKXQIDAQABAoIBABtfsAach73Z6LXd\nC0Px/a4MO+Wq6OH1Oajrt9cI9o4xkedP73KlDD0SoSEWybFxRErHeKZUSEmygBdV\nbaIeSxzxaaJG+dqQFoj5fkDrWtDn69zZ6BjA8wxjEVZCLgpGDU6srtTI1jZkGUIs\nCKrVx378QwrsJAlRBgHFYGDsmAtqvLetbMm272K/hz2e4jxMf08LcDx1fUgDO+hD\naMjzVmbIYNbFftLQD/yG+DgtvP7f728yoG8gNXC0shPqetHtfnwCbJ3H1ju9svGW\nDFYzrBwZZZMY0nTAWjY/DXSS1ORrq7LXSIPKf/3kobfMU67ugeC6NrEsncdIKvIE\n/yVKTrUCgYEA4iMKFeRdIWjzijg3Iie6k09vduTH+nsELDKjzHqcyPmEBisidFQA\nFMjJO8+jh+KKusqYEDp1l4qHLbtN1hatKZV6PwfcmPITA+uczZa9Z3YAKsI1GAOi\n0GUmjmoElOGc1I+k55fWAt48hWRoPd4vrlGaAw8otIdiSXHdpwdb3rsCgYEA1oZa\nH7R4j757Ny47NHIPsXsfZwyD2TTU+oOIDOPvBWN6GuU70N5ZW21529mwLKbr5e2H\n9ofMhSJQkXlg6e6F5wmj7Q0n+mGNoPeNoq7bRB1gHelODs4vAnnVNz2vCGt0uqSd\n+UoemidWKm8RFNAG8yS9uoQrk7sZpA5MYHrJBccCgYBELqxrzV8HI83Kbwiwk6n9\noIXLI0/ohg7MBLi+fnmnXxQfiAHrcShVG/UQw5pa7kNF7q/KtNWfy3TWpRLi6hNr\n5lXli0lIFDUHiZLNqhWRjFKgkc3QX8hHbTgi2HRpL11J+cWOzokIdFlrHssPXF6k\nAJafNYLga7GG034xTla04QKBgAK5Meu1HtK0WFwa+iVwTUKzjXKBdisLwKhtgwym\n2CH5YVN2FYxRRlEi0qk32kS22cfRfChlEPOfu+Yc5F4T6R9FwA8CW7+R/XpNqj6m\neaIjvVSj4ZnOhEpDwbEx10cEFjdIX7kKd9j9JtrjDhR1j6EGlmIHy4XUmj66771J\n0cOBAoGBAJyXMkKKbsSGDGYoyzazVjLYzIqmC2tOnYkHHl3heEZN/LkphPuLdbcj\n2pk2wlqskZ2LQxnylJDgIIA6rJBoLvBj5Xo+9EN7uidHHv+8JGBy4FPcDNl2O5RR\nLbiaAVSQNQNm+hku9e0XH0+YFrCP+0Q8D9DGYzhupslAzJEyoz3R\n-----END RSA PRIVATE KEY-----'

# Signaling plane VNF LCM Tests
# Need to support resume
class SigVnfLcmTestDriver(object):
    def __init__(self, sigvnf):
        # Need to determine which is sig plane vnf
        # Need to get all vnfs and decide
        self.getvnfs = cbam_url + '/vnflcm/v1' + '/vnf_instances/'
        self.opstatus = 0
        self.status_file = working_dir + '.sig_status'
        self.sigvnf = sigvnf
        self.sig_id = ''
        # centos is for pubkey login
        self.backup_server_login_pubkey = 'centos'
        self.local_private_key = 'C:\\Users\\shawnx\\.ssh\\id_rsa'
        # root is for passwd login
        self.backup_server_login_passwd = 'root'
        self.backup_server_passwd_passwd = 'newsys'
        self.backup_server_ip = '10.75.44.7'
        self.backup_server_dir = '/var/www/html/sbclcm-auto/'
        self.cssu_zip = 'cssu_archive.zip'
        self.backup_zip = 'backup.zip'
        # Following are additionalParams for various operations
        self.additinalParams_Backup_Local = {
            'backupServer1': '',
            'backup_server_credentials1': '',
            'backupServer2': '',
            'backup_server_credentials2': ''
        }
        self.additinalParams_Backup_Remote_1 = {
            'backupServer1': 'centos@10.75.44.7:/var/www/html/sbclcm-auto/',
            'backup_server_credentials1': '',
            'backupServer2': '',
            'backup_server_credentials2': ''
        }
        self.additinalParams_Backup_Remote_2 = {
            'backupServer1': '',
            'backup_server_credentials1': '',
            'backupServer2': 'centos@10.75.44.7:/var/www/html/sbclcm-auto/',
            'backup_server_credentials2': ''
        }
        self.additinalParams_Backup_Remote_12 = {
            'backupServer1': 'centos@10.75.44.7:/var/www/html/sbclcm-auto/',
            'backup_server_credentials1': '',
            'backupServer2': 'centos@10.75.44.7:/var/www/html/sbclcm-auto/',
            'backup_server_credentials2': ''
        }
        self.additinalParams_Backup_Remote_Creds_1 = {
            'backupServer1': 'centos@10.75.44.7:/var/www/html/sbclcm-auto/',
            'backup_server_credentials1': backup_server_creds,
            'backupServer2': '',
            'backup_server_credentials2': ''
        }
        self.additinalParams_Backup_Remote_Creds_2 = {
            'backupServer1': '',
            'backup_server_credentials1': '',
            'backupServer2': 'centos@10.75.44.7:/var/www/html/sbclcm-auto/',
            'backup_server_credentials2': backup_server_creds
        }
        self.additinalParams_Backup_Remote_Creds_12 = {
            'backupServer1': 'centos@10.75.44.7:/var/www/html/sbclcm-auto/',
            'backup_server_credentials1': backup_server_creds,
            'backupServer2': 'centos@10.75.44.7:/var/www/html/sbclcm-auto/',
            'backup_server_credentials2': backup_server_creds
        }
        self.additinalParams_Connection = {
            'FixedScmIpAddress': '10.75.44.10,10.75.44.11',
            'LcmUser': 'cloud-user',
            'ApplUser': 'diag',
            'ApplUserPw': '-assured'
        }
        self.additinalParams_Disconnection = {
            'FixedScmIpAddress': '10.75.44.10,10.75.44.11',
            'LcmUser': 'cloud-user'
        }
        self.additinalParams_DBRestore = {
            'backupInfo': 'centos@10.75.44.7:/var/www/html/sbclcm-auto/backup.zip',
            'restore_media_plane': 'ALL'
        }
        self.additinalParams_Upgrade1Apply = {
            'upgradeImageName': 'nokia-SBC_sig-RHEL7-R37.28.06.0020.x86_64.qcow2',
            'upgradeVersion': 'R37.28.06.0020',
            'upgradeDeftKey': '13582',
            'upgradeDeftUrl': 'http://10.75.44.7/deft_R37.28.XX_R37.28.XX.zip'
        }
        self.additinalParams_UpgradeArchive = {
            'upgradeDeftKey': '13582',
            'upgradeDeftUrl': 'http://10.75.44.7/deft_R37.28.XX_R37.28.XX.zip',
            'upgradeVersion': 'R37.28.06.0020',
            'upgradeServer': 'centos@10.75.44.7:/var/www/html/sbclcm-auto/',
            'upgradeServerCredentials': '',
        }
        self.additinalParams_UpgradeArchive_Creds = {
            'upgradeDeftKey': '13582',
            'upgradeDeftUrl': 'http://10.75.44.7/deft_R37.28.XX_R37.28.XX.zip',
            'upgradeVersion': 'R37.28.06.0020',
            'upgradeServer': 'centos@10.75.44.7:/var/www/html/sbclcm-auto/',
            'upgradeServerCredentials': backup_server_creds,
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

# Sig VNF Operations
def sigvnf_CreateInstantiate(sig_vnfdId):
    print('sigvnf_CreateInstantiate')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.create_instantiate()
    sigDriver.check_opstatus(operation='INSTANTIATE', operationName='', timeout=90)

def sigvnf_Terminate(sig_vnfdId):
    print('sigvnf_Terminate')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.terminate()
    sigDriver.check_opstatus(operation='TERMINATE', operationName='', timeout=10)

def sigvnf_Delete(sig_vnfdId):
    print('sigvnf_Delete')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.delete()
    # No able to to check status as the VNF has already been deleted.
    # sigDriver.check_opstatus(operation='DELETE', operationName='', timeout=10)

def sigvnf_Modify_DisableAutoScale(sig_vnfdId):
    print('sigvnf_Modify_DisableAutoScale')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.wait_processing()
    sigDriver.modify_auto_scale(enabled=False)
    sigDriver.check_opstatus(operation='MODIFY_INFO', operationName='', timeout=10)

def sigvnf_Modify_EnableAutoScale(sig_vnfdId):
    print('sigvnf_Modify_EnableAutoScale')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.modify_auto_scale(enabled=True)
    sigDriver.check_opstatus(operation='MODIFY_INFO', operationName='', timeout=10)

def sigvnf_Modify_DisableAutoBackup(sig_vnfdId):
    print('sigvnf_Modify_DisableAutoBackup')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.wait_processing()
    sigDriver.modify_auto_backup(enabled=False)
    sigDriver.check_opstatus(operation='MODIFY_INFO', operationName='', timeout=10)

def sigvnf_Modify_EnableAutoBackup(sig_vnfdId):
    print('sigvnf_Modify_EnableAutoBackup')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.modify_auto_backup(enabled=True)
    sigDriver.check_opstatus(operation='MODIFY_INFO', operationName='', timeout=10)

def sigvnf_ScaleOut(sig_vnfdId):
    print('Start sigvnf_ScaleOut')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.wait_processing()
    sigDriver.scale(scaleType='SCALE_OUT')
    sigDriver.check_opstatus(operation='SCALE', operationName='', timeout=60)

def sigvnf_ScaleIn(sig_vnfdId):
    print('Start sigvnf_ScaleIn')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.scale(scaleType='SCALE_IN')
    sigDriver.check_opstatus(operation='SCALE', operationName='', timeout=60)

def sigvnf_ScaleOutToMax(sig_vnfdId):
    pass

def sigvnf_ScaleInToInit(sig_vnfdId):
    pass

def sigvnf_Scale_OutIn(sig_vnfdId):
    print('Start sigvnf_Scale_OutIn')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.wait_processing()
    # First to scale out SC to max number: 5
    # then scale in SC to initial count: depends on initial deployment
    # Here need to get the initial SC count by some way
    # The system initial count at: /storage/auto_scale/initial_sys_config.json
    # Need to add func to parser the file and get initial SC count
    # For now, use 1 as initial count
    initial_count = 1
    max_count = 5
    current_count, max_count = sigDriver.get_scale_status()
    print('current_count, max_count: ', current_count, ' ', max_count)
    while current_count < max_count:
        sigDriver.scale(scaleType='SCALE_OUT')
        sigDriver.check_opstatus(operation='SCALE', operationName='', timeout=60)
        current_count, max_count = sigDriver.get_scale_status()
    while current_count > initial_count:
        sigDriver.scale(scaleType='SCALE_IN')
        sigDriver.check_opstatus(operation='SCALE', operationName='', timeout=60)
        current_count, max_count = sigDriver.get_scale_status()

def sigvnf_Heal_Single(sig_vnfdId):
    print('Start sigvnf_Heal_Single')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.wait_processing()
    vnfcInstanceId_List = sigDriver.get_vnfcInstanceId_List_4Heal()
    print('vnfcInstanceId_List in sigvnf_Heal_Single(): ', vnfcInstanceId_List)
    # Single VM heal, for all VMs, one VM each time
    for vnfcid in vnfcInstanceId_List:
        print('Start to Heal: ', vnfcid)
        sigDriver.heal(vnfcInstanceId=[vnfcid], cause='Sig Plane VM Heal: '+vnfcid)
        sigDriver.check_opstatus(operation='HEAL', operationName='', timeout=60)

def sigvnf_Heal_Multiple(sig_vnfdId):
    print('Start sigvnf_Heal_Multiple')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.wait_processing()
    vnfcInstanceId_List = sigDriver.get_vnfcInstanceId_List_4Heal()
    if not vnfcInstanceId_List:
        print('Failed to get vnfcInstanceId_List, Error out.')
        exit(1)
    print('vnfcInstanceId_List:', vnfcInstanceId_List)
    # Multiple VMs heal, A and B VM can't be healed at the same time,
    # so split them into 2 lists
    # vmaList = []
    # vmbList = []
    # for vnfc in vnfcInstanceId_List:
    #     if vnfc.endswith('VMA'):
    #         vmaList.append(vnfc)
    #     if vnfc.endswith('VMB'):
    #         vmbList.append(vnfc)
    # print('vmaList: ', vmaList)
    # print('vmbList: ', vmbList)
    # Here, form multiple VM list. range(2, maxHealListLength+1)
    maxHealListLength = int(len(vnfcInstanceId_List) / 2)
    start = 2
    end   = maxHealListLength + 1
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
        sigDriver.heal(vnfcInstanceId=healList, cause='Sig Plane Multiple VM Heal: ' + str(healList))
        sigDriver.check_opstatus(operation='HEAL', operationName='', timeout=60)

def sigvnf_Backup(sig_vnfdId):
    print('Start sigvnf_Backup')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.wait_processing()
    for ap in [
                # sigDriver.additinalParams_Backup_Local,
                # sigDriver.additinalParams_Backup_Remote_1,
                # sigDriver.additinalParams_Backup_Remote_2,
                # sigDriver.additinalParams_Backup_Remote_12,
                sigDriver.additinalParams_Backup_Remote_Creds_1,
                sigDriver.additinalParams_Backup_Remote_Creds_2,
                sigDriver.additinalParams_Backup_Remote_Creds_12
                ]:
        sigDriver.custom_backup(ap)
        sigDriver.check_opstatus(operation='OTHER', operationName='custom:backup', timeout=20)
        sigDriver.prep_backup_cssu_zip(sshtype='passwd', ziptype='backup')

def sigvnf_ConnectSbcMediaVnf(sig_vnfdId):
    print('Start sigvnf_ConnectSbcMediaVnf')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.custom_connect_SBC_Media_VNF(sigDriver.additinalParams_Connection)
    sigDriver.check_opstatus(operation='OTHER', operationName='custom:connect_SBC_Media_VNF', timeout=20)

def sigvnf_DisconnectSbcMediaVnf(sig_vnfdId):
    print('Start sigvnf_DisconnectSbcMediaVnf')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.custom_disconnect_SBC_Media_VNF(sigDriver.additinalParams_Disconnection)
    sigDriver.check_opstatus(operation='OTHER', operationName='custom:disconnect_SBC_Media_VNF', timeout=20)

def sigvnf_DBRestore(sig_vnfdId):
    print('Start sigvnf_DBRestore')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.custom_dbrestore(sigDriver.additinalParams_DBRestore)
    sigDriver.check_opstatus(operation='OTHER', operationName='custom:DB_Restore', timeout=60)

# For UpgradePrecheck, Upgrade1Apply, Upgrade2Activate, Upgrade3Commit,
# assume the VNF package has been changed by ChangePackageVersion,
# so use sig_vnfdId_SUToLoad as vnfdId
def sigvnf_ChangePackageVersion(sig_vnfdId, sig_vnfdId_SUToLoad):
    # This is by default to change package version to SU TO load
    print('sigvnf_ChangePackageVersion')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.change_package_version(sig_vnfdId_SUToLoad)
    # Change Package version consists of: UPGRADE then MODIFY_INFO
    sigDriver.check_opstatus(operation='MODIFY_INFO', operationName='', timeout=10)
    time.sleep(60)

def sigvnf_UpgradePrecheck(sig_vnfdId):
    print('Start sigvnf_UpgradePrecheck')
    # Here need to pass in sig_vnfdId_SUToLoad
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.custom_upgrade_precheck()
    sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_precheck', timeout=20)

def sigvnf_Upgrade1Apply(sig_vnfdId):
    print('Start sigvnf_Upgrade1Apply')
    # Here need to pass in sig_vnfdId_SUToLoad
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.custom_upgrade_1_apply(sigDriver.additinalParams_Upgrade1Apply)
    sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_1_apply', timeout=90)

def sigvnf_Upgrade2Activate(sig_vnfdId):
    print('Start sigvnf_Upgrade2Activate')
    # Here need to pass in sig_vnfdId_SUToLoad
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.custom_upgrade_2_activate()
    sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_2_activate', timeout=30)

def sigvnf_Upgrade3Commit(sig_vnfdId):
    print('Start sigvnf_Upgrade3Commit')
    # Here need to pass in sig_vnfdId_SUToLoad
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    sigDriver.custom_upgrade_3_commit()
    sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_3_commit', timeout=90)

def sigvnf_UpgradeArchive(sig_vnfdId):
    print('Start sigvnf_UpgradeArchive')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    for ap in [ sigDriver.additinalParams_UpgradeArchive,
                sigDriver.additinalParams_UpgradeArchive_Creds
                ]:
        sigDriver.custom_upgrade_archive(ap)
        sigDriver.check_opstatus(operation='OTHER', operationName='custom:upgrade_archive', timeout=20)
        # After each upgrade archive, cp the archive.zip to cssu_archive.zip

def sigvnf_PrepCSSUArchiveZip(sig_vnfdId):
    print('sigvnf_PrepSUArchiveZip')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.restore_vnf()
    # sigDriver.prep_cssu_archive_zip_passwd()
    # sigDriver.prep_cssu_archive_zip_pubkey()
    # sigDriver.prep_cssu_archive_zip(type='passwd')
    # sigDriver.prep_cssu_archive_zip(type='pubkey')
    # sigDriver.prep_backup_cssu_archive_zip(sshtype='passwd', ziptype='cssu')
    # sigDriver.prep_backup_cssu_archive_zip(sshtype='pubkey', ziptype='cssu')
    # sigDriver.prep_backup_cssu_archive_zip(sshtype='passwd', ziptype='backup')
    # sigDriver.prep_backup_cssu_archive_zip(sshtype='pubkey', ziptype='backup')
    # prep_backup_cssu_zip(sshtype='passwd', ziptype='backup')

def sigvnf_CSSUInstantiate(sig_vnfdId):
    print('sigvnf_CSSUInstantiate')
    sigDriver = SigVnfLcmTestDriver(SigVnf(vnfdId = sig_vnfdId))
    sigDriver.cssu_create_instantiate()
    sigDriver.check_opstatus(operation='INSTANTIATE', operationName='', timeout=90)

########################################################################################################################
# Setup env
def setup_vnfdIds():
    # First to find vnfdId for both signaling plane and media plane
    # Need to find a way to determine sig and media vnfdId
    # BL: BaseLoad
    # TL: SUToLoad
    global sig_vnfdId_BaseLoad
    global media_vnfdId_BaseLoad
    global sig_vnfdId_SUToLoad
    global media_vnfdId_SUToLoad
    global sigVersion_BaseLoad
    global sigVersion_SUToLoad
    global mediaVersion_BaseLoad
    global mediaVersion_SUToLoad
    sig_vnfdId_BaseLoad = ''
    media_vnfdId_BaseLoad = ''
    sig_vnfdId_SUToLoad = ''
    media_vnfdId_SUToLoad = ''

    vnfpkgs = VnfPkgs()
    vnfpkgs.get_vnfpkgs()
    vnfpkgs.dump_vnfpkgs()

    sigVersion_BaseLoad = '37.28.06'
    sigVersion_SUToLoad = '37.28.06.0020'
    mediaVersion_BaseLoad = 'an100047'
    mediaVersion_SUToLoad = 'an100052'

    # For sig plane, example of vnfSoftwareVersion:
    #'vnfSoftwareVersion': 'sbclcm01~37.28.06'
    # 'vnfSoftwareVersion': 'sbclcm01~37.28.06.0020'
    if vnfpkgs.vnfpkgs_list:
        for vp in vnfpkgs.vnfpkgs_list:
            if vp.vnfProductName == 'SBC' and vp.vnfSoftwareVersion.endswith(sigVersion_BaseLoad):
                # This is sig plane vnfp
                # Normal case for sig plane
                sig_vnfdId_BaseLoad = vp.vnfdId
                print('Sig Plane vnfdId: ', sig_vnfdId_BaseLoad)
                print('Sig Plane vnfSoftwareVersion: ', vp.vnfSoftwareVersion)
            elif vp.vnfProductName == 'SBC' and vp.vnfSoftwareVersion.endswith(sigVersion_SUToLoad):
                # This is sig plane vnfp
                # SU case for sig plane
                sig_vnfdId_SUToLoad = vp.vnfdId
                print('Sig Plane vnfdId_SUTOLoad: ', sig_vnfdId_SUToLoad)
                print('Sig Plane vnfSoftwareVersion for SUTOLoad: ', vp.vnfSoftwareVersion)
            if vp.vnfProductName == 'SBC-media':
                # This is media plane vnfp
                media_vnfdId_BaseLoad = vp.vnfdId
                print('Media Plane vnfdId: ', media_vnfdId_BaseLoad)

########################################################################################################################
# Following actions for alpha:
# - Upload VNF Package                  - done
# - Create, Instantiate                 - done
# - Disable auto_backup, auto_scale     - done
# - Connection                          - done
# - Disconnection                       - done
# - backup                              - done
# - DB restore                          - done
# - Single VM Heal                      - done
# - Multple VM Heal                     - done
# - Scale                               - done
# - Scale Out and In                    - done
# - Terminate                           - done
# - Delete                              - done
# Following actions for beta:
# - Change Package Version              - done
# - SU                                  - done
# - Upgrade archive                     - done
# - CSSU                                - done
def sigvnf_tests_alpha():
    sigvnf_CreateInstantiate(sig_vnfdId_BaseLoad)
    sigvnf_Modify_DisableAutoScale(sig_vnfdId_BaseLoad)
    sigvnf_Modify_DisableAutoBackup(sig_vnfdId_BaseLoad)
    sigvnf_ConnectSbcMediaVnf(sig_vnfdId_BaseLoad)
    sigvnf_DisconnectSbcMediaVnf(sig_vnfdId_BaseLoad)
    sigvnf_ConnectSbcMediaVnf(sig_vnfdId_BaseLoad)
    sigvnf_Backup(sig_vnfdId_BaseLoad)
    sigvnf_ScaleOut(sig_vnfdId_BaseLoad)
    sigvnf_ScaleIn(sig_vnfdId_BaseLoad)
    sigvnf_ScaleOut(sig_vnfdId_BaseLoad)
    # sigvnf_Heal_Single(sig_vnfdId_BaseLoad)
    sigvnf_Backup(sig_vnfdId_BaseLoad)
    sigvnf_DBRestore(sig_vnfdId_BaseLoad)
    sigvnf_Terminate(sig_vnfdId_BaseLoad)

def sigvnf_tests_cimcb():
    sigvnf_CreateInstantiate(sig_vnfdId_BaseLoad)
    sigvnf_Modify_DisableAutoScale(sig_vnfdId_BaseLoad)
    sigvnf_Modify_DisableAutoBackup(sig_vnfdId_BaseLoad)
    sigvnf_ConnectSbcMediaVnf(sig_vnfdId_BaseLoad)
    sigvnf_Backup(sig_vnfdId_BaseLoad)

def sigvnf_tests_br():
    sigvnf_Backup(sig_vnfdId_BaseLoad)
    sigvnf_DBRestore(sig_vnfdId_BaseLoad)

def sigvnf_tests_td():
    sigvnf_Terminate(sig_vnfdId_BaseLoad)
    sigvnf_Delete(sig_vnfdId_BaseLoad)

def sigvnf_tests_Heal():
    sigvnf_Heal_Single(sig_vnfdId_BaseLoad)
    sigvnf_Heal_Multiple(sig_vnfdId_BaseLoad)

def sigvnf_tests_scale():
    sigvnf_Scale_OutIn(sig_vnfdId_BaseLoad)

def sigvnf_tests_su():
    sigvnf_ChangePackageVersion(sig_vnfdId_BaseLoad, sig_vnfdId_SUToLoad)
    sigvnf_UpgradePrecheck(sig_vnfdId_SUToLoad)
    sigvnf_Upgrade1Apply(sig_vnfdId_SUToLoad)
    sigvnf_Upgrade2Activate(sig_vnfdId_SUToLoad)
    sigvnf_Upgrade3Commit(sig_vnfdId_SUToLoad)

def sigvnf_tests_cssu():
    sigvnf_UpgradeArchive(sig_vnfdId_BaseLoad)
    sigvnf_Terminate(sig_vnfdId_BaseLoad)
    sigvnf_Delete(sig_vnfdId_BaseLoad)
    sigvnf_CSSUInstantiate(sig_vnfdId_SUToLoad)

########################################################################################################################
# Main
# To-do list:
# - request timeout and maxretries
# - form instantiate.json with additionalParams, vim passwd
# - check operation status before do operation to avoid PROCESSING lcm action
# - setup ssh key for backup use
if __name__ == '__main__':

    # Disable following warning:
    # D:\Program Files (x86)\Python37-32\lib\site-packages\urllib3\connectionpool.py:1004:
    # InsecureRequestWarning: Unverified HTTPS request is being made.
    # Adding certificate verification is strongly advised.
    # See: https://urllib3.readthedocs.io/en/latest/advanced-usage.html#ssl-warnings
    urllib3.disable_warnings()

    setup_vnfdIds()

    # sigvnf_Heal_Multiple(sig_vnfdId_BaseLoad)
    # sigvnf_Scale_OutIn(sig_vnfdId_BaseLoad)
    # sigvnf_PrepCSSUArchiveZip(sig_vnfdId_BaseLoad)

    # sigvnf_tests_td()

    # sigvnf_DeleteVnfpkg(sigVersion_SUToLoad)
    # sigvnf_UploadVnfpkg(sigVersion_SUToLoad)

    # sigvnf_tests_cimcb()

    # sigvnf_Scale_OutIn(sig_vnfdId_BaseLoad)

    # sigvnf_Heal_Multiple(sig_vnfdId_BaseLoad)

    # sigvnf_tests_br()

    # sigvnf_tests_scale()

    # sigvnf_tests_td()

    sigvnf_tests_alpha()








