"""在桌面创建两个标准 Windows 快捷方式（.lnk）。

为什么不用 .url：`[InternetShortcut]` 的 URL 里如果出现百分号编码的中文路径
（%E5%AD%A6%E4%B9%A0 = 学习），Windows shell 不做百分号解码，而是把字节按
ANSI 解读，路径就变成乱码 "å­¦ä¹ "，双击报「找不到文件」。

PowerShell 的 `New-Object -ComObject WScript.Shell` 在本机被安全策略拦截，
所以这里用 ctypes 直接走 COM：
CoCreateInstance(CLSID_ShellLink) → IShellLinkW 设目标 → QueryInterface(IPersistFile) → Save。
GUID 必须用 Structure 布局（用原始字节缓冲会拿到 E_NOINTERFACE）。

用法：python tools/make_desktop_shortcuts.py
"""

import ctypes
import os
import sys
from ctypes import POINTER, byref, c_uint16, c_uint32, c_ubyte, c_void_p

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESK = os.path.join(os.path.expanduser("~"), "Desktop")
WINDIR = os.environ.get("SystemRoot", r"C:\Windows")


class GUID(ctypes.Structure):
    _fields_ = [("Data1", c_uint32), ("Data2", c_uint16),
                ("Data3", c_uint16), ("Data4", c_ubyte * 8)]


def _guid(d1, d2, d3, d4):
    g = GUID()
    g.Data1, g.Data2, g.Data3 = d1, d2, d3
    for i, b in enumerate(d4):
        g.Data4[i] = b
    return g


CLSID_ShellLink = _guid(0x00021401, 0, 0, [0xC0, 0, 0, 0, 0, 0, 0, 0x46])
IID_IShellLinkW = _guid(0x000214F9, 0, 0, [0xC0, 0, 0, 0, 0, 0, 0, 0x46])
IID_IPersistFile = _guid(0x0000010B, 0, 0, [0xC0, 0, 0, 0, 0, 0, 0, 0x46])

ole32 = ctypes.oledll.ole32
ole32.CoInitialize(None)


def vfn(ptr, index, restype, *argtypes):
    """取 COM 接口 vtable 第 index 个方法，带签名。"""
    vt = ctypes.cast(ptr, POINTER(POINTER(c_void_p)))
    proto = ctypes.WINFUNCTYPE(restype, c_void_p, *argtypes)
    return proto(ctypes.cast(vt[0][index], c_void_p).value)


def make_lnk(lnk_path, target, working_dir, description, icon=None):
    p_sl = c_void_p(0)
    hr = ole32.CoCreateInstance(byref(CLSID_ShellLink), None, 1,
                                byref(IID_IShellLinkW), byref(p_sl))
    if hr != 0:
        raise OSError(f"CoCreateInstance 失败 hr=0x{hr & 0xFFFFFFFF:X}")

    # IShellLinkW: SetPath(20) SetWorkingDirectory(9) SetDescription(7)
    #              SetIconLocation(17) SetShowCmd(15)
    vfn(p_sl, 20, ctypes.HRESULT, ctypes.c_wchar_p)(p_sl, target)
    vfn(p_sl, 9, ctypes.HRESULT, ctypes.c_wchar_p)(p_sl, working_dir)
    vfn(p_sl, 7, ctypes.HRESULT, ctypes.c_wchar_p)(p_sl, description)
    vfn(p_sl, 15, ctypes.HRESULT, ctypes.c_int)(p_sl, 1)   # SW_SHOWNORMAL
    if icon:
        vfn(p_sl, 17, ctypes.HRESULT, ctypes.c_wchar_p,
            ctypes.c_int)(p_sl, icon, 0)

    p_pf = c_void_p(0)
    vfn(p_sl, 0, ctypes.HRESULT, ctypes.c_void_p,
        ctypes.c_void_p)(p_sl, byref(IID_IPersistFile), byref(p_pf))
    if not p_pf:
        raise OSError("QueryInterface(IPersistFile) 失败")
    hr = vfn(p_pf, 6, ctypes.HRESULT, ctypes.c_wchar_p,
             ctypes.c_int)(p_pf, lnk_path, 1)
    if hr != 0:
        raise OSError(f"IPersistFile::Save 失败 hr=0x{hr & 0xFFFFFFFF:X}")

    vfn(p_pf, 2, ctypes.c_ulong)(p_pf)     # Release
    vfn(p_sl, 2, ctypes.c_ulong)(p_sl)     # Release
    return lnk_path


def read_back(lnk_path):
    """用同一套 COM 打开 .lnk 并读回目标路径——这才是真校验。"""
    p_sl = c_void_p(0)
    ole32.CoCreateInstance(byref(CLSID_ShellLink), None, 1,
                           byref(IID_IShellLinkW), byref(p_sl))
    p_pf = c_void_p(0)
    vfn(p_sl, 0, ctypes.HRESULT, ctypes.c_void_p,
        ctypes.c_void_p)(p_sl, byref(IID_IPersistFile), byref(p_pf))
    vfn(p_pf, 5, ctypes.HRESULT, ctypes.c_wchar_p,
        ctypes.c_int)(p_pf, lnk_path, 0)          # IPersistFile::Load
    buf = ctypes.create_unicode_buffer(1024)
    vfn(p_sl, 3, ctypes.HRESULT, ctypes.c_wchar_p, ctypes.c_int,
        ctypes.c_void_p, ctypes.c_uint)(p_sl, buf, 1024, None, 0)  # GetPath
    vfn(p_pf, 2, ctypes.c_ulong)(p_pf)
    vfn(p_sl, 2, ctypes.c_ulong)(p_sl)
    return buf.value


def main():
    if not os.path.isdir(DESK):
        sys.exit(f"桌面目录不存在: {DESK}")

    jobs = [
        (os.path.join(DESK, "课程首页.lnk"),
         os.path.join(ROOT, "index.html"), ROOT,
         "Python 课程包 · 课程首页（双击打开）",
         os.path.join(WINDIR, "System32", "imageres.dll")),
        (os.path.join(DESK, "开关课程服务器.lnk"),
         os.path.join(ROOT, "开关课程服务器.bat"), ROOT,
         "Python 课程包 · 启动/停止本地服务器 127.0.0.1:8090",
         os.path.join(WINDIR, "System32", "shell32.dll")),
    ]

    ok = True
    for lnk, target, wd, desc, icon in jobs:
        make_lnk(lnk, target, wd, desc, icon)
        got = read_back(lnk)
        same = os.path.normcase(got) == os.path.normcase(target)
        exists = os.path.exists(got) if got else False
        print(f"{'✓' if same and exists else '✗'} {os.path.basename(lnk)}")
        print(f"    写入: {target}")
        print(f"    读回: {got}")
        print(f"    目标存在: {exists} | 一致: {same} | 大小 {os.path.getsize(lnk)} B")
        ok = ok and same and exists
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
