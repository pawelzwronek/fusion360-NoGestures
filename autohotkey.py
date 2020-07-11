# import pythoncom, pyHook
import ctypes
# from threading import Timer
from ctypes import oledll, windll, byref, POINTER
from ctypes.wintypes import POINT, HWND
# from comtypes.client import wrap
# from comtypes.automation import VARIANT
# from comtypes import IUnknown
try:
    from . import pyHook as ph
except:
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
# WM_MOUSEMOVE                    0x0200


def printMouseEvent(event):
    print('MessageName:', event.MessageName)
    print('Message:', event.Message)
    print('Time:', event.Time)
    print('Window:', event.Window)
    print('WindowName:', event.WindowName)
    print('Position:', event.Position)
    print('Wheel:', event.Wheel)
    print('Injected:', event.Injected)
    print('---')


blockMouseMove = False
onMouseAll = None


def onMouseMove(event):
    global blockMouseMove
    if blockMouseMove:
        return False
    return True

# create a hook manager
hm = ph.HookManager()
hm.MouseMove = onMouseMove


def setOnRButton(func):
    hm.MouseRightDown = func
    # hm.HookMouse()


def hookMouse():
    hm.HookMouse()


def setOnRButtonUp(func):
    hm.MouseRightUp = func
    # hm.HookMouse()


def setOnAllMouse(func):
    global onMouseAll
    onMouseAll = func
    hm.HookMouse()


def GetCursorPos():
    pt = POINT()
    windll.user32.GetCursorPos(byref(pt))
    return pt.x, pt.y


def mouse_event(flags, pos=None):
    x, y = pos if pos else 0, 0
    if pos:
        flags |= MOUSEEVENTF_ABSOLUTE
    windll.user32.mouse_event(flags, x, y, 0, 0)


def MDown(pos=None):
    mouse_event(MOUSEEVENTF_MIDDLEDOWN, pos)


def MUp(pos=None):
    mouse_event(MOUSEEVENTF_MIDDLEUP, pos)


def RDown(pos=None):
    mouse_event(MOUSEEVENTF_RIGHTDOWN, pos)


def RUp(pos=None):
    mouse_event(MOUSEEVENTF_RIGHTUP, pos)


def block_mouse_move(block):
    global blockMouseMove
    blockMouseMove = block


def GetKeyState(key):
    return windll.user32.GetKeyState(ph.HookConstants.VKeyToID(key)) & 0x8000

def SetKeyState(key, state):
    KEYEVENTF_EXTENDEDKEY = 0x0001
    KEYEVENTF_KEYUP = 0x0002
    if state: state = 0
    else:     state = KEYEVENTF_KEYUP
    key1 = ph.HookConstants.VKeyToID(key)
    windll.user32.keybd_event(key1, windll.user32.MapVirtualKeyA(key1, 0), state , 0)

def MouseGetPos():
    # // Returns OK or FAIL.
    # 	// Caller should already have ensured that at least one of these will be non-NULL.
    # 	// The only time this isn't true is for dynamically-built variable names.  In that
    # 	// case, we don't worry about it if it's NULL, since the user will already have been
    # 	// warned:
    x, y = GetCursorPos()

    # pacc, value = AccessibleObjectFromPoint(x, y)
    # try:
    #     name = pacc.accName()
    # except:
    #     name = '----'
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


oleacc = oledll.oleacc

# def AccessibleObjectFromPoint(x, y):
#     pacc = POINTER(IUnknown)()
#     var = VARIANT()
#     oleacc.AccessibleObjectFromPoint(POINT(x, y), byref(pacc), byref(var))
#     return wrap(pacc), var.value

if __name__ == "__main__":
    MouseGetPos()
