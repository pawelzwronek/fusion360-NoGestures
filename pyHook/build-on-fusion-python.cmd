rm build\lib.win-amd64-3.5\pyHook\_cpyHook.cp35-win_amd64.pyd
rm _cpyHook.cp35-win_amd64.pyd
C:\Users\P\AppData\Local\Autodesk\webdeploy\shared\PYTHON\3.5.3c\WIN64\Python\python.exe setup.py build -cmingw32
copy build\lib.win-amd64-3.5\pyHook\_cpyHook.cp35-win_amd64.pyd _cpyHook.cp35-win_amd64.pyd
pause