__version__ = '1.0.8'

import collections
import os
import re
import sys

_ver_stages = {'dev': 10,'alpha': 20, 'a': 20,'beta': 30, 'b': 30,'c': 40,'RC': 50, 'rc': 50,'pl': 200, 'p': 200,}
_component_re = re.compile(r'([0-9]+|[._+-])')

def _comparable_version(version):
    result = []
    for v in _component_re.split(version):
        if v not in '._+-':
            try:  v = int(v, 10); t = 100
            except ValueError: t = _ver_stages.get(v, 0)
            result.extend((t, v))
    return result

_libc_search = re.compile(b'(__libc_init)' b'|' b'(GLIBC_([0-9.]+))' b'|' br'(libc(_\w+)?\.so(?:\.(\d[0-9.]*))?)', re.ASCII)

def libc_ver(executable=None, lib='', version='', chunksize=16384):
    if executable is None:
        try:
            ver = os.confstr('CS_GNU_LIBC_VERSION');parts = ver.split(maxsplit=1)
            if len(parts) == 2: return tuple(parts)
        except (AttributeError, ValueError, OSError):  pass
        executable = sys.executable
    V = _comparable_version
    if hasattr(os.path, 'realpath'): executable = os.path.realpath(executable)
    with open(executable, 'rb') as f:
        binary = f.read(chunksize);pos = 0
        while pos < len(binary):
            if b'libc' in binary or b'GLIBC' in binary: m = _libc_search.search(binary, pos)
            else: m = None
            if not m or m.end() == len(binary):
                chunk = f.read(chunksize)
                if chunk: binary = binary[max(pos, len(binary) - 1000):] + chunk; pos = 0;continue
                if not m:  break
            libcinit, glibc, glibcversion, so, threads, soversion = [ s.decode('latin1') if s is not None else s for s in m.groups()]
            if libcinit and not lib: lib = 'libc'
            elif glibc:
                if lib != 'glibc': lib = 'glibc';version = glibcversion
                elif V(glibcversion) > V(version): version = glibcversion
            elif so:
                if lib != 'glibc':
                    lib = 'libc'
                    if soversion and (not version or V(soversion) > V(version)): version = soversion
                    if threads and version[-len(threads):] != threads: version = version + threads
            pos = m.end()
    return lib, version

def _norm_version(version, build=''):
    l = version.split('.')
    if build: l.append(build)
    try: ints = map(int, l)
    except ValueError: strings = l
    else: strings = list(map(str, ints))
    version = '.'.join(strings[:3]);return version

_ver_output = re.compile(r'(?:([\w ]+) ([\w.]+) ' r'.*' r'\[.* ([\d.]+)\])')

def _syscmd_ver(system='', release='', version='',  supported_platforms=('win32', 'win16', 'dos')):
    if sys.platform not in supported_platforms: return system, release, version
    import subprocess
    for cmd in ('ver', 'command /c ver', 'cmd /c ver'):
        try: info = subprocess.check_output(cmd, stderr=subprocess.DEVNULL, text=True, shell=True)
        except (OSError, subprocess.CalledProcessError) as why: continue
        else: break
    else: return system, release, version
    info = info.strip();m = _ver_output.match(info)
    if m is not None:
        system, release, version = m.groups()
        if release[-1] == '.': release = release[:-1]
        if version[-1] == '.': version = version[:-1]
        version = _norm_version(version)
    return system, release, version

_WIN32_CLIENT_RELEASES = {
    (5, 0): "2000",
    (5, 1): "XP",
    (5, 2): "2003Server",
    (5, None): "post2003",
    (6, 0): "Vista",
    (6, 1): "7",
    (6, 2): "8",
    (6, 3): "8.1",
    (6, None): "post8.1",
    (10, 0): "10",
    (10, None): "post10",
}

_WIN32_SERVER_RELEASES = {
    (5, 2): "2003Server",
    (6, 0): "2008Server",
    (6, 1): "2008ServerR2",
    (6, 2): "2012Server",
    (6, 3): "2012ServerR2",
    (6, None): "post2012ServerR2",
}

def win32_is_iot():
    return win32_edition() in ('IoTUAP', 'NanoServer', 'WindowsCoreHeadless', 'IoTEdgeOS')

def win32_edition():
    try:
        try: import winreg
        except ImportError: import _winreg as winreg
    except ImportError: pass
    else:
        try:
            cvkey = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion'
            with winreg.OpenKeyEx(winreg.HKEY_LOCAL_MACHINE, cvkey) as key: return winreg.QueryValueEx(key, 'EditionId')[0]
        except OSError: pass
    return None

