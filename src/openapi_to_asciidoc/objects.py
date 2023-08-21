# Copyright © LFV
from marshmallow import Schema, ValidationError, fields, post_load, pre_load, validates, validate, EXCLUDE
import re
from openapi_to_asciidoc.render import render_object as jinja_render


def filter_x_variables(data):
    x_variables = {key: value for key, value in data.items() if key.startswith("x-")}
    data["x_variables"] = x_variables
    # remove x- key from original data since it now resides in the x_variabels dict.
    for key in x_variables.keys():
        del data[key]

    return data


# Base class that will use jinja to render the template.
class RenderableObject:
    def __init__(self, template_name: str, schema: Schema) -> str:
        self.template_name = template_name
        self.schema = schema
        self.result = self.render()

    def render(self) -> str:
        asciidoc_text = jinja_render(self.schema, self.template_name)
        return asciidoc_text


# Base class for objects that needs support for specification extensions.
#  https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#specificationExtensions
class SpecificationExtensions(Schema):
    x_variables = fields.Dict(keys=fields.Str(validate=validate.Regexp("^x-.*$")))

    @pre_load
    def preprocess_data(self, data, **kwargs):
        self.unknown = EXCLUDE  # exclude unknown variables
        return filter_x_variables(data=data)


class ContactObject(RenderableObject):
    def __init__(self, **data):
        self.name = data.get("name")
        self.url = data.get("url")
        self.email = data.get("email")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="contact_obj.j2", schema=self)


class ContactObjectSchema(SpecificationExtensions):
    name = fields.Str()
    url = fields.Str()
    email = fields.Str()

    @post_load
    def make_object(self, data, **kwargs):
        return ContactObject(**data)


class LicenseObject(RenderableObject):
    def __init__(self, **data):
        self.name = data.get("name")
        self.url = data.get("url")
        self.identifier = data.get("identifier")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="license_obj.j2", schema=self)


class LicenseObjectSchema(SpecificationExtensions):
    name = fields.Str()
    url = fields.Str()
    identifer = fields.Str()

    @post_load
    def make_object(self, data, **kwargs):
        return LicenseObject(**data)


class InfoObject(RenderableObject):
    def __init__(self, **data):
        self.title = data.get("title")
        self.summary = data.get("summary")
        self.description = data.get("description")
        self.terms_of_service = data.get("terms_of_service")
        self.version = data.get("version")
        self.contact = data.get("contact")
        self.license = data.get("license")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="info_obj.j2", schema=self)


class InfoObjectSchema(SpecificationExtensions):
    title = fields.Str(required=True)
    summary = fields.Str()
    description = fields.Str()
    terms_of_service = fields.Str(data_key="termsOfService")
    version = fields.Str(required=True)
    contact = fields.Nested(ContactObjectSchema)
    license = fields.Nested(LicenseObjectSchema)

    @post_load
    def make_info_object(self, data, **kwargs):
        return InfoObject(**data)


class ServerObject(RenderableObject):
    def __init__(self, **data):
        self.url = data.get("url")
        self.description = data.get("description")
        self.variables = data.get("variables")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="server_obj.j2", schema=self)


class ServerVariableObject(RenderableObject):
    def __init__(self, **data):
        self.enum = data.get("enum")
        self.default = data.get("default")
        self.description = data.get("description")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="server_variable_obj.j2", schema=self)


class ServerVariableObjectSchema(SpecificationExtensions):
    enum = fields.List(fields.String())
    default = fields.Str()
    description = fields.Str()

    @validates("enum")
    def validate_enum(self, value):
        if not value:
            raise ValidationError("enum cannot be empty")

    @post_load
    def make_server_variable(self, data, **kwargs):
        return ServerVariableObject(**data)


class ServerObjectSchema(SpecificationExtensions):
    url = fields.Str()
    description = fields.Str()
    variables = fields.Dict(keys=fields.Str(), values=fields.Nested(ServerVariableObjectSchema))

    @post_load
    def make_server_object(self, data, **kwargs):
        return ServerObject(**data)


