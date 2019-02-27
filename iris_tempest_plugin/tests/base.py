# -*- coding: utf-8 -*-

# Copyright 2010-2011 OpenStack Foundation
# Copyright (c) 2013 Hewlett-Packard Development Company, L.P.
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

import tempest.test

from tempest.api import compute
from tempest.lib.common import api_version_utils
from tempest import config

CONF = config.CONF


class TestCase(tempest.test.BaseTestCase):
    """Test case base class for all unit tests."""
    credentials = ['primary']


class ComputeTest(TestCase):

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
