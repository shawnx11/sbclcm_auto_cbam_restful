#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
import time
import argparse
import zipfile
import glob
import re
import shutil
import subprocess
import sys
import yaml

from cbam_api import CbamApi, InvalidConfiguration, Executor


class VM:
    def __init__(self, idVM, nameVM, typeVM, flavorVM):
        self.id = idVM
        self.name = nameVM
        self.type = typeVM
        self.flavor = flavorVM


class VMResouces(VM):
    def __init__(self, idVM, nameVM, typeVM, flavorVM, ramVM, diskVM, vcpuVM):
        self.ram = ramVM
        self.disk = diskVM
        self.vcpu = vcpuVM
        VM.__init__(self, idVM, nameVM, typeVM, flavorVM)


class VMNetworkInfo():
    def __init__(self, networkVM, networkStatusVM):
        self.network = networkVM
        self.networkStatus = networkStatusVM


class VMSubnetInfo():
    def __init__(self, subnetVM, subnetStatusVM):
        self.subnet = subnetVM
        self.subnetStatus = subnetStatusVM


class VMImageInfo():
    def __init__(self, imageVM, imageStatusVM):
        self.image = imageVM
        self.imageStatus = imageStatusVM


class VMZoneInfo():
    def __init__(self, zoneVM, zoneStatusVM):
        self.zone = zoneVM
        self.zoneStatus = zoneStatusVM


class Alert():
    def __init__(self, typeAl, descriptionAl):
        self.type = typeAl
        self.description = descriptionAl

    def get_type(self):
        return self.type

    def get_description(self):
        return self.description


