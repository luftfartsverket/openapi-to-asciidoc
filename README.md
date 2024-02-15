
[![Commit Activity](https://img.shields.io/github/commit-activity/m/Luftfartsverket/openapi-to-asciidoc?label=commits&style=for-the-badge)](https://github.com/Luftfartsverket/openapi-to-asciidoc/pulse)
[![GitHub Issues](https://img.shields.io/github/issues/Luftfartsverket/openapi-to-asciidoc?style=for-the-badge&logo=github)](https://github.com/Luftfartsverket/openapi-to-asciidoc/issues)
[![License](https://img.shields.io/github/license/Luftfartsverket/openapi-to-asciidoc?style=for-the-badge&logo=opensourceinitiative)](https://opensource.org/license/mit/)
[![Build](https://img.shields.io/github/actions/workflow/status/Luftfartsverket/openapi-to-asciidoc/build.yml?style=for-the-badge&logo=github)](https://github.com/Luftfartsverket/openapi-to-asciidoc/actions/workflows/build.yml)

# OpenAPI Specification to AsciiDoc

## Overview

The OpenAPI Specification to AsciiDoc is a set of Jinja2 templates that will help you create readable API documentation from a JSON OpenAPI Specification file.  

AsciiDoc is a versatile plain-text writing format which you can use as it is, or can easily be converted to pdf. 

## Installation

To use the templates, you need to install the openapi_to_asciidoc module.

```bash
pip install -U openapi-to-asciidoc
```

## Usage

To convert your OpenAPI Specification, type:

```bash
$ python openapi_to_asciidoc -j <path-to-open-api-spec>.json -o <path-to-output-file>.adoc
```

This will generate an AsciiDoc from your OpenAPI Specification. 

The templates are created with the OpenAPI Specification v.3.1.0 as a base. If your specification contains sections that are not included or requires improvement, please feel to provide an PR or file an issue.

### Objects

openapi-to-asciidoc creates objects with the help of Marshmallow in order to generate the templates. Each object of the specification follows the rules of its SchemaObject and can be generated independently, but most users will probably use the OpenAPISchema as their starting point. 

All Objects of the OpenAPI specification are represented in [objects.py](src/openapi_to_asciidoc/objects.py) and can be changed and modified depending on your needs. All but the OpenAPI object has their call to super() commented out to speed up processing. If you would like to just render a specific model, just enable the call to super() and you are good to go!

Example:

If you where to render and print just the Schema Object from an json string containing SchemaObject data, You would make the call to Super in the SchemaObject's init method, then you could just render it like this:

```python
var data = get_json_data() # Get json data of the Schema object however you like

schema_as_asciidoc: SchemaObject = SchemaObjectSchema().load(data) # Render the SchemaObject

print(schema_as_asciidoc.result) # Print the asciidoc generated output
```

The code in [convert.py](src/openapi_to_asciidoc/convert.py) is a good starting point to examine what's going on under the hood. 

## Requirements 

In order to run the templates, you need to have following installed:

* Python
* pip

## PIP Dependencies

* [Jinja2](https://pypi.org/project/Jinja2/)
* [marshmallow](https://pypi.org/project/marshmallow/)


## Known bugs and issues

1. _Nested objects and lists._ Objects using it's own Schema to render fields (Like the SchemaObjectSchema) might get less than perfect output if it contains a lot of nested objects. 

1. _Page breaks._ The generated document is just an AsciiDoc, so if you want to export it as a PDF for example, there is no functionality for page breaks. 

1. _Special characters._ Sometimes JSON specifications contains characters that are used for styles in AsciiDoc (like quotes '', asterisk *, HTML tags <b></b> etc.). There is no handling of these characters, so some sections may look a bit odd. These issues often appear when an object or list is too nested for the template.  

1. _Specification extensions_ There might be some inconsistencies in how the specification support is presented in the finished AsciiDoc document. If this is a feature that is widely used, the implementation may have to be tweaked to each individual template. 


## Limitations

The API Specification needs to be in JSON format, and built according to the [OpenAPI Specification standard](https://spec.openapis.org/oas/latest.html). If your specification contains sections that are not stated in the OpenAPI Specification, the template will not print that information in the generated document. 

## Possible improvements

- _Escaping of special characters_ Some characters like i.e html tags could possibly be handled better.

- _Schema object_ is referring to it self during parsing, which works fine for most use cases, but if you have Schema objects with nested properties for example, the output will look a bit strange. This could be handled differently, but given the Schema object's flexible structure, there might be a need to tweak this object to best suit your needs anyways.   

## Contribute

Want to help out? Read [this](CONTRIBUTING.md). 
