# -*- coding: utf-8 -*-
# Copyright 2016 Yelp Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import absolute_import
from __future__ import unicode_literals

import pytest

from data_pipeline import message as dp_message
from data_pipeline.envelope import Envelope
from data_pipeline.meta_attribute import MetaAttribute


class TestEnvelope(object):

    @pytest.fixture
    def envelope(self):
        return Envelope()

    @pytest.fixture(params=[
        None,
        {'good_payload': 26}
    ])
    def meta_attr_payload_data(self, request):
        return request.param

    @pytest.fixture
    def valid_meta(
        self,
        meta_attr_payload_data,
        registered_meta_attribute_schema
    ):
        if meta_attr_payload_data is None:
            return None
        meta_attr = MetaAttribute(
            schema_id=registered_meta_attribute_schema.schema_id,
            payload_data=meta_attr_payload_data
        )
        return [meta_attr]

    @pytest.fixture
    def meta_attr_param(self, valid_meta):
        return {'meta': valid_meta}

    @pytest.fixture(params=[
        (dp_message.CreateMessage, {}),
        (dp_message.RefreshMessage, {}),
        (dp_message.DeleteMessage, {}),
        (dp_message.UpdateMessage, {'previous_payload': bytes(20)})
    ])
    def message(self, request, registered_schema, payload, meta_attr_param):
        message_class, additional_params = request.param
        if meta_attr_param:
            additional_params.update(meta_attr_param)
        return message_class(
            schema_id=registered_schema.schema_id,
            payload=payload,
            **additional_params
        )

    @pytest.fixture
    def expected_unpacked_message(self, message):
        previous_payload = None
        if isinstance(message, dp_message.UpdateMessage):
            previous_payload = message.previous_payload
        return dict(
            encryption_type=message.encryption_type,
            message_type=message.message_type.name,
            meta=[
                meta_attr.avro_repr
                for meta_attr in message.meta
            ] if message.meta else None,
            payload=message.payload,
            previous_payload=previous_payload,
            schema_id=message.schema_id,
            timestamp=message.timestamp,
            uuid=message.uuid
        )

    def test_pack_create_bytes(self, message, envelope):
        assert isinstance(envelope.pack(message), bytes)

    def test_pack_create_str(self, message, envelope):
        assert isinstance(envelope.pack(message, ascii_encoded=True), str)

    def test_pack_unpack(self, message, envelope, expected_unpacked_message):
        unpacked = envelope.unpack(envelope.pack(message))
        assert unpacked == expected_unpacked_message

    def test_pack_unpack_ascii(self, message, envelope, expected_unpacked_message):
        unpacked = envelope.unpack(envelope.pack(message, ascii_encoded=True))
        assert unpacked == expected_unpacked_message
