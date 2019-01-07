# -*- coding: utf-8 -*-
"""
Created on 2018/12/19 11:43
@author: mengph
reach
"""
import requests
import json
import jsonschema
import exceptions
import cyborg_sechma
from cyborg import create_firmware

JSONSCHEMA_VALIDATOR = jsonschema.Draft4Validator
FORMAT_CHECKER = jsonschema.draft4_format_checker

br_ex_address="fd00:dead:beef:57::5"
keystone_url_12_v6="http://[%s]:5000/v2.0/tokens" %br_ex_address
cyborg_url_12_v6="http://[%s]:6666/v1/" %br_ex_address
firmware_url="http://10.121.136.222/Lenovo_thinkcloud_shell_role_20181213_015432.shr"


def sayname(func):
    def run(*argv):
        print func.__name__
        return func(*argv)
    return run

@sayname
def get_token_from_vim(keystone_url=keystone_url_12_v6):
    verify = False
    headers = {"Content-Type": "application/json;charset=UTF-8"}
    data = json.dumps({"auth": {"tenantName": "admin", "passwordCredentials": {"username": "admin", "password": "admin"}}})
    resp = requests.post(url=keystone_url, data=data, headers=headers,
                         verify=verify)

    # body=resp.json()
    body = json.loads(resp.content)

    print "++++++++++++++++++++++++++++++++"
    print body
    print "++++++++++++++++++++++++++++++++"
    return body["access"]["token"]["id"]

headers = {"Content-Type": "application/json;charset=UTF-8",
           "X-Auth-Token": get_token_from_vim(keystone_url_12_v6)}
@sayname
def post_cyborg_deployables(headers=headers):
    verify = False
    data = json.dumps(
                    {
                       "name":"test",
                       "uuid":"d50c7148-4d8e-4afa-846d-77c629e0f3e6",
                       "parent_uuid": None,
                       "root_uuid": None,
                       "pcie_address":"00ff:1f.2",
                       "host":"node-7.domain.tld",
                       "board":"37c9",
                       "vendor":"8086",
                       "version":"1.0",
                       "type":"Co-processor",
                       "function": "QAT",
                       "assignable": True,
                       "instance_uuid": None,
                       "availability": "free",
                       "programable": False
                    }
                    )
    resp = requests.post(url=cyborg_url_12_v6+"deployables/", data=data, headers=headers,
                         verify=verify)
    body = json.loads(resp.content)

    print "++++++++++++++++++++++++++++++++"
    print body
    print "++++++++++++++++++++++++++++++++"

    validate_res(schema=cyborg_sechma.schema_post_deployables,resp=resp,body=body)

@sayname
def post_cyborg_accelerators(headers=headers):
    verify = False
    data = json.dumps(
                    {
                        "name": "test",
                        "uuid": "0177845f-590b-4e55-9516-301830981df1",
                        "description": "test",
                        "device_type": "test",
                        "acc_type": "test",
                        "acc_capability": "test",
                        "vendor_id": "test",
                        "product_id": "test",
                        "remotable": 1
                    }
                    )
    resp = requests.post(url=cyborg_url_12_v6+"accelerators/", data=data, headers=headers,
                         verify=verify)
    body = json.loads(resp.content)

    print "++++++++++++++++++++++++++++++++"
    print body
    print "++++++++++++++++++++++++++++++++"
    validate_res(schema=cyborg_sechma.schema_post_accelerators, resp=resp, body=body)


@sayname
def get_cyborg_deployables(headers=headers):
    verify = False
    resp = requests.get(url=cyborg_url_12_v6+"deployables/d50c7148-4d8e-4afa-846d-77c629e0f3e6",  headers=headers,
                         verify=verify)
    # body=resp.json()
    body = json.loads(resp.content)
    print "++++++++++++++++++++++++++++++++"
    print body
    print "++++++++++++++++++++++++++++++++"
    validate_res(schema=cyborg_sechma.schema_post_deployables, resp=resp, body=body)

@sayname
def get_cyborg_accelerators(headers=headers):
    verify = False
    resp = requests.get(url=cyborg_url_12_v6+"accelerators/0177845f-590b-4e55-9516-301830981df1",  headers=headers,
                         verify=verify)
    # body=resp.json()
    body = json.loads(resp.content)
    print "++++++++++++++++++++++++++++++++"
    print body
    print "++++++++++++++++++++++++++++++++"

@sayname
def get_cyborg_deployables_all(headers=headers):
    verify = False
    resp = requests.get(url=cyborg_url_12_v6+"deployables/?",  headers=headers,
                         verify=verify)
    # body=resp.json()
    body = json.loads(resp.content)
    print "++++++++++++++++++++++++++++++++"
    print body
    print "++++++++++++++++++++++++++++++++"
    validate_res(schema=cyborg_sechma.schema_get_deployables_all, resp=resp, body=body)