def win32_ver(release='', version='', csd='', ptype=''):
    try: from sys import getwindowsversion
    except ImportError: return release, version, csd, ptype
    winver = getwindowsversion();maj, min, build = winver.platform_version or winver[:3];version = '{0}.{1}.{2}'.format(maj, min, build);release = (_WIN32_CLIENT_RELEASES.get((maj, min)) or _WIN32_CLIENT_RELEASES.get((maj, None)) or release)
    if winver[:2] == (maj, min):
        try: csd = 'SP{}'.format(winver.service_pack_major)
        except AttributeError:
            if csd[:13] == 'Service Pack ': csd = 'SP' + csd[13:]
    if getattr(winver, 'product_type', None) == 3: release = (_WIN32_SERVER_RELEASES.get((maj, min)) or _WIN32_SERVER_RELEASES.get((maj, None)) or release)
    try:
        try: import winreg
        except ImportError:  import _winreg as winreg
    except ImportError: pass
    else:
        try:
            cvkey = r'SOFTWARE\Microsoft\Windows NT\CurrentVersion'
            with winreg.OpenKeyEx(HKEY_LOCAL_MACHINE, cvkey) as key: ptype = QueryValueEx(key, 'CurrentType')[0]
        except: pass
    return release, version, csd, ptype


def _mac_ver_xml():
    fn = '/System/Library/CoreServices/SystemVersion.plist'
    if not os.path.exists(fn): return None
    try: import plistlib
    except ImportError: return None
    with open(fn, 'rb') as f:  pl = plistlib.load(f)
    release = pl['ProductVersion'];versioninfo = ('', '', '');machine = os.uname().machine
    if machine in ('ppc', 'Power Macintosh'): machine = 'PowerPC'
    return release, versioninfo, machine


def mac_ver(release='', versioninfo=('', '', ''), machine=''):
    info = _mac_ver_xml()
    if info is not None:
        return info
    return release, versioninfo, machine

def _java_getprop(name, default):
    from java.lang import System
    try:
        value = System.getProperty(name)
        if value is None: return default
        return value
    except AttributeError: return default

def java_ver(release='', vendor='', vminfo=('', '', ''), osinfo=('', '', '')):
    try:  import java.lang
    except ImportError:  return release, vendor, vminfo, osinfo
    vendor = _java_getprop('java.vendor', vendor);release = _java_getprop('java.version', release);vm_name, vm_release, vm_vendor = vminfo;vm_name = _java_getprop('java.vm.name', vm_name);vm_vendor = _java_getprop('java.vm.vendor', vm_vendor);vm_release = _java_getprop('java.vm.version', vm_release);vminfo = vm_name, vm_release, vm_vendor;os_name, os_version, os_arch = osinfo;os_arch = _java_getprop('java.os.arch', os_arch);os_name = _java_getprop('java.os.name', os_name);os_version = _java_getprop('java.os.version', os_version);osinfo = os_name, os_version, os_arch
    return release, vendor, vminfo, osinfo

def system_alias(system, release, version):
    if system == 'SunOS':
        if release < '5': return system, release, version
        l = release.split('.')
        if l:
            try: major = int(l[0])
            except ValueError: pass
            else:  major = major - 3; l[0] = str(major); release = '.'.join(l)
        if release < '6': system = 'Solaris'
        else: system = 'Solaris'
    elif system == 'IRIX64':
        system = 'IRIX'
        if version: version = version + ' (64bit)'
        else: version = '64bit'
    elif system in ('win32', 'win16'):  system = 'Windows'
    return system, release, version


def _platform(*args):
    platform = '-'.join(x.strip() for x in filter(len, args));platform = platform.replace(' ', '_');platform = platform.replace('/', '-');platform = platform.replace('\\', '-');platform = platform.replace(':', '-');platform = platform.replace(';', '-');platform = platform.replace('"', '-');platform = platform.replace('(', '-');platform = platform.replace(')', '-');platform = platform.replace('unknown', '')
    while 1:
        cleaned = platform.replace('--', '-')
        if cleaned == platform: break
        platform = cleaned
    while platform[-1] == '-': platform = platform[:-1]

    return platform

def _node(default=''):
    try: import socket
    except ImportError: return default
    try: return socket.gethostname()
    except OSError: return default

def _follow_symlinks(filepath):
    filepath = os.path.abspath(filepath)
    while os.path.islink(filepath): filepath = os.path.normpath(os.path.join(os.path.dirname(filepath), os.readlink(filepath)))
    return filepath

