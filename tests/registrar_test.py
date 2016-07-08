# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from data_pipeline.client import Client


class ClientTester(Client):
    @property
    def client_type(self):
        return 'tester'


@pytest.mark.usefixtures("configure_teams")
class TestRegistration(object):
    @property
    def client_name(self):
        return 'test_client'

    @property
    def team_name(self):
        return 'bam'

    @property
    def expected_frequency_seconds(self):
        return 0

    def _build_client(self, **override_kwargs):
        args = dict(
            client_name=self.client_name,
            team_name=self.team_name,
            expected_frequency_seconds=self.expected_frequency_seconds,
            monitoring_enabled=False
        )
        args.update(override_kwargs)
        return ClientTester(**args)

    def test_registration_message_schema(self, schematizer_client):
        client = self._build_client()
        expected_schema = client.registrar.registration_schema
        schema_id = client.registrar.registration_schema_id
        actual_schema = schematizer_client.get_schema_by_id(schema_id)
        assert expected_schema == actual_schema
        assert schema_id != 0 and schema_id is not None and actual_schema is not None
