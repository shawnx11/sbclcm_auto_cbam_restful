import unittest
import requests

from unittest.mock import patch, Mock
from cbam_api import CbamApi, Address, ExtensionAddress, InvalidAuthorizationHeader, InvalidConfiguration, Executor, Query, Headers, Utils
from cbam_api import validate_required_params

from cbam_api_robot import Create_VNF_Package, Read_VNF_Packages, Read_VNF_Package, Delete_VNF_Package, Read_VNF, Create_VNF, Update_VNF, Delete_VNF, Instantiate, Scale, Terminate, Heal, Upgrade, Custom, Read_Upgrade_Baseline, Read_VNF_LCM_Operations, Read_VNF_LCM_Operation, Read_VNFs, Wait_For_Operation_To_Complete, Find_VNF_LCM_Operations_By_Name


class FakeRequestsResponse(object):
    def __init__(self, response, headers=[], status_code=200):
        self.response = response
        self.status_code = status_code
        self.headers = headers

    def json(self):
        return self.response

    def status_code(self):
        return self.status_code


class FakeArgs(object):
    host = None
    client_id = None
    client_secret = None
    command = None
    file = None
    data = None
    operation_name = None


class FakeHeaders(object):
    def __init__(self, headers):
        self.headers = headers


class FakeFactory(object):
    @staticmethod
    def fake_headers():
        return FakeHeaders({
            "Set-Cookie":
            "KC_RESTART=; Version=1; Expires=Thu, 01-Jan-1970 00:00:10 GMT; Max-Age=0; Path=/auth/realms/cbam/; Secure; HttpOnly",
            "Content-Type":
            "application/json",
            "Content-Length":
            "3316",
            "Date":
            "Wed, 20 Mar 2019 09:45:05 GMT",
            "Cache-Control":
            "no-cache, no-store, must-revalidate",
            "Pragma":
            "no-cache",
            "X-XSS-Protection":
            "1",
            "X-Content-Type-Options":
            "nosniff",
            "X-Frame-Options":
            "SAMEORIGIN",
            "Content-Security-Policy":
            "default-src 'self';font-src 'self' data:;img-src 'self' data:;script-src 'unsafe-inline' 'unsafe-eval' 'self';style-src 'unsafe-inline' 'self';"
        })

    @staticmethod
    def fake_args(name=None):
        args = FakeArgs()
        args.host = "https://host"
        args.client_id = "cbam_restapi"
        args.client_secret = "secret"
        args.command = name if name is not None else None
        args.resource_id = None
        return args

    @staticmethod
    def fake_read_vnf_packages_response():
        return FakeRequestsResponse([{
            "@type":
            "catalog_adapter_vnfpackage",
            "id":
            "83",
            "links":
            [{
                "@href":
                "/api/catalog/adapter/vnfpackages/Nokia-SBC-media-C190B01-SBC-C190B01",
                "@method": "delete",
                "@rel": "delete"
            },
             {
                 "@href":
                 "/api/catalog/adapter/vnfpackages/Nokia-SBC-media-C190B01-SBC-C190B01",
                 "@method": "get",
                 "@rel": "getById"
             },
             {
                 "@href":
                 "/api/catalog/adapter/vnfpackages/Nokia-SBC-media-C190B01-SBC-C190B01/addusagereference",
                 "@method": "post",
                 "@rel": "addusagereference"
             },
             {
                 "@href": "/api/catalog/adapter/import",
                 "@method": "post",
                 "@rel": "importVnf"
             },
             {
                 "@href":
                 "/api/catalog/adapter/vnfpackages/Nokia-SBC-media-C190B01-SBC-C190B01/content",
                 "@method": "get",
                 "@rel": "content"
             },
             {
                 "@href":
                 "/api/catalog/adapter/export/Nokia-SBC-media-C190B01-SBC-C190B01",
                 "@method": "get",
                 "@rel": "exportOneVnf"
             },
             {
                 "@href": "/api/catalog/adapter/export",
                 "@method": "get",
                 "@rel": "exportAllVnfs"
             },
             {
                 "@href":
                 "/api/catalog/adapter/vnfpackages/Nokia-SBC-media-C190B01-SBC-C190B01/removeusagereference",
                 "@method": "post",
                 "@rel": "removeusagereference"
             },
             {
                 "@href": "/api/catalog/adapter/vnfpackages",
                 "@method": "get",
                 "@rel": "list"
             },
             {
                 "@href": "/api/catalog/adapter/vnfpackages",
                 "@method": "post",
                 "@rel": "create"
             }],
            "name":
            "Nokia-SBC-media-C190B01-SBC-C190B01",
            "productName":
            "SBC-media",
            "provider":
            "Nokia",
            "references": [],
            "swVersion":
            "C190B01",
            "version":
            "SBC-C190B01",
            "vimType":
            "openstack",
            "vnfdId":
            "Nokia-SBC-media-C190B01-SBC-C190B01"
        }],
                                    headers=[{
                                        "content-type": "application/json"
                                    }])

    @staticmethod
    def fake_read_vnf_lcm_operation_response():
        return FakeRequestsResponse({
            "vnfInstanceId":
            "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
            "additionalData": {
                "requestId": "8acce9dfcd58441499d8eca08eb63492",
                "operationResult": {}
            },
            "isCancelPending":
            "false",
            "isAutomaticInvocation":
            "false",
            "operationState":
            "PROCESSING",
            "_links": {
                "vnfInstance": {
                    "href":
                    "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                },
                "cancel": {
                    "href":
                    "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-230d76431c0d41cd9c66e2283dede78a/cancel"
                },
                "self": {
                    "href":
                    "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-230d76431c0d41cd9c66e2283dede78a"
                },
                "list": {
                    "href": "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                }
            },
            "startTime":
            "2019-04-05T09:35:26.907082Z",
            "stateEnteredTime":
            "2019-04-05T09:35:26.907082Z",
            "operation":
            "INSTANTIATE",
            "id":
            "CBAM-230d76431c0d41cd9c66e2283dede78a"
        },
                                    headers=[{
                                        'content-type': 'application/json'
                                    }])

    @staticmethod
    def fake_read_vnf_lcm_operations_response():
        return FakeRequestsResponse([
            {
                "vnfInstanceId": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "additionalData": {
                    "requestId": "8acce9dfcd58441499d8eca08eb63492",
                    "operationResult": {}
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationState": "PROCESSING",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "cancel": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-230d76431c0d41cd9c66e2283dede78a/cancel"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-230d76431c0d41cd9c66e2283dede78a"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-05T09:35:26.907082Z",
                "stateEnteredTime": "2019-04-05T09:35:26.907082Z",
                "operation": "INSTANTIATE",
                "id": "CBAM-230d76431c0d41cd9c66e2283dede78a"
            },
            {
                "vnfInstanceId": "CBAM-9cb609fc5ff64821b037d8ad0fc22423",
                "additionalData": {
                    "requestId": "73eb3d61164f4bb68548186405c40ef2"
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationName": "custom:backup",
                "operationState": "COMPLETED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-9cb609fc5ff64821b037d8ad0fc22423"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-d85b9bf9ae834f569ed6b951452b6d51"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-12T08:38:47.013784Z",
                "stateEnteredTime": "2019-04-12T08:39:30.368040Z",
                "operation": "OTHER",
                "id": "CBAM-d85b9bf9ae834f569ed6b951452b6d51"
            },
            {
                "vnfInstanceId": "CBAM-9cb609fc5ff64821b037d8ad0fc22423",
                "additionalData": {
                    "requestId": "73eb3d61164f4bb68548186405c40ef2"
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationName": "custom:backup",
                "operationState": "COMPLETED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-9cb609fc5ff64821b037d8ad0fc22423"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-d85b9bf9ae834f569ed6b951452b6d51"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-12T10:38:47.013784Z",
                "stateEnteredTime": "2019-04-12T08:39:30.368040Z",
                "operation": "OTHER",
                "id": "CBAM-d85b9bf9ae834f569ed6b951452b1111"
            },
            {
                "vnfInstanceId": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "additionalData": {
                    "requestId": "61e189723039445583b0324191fb3509"
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationState": "COMPLETED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-3148f6fa02b24a58a4fbab918e14e98a"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-05T09:32:09.868572Z",
                "stateEnteredTime": "2019-04-05T09:34:42.311548Z",
                "operation": "TERMINATE",
                "id": "CBAM-3148f6fa02b24a58a4fbab918e14e98a"
            },
            {
                "vnfInstanceId": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "additionalData": {
                    "requestId": "64cf352172d644c09e825ac53eb4d313",
                    "operationResult": {}
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationState": "COMPLETED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-68e45d5aa41449a39d1d5c9dd090b1bf"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-05T08:54:17.531711Z",
                "stateEnteredTime": "2019-04-05T09:14:33.813983Z",
                "operation": "INSTANTIATE",
                "id": "CBAM-68e45d5aa41449a39d1d5c9dd090b1bf"
            },
            {
                "vnfInstanceId": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "additionalData": {
                    "requestId": "2d9d7c5fd5e749c686f4df44a3f41090"
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationState": "COMPLETED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-37c59028ee4840f2a6d3973ac30b296f"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-05T08:52:27.259526Z",
                "stateEnteredTime": "2019-04-05T08:54:06.738200Z",
                "operation": "TERMINATE",
                "id": "CBAM-37c59028ee4840f2a6d3973ac30b296f"
            },
            {
                "vnfInstanceId": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "additionalData": {
                    "requestId": "eb0aa3a564564875b2ddde2ec6989b50",
                    "operationResult": {}
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationState": "COMPLETED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-fb2c1dc5e55c4082a50225fa1a239ca6"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-12T10:07:32.779434Z",
                "stateEnteredTime": "2019-04-05T08:50:12.104544Z",
                "operation": "INSTANTIATE",
                "id": "CBAM-fb2c1dc5e55c4082a50225fa1a239ca6"
            },
            {
                "vnfInstanceId": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "additionalData": {
                    "requestId": "072757435b564a6d8417e53fa55727cc"
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationState": "COMPLETED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-f6f54c4a83034842be3bcac8375dbd0c"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-05T08:33:52.688014Z",
                "stateEnteredTime": "2019-04-05T08:34:26.173449Z",
                "operation": "TERMINATE",
                "id": "CBAM-f6f54c4a83034842be3bcac8375dbd0c"
            },
            {
                "vnfInstanceId": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "additionalData": {
                    "requestId": "5715436db57247f5b5437229a95ea675",
                    "operationResult": {}
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationState": "FAILED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-67145af2357541cb8248fc5a10c8fb91"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-05T08:31:54.308120Z",
                "stateEnteredTime": "2019-04-05T08:32:45.983360Z",
                "operation": "INSTANTIATE",
                "id": "CBAM-67145af2357541cb8248fc5a10c8fb91"
            },
            {
                "vnfInstanceId": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "additionalData": {
                    "requestId": "063ddc0634234513992e62485f85d5f3"
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationState": "FAILED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-17ee99cef23742f68df7148342f7a693"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-05T08:30:07.327244Z",
                "stateEnteredTime": "2019-04-05T08:30:16.974985Z",
                "operation": "INSTANTIATE",
                "id": "CBAM-17ee99cef23742f68df7148342f7a693"
            },
            {
                "vnfInstanceId": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "additionalData": {
                    "requestId": "d452aa99062240d49daeb5a798ef5178"
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationState": "COMPLETED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-79187c1f07f44cad9b056fef32b30754"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-05T07:49:48.291387Z",
                "stateEnteredTime": "2019-04-05T07:51:49.699119Z",
                "operation": "TERMINATE",
                "id": "CBAM-79187c1f07f44cad9b056fef32b30754"
            },
            {
                "vnfInstanceId": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "additionalData": {
                    "requestId": "ed9d97ceb96943efb310f2443f65e218",
                    "operationResult": {}
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationState": "COMPLETED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-abe5846cbb5942ac831a846a6c2433af"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-05T07:23:50.725426Z",
                "stateEnteredTime": "2019-04-05T07:44:37.712664Z",
                "operation": "INSTANTIATE",
                "id": "CBAM-abe5846cbb5942ac831a846a6c2433af"
            },
            {
                "vnfInstanceId": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "additionalData": {
                    "requestId": "fa4acbe464d5492bb0781d56d483f8be"
                },
                "isCancelPending": "false",
                "isAutomaticInvocation": "false",
                "operationState": "COMPLETED",
                "_links": {
                    "vnfInstance": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs/CBAM-98185499a961404ba13abdcc60f77503"
                    },
                    "list": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_lcm_op_occs"
                    }
                },
                "startTime": "2019-04-05T07:21:47.260238Z",
                "stateEnteredTime": "2019-04-05T07:21:47.260238Z",
                "operation": "MODIFY_INFO",
                "id": "CBAM-98185499a961404ba13abdcc60f77503"
            }
        ],
                                    headers=[{
                                        'content-type': 'application/json'
                                    }])

    @staticmethod
    def fake_read_vnf_package_response():
        return FakeRequestsResponse({
            "@type":
            "catalog_adapter_vnfpackage",
            "id":
            "83",
            "links":
            [{
                "@href":
                "/api/catalog/adapter/vnfpackages/Nokia-SBC-media-C190B01-SBC-C190B01",
                "@method": "delete",
                "@rel": "delete"
            },
             {
                 "@href":
                 "/api/catalog/adapter/vnfpackages/Nokia-SBC-media-C190B01-SBC-C190B01",
                 "@method": "get",
                 "@rel": "getById"
             },
             {
                 "@href":
                 "/api/catalog/adapter/vnfpackages/Nokia-SBC-media-C190B01-SBC-C190B01/addusagereference",
                 "@method": "post",
                 "@rel": "addusagereference"
             },
             {
                 "@href": "/api/catalog/adapter/import",
                 "@method": "post",
                 "@rel": "importVnf"
             },
             {
                 "@href":
                 "/api/catalog/adapter/vnfpackages/Nokia-SBC-media-C190B01-SBC-C190B01/content",
                 "@method": "get",
                 "@rel": "content"
             },
             {
                 "@href":
                 "/api/catalog/adapter/export/Nokia-SBC-media-C190B01-SBC-C190B01",
                 "@method": "get",
                 "@rel": "exportOneVnf"
             },
             {
                 "@href": "/api/catalog/adapter/export",
                 "@method": "get",
                 "@rel": "exportAllVnfs"
             },
             {
                 "@href":
                 "/api/catalog/adapter/vnfpackages/Nokia-SBC-media-C190B01-SBC-C190B01/removeusagereference",
                 "@method": "post",
                 "@rel": "removeusagereference"
             },
             {
                 "@href": "/api/catalog/adapter/vnfpackages",
                 "@method": "get",
                 "@rel": "list"
             },
             {
                 "@href": "/api/catalog/adapter/vnfpackages",
                 "@method": "post",
                 "@rel": "create"
             }],
            "name":
            "Nokia-SBC-media-C190B01-SBC-C190B01",
            "productName":
            "SBC-media",
            "provider":
            "Nokia",
            "references": [],
            "swVersion":
            "C190B01",
            "version":
            "SBC-C190B01",
            "vimType":
            "openstack",
            "vnfdId":
            "Nokia-SBC-media-C190B01-SBC-C190B01"
        },
                                    headers=[{
                                        "content-type": "application/json"
                                    }])

    @staticmethod
    def fake_read_vnf_response():
        return FakeRequestsResponse({
            "_links": {
                "custom:Post_Disaster_Recovery": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422/custom/Post_Disaster_Recovery"
                },
                "custom:backout": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422/custom/backout"
                },
                "custom:backup": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422/custom/backup"
                },
                "custom:issu": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422/custom/issu"
                },
                "custom:nssu": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422/custom/nssu"
                },
                "custom:register_lcm_user": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422/custom/register_lcm_user"
                },
                "custom:restore": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422/custom/restore"
                },
                "custom:rollback": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422/custom/rollback"
                },
                "custom:unregister_lcm_user": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422/custom/unregister_lcm_user"
                },
                "custom:update_lcm_admin_user": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422/custom/update_lcm_admin_user"
                },
                "delete": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422"
                },
                "instantiate": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422/instantiate"
                },
                "list": {
                    "href": "https://10.15.170.118/vnflcm/v1/vnf_instances"
                },
                "modifyInfo": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422"
                },
                "self": {
                    "href":
                    "https://10.15.170.118/vnflcm/v1/vnf_instances/CBAM-3e7b5babe49d4ae598d3d55326486422"
                }
            },
            "extensions": {
                "default_action": "none",
                "lcm_admin_user": "cloud-user",
                "mcm_scale_in_threshold": "30",
                "mcm_scale_out_threshold": "70",
                "media_params": "none",
                "minimum_configuration": "[]",
                "pim_scale_in_threshold": "30",
                "pim_scale_out_threshold": "70",
                "quiet_period": "900",
                "resource_backup": "none",
                "vdus_backup": "none"
            },
            "id": "CBAM-3e7b5babe49d4ae598d3d55326486422",
            "instantiationState": "NOT_INSTANTIATED",
            "metadata": {},
            "vimConnectionInfo": [],
            "vnfConfigurableProperties": {
                "operation_triggers": {
                    "auto_scale": {
                        "enabled": "false",
                        "periodInSeconds": 300
                    }
                }
            },
            "vnfInstanceName": "CBAM-3e7b5babe49d4ae598d3d55326486422",
            "vnfPkgId": "Nokia-SBC-media-C190B01-SBC-C190B01",
            "vnfProductName": "SBC-media",
            "vnfProvider": "Nokia",
            "vnfSoftwareVersion": "C190B01",
            "vnfdId": "Nokia-SBC-media-C190B01-SBC-C190B01",
            "vnfdVersion": "SBC-C190B01"
        },
                                    headers=[{
                                        "content-type": "application/json"
                                    }])

    @staticmethod
    def fake_read_vnfs_response():
        return FakeRequestsResponse(
            [{
                "vnfInstanceName": "CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                "vnfProductName": "SBC-media",
                "vnfSoftwareVersion": "C190B01",
                "instantiationState": "INSTANTIATED",
                "vnfProvider": "Nokia",
                "vnfdId": "Nokia-SBC-media-C190B01-default",
                "_links": {
                    "custom:rollback": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/custom/rollback"
                    },
                    "upgrade": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/upgrade"
                    },
                    "custom:backup": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/custom/backup"
                    },
                    "custom:nssu": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/custom/nssu"
                    },
                    "list": {
                        "href": "https://10.75.168.52/vnflcm/v1/vnf_instances"
                    },
                    "self": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "terminate": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/terminate"
                    },
                    "custom:issu": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/custom/issu"
                    },
                    "custom:backout": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/custom/backout"
                    },
                    "modifyInfo": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee"
                    },
                    "custom:Post_Disaster_Recovery": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/custom/Post_Disaster_Recovery"
                    },
                    "scale": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/scale"
                    },
                    "custom:register_lcm_user": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/custom/register_lcm_user"
                    },
                    "custom:unregister_lcm_user": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/custom/unregister_lcm_user"
                    },
                    "custom:update_lcm_admin_user": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/custom/update_lcm_admin_user"
                    },
                    "heal": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/heal"
                    },
                    "custom:restore": {
                        "href":
                        "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-e8bd1ab2c233453389aceb6b12e7caee/custom/restore"
                    }
                },
                "vnfdVersion": "default",
                "vnfPkgId": "Nokia-SBC-media-C190B01-default",
                "id": "CBAM-e8bd1ab2c233453389aceb6b12e7caee"
            },
             {
                 "vnfInstanceName": "CBAM-d8c148f57f674296bf07d33b9793dfeb",
                 "vnfProductName": "SBC-media",
                 "vnfSoftwareVersion": "C190B01",
                 "instantiationState": "NOT_INSTANTIATED",
                 "vnfProvider": "Nokia",
                 "vnfdId": "Nokia-SBC-media-C190B01-SBC-C190B01",
                 "_links": {
                     "custom:rollback": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb/custom/rollback"
                     },
                     "custom:update_lcm_admin_user": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb/custom/update_lcm_admin_user"
                     },
                     "custom:backup": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb/custom/backup"
                     },
                     "custom:nssu": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb/custom/nssu"
                     },
                     "self": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb"
                     },
                     "instantiate": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb/instantiate"
                     },
                     "list": {
                         "href": "https://10.75.168.52/vnflcm/v1/vnf_instances"
                     },
                     "custom:issu": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb/custom/issu"
                     },
                     "custom:backout": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb/custom/backout"
                     },
                     "modifyInfo": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb"
                     },
                     "custom:Post_Disaster_Recovery": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb/custom/Post_Disaster_Recovery"
                     },
                     "custom:register_lcm_user": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb/custom/register_lcm_user"
                     },
                     "custom:restore": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb/custom/restore"
                     },
                     "custom:unregister_lcm_user": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb/custom/unregister_lcm_user"
                     },
                     "delete": {
                         "href":
                         "https://10.75.168.52/vnflcm/v1/vnf_instances/CBAM-d8c148f57f674296bf07d33b9793dfeb"
                     }
                 },
                 "vnfdVersion": "SBC-C190B01",
                 "vnfPkgId": "Nokia-SBC-media-C190B01-SBC-C190B01",
                 "id": "CBAM-d8c148f57f674296bf07d33b9793dfeb"
             }],
            headers=[{
                "content-type": "application/json"
            }])


