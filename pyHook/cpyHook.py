import time
import datetime
import ctypes
from ctypes import wintypes

_tmpPath = "C:\\temp\\fusionlog_cpyHook.log"
logToFile = False
logToConsole = False


user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WH_MOUSE_LL = 14
WH_MAX = 16

def MouseSwitch(_msg, _x, _y, _data, _flags, _time, _hwnd, _window_name):
    return False

callback_funcs = [MouseSwitch] * WH_MAX
hHooks = [None] * WH_MAX
hHooks1 = [None] * WH_MAX

for i in range(WH_MAX):
    callback_funcs[i] = None
    hHooks[i] = None
    hHooks1[i] = None

HOOKPROC = ctypes.WINFUNCTYPE(ctypes.HRESULT, ctypes.c_int, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)

CallNextHookEx = user32.CallNextHookEx
CallNextHookEx.argtypes = [wintypes.HHOOK, ctypes.c_int, wintypes.WPARAM, wintypes.LPARAM]

SetWindowsHookExW = user32.SetWindowsHookExW
SetWindowsHookExW.argtypes = [ctypes.c_int, HOOKPROC, wintypes.HINSTANCE, wintypes.DWORD]
SetWindowsHookExW.restype = wintypes.HHOOK

GetModuleHandleW = kernel32.GetModuleHandleW
GetModuleHandleW.restype = ctypes.c_uint64

UnhookWindowsHookEx = user32.UnhookWindowsHookEx
UnhookWindowsHookEx.argtypes = [wintypes.HHOOK]

class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [("pt", POINT),
                ("mouseData", ctypes.c_ulong),
                ("flags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))]
casted_l_param = ctypes.POINTER(MSLLHOOKSTRUCT)


def log(msg):
    if logToConsole or logToFile:
        fracSecs = time.time()
        fracSecs = int((fracSecs - int(fracSecs)) * 1000)
        msg = f"{datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S.{fracSecs:03}:')} {msg}"

        if logToConsole:
            print(msg)
        if logToFile:
            with open(_tmpPath, 'a', encoding='utf-8') as f:
                f.write(msg + '\n')


def cLLMouseCallback(code, wParam, lParam):
    if code >= 0:
        ms = ctypes.cast(lParam, casted_l_param).contents

        args = (wParam, ms.pt.x, ms.pt.y, ms.mouseData, ms.flags, ms.time, None, None)

        pyfunc = callback_funcs[WH_MOUSE_LL]
        if pyfunc is not None:
            result = pyfunc(*args)
            if result == 0:
                return 42  # Block further processing

    return CallNextHookEx(hHooks[WH_MOUSE_LL], code, wParam, lParam)

def cSetHook(idHook, pyfunc):
    if idHook < 0 or idHook >= WH_MAX:
        raise ValueError("Hooking error: invalid hook ID")

    log(f"Setting hook for {idHook}")

    if idHook == WH_MOUSE_LL:
        if callback_funcs[idHook] is None:
            callback_funcs[idHook] = pyfunc

            hMod = GetModuleHandleW(None)
            hook_proc = HOOKPROC(cLLMouseCallback)
            hHooks1[idHook] = hook_proc
            hHooks[idHook] = SetWindowsHookExW(WH_MOUSE_LL, hook_proc, hMod, 0)
            last_error = ctypes.get_last_error()
            if last_error != 0:
                log(f"Last error: {last_error} {ctypes.FormatError(last_error)}")

        if not hHooks[idHook]:
            raise RuntimeError("Could not set hook")

    # Set process priority
    REALTIME_PRIORITY_CLASS = 256 # win32con.REALTIME_PRIORITY_CLASS
    SetPriorityClass = ctypes.windll.kernel32.SetPriorityClass
    SetPriorityClass.argtypes = [wintypes.HANDLE, wintypes.DWORD]
    SetPriorityClass.restype = wintypes.BOOL
    GetCurrentProcess = ctypes.windll.kernel32.GetCurrentProcess
    GetCurrentProcess.argtypes = []
    GetCurrentProcess.restype = wintypes.HANDLE
    SetPriorityClass(GetCurrentProcess(), REALTIME_PRIORITY_CLASS)

    return True

def cUnhook(idHook):
    log(f"Unhooking {idHook}")

    if idHook < 0 or idHook >= WH_MAX:
        raise ValueError("Invalid hook ID")

    if UnhookWindowsHookEx(hHooks[idHook]):
        callback_funcs[idHook] = None
        hHooks[idHook] = None
        hHooks1[idHook] = None
        return True
    return False
