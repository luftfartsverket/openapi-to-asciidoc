# Copyright © LFV
from pathlib import Path
import logging
import re

from jinja2 import (
    BaseLoader,
    Environment,
    FileSystemLoader,
    PackageLoader,
    Template,
    TemplateNotFound,
    select_autoescape,
)


def render_object(object, template: Template):
    def load_template(loader: BaseLoader, template: Template) -> str:
        template_env = Environment(loader=loader, autoescape=select_autoescape(), trim_blocks=True, lstrip_blocks=True)
        template = template_env.get_template(template)
        output = template.render(obj=object)
        return format_output(output=output)

    try:
        p = Path(__file__).parent / "templates"
        fs_loader = FileSystemLoader(searchpath=p)
        return load_template(loader=fs_loader, template=template)
    except TemplateNotFound:
        logging.info("Can't find local files. Uses package loader instead.")
        package_loader = PackageLoader("openapi_to_asciidoc")
        return load_template(loader=package_loader, template=template)


# Since Jinja is super unreliable with it's formatting,
#  we'll replace all newlines that occur more than 3 times in a row with just 2 newlines.
# Makes for a much more readable file
def format_output(output: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", output)
