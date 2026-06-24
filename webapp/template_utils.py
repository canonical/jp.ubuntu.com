import json
import logging

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
