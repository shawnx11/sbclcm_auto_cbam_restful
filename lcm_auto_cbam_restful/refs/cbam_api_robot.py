#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time

from cbam_api import CbamApi, Utils

# This is CBAM API wrapper for robotframework
# it does not follow python naming convention 
# due to match robotframework naming convention

def Create_VNF_Package(base_address, client_id, client_secret, file_location):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    result = cbam_api.create_vnf_package(file_location)
    return result

def Read_VNF_Packages(base_address, client_id, client_secret):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    result = cbam_api.read_vnf_packages()
    return result.content

def Read_VNF_LCM_Operations(base_address, client_id, client_secret):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    result = cbam_api.read_vnf_lcm_operations()
    return result.content

def Read_VNF_Package(base_address, client_id, client_secret, package_vnfd_id):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    result = cbam_api.read_vnf_package(package_vnfd_id)
    return result.content

def Read_VNF_LCM_Operation(base_address, client_id, client_secret, operation_id):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    result = cbam_api.read_vnf_lcm_operation(operation_id)
    return result.content

def Delete_VNF_Package(base_address, client_id, client_secret, package_vnfd_id):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    result = cbam_api.delete_vnf_package(package_vnfd_id)
    return result

def Create_VNF(base_address, client_id, client_secret, name, package_vnfd_id, description=None):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    result = cbam_api.create_vnf(name, package_vnfd_id, description)
    return result

def Read_VNF(base_address, client_id, client_secret, vnf_id):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    result = cbam_api.read_vnf(vnf_id)
    return result.content

def Read_VNFs(base_address, client_id, client_secret):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    result = cbam_api.read_vnfs()
    return result.content

def Update_VNF(base_address, client_id, client_secret, vnf_id, update_data):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    update_data = Utils.load_parameters(update_data)
    result = cbam_api.update_vnf(vnf_id, update_data)
    return result

def Delete_VNF(base_address, client_id, client_secret, vnf_id):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    result = cbam_api.delete_vnf(vnf_id)
    return result

def Instantiate(base_address, client_id, client_secret, vnf_id, instantiate_data):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    instantiate_data = Utils.load_parameters(instantiate_data)
    result = cbam_api.instantiate(vnf_id, instantiate_data)
    return result
    
def Scale(base_address, client_id, client_secret, vnf_id, scale_data):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    scale_data = Utils.load_parameters(scale_data)
    result = cbam_api.scale(vnf_id, scale_data)
    return result

def Terminate(base_address, client_id, client_secret, vnf_id, terminate_data):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    terminate_data = Utils.load_parameters(terminate_data)
    result = cbam_api.terminate(vnf_id, terminate_data)
    return result

def Heal(base_address, client_id, client_secret, vnf_id, heal_data):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    heal_data = Utils.load_parameters(heal_data)
    result = cbam_api.heal(vnf_id, heal_data)
    return result

def Upgrade(base_address, client_id, client_secret, vnf_id, upgrade_data):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    update_data = Utils.load_parameters(upgrade_data)
    result = cbam_api.upgrade(vnf_id, upgrade_data)
    return result

def Custom(base_address, client_id, client_secret, vnf_id, operation_name, custom_data):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    custom_data = Utils.load_parameters(custom_data)
    result = cbam_api.custom(vnf_id, operation_name, custom_data)
    return result

def Read_Upgrade_Baseline(base_address, client_id, client_secret, vnf_id):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    result = cbam_api.read_upgrade_baseline(vnf_id)
    return result.content

def Wait_For_Operation_To_Complete(base_address, client_id, client_secret, operation_id, timeout=1500, check_delay=30):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    start_time = time.time()
    end_time = start_time + timeout
    while end_time > time.time():
        cbam_api.authenticate()
        operation_data = cbam_api.read_vnf_lcm_operation(operation_id)
        if operation_data.content["operationState"] != "PROCESSING":
            return operation_data.content
        time.sleep(check_delay)
    return None

def Find_VNF_LCM_Operations_By_Name(base_address, client_id, client_secret, operation_name):
    cbam_api = CbamApi(base_address, client_id, client_secret)
    cbam_api.authenticate()
    response = cbam_api.read_vnf_lcm_operations()
    found = []
    if not response.content:
        return found
    operations = response.content
    for operation in operations:
        if not operation_name.lower().startswith("custom:"):
            if operation['operation'].lower() == operation_name.lower():
                found.append(operation)
        else:
            try:
                if operation['operationName'].lower() == operation_name.lower():
                    found.append(operation)
            except KeyError:
                pass
    return sorted(found, key=lambda item: item["startTime"], reverse=True)
