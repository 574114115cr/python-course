r"""统一给 slidep / swc 准备可写的临时目录。

背景：2026-10-28 起本机 `TEMP` 指向 `...\Temp\workbuddy-update-x64-workbuddy`，
@swc/core 的原生 binding 要在 TEMP 里"物化"缓存，写到那里会失败，报
`Failed to load native binding / cannot determine native addon user cache`。
表现是 slidep 的 create 成功但只产出 0 页 pptx，upsert 全部静默失败
（一度把 8 个单元的课件写成了空文件）。

所以在调用任何 slidep 之前，把 TMP / TEMP / SWC_NATIVE_BINDING_CACHE
指到仓库内的可写目录。

用法：
    import slidep_env
    slidep_env.prepare()      # 越早调用越好，必须在 subprocess 之前
"""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def prepare(verbose=False):
    tmp = os.path.join(ROOT, ".cache", "tmp")
    swc = os.path.join(ROOT, ".cache", "swc_cache")
    os.makedirs(tmp, exist_ok=True)
    os.makedirs(swc, exist_ok=True)
    os.environ["TMP"] = tmp
    os.environ["TEMP"] = tmp
    os.environ["SWC_NATIVE_BINDING_CACHE"] = swc
    if verbose:
        print(f"  slidep 临时目录：{tmp}")
        print(f"  swc 缓存目录：{swc}")
    return tmp