class ReferenceObjectSchema(Schema):
    ref = fields.String(required=True, data_key="$ref")


class ExternalDocumentationSchema(Schema):
    description = fields.String()
    url = fields.String()


class ExampleObject(RenderableObject):
    def __init__(self, **data):
        self.description = data.get("description")
        self.summary = data.get("summary")
        self.value = data.get("value")
        self.externalValue = data.get("externalValue")
        # super().__init__(template_name="example_obj.j2", schema=self)


class ExampleObjectSchema(Schema):
    summary = fields.String()
    description = fields.String()
    value = fields.Raw()
    externalValue = fields.String(data_key="externalValue")

    @post_load
    def make_example(self, data, **kwargs):
        return ExampleObject(**data)


class ExamplesObjectSchema(Schema):
    examples = fields.Dict(keys=fields.String(), values=fields.Nested(ExampleObjectSchema))


class XMLObject(RenderableObject):
    def __init__(self, **data):
        self.name = data.get("name")
        self.namespace = data.get("namespace")
        self.prefix = data.get("prefix")
        self.attribute = data.get("attribute")
        self.wrapped = data.get("wrapped")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="xml_obj.j2", schema=self)


class XMLObjectSchema(SpecificationExtensions):
    name = fields.String()
    namespace = fields.String()
    prefix = fields.String()
    attribute = fields.Boolean()
    wrapped = fields.Boolean()

    @post_load
    def make_server_variable(self, data, **kwargs):
        return XMLObject(**data)


class DiscriminatorObject(RenderableObject):
    def __init__(self, **data):
        self.property_name = data.get("property_name")
        self.mapping = data.get("mapping")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="discriminator_obj.j2", schema=self)


class DiscriminatorObjectSchema(SpecificationExtensions):
    property_name = fields.String(data_key="propertyName")
    mapping = fields.Dict(keys=fields.Str(), values=fields.Str())

    @post_load
    def make_discriminator(self, data, **kwargs):
        return DiscriminatorObject(**data)


class SchemaObject(RenderableObject):
    def __init__(self, **data):
        self.title = data.get("title")
        self.multipleOf = data.get("multipleOf")
        self.maximum = data.get("maximum")
        self.exclusiveMaximum = data.get("exclusiveMaximum")
        self.minimum = data.get("minimum")
        self.exclusiveMinimum = data.get("exclusiveMinimum")
        self.maxLength = data.get("maxLength")
        self.minLength = data.get("minLength")
        self.pattern = data.get("pattern")
        self.maxItems = data.get("maxItems")
        self.minItems = data.get("minItems")
        self.uniqueItems = data.get("uniqueItems")
        self.maxProperties = data.get("maxProperties")
        self.minProperties = data.get("minProperties")
        self.required = data.get("required")
        self.enum = data.get("enum")
        self.type = data.get("type")
        self.allOf = data.get("allOf")
        self.oneOf = data.get("oneOf")
        self.anyOf = data.get("anyOf")
        self.not_ = data.get("not_")
        self.items = data.get("items")
        self.properties = data.get("properties")
        self.additionalProperties = data.get("additonalProperties")
        self.description = data.get("description")
        self.format = data.get("format")
        self.default = data.get("default")
        self.nullable = data.get("nullable")
        self.readOnly = data.get("readOnly")
        self.writeOnly = data.get("writeOnly")
        self.example = data.get("example")
        self.externalDocs = data.get("externalDocs")
        self.deprecated = data.get("deprecated")
        self.xml = data.get("xml")
        self.discriminator = data.get("discriminator")
        self.ref = data.get("ref")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="schema_obj.j2", schema=self)


