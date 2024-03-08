pyinstaller --onefile -w to_arduino.py
del to_arduino.spec
del /Q build\*
rmdir /S /Q build