rd /S /Q dist
rd /S /Q build
del *.pyc
ping -n 5 127.0.0.1
C:\Python27\python.exe setup.py py2exe
pause