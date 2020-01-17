# -*- coding:UTF-8 -*-

import requests
import json
import time

# CBAM url and CBAM client
cbam_url = 'https://10.75.44.14'
url = 'https://10.75.44.14'
client_id = 'cbam_rest'
client_secret = '5b895f51-fbec-46b9-bf98-8bd5ab6c859d'

vnflcm_base_path = '/vnflcm/v1'
vnfpkgm_base_path = '/vnfpkgm/v1'

vnflcm_dict = {
    'instantiate': cbam_url + vnflcm_base_path + '/vnf_instances/' + vnf_id + '/instantiate'
}

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

    return token

def print_response(response):
    print('response: ', response)
    print('response.headers: ', response.headers)
    print('response.text: ', response.text)

def dump_response_data(response, funcname):
    print('Now is at function:', funcname)
    data = json.loads(response.text)
    # for item in data:
    #     for i, j in item.items():
    #         print(i, ':', j)
    #     print('\n')
    print(data)
    print('\n')

def get_vnf_packages():

    token = get_token()
    token_bear = 'bearer ' + token
    headers = {'Authorization': token_bear}

    # url_vnfps = url + '/api/catalog/adapter/vnfpackages'
    url_vnfps = url + '/vnfpkgm/v1' + '/vnf_packages'
    address = url_vnfps
    verify = False
    response = requests.get(address, headers=headers, verify=verify)

    dump_response_data(response, 'get_vnf_packages')

# id : 1006
# vnfdId : f716ad0b-4087-4309-8244-d9079e6fedf7
# vnfProvider : Nokia
# vnfProductName : SBC
# vnfSoftwareVersion : sbclcm01~37.28.06
# vnfdVersion : sbclcm01~37.28.06
# onboardingState : ONBOARDED
# operationalState : ENABLED
# userDefinedData : {'vimType': 'openstack', 'references': []}
# _links : {'vnfd': {'href': 'https://10.75.44.14/vnfpkgm/v1/vnf_packages/1006/vnfd'}, 'packageContent': {'href': 'https://10.75.44.14/vnfpkgm/v1/vnf_packages/1006/package_content'}, 'self': {'href': 'https://10.75.44.14/vnfpkgm/v1/vnf_packages/1006'}}
#
#
# id : 1010
# vnfdId : fa398a22-1654-11ea-9417-1cc1de70bde4
# vnfProvider : Nokia
# vnfProductName : SBC-media
# vnfSoftwareVersion : an100047
# vnfdVersion : sbgw01
# onboardingState : ONBOARDED
# operationalState : ENABLED
# userDefinedData : {'vimType': 'openstack', 'references': []}
# _links : {'vnfd': {'href': 'https://10.75.44.14/vnfpkgm/v1/vnf_packages/1010/vnfd'}, 'packageContent': {'href': 'https://10.75.44.14/vnfpkgm/v1/vnf_packages/1010/package_content'}, 'self': {'href': 'https://10.75.44.14/vnfpkgm/v1/vnf_packages/1010'}}


# Signaling plane VNF
class SigVnf(object):
    def __init__(self, vnfdId, name='sbclcm-sig-plane', description = 'SBC LCM signaling plane VNF for Auto Test via CBAM REST API'):
        self.name = name
        self.description = description
        self.vnfdId = vnfdId
        self.id = ''
        self.vnflcm_create          = cbam_url + '/vnflcm/v1' + '/vnf_instances'
        self.vnflcm_instantiate     = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/instantiate'
        self.vnflcm_terminate       = cbam_url + '/vnflcm/v1' + '/vnf_instances/' + self.id + '/terminate'
        self.vnflcm_delete          = url + '/vnflcm/v1' + '/vnf_instances/' + self.id

    def get_vnfdId(self):
        return self.vnfdId

    def get_id(self):
        return self.id

    def create_vnf(self):
        token = get_token()
        token_bear = 'bearer ' + token
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


# Media plane VNF
class MediaVnf(object):
    pass

def create_vnf():
    name = 'sbclcm-sig-plane'
    vnfdId = 'f716ad0b-4087-4309-8244-d9079e6fedf7'
    description = 'SBC LCM signaling plane VNF for Auto Test via CBAM REST API'

    token = get_token()
    token_bear = 'bearer ' + token
    headers = {'Authorization': token_bear, "Content-Type": "application/json"}

    # url_vnf = url + '/vnfm/lcm/v3/vnfs'
    url_vnf = url + '/vnflcm/v1' + '/vnf_instances'
    address = url_vnf
    verify = False
    response = requests.post(
        address,
        headers=headers,
        json={
            "vnfdId": vnfdId,
            "vnfInstanceName": name,
            "vnfInstanceDescription": description
            },
        verify=verify)

    # data = json.loads(response.text)
    dump_response_data(response, 'create_vnf')

    #get vnf ID
    data = json.loads(response.text)

    global vnf_id
    vnf_id = data['id']
    print(vnf_id)


def instantiate_vnf():
    token = get_token()
    token_bear = 'bearer ' + token
    headers = {'Authorization': token_bear, "Content-Type": "application/json"}

    url_vnf = url + '/vnflcm/v1' + '/vnf_instances/' + vnf_id + '/instantiate'
    print('url_vnf:', url_vnf)
    instantiate_file = 'D:\\Programs\\JetBrains\\PycharmProjects\\py37projects\\lcm_auto_cbam_restful\\data\\sig-plane\\LCM_instantiate_params.json'

    address = url_vnf
    verify = False
    parameters = json.load(open(instantiate_file, "rb"))
    response = requests.post(address, headers=headers, json=parameters, verify=verify)

    # data = json.loads(response.text)
    # print(data)


def terminate_vnf():
    token = get_token()
    token_bear = 'bearer ' + token
    headers = {'Authorization': token_bear}

    url_vnf = url + '/vnflcm/v1' + '/vnf_instances/' + vnf_id + '/terminate'

    address = url_vnf
    verify = False
    response = requests.post(
        address,
        headers=headers,
        json={
            "terminationType": 'FORCEFUL'
            },
        verify=verify)


def delete_vnf():
    token = get_token()
    token_bear = 'bearer ' + token
    headers = {'Authorization': token_bear}

    url_vnf = url + '/vnflcm/v1' + '/vnf_instances/' + vnf_id

    address = url_vnf
    verify = False
    response = requests.delete(address, headers=headers, verify=verify)


# This is to get vnf list
def get_vnfs():

    token = get_token()
    token_bear = 'bearer ' + token
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

# CBAM GUI client:
# client_id = 'lcm'
# client_secret = '-Assured1111'
# REST API client:
# client: cbam_rest
# secret: 5b895f51-fbec-46b9-bf98-8bd5ab6c859d
if __name__ == '__main__':

    # get_vnfs()

    # get_vnf_packages()

    create_vnf()

    instantiate_vnf()

    # check vnf status