class SbcAutoRun(object):
    def __init__(self, args=None):
        self.args = args
        if args is not None:
            self.cbam_api = CbamApi(args.host, args.client_id, args.client_secret, args.version)
            self.cbam_api.authenticate()


    def get_vnfd_id(self, zip_package_file):
        tmp_dir = "/tmp/pack_check/"
        z = zipfile.ZipFile(zip_package_file)
        z.extractall(tmp_dir)
        yaml_files = glob.glob(tmp_dir + "*tosca.yaml")
        tosca_file = yaml_files[0]
        z.close()
        with open(tosca_file, 'r') as f:
            dataMap = yaml.safe_load(f)
        try:
            vnfd_id = dataMap["topology_template"]["substitution_mappings"]["properties"]["descriptor_id"]
        except KeyError:
            raise InvalidConfiguration("descriptor_id key not found in tosca file of VNF package")
        shutil.rmtree(tmp_dir)
        return vnfd_id


    def write_vnf_id_to_file(self, vnf_id):
        vnf_file = open(self.args.dir + "/vnf_id.out", "w")
        vnf_file.write(vnf_id + "\n")
        vnf_file.close()


    def run_install(self):
        ret_install = 1
        vnfd_name = self.get_vnfd_id(self.args.vnf_package_file)

        # Create VNF package
        self.args.file = self.args.vnf_package_file
        self.args.command = "create_vnf_package"
        Executor(self.args).validate_create_vnf_package()

        print("+ Start VNF package create")
        resp_create_vnf_package = self.cbam_api.create_vnf_package(self.args.file)
        # Create VNF
        if (resp_create_vnf_package.status_code == 200) or (resp_create_vnf_package.status_code == 500 and "Vnf package already exists." in resp_create_vnf_package.content.values()):
            create_data = {'name': 'Auto-install-test', 'vnfdId': vnfd_name, 'description': 'Test auto installation'}
            self.args.data = json.dumps(create_data)
            self.args.command = "create_vnf"
            Executor(self.args).validate_create_vnf()

            print("+ Start VNF create")
            resp_create_vnf = self.cbam_api.create_vnf(create_data["name"], create_data["vnfdId"])
            # Modify VNF
            if resp_create_vnf.status_code == 201:
                vnfId = resp_create_vnf.content["id"]
                self.write_vnf_id_to_file(vnfId)

                with open(self.args.extension_file, "r") as f_ext:
                    json_data_ext = json.load(f_ext)

                self.args.data = "@" + self.args.extension_file
                self.args.resource_id = vnfId
                self.args.command = "update_vnf"
                Executor(self.args).validate_update_vnf()

                print("+ Start Modify")
                resp_update_vnf = self.cbam_api.update_vnf(self.args.resource_id, json_data_ext)

                # Instantiate
                if resp_update_vnf.status_code == 202:
                    with open(self.args.instantiate_file, "r") as f_inst:
                        json_data_inst = json.load(f_inst)

                    self.args.data = "@" + self.args.instantiate_file
                    self.args.command = "instantiate"
                    Executor(self.args).validate_instantiate()
                    print("+ Start Instantiate")
                    resp_instantiate = self.cbam_api.instantiate(self.args.resource_id, json_data_inst)
                    if resp_instantiate.status_code == 202:
                        find_resp = find_operation_by_name(self.cbam_api, "INSTANTIATE", vnfId)
                        if len(find_resp) > 0:
                            last_instantiate_op_id = find_resp[0]["id"]
                            # Wait to complete instantiate operation
                            ret_install = wait_for_operation_complete(self.cbam_api, last_instantiate_op_id, 3600)
                        else:
                            print("Instantiate operation not found")
                    else:
                        print("Instantiate failure:", resp_instantiate.content)
                else:
                    print("VNF modify failure:", resp_update_vnf.content)
            else:
                print("VNF create failure:", resp_create_vnf.content)
        else:
            print("VNF package create failure:", resp_create_vnf_package.content)

        return ret_install


    def verify_vnf_inst_state(self):
        resp_read_vnf = self.cbam_api.read_vnf(self.args.vnf_id)
        if resp_read_vnf.status_code == 200:
            try:
                if resp_read_vnf.content["instantiationState"] == "NOT_INSTANTIATED":
                    print("Upgrade operation requires VNF in INSTANTIATED state. VNF =", self.args.vnf_id, "state is:", resp_read_vnf.content["instantiationState"])
                    return 1
            except KeyError:
                print(resp_read_vnf.content)
                return 1
        else:
            print("Read VNF =", self.args.vnf_id, "failed with status:", resp_read_vnf.status_code)
            print(resp_read_vnf.content)
            return 1
        return None


    def get_image_name(self, ext_data):
        image_name = None
        try:
            if int(self.args.version) >= 4:
                image_name = ext_data["extensions"]["media_params"]["vm_sw_image"]["10"]
            else:
                image_name = ext_data["extensions"][0]["value"]["vm_sw_image"]["10"]
        except KeyError:
            print("Error when getting vm_sw_image key from extensions file")
        return image_name


    def run_upgrade(self):
        upgrade_operation = self.args.command
        ret_upgrade = self.verify_vnf_inst_state()
        if ret_upgrade is not None:
            return ret_upgrade
        else:
            ret_upgrade = 1

        # Create VNF package
        self.args.file = self.args.vnf_package_file
        self.args.command = "create_vnf_package"
        Executor(self.args).validate_create_vnf_package()

        print("+ Start VNF package create")
        resp_create_vnf_package = self.cbam_api.create_vnf_package(self.args.file)

        # Change package version
        packExist = "Vnf package already exists."
        if (resp_create_vnf_package.status_code == 200) or (resp_create_vnf_package.status_code == 500 and packExist in resp_create_vnf_package.content.values()):
            print("+ Start Change Package Version")
            with open(self.args.extension_file, "r") as f_in:
                json_data_ext = json.load(f_in)
            self.args.data = "@" + self.args.extension_file
            self.args.command = "upgrade"
            self.args.resource_id = self.args.vnf_id
            Executor(self.args).validate_upgrade()
            resp_upgrade = self.cbam_api.upgrade(self.args.resource_id, json_data_ext)
            if resp_upgrade.status_code == 202:
                upgrade_op_id = resp_upgrade.content["id"]
                # Wait to complete Change package version
                wait_for_operation_complete(self.cbam_api, upgrade_op_id, 100, 2)

                # Start custom operation nssu/issu
                self.args.command = "custom"
                self.args.operation_name = upgrade_operation
                Executor(self.args).validate_custom()

                image = self.get_image_name(json_data_ext)
                if image is None:
                    return 1
                print("+ Start", self.args.operation_name, "to image:", image)
                image_data = {'additionalParams': {'image': image}}

                resp_custom = self.cbam_api.custom(self.args.resource_id, self.args.operation_name, image_data)

                # Wait to complete custom operation
                other_op_id = resp_custom.content["id"]
                ret_upgrade = wait_for_operation_complete(self.cbam_api, other_op_id, 3600, 30)
            else:
                print("Change Package Version failure:", resp_upgrade.content)
        else:
            print("VNF package create failure:", resp_create_vnf_package.content)

        return ret_upgrade


