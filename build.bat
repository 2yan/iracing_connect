pyinstaller --onefile RyGuy.py --icon="icon.ico"
del RyGuy.spec
del /Q build\*
rmdir /S /Q build