class SchemaObjectSchema(SpecificationExtensions):
    title = fields.String()
    multipleOf = fields.Float()
    maximum = fields.Float()
    exclusiveMaximum = fields.Boolean()
    minimum = fields.Float()
    exclusiveMinimum = fields.Boolean()
    maxLength = fields.Integer()
    minLength = fields.Integer()
    pattern = fields.String()
    maxItems = fields.Integer()
    minItems = fields.Integer()
    uniqueItems = fields.Boolean()
    maxProperties = fields.Integer()
    minProperties = fields.Integer()
    required = fields.List(fields.String())
    enum = fields.List(fields.Raw())
    type = fields.String()
    allOf = fields.List(fields.Nested(lambda: SchemaObjectSchema()))
    oneOf = fields.List(fields.Nested(lambda: SchemaObjectSchema()))
    anyOf = fields.List(fields.Nested(lambda: SchemaObjectSchema()))
    not_ = fields.Nested(lambda: SchemaObjectSchema())
    items = fields.Nested(lambda: SchemaObjectSchema())
    properties = fields.Dict(keys=fields.String(), values=fields.Nested(lambda: SchemaObjectSchema()))
    additionalProperties = fields.Nested(lambda: SchemaObjectSchema())
    description = fields.String()
    format = fields.String()
    default = fields.Raw()
    nullable = fields.Boolean()
    readOnly = fields.Boolean()
    writeOnly = fields.Boolean()
    example = fields.Raw()
    externalDocs = fields.Nested("ExternalDocumentationObjectSchema")
    deprecated = fields.Boolean()
    xml = fields.Nested(XMLObjectSchema)
    discriminator = fields.Nested(DiscriminatorObjectSchema)
    ref = fields.String(data_key="$ref")

    @post_load
    def make_schema_object(self, data, **kwargs):
        return SchemaObject(**data)


class MediaTypeObject(RenderableObject):
    def __init__(self, **data):
        self.schema_object = data.get("schema_object")
        self.example = data.get("example")
        self.examples = data.get("examples")
        self.encoding = data.get("encoding")
        self.ref = data.get("ref")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="media_type_obj.j2", schema=self)


class MediaTypeObjectSchema(SpecificationExtensions):
    schema_object = fields.Nested(SchemaObjectSchema)
    example = fields.Raw()
    examples = fields.Dict(keys=fields.String(), values=fields.Nested(ExampleObjectSchema))
    encoding = fields.Dict()
    ref = fields.String(data_key="$ref")  # This enables support for reference object

    @pre_load
    def parse_data(self, data, **kwargs):
        if "schema" in data:
            data["schema_object"] = data["schema"]
            del data["schema"]
        return data

    @post_load
    def make_server_variable(self, data, **kwargs):
        return MediaTypeObject(**data)


class LinkObject(RenderableObject):
    def __init__(self, **data):
        self.enum = data.get("enum")
        self.operationRef = data.get("operationRef")
        self.operationId = data.get("operationId")
        self.parameters = data.get("parameters")
        self.requestBody = data.get("requestBody")
        self.description = data.get("description")
        self.server = data.get("server")
        self.ref = data.get("ref")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="link_obj.j2", schema=self)


class LinkObjectSchema(SpecificationExtensions):
    operationRef = fields.String(data_key="operationRef")
    operationId = fields.String(data_key="operationId")
    parameters = fields.Dict()  # Keep it generic as it supports Any attribute as value
    requestBody = fields.Raw()  # This supports any class as key and an expression as value.
    description = fields.String()
    server = fields.Nested(ServerObjectSchema)
    ref = fields.String(data_key="$ref")  # This enables support for reference object

    @post_load
    def make_link_object(self, data, **kwargs):
        return LinkObject(**data)


class HeaderObject(RenderableObject):
    def __init__(self, **data):
        self.description = data.get("description")
        self.required = data.get("required")
        self.deprecated = data.get("deprecated")
        self.allowEmptyValue = data.get("allowEmptyValue")
        self.style = data.get("style")
        self.explode = data.get("explode")
        self.allowReserved = data.get("allowReserved")
        self.schema_object = data.get("schema_object")
        self.example = data.get("example")
        self.examples = data.get("examples")
        self.content = data.get("content")
        self.ref = data.get("ref")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="header_obj.j2", schema=self)