def find_operation_by_name(api, operation_name, vnfID=None):
    api.authenticate()
    response = api.read_vnf_lcm_operations(vnfID)
    found = []
    if not response.content:
        return found
    operations = response.content
    for operation in operations:
        if not operation_name.lower().startswith("custom:"):
            if int(api.version) >= 4:
                opType = "operation"
            else:
                opType = "operationType"
            if operation[opType].lower() == operation_name.lower():
                found.append(operation)
        else:
            try:
                if operation['operationName'].lower() == operation_name.lower():
                    found.append(operation)
            except KeyError:
                pass
    return sorted(found, key=lambda item: item["startTime"], reverse=True)


def wait_for_operation_complete(api, operation_id, timeout=1500, check_delay=30):
    print("Operation id=", operation_id)
    print("Wait to finish operation ...")
    if int(api.version) >= 4:
        opState = "operationState"
        startStr = "PROCESSING"
        endStr = "COMPLETED"
    else:
        opState = "status"
        startStr = "STARTED"
        endStr = "FINISHED"

    start_time = time.time()
    end_time = start_time + timeout
    while end_time > time.time():
        api.authenticate()
        operation_data = api.read_vnf_lcm_operation(operation_id)

        if operation_data.content[opState] != startStr:
            if operation_data.content[opState] == endStr:
                return 0
            else:
                print("Operation Failure:", operation_data.content)
                return 1
        time.sleep(check_delay)

    print("Operation wait timeout, state:", operation_data.content[opState])
    return 2

def validate_cbam_params(args):
    if args.host is None:
        if "CBAM_HOST" in os.environ:
            args.host = os.environ["CBAM_HOST"]
        else:
            raise InvalidConfiguration("Host must be provided")
    if args.client_id is None:
        if "CBAM_CLIENT_ID" in os.environ:
            args.client_id = os.environ["CBAM_CLIENT_ID"]
        else:
            raise InvalidConfiguration("Client ID must be provided")
    if args.client_secret is None:
        if "CBAM_CLIENT_SECRET" in os.environ:
            args.client_secret = os.environ["CBAM_CLIENT_SECRET"]
        else:
            raise InvalidConfiguration("Client secret must be provided")


def validate_install_params(args):
    if args.dir is None:
        if "ARTIFACTS_DIR" in os.environ:
            args.dir = os.environ["ARTIFACTS_DIR"]
        else:
            raise InvalidConfiguration("Artifacts directory must be provided")
    if "VNF_PACKAGE_FILE" in os.environ:
        args.vnf_package_file = args.dir + "/" + os.environ["VNF_PACKAGE_FILE"]
    else:
        raise InvalidConfiguration("VNF package file must be provided. Set environment running 'source sbcAutoRunSetup.sh'")
    if "EXTENSION_FILE" in os.environ:
        args.extension_file = args.dir + "/" + os.environ["EXTENSION_FILE"]
    else:
        raise InvalidConfiguration("Extensions file must be provided. Set environment running 'source sbcAutoRunSetup.sh'")
    if "INSTANTIATE_FILE" in os.environ:
        args.instantiate_file = args.dir + "/" + os.environ["INSTANTIATE_FILE"]
    else:
        raise InvalidConfiguration("Instantiate file must be provided. Set environment running 'source sbcAutoRunSetup.sh'")


