"""Create and edit site configurations."""

from pathlib import Path
import re
import ast


def parse_page_config(str):
    """Parse a page-config string on the format "id: "ID", endpoint: "E", ..."""
    page_config = {}
    for item in str.split(","):
        pair = re.fullmatch(r"\s*([\w\-]+)\s*:\s*(\S+)\s*", item)
        if pair:
            page_config[pair[1]] = ast.literal_eval(pair[2])
    return page_config


def create_site_config(template_dir):
    """Find all files in a given directory with a valid page-config header and add them to the config dict."""
    item_config = {}
    for file in Path(template_dir).glob("*"):
        if not file.is_dir():
            with file.open(mode="r", encoding="utf-8") as f:
                line = f.readline()
                match = re.fullmatch(r"\{#(.*)#\}", line.rstrip())
                if match:
                    page_config = parse_page_config(match[1])
                    page_config["template"] = file.name
                    if "id" in page_config:
                        item_config[page_config["id"]] = page_config

    return {
        "template_dir": template_dir,
        "item_config": item_config,
    }


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


def add_resources_dir(resources_dir, site_config):
    item_config = site_config["item_config"]
    for file in Path(resources_dir).glob("**/*"):
        if not file.is_dir():
            if is_referable_content(file):
                id = file.name
            else:
                id = "_%d" % len(item_config)

            if id in item_config:
                raise ValueError("Static file already exists: " + id)

            endpoint = str(file)[len(resources_dir) :].replace("\\", "/")

            item_config[id] = {
                "endpoint": endpoint,
                "source": file,
            }


def add_translation(language_tag, po_file_path, translated_template_dir, site_config):
    if not "translations" in site_config:
        site_config["translations"] = {}
    site_config["translations"][language_tag] = {
        "po_file_path": po_file_path,
        "translated_template_dir": translated_template_dir,
    }
