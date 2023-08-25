# Copyright © LFV

import pytest
import json

from openapi_to_asciidoc.objects import OpenApi, OpenApiSchema


@pytest.mark.skip("Convert is not a class and we don't have things setup for testing it yet")
def test_convert():
    pass


def test_parse():
    json_file = open("tests/resources/test.json")
    file_data = json.load(json_file)
    json_file.close()
    json_data = json.dumps(file_data)

    data = json.loads(json_data)
    openapi_schema = OpenApiSchema()

    open_api: OpenApi = openapi_schema.load(data)

    assert open_api.result is not None
