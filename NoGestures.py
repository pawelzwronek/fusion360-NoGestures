# Author - pawelzwronek
# Description - Disables gestures so you can use RMB to pan and orbit the viewport

# Changelog
# v1.0 - Initial version
# v1.1 - fix GetKeyState() on Win7
#      - merge with NoGesturesNoShift
# v1.2 - build for python 3.7
# v1.3 - fix for Fusion360 v2.0.8609 - June 2020 Update
# v1.4-beta - add switchRMB_MMB bool to remap RMB as MMB and MMB as RMB
# v1.5 - fix for Fusion360 2.0.10027 - April 2021 Update
# v1.6 - fix for Fusion360 2.0.12665 - March 2022 Update
# v1.7 - fix for Fusion360 2.0.17244 - September 2023 Update
#      - python changed to 3.11
# v1.8 - fix for Fusion360 2.0.20256
#      - python changed to 3.12
#      - update SWIG to v4.2.0
# v2.0 - fix hung up on rapid RMB clicks
#      - better RMB response
#      - pure python implementation, no SWIG binaries
# v2.1 - fix not starting when there is a space character in user name
# v2.2 - fix hanging on first Fusion startup after an update
#      - subprocess is now spawned in a background thread so it cannot block
#        Fusion's module loading (e.g. when the new python.exe is briefly
#        locked by antivirus / Windows Defender right after the update)

import math
import threading
import subprocess
import os
import sys
import datetime
import traceback
import tkinter as tk
import time

# pylint: disable=W0603

VERSION = '2.2'
APP_NAME = 'NoGestures'

rmbAsOrbit = False # exclusive with switchRMB_MMB
switchRMB_MMB = False  # exclusive with rmbAsOrbit

logToFile = False
logToConsole = False

# --- Global state (initialized in run()) ---
boot = 'boot'
_tmpPath = None
pid = 0
fromFusion = False
pyt = ''
process = None
_spawn_thread = None
ahk = None
ui = None
root = None


def log(msg):
    global _tmpPath
    if logToFile or logToConsole:
        fracSecs = time.time()
        fracSecs = int((fracSecs - int(fracSecs))*1000)
        msg = f"{datetime.datetime.now().strftime(f'%Y-%m-%d %H:%M:%S.{fracSecs:03}')} {boot}({pid}): {msg}"
        if logToConsole:
            print(msg, flush=True)
        if logToFile:
            if not _tmpPath:
                import tempfile # pylint: disable=C0415
                with tempfile.NamedTemporaryFile(mode='w', delete=False, prefix=APP_NAME + '_', suffix='.log') as tmpFile:
                    if tmpFile and tmpFile.file and tmpFile.name:
                        _tmpPath = tmpFile.name
            if _tmpPath:
                with open(_tmpPath, 'a', encoding='utf-8') as f:
                    f.write(msg + '\n')


# ==================================+++++++++++++++++===================================================================
# ==================================   main script   ===================================================================

def fire_in(func, time_ms, ars=None):
    log('fire in ' + str(time_ms) + ' ' + str(func.__name__) + '(' + str(ars) + ')')
    threading.Timer(time_ms/1000, func, args=ars).start()

xpos = 0
ypos = 0
xpos2 = 0
ypos2 = 0
detecting_move = False
move_detected = False
inFusion = False
rbutton_down = False
mbutton_down = False
shift_pressed = False


def is_in_fusion():
    className = str(ahk.getClassUnderMouse())
    log('className: ' + className)
    return 'QWindowIcon:Fusion360' in className or 'AcApCoreView' in className


def detect_move(start=-1):
    global xpos, ypos, xpos2, ypos2, detecting_move, move_detected
    if isinstance(start, bool) and start:
        detecting_move = True
        move_detected = False
        xpos, ypos = ahk.GetCursorPos()
        fire_in(detect_move, 100)
    elif isinstance(start, bool) and not start:
        detecting_move = False
    elif detecting_move:
        xpos2, ypos2 = ahk.GetCursorPos()
        distance = math.floor(math.sqrt((ypos2-ypos)**2 + (xpos-xpos2)**2) + 0.5)
        if distance > 5:
            move_detected = True
            log('move detected')
            detecting_move = False
        else:
            fire_in(detect_move, 100)


def RButton1(event):
    try:
        if not event.Injected:
            if is_in_fusion():
                log('rdown not injected')
                fire_in(ahk.MDown, 20)
                if rmbAsOrbit or switchRMB_MMB:
                    if not shift_pressed:
                        ahk.SetKeyState('VK_LSHIFT', True) # press SHIFT key
                    else:
                        fire_in(ahk.MUp, 30)
                return False  # block event

            log('rdown not inFusion')
    except Exception: # pylint: disable=W0703
        log(traceback.format_exc())
    return True  # pass event to next hook


def RButtonup1(event):
    try:
        if not event.Injected:
            log('rup1 not injected')
            if rmbAsOrbit or switchRMB_MMB:
                ahk.SetKeyState('VK_LSHIFT', False) # release SHIFT key

            if move_detected:
                fire_in(ahk.MUp, 50)
            else:
                log('no move')
                if (not rmbAsOrbit or not switchRMB_MMB) and shift_pressed:
                    log('no move, shift')
                    ahk.block_mouse_move(True)
                    fire_in(ahk.MUp, 10)
                    fire_in(ahk.block_mouse_move, 100, {False})
                elif switchRMB_MMB:
                    fire_in(ahk.MUp, 20)

            return False  # block event
    except Exception: # pylint: disable=W0703
        log(traceback.format_exc())
    log('rup1 injected')
    return True  # pass event to next hook


