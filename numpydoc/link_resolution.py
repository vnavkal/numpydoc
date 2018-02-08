import inspect
import os
import sys


def _locate(module_name, obj_name):
    class_name = obj_name.split('.')[0]
    if type(class_name) != str:
        # Python 2 only
        class_name = class_name.encode('utf-8')
    module = __import__(module_name, fromlist=[class_name])
    obj = getattr(module, obj_name)

    try:
        path = inspect.getsourcefile(obj)
    except Exception:
        path = None
    if not path:
        try:
            path = inspect.getsourcefile(sys.modules[obj.__module__])
        except Exception:
            path = None
    if not path:
        return

    try:
        source, start = inspect.getsourcelines(obj)
        end = start - len(source) + 1
    except Exception:
        start = None
        end = None

    return path, start, end


def _linkcode_resolve(domain, info, package, url_fmt, revision):
    """Determine a link to online source for a class/method/function

    This is called by sphinx.ext.linkcode

    An example with a long-untouched module that everyone has
    >>> _linkcode_resolve('py', {'module': 'tty',
    ...                          'fullname': 'setraw'},
    ...                   package='tty',
    ...                   url_fmt='http://hg.python.org/cpython/file/'
    ...                           '{revision}/Lib/{package}/{path}#L{lineno}',
    ...                   revision='xxxx')
    'http://hg.python.org/cpython/file/xxxx/Lib/tty/tty.py#L18'
    """

    if revision is None:
        return
    if domain not in ('py', 'pyx'):
        return
    if not info.get('module') or not info.get('fullname'):
        return

    class_name = info['fullname'].split('.')[0]
    if type(class_name) != str:
        # Python 2 only
        class_name = class_name.encode('utf-8')
    module = __import__(info['module'], fromlist=[class_name])
    obj = attrgetter(info['fullname'])(module)

    try:
        fn = inspect.getsourcefile(obj)
    except Exception:
        fn = None
    if not fn:
        try:
            fn = inspect.getsourcefile(sys.modules[obj.__module__])
        except Exception:
            fn = None
    if not fn:
        return

    fn = os.path.relpath(fn,
                         start=os.path.dirname(__import__(package).__file__))
    try:
        lineno = inspect.getsourcelines(obj)[1]
    except Exception:
        lineno = ''
    return url_fmt.format(revision=revision, package=package,
                          path=fn, lineno=lineno)
