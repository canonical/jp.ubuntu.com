import json
import logging
import os

from dateutil import parser
from webapp.api import get


def truncate_chars(value, max_length):
    length = len(value)
    if length > max_length:
        truncated = value[:max_length]
        if not length == (max_length + 1) and value[max_length + 1] != " ":
            truncated = truncated[: truncated.rfind(" ")]
        return truncated + "&hellip;"
    return value


def format_date(date):
    date_formatted = parser.parse(date)
    return date_formatted.strftime("%-d %B %Y")


def replace_admin(url):
    return url.replace("admin.insights.ubuntu.com", "jp.ubuntu.com/blog")


def get_json_feed_content(url, offset=0, limit=None):
    """
    Get the entries in a JSON feed
    """

    logger = logging.getLogger(__name__)
    end = limit + offset if limit is not None else None

    response = get(url)

    try:
        content = json.loads(response.text)
    except Exception as parse_error:
        logger.warning(
            "Failed to parse feed from {}: {}".format(url, str(parse_error))
        )
        return []

    return content[offset:end]


def load_form(path, form_id=None, is_modal=None, **kwargs):
    """
    Load and render a form from form-data.json using the shared form template.
    Reads the form-data.json located alongside the template for the given path,
    then renders it with shared/forms/form-template.html.
    """
    import flask

    # Locate the form-data.json relative to the templates folder
    templates_dir = os.path.join(os.path.dirname(__file__), "..", "templates")
    # Strip leading slash and map to directory containing the template
    template_rel = path.lstrip("/")
    form_data_path = os.path.join(
        templates_dir, template_rel, "form-data.json"
    )

    # Fall back to searching by page-level form-data.json 
    # (e.g. /blog/newsletter lives alongside templates/blog/form-data.json)
    if not os.path.exists(form_data_path):
        parent_dir = os.path.dirname(template_rel)
        form_data_path = os.path.join(
            templates_dir, parent_dir, "form-data.json"
        )

    if not os.path.exists(form_data_path):
        return ""

    with open(form_data_path) as f:
        data = json.load(f)

    form_config = data.get("form", {}).get(path)
    if not form_config:
        return ""

    form_data = dict(form_config.get("formData", {}))

    # Allow callers to override specific fields
    if form_id is not None:
        form_data["formId"] = str(form_id)
    if is_modal is not None:
        form_config = dict(form_config, isModal=is_modal)
    for key in ("title", "introText", "returnUrl", "lpId", "lpUrl"):
        if key in kwargs:
            form_data[key] = kwargs[key]

    return flask.render_template(
        "shared/forms/form-template.html",
        form_config=form_config,
        form_data=form_data,
        fieldsets=form_config.get("fieldsets", []),
    )