class HeaderObjectSchema(SpecificationExtensions):
    description = fields.String()
    required = fields.Boolean()
    deprecated = fields.Boolean()
    allowEmptyValue = fields.Boolean(data_key="allowEmptyValue")
    style = fields.String()
    explode = fields.Boolean()
    allowReserved = fields.Boolean(data_key="allowReserved")
    schema_object = fields.Nested(SchemaObjectSchema)
    example = fields.Raw()
    examples = fields.Dict(keys=fields.String(), values=fields.Nested(ExampleObjectSchema))
    content = fields.Dict(keys=fields.String(), values=fields.Nested(MediaTypeObjectSchema))
    ref = fields.String(data_key="$ref")  # This enables support for reference object

    @pre_load
    def parse_data(self, data, **kwargs):
        if "schema" in data:
            data["schema_object"] = data["schema"]
            del data["schema"]
        return data

    @post_load
    def make_header_object(self, data, **kwargs):
        return HeaderObject(**data)


class EncodingObject(RenderableObject):
    def __init__(self, **data):
        self.contentType = data.get("contentType")
        self.headers = data.get("headers")
        self.style = data.get("style")
        self.explode = data.get("explode")
        self.allowReserved = data.get("allowReserved")
        self.ref = data.get("ref")
        # super().__init__(template_name="encoding_obj.j2", schema=self)


class EncodingObjectSchema(Schema):
    contentType = fields.String(data_key="contentType")
    headers = fields.Dict(keys=fields.String(), values=fields.Nested(HeaderObjectSchema))
    style = fields.String()
    explode = fields.Boolean()
    allowReserved = fields.Boolean(data_key="allowReserved")
    ref = fields.String(data_key="$ref")

    @post_load
    def make_encoding_object(self, data, **kwargs):
        return EncodingObject(**data)


class ParameterObject(RenderableObject):
    def __init__(self, **data):
        self.name = data.get("name")
        self.in_ = data.get("in_")
        self.description = data.get("description")
        self.required = data.get("required")
        self.deprecated = data.get("deprecated")
        self.allowEmptyValue = data.get("allowEmptyValue")
        self.style = data.get("style")
        self.allowReserved = data.get("allowReserved")
        self.schema_object = data.get("schema_object")
        self.example = data.get("example")
        self.examples = data.get("examples")
        self.ref = data.get("ref")
        # super().__init__(template_name="parameter_obj.j2", schema=self)


class ParameterObjectSchema(SpecificationExtensions):
    name = fields.String()
    in_ = fields.String(data_key="in")
    description = fields.String()
    required = fields.Boolean()
    deprecated = fields.Boolean()
    allowEmptyValue = fields.Boolean()
    style = fields.Str()
    explode = fields.Boolean()
    allowReserved = fields.Boolean()
    schema_object = fields.Nested(SchemaObjectSchema)
    example = fields.Raw()
    examples = fields.Dict(keys=fields.Str(), values=fields.Field())
    ref = fields.String(data_key="$ref")  # This enables support for reference object

    @pre_load
    def parse_data(self, data, **kwargs):
        if "schema" in data:
            data["schema_object"] = data["schema"]
            del data["schema"]
        return data

    @post_load
    def make_paramter_object(self, data, **kwargs):
        return ParameterObject(**data)


class ExternalDocsObject(RenderableObject):
    def __init__(self, **data):
        self.description = data.get("description")
        self.url = data.get("url")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="external_docs_obj.j2", schema=self)


class ExternalDocumentationObjectSchema(SpecificationExtensions):
    description = fields.Str()
    url = fields.Str()

    @post_load
    def make_external_docs(self, data, **kwargs):
        return ExternalDocsObject(**data)


class ResponseObject(RenderableObject):
    def __init__(self, **data):
        self.description = data.get("description")
        self.headers = data.get("headers")
        self.content = data.get("content")
        self.links = data.get("links")
        self.ref = data.get("ref")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="response_obj.j2", schema=self)


class ResponseObjectSchema(SpecificationExtensions):
    description = fields.String()
    headers = fields.Dict(keys=fields.String(), values=fields.Nested(HeaderObjectSchema))
    content = fields.Dict(keys=fields.String(), values=fields.Nested(MediaTypeObjectSchema))
    links = fields.Dict(keys=fields.String(), values=fields.Nested(LinkObjectSchema))
    ref = fields.String(data_key="$ref")

    @post_load
    def make_response_object(self, data, **kwargs):
        return ResponseObject(**data)


