"""
A Flask application for jp.ubuntu.com
"""

# Packages
import flask
import talisker
import os
import webapp.template_utils as template_utils
from flask_caching import Cache
from datetime import timedelta

from canonicalwebteam.blog import build_blueprint, BlogViews, BlogAPI
from canonicalwebteam.discourse import DiscourseAPI, EngagePages
from canonicalwebteam.flask_base.app import FlaskBase
from canonicalwebteam.templatefinder import TemplateFinder
from canonicalwebteam import image_template
from webapp.views import (
    build_engage_index,
    build_engage_page,
    engage_thank_you,
)
from webapp.api import get_releases
from canonicalwebteam.cookie_service import CookieConsent
from jinja2 import ChoiceLoader, FileSystemLoader

session = talisker.requests.get_session()
app = FlaskBase(
    __name__,
    "jp.ubuntu.com",
    template_folder="../templates",
    static_folder="../static",
    template_404="404.html",
    template_500="500.html",
)

# Configuration for shared cookie service

# Configure Flask session
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=365)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SECURE"] = True
app.config["UBUNTU_COM_RELEASES"] = (
    "https://raw.githubusercontent.com/canonical/ubuntu.com/main/releases.yaml"
)


# Initialize Flask-Caching
app.config["CACHE_TYPE"] = "SimpleCache"
cache = Cache(app)

# ChoiceLoader attempts loading templates from each path in successive order
loader = ChoiceLoader(
    [
        FileSystemLoader("templates"),
        FileSystemLoader("node_modules/vanilla-framework/templates/"),
        FileSystemLoader("static/js/modules/vanilla-framework/"),
    ]
)

# Loader supplied to jinja_loader overwrites default jinja_loader
app.jinja_loader = loader


# Set up cache functions for cookie consent service
def get_cache(key):
    return cache.get(key)


def set_cache(key, value, timeout):
    cache.set(key, value, timeout)


cookie_service = None
if not app.debug:
    cookie_service = CookieConsent().init_app(
        app,
        get_cache_func=get_cache,
        set_cache_func=set_cache,
        start_health_check=True,
    )


blog_views = BlogViews(
    api=BlogAPI(
        session=session,
        api_url="https://ubuntu.com/blog/wp-json/wp/v2",
        thumbnail_width=354,
        thumbnail_height=180,
    ),
    blog_title="Ubuntu blog",
    tag_ids=[3184],
    per_page=11,
)
app.register_blueprint(build_blueprint(blog_views), url_prefix="/blog")


# Engage pages and takeovers from Discourse
# This section needs to provide takeover data for /
discourse_api = DiscourseAPI(
    base_url="https://discourse.ubuntu.com/",
    session=session,
    get_topics_query_id=16,
    api_key=os.getenv("DISCOURSE_API_KEY"),
    api_username=os.getenv("DISCOURSE_API_USERNAME"),
)

takeovers_path = "/takeovers"
discourse_takeovers = EngagePages(
    api=discourse_api,
    category_id=113,
    page_type="takeovers",
    exclude_topics=[29461, 21103],
)

engage_path = "/engage"
engage_pages = EngagePages(
    api=discourse_api,
    category_id=112,
    page_type="engage-pages",
    exclude_topics=[29460, 21103],
)

app.add_url_rule(engage_path, view_func=build_engage_index(engage_pages))
app.add_url_rule("/engage/<page>", view_func=build_engage_page(engage_pages))
app.add_url_rule(
    "/engage/<page>/thank-you",
    view_func=engage_thank_you(engage_pages),
)


def takeovers_json():
    active_takeovers = discourse_takeovers.parse_active_takeovers()
    takeovers = sorted(
        active_takeovers,
        key=lambda takeover: takeover["publish_date"],
        reverse=True,
    )
    response = flask.jsonify(takeovers)
    response.cache_control.max_age = "300"

    return response


def takeovers_index():
    all_takeovers = discourse_takeovers.get_index()
    all_takeovers.sort(
        key=lambda takeover: takeover["active"] == "true", reverse=True
    )
    active_count = len(
        [
            takeover
            for takeover in all_takeovers
            if takeover["active"] == "true"
        ]
    )

    return flask.render_template(
        "takeovers/index.html",
        takeovers=all_takeovers,
        active_count=active_count,
    )


app.add_url_rule("/takeovers.json", view_func=takeovers_json)
app.add_url_rule("/takeovers", view_func=takeovers_index)

releases = get_releases(app.config["UBUNTU_COM_RELEASES"])


# Image template
@app.context_processor
def utility_processor():
    return {"image": image_template}


# Template context
@app.context_processor
def context():
    return {
        "format_date": template_utils.format_date,
        "get_json_feed": template_utils.get_json_feed_content,
        "replace_admin": template_utils.replace_admin,
        "truncate_chars": template_utils.truncate_chars,
        "page": flask.request.args.get("page", ""),
        "releases": releases,
        "platform": flask.request.args.get("platform", ""),
        "version": flask.request.args.get("version", ""),
        "architecture": flask.request.args.get("architecture", ""),
        "product": flask.request.args.get("product", ""),
    }


@app.route("/favicon.ico")
def favicon():
    return flask.redirect(
        "https://res.cloudinary.com/canonical/image/fetch/q_auto,f_auto/"
        "https://assets.ubuntu.com/v1/088fd1bf-favicon.ico"
    )


@app.route("/robots.txt")
def robots():
    return flask.Response("", mimetype="text/plain")


# All other routes
template_finder_view = TemplateFinder.as_view("template_finder")
template_finder_view._exclude_xframe_options_header = True
app.add_url_rule("/", view_func=template_finder_view)
app.add_url_rule("/<path:subpath>", view_func=template_finder_view)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
