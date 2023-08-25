#!/usr/bin/env python3
# Copyright © LFV
"""OpenAPI Specification to AsciiDoc
"""

import argparse
import json
import sys

from openapi_to_asciidoc.objects import OpenApi, OpenApiSchema


def get_arguments():
    """
    Parses command line arguments
    """

    usage = """
    Usage:

    Use stdin and stdout:
      cat openapi.json | openapi_to_asciidoc.py -t openapi.j2

    Use specific files for input and output:
      openapi_to_asciidoc.py -j openapi.json -t openapi.j2 -o openapi.adoc
    """
    parser = argparse.ArgumentParser(epilog=usage, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument(
        "-j",
        "--json",
        help="OpenAPI JSON Specification File (default: stdin)",
        type=argparse.FileType("r"),
        default=sys.stdin,
    )
    parser.add_argument(
        "-o",
        "--output",
        nargs="?",
        help="Where to output result (default: stdout)",
        type=argparse.FileType("w"),
        default=sys.stdout,
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