class TestCbamApi(unittest.TestCase):
    def setUp(self):
        self.base_address = "https://10.15.170.118"
        self.cbam_api = CbamApi(self.base_address)

    def test_default(self):
        self.assertEqual(self.cbam_api.client_id, "cbam_restapi")
        self.assertEqual(self.cbam_api.client_secret,
                         "244181d7-1f01-4937-9a22-b83372cbf778")
        cbam_custom_user = CbamApi(self.base_address, "rest_user",
                                   "rest_password")
        self.assertEqual(cbam_custom_user.client_id, "rest_user")
        self.assertEqual(cbam_custom_user.client_secret, "rest_password")

    def test_request_address(self):
        self.assertEqual(
            self.cbam_api.request_address(Address.token()),
            "{base}/auth/realms/cbam/protocol/openid-connect/token".format(
                base=self.base_address))
        self.assertEqual(
            self.cbam_api.request_address(Address.vnf_packages()),
            "{base}/api/catalog/adapter/vnfpackages".format(
                base=self.base_address))
        self.assertEqual(
            self.cbam_api.request_address(Address.vnf_package("test-vnfdId")),
            "{base}/api/catalog/adapter/vnfpackages/test-vnfdId".format(
                base=self.base_address))
        self.assertEqual(
            self.cbam_api.request_address(Address.vnf_instances()),
            "{base}/vnflcm/v1/vnf_instances".format(base=self.base_address))
        self.assertEqual(
            self.cbam_api.request_address(Address.vnf_instance("test-id")),
            "{base}/vnflcm/v1/vnf_instances/test-id".format(
                base=self.base_address))

    def test_request_headers(self):
        try:
            self.cbam_api.request_headers()["Authorization"]
            headers = self.cbam_api.request_headers(
                additional={"Test": "Value"})
            auth = headers["Authorization"]
            test = headers["Test"]
            self.assertEqual(auth, "bearer None")
            self.assertEqual(test, "Value")
            headers = self.cbam_api.request_headers(
                additional={"Authorization": "MyVal"})
            self.assertEqual(headers["Authorization"], "MyVal")
        except KeyError:
            self.fail()
        headers = self.cbam_api.request_headers(
            additional=[{
                "SuperTest": "SuperValue"
            }, {
                "SuperTest2": "SuperValue2"
            }])
        self.assertEqual(headers["SuperTest"], "SuperValue")
        self.assertEqual(headers["SuperTest2"], "SuperValue2")
        self.assertNotEqual(headers["Authorization"], None)

    @patch("builtins.open")
    @patch("cbam_api.requests")
    def test_auth_guard(self, mocked_requests, mocked_os):
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.create_vnf_package(None)

        cbam_api_two = CbamApi(self.base_address)
        cbam_api_two.token = "rf6das789698gas"
        cbam_api_two.create_vnf_package(None)
        mocked_requests.post.assert_called()

    @patch("cbam_api.os")
    def test_validate(self, mocked_os):
        fake_args = FakeArgs()
        mocked_os.environ = []
        with self.assertRaisesRegex(InvalidConfiguration,
                                    "Host must be provided"):
            validate_required_params(fake_args)

        mocked_os.environ = {"CBAM_HOST": self.base_address}
        with self.assertRaisesRegex(InvalidConfiguration,
                                    "Client ID must be provided"):
            validate_required_params(fake_args)

        mocked_os.environ["CBAM_CLIENT_ID"] = "cbam_restapi"
        with self.assertRaisesRegex(InvalidConfiguration,
                                    "Client secret must be provided"):
            validate_required_params(fake_args)

        mocked_os.environ["CBAM_CLIENT_SECRET"] = "secret"
        validate_required_params(fake_args)

    @patch("cbam_api.requests")
    def test_authenticate(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "SuperToken123"})
        self.cbam_api.authenticate()
        mocked_requests.post.assert_called()
        self.assertEqual(self.cbam_api.token, None)
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "SuperToken123"},
            headers=[{
                "content-type": "application/json"
            }])
        self.cbam_api.authenticate()
        mocked_requests.post.assert_called()
        self.assertEqual(self.cbam_api.token, "SuperToken123")

    @patch("builtins.open")
    @patch("cbam_api.requests")
    def test_create_vnf_package(self, mocked_requests, mocked_os):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, headers=[{
                "content-type": "application/json"
            }])
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.create_vnf_package(None)
        self.cbam_api.token = "blah"
        result = self.cbam_api.create_vnf_package(None)
        mocked_requests.post.assert_called()
        self.assertTrue("id" in result.content)

    @patch("builtins.open")
    @patch("cbam_api.requests")
    def test_read_vnf_packages(self, mocked_requests, mocked_os):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, headers=[{
                "content-type": "application/json"
            }])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_packages_response(
        )

        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.read_vnf_packages()
        self.cbam_api.token = "blah"
        result = self.cbam_api.read_vnf_packages()
        mocked_requests.get.assert_called()
        self.assertEqual(1, len(result.content))
        self.assertEqual("83", result.content[0]["id"])

    @patch("builtins.open")
    @patch("cbam_api.requests")
    def test_read_vnfs(self, mocked_requests, mocked_os):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, headers=[{
                "content-type": "application/json"
            }])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnfs_response(
        )

        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.read_vnfs()
        self.cbam_api.token = "blah"
        result = self.cbam_api.read_vnfs()
        mocked_requests.get.assert_called()
        self.assertEqual(2, len(result.content))
        self.assertEqual("CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                         result.content[0]["vnfInstanceName"])

    @patch("builtins.open")
    @patch("cbam_api.requests")
    def test_read_vnf_lcm_operations(self, mocked_requests, mocked_os):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, headers=[{
                "content-type": "application/json"
            }])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_lcm_operations_response(
        )

        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.read_vnf_packages()
        self.cbam_api.token = "blah"
        result = self.cbam_api.read_vnf_lcm_operations()
        mocked_requests.get.assert_called()
        self.assertEqual(13, len(result.content))
        self.assertEqual("CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                         result.content[0]["vnfInstanceId"])
        self.assertEqual("PROCESSING", result.content[0]["operationState"])

    @patch("builtins.open")
    @patch("cbam_api.requests")
    def test_read_vnf_package(self, mocked_requests, mocked_os):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, headers=[{
                "content-type": "application/json"
            }])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_package_response(
        )

        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.read_vnf_package(
                "Nokia-SBC-media-C190B01-SBC-C190B01")
        self.cbam_api.token = "blah"
        result = self.cbam_api.read_vnf_package(
            "Nokia-SBC-media-C190B01-SBC-C190B01")
        mocked_requests.get.assert_called()
        self.assertTrue("Nokia-SBC-media-C190B01-SBC-C190B01" in
                        mocked_requests.get.call_args[0][0])
        self.assertEqual("Nokia-SBC-media-C190B01-SBC-C190B01",
                         result.content["vnfdId"])

    @patch("builtins.open")
    @patch("cbam_api.requests")
    def test_read_vnf_lcm_operation(self, mocked_requests, mocked_os):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, headers=[{
                "content-type": "application/json"
            }])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_lcm_operation_response(
        )

        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.read_vnf_lcm_operation(
                "CBAM-230d76431c0d41cd9c66e2283dede78a")
        self.cbam_api.token = "blah"
        result = self.cbam_api.read_vnf_lcm_operation(
            "CBAM-230d76431c0d41cd9c66e2283dede78a")
        mocked_requests.get.assert_called()
        self.assertTrue("CBAM-230d76431c0d41cd9c66e2283dede78a" in
                        mocked_requests.get.call_args[0][0])
        self.assertEqual("CBAM-230d76431c0d41cd9c66e2283dede78a",
                         result.content["id"])

    @patch("builtins.open")
    @patch("cbam_api.requests")
    def test_delete_vnf_package(self, mocked_requests, mocked_os):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, headers=[{
                "content-type": "application/json"
            }])
        mocked_requests.delete.return_value = FakeRequestsResponse(
            None,
            status_code=204,
            headers=[{
                "content-type": "application/json"
            }])

        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.delete_vnf_package(
                "Nokia-SBC-media-C190B01-SBC-C190B01")
        self.cbam_api.token = "blah"
        result = self.cbam_api.delete_vnf_package(
            "Nokia-SBC-media-C190B01-SBC-C190B01")
        mocked_requests.delete.assert_called()
        self.assertTrue("Nokia-SBC-media-C190B01-SBC-C190B01" in
                        mocked_requests.delete.call_args[0][0])
        self.assertEqual(204, result.status_code)

    @patch("cbam_api.requests")
    def test_create_vnf(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, headers=[{
                "content-type": "application/json"
            }])
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.create_vnf("test", "test-id", "test-desc")
        self.cbam_api.token = "blah"
        result = self.cbam_api.create_vnf("test", "test-id", "test-desc")
        mocked_requests.post.assert_called()
        self.assertEqual(mocked_requests.post.call_args[1]["json"], {
            "name": "test",
            "vnfdId": "test-id",
            "description": "test-desc"
        })
        self.assertTrue("id" in result.content)

    @patch("cbam_api.requests")
    def test_update_vnf(self, mocked_requests):
        mocked_requests.patch.return_value = FakeRequestsResponse(
            {"id": "1234"}, status_code=202)
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.update_vnf("test", {"testKey": "testValue"})
        self.cbam_api.token = "blah"
        result = self.cbam_api.update_vnf("test-resource-id",
                                          {"testKey": "testValue"})
        mocked_requests.patch.assert_called()
        self.assertEqual(mocked_requests.patch.call_args[1]["json"],
                         {"testKey": "testValue"})
        self.assertTrue(
            "test-resource-id" in mocked_requests.patch.call_args[0][0])
        self.assertEqual(result.status_code, 202)

    @patch("cbam_api.requests")
    def test_delete_vnf(self, mocked_requests):
        mocked_requests.delete.return_value = FakeRequestsResponse(
            {"id": "1234"}, status_code=204)
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.delete_vnf("test")
        self.cbam_api.token = "blah"
        result = self.cbam_api.delete_vnf("test-resource-id")
        mocked_requests.delete.assert_called()
        self.assertTrue(
            "test-resource-id" in mocked_requests.delete.call_args[0][0])
        self.assertEqual(result.status_code, 204)

    @patch("cbam_api.requests")
    def test_instantiate(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, status_code=202)
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.instantiate("test", {"testKey": "testValue"})
        self.cbam_api.token = "blah"
        result = self.cbam_api.instantiate("test-resource-id",
                                           {"testKey": "testValue"})
        mocked_requests.post.assert_called()
        self.assertEqual(
            mocked_requests.post.call_args[0][0], "{}/{}".format(
                self.cbam_api.base_address,
                Address.instantiate("test-resource-id")))
        self.assertEqual(mocked_requests.post.call_args[1]["json"],
                         {"testKey": "testValue"})
        self.assertTrue(
            "test-resource-id" in mocked_requests.post.call_args[0][0])
        self.assertEqual(result.status_code, 202)

    @patch("cbam_api.requests")
    def test_scale(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, status_code=202)
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.scale("test", {"testKey": "testValue"})
        self.cbam_api.token = "blah"
        result = self.cbam_api.scale("test-resource-id",
                                     {"testKey": "testValue"})
        mocked_requests.post.assert_called()
        self.assertEqual(
            mocked_requests.post.call_args[0][0], "{}/{}".format(
                self.cbam_api.base_address, Address.scale("test-resource-id")))
        self.assertEqual(mocked_requests.post.call_args[1]["json"],
                         {"testKey": "testValue"})
        self.assertTrue(
            "test-resource-id" in mocked_requests.post.call_args[0][0])
        self.assertEqual(result.status_code, 202)

    @patch("cbam_api.requests")
    def test_terminate(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, status_code=202)
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.terminate("test", {"testKey": "testValue"})
        self.cbam_api.token = "blah"
        result = self.cbam_api.terminate("test-resource-id",
                                         {"testKey": "testValue"})
        mocked_requests.post.assert_called()
        self.assertEqual(
            mocked_requests.post.call_args[0][0], "{}/{}".format(
                self.cbam_api.base_address,
                Address.terminate("test-resource-id")))
        self.assertEqual(mocked_requests.post.call_args[1]["json"],
                         {"testKey": "testValue"})
        self.assertTrue(
            "test-resource-id" in mocked_requests.post.call_args[0][0])
        self.assertEqual(result.status_code, 202)

    @patch("cbam_api.requests")
    def test_heal(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, status_code=202)
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.heal("test", {"testKey": "testValue"})
        self.cbam_api.token = "blah"
        result = self.cbam_api.heal("test-resource-id",
                                    {"testKey": "testValue"})
        mocked_requests.post.assert_called()
        self.assertEqual(
            mocked_requests.post.call_args[0][0], "{}/{}".format(
                self.cbam_api.base_address, Address.heal("test-resource-id")))
        self.assertEqual(mocked_requests.post.call_args[1]["json"],
                         {"testKey": "testValue"})
        self.assertTrue(
            "test-resource-id" in mocked_requests.post.call_args[0][0])
        self.assertEqual(result.status_code, 202)

    @patch("cbam_api.requests")
    def test_upgrade(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, status_code=202)
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.upgrade("test", {"testKey": "testValue"})
        self.cbam_api.token = "blah"
        result = self.cbam_api.upgrade("test-resource-id",
                                       {"testKey": "testValue"})
        mocked_requests.post.assert_called()
        self.assertEqual(
            mocked_requests.post.call_args[0][0],
            "{}/{}".format(self.cbam_api.base_address,
                           Address.upgrade("test-resource-id")))
        self.assertEqual(mocked_requests.post.call_args[1]["json"],
                         {"testKey": "testValue"})
        self.assertTrue(
            "test-resource-id" in mocked_requests.post.call_args[0][0])
        self.assertEqual(result.status_code, 202)

    @patch("builtins.open")
    @patch("cbam_api.requests")
    def test_read_vnf(self, mocked_requests, mocked_os):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, headers=[{
                "content-type": "application/json"
            }])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_response()

        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.read_vnf("CBAM-3e7b5babe49d4ae598d3d55326486422")
        self.cbam_api.token = "blah"
        result = self.cbam_api.read_vnf(
            "CBAM-3e7b5babe49d4ae598d3d55326486422")
        mocked_requests.get.assert_called()
        self.assertTrue("CBAM-3e7b5babe49d4ae598d3d55326486422" in
                        mocked_requests.get.call_args[0][0])
        self.assertEqual("CBAM-3e7b5babe49d4ae598d3d55326486422",
                         result.content["id"])

    @patch("cbam_api.requests")
    def test_custom(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"id": "1234"}, status_code=202)
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.custom("test", "test-operation",
                                 {"testKey": "testValue"})
        self.cbam_api.token = "blah"
        result = self.cbam_api.custom("test-resource-id", "test-operation",
                                      {"testKey": "testValue"})
        mocked_requests.post.assert_called()
        self.assertEqual(
            mocked_requests.post.call_args[0][0], "{}/{}".format(
                self.cbam_api.base_address,
                Address.custom("test-resource-id", "test-operation")))
        self.assertEqual(mocked_requests.post.call_args[1]["json"],
                         {"testKey": "testValue"})
        self.assertTrue(
            "test-resource-id" in mocked_requests.post.call_args[0][0])
        self.assertEqual(result.status_code, 202)

    @patch("cbam_api.requests")
    def test_read_upgrade_baseline(self, mocked_requests):
        mocked_requests.get.return_value = FakeRequestsResponse(
            {"id": "1234"}, status_code=200)
        with self.assertRaises(InvalidAuthorizationHeader):
            self.cbam_api.read_upgrade_baseline("test")
        self.cbam_api.token = "blah"
        result = self.cbam_api.read_upgrade_baseline("test-resource-id")
        mocked_requests.get.assert_called()
        self.assertEqual(
            mocked_requests.get.call_args[0][0], "{}/{}".format(
                self.cbam_api.base_address,
                ExtensionAddress.upgrade_baseline("test-resource-id")))
        self.assertTrue(
            "test-resource-id" in mocked_requests.get.call_args[0][0])
        self.assertEqual(result.status_code, 200)


