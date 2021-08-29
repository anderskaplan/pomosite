from pathlib import Path
import shutil
from pomosite import (
    create_site_config,
    add_resources,
    add_language,
    generate,
    write_manifest_file,
)

site_root_path = Path(__file__).parent
temp_path = site_root_path / "temp"
output_path = temp_path / "public_html"

site_config = create_site_config(str(site_root_path / "templates"), str(temp_path))
add_resources(str(site_root_path / "resources"), site_config)
# add_language("en", str(site_root_path / "translations/en.po"), site_config)

print("%d items" % len(site_config["item_config"]))

if output_path.exists():
    shutil.rmtree(str(output_path))

file_list = []
generate(site_config, str(output_path), file_list)
write_manifest_file(file_list, str(output_path), output_path / ".site.txt")
