@prompt $g

set dst="bundle v1.1"

rmdir /S /Q %dst%
mkdir %dst%
mkdir %dst%\pyHook
mkdir %dst%\icons

copy pyHook\__init__.py  %dst%\pyHook
copy pyHook\_cpyHook.cp35-win_amd64.pyd  %dst%\pyHook
copy pyHook\cpyHook.py  %dst%\pyHook
copy pyHook\HookManager.py  %dst%\pyHook
copy pyHook\LICENSE.txt  %dst%\pyHook
copy NoGestures.manifest  %dst%
copy autohotkey.py  %dst%
copy NoGestures.py  %dst%
copy icons %dst%\icons

pause
