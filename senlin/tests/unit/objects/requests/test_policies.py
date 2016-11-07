# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import copy

from oslo_serialization import jsonutils
from senlin.objects.requests import policies
from senlin.tests.unit.common import base as test_base


class TestPolicyList(test_base.SenlinTestCase):

    def test_policy_list_request_body_full(self):
        params = {
            'name': ['policy1'],
            'type': ['senlin.policy.scaling-1.0'],
            'limit': 2,
            'marker': 'd6901ce0-1403-4b9c-abf5-25c59cf79823',
            'sort': 'name:asc',
            'project_safe': False
        }
        sot = policies.PolicyListRequest(**params)
        self.assertEqual(['policy1'], sot.name)
        self.assertEqual(['senlin.policy.scaling-1.0'], sot.type)
        self.assertEqual(2, sot.limit)
        self.assertEqual('d6901ce0-1403-4b9c-abf5-25c59cf79823', sot.marker)
        self.assertEqual('name:asc', sot.sort)
        self.assertFalse(sot.project_safe)


class TestPolicyCreate(test_base.SenlinTestCase):

    spec = {
        "properties": {
            "adjustment": {
                "min_step": 1,
                "number": 1,
                "type": "CHANGE_IN_CAPACITY"
            },
            "event": "CLUSTER_SCALE_IN"
        },
        "type": "senlin.policy.scaling",
        "version": "1.0"
    }

    body = {
        'name': 'test-policy',
        'spec': spec,
    }

    def test_policy_create_spec(self):
        properties = {
            "adjustment": {
                "min_step": 1,
                "number": 1,
                "type": "CHANGE_IN_CAPACITY"
            },
            "event": "CLUSTER_SCALE_IN"
        }
        sot = policies.PolicySpec(**self.spec)
        self.assertEqual(properties, sot.properties)
        self.assertEqual('senlin.policy.scaling', sot.type)
        self.assertEqual('1.0', sot.version)

    def test_policy_create_body(self):
        spec = copy.deepcopy(self.spec)
        sp = policies.PolicySpec(**spec['properties'])
        body = {
            'name': 'foo',
            'spec': sp
        }
        sot = policies.PolicyCreateRequestBody(**body)
        self.assertIsInstance(sot.spec, policies.PolicySpec)
        self.assertEqual('foo', sot.name)

    def test_policy_create_request(self):
        spec = copy.deepcopy(self.spec)
        sp = policies.PolicySpec(**spec['properties'])
        body = {
            'name': 'foo',
            'spec': sp
        }
        policy = policies.PolicyCreateRequestBody(**body)
        request = {'policy': policy}
        sot = policies.PolicyCreateRequest(**request)
        self.assertIsInstance(sot.policy, policies.PolicyCreateRequestBody)

    def test_request_spec_to_primitice(self):
        spec = copy.deepcopy(self.spec)
        sot = policies.PolicySpec(**spec)
        res = sot.obj_to_primitive()

        # assertions
        changes = res['senlin_object.changes']
        data = res['senlin_object.data']
        properties = jsonutils.loads(data['properties'])
        adjustment = properties['adjustment']

        self.assertEqual('PolicySpec', res['senlin_object.name'])
        self.assertEqual('senlin', res['senlin_object.namespace'])
        self.assertEqual('1.0', res['senlin_object.version'])

        self.assertIn('version', changes)
        self.assertIn('type', changes)
        self.assertIn('properties', changes)

        self.assertEqual(u'senlin.policy.scaling', data['type'])
        self.assertEqual(u'1.0', data['version'])

        self.assertEqual('CLUSTER_SCALE_IN', properties['event'])
        self.assertEqual(1, adjustment['min_step'])
        self.assertEqual('CHANGE_IN_CAPACITY', adjustment['type'])
        self.assertEqual(1, adjustment['number'])

    def test_request_body_to_primitive(self):
        spec = policies.PolicySpec(**self.spec)
        request = {
            'name': 'test-policy',
            'spec': spec
        }
        sot = policies.PolicyCreateRequestBody(**request)
        self.assertEqual('test-policy', sot.name)
        self.assertIsInstance(sot.spec, policies.PolicySpec)

        res = sot.obj_to_primitive()
        data = res['senlin_object.data']['spec']
        spec_data = data['senlin_object.data']
        # request body
        self.assertEqual('PolicyCreateRequestBody', res['senlin_object.name'])
        self.assertEqual('1.0', res['senlin_object.version'])
        self.assertEqual('senlin', res['senlin_object.namespace'])
        self.assertEqual(u'test-policy', res['senlin_object.data']['name'])
        self.assertIn('name', res['senlin_object.changes'])
        self.assertIn('spec', res['senlin_object.changes'])
        # spec
        self.assertEqual('PolicySpec', data['senlin_object.name'])
        self.assertEqual('1.0', data['senlin_object.version'])
        self.assertEqual('senlin', data['senlin_object.namespace'])
        self.assertIn('version', data['senlin_object.changes'])
        self.assertIn('type', data['senlin_object.changes'])
        self.assertIn('properties', data['senlin_object.changes'])
        # spec data
        self.assertEqual(u'senlin.policy.scaling', spec_data['type'])
        self.assertEqual(u'1.0', spec_data['version'])

    def test_request_to_primitive(self):
        spec = policies.PolicySpec(**self.spec)
        body = {
            'name': 'test-policy',
            'spec': spec
        }
        body = policies.PolicyCreateRequestBody(**body)
        request = {'policy': body}
        sot = policies.PolicyCreateRequest(**request)
        self.assertIsInstance(sot.policy, policies.PolicyCreateRequestBody)
        self.assertEqual('test-policy', sot.policy.name)

        res = sot.obj_to_primitive()
        self.assertIn('policy', res['senlin_object.changes'])
        self.assertEqual('PolicyCreateRequest', res['senlin_object.name'])
        self.assertEqual('senlin', res['senlin_object.namespace'])
        self.assertEqual('1.0', res['senlin_object.version'])

        data = res['senlin_object.data']['policy']
        self.assertEqual('PolicyCreateRequestBody', data['senlin_object.name'])
        self.assertEqual('senlin', data['senlin_object.namespace'])
        self.assertEqual('1.0', data['senlin_object.version'])
        self.assertIn('name', data['senlin_object.changes'])
        self.assertIn('spec', data['senlin_object.changes'])

        pd = data['senlin_object.data']
        self.assertEqual(u'test-policy', pd['name'])

        pd_spec = pd['spec']
        self.assertIn('version', pd_spec['senlin_object.changes'])
        self.assertIn('type', pd_spec['senlin_object.changes'])
        self.assertIn('properties', pd_spec['senlin_object.changes'])
        self.assertEqual('PolicySpec', pd_spec['senlin_object.name'])
        self.assertEqual('senlin', pd_spec['senlin_object.namespace'])
        self.assertEqual('1.0', pd_spec['senlin_object.version'])

        spec_data = pd_spec['senlin_object.data']
        self.assertEqual(u'senlin.policy.scaling', spec_data['type'])
        self.assertEqual(u'1.0', spec_data['version'])


