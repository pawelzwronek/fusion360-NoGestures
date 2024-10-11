@prompt $g

set dst="bundle v2.0"

rmdir /S /Q %dst%
mkdir %dst%
mkdir %dst%\icons
mkdir %dst%\pyHook

copy icons %dst%\icons
copy pyHook  %dst%\pyHook
copy privacy-policy.md %dst%
copy autohotkey.py  %dst%
copy NoGestures.py  %dst%

pause