def validate_upgrade_params(args):
    if args.dir is None:
        if "UPGRADE_ARTIFACTS_DIR" in os.environ:
            args.dir = os.environ["UPGRADE_ARTIFACTS_DIR"]
        else:
            raise InvalidConfiguration("Upgrade Artifacts directory must be provided")
    if args.vnf_id is None:
        raise InvalidConfiguration("VNF id must be provided")
    if "UPGR_VNF_PACKAGE_FILE" in os.environ:
        args.vnf_package_file = args.dir + "/" + os.environ["UPGR_VNF_PACKAGE_FILE"]
    else:
        raise InvalidConfiguration("Upgrade VNF package file must be provided. Set environment running 'source sbcAutoRunSetup.sh'")
    if "UPGR_EXTENSION_FILE" in os.environ:
        args.extension_file = args.dir + "/" + os.environ["UPGR_EXTENSION_FILE"]
    else:
        raise InvalidConfiguration("Upgrade extensions file must be provided. Set environment running 'source sbcAutoRunSetup.sh'")
    args.instantiate_file = None


def validate_required_files(args):
    if args.command == "install" or args.command == "issu" or args.command == "nssu":
        if not os.path.isfile(args.vnf_package_file):
            print("File not found:", args.vnf_package_file)
            return 1
        if not os.path.isfile(args.extension_file):
            print("File not found:", args.extension_file)
            return 1
    if args.command == "install":
        if not os.path.isfile(args.instantiate_file):
            print("File not found:", args.instantiate_file)
            return 1
    return 0

def send_command(command):
    bashCom = command
    try:
        process = subprocess.Popen(bashCom.split(), stdout=subprocess.PIPE)
    except Exception as ex:
        print("Command \"" + bashCom +"\" failure:", ex)
        return "-1"
    output = process.communicate()
    if output:
        return output[0].decode('ascii')
    else:
        return 0

def search_word(pattern, sfile, numb):
    word = re.search(pattern, sfile)
    if not word:
        return 0
    else:
        return word.group(numb)

def write_line(length):
    return ''.join('-' for i in range(length))

def write_alert(alertObjects):
    idAlert = 1
    print
    print(write_line(121))
    print(('|{:*^119}|').format("ALERTS"))
    print(write_line(121))
    for alertObject in alertObjects:
        print(('|{:10}) |{:40}| {:64}|').format(idAlert, Alert.get_type(alertObject), Alert.get_description(alertObject)))
        idAlert += 1
    print(write_line(121))
    print

def check_output(output, message):
    alertArray = []
    if output == 0:
        alertArray.append(Alert("OPENSTACK COMMAND RESULT", message))
        write_alert(alertArray)
        sys.exit(1)

def rm_duplicate(array):
    newArray = []
    for element in array:
        if element not in newArray:
            newArray.append(element)
    return newArray

def check_array(array, mesage):
    alertArray = []
    if not array:
        alertArray.append(Alert("FILE/OPENSTACK PROBLEM", mesage))
        alertArray.append(Alert("FILE/OPENSTACK PROBLEM", "The command is stopped."))
        write_alert(alertArray)
        sys.exit(1)

def del_duplicate(array):
    newArray = []
    for element in array:
        if array[element] not in newArray:
            newArray.append(array[element])
    return newArray

def check_result(variable, message):
    if variable == 0:
        alertArray = []
        alertArray.append(Alert("FILE/OPENSTACK PROBLEM", str(message) + "is not found in text!"))
        alertArray.append(Alert("FILE/OPENSTACK PROBLEM", "The command is stopped!"))
        write_alert(alertArray)
        sys.exit(1)

def find_element_in_comand(comandOutput, array, classOutput):
    newArray = []
    for element in array:
        searchElement = search_word(r"(\W+)(" + str(element) + r")(\W+)(\w+)(\W+)", comandOutput, 1)
        if searchElement == 0:
            statusElement = "NOT FOUND"
        else:
            statusElement = "OK"
        newArray.append(classOutput(element, statusElement))
    return newArray

