#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import json
import uuid

try:
    from json.decoder import JSONDecodeError
except:
    from builtins import ValueError as JSONDecodeError 
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class InvalidAuthorizationHeader(Exception):
    pass


class InvalidConfiguration(Exception):
    pass


class Auth(object):
    def __init__(self, headers):
        self.headers = headers

    def __enter__(self):
        try:
            if self.headers["Authorization"] == "bearer None":
                raise InvalidAuthorizationHeader(
                    "Authorization header invalid")
        except KeyError:
            raise InvalidAuthorizationHeader(
                "No authorization header")

    def __exit__(self, type, value, traceback):
        pass


class Address(object):
    def token(self):
        return "auth/realms/cbam/protocol/openid-connect/token"

    def vnf_packages(self):
        return "api/catalog/adapter/vnfpackages"

    def vnf_package(self, resource_id):
        return "api/catalog/adapter/vnfpackages/{resource_id}".format(
            resource_id=resource_id)


class Address_v3(Address):
    def vnf_lcm_operations(self, resource_id):
        return "vnfm/lcm/v3/vnfs/{resource_id}/operation_executions".format(
            resource_id=resource_id)

    def vnf_lcm_operation(self, resource_id):
        return "vnfm/lcm/v3/operation_executions/{resource_id}".format(
            resource_id=resource_id)

    def vnf_instances(self):
        return "vnfm/lcm/v3/vnfs"

    def vnf_instance(self, resource_id):
        return "vnfm/lcm/v3/vnfs/{resource_id}".format(
            resource_id=resource_id)

    def instantiate(self, resource_id):
        return "vnfm/lcm/v3/vnfs/{resource_id}/instantiate".format(
            resource_id=resource_id)

    def scale(self, resource_id):
        return "vnfm/lcm/v3/vnfs/{resource_id}/scale".format(
            resource_id=resource_id)

    def terminate(self, resource_id):
        return "vnfm/lcm/v3/vnfs/{resource_id}/terminate".format(
            resource_id=resource_id)

    def heal(self, resource_id):
        return "vnfm/lcm/v3/vnfs/{resource_id}/heal".format(
            resource_id=resource_id)

    def upgrade(self, resource_id):
        return "vnfm/lcm/v3/vnfs/{resource_id}/upgrade".format(
            resource_id=resource_id)

    def custom(self, resource_id, operation_name):
        return "vnfm/lcm/v3/vnfs/{resource_id}/custom/{name}".format(
            resource_id=resource_id, name=operation_name)


class Address_v4(Address):
    def vnf_lcm_operations(self, resource_id):
        return "vnflcm/v1/vnf_lcm_op_occs"

    def vnf_lcm_operation(self, resource_id):
        return "vnflcm/v1/vnf_lcm_op_occs/{resource_id}".format(
            resource_id=resource_id)

    def vnf_instances(self):
        return "vnflcm/v1/vnf_instances"

    def vnf_instance(self, resource_id):
        return "vnflcm/v1/vnf_instances/{resource_id}".format(
            resource_id=resource_id)

    def instantiate(self, resource_id):
        return "vnflcm/v1/vnf_instances/{resource_id}/instantiate".format(
            resource_id=resource_id)

    def scale(self, resource_id):
        return "vnflcm/v1/vnf_instances/{resource_id}/scale".format(
            resource_id=resource_id)

    def terminate(self, resource_id):
        return "vnflcm/v1/vnf_instances/{resource_id}/terminate".format(
            resource_id=resource_id)

    def heal(self, resource_id):
        return "vnflcm/v1/vnf_instances/{resource_id}/heal".format(
            resource_id=resource_id)

    def upgrade(self, resource_id):
        return "vnflcm/v1/vnf_instances/{resource_id}/upgrade".format(
            resource_id=resource_id)

    def custom(self, resource_id, operation_name):
        return "vnflcm/v1/vnf_instances/{resource_id}/custom/{name}".format(
            resource_id=resource_id, name=operation_name)


class ExtensionAddress(object):
    @staticmethod
    def upgrade_baseline(resource_id):
        return "vnflcm/v1/vnf_instances/{resource_id}/upgrade_baseline".format(resource_id=resource_id)


class Headers(object):
    @staticmethod
    def accept_all():
        return {"Accept": "*/*"}

    @staticmethod
    def application_form_urlencoded():
        return {"Content-Type": "application/x-www-form-urlencoded"}

    @staticmethod
    def application_json():
        return {"Content-Type": "application/json"}

    @staticmethod
    def application_problem_json():
        return {"Content-Type": "application/problem+json"}

    @staticmethod
    def multipart_form_data():
        return {"Content-Type": "multipart/form-data"}

    @staticmethod
    def authorization(token):
        return {"Authorization": "bearer {token}".format(token=token)}


