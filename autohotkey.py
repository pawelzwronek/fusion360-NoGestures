import ctypes
from ctypes import windll, byref
from ctypes.wintypes import POINT
import ctypes.wintypes
try:
    from . import pyHook as ph
except ImportError:
    import pyHook as ph

MOUSEEVENTF_MOVE = 0x0001 # mouse move
MOUSEEVENTF_LEFTDOWN = 0x0002 # left button down
MOUSEEVENTF_LEFTUP = 0x0004 # left button up
MOUSEEVENTF_RIGHTDOWN = 0x0008 # right button down
MOUSEEVENTF_RIGHTUP = 0x0010 # right button up
MOUSEEVENTF_MIDDLEDOWN = 0x0020 # middle button down
MOUSEEVENTF_MIDDLEUP = 0x0040 # middle button up
MOUSEEVENTF_WHEEL = 0x0800 # wheel button rolled
MOUSEEVENTF_ABSOLUTE = 0x8000 # absolute move


blockMouseMove = False
onMouseAll = None


def onMouseMove(_event):
    if blockMouseMove:
        return False
    return True

# create a hook manager
hm = ph.HookManager()
hm.MouseMove = onMouseMove


def setOnRButton(func):
    hm.MouseRightDown = func

def setOnMButton(func):
    hm.MouseMiddleDown = func

def hookMouse():
    hm.HookMouse()

def unhookMouse():
    hm.UnhookMouse()

def setOnRButtonUp(func):
    hm.MouseRightUp = func

def setOnMButtonUp(func):
    hm.MouseMiddleUp = func

def setOnAllMouse(func):
    global onMouseAll #pylint: disable=global-statement
    onMouseAll = func
    hm.HookMouse()


def GetCursorPos():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt.x, pt.y


mouse_event = windll.user32.mouse_event
mouse_event.restype = None
mouse_event.argtypes = [ctypes.wintypes.DWORD, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD, ctypes.wintypes.DWORD, ctypes.POINTER(ctypes.wintypes.ULONG)]
def win_mouse_event(flags, pos=None):
    x, y = pos if pos else 0, 0
    if pos:
        flags |= MOUSEEVENTF_ABSOLUTE
    mouse_event(flags, x, y, 0, None)


def MDown(pos=None):
    win_mouse_event(MOUSEEVENTF_MIDDLEDOWN, pos)


def MUp(pos=None):
    win_mouse_event(MOUSEEVENTF_MIDDLEUP, pos)


def RDown(pos=None):
    win_mouse_event(MOUSEEVENTF_RIGHTDOWN, pos)


def RUp(pos=None):
    win_mouse_event(MOUSEEVENTF_RIGHTUP, pos)


def block_mouse_move(block):
    global blockMouseMove #pylint: disable=global-statement
    blockMouseMove = block


def GetKeyState(key):
    return windll.user32.GetKeyState(ph.HookConstants.VKeyToID(key)) & 0x8000

def SetKeyState(key, state):
    KEYEVENTF_KEYUP = 0x0002
    if state:
        state = 0
    else:
        state = KEYEVENTF_KEYUP
    key1 = ph.HookConstants.VKeyToID(key)
    windll.user32.keybd_event(key1, windll.user32.MapVirtualKeyA(key1, 0), state , 0)

def MouseGetPos():
    x, y = GetCursorPos()

    child_under_cursor = windll.user32.WindowFromPoint(POINT(x, y))
    buff = ctypes.create_unicode_buffer(512)
    windll.user32.GetClassNameW(child_under_cursor, buff, 510)
    className = buff.value
    window = windll.user32.GetForegroundWindow()
    windll.user32.GetWindowTextW(window, buff, 99)
    activeWindow = buff.value
    return x, y, str(className), str(activeWindow)


def getClassUnderMouse():
    child_under_cursor = windll.user32.WindowFromPoint(POINT(*(GetCursorPos())))
    buff = ctypes.create_unicode_buffer(512)
    windll.user32.GetClassNameW(child_under_cursor, buff, 510)

    buff2 = ctypes.create_unicode_buffer(512)
    windll.user32.GetWindowTextW(child_under_cursor, buff2, 510)
    return str(buff.value) + ':' + str(buff2.value)


if __name__ == "__main__":
    MouseGetPos()