def get_pim_to_install(gr_num):
    to_install = []
    slot_num = [19, 20, 17, 18, 15, 16, 13, 14, 7, 8, 5, 6, 3, 4, 1, 2]
    for pimNr in range(int(gr_num)*2):
        to_install.append(slot_num[pimNr])
    return to_install


def get_mcm_to_install(num):
    to_install = []
    slot_num = [1, 2, 3, 4, 5, 6, 7, 8, 13, 14, 15, 16, 17, 18]
    for mcmNr in range(int(num)):
        to_install.append(slot_num[mcmNr])
    return to_install


def get_resource_status(res_value):
    if res_value < 0:
        return "ERROR - not enough"
    else:
        return "OK"

def alert_for_unusedVMs(uninstArr, out):
    alertArray = []
    for element in uninstArr:
        txtPatter = r"(" + re.escape(element.flavor) + r"\s+\W)(\s\w+\s+\W\s+)(\d+)(\s\W+)(\d+)(\s\W+)(\d+)(\s\W+)(\d)(\s\W+)(\w+)"
        ram = search_word(txtPatter, out, 3)
        disk = search_word(txtPatter, out, 5)
        vcpus = search_word(txtPatter, out, 9)
        if int(ram) <= 0 or int(disk) <= 0 or int(vcpus) <= 0:
            alertArray.append(Alert("WARNING for unused VMs", str(element.name) + " -> UNKNOWN FLAVOR  " + element.flavor + " assigned!"))

    if alertArray:
        write_alert(alertArray)

def print_resources_table(resArray):
    print(write_line(121))
    print(('|{:*^119}|').format("VM RESOURCES"))
    print(write_line(121))
    print(('|{:35}|{:20}|{:20}|{:20}|{:20}|').format("VM Name", "VM Type", "RAM (MB)", "DISK SPACE (GB)", "VCPU"))
    print(write_line(121))
    totalRam, totalDisk, totalVcpu = 0, 0, 0
    for res in resArray:
        print(('|{:35}|{:20}|{:20}|{:20}|{:20}|').format(str(res.name), str(res.type), str(res.ram), str(res.disk), str(res.vcpu)))
        totalRam += int(res.ram)
        totalDisk += int(res.disk)
        totalVcpu += int(res.vcpu)

    output = send_command("openstack limits show --quote all --absolute")
    check_output(output, "Error reading openstack limits")
    vcpuLimit = int(search_word(r"(\W+)(maxTotalCores)(\W+)(\d+)(\W+)", output, 4))
    check_result(vcpuLimit, "limit number cores")
    ramLimit = int(search_word(r"(\W+)(maxTotalRAMSize)(\W+)(\d+)(\W+)", output, 4))
    check_result(ramLimit, "limit memory")
    diskLimit = int(search_word(r"(\W+)(maxTotalVolumeGigabytes)(\W+)(\d+)(\W+)", output, 4))
    check_result(diskLimit, "limit space on disk")

    vcpuUsed = int(search_word(r"(\W+)(totalCoresUsed)(\W+)(\d+)(\W+)", output, 4))
    check_result(vcpuUsed, "used number cores")
    ramUsed = int(search_word(r"(\W+)(totalRAMUsed)(\W+)(\d+)(\W+)", output, 4))
    check_result(ramUsed, "used memory")
    diskUsed = int(search_word(r"(\W+)(totalGigabytesUsed)(\W+)(\d+)(\W+)", output, 4))
    check_result(diskUsed, "used space on disk")

    freeVcpu = vcpuLimit - vcpuUsed
    freeRam = ramLimit - ramUsed
    freeDisk = diskLimit - diskUsed

    print(write_line(121))
    print(('|{:{width}}|{:20}|{:20}|{:20}|').format("", "RAM", "DISK", "VCPU", width=56))
    print(write_line(121))
    print(('|{:{width}}|{:20}|{:20}|{:20}|').format("RESOURCES TOTAL USAGE", str(totalRam), str(totalDisk), str(totalVcpu), width=56))
    print(('|{:{width}}|{:20}|{:20}|{:20}|').format("FREE RESOURCES AT OPENSTACK", str(freeRam), str(freeDisk), str(freeVcpu), width=56))
    print(write_line(121))
    freeRam -= totalRam
    freeDisk -= totalDisk
    freeVcpu -= totalVcpu
    print(('|{:{width}}|{:20}|{:20}|{:20}|').format("FREE - TOTAL USAGE", str(freeRam), str(freeDisk), str(freeVcpu), width=56))
    print(write_line(121))
    print(('|{:{width}}|{:20}|{:20}|{:20}|').format("STATUS", get_resource_status(freeRam), get_resource_status(freeDisk), get_resource_status(freeVcpu), width=56))
    print(write_line(121))

    alertArray = []
    if get_resource_status(freeRam) != "OK" or get_resource_status(freeDisk) != "OK" or get_resource_status(freeVcpu) != "OK":
        alertArray.append(Alert("RESOURCES CHECK FAILED", " -> NOT ENOUGH RESOURCES AVAILABLE!"))
        write_alert(alertArray)
        sys.exit(1)


