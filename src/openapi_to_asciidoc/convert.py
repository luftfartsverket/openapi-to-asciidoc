#!/usr/bin/env python3
# Copyright © LFV
"""OpenAPI Specification to AsciiDoc
"""

import argparse
import json
import os
import sys
from importlib.metadata import version
from typing import TextIO, Union

if __package__ is None:
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    from openapi_to_asciidoc.objects import OpenApi, OpenApiSchema
else:
    from openapi_to_asciidoc.objects import OpenApi, OpenApiSchema


@staticmethod
def create_directory_and_open(file_path: Union[TextIO, str]) -> TextIO:
    """
    Create the directory if it doesn't exist and open the specified file.

    Parameters:
    - file_path (TextIO (sys.stdout) or str (path as argument on command line): The file path.
    - mode (str): The mode in which the file should be opened.

    Returns:
    - TextIO: The opened file.

    If the file path is sys.stdout, it is returned as is without attempting to create the directory.
    """
    if file_path == sys.stdout:
        return file_path

    directory = os.path.dirname(os.path.abspath(file_path))

    if not os.path.exists(directory):
        os.makedirs(directory)

    return open(file_path, "w")


def get_arguments():
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter)

    ver: str = "local dev" if __package__ is None else f"{version('openapi-to-asciidoc')}"

    parser.add_argument("-V", "--version", action="version", version=ver)

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
        help="Where to output result (default: stdout)",
        type=lambda file: create_directory_and_open(file),
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