class UniformResponse(object):
    def __init__(self, raw):
        self.raw = raw
        self.prepare_content()
        self.status_code = self.raw.status_code
        self.headers = self.raw.headers

    def prepare_content(self):
        if Query(self.raw).is_one_of_headers_in(
            [Headers.application_problem_json(),
             Headers.application_json()]):
            self.content = self.raw.json()
        else:
            self.content = None

    def __stringify_headers__(self):
        output = ""
        for key, value in self.headers.items():
            output += key + ": " + value + "\n"
        return output

    def dump(self):
        return """
{title_sep}
 HTTP RESPONSE {status_code}
{title_sep}

{headers_sep}
{normal_sep}
 HEADERS
{normal_sep}
{headers}
{headers_sep}

{normal_sep}
 CONTENT
{normal_sep}
{content}
{normal_sep}
{raw}
        """.format(
            title_sep=("=" * 180),
            headers_sep=("+" * 180),
            normal_sep=("-" * 180),
            status_code=self.status_code,
            headers=self.__stringify_headers__(),
            content=(json.dumps(self.content, indent=2)
                     if self.content is not None else "NO CONTENT"),
            raw=self.raw.text)


class Query(object):
    def __init__(self, response):
        self.response = response

    def is_header_in(self, header):
        if self.response is None or self.response.headers is None:
            return False
        if isinstance(header, (list, )):
            return False
        if len(header.keys()) != 1:
            return False
        key = list(header.keys())[0]
        if isinstance(self.response.headers, (list, )):
            for response_header in self.response.headers:
                response_key = list(response_header.keys())[0]
                response_val = response_header[response_key]
                if key.lower() == response_key.lower(
                ) and response_val == header[key]:
                    return True
        else:
            for response_key, response_val in self.response.headers.items():
                if key.lower() == response_key.lower(
                ) and response_val == header[key]:
                    return True

        return False

    def is_one_of_headers_in(self, headers_list):
        if self.response is None:
            return False
        if headers_list is None:
            return False
        if not isinstance(headers_list, (list, )):
            return self.is_header_in(headers_list)
        for header in headers_list:
            if self.is_header_in(header):
                return True
        return False


class Utils(object):
    @staticmethod
    def resolve_if_remote_file(file_location):
        if not file_location:
            return file_location
        if not file_location.startswith("http://"):
            return file_location
        else:
            response = requests.get(file_location, stream=True)
            full_name = "{}-{}".format(uuid.uuid4(), file_location.split("/")[-1])
            with open("/tmp/" + full_name, 'wb') as file_handle:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        file_handle.write(chunk)
            return "/tmp/{}".format(full_name)

    @staticmethod
    def load_parameters(parameters_location):
        if isinstance(parameters_location, str):
            parameters = []
            if parameters_location.startswith("@") or parameters_location.endswith("@"):
                file_location = parameters_location.strip("@")
                if not Path(file_location).is_file():
                    raise InvalidConfiguration(
                        "Extra data file {file} does not exist".format(
                            file=file_location))
                try:
                    parameters = json.load(open(file_location, "rb"))
                except JSONDecodeError:
                    raise InvalidConfiguration(
                        "Extra data should be in JSON format")
            elif parameters_location.startswith("http://"):
                try:
                    result = requests.get(parameters_location)
                    parameters = result.json()
                except Exception:
                    raise InvalidConfiguration(
                        "Extra data should be in JSON format")
            else:
                try:
                    parameters = json.loads(parameters_location)
                except JSONDecodeError:
                    raise InvalidConfiguration(
                        "Extra data should be in JSON format")
            return parameters
        else:
            return parameters_location


