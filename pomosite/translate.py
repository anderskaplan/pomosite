import os
import shutil
from pathlib import Path
from translate.storage import html, po
from translate.convert.po2html import po2html


def translate_page_templates(source_dir, po_file_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    f = open(po_file_path, "rb")
    inputstore = po.pofile(f)
    f.close()
    for file in Path(source_dir).glob("*"):
        if file.suffix.lower() in [".html"]:
            templatefile = open(file, "rb")
            outputstring = po2html().mergestore(
                inputstore, templatefile, includefuzzy=False
            )
            templatefile.close()
            outputfile = open(Path(output_dir, file.name), "wb")
            outputfile.write(outputstring.encode("utf-8"))
            outputfile.close()
        else:
            shutil.copy(str(file), output_dir + "/" + file.name)
