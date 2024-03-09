pyinstaller --onefile RyGuy.py
del RyGuy.spec
del /Q build\*
rmdir /S /Q build