class CbamApi(object):
    def __init__(self, base_address, client_id=None, client_secret=None, vnfm_api_version=None):
        self.base_address = base_address
        self.client_id = "cbam_restapi" if client_id is None else client_id
        self.client_secret = "924785d6-635a-4057-a9c5-2ddc43047f28" if client_secret is None else client_secret
        self.token = None
        self.verify = False
        self.version = "4" if vnfm_api_version is None else vnfm_api_version
        self.addresser = Address_v4() if self.version == "4" else Address_v3()

    def authenticate(self):
        headers = self.request_headers(
            include_required=False,
            additional=[
                Headers.accept_all(),
                Headers.application_form_urlencoded()
            ])
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        address = self.request_address(self.addresser.token())
        response = requests.post(
            address, data=data, headers=headers, verify=self.verify)
        if response.status_code == 200 and Query(response).is_header_in(
                Headers.application_json()):
            self.token = response.json()["access_token"]
        return UniformResponse(response)

    def read_vnf_lcm_operations(self, resource_id=None):
        headers = self.request_headers()
        address = self.request_address(self.addresser.vnf_lcm_operations(resource_id))
        with Auth(headers):
            response = requests.get(
                address, headers=headers, verify=self.verify)
            return UniformResponse(response)

    def read_vnf_lcm_operation(self, resource_id):
        headers = self.request_headers()
        address = self.request_address(self.addresser.vnf_lcm_operation(resource_id))
        with Auth(headers):
            response = requests.get(
                address, headers=headers, verify=self.verify)
            return UniformResponse(response)

    def read_vnf_packages(self):
        headers = self.request_headers()
        address = self.request_address(self.addresser.vnf_packages())
        with Auth(headers):
            response = requests.get(
                address, headers=headers, verify=self.verify)
            return UniformResponse(response)

    def create_vnf_package(self, file_location):
        headers = self.request_headers()
        address = self.request_address(self.addresser.vnf_packages())
        file_location = Utils.resolve_if_remote_file(file_location)
        with Auth(headers):
            response = requests.post(
                address,
                headers=headers,
                files=[("content", (open(file_location, "rb")))],
                verify=self.verify)
            return UniformResponse(response)

    def read_vnf_package(self, resource_id):
        headers = self.request_headers()
        address = self.request_address(self.addresser.vnf_package(resource_id))
        with Auth(headers):
            response = requests.get(
                address, headers=headers, verify=self.verify)
            return UniformResponse(response)

    def delete_vnf_package(self, resource_id):
        headers = self.request_headers()
        address = self.request_address(self.addresser.vnf_package(resource_id))
        with Auth(headers):
            response = requests.delete(
                address, headers=headers, verify=self.verify)
            return UniformResponse(response)

    def create_vnf(self, name, package_vnfd_id, description=None):
        headers = self.request_headers(additional=Headers.application_json())
        address = self.request_address(self.addresser.vnf_instances())
        with Auth(headers):
            response = requests.post(
                address,
                headers=headers,
                json={
                    "name": name,
                    "vnfdId": package_vnfd_id,
                    "description":
                    description if description is not None else ''
                },
                verify=self.verify)
            return UniformResponse(response)

    def read_vnf(self, resource_id):
        headers = self.request_headers()
        address = self.request_address(self.addresser.vnf_instance(resource_id))
        with Auth(headers):
            response = requests.get(
                address, headers=headers, verify=self.verify)
            return UniformResponse(response)

    def read_vnfs(self):
        headers = self.request_headers()
        address = self.request_address(self.addresser.vnf_instances())
        with Auth(headers):
            response = requests.get(
                address, headers=headers, verify=self.verify)
            return UniformResponse(response)

    def update_vnf(self, resource_id, json_data):
        headers = self.request_headers(additional=Headers.application_json())
        address = self.request_address(self.addresser.vnf_instance(resource_id))
        with Auth(headers):
            response = requests.patch(
                address, headers=headers, json=json_data, verify=self.verify)
            return UniformResponse(response)

    def delete_vnf(self, resource_id):
        headers = self.request_headers(additional=Headers.application_json())
        address = self.request_address(self.addresser.vnf_instance(resource_id))
        with Auth(headers):
            response = requests.delete(
                address, headers=headers, verify=self.verify)
            return UniformResponse(response)

    def instantiate(self, resource_id, json_data):
        headers = self.request_headers(additional=Headers.application_json())
        address = self.request_address(self.addresser.instantiate(resource_id))
        with Auth(headers):
            response = requests.post(
                address, headers=headers, json=json_data, verify=self.verify)
            return UniformResponse(response)

    def scale(self, resource_id, json_data):
        headers = self.request_headers(additional=Headers.application_json())
        address = self.request_address(self.addresser.scale(resource_id))
        with Auth(headers):
            response = requests.post(
                address, headers=headers, json=json_data, verify=self.verify)
            return UniformResponse(response)

    def terminate(self, resource_id, json_data):
        headers = self.request_headers(additional=Headers.application_json())
        address = self.request_address(self.addresser.terminate(resource_id))
        with Auth(headers):
            response = requests.post(
                address, headers=headers, json=json_data, verify=self.verify)
            return UniformResponse(response)

    def heal(self, resource_id, json_data):
        headers = self.request_headers(additional=Headers.application_json())
        address = self.request_address(self.addresser.heal(resource_id))
        with Auth(headers):
            response = requests.post(
                address, headers=headers, json=json_data, verify=self.verify)
            return UniformResponse(response)

    def upgrade(self, resource_id, json_data):
        headers = self.request_headers(additional=Headers.application_json())
        address = self.request_address(self.addresser.upgrade(resource_id))
        with Auth(headers):
            response = requests.post(
                address, headers=headers, json=json_data, verify=self.verify)
            return UniformResponse(response)

    def custom(self, resource_id, operation_name, json_data):
        headers = self.request_headers(additional=Headers.application_json())
        address = self.request_address(self.addresser.custom(resource_id, operation_name))
        with Auth(headers):
            response = requests.post(
                address, headers=headers, json=json_data, verify=self.verify)
            return UniformResponse(response)

    def read_upgrade_baseline(self, resource_id):
        headers = self.request_headers()
        address = self.request_address(ExtensionAddress.upgrade_baseline(resource_id))
        with Auth(headers):
            response = requests.get(
                address, headers=headers, verify=self.verify)
            return UniformResponse(response)

    def request_headers(self, include_required=True, additional=None):
        if include_required:
            merged = self.required_headers()
        else:
            merged = {}
        if additional is not None:
            if isinstance(additional, (list, )):
                for item in additional:
                    merged.update(item)
            else:
                merged.update(additional)
        return merged

    def required_headers(self):
        return Headers.authorization(self.token)

    def request_address(self, uri):
        return "{base_address}/{uri}".format(
            base_address=self.base_address, uri=uri)


