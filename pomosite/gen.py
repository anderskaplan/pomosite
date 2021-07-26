from pathlib import Path
import jinja2
import shutil
import re
import ast


class ValidationError(Exception):
    pass


class InvalidResourceIdError(Exception):
    pass


def strip_leading_slash(s):
    if s.startswith("/"):
        return s[1:]
    return s


def strip_trailing_slash(s):
    if s.endswith("/"):
        return s[:-1]
    return s


def validate_endpoint(endpoint, item_id):
    if not re.fullmatch(r"(/[a-zA-Z0-9_\-\.]*)+", endpoint):
        raise ValidationError('Invalid endpoint "%s" for %s.' % (endpoint, item_id))


def validate(pages):
    all_endpoints = {}
    for page_id, page in pages.items():
        if not "endpoint" in page:
            raise ValidationError("Endpoint for page id %s is missing." % page_id)
        validate_endpoint(page["endpoint"], "page id %s" % page_id)
        if page["endpoint"] in all_endpoints:
            raise ValidationError("Duplicate endpoint %s" % page["endpoint"])
        all_endpoints[page["endpoint"]] = page_id


def make_relative_url(from_endpoint, to_endpoint):
    # split both paths. they should always start with a slash.
    f = from_endpoint.split("/")
    t = to_endpoint.split("/")

    # clear the last part of the from path
    if f:
        f[-1] = ""

    # drop commons from left
    common = 0
    while common < len(f) and common < len(t) and f[common] == t[common]:
        common = common + 1
    f = f[common:]
    t = t[common:]

    # append all remaining items of the to path
    combined = t
    if len(f) > 1:
        # for each remaining from, append a '..'
        combined = [".."] * (len(f) - 1) + t

    # special case: the empty path
    if not combined:
        return "./"

    return "/".join(combined)


def localize_endpoint(endpoint, language_tag):
    if not language_tag:
        return endpoint

    atoms = endpoint.split("/")
    atoms.insert(-1, language_tag)
    return "/".join(atoms)


def endpoint_to_output_path(endpoint, output_base_path, language_tag):
    if endpoint.endswith("/"):
        endpoint = endpoint + "index.html"

    endpoint = localize_endpoint(endpoint, language_tag)

    return Path(Path(".").resolve(), output_base_path, strip_leading_slash(endpoint))


def ensure_parent_dir_exists(path):
    if not path.parent.exists():
        path.parent.mkdir(parents=True)


def generate_dynamic_pages(pages, templates_by_lang, output_base_path):
    @jinja2.contextfunction
    def url_for(context, id):
        if id in pages:
            to_endpoint = pages[id]["endpoint"]
            if "template" in pages[id]:
                localized_to_endpoint = localize_endpoint(
                    to_endpoint, context["language_tag"]
                )
            else:
                localized_to_endpoint = to_endpoint
        else:
            raise InvalidResourceIdError('Invalid page id "%s".' % id)

        if context["rooted_urls"]:
            return localized_to_endpoint
        else:
            from_endpoint = page["endpoint"]
            return make_relative_url(
                localize_endpoint(from_endpoint, context["language_tag"]),
                localized_to_endpoint,
            )

    @jinja2.contextfunction
    def url_for_language(context, language):
        page_endpoint = page["endpoint"]
        from_endpoint = localize_endpoint(page_endpoint, context["language_tag"])
        to_language_tag = None if language == templates_by_lang[0][0] else language
        to_endpoint = localize_endpoint(page_endpoint, to_language_tag)
        return make_relative_url(from_endpoint, to_endpoint)

    for index, item in enumerate(templates_by_lang):
        language, template_path = item
        language_tag = None if index == 0 else language

        jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            autoescape=jinja2.select_autoescape([]),
        )
        # jinja_env.trim_blocks = True
        # jinja_env.lstrip_blocks = True
        jinja_env.globals["url_for"] = url_for
        jinja_env.globals["url_for_language"] = url_for_language

        for page_id, page in pages.items():
            template = page.get("template", None)
            if template:
                try:
                    template = jinja_env.get_template(template)
                    context = {
                        "page_id": page_id,
                        "language_tag": language_tag,
                        "rooted_urls": page.get("rooted-urls", False),
                    }
                    rendered_page = template.render(context).encode("utf-8")
                    output_path = endpoint_to_output_path(
                        page["endpoint"], output_base_path, language_tag
                    )
                    ensure_parent_dir_exists(output_path)
                    with output_path.open(mode="wb") as fh:
                        fh.write(rendered_page)
                except Exception as e:
                    e.page_id = page_id
                    raise


def copy_static_pages(pages, output_base_path):
    for _, item in pages.items():
        if "source" in item:
            output_path = endpoint_to_output_path(
                item["endpoint"], output_base_path, None
            )
            ensure_parent_dir_exists(output_path)
            shutil.copyfile(item["source"], output_path)


def generate(pages, templates_by_lang, output_base_path):
    # templates_by_lang: [ (language, template_path), ... ] -- the first entry being the default language
    validate(pages)
    copy_static_pages(pages, output_base_path)
    generate_dynamic_pages(pages, templates_by_lang, output_base_path)


def parse_page_config(str):
    """Parse a page-config string on the format "id: "ID", endpoint: "E", ..."""
    page_config = {}
    for item in str.split(","):
        pair = re.fullmatch(r"\s*([\w\-]+)\s*:\s*(\S+)\s*", item)
        if pair:
            page_config[pair[1]] = ast.literal_eval(pair[2])
    return page_config


def add_dynamic_content_templates(path, config):
    """Find all files in a given directory with a valid page-config header and add them to the config dict."""
    for file in Path(path).glob("*"):
        if not file.is_dir():
            with file.open(mode="r", encoding="utf-8") as f:
                line = f.readline()
                match = re.fullmatch(r"\{#(.*)#\}", line.rstrip())
                if match:
                    page_config = parse_page_config(match[1])
                    page_config["template"] = file.name
                    if "id" in page_config:
                        config[page_config["id"]] = page_config


# add static files from a content directory structure to the page config.
# files of common types (style sheets, images, etc) are added with their file name as key, so that
# they can be referred to from dynamic pages. note that this means that they must have unique names.
# no translation.
# no exclusion of files with special names, as we may want to include files like ".htaccess".


def is_referable_content(file):
    return file.suffix.lower() in [
        ".css",
        ".jpg",
        ".png",
        ".eps",
        ".pdf",
        ".tif",
        ".tiff",
    ]


def add_static_content(path, config):
    for file in Path(path).glob("**/*"):
        if not file.is_dir():
            if is_referable_content(file):
                id = file.name
            else:
                id = "_%d" % len(config)

            if id in config:
                raise ValueError("Static file already exists: " + id)

            endpoint = str(file)[len(path) :].replace("\\", "/")

            config[id] = {
                "endpoint": endpoint,
                "source": file,
            }
