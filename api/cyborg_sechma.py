# -*- coding: utf-8 -*-
"""
Created on 2018/12/21 17:01
@author: mengph
reach
"""
schema_post_deployables={
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'function': {
                'type': 'string',
                'enum':["QAT","FPGA"]
            },
            'assignable':{
                'type': 'boolean'
            },
            'vendor': {
                'type': 'string'
            },
            'parent_uuid': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ]
            },
            'links': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'href': {'type': 'string'},
                        'rel' : {'type': 'string'}}
                    },
                    'required': ['href','rel']
            },
            'updated_at': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ]
            },
            'type': {
                'type': 'string'
            },
            'created_at': {
                'type': 'string'
            },
            'availability': {
                'type': 'string'
            },
            'uuid': {
                'type': 'string'
            },
            'name': {
                'type': 'string'
            },
            'host': {
                'type': 'string'
            },
            'version': {
                'type': 'string'
            },
            'board': {
                'type': 'string'
            },
            'programable': {
                'type': 'boolean'
            },
            'pcie_address': {
                'type': 'string'
            },
            'instance_uuid': {
                'anyOf':[
                    {'type': 'string'},
                    {'type': 'null'}
                ]
            },
            'root_uuid': {
                'type': 'string'
            },
        },
        'required': ['function',"assignable",'vendor','parent_uuid','links','updated_at','type','created_at',
                     'availability','uuid','name','host','version','board','programable','pcie_address',
                     'instance_uuid','root_uuid']
    }
}

schema_get_deployables_all={
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'deployables': {
                'type': 'array',
                'items':schema_post_deployables
            }
        },
        'required': ['deployables']
    }
}

schema_delete_deployables={
    'status_code': [204],
    'response_body': {
        'type': 'null'
    }
}

schema_post_accelerators={
    'status_code': [200],
    'response_body': {
        'type': 'object',
        'properties': {
            'user_id': {
                'type': 'string'
            },
            'description': {
                'type': 'string'
            },
            'links': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'href': {'type': 'string'},
                        'rel': {'type': 'string'}}
                },
                'required': ['href', 'rel']
            },
            'acc_capability': {
                'type': 'string'
            },
            'created_at': {
                'type': 'string'
            },
            'vendor_id': {
                'type': 'string'
            },
            'updated_at': {
                'anyOf': [
                    {'type': 'string'},
                    {'type': 'null'}
                ]
            },
            'acc_type': {
                'type': 'string'
            },
            'name': {
                'type': 'string'
            },
            'product_id': {
                'type': 'string'
            },
            'device_type': {
                'type': 'string'
            },
            'remotable': {
                'type': 'integer'
            },
            'project_id': {
                'type': 'string'
            },
            'uuid': {
                'type': 'string'
            },
        },
        'required': ['user_id', "description", 'links', 'acc_capability', 'created_at','vendor_id','updated_at', 'acc_type',
                     'name','product_id',  'device_type','remotable','project_id','uuid' ]
    }
}