%module cpyHook
%include typemaps.i

%{
  #include "windows.h"

  PyObject* callback_funcs[WH_MAX];
  HHOOK hHooks[WH_MAX];
%}

#ifdef SWIGPYTHON
%typemap(in) PyObject *pyfunc {
  if (!PyCallable_Check($input)) {
    PyErr_SetString(PyExc_TypeError, "Need a callable object");
    return NULL;
  }
  $1 = $input;
}
#endif

%init %{
  memset(callback_funcs, 0, WH_MAX * sizeof(PyObject*));
  memset(hHooks, 0, WH_MAX * sizeof(HHOOK));
%}

%wrapper %{
  LRESULT CALLBACK cLLMouseCallback(int code, WPARAM wParam, LPARAM lParam) {
    PyObject *arglist, *r;
    PMSLLHOOKSTRUCT ms;
    static long result;
    long pass = 1;
    PyGILState_STATE gil;

    // get the GIL
    gil = PyGILState_Ensure();

    //pass the message on to the Python function
    ms = (PMSLLHOOKSTRUCT)lParam;

    //build the argument list to the callback function
	arglist = Py_BuildValue("(iiiiiiiz)", wParam, ms->pt.x, ms->pt.y, ms->mouseData,
                            ms->flags, ms->time, NULL, NULL);
    r = PyObject_CallObject(callback_funcs[WH_MOUSE_LL], arglist);

    // check if we should pass the event on or not
    if(r == NULL) {
        if (PyErr_Occurred()) {
            PyErr_Print();
            PyErr_Clear();
        }
    } else {
      pass = PyInt_AsLong(r);
      Py_XDECREF(r);
	}
    Py_DECREF(arglist);
    // release the GIL
    PyGILState_Release(gil);

    // decide whether or not to call the next hook
    if(code < 0 || pass)
      result = CallNextHookEx(hHooks[WH_MOUSE_LL], code, wParam, lParam);
    else {
    	// return non-zero to prevent further processing
      result = 42;
    }
    return result;
  }

  int cSetHook(int idHook, PyObject *pyfunc) {
    HINSTANCE hMod;

    //make sure we have a valid hook number
    if(idHook > WH_MAX || idHook < WH_MIN) {
      PyErr_SetString(PyExc_ValueError, "Hooking error: invalid hook ID");
    }

    //get the module handle
    Py_BEGIN_ALLOW_THREADS
    // try to get handle for current file - will succeed if called from a compiled .exe
    hMod = GetModuleHandle(NULL);
    if(NULL == hMod)    // otherwise use name for DLL
        hMod = GetModuleHandle("_cpyHook.pyd");
    Py_END_ALLOW_THREADS

    //switch on the type of hook so we point to the right C callback
    switch(idHook) {
      case WH_MOUSE_LL:
        if(callback_funcs[idHook] != NULL)
          break;

        callback_funcs[idHook] = pyfunc;
        Py_INCREF(callback_funcs[idHook]);

        Py_BEGIN_ALLOW_THREADS
        hHooks[idHook] = SetWindowsHookEx(WH_MOUSE_LL, cLLMouseCallback, (HINSTANCE) hMod, 0);
        Py_END_ALLOW_THREADS
        break;

      default:
       return 0;
    }

    if(!hHooks[idHook]) {
      PyErr_SetString(PyExc_TypeError,hMod == NULL ? "Could not set hook NULL" : "Could not set hook not NULL");
    }
    
    SetPriorityClass(GetCurrentProcess(), REALTIME_PRIORITY_CLASS); //HIGH_PRIORITY_CLASS

    return 1;
  }

  int cUnhook(int idHook) {
    BOOL result;

    //make sure we have a valid hook number
    if(idHook > WH_MAX || idHook < WH_MIN) {
      PyErr_SetString(PyExc_ValueError, "Invalid hook ID");
    }

    //unhook the callback
    Py_BEGIN_ALLOW_THREADS
    result = UnhookWindowsHookEx(hHooks[idHook]);
    Py_END_ALLOW_THREADS

    if(result) {
      //decrease the ref to the Python callback
    	Py_DECREF(callback_funcs[idHook]);
      callback_funcs[idHook] = NULL;
    }

    return result;
  }
%}

int cSetHook(int idHook, PyObject *pyfunc);
int cUnhook(int idHook);
