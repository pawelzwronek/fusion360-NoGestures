set dst=boundle

mkdir %dst%
mkdir %dst%\pyHook

copy pyHook\__init__.py  %dst%\pyHook
copy pyHook\_cpyHook.cp35-win_amd64.pyd  %dst%\pyHook
copy pyHook\cpyHook.py  %dst%\pyHook
copy pyHook\HookManager.py  %dst%\pyHook
copy pyHook\LICENSE.txt  %dst%\pyHook
copy autohotkey.py  %dst%
copy NoGestures.py  %dst%
copy NoGestures.manifest %dst%

pause
