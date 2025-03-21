import flask
import math


def build_engage_index(engage_docs):
    """
    List of all engage pages
    """

    def engage_index():
        page = flask.request.args.get("page", default=1, type=int)
        topic = flask.request.args.get("topic", default=None, type=str)
        sort = flask.request.args.get("sort", default=None, type=str)
        posts_per_page = 15
        metadata = engage_docs.get_index()

        total_pages = math.ceil(len(metadata) / posts_per_page)

        return flask.render_template(
            "engage/index.html",
            forum_url=engage_docs.api.base_url,
            metadata=metadata,
            page=page,
            topic=topic,
            sort=sort,
            posts_per_page=posts_per_page,
            total_pages=total_pages,
        )

    return engage_index


def build_engage_page(engage_pages):
    """
    Individual engage page
    """

    def engage_page(page):
        path = f"/engage/{page}"
        metadata = engage_pages.get_engage_page(path)
        if not metadata:
            flask.abort(404)
        else:
            return flask.render_template(
                "engage/base.html",
                forum_url=engage_pages.api.base_url,
                metadata=metadata,
            )

    return engage_page


def match_tags(tags_1, tags_2):
    for tag_1 in tags_1:
        for tag_2 in tags_2:
            if tag_1.strip().lower() == tag_2.strip().lower():
                return True
            else:
                continue

    return False


def engage_thank_you(engage_pages):
    """
    Renders an engage pages thank-you page
    i.e. whitepapers, pdfs

    If there is no current topic it can't render the page
    e.g. accessing directly

    @parameters: language (optional) and page path name
    e.g. /cloud-init-whitepaper
    @returns: a function that renders a template
    """

    def render_template(page):
        path = f"/engage/{page}"
        metadata = engage_pages.get_engage_page(path)
        all_engage_pages = engage_pages.get_index()
        if not metadata:
            flask.abort(404)

        # Filter engage pages by language and tags
        total_num_related = 3
        related = []
        for item in all_engage_pages:
            # Match language and match tags
            if match_tags(
                item["tags"].split(","), metadata["tags"].split(",")
            ):
                related.append(item)
            if len(related) < total_num_related:
                # we can only fit 3 related posts, no need to finish the loop
                break

        thank_you_text = metadata.get("thank_you_text", None)

        return flask.render_template(
            "engage/shared/thank-you.html",
            request_url=flask.request.referrer,
            resource_name=metadata["type"],
            resource_url=metadata["resource_url"],
            related=related,
            thank_you_text=thank_you_text,
        )

    return render_template
