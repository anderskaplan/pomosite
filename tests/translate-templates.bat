mkdir temp
del temp\templates.pot
html2po --pot --multifile=onefile --duplicates=merge --pot content/test_multilingual/templates/ temp/templates.pot
podebug -i temp/templates.pot -o temp/pseudo.po --rewrite=unicode
pause