class TestPolicyGet(test_base.SenlinTestCase):

    def test_policy_get(self):
        sot = policies.PolicyGetRequest(identity='foo')

        self.assertEqual('foo', sot.identity)


class TestPolicyUpdate(test_base.SenlinTestCase):

    def test_policy_update_body(self):
        data = {'name': 'foo'}
        sot = policies.PolicyUpdateRequestBody(**data)
        self.assertEqual('foo', sot.name)

    def test_policy_update(self):
        data = {'name': 'foo'}
        body = policies.PolicyUpdateRequestBody(**data)

        request = {
            'identity': 'pid',
            'policy': body
        }
        sot = policies.PolicyUpdateRequest(**request)
        self.assertEqual('pid', sot.identity)
        self.assertIsInstance(sot.policy, policies.PolicyUpdateRequestBody)

    def test_policy_data_to_primitive(self):
        data = {'name': 'foo'}
        sot = policies.PolicyUpdateRequestBody(**data)
        res = sot.obj_to_primitive()

        self.assertIn('name', res['senlin_object.changes'])
        self.assertEqual(u'foo', res['senlin_object.data']['name'])
        self.assertEqual('PolicyUpdateRequestBody', res['senlin_object.name'])
        self.assertEqual('senlin', res['senlin_object.namespace'])
        self.assertEqual('1.0', res['senlin_object.version'])

    def test_request_to_primitive(self):
        data = {'name': 'foo'}
        name = policies.PolicyUpdateRequestBody(**data)

        request = {
            'identity': 'pid',
            'name': name
        }
        sot = policies.PolicyUpdateRequest(**request)
        res = sot.obj_to_primitive()

        self.assertIn('identity', res['senlin_object.changes'])
        self.assertEqual(u'pid', res['senlin_object.data']['identity'])
        self.assertEqual('PolicyUpdateRequest', res['senlin_object.name'])
        self.assertEqual('senlin', res['senlin_object.namespace'])
        self.assertEqual('1.0', res['senlin_object.version'])


