"""Main site generation functionality: templating and reference resolution.

Isolation layer for the jinja2 package.
"""

from pathlib import Path
import jinja2
import shutil
import re
import hashlib
from .translation import translate_page_templates


class ConfigurationError(Exception):
    """Exception raised for configuration errors."""

    pass


class InvalidReferenceError(Exception):
    """Exception raised when an invalid reference is encountered."""

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
        raise ConfigurationError('Invalid endpoint "%s" for %s.' % (endpoint, item_id))


def validate_config(site_config):
    if not "item_config" in site_config:
        raise ConfigurationError("Item configuration is missing.")
    all_endpoints = {}
    for page_id, page in site_config["item_config"].items():
        if not "endpoint" in page:
            raise ConfigurationError(
                "Item with id %s is missing the endpoint attribute." % page_id
            )
        validate_endpoint(page["endpoint"], "page id %s" % page_id)
        if page["endpoint"] in all_endpoints:
            raise ConfigurationError(
                "Found duplicate endpoint %s in the site configuration."
                % page["endpoint"]
            )
        all_endpoints[page["endpoint"]] = page_id

        if "template" in page and not "template_dir" in site_config:
            raise ConfigurationError(
                "Template directory is missing in the site configuration."
            )

        if "template" in page and "source" in page:
            raise ConfigurationError(
                "Item with id %s has both 'template' and 'source' attributes. It may only have one."
                % page_id
            )


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


def get_output_path(item, output_dir, language_tag):
    endpoint = item["endpoint"]
    if endpoint.endswith("/"):
        if "template" in item:
            source_file = item["template"]
        else:
            source_file = item["source"]
        endpoint = endpoint + "index" + Path(source_file).suffix

    endpoint = localize_endpoint(endpoint, language_tag)

    return Path(".").resolve() / output_dir / strip_leading_slash(endpoint)


def ensure_parent_dir_exists(path):
    if not path.parent.exists():
        path.parent.mkdir(parents=True)


def generate_pages_from_templates(site_config, output_dir, file_list=[]):
    @jinja2.pass_context
    def url_for(context, id, rooted=False):
        item = site_config["item_config"].get(id, None)
        if not item:
            raise InvalidReferenceError('Invalid page id "%s".' % id)

        to_endpoint = item["endpoint"]
        if "template" in item:
            localized_to_endpoint = localize_endpoint(
                to_endpoint, context["language_tag"]
            )
        else:
            localized_to_endpoint = to_endpoint

        if rooted or context.get("rooted_urls", False):
            return localized_to_endpoint
        else:
            from_endpoint = context["endpoint"]
            return make_relative_url(
                localize_endpoint(from_endpoint, context["language_tag"]),
                localized_to_endpoint,
            )

    @jinja2.pass_context
    def url_for_language(context, language_tag):
        page_endpoint = context["endpoint"]
        from_endpoint = localize_endpoint(page_endpoint, context["language_tag"])
        to_language_tag = None
        if (
            "translations" in site_config
            and language_tag in site_config["translations"]
        ):
            to_language_tag = language_tag
        to_endpoint = localize_endpoint(page_endpoint, to_language_tag)
        return make_relative_url(from_endpoint, to_endpoint)

    def create_jinja_environment(template_path):
        jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_path),
            autoescape=jinja2.select_autoescape([]),
        )
        # jinja_env.trim_blocks = True
        # jinja_env.lstrip_blocks = True
        jinja_env.globals["url_for"] = url_for
        jinja_env.globals["url_for_language"] = url_for_language
        return jinja_env

    def render_pages(template_path, language_tag=None):
        jinja_env = create_jinja_environment(template_path)
        for page_id, page in site_config["item_config"].items():
            template = page.get("template", None)
            if not template:
                continue
            jinja_template = jinja_env.get_template(template)
            context = {
                **page,
                "page_id": page_id,
                "language_tag": language_tag,
            }
            rendered_page = jinja_template.render(context).encode("utf-8")
            output_path = get_output_path(page, output_dir, language_tag)
            ensure_parent_dir_exists(output_path)
            with output_path.open(mode="wb") as fh:
                fh.write(rendered_page)
            file_list.append(str(output_path))

    template_dir = site_config.get("template_dir", "#invalid#")
    temp_dir = site_config.get("temp_dir", "#invalid#")
    render_pages(template_dir)
    translations = site_config.get("translations", {})
    for language_tag, language_config in translations.items():
        translated_template_dir = str(Path(temp_dir, language_tag))
        translate_page_templates(
            template_dir, language_config["po_file_path"], translated_template_dir
        )
        render_pages(translated_template_dir, language_tag)


def copy_resources(site_config, output_dir, file_list=[]):
    for _, item in site_config["item_config"].items():
        if "source" in item:
            output_path = get_output_path(item, output_dir, None)
            ensure_parent_dir_exists(output_path)
            shutil.copyfile(item["source"], output_path)
            file_list.append(str(output_path))


def write_manifest_file(file_list, output_dir, manifest_file_path):
    base_path = str(Path(".").resolve() / output_dir)
    with open(manifest_file_path, "w") as manifest_file:
        for file_name in sorted(file_list):
            short_name = file_name[len(base_path) :].replace("\\", "/")
            with open(file_name, "rb") as f:
                hash = hashlib.sha256()
                hash.update(f.read())
                digest = hash.hexdigest()
            manifest_file.write(f"{short_name};{digest}\n")


def generate(site_config, output_dir, file_list=[]):
    """Generate a static web site according to the given configuration.

    NOTE The output directory is created if it doesn't already exist.
    """
    validate_config(site_config)
    copy_resources(site_config, output_dir, file_list)
    generate_pages_from_templates(site_config, output_dir, file_list)
