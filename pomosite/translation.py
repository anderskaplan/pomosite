import os
import shutil
from pathlib import Path
from translate.storage import po, html
from translate.convert.po2html import po2html
import translate.tools.podebug as podebug


def translate_page_templates(source_dir, po_file_path, destination_dir):
    """Translate template files in a directory using a specified PO file.

    The output is written to *destination_dir*. The output directory is created if it
    doesn't already exist.

    Currently only HTML template files are translated. Other files are copied
    verbatim to the destination directory.
    """
    with open(po_file_path, "rb") as f:
        inputstore = po.pofile(f)

    os.makedirs(destination_dir, exist_ok=True)

    for file in Path(source_dir).glob("*"):
        if file.suffix.lower() in [".html"]:
            with open(file, "rb") as templatefile:
                outputstring = po2html().mergestore(
                    inputstore, templatefile, includefuzzy=False
                )
            with open(Path(destination_dir, file.name), "wb") as outputfile:
                outputfile.write(outputstring.encode("utf-8"))
        else:
            shutil.copy(str(file), str(Path(destination_dir, file.name)))


def extract_translatable_content(source_dir, pot_file_path):
    outputstore = po.pofile()
    for file in Path(source_dir).glob("*"):
        if file.suffix.lower() in [".html"]:
            with open(file, "rb") as templatefile:
                htmlparser = html.htmlfile(inputfile=templatefile)
            for htmlunit in htmlparser.units:
                thepo = outputstore.addsourceunit(htmlunit.source)
                thepo.addlocations(htmlunit.getlocations())

    outputstore.removeduplicates(duplicatestyle="merge")
    with open(pot_file_path, "wb") as outputfile:
        outputstore.serialize(outputfile)


def generate_dummy_translation(source_pot_file_path, po_file_path):
    with open(po_file_path, "wb") as outputfile:
        podebug.convertpo(source_pot_file_path, outputfile, None, rewritestyle="unicode")