class TestPolicyValidate(test_base.SenlinTestCase):
    spec = {
        "properties": {
            "adjustment": {
                "min_step": 1,
                "number": 1,
                "type": "CHANGE_IN_CAPACITY"
            },
            "event": "CLUSTER_SCALE_IN"
        },
        "type": "senlin.policy.scaling",
        "version": "1.0"
    }

    def test_validate_request_body(self):
        spec = copy.deepcopy(self.spec)
        sot = policies.PolicySpec(**spec)

        self.assertEqual('senlin.policy.scaling', sot.type)
        self.assertEqual('1.0', sot.version)

    def test_validate_request(self):
        spec = copy.deepcopy(self.spec)
        policy = policies.PolicySpec(**spec)

        request = {'policy': policy}
        sot = policies.PolicyValidateRequest(**request)
        self.assertIsInstance(sot.policy, policies.PolicySpec)

    def test_request_body_to_primitive(self):
        spec = copy.deepcopy(self.spec)
        sot = policies.PolicySpec(**spec)
        res = sot.obj_to_primitive()

        changes = res['senlin_object.changes']
        self.assertIn('version', changes)
        self.assertIn('type', changes)
        self.assertIn('properties', changes)
        self.assertEqual('PolicySpec', res['senlin_object.name'])
        self.assertEqual('senlin', res['senlin_object.namespace'])
        self.assertEqual('1.0', res['senlin_object.version'])

        data = res['senlin_object.data']
        self.assertEqual(u'senlin.policy.scaling', data['type'])
        self.assertEqual(u'1.0', data['version'])

    def test_request_to_primitive(self):
        spec = copy.deepcopy(self.spec)
        policy = policies.PolicySpec(**spec)

        request = {'policy': policy}
        sot = policies.PolicyValidateRequest(**request)
        res = sot.obj_to_primitive()

        self.assertIn('policy', res['senlin_object.changes'])
        self.assertEqual('PolicyValidateRequest', res['senlin_object.name'])
        self.assertEqual('senlin', res['senlin_object.namespace'])
        self.assertEqual('1.0', res['senlin_object.version'])

        pd = res['senlin_object.data']['policy']
        pd_change = pd['senlin_object.changes']
        self.assertIn('version', pd_change)
        self.assertIn('type', pd_change)
        self.assertIn('properties', pd_change)

        self.assertEqual('PolicySpec', pd['senlin_object.name'])
        self.assertEqual('senlin', pd['senlin_object.namespace'])
        self.assertEqual('1.0', pd['senlin_object.version'])

        pd_data = pd['senlin_object.data']
        self.assertEqual(u'senlin.policy.scaling', pd_data['type'])
        self.assertEqual(u'1.0', pd_data['version'])


class TestPolicyDelete(test_base.SenlinTestCase):

    def test_policy_delete(self):
        sot = policies.PolicyDeleteRequest(identity='foo')

        self.assertEqual('foo', sot.identity)