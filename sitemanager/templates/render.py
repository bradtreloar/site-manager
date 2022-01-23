
from jinja2 import Environment, FunctionLoader, select_autoescape
import os

import sitemanager


def load_template(template_name):
    """
    Loads a Jinja2 template from file, given its name.

    A template's name has the following pattern:
    <module_name>.[<module_name>.]<base_name>

    This is resolved to the following patterns:
    - sitemanager/<module_name>/templates/<base_name>.html.j2
    - sitemanager/templates/common/<module_name>/]<base_name>.html.j2
    """
    siteman_path = sitemanager.__path__[0]
    path_components = template_name.split(".")
    module_name = path_components[0]
    path_components = path_components[1:]

    # Create the list of template paths.
    template_paths = [
        os.path.join(
            siteman_path,
            module_name,
            "templates",
            *path_components) + ".html.j2",
        os.path.join(
            siteman_path,
            "templates",
            "common",
            module_name,
            *path_components) + ".html.j2",
    ]

    # Load the first template found.
    for template_path in template_paths:
        if os.path.exists(template_path):
            with open(template_path) as template_file:
                return template_file.read()


def render_template(template_name, data):
    """
    Render a Jinja2 template with given data object.
    """
    # Render the template with the given data.
    template = Environment(
        loader=FunctionLoader(load_template),
        autoescape=select_autoescape()
    ).get_template(template_name)
    output = template.render(**data)
    return output