def verify_resources(VMarr, uVMs):
    alertArray = []
    output = send_command("openstack flavor list")
    check_output(output, "Error reading openstack flavor list")
    resourcesArray = []

    for element in VMarr:
        txtPatter = r"(" + re.escape(element.flavor) + r"\s+\W)(\s\w+\s+\W\s+)(\d+)(\s\W+)(\d+)(\s\W+)(\d+)(\s\W+)(\d)(\s\W+)(\w+)"
        ram = search_word(txtPatter, output, 3)
        disk = search_word(txtPatter, output, 5)
        vcpus = search_word(txtPatter, output, 9)
        if int(ram) <= 0 or int(disk) <= 0 or int(vcpus) <= 0:
            alertArray.append(Alert("VM SEARCHING", str(element.name) + " -> UNKNOWN FLAVOR  " + element.flavor + " assigned!"))
        else:
            resourcesArray.append(VMResouces(element.id, element.name, element.type, element.flavor, ram, disk, vcpus))

    if alertArray:
        write_alert(alertArray)
        sys.exit(1)

    check_array(resourcesArray, "Error creating VM's resorces list")

    # Verify flavors for unused VMs - grow preparation check
    alert_for_unusedVMs(uVMs, output)
    print_resources_table(resourcesArray)


def verify_image(imageList):
    stat = 0
    outputImage = send_command("openstack image list")
    check_output(outputImage, "Error reading openstack image list")

    imageArray = del_duplicate(imageList)
    check_array(imageArray, "Error creating image list.")
    imageArray = rm_duplicate(imageArray)

    vmImageInfos = []
    vmImageInfos = find_element_in_comand(outputImage, imageArray, VMImageInfo)
    check_array(vmImageInfos, "Error creating image list.")

    print("")
    print("")
    print(write_line(121))
    print(('|{:*^119}|').format("ADDITIONAL INFORMATION"))
    print(write_line(121))
    print(('|{:83}|{:35}|').format("NETWORK IMAGE", "IMAGE STATUS"))
    print(write_line(121))
    for img in vmImageInfos:
        print(('|{:83}|{:35}|').format(img.image, img.imageStatus))
        if img.imageStatus != "OK":
            stat = -1
    print(write_line(121))
    alertArray = []
    if stat < 0:
        alertArray.append(Alert("IMAGE CHECK FAILED", " -> NOT UPLOADED AT OPENSTACK!"))
        write_alert(alertArray)
        sys.exit(1)


def get_net_status(search):
    if search == 0:
        return "NOT FOUND"
    else:
        return "OK"