class RequestBodyObject(RenderableObject):
    def __init__(self, **data):
        self.description = data.get("description")
        self.content = data.get("content")
        self.required = data.get("required")
        self.ref = data.get("ref")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="request_body_obj.j2", schema=self)


class RequestBodySchema(SpecificationExtensions):
    description = fields.String()
    content = fields.Dict(keys=fields.String(), values=fields.Nested(MediaTypeObjectSchema))
    required = fields.Boolean()
    ref = fields.String(data_key="$ref")

    @post_load
    def make_request_body(self, data, **kwargs):
        return RequestBodyObject(**data)


class SecuritySchemeObject(RenderableObject):
    def __init__(self, **data):
        self.type = data.get("type")
        self.description = data.get("description")
        self.name = data.get("name")
        self.in_ = data.get("in_")
        self.scheme = data.get("scheme")
        self.bearerFormat = data.get("bearerFormat")
        self.flows = data.get("flows")
        self.ref = data.get("ref")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="security_scheme_obj.j2", schema=self)


class SecuritySchemeObjectSchema(SpecificationExtensions):
    type = fields.String(required=True)
    description = fields.String()
    name = fields.String()
    in_ = fields.String(data_key="in")
    scheme = fields.String()
    bearerFormat = fields.String(data_key="bearerFormat")
    flows = fields.Nested("OAuthFlowsObjectSchema")
    ref = fields.String(data_key="$ref")

    @post_load
    def make_security_scheme(self, data, **kwargs):
        return SecuritySchemeObject(**data)


class OAuthFlowObject(RenderableObject):
    def __init__(self, **data):
        self.authorizationUrl = data.get("authorizationUrl")
        self.tokenUrl = data.get("tokenUrl")
        self.refreshUrl = data.get("refreshUrl")
        self.scopes = data.get("scopes")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="oauth_flow_obj.j2", schema=self)


class OAuthFlowObjectSchema(SpecificationExtensions):
    authorizationUrl = fields.String(data_key="authorizationUrl")
    tokenUrl = fields.String(data_key="tokenUrl")
    refreshUrl = fields.String(data_key="refreshUrl")
    scopes = fields.Dict(keys=fields.String(), values=fields.String())

    @post_load
    def make_oauths_flow(self, data, **kwargs):
        return OAuthFlowObject(**data)


class OAuthFlowsObject(RenderableObject):
    def __init__(self, **data):
        self.implicit = data.get("implicit")
        self.password = data.get("password")
        self.clientCredentials = data.get("clientCredentials")
        self.authorizationCode = data.get("authorizationCode")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="oauth_flows_obj.j2", schema=self)


class OAuthFlowsObjectSchema(SpecificationExtensions):
    implicit = fields.Nested(OAuthFlowObjectSchema)
    password = fields.Nested(OAuthFlowObjectSchema)
    clientCredentials = fields.Nested("OAuthFlowObjectSchema", data_key="clientCredentials")
    authorizationCode = fields.Nested("OAuthFlowObjectSchema", data_key="authorizationCode")

    @post_load
    def make_oauths_flows(self, data, **kwargs):
        return OAuthFlowsObject(**data)


class SecurityRequirementObject(RenderableObject):
    def __init__(self, **data):
        self.securitySchemeName = data.get("securitySchemeName")
        self.securitySchemeType = data.get("securitySchemeType")
        # super().__init__(template_name="security_requirement_obj.j2", schema=self)


class SecurityRequirementObjectSchema(Schema):
    securitySchemeName = fields.Str()
    securitySchemeType = fields.List(fields.String())

    @pre_load
    def test(self, data, **kwargs):
        new_data = {}
        if data:
            for entry in data:
                # adds scheme name as an extra variable as cant be known before
                new_data["securitySchemeName"] = entry
                new_data["securitySchemeType"] = data[entry]
        return new_data

    @post_load
    def make_security_requirement(self, data, **kwargs):
        return SecurityRequirementObject(**data)


