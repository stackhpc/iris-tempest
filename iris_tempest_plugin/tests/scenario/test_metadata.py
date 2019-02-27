# -*- coding: utf-8 -*-
# Copyright 2019 StackHPC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from collections import namedtuple

from tempest.api import compute
from tempest import config
from tempest.lib.common import api_version_utils
from tempest.lib import decorators
from tempest.lib import exceptions as lib_exc
from tempest.lib.exceptions import TempestException

from iris_tempest_plugin.tests import base

CONF = config.CONF

ImageSearchResult = namedtuple("SearchResult", "success image")


def _params(**kwargs):
    # filter out null values
    return {k: v for (k, v) in kwargs.items() if v is not None}


class GlanceMetaDataTest(base.TestCase):
    LIMIT = None

    @staticmethod
    def _contains(images, meta):
        # Does at least one image exist with metadata matching that in the
        # meta dict?
        for image in images:
            for key, value in meta.items():
                if key not in image:
                    continue
                if image[key] != meta[key]:
                    continue
                return ImageSearchResult(success=True, image=image)
        return ImageSearchResult(success=False, image=None)

    @decorators.idempotent_id('94069db2-792f-4fa8-8bd3-2271a6e0c095')
    def test_centos_image_exists(self):
        if CONF.image_feature_enabled.api_v1:
            glance_client = self.os_primary.image_client
        elif CONF.image_feature_enabled.api_v2:
            glance_client = self.os_primary.image_client_v2
        else:
            raise lib_exc.InvalidConfiguration(
                'Either api_v1 or api_v2 must be True in '
                '[image-feature-enabled].')
        response = glance_client.list_images(params=_params(limit=self.LIMIT))
        # TODO(wszumski): check response http code and possibly retry
        while True:
            images = response["images"]
            expected = {
                'os_distro': "centos"
            }
            result = GlanceMetaDataTest._contains(images, expected)
            if result.success:
                break
            if "next" not in response:
                break
            last = images[-1]
            response = glance_client.list_images(params=_params(
                limit=self.LIMIT, marker=last["id"])
            )

        self.assertTrue(result.success)


class SpecMissing(TempestException):
    message = "The spec %(spec)s is missing on the flavor with uuid %(uuid)s"


class NoExtraSpecs(TempestException):
    message = (
        "The flavor with uuid %(uuid)s does not have any extra specs defined"
    )


class SpecInvalid(TempestException):
    def __init__(self, msg, *args, **kwargs):
        self.message = msg
        super(SpecInvalid, self).__init__(*args, **kwargs)


class ComputeTest(base.TestCase):

    def setUp(self):
        super(ComputeTest, self).setUp()
        if hasattr(self, "request_microversion"):
            self.useFixture(
                compute.api_microversion_fixture.APIMicroversionFixture(
                    self.request_microversion))

    @classmethod
    def skip_checks(cls):
        super(ComputeTest, cls).skip_checks()
        if not CONF.service_available.nova:
            raise cls.skipException("Nova is not available")
        cfg_min_version = CONF.compute.min_microversion
        cfg_max_version = CONF.compute.max_microversion or 'latest'
        if hasattr(cls, "min_microversion") and hasattr(cls,
                                                        "max_microversion"):
            api_version_utils.check_skip_with_microversion(
                cls.min_microversion,
                cls.max_microversion,
                cfg_min_version,
                cfg_max_version)

    @classmethod
    def resource_setup(cls):
        super(ComputeTest, cls).resource_setup()
        if hasattr(cls, "min_microversion"):
            cls.request_microversion = (
                api_version_utils.select_request_microversion(
                    cls.min_microversion,
                    CONF.compute.min_microversion))


class NovaFlavorTest(ComputeTest):
    LIMIT = None

    # NOTE(wszumski): in 2.61 we can get the extra specs from a list_detailed
    # call: https://developer.openstack.org/api-ref/compute/?expanded=list-flavors-with-details-detail#list-flavors-with-details  # noqa E501
    # min_microversion = '2.61'
    # max_microversion = 'latest'

    def _foreach_check_extra_specs(self, flavors, specs):
        client = self.client
        for flavor in flavors:
            response = client.list_flavor_extra_specs(flavor["id"])
            extra_specs = response["extra_specs"]
            for spec, action in specs.items():
                validator = action["validator"]
                if spec not in extra_specs:
                    raise SpecMissing(spec=spec, uuid=flavor["id"])
                value = extra_specs[spec]
                if not validator(value):
                    failure_tmpl = (
                        "%(spec)s on the flavor with uuid "
                        "%(flavor_id)s is set to %(value)s. %(msg)s"
                    )
                    fail_msg = failure_tmpl % {
                        "msg": action["fail_msg"],
                        "spec": spec,
                        "flavor_id": flavor["id"],
                        "value": value
                    }
                    raise SpecInvalid(fail_msg)

    def setUp(self):
        super(NovaFlavorTest, self).setUp()
        self.client = self.os_primary.flavors_client

    def test_apel_cpu_cost_on_every_flavor(self):
        client = self.client
        extra_specs = {
            "APEL_CPU_COST": {
                "validator": unicode.isdigit,
                "fail_msg": "Was expecting an int."
            }
        }
        response = client.list_flavors(detail=True,
                                       **_params(limit=self.LIMIT))
        while True:
            flavors = response["flavors"]
            self._foreach_check_extra_specs(flavors, extra_specs)
            flavor_links = response["flavors_links"]
            has_next = bool([x for x in flavor_links if x["rel"] == "next"])
            if not has_next:
                break
            next_ = flavors[-1]
            response = client.list_flavors(
                detail=True, **_params(
                    limit=self.LIMIT,
                    marker=next_["id"]
                )
            )
