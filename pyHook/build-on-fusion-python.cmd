rem "Potrzebny msys2-64 -> pacman -S mingw-w64-x86_64-gcc"
rem W C:\Users\p\AppData\Local\Autodesk\webdeploy\production\8fc78e02ada35f7bfe8c61944f4c29231b2e06ab\Python\lib\distutils\cygwinccompiler.py
rem         elif msc_ver == '1916':
rem            # VS2010 / MSVC 10.0
rem            return ['msvcr100']

set PYTHONDIR=C:\Users\p\AppData\Local\Autodesk\webdeploy\production\8fc78e02ada35f7bfe8c61944f4c29231b2e06ab\Python
set PATH=%PATH%;C:\temp\swigwin-4.0.1
set PATH=c:\msys64\mingw64\bin\;%PATH%
set PATH=c:\Users\p\AppData\Local\Programs\Python\Python37-64;%PATH%

rmdir /S /Q build
rm *.pyd

xcopy /S /Y /Q c:\Users\p\AppData\Local\Programs\Python\Python37-64\include %PYTHONDIR%\include\
xcopy /S /Y /Q c:\Users\p\AppData\Local\Programs\Python\Python37-64\libs %PYTHONDIR%\libs\
%PYTHONDIR%\python.exe setup.py build -cmingw32
copy build\lib.win-amd64-3.7\pyHook\*.pyd .\