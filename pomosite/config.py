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


def create_site_config(template_dir, temp_dir):
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
        "temp_dir": temp_dir,
        "item_config": item_config,
    }


def is_common_media_file(file: Path):
    """Tests whether a given file is a media file.

    The input parameter should be a Path object.

    The check is performed on the file extension.
    """
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


def is_resource_file(file: Path):
    """Tests whether a file should be ignored when adding resources.

    The input parameter should be a Path object.
    """
    return file.name not in [".DS_Store"]


def add_resources(resources_dir, site_config, referable_test=is_common_media_file, resource_test=is_resource_file):
    """Add resource files from a directory to the site configuration.

    Files in subdirectories are also added with the relative path preserved. For
    example, the resource file resources/foo/image.gif will be added with URL path
    /foo/image.gif.

    Any file which tests as referable is added to the site configuration
    with its name (including suffix) as ID. This means that the file name must be
    unique.
    """
    item_config = site_config.get("item_config")
    for file in Path(resources_dir).glob("**/*"):
        if file.is_file():
            if not resource_test(file):
                continue
            elif referable_test(file):
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


def add_language(language_tag, po_file_path, site_config):
    """Add a language for a multi-lingual site.

    The language_tag is used in templates to refer to the language.

    The po_file_path specifies the PO file containing the translation for the language.
    A single PO file is used for all template files.
    """
    if not "translations" in site_config:
        site_config["translations"] = {}
    site_config["translations"][language_tag] = {
        "po_file_path": po_file_path,
    }
