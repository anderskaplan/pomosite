import os
import shutil
from pathlib import Path
from translate.storage import html, po
from translate.convert.po2html import po2html


def translate_page_templates(source_dir, po_file_path, destination_dir):
    """Translate template files in a directory using a specified PO file.

    The output is written to *destination_dir*. The output directory is created if it
    doesn't already exist.

    Currently only HTML template files are translated. Other files are copied
    verbatim to the destination directory.
    """
    f = open(po_file_path, "rb")
    inputstore = po.pofile(f)
    f.close()

    os.makedirs(destination_dir, exist_ok=True)

    for file in Path(source_dir).glob("*"):
        if file.suffix.lower() in [".html"]:
            templatefile = open(file, "rb")
            outputstring = po2html().mergestore(
                inputstore, templatefile, includefuzzy=False
            )
            templatefile.close()
            outputfile = open(Path(destination_dir, file.name), "wb")
            outputfile.write(outputstring.encode("utf-8"))
            outputfile.close()
        else:
            shutil.copy(str(file), str(Path(destination_dir, file.name)))
