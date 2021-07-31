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
    """Create a site configuration dictionary based on a given template directory.

    All files in the template directory with valid page-config headers are added as items.
    """
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


def is_referable_content(file):
    return file.suffix.lower() in [
        ".css",
        ".gif",
        ".jpg",
        ".jpeg",
        ".png",
        ".svg",
        ".ps",
        ".eps",
        ".pdf",
        ".tif",
        ".tiff",
        ".mp4",
        ".mpg",
        ".mpeg",
        ".avi",
    ]


def add_resources(resources_dir, site_config):
    """Add resource files from a directory (and subdirectories) to the site
    configuration.

    Resource files of common media types (.jpg, .css, etc) are added to the site
    configuration with their file name as ID, which must be unique.
    """
    item_config = site_config.get("item_config")
    for file in Path(resources_dir).glob("**/*"):
        if file.is_file():
            if is_referable_content(file):
                id = file.name
            else:
                id = "_%d" % len(item_config)

            if id in item_config:
                raise ValueError("An item with the same ID already exists: " + id)

            endpoint = str(file)[len(resources_dir) :].replace("\\", "/")

            item_config[id] = {
                "endpoint": endpoint,
                "source": str(file),
            }


def add_translation(language_tag, po_file_path, translated_template_dir, site_config):
    if not "translations" in site_config:
        site_config["translations"] = {}
    site_config["translations"][language_tag] = {
        "po_file_path": po_file_path,
        "translated_template_dir": translated_template_dir,
    }
