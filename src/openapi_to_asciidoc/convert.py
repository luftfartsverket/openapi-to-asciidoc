#!/usr/bin/env python3
# Copyright © LFV
"""OpenAPI Specification to AsciiDoc
"""

import argparse
import json

from openapi_to_asciidoc.objects import OpenApi, OpenApiSchema


def get_arguments():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "-j",
        "--json",
        help="OpenAPI JSON Specification File (default: openapi.json)",
        type=argparse.FileType("r"),
        default="openapi.json",
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="?",
        help="Where to output result (default: openapi.adoc)",
        type=argparse.FileType("w"),
        default="openapi.adoc",
    )

    return parser.parse_args()


def main():
    args = get_arguments()

    js_input = args.json
    output = args.output

    # read openapi json input
    openapi = json.load(js_input)

    # render template from schema
    openapi_schema = OpenApiSchema()
    schema: OpenApi = openapi_schema.load(openapi)

    # output rendered result
    output.write(schema.result)


if __name__ == "__main__":
    main()