def verify_networks(networksList):
    networks, subnets = [], []
    for netElement in networksList:
        if netElement != "SCM":
            for pair in range(0, 2):
                networks.append(networksList[netElement][pair]['network'])
                subnets.append(networksList[netElement][pair]['ipv4']['subnet'])
        else:
            for element in networksList[netElement]:
                networks.append(networksList[netElement][element]['network'])
                subnets.append(networksList[netElement][element]['ipv4']['subnet'])

    networks = rm_duplicate(networks)
    subnets = rm_duplicate(subnets)

    outputNet = send_command("openstack network list")
    check_output(outputNet, "Error reading openstack network list")
    outputSub = send_command("openstack subnet list")
    check_output(outputSub, "Error reading openstack subnet list")

    vmNetworkInfos = []
    vmSubnetInfos = []
    for network in networks:
        searchNetwork = search_word(r"(\W+)(" + str(network) + r")(\W+)", outputNet, 2)
        vmNetworkInfos.append(VMNetworkInfo(network, get_net_status(searchNetwork)))

    for subnet in subnets:
        searchSubnet = search_word(r"(\W+)(" + str(subnet) + r")(\W+)", outputSub, 2)
        vmSubnetInfos.append(VMSubnetInfo(subnet, get_net_status(searchSubnet)))

    check_array(vmNetworkInfos, "Error creating network list.")
    check_array(vmSubnetInfos, "Error creating subnet list.")

    stat = 0
    print(('|{:83}|{:35}|').format("NETWORK NAME", "NETWORK STATUS"))
    print(write_line(121))
    for net in vmNetworkInfos:
        print(('|{:83}|{:35}|').format(net.network, net.networkStatus))
        if net.networkStatus != "OK":
            stat = -1
    print(write_line(121))
    print(('|{:83}|{:35}|').format("SUBNET NAME", "SUBNET STATUS"))
    print(write_line(121))
    for sub in vmSubnetInfos:
        print(('|{:83}|{:35}|').format(sub.subnet, sub.subnetStatus))
        if sub.subnetStatus != "OK":
            stat = -1
    print(write_line(121))
    return stat


def verify_zones(zoneList):
    stat = 0
    outputZone = send_command("openstack availability zone list")
    check_output(outputZone, "Error reading availability zone list")

    zoneArray = del_duplicate(zoneList)
    check_array(zoneArray, "Error creating zone list.")
    zoneArray = rm_duplicate(zoneArray)

    vmZoneInfos = []
    vmZoneInfos = find_element_in_comand(outputZone, zoneArray, VMZoneInfo)
    check_array(vmZoneInfos, "Error creating zone list.")

    stat = 0
    print(('|{:83}|{:35}|').format("ZONE NAME", "ZONE STATUS"))
    print(write_line(121))
    for z in vmZoneInfos:
        print(('|{:83}|{:35}|').format(z.zone, z.zoneStatus))
        if z.zoneStatus != "OK":
            stat = -1
    print(write_line(121))
    return stat