class Executor(object):
    def __init__(self, args=None):
        self.args = args
        if args is not None:
            self.api = CbamApi(args.host, args.client_id, args.client_secret, args.version)

    def commands(self):
        commands = []
        for item in dir(self):
            if not item.startswith("__") and not item.startswith(
                    "validate") and item not in [
                        "commands", "args", "execute", "load_parameters"
                    ]:
                commands.append(item)
        return commands

    def execute(self):
        try:
            validate_method = getattr(
                self, "validate_{command}".format(command=self.args.command))
            validate_method()
        except AttributeError:
            pass
        command_method = getattr(self, self.args.command)
        return command_method()

    def load_parameters(self, action_name):
        if self.args.data is None:
            raise InvalidConfiguration(
                "Extra data parameter must to be provided for {action} action".
                format(action=action_name))

        self.parameters = []
        if self.args.data.startswith("@") or self.args.data.endswith("@"):
            file_location = self.args.data.strip("@")
            if not Path(file_location).is_file():
                raise InvalidConfiguration(
                    "Extra data file {file} does not exist".format(
                        file=file_location))
            try:
                self.parameters = json.load(open(file_location, "rb"))
            except JSONDecodeError:
                raise InvalidConfiguration(
                    "Extra data should be in JSON format")
        elif self.args.data.startswith("http://"):
            try:
                result = requests.get(self.args.data)
                self.parameters = result.json()
            except Exception:
                raise InvalidConfiguration(
                    "Extra data should be in JSON format")
        else:
            try:
                self.parameters = json.loads(self.args.data)
            except JSONDecodeError:
                raise InvalidConfiguration(
                    "Extra data should be in JSON format")

    def create_vnf_package(self):
        self.api.authenticate()
        return self.api.create_vnf_package(self.args.file)

    def validate_create_vnf_package(self):
        if self.args.file is None:
            raise InvalidConfiguration(
                "File must be provided for create_vnf_package action")
        if not self.args.file.startswith("http://") and not Path(self.args.file).is_file():
            raise InvalidConfiguration(
                "File '{file}' does not exist".format(file=self.args.file))

    def read_vnf_lcm_operations(self):
        self.api.authenticate()
        return self.api.read_vnf_lcm_operations(self.args.resource_id)

    def validate_read_vnf_lcm_operations(self):
        if int(self.api.version) == 3 and self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for read_vnf_lcm_operations for VNFM API version 3")

    def read_vnf_packages(self):
        self.api.authenticate()
        return self.api.read_vnf_packages()

    def read_vnf_package(self):
        self.api.authenticate()
        return self.api.read_vnf_package(self.args.resource_id)

    def validate_read_vnf_package(self):
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for read_vnf_package action")

    def read_vnf_lcm_operation(self):
        self.api.authenticate()
        return self.api.read_vnf_lcm_operation(self.args.resource_id)

    def validate_read_vnf_lcm_operation(self):
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for read_vnf_lcm_operation action")

    def delete_vnf_package(self):
        self.api.authenticate()
        return self.api.delete_vnf_package(self.args.resource_id)

    def validate_delete_vnf_package(self):
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for delete_vnf_package action")

    def create_vnf(self):
        self.api.authenticate()
        return self.api.create_vnf(self.parameters["name"],
                                   self.parameters["vnfdId"],
                                   self.parameters["description"])

    def validate_create_vnf(self):
        self.load_parameters("create_vnf")
        if "name" not in self.parameters:
            raise InvalidConfiguration(
                "Extra data should contain 'name' parameter")
        if "vnfdId" not in self.parameters:
            raise InvalidConfiguration(
                "Extra data should contain 'vnfdId' parameter - vnf catalogue package identifier"
            )
        if "description" not in self.parameters:
            self.parameters["description"] = None

    def read_vnfs(self):
        self.api.authenticate()
        return self.api.read_vnfs()

    def read_vnf(self):
        self.api.authenticate()
        return self.api.read_vnf(self.args.resource_id)

    def validate_read_vnf(self):
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for read_vnf action")

    def update_vnf(self):
        self.api.authenticate()
        return self.api.update_vnf(self.args.resource_id, self.parameters)

    def validate_update_vnf(self):
        self.load_parameters("update_vnf")
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for update_vnf action")

    def delete_vnf(self):
        self.api.authenticate()
        return self.api.delete_vnf(self.args.resource_id)

    def validate_delete_vnf(self):
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for delete_vnf action")

    def instantiate(self):
        self.api.authenticate()
        return self.api.instantiate(self.args.resource_id, self.parameters)

    def validate_instantiate(self):
        self.load_parameters("instantiate")
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for instantiate action")

    def scale(self):
        self.api.authenticate()
        return self.api.scale(self.args.resource_id, self.parameters)

    def validate_scale(self):
        self.load_parameters("scale")
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for scale action")

    def terminate(self):
        self.api.authenticate()
        return self.api.terminate(self.args.resource_id, self.parameters)

    def validate_terminate(self):
        self.load_parameters("terminate")
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for terminate action")

    def heal(self):
        self.api.authenticate()
        return self.api.heal(self.args.resource_id, self.parameters)

    def validate_heal(self):
        self.load_parameters("heal")
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for heal action")

    def upgrade(self):
        self.api.authenticate()
        return self.api.upgrade(self.args.resource_id, self.parameters)

    def validate_upgrade(self):
        self.load_parameters("upgrade")
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for upgrade action")

    def custom(self):
        self.api.authenticate()
        return self.api.custom(self.args.resource_id, self.args.operation_name, self.parameters)

    def validate_custom(self):
        self.load_parameters("custom")
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for custom action")
        if self.args.operation_name is None:
            raise InvalidConfiguration(
                "Operation name must be provided for custom action")

    def read_upgrade_baseline(self):
        self.api.authenticate()
        return self.api.read_upgrade_baseline(self.args.resource_id)

    def validate_read_upgrade_baseline(self):
        if int(self.args.version) < 4:
            raise InvalidConfiguration(
                "This command is allowed from VNFM API version 4")
        if self.args.resource_id is None:
            raise InvalidConfiguration(
                "Resource id must be provided for read_upgrade_baseline action")


def parser():
    parser = argparse.ArgumentParser(description="CBAM cli")
    parser.add_argument(
        "-v", "--version", help="VNFM API version", choices={'3', '4'}, default="3")
    parser.add_argument(
        "-f", "--file", help="VNF package file to upload", default=None)
    parser.add_argument(
        "-u",
        "--host",
        help="CBAM host address, http[s]://host[:port]",
        default=None)
    parser.add_argument("-cid", "--client-id", help="Client id", default=None)
    parser.add_argument(
        "-s", "--client-secret", help="Client secret", default=None)
    parser.add_argument(
        "-rid", "--resource-id", help="Resource id", default=None)
    parser.add_argument(
        "-o", "--operation-name", help="Operation name", default=None)
    parser.add_argument(
        "-d",
        "--data",
        help="JSON extra data, use @ to pass file instead of inline definition",
        default=None)
    parser.add_argument(
        "command", help="Command to execute", choices=Executor().commands())
    return parser


def validate_required_params(args):
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


def get_args():
    args = parser().parse_args()
    validate_required_params(args)
    return args


if __name__ == "__main__":
    args = get_args()
    executor_response = Executor(args).execute()
    print(executor_response.dump())
