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

from tempest import config
from tempest.lib import decorators
from tempest.lib import exceptions as lib_exc

from iris_tempest_plugin.tests import base

CONF = config.CONF
LIMIT = None

ImageSearchResult = namedtuple("SearchResult", "success image")


def _params(**kwargs):
    # filter out null values
    return {k: v for (k, v) in kwargs.items() if v is not None}


class GlanceMetaDataTest(base.TestCase):

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
        response = glance_client.list_images(params=_params(limit=LIMIT))
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
                limit=LIMIT, marker=last["id"])
            )

        self.assertTrue(result.success)