def verify_openstack_config(args):
    with open(args.extension_file, "r") as f_in:
        extension_json = json.load(f_in)

    try:
        baseInformation = extension_json['extensions'][0]
    except KeyError:
        raise InvalidConfiguration("Wrong format of extensions file")

    allValues = baseInformation['value']
    try:
        pim_groups_number = allValues['pim_groups_number']
        physical_mcm_number = allValues['physical_mcm_number']
        max_pim_groups_number = allValues['max_pim_groups_number']
        max_physical_mcm_number = allValues['max_physical_mcm_number']
        vm_flavor = allValues['vm_flavor']
        provider_networks = allValues['provider_networks']
        vm_sw_image = allValues['vm_sw_image']
        vm_compute_avail_zone = allValues['vm_compute_avail_zone']
    except KeyError:
        raise InvalidConfiguration("Required value field is not found in extensions file")

    VMdict = {}
    for element in allValues:
        if str(element) == "vm_name":
            VMnames = allValues[element]
            for vmGroups in VMnames:
                for vm_nr in VMnames[vmGroups]:
                    VMdict[vm_nr] = VMnames[vmGroups][vm_nr]
            break
        elif str(element) == "name_map_slot":
            VMnames = allValues[element]
            for name in VMnames:
                VMdict[VMnames[name]] = name
            break

    check_array(VMdict, "Cannot create VM list. VM names not found in extensions file.")

    MCM_to_install = get_mcm_to_install(physical_mcm_number)
    PIM_to_install = get_pim_to_install(pim_groups_number)

    vmArray = []
    for s in [10, 11]:
        vmArray.append(VM(s, VMdict[str(s)], "SCM", vm_flavor[str(s)]))
    for m in MCM_to_install:
        vmArray.append(VM(m, VMdict[str(m)], "MCM", vm_flavor[str(m)]))
    for p in PIM_to_install:
        vmArray.append(VM(p, VMdict[str(p)], "PIM", vm_flavor[str(p)]))

    unusedVmArr = []
    for maxm in get_mcm_to_install(max_physical_mcm_number):
        if maxm not in MCM_to_install:
            unusedVmArr.append(VM(maxm, VMdict[str(maxm)], "MCM", vm_flavor[str(maxm)]))
    for maxp in get_pim_to_install(max_pim_groups_number):
        if maxp not in PIM_to_install:
            unusedVmArr.append(VM(maxp, VMdict[str(maxp)], "MCM", vm_flavor[str(maxp)]))

    verify_resources(vmArray, unusedVmArr)
    verify_image(vm_sw_image)
    vn = verify_networks(provider_networks)
    vz = verify_zones(vm_compute_avail_zone)
    alertArray = []
    if vn < 0 or vz < 0:
        alertArray.append(Alert("CHECK FAILED", " -> NOT FOUND AT OPENSTACK!"))
        write_alert(alertArray)
        sys.exit(1)


def parser():
    p = argparse.ArgumentParser(description="SBC automatic installation/upgrade cli")
    p.add_argument(
        "-v", "--version", help="VNFM API version", choices={'3', '4'}, default="3")
    p.add_argument(
        "-d", "--dir", help="Artifacts directory at cbam server", default=None)
    p.add_argument(
        "-u",
        "--host",
        help="CBAM host address, http[s]://host[:port]",
        default=None)
    p.add_argument("-cid", "--client-id", help="Client id", default=None)
    p.add_argument(
        "-s", "--client-secret", help="Client secret", default=None)
    p.add_argument(
        "-vnf", "--vnf-id", help="VNF identifier, CBAM-XXXXXXXXXX", default=None)
    p.add_argument(
        "-o", "--openstack", help="Openstack data verification. Applicable for installation only.", choices=('yes', 'no'), default="no")
    p.add_argument(
        "command", help="Command to execute", choices={'install', 'issu', 'nssu'})
    return p


def print_settings(args):
    print("Settings:")
    print("---------")
    print("CBAM host          ", args.host)
    print("CBAM client id     ", args.client_id)
    print("CBAM client secret ", args.client_secret)
    print("VNFM API version   ", args.version)
    if args.command == "install" or args.command == "issu" or args.command == "nssu":
        print("VNF package file   ", args.vnf_package_file)
        print("Extensions file    ", args.extension_file)
    if args.command == "install":
        print("Instantiate file   ", args.instantiate_file)
    print("")


def get_args():
    args = parser().parse_args()
    validate_cbam_params(args)
    if args.command == "issu" or args.command == "nssu":
        validate_upgrade_params(args)
    if args.command == "install":
        validate_install_params(args)
    return args


if __name__ == "__main__":
    margs = get_args()
    if validate_required_files(margs) == 1:
        sys.exit(1)
    print_settings(margs)
    op = margs.command
    if op == "install":
        if margs.openstack == "yes":
            verify_openstack_config(margs)
        main_ret = SbcAutoRun(margs).run_install()
    if op == "nssu" or op == "issu":
        if margs.openstack == "yes":
            print("Warning: Openstack verification is not applicable for upgrade!")
        main_ret = SbcAutoRun(margs).run_upgrade()

    print("")
    if main_ret == 0:
        print("+", op, "finished with Success")
    else:
        print("-", op, "finished with Failure")

    sys.exit(main_ret)