def RButton(event):
    global rbutton_down, shift_pressed
    if not event.Injected and is_in_fusion():
        log('rdown not injected')
        rbutton_down = True
        detect_move(True)
        shift_pressed = ahk.GetKeyState('VK_LSHIFT')

        if switchRMB_MMB:
            fire_in(ahk.MDown, 10)
            return False

    if switchRMB_MMB:
        return True

    return RButton1(event)

def RButtonup(event):
    global rbutton_down
    if not event.Injected:
        log('rup not injected')
        detect_move(False)
    else:
        log('rup injected')

    if rbutton_down:
        rbutton_down = False

        if not event.Injected and not move_detected:
            log('no move, shift_pressed: ' + str(shift_pressed))
            if not shift_pressed:
                log('no move, no shift. Show RMB menu')
                ahk.block_mouse_move(True)
                fire_in(ahk.MUp, 0)
                fire_in(ahk.RDown, 10)
                fire_in(ahk.RUp, 100)
                fire_in(ahk.block_mouse_move, 120, {False})

        if switchRMB_MMB:
            if not event.Injected and is_in_fusion():
                log('rup not event.Injected and inFusion')
                fire_in(ahk.MUp, 10)
                return False
            return True

        return RButtonup1(event)
    return True

def MButton(event):
    global shift_pressed, mbutton_down
    if not event.Injected and is_in_fusion():
        mbutton_down = True
        detect_move(True)
        shift_pressed = ahk.GetKeyState('VK_LSHIFT')

    if switchRMB_MMB:
        if not event.Injected and is_in_fusion():
            log('mdown not event.Injected and inFusion')
            return RButton1(event)
        else:
            return True
    else:
        return True

def MButtonup(event):
    global rbutton_down, mbutton_down

    if not event.Injected:
        detect_move(False)

    if mbutton_down:
        mbutton_down = False

        if switchRMB_MMB:
            if not event.Injected and is_in_fusion():
                log('mup not injected and inFusion')
                ret = RButtonup1(event)
                rbutton_down = False
                return ret

    return True


# Fusion callback
def run(context):
    global boot, pid, fromFusion, pyt, process, _spawn_thread, ahk, ui, root

    boot = 'boot'
    fromFusion = context is not None
    if not fromFusion:
        boot = 'main'

    log('fromFusion: ' + str(fromFusion))
    log('__name__: ' + str(__name__))
    log('args: ' + str(sys.argv))

    pid = os.getpid()
    log(APP_NAME + ' v' + VERSION + ' started')

    # find Fusion python interpreter
    pyt = os.path.join(os.path.split(tk.__file__)[0], '..\\..\\python')
    log('exe: ' + pyt)

    # if executed directly from Fusion run this script as a subprocess to avoid
    # lags in mouse events caused by Fusion's python loop
    if fromFusion:
        # Spawn the subprocess in a background thread so a slow or blocking Popen
        # (e.g. antivirus scanning the newly-updated python.exe right after a
        # Fusion 360 update) cannot freeze Fusion's module-loading phase.
        def _do_spawn():
            global process
            try:
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW | subprocess.CREATE_NEW_PROCESS_GROUP  # hide console window
                args = [pyt, __file__, 'main']
                log('running subprocess: ' + str(args))
                process = subprocess.Popen(args, startupinfo=si)
            except Exception:  # pylint: disable=W0703
                log('failed to start subprocess:\n' + traceback.format_exc())
        _spawn_thread = threading.Thread(target=_do_spawn, daemon=True)
        _spawn_thread.start()
        log('bootstrap')
    else:
        try:
            if fromFusion:
                from . import autohotkey as ahk  # pylint: disable=C0415
            else:
                import autohotkey as ahk  # pylint: disable=C0415
        except ImportError:
            log(traceback.format_exc())
            return

        ui = None
        try:
            log('hook RMB')
            ahk.setOnRButton(RButton)
            ahk.setOnRButtonUp(RButtonup)
            log('hook MMB')
            ahk.setOnMButton(MButton)
            ahk.setOnMButtonUp(MButtonup)
            ahk.hookMouse()

            # start hidden Tk window to pump events
            root = tk.Tk()
            root.withdraw()
            log('mainloop starting...')
            root.mainloop()
            log('mainloop ended')
        except Exception:  # pylint: disable=W0703
            log(traceback.format_exc())


def process_terminate():
    process.terminate()


# Fusion callback
def stop(_context):
    log('stop')
    if ui is not None:
        ui.messageBox('stop')
    if _spawn_thread is not None and _spawn_thread.is_alive():
        log('waiting for spawn thread to finish...')
        _spawn_thread.join(timeout=5)
    if process is not None:
        log(f'kill {process.pid}')
        fire_in(process_terminate, 1)
        time.sleep(0.1)
        log('process killed')


if __name__ == '__main__':
    run(None)
    if fromFusion:
        # standalone (for testing) boot phase: keep alive while the subprocess runs
        _boot_root = tk.Tk()
        _boot_root.mainloop()
    stop(None)
    log('end of script')