def _syscmd_uname(option, default=''):
    if sys.platform in ('dos', 'win32', 'win16'): return default
    import subprocess
    try: output = subprocess.check_output(('uname', option),stderr=subprocess.DEVNULL,text=True)
    except (OSError, subprocess.CalledProcessError): return default
    return (output.strip() or default)

def _syscmd_file(target, default=''):
    if sys.platform in ('dos', 'win32', 'win16'): return default
    import subprocess;target = _follow_symlinks(target);env = dict(os.environ, LC_ALL='C')
    try: output = subprocess.check_output(['file', '-b', target], stderr=subprocess.DEVNULL, env=env)
    except (OSError, subprocess.CalledProcessError): return default
    if not output:  return default
    return output.decode('latin-1')

_default_architecture = {'win32': ('', 'WindowsPE'),'win16': ('', 'Windows'),'dos': ('', 'MSDOS'),}

def architecture(executable=sys.executable, bits='', linkage=''):
    if not bits: import struct; size = struct.calcsize('P'); bits = str(size * 8) + 'bit'
    if executable:  fileout = _syscmd_file(executable, '')
    else: fileout = ''
    if not fileout and executable == sys.executable:
        if sys.platform in _default_architecture:
            b, l = _default_architecture[sys.platform]
            if b: bits = b
            if l: linkage = l
        return bits, linkage
    if 'executable' not in fileout and 'shared object' not in fileout: return bits, linkage
    if '32-bit' in fileout: bits = '32bit'
    elif 'N32' in fileout: bits = 'n32bit'
    elif '64-bit' in fileout: bits = '64bit'
    if 'ELF' in fileout: linkage = 'ELF'
    elif 'PE' in fileout:
        if 'Windows' in fileout: linkage = 'WindowsPE'
        else: linkage = 'PE'
    elif 'COFF' in fileout: linkage = 'COFF'
    elif 'MS-DOS' in fileout: linkage = 'MSDOS'
    else: pass
    return bits, linkage

uname_result = collections.namedtuple("uname_result", "system node release version machine processor")
_uname_cache = None

def uname():
    global _uname_cache;no_os_uname = 0
    if _uname_cache is not None: return _uname_cache
    processor = ''
    try: system, node, release, version, machine = os.uname()
    except AttributeError: no_os_uname = 1
    if no_os_uname or not list(filter(None, (system, node, release, version, machine))):
        if no_os_uname: system = sys.platform ;release = '' ;version = '' ;node = _node() ;machine = ''
        use_syscmd_ver = 1
        if system == 'win32':
            release, version, csd, ptype = win32_ver()
            if release and version: use_syscmd_ver = 0
            if not machine:
                if "PROCESSOR_ARCHITEW6432" in os.environ: machine = os.environ.get("PROCESSOR_ARCHITEW6432", '')
                else: machine = os.environ.get('PROCESSOR_ARCHITECTURE', '')
            if not processor: processor = os.environ.get('PROCESSOR_IDENTIFIER', machine)
        if use_syscmd_ver:
            system, release, version = _syscmd_ver(system)
            if system == 'Microsoft Windows': system = 'Windows'
            elif system == 'Microsoft' and release == 'Windows':
                system = 'Windows'
                if '6.0' == version[:3]: release = 'Vista'
                else: release = ''
        if system in ('win32', 'win16'):
            if not version:
                if system == 'win32': version = '32bit'
                else: version = '16bit'
            system = 'Windows'

        elif system[:4] == 'java':
            release, vendor, vminfo, osinfo = java_ver()
            system = 'Java'
            version = ', '.join(vminfo)
            if not version: version = vendor

    if system == 'OpenVMS':
        if not release or release == '0': release = version;version = ''
        try: import vms_lib
        except ImportError: pass
        else:
            csid, cpu_number = vms_lib.getsyi('SYI$_CPU', 0)
            if (cpu_number >= 128): processor = 'Alpha'
            else: processor = 'VAX'
    if not processor: processor = _syscmd_uname('-p', '')
    if system == 'unknown': system = ''
    if node == 'unknown': node = ''
    if release == 'unknown': release = ''
    if version == 'unknown': version = ''
    if machine == 'unknown': machine = ''
    if processor == 'unknown': processor = ''
    if system == 'Microsoft' and release == 'Windows': system = 'Windows';release = 'Vista'
    _uname_cache = uname_result(system, node, release, version, machine, processor)
    return _uname_cache