@sayname
def get_cyborg_accelerators_all(headers=headers):
    verify = False
    resp = requests.get(url=cyborg_url_12_v6+"accelerators/?",  headers=headers,
                         verify=verify)
    # body=resp.json()
    body = json.loads(resp.content)
    print "++++++++++++++++++++++++++++++++"
    print body
    print "++++++++++++++++++++++++++++++++"

@sayname
def patch_cyborg_deployables_update(headers=headers):
    verify = False
    data = json.dumps([
            { "op": "replace", "path": "/availability", "value": "in-use" },
            { "op": "replace", "path": "/instance_uuid", "value": "d50c7148-4d8e-4afa-846d-77c629e0f3e6" }
            ])

    resp = requests.patch(url=cyborg_url_12_v6+"deployables/d50c7148-4d8e-4afa-846d-77c629e0f3e6", data=data, headers=headers,
                         verify=verify)
    body = json.loads(resp.content)

    print "++++++++++++++++++++++++++++++++"
    print body
    print "++++++++++++++++++++++++++++++++"
    validate_res(schema=cyborg_sechma.schema_post_deployables, resp=resp, body=body)

@sayname
def patch_cyborg_accelerators_update(headers=headers):
    verify = False
    data = json.dumps([
                        {"op": "replace", "path": "/description", "value": "testtest"},
                        {"op": "replace", "path": "/name", "value": "testtest"}
                    ])

    resp = requests.patch(url=cyborg_url_12_v6+"accelerators/0177845f-590b-4e55-9516-301830981df1", data=data, headers=headers,
                         verify=verify)
    body = json.loads(resp.content)

    print "++++++++++++++++++++++++++++++++"
    print body
    print "++++++++++++++++++++++++++++++++"

@sayname
def delete_cyborg_deployables(headers=headers):
    verify = False
    resp = requests.delete(url=cyborg_url_12_v6+"deployables/d50c7148-4d8e-4afa-846d-77c629e0f3e6",  headers=headers,
                         verify=verify)
    print "++++++++++++++++++++++++++++++++"
    print resp
    print "++++++++++++++++++++++++++++++++"

@sayname
def delete_cyborg_accelerators(headers=headers):
    verify = False
    resp = requests.delete(url=cyborg_url_12_v6+"accelerators/0177845f-590b-4e55-9516-301830981df1",  headers=headers,
                         verify=verify)
    body = None
    print "++++++++++++++++++++++++++++++++"
    print resp
    print "++++++++++++++++++++++++++++++++"
    validate_res(schema=cyborg_sechma.schema_delete_deployables, resp=resp, body=body)

@sayname
def post_cyborg_deployables_program(header=headers):
    verify = False
    data = json.dumps(
        {"uuid":"b1df47f6-74c1-488f-9544-c271ef301374","firmware_uuid":"63eb6d69-8454-4732-a6c9-7d0b9ed321c1"})
    resp = requests.post(url=cyborg_url_12_v6+"deployables/program/", data=data,headers=headers,
                         verify=verify)
    # body = json.loads(resp.content)

    print "++++++++++++++++++++++++++++++++"
    print resp
    print "++++++++++++++++++++++++++++++++"
    # validate_res(schema=cyborg_sechma.schema_post_accelerators, resp=resp, body=body)

def validate_res(schema,resp,body):
    body_schema = schema.get('response_body')
    try:
        jsonschema.validate(body, body_schema,
                            cls=JSONSCHEMA_VALIDATOR,
                            format_checker=FORMAT_CHECKER)
    except jsonschema.ValidationError as ex:
        msg = ("HTTP response body is invalid (%s)" % ex)
        print msg
        # raise exceptions.InvalidHTTPResponseBody(msg)


post_cyborg_deployables_program(headers)


try:
    post_cyborg_deployables(headers)
    post_cyborg_accelerators(headers)
    get_cyborg_deployables(headers)
    get_cyborg_accelerators(headers)
    get_cyborg_deployables_all(headers)
    get_cyborg_accelerators_all(headers)
    patch_cyborg_deployables_update(headers)
    patch_cyborg_accelerators_update(headers)
    post_cyborg_deployables_program(headers)
    firmware_1 = create_firmware(fuel_ip="10.121.137.11", controller_node="node-6", keystone_url=keystone_url_12_v6,
                                 firmware_url=firmware_url)
    firmware_uuid = firmware_1[0]["id"]
    print firmware_uuid
except Exception,error:
    raise error
finally:
    delete_cyborg_deployables(headers)
    delete_cyborg_accelerators(headers)