class CallbackObject(RenderableObject):
    def __init__(self, **data):
        self.expression = data.get("expression")
        self.data_key = data.get("data_key")
        self.ref = data.get("ref")
        # super().__init__(template_name="callback_obj.j2", schema=self)


class CallbackObjectSchema(Schema):
    expression = fields.Nested("PathItemObjectSchema")
    data_key = fields.String()
    ref = fields.String()

    @pre_load
    def map_expression(self, data, **kwargs):
        self.unknown = EXCLUDE  # exclude unknown variables
        new_data = {}
        # remap data to fit the expression and ref key defined above
        # Necessary since keys are expressions and cannot be known before
        pattern = r"\$((?!ref)[^\W_])\w*"
        for key, value in data.items():
            expression_found = re.search(pattern=pattern, string=key)
            if expression_found:
                new_data["data_key"] = key
                new_data["expression"] = value
            elif key == "$ref":
                new_data["ref"] = value
        return new_data

    @post_load
    def make_callback_object(self, data, **kwargs):
        return CallbackObject(**data)


class OperationObject(RenderableObject):
    def __init__(self, **data):
        self.tags = data.get("tags")
        self.summary = data.get("summary")
        self.description = data.get("description")
        self.externalDocs = data.get("externalDocs")
        self.operationId = data.get("operationId")
        self.parameters = data.get("parameters")
        self.requestBody = data.get("requestBody")
        self.responses = data.get("responses")
        self.callbacks = data.get("callbacks")
        self.deprecated = data.get("deprecated")
        self.security = data.get("security")
        self.servers = data.get("servers")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="operation_obj.j2", schema=self)


class OperationObjectSchema(SpecificationExtensions):
    tags = fields.List(fields.Str())
    summary = fields.String()
    description = fields.String()
    externalDocs = fields.Nested(ExternalDocumentationObjectSchema)
    operationId = fields.String()
    parameters = fields.List(fields.Nested(ParameterObjectSchema))
    requestBody = fields.Nested(RequestBodySchema)
    responses = fields.Dict(keys=fields.String(), values=fields.Nested(ResponseObjectSchema))
    callbacks = fields.Dict(keys=fields.String(), values=fields.Nested(CallbackObjectSchema))
    deprecated = fields.Bool()
    security = fields.List(fields.Nested(SecurityRequirementObjectSchema))
    servers = fields.Nested(ServerObjectSchema)

    @post_load
    def make_operation_object(self, data, **kwargs):
        return OperationObject(**data)


class PathItemObject(RenderableObject):
    def __init__(self, **data):
        self.get = data.get("get")
        self.put = data.get("put")
        self.post = data.get("post")
        self.delete = data.get("delete")
        self.options = data.get("options")
        self.head = data.get("head")
        self.patch = data.get("patch")
        self.trace = data.get("trace")
        self.servers = data.get("servers")
        self.parameters = data.get("parameters")
        self.ref = data.get("ref")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="path_item_obj.j2", schema=self)


class PathItemObjectSchema(SpecificationExtensions):
    get = fields.Nested(OperationObjectSchema)
    put = fields.Nested(OperationObjectSchema)
    post = fields.Nested(OperationObjectSchema)
    delete = fields.Nested(OperationObjectSchema)
    options = fields.Nested(OperationObjectSchema)
    head = fields.Nested(OperationObjectSchema)
    patch = fields.Nested(OperationObjectSchema)
    trace = fields.Nested(OperationObjectSchema)
    servers = fields.Nested(ServerObjectSchema)
    parameters = fields.List(fields.Nested(ParameterObjectSchema))
    ref = fields.Nested(ReferenceObjectSchema, data_key="$ref")

    @post_load
    def make_path_item(self, data, **kwargs):
        return PathItemObject(**data)


class PathsItem(RenderableObject):
    def __init__(self, **data):
        self.paths = data.get("paths")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="paths_obj.j2", schema=self)