def system(): return uname().system
def node(): return uname().node
def release(): return uname().release
def version(): return uname().version
def machine(): return uname().machine
def processor(): return uname().processor
_sys_version_parser = re.compile(r'([\w.+]+)\s*'  r'\(#?([^,]+)' r'(?:,\s*([\w ]*)' r'(?:,\s*([\w :]*))?)?\)\s*'  r'\[([^\]]+)\]?', re.ASCII)  
_ironpython_sys_version_parser = re.compile(r'IronPython\s*' r'([\d\.]+)' r'(?: \(([\d\.]+)\))?' r' on (.NET [\d\.]+)', re.ASCII)
_ironpython26_sys_version_parser = re.compile(r'([\d.]+)\s*' r'\(IronPython\s*' r'[\d.]+\s*' r'\(([\d.]+)\) on ([\w.]+ [\d.]+(?: \(\d+-bit\))?)\)')
_pypy_sys_version_parser = re.compile(r'([\w.+]+)\s*' r'\(#?([^,]+),\s*([\w ]+),\s*([\w :]+)\)\s*' r'\[PyPy [^\]]+\]?')
_sys_version_cache = {}

def _sys_version(sys_version=None):
    if sys_version is None: sys_version = sys.version
    result = _sys_version_cache.get(sys_version, None)
    if result is not None: return result
    if 'IronPython' in sys_version:
        name = 'IronPython'
        if sys_version.startswith('IronPython'): match = _ironpython_sys_version_parser.match(sys_version)
        else: match = _ironpython26_sys_version_parser.match(sys_version)
        if match is None: raise ValueError('failed to parse IronPython sys.version: %s' % repr(sys_version))
        version, alt_version, compiler = match.groups(); buildno = ''; builddate = ''
    elif sys.platform.startswith('java'):
        name = 'Jython';match = _sys_version_parser.match(sys_version)
        if match is None: raise ValueError('failed to parse Jython sys.version: %s' % repr(sys_version))
        version, buildno, builddate, buildtime, _ = match.groups()
        if builddate is None: builddate = ''
        compiler = sys.platform
    elif "PyPy" in sys_version:
        name = "PyPy";match = _pypy_sys_version_parser.match(sys_version)
        if match is None: raise ValueError("failed to parse PyPy sys.version: %s" % repr(sys_version))
        version, buildno, builddate, buildtime = match.groups();compiler = ""
    else:
        match = _sys_version_parser.match(sys_version)
        if match is None: raise ValueError('failed to parse CPython sys.version: %s' % repr(sys_version))
        version, buildno, builddate, buildtime, compiler = match.groups(); name = 'CPython'
        if builddate is None: builddate = ''
        elif buildtime: builddate = builddate + ' ' + buildtime

    if hasattr(sys, '_git'): _, branch, revision = sys._git
    elif hasattr(sys, '_mercurial'):  _, branch, revision = sys._mercurial
    else: branch = ''; revision = ''

    l = version.split('.')
    if len(l) == 2: l.append('0'); version = '.'.join(l)
    result = (name, version, branch, revision, buildno, builddate, compiler);_sys_version_cache[sys_version] = result; return result

def python_implementation(): return _sys_version()[0]
def python_version(): return _sys_version()[1]
def python_version_tuple(): return tuple(_sys_version()[1].split('.'))
def python_branch(): return _sys_version()[2]
def python_revision(): return _sys_version()[3]
def python_build():  return _sys_version()[4:6]
def python_compiler(): return _sys_version()[6]

_platform_cache = {}

def platform(aliased=0, terse=0):
    result = _platform_cache.get((aliased, terse), None)
    if result is not None: return result
    system, node, release, version, machine, processor = uname()
    if machine == processor: processor = ''
    if aliased: system, release, version = system_alias(system, release, version)
    if system == 'Darwin':
        macos_release = mac_ver()[0]
        if macos_release: system = 'macOS';release = macos_release
    if system == 'Windows':
        rel, vers, csd, ptype = win32_ver(version)
        if terse: platform = _platform(system, release)
        else: platform = _platform(system, release, version, csd)
    elif system in ('Linux',): libcname, libcversion = libc_ver(sys.executable);platform = _platform(system, release, machine, processor, 'with', libcname+libcversion)
    elif system == 'Java':
        r, v, vminfo, (os_name, os_version, os_arch) = java_ver()
        if terse or not os_name: platform = _platform(system, release, version)
        else: platform = _platform(system, release, version,  'on', os_name, os_version, os_arch)
    else:
        if terse: platform = _platform(system, release)
        else: bits, linkage = architecture(sys.executable);platform = _platform(system, release, machine, processor, bits, linkage)
    _platform_cache[(aliased, terse)] = platform;return platform


print(platform())