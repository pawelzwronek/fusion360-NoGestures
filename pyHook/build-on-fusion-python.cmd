rem "Potrzebny msys2-64 -> pacman -S mingw-w64-x86_64-gcc"
rem W C:\Users\p\AppData\Local\Autodesk\webdeploy\production\19107935ce2ad08720646cb4a31efe37d8a5f41b\Python\lib\distutils\cygwinccompiler.py
rem         elif msc_ver == '1916':
rem            # VS2010 / MSVC 10.0
rem            return ['msvcr100']

set PYTHONDIR=C:\Users\p\AppData\Local\Autodesk\webdeploy\production\06fdec045fd75975b505ab1dcbd568595c1cf626\Python
set PATH=%PATH%;C:\temp\swigwin-4.2.0
set PATH=c:\msys64\mingw64\bin\;%PATH%
set PATH=c:\Users\p\AppData\Local\Programs\Python\Python311;%PATH%

rmdir /S /Q build
rm *.pyd

xcopy /S /Y /Q c:\Users\p\AppData\Local\Programs\Python\Python311\include %PYTHONDIR%\include\
xcopy /S /Y /Q c:\Users\p\AppData\Local\Programs\Python\Python311\libs %PYTHONDIR%\libs\
%PYTHONDIR%\python.exe -m pip install setuptools
%PYTHONDIR%\python.exe setup.py build -cmingw32
copy build\lib.win-amd64-cpython-312\pyHook\*.pyd .\