class PathsItemObjectSchema(SpecificationExtensions):
    paths = fields.Dict(
        keys=fields.Str(validate=lambda key: key.startswith("/")), values=fields.Nested(PathItemObjectSchema)
    )

    @pre_load
    def map_paths(self, data, **kwargs):
        new_data = {}
        new_data["paths"] = data
        return new_data

    @post_load
    def make_paths_item(self, data, **kwargs):
        return PathsItem(**data)


class ComponentsObject(RenderableObject):
    def __init__(self, **data):
        self.schemas = data.get("schemas")
        self.responses = data.get("responses")
        self.parameters = data.get("parameters")
        self.examples = data.get("examples")
        self.request_bodies = data.get("requestBodies")
        self.headers = data.get("headers")
        self.security_schemes = data.get("securitySchemes")
        self.links = data.get("links")
        self.callbacks = data.get("callbacks")
        self.path_Items = data.get("pathItems")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="components_obj.j2", schema=self)


class ComponentsObjectSchema(SpecificationExtensions):
    schemas = fields.Dict(keys=fields.String(), values=fields.Nested(SchemaObjectSchema))
    responses = fields.Dict(
        keys=fields.String(), values=fields.Nested(ResponseObjectSchema)
    )  # all fields below should also handle reference objects.
    parameters = fields.Dict(keys=fields.String(), values=fields.Nested(ParameterObjectSchema))
    examples = fields.Dict(keys=fields.String(), values=fields.Nested(ExampleObjectSchema))
    requestBodies = fields.Dict(keys=fields.String(), values=fields.Nested(RequestBodySchema))
    headers = fields.Dict(keys=fields.String(), values=fields.Nested(HeaderObjectSchema))
    securitySchemes = fields.Dict(keys=fields.String(), values=fields.Nested(SecuritySchemeObjectSchema))
    links = fields.Dict(keys=fields.String(), values=fields.Nested(LinkObjectSchema))
    callbacks = fields.Dict(keys=fields.String(), values=fields.Nested(CallbackObjectSchema))
    pathItems = fields.Dict(keys=fields.String(), values=fields.Nested(PathItemObjectSchema))

    @post_load
    def make_openapi(self, data, **kwargs):
        return ComponentsObject(**data)


class TagObject(RenderableObject):
    def __init__(self, **data):
        self.name = data.get("name")
        self.description = data.get("description")
        self.external_docs = data.get("external_docs")
        self.x_variables = data.get("x_variables")
        # super().__init__(template_name="tag_obj.j2", schema=self)


class TagObjectSchema(SpecificationExtensions):
    name = fields.String(required=True)
    description = fields.String()
    external_docs = fields.Nested(ExternalDocumentationObjectSchema, data_key="externalDocs")

    @post_load
    def make_tag_object(self, data, **kwargs):
        return TagObject(**data)


class OpenApi(RenderableObject):
    def __init__(self, **data):
        self.open_api = data.get("openapi")
        self.info = data.get("info")
        self.jsonSchemaDialect = data.get("jsonSchemaDialect")
        self.servers = data.get("servers")
        self.paths = data.get("paths")
        self.webhooks = data.get("webhooks")
        self.components = data.get("components")
        self.security = data.get("security")
        self.tags = data.get("tags")
        self.external_docs = data.get("external_docs")
        self.x_variables = data.get("x_variables")
        super().__init__(template_name="openapi_obj.j2", schema=self)


class OpenApiSchema(SpecificationExtensions):
    openapi = fields.Str()
    info = fields.Nested(InfoObjectSchema)
    jsonSchemaDialect = fields.Str()
    servers = fields.List(fields.Nested(ServerObjectSchema))
    paths = fields.Nested(PathsItemObjectSchema)
    webhooks = fields.Dict(keys=fields.Str(), values=fields.Nested(PathItemObjectSchema))
    components = fields.Nested(ComponentsObjectSchema)
    security = fields.List(fields.Nested(SecurityRequirementObjectSchema))
    tags = fields.List(fields.Nested(TagObjectSchema))
    external_docs = fields.Nested(ExternalDocumentationObjectSchema, data_key="externalDocs")

    @post_load
    def make_openapi(self, data, **kwargs):
        return OpenApi(**data)