class TestExecutor(unittest.TestCase):
    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_create_vnf_package(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("create_vnf_package")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        with self.assertRaisesRegex(
                InvalidConfiguration,
                "File must be provided for create_vnf_package action"):
            Executor(fake_args).execute()

        fake_args.file = "none.none"
        with self.assertRaisesRegex(InvalidConfiguration,
                                    "File 'none.none' does not exist"):
            Executor(fake_args).execute()

        fake_args.file = "{name}.py".format(name=__name__)

        executor = Executor(fake_args)
        executor.api.token = "blah"
        executor.execute()
        mocked_open.assert_called_with(fake_args.file, "rb")
        self.assertTrue(
            api.request_address(Address.vnf_packages()) in
            mocked_requests.post.call_args[0])

        fake_args.file = "http://remote/file.ext"

        executor = Executor(fake_args)
        executor.api.token = "blah"
        executor.execute()
        mocked_requests.get.assert_called_once()
        self.assertEqual(mocked_requests.get.call_args[0][0],
                         "http://remote/file.ext")

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_read_vnf_packages(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("read_vnf_packages")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        executor = Executor(fake_args)
        executor.api.token = "blah"
        executor.execute()
        self.assertTrue(
            api.request_address(Address.vnf_packages()) in
            mocked_requests.get.call_args[0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_read_vnfs(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("read_vnfs")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        executor = Executor(fake_args)
        executor.api.token = "blah"
        executor.execute()
        self.assertTrue(
            api.request_address(Address.vnf_instances()) in
            mocked_requests.get.call_args[0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_read_vnf_lcm_operations(self, mocked_open,
                                              mocked_requests):
        fake_args = FakeFactory.fake_args("read_vnf_lcm_operations")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        executor = Executor(fake_args)
        executor.api.token = "blah"
        executor.execute()
        self.assertTrue(
            api.request_address(Address.vnf_lcm_operations()) in
            mocked_requests.get.call_args[0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_read_vnf_package(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("read_vnf_package")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        executor = Executor(fake_args)
        executor.api.token = "blah"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for read_vnf_package action"):
            executor.execute()
        fake_args.resource_id = "Nokia-SBC-media-C190B01-SBC-C190B01"
        executor.execute()
        mocked_requests.get.assert_called()
        self.assertTrue("Nokia-SBC-media-C190B01-SBC-C190B01" in
                        mocked_requests.get.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_read_vnf_lcm_operation(self, mocked_open,
                                             mocked_requests):
        fake_args = FakeFactory.fake_args("read_vnf_lcm_operation")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        executor = Executor(fake_args)
        executor.api.token = "blah"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for read_vnf_lcm_operation action"
        ):
            executor.execute()
        fake_args.resource_id = "CBAM-230d76431c0d41cd9c66e2283dede78a"
        executor.execute()
        mocked_requests.get.assert_called()
        self.assertTrue("CBAM-230d76431c0d41cd9c66e2283dede78a" in
                        mocked_requests.get.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_delete_vnf_package(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("delete_vnf_package")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        executor = Executor(fake_args)
        executor.api.token = "blah"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for delete_vnf_package action"):
            executor.execute()
        fake_args.resource_id = "Nokia-SBC-media-C190B01-SBC-C190B01"
        executor.execute()
        mocked_requests.delete.assert_called()
        self.assertTrue("Nokia-SBC-media-C190B01-SBC-C190B01" in
                        mocked_requests.delete.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_create_vnf(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("create_vnf")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data parameter must to be provided for create_vnf action"
        ):
            Executor(fake_args).execute()

        fake_args.data = "hlfdas"

        with self.assertRaisesRegex(InvalidConfiguration,
                                    "Extra data should be in JSON format"):
            Executor(fake_args).execute()

        fake_args.data = '{"blah": "value"}'
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data should contain 'name' parameter"):
            Executor(fake_args).execute()

        fake_args.data = '{"name": "test-media"}'
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data should contain 'vnfdId' parameter - vnf catalogue package identifier"
        ):
            Executor(fake_args).execute()

        fake_args.data = "@none.none"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data file {file} does not exist".format(
                    file=fake_args.data[1:])):
            Executor(fake_args).execute()

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_update_vnf(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("update_vnf")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data parameter must to be provided for update_vnf action"
        ):
            Executor(fake_args).execute()

        fake_args.data = "hlfdas"

        with self.assertRaisesRegex(InvalidConfiguration,
                                    "Extra data should be in JSON format"):
            Executor(fake_args).execute()

        fake_args.data = '{"blah": "value"}'
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for update_vnf action"):
            Executor(fake_args).execute()

        fake_args.data = "@none.none"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data file {file} does not exist".format(
                    file=fake_args.data[1:])):
            Executor(fake_args).execute()

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_delete_vnf(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("delete_vnf")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for delete_vnf action"):
            Executor(fake_args).execute()

        fake_args.resource_id = "test-id"
        executor = Executor(fake_args)
        executor.api.token = 'blah'
        executor.execute()
        mocked_requests.delete.assert_called()
        self.assertTrue("test-id" in mocked_requests.delete.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_instantiate(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("instantiate")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data parameter must to be provided for instantiate action"
        ):
            Executor(fake_args).execute()

        fake_args.data = "hlfdas"

        with self.assertRaisesRegex(InvalidConfiguration,
                                    "Extra data should be in JSON format"):
            Executor(fake_args).execute()

        fake_args.data = '{"blah": "value"}'
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for instantiate action"):
            Executor(fake_args).execute()

        fake_args.data = "@none.none"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data file {file} does not exist".format(
                    file=fake_args.data[1:])):
            Executor(fake_args).execute()

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_scale(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("scale")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data parameter must to be provided for scale action"):
            Executor(fake_args).execute()

        fake_args.data = "hlfdas"

        with self.assertRaisesRegex(InvalidConfiguration,
                                    "Extra data should be in JSON format"):
            Executor(fake_args).execute()

        fake_args.data = '{"blah": "value"}'
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for scale action"):
            Executor(fake_args).execute()

        fake_args.data = "@none.none"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data file {file} does not exist".format(
                    file=fake_args.data[1:])):
            Executor(fake_args).execute()

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_terminate(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("terminate")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data parameter must to be provided for terminate action"
        ):
            Executor(fake_args).execute()

        fake_args.data = "hlfdas"

        with self.assertRaisesRegex(InvalidConfiguration,
                                    "Extra data should be in JSON format"):
            Executor(fake_args).execute()

        fake_args.data = '{"blah": "value"}'
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for terminate action"):
            Executor(fake_args).execute()

        fake_args.data = "@none.none"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data file {file} does not exist".format(
                    file=fake_args.data[1:])):
            Executor(fake_args).execute()

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_heal(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("heal")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data parameter must to be provided for heal action"):
            Executor(fake_args).execute()

        fake_args.data = "hlfdas"

        with self.assertRaisesRegex(InvalidConfiguration,
                                    "Extra data should be in JSON format"):
            Executor(fake_args).execute()

        fake_args.data = '{"blah": "value"}'
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for heal action"):
            Executor(fake_args).execute()

        fake_args.data = "@none.none"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data file {file} does not exist".format(
                    file=fake_args.data[1:])):
            Executor(fake_args).execute()

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_read_vnf(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("read_vnf")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        executor = Executor(fake_args)
        executor.api.token = "blah"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for read_vnf action"):
            executor.execute()
        fake_args.resource_id = "CBAM-3e7b5babe49d4ae598d3d55326486422"
        executor.execute()
        mocked_requests.get.assert_called()
        self.assertTrue("CBAM-3e7b5babe49d4ae598d3d55326486422" in
                        mocked_requests.get.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_upgrade(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("upgrade")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data parameter must to be provided for upgrade action"):
            Executor(fake_args).execute()

        fake_args.data = "hlfdas"

        with self.assertRaisesRegex(InvalidConfiguration,
                                    "Extra data should be in JSON format"):
            Executor(fake_args).execute()

        fake_args.data = '{"blah": "value"}'
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for upgrade action"):
            Executor(fake_args).execute()

        fake_args.data = "@none.none"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data file {file} does not exist".format(
                    file=fake_args.data[1:])):
            Executor(fake_args).execute()

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_custom(self, mocked_open, mocked_requests):
        fake_args = FakeFactory.fake_args("custom")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data parameter must to be provided for custom action"):
            Executor(fake_args).execute()

        fake_args.data = "hlfdas"

        with self.assertRaisesRegex(InvalidConfiguration,
                                    "Extra data should be in JSON format"):
            Executor(fake_args).execute()

        fake_args.data = '{"blah": "value"}'
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for custom action"):
            Executor(fake_args).execute()

        fake_args.resource_id = "test-id"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Operation name must be provided for custom action"):
            Executor(fake_args).execute()

        fake_args.operation_name = "test-operation"
        fake_args.data = "@none.none"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data file {file} does not exist".format(
                    file=fake_args.data[1:])):
            Executor(fake_args).execute()

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_executor_read_upgrade_baseline(self, mocked_open,
                                            mocked_requests):
        fake_args = FakeFactory.fake_args("read_upgrade_baseline")
        api = CbamApi(fake_args.host, fake_args.client_id,
                      fake_args.client_secret)

        executor = Executor(fake_args)
        executor.api.token = "blah"
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Resource id must be provided for read_upgrade_baseline action"
        ):
            executor.execute()
        fake_args.resource_id = "CBAM-3e7b5babe49d4ae598d3d55326486422"
        executor.execute()
        mocked_requests.get.assert_called()
        self.assertTrue("CBAM-3e7b5babe49d4ae598d3d55326486422" in
                        mocked_requests.get.call_args[0][0])


class TestUtils(unittest.TestCase):
    def test_query(self):
        fake_response = FakeHeaders(None)
        self.assertFalse(
            Query(fake_response).is_header_in(Headers.application_json()))
        fake_response = FakeHeaders([{"content-type": "application/json"}])
        self.assertFalse(
            Query(fake_response).is_header_in([
                Headers.application_form_urlencoded(),
                Headers.application_json()
            ]))
        self.assertFalse(
            Query(fake_response).is_header_in({
                "blah": "value",
                "blah2": "value2"
            }))
        fake_response = FakeHeaders([])
        self.assertFalse(
            Query(fake_response).is_header_in(Headers.application_json()))
        fake_response = FakeHeaders([{
            "content-type": "application/json"
        }, {
            "authorization": "bearer blah"
        }, {
            "accept": "*/*"
        }])
        self.assertTrue(
            Query(fake_response).is_header_in(Headers.accept_all()))
        self.assertFalse(
            Query(fake_response).is_header_in(
                Headers.application_form_urlencoded()))
        self.assertTrue(
            Query(fake_response).is_header_in(Headers.authorization("blah")))
        self.assertTrue(
            Query(fake_response).is_one_of_headers_in(Headers.accept_all()))
        self.assertTrue(
            Query(fake_response).is_one_of_headers_in(
                [Headers.accept_all(),
                 Headers.application_form_urlencoded()]))
        self.assertFalse(
            Query(fake_response).is_one_of_headers_in([
                Headers.application_problem_json(),
                Headers.application_form_urlencoded()
            ]))
        fake_response = FakeFactory.fake_headers()
        self.assertTrue(
            Query(fake_response).is_header_in(Headers.application_json()))
        self.assertTrue(
            Query(fake_response).is_one_of_headers_in([
                Headers.application_json(),
                Headers.application_form_urlencoded()
            ]))
        self.assertFalse(
            Query(fake_response).is_one_of_headers_in([
                Headers.authorization("token"),
                Headers.application_form_urlencoded()
            ]))

    @patch('cbam_api.requests')
    @patch("builtins.open")
    def test_file_utils(self, mocked_open, mocked_requests):
        test_file_name = "test-file-name.ext"
        test_file_name = Utils.resolve_if_remote_file(test_file_name)
        self.assertEqual(test_file_name, "test-file-name.ext")
        test_file_name = Utils.resolve_if_remote_file(
            "http://{}".format(test_file_name))
        mocked_requests.get.assert_called_once()
        mocked_open.assert_called_once()
        self.assertGreater(
            len(test_file_name.split("/")[-1]), len("test-file-name.ext"))

    @patch('cbam_api.requests')
    @patch('cbam_api.json')
    @patch("builtins.open")
    def test_load_parameters(self, mocked_open, mocked_json, mocked_requests):
        fake_args = FakeArgs()
        test_dict = {"some": "data"}
        result = Utils.load_parameters(test_dict)
        self.assertEqual(result, test_dict)
        result = Utils.load_parameters(fake_args)
        self.assertEqual(result, fake_args)
        with self.assertRaisesRegex(
                InvalidConfiguration,
                "Extra data file none.none does not exist"):
            Utils.load_parameters("@none.none")
        mocked_json.load.return_value = {"key": "value"}
        result = Utils.load_parameters("@{}.py".format(__name__))
        mocked_json.load.assert_called_once()
        self.assertEqual(result, {"key": "value"})
        mocked_requests.get.return_value = FakeRequestsResponse(
            {"key": "value"}, headers=[Headers.application_problem_json()])
        result = Utils.load_parameters("http://remote/file.ext")
        mocked_requests.get.assert_called_once()
        self.assertEqual(result, {"key": "value"})
        result = Utils.load_parameters('{"key": "value"}')
        mocked_json.loads.assert_called_once()


class TestCbamApiRobot(unittest.TestCase):
    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_create_vnf_package(self, mocked_open, mocked_requests):
        mocked_requests.post.side_effect = [
            FakeRequestsResponse({"access_token": "blah"},
                                 status_code=200,
                                 headers=[Headers.application_json()]),
            FakeRequestsResponse({}, headers=[Headers.application_json()])
        ]
        file_location = "{name}.py".format(name=__name__)
        Create_VNF_Package("http://127.0.0.1", "test-id", "test-secret",
                           file_location)
        self.assertEqual(2, mocked_requests.post.call_count)
        mocked_open.assert_called()

    @patch("cbam_api.requests")
    def test_read_vnf_packages(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_packages_response(
        )
        result = Read_VNF_Packages("http://127.0.0.1", "test-id",
                                   "test-secret")
        mocked_requests.post.assert_called_once()
        mocked_requests.get.assert_called_once()
        self.assertEqual(result[0]["id"], "83")

    @patch("cbam_api.requests")
    def test_read_vnfs(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnfs_response(
        )
        result = Read_VNFs("http://127.0.0.1", "test-id", "test-secret")
        mocked_requests.post.assert_called_once()
        mocked_requests.get.assert_called_once()
        self.assertEqual(result[0]["vnfInstanceName"],
                         "CBAM-e8bd1ab2c233453389aceb6b12e7caee")

    @patch("cbam_api.requests")
    def test_read_vnf_lcm_operations(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_lcm_operations_response(
        )
        result = Read_VNF_LCM_Operations("http://127.0.0.1", "test-id",
                                         "test-secret")
        mocked_requests.post.assert_called_once()
        mocked_requests.get.assert_called_once()
        self.assertEqual("CBAM-e8bd1ab2c233453389aceb6b12e7caee",
                         result[0]["vnfInstanceId"])
        self.assertEqual("PROCESSING", result[0]["operationState"])

    @patch("cbam_api.requests")
    def test_read_vnf_package(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_package_response(
        )
        result = Read_VNF_Package("http://127.0.0.1", "test-id", "test-secret",
                                  "Nokia-SBC-media-C190B01-SBC-C190B01")
        mocked_requests.post.assert_called_once()
        mocked_requests.get.assert_called_once()
        self.assertEqual(result["vnfdId"],
                         "Nokia-SBC-media-C190B01-SBC-C190B01")

    @patch("cbam_api.requests")
    def test_read_vnf_lcm_operation(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_lcm_operation_response(
        )
        result = Read_VNF_Package("http://127.0.0.1", "test-id", "test-secret",
                                  "CBAM-230d76431c0d41cd9c66e2283dede78a")
        mocked_requests.post.assert_called_once()
        mocked_requests.get.assert_called_once()
        self.assertEqual(result["id"], "CBAM-230d76431c0d41cd9c66e2283dede78a")

    @patch("cbam_api.requests")
    def test_delete_vnf_package(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.delete.return_value = FakeRequestsResponse(
            None, status_code=204, headers=[Headers.application_json()])
        result = Delete_VNF_Package("http://127.0.0.1", "test-id",
                                    "test-secret",
                                    "CBAM-3e7b5babe49d4ae598d3d55326486422")
        mocked_requests.post.assert_called_once()
        mocked_requests.delete.assert_called_once()
        self.assertEqual(204, result.status_code)

    @patch("cbam_api.requests")
    def test_read_vnf(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_response()
        result = Read_VNF("http://127.0.0.1", "test-id", "test-secret",
                          "CBAM-3e7b5babe49d4ae598d3d55326486422")
        mocked_requests.post.assert_called_once()
        mocked_requests.get.assert_called_once()
        self.assertEqual(result["id"], "CBAM-3e7b5babe49d4ae598d3d55326486422")

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_create_vnf(self, mocked_open, mocked_requests):
        mocked_requests.post.side_effect = [
            FakeRequestsResponse({"access_token": "blah"},
                                 status_code=200,
                                 headers=[Headers.application_json()]),
            FakeRequestsResponse({}, headers=[Headers.application_json()])
        ]
        file_location = "{name}.py".format(name=__name__)
        Create_VNF("http://127.0.0.1", "test-id", "test-secret", "test-name",
                   "test-vnfdId", "test-description")
        self.assertEqual(2, mocked_requests.post.call_count)
        self.assertEqual("test-name",
                         mocked_requests.post.call_args[1]["json"]["name"])
        self.assertEqual("test-vnfdId",
                         mocked_requests.post.call_args[1]["json"]["vnfdId"])
        self.assertEqual(
            "test-description",
            mocked_requests.post.call_args[1]["json"]["description"])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_update_vnf(self, mocked_open, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.patch.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=202,
            headers=[Headers.application_json()])
        result = Update_VNF("http://127.0.0.1", "test-id", "test-secret",
                            "CBAM-3e7b5babe49d4ae598d3d55326486422",
                            {"name": "SuperName"})
        self.assertEqual(202, result.status_code)
        mocked_requests.post.assert_called()
        mocked_requests.patch.assert_called()
        self.assertTrue("CBAM-3e7b5babe49d4ae598d3d55326486422" in
                        mocked_requests.patch.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_delete_vnf(self, mocked_open, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.delete.return_value = FakeRequestsResponse(
            None, status_code=204, headers=[Headers.application_json()])
        result = Delete_VNF("http://127.0.0.1", "test-id", "test-secret",
                            "CBAM-3e7b5babe49d4ae598d3d55326486422")
        self.assertEqual(204, result.status_code)
        mocked_requests.post.assert_called()
        mocked_requests.delete.assert_called()
        self.assertTrue("CBAM-3e7b5babe49d4ae598d3d55326486422" in
                        mocked_requests.delete.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_instantiate(self, mocked_open, mocked_requests):
        mocked_requests.post.side_effect = [
            FakeRequestsResponse({"access_token": "blah"},
                                 status_code=200,
                                 headers=[Headers.application_json()]),
            FakeRequestsResponse(
                None,
                status_code=202,
                headers=[{
                    "location": "http://someoperationurl"
                },
                         Headers.application_json()])
        ]
        result = Instantiate("https://127.0.0.1", "test-id", "test-secret",
                             "CBAM-3e7b5babe49d4ae598d3d55326486422",
                             {"some": "data"})
        self.assertEqual(
            mocked_requests.post.call_args[0][0], "{}/{}".format(
                "https://127.0.0.1",
                Address.instantiate("CBAM-3e7b5babe49d4ae598d3d55326486422")))
        self.assertEqual(202, result.status_code)
        self.assertEqual(2, mocked_requests.post.call_count)
        self.assertTrue("CBAM-3e7b5babe49d4ae598d3d55326486422" in
                        mocked_requests.post.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_scale(self, mocked_open, mocked_requests):
        mocked_requests.post.side_effect = [
            FakeRequestsResponse({"access_token": "blah"},
                                 status_code=200,
                                 headers=[Headers.application_json()]),
            FakeRequestsResponse(
                None,
                status_code=202,
                headers=[{
                    "location": "http://someoperationurl"
                },
                         Headers.application_json()])
        ]
        result = Scale("https://127.0.0.1", "test-id", "test-secret",
                       "CBAM-3e7b5babe49d4ae598d3d55326486422",
                       {"some": "data"})
        self.assertEqual(
            mocked_requests.post.call_args[0][0], "{}/{}".format(
                "https://127.0.0.1",
                Address.scale("CBAM-3e7b5babe49d4ae598d3d55326486422")))
        self.assertEqual(202, result.status_code)
        self.assertEqual(2, mocked_requests.post.call_count)
        self.assertTrue("CBAM-3e7b5babe49d4ae598d3d55326486422" in
                        mocked_requests.post.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_terminate(self, mocked_open, mocked_requests):
        mocked_requests.post.side_effect = [
            FakeRequestsResponse({"access_token": "blah"},
                                 status_code=200,
                                 headers=[Headers.application_json()]),
            FakeRequestsResponse(
                None,
                status_code=202,
                headers=[{
                    "location": "http://someoperationurl"
                },
                         Headers.application_json()])
        ]
        result = Terminate("https://127.0.0.1", "test-id", "test-secret",
                           "CBAM-3e7b5babe49d4ae598d3d55326486422",
                           {"some": "data"})
        self.assertEqual(
            mocked_requests.post.call_args[0][0], "{}/{}".format(
                "https://127.0.0.1",
                Address.terminate("CBAM-3e7b5babe49d4ae598d3d55326486422")))
        self.assertEqual(202, result.status_code)
        self.assertEqual(2, mocked_requests.post.call_count)
        self.assertTrue("CBAM-3e7b5babe49d4ae598d3d55326486422" in
                        mocked_requests.post.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_heal(self, mocked_open, mocked_requests):
        mocked_requests.post.side_effect = [
            FakeRequestsResponse({"access_token": "blah"},
                                 status_code=200,
                                 headers=[Headers.application_json()]),
            FakeRequestsResponse(
                None,
                status_code=202,
                headers=[{
                    "location": "http://someoperationurl"
                },
                         Headers.application_json()])
        ]
        result = Heal("https://127.0.0.1", "test-id", "test-secret",
                      "CBAM-3e7b5babe49d4ae598d3d55326486422",
                      {"some": "data"})
        self.assertEqual(
            mocked_requests.post.call_args[0][0], "{}/{}".format(
                "https://127.0.0.1",
                Address.heal("CBAM-3e7b5babe49d4ae598d3d55326486422")))
        self.assertEqual(202, result.status_code)
        self.assertEqual(2, mocked_requests.post.call_count)
        self.assertTrue("CBAM-3e7b5babe49d4ae598d3d55326486422" in
                        mocked_requests.post.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_upgrade(self, mocked_open, mocked_requests):
        mocked_requests.post.side_effect = [
            FakeRequestsResponse({"access_token": "blah"},
                                 status_code=200,
                                 headers=[Headers.application_json()]),
            FakeRequestsResponse(
                None,
                status_code=202,
                headers=[{
                    "location": "http://someoperationurl"
                },
                         Headers.application_json()])
        ]
        result = Upgrade("https://127.0.0.1", "test-id", "test-secret",
                         "CBAM-3e7b5babe49d4ae598d3d55326486422",
                         {"some": "data"})
        self.assertEqual(
            mocked_requests.post.call_args[0][0], "{}/{}".format(
                "https://127.0.0.1",
                Address.upgrade("CBAM-3e7b5babe49d4ae598d3d55326486422")))
        self.assertEqual(202, result.status_code)
        self.assertEqual(2, mocked_requests.post.call_count)
        self.assertTrue("CBAM-3e7b5babe49d4ae598d3d55326486422" in
                        mocked_requests.post.call_args[0][0])

    @patch("cbam_api.requests")
    @patch("builtins.open")
    def test_custom(self, mocked_open, mocked_requests):
        mocked_requests.post.side_effect = [
            FakeRequestsResponse({"access_token": "blah"},
                                 status_code=200,
                                 headers=[Headers.application_json()]),
            FakeRequestsResponse(
                None,
                status_code=202,
                headers=[{
                    "location": "http://someoperationurl"
                },
                         Headers.application_json()])
        ]
        result = Custom("https://127.0.0.1", "test-id", "test-secret",
                        "CBAM-3e7b5babe49d4ae598d3d55326486422",
                        "test-operation", {"some": "data"})
        self.assertEqual(
            mocked_requests.post.call_args[0][0], "{}/{}".format(
                "https://127.0.0.1",
                Address.custom("CBAM-3e7b5babe49d4ae598d3d55326486422",
                               "test-operation")))
        self.assertEqual(202, result.status_code)
        self.assertEqual(2, mocked_requests.post.call_count)
        self.assertTrue("CBAM-3e7b5babe49d4ae598d3d55326486422" in
                        mocked_requests.post.call_args[0][0])

    @patch("cbam_api.requests")
    def test_read_upgrade_baseline(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.get.return_value = FakeRequestsResponse(
            {"id": "CBAM-3e7b5babe49d4ae598d3d55326486422"},
            status_code=200,
            headers=[Headers.application_json()])
        result = Read_Upgrade_Baseline(
            "http://127.0.0.1", "test-id", "test-secret",
            "CBAM-3e7b5babe49d4ae598d3d55326486422")
        mocked_requests.post.assert_called_once()
        mocked_requests.get.assert_called_once()
        self.assertEqual(result["id"], "CBAM-3e7b5babe49d4ae598d3d55326486422")

    @patch("cbam_api.requests")
    def test_wait_for_operation_to_complete(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_lcm_operation_response(
        )
        result = Wait_For_Operation_To_Complete(
            "http://127.0.0.1", "test-id", "test-secret",
            "CBAM-230d76431c0d41cd9c66e2283dede78a", 2, 1)
        self.assertEqual(mocked_requests.get.call_count, 2)
        self.assertEqual(result, None)

        mocked_requests.get.return_value.response[
            'operationState'] = 'COMPLETED'
        result = Wait_For_Operation_To_Complete(
            "http://127.0.0.1", "test-id", "test-secret",
            "CBAM-230d76431c0d41cd9c66e2283dede78a", 2, 1)
        self.assertEqual(mocked_requests.get.call_count, 3)
        self.assertEqual(result['operationState'], 'COMPLETED')

    @patch("cbam_api.requests")
    def test_find_vnf_lcm_operations_by_name(self, mocked_requests):
        mocked_requests.post.return_value = FakeRequestsResponse(
            {"access_token": "blah"},
            status_code=200,
            headers=[Headers.application_json()])
        mocked_requests.get.return_value = FakeFactory.fake_read_vnf_lcm_operations_response(
        )
        result = Find_VNF_LCM_Operations_By_Name("http://127.0.0.1", "test-id",
                 "test-secret", "INSTANTIATE")
        self.assertEqual(result[0]["id"],
                 "CBAM-fb2c1dc5e55c4082a50225fa1a239ca6")
        result = Find_VNF_LCM_Operations_By_Name("http://127.0.0.1", "test-id",
                "test-secret", "CUSTOM:BACKUP")
        self.assertEqual(result[0]["id"],
                 "CBAM-d85b9bf9ae834f569ed6b951452b1111")


if __name__ == "__main__":
    verbosity = 2
    cbam_api = unittest.TestLoader().loadTestsFromTestCase(TestCbamApi)
    unittest.TextTestRunner(verbosity=verbosity).run(cbam_api)
    cbam_api_robot = unittest.TestLoader().loadTestsFromTestCase(
        TestCbamApiRobot)
    unittest.TextTestRunner(verbosity=verbosity).run(cbam_api_robot)
    executor = unittest.TestLoader().loadTestsFromTestCase(TestExecutor)
    unittest.TextTestRunner(verbosity=verbosity).run(executor)
    utils = unittest.TestLoader().loadTestsFromTestCase(TestUtils)
    unittest.TextTestRunner(verbosity=verbosity).run(utils)
