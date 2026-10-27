"""生成 assets/css/fonts.css，并把用到的字体文件复制到 static/fonts/。

西文取自 Fontsource 的 npm 包（需要 npm），版本见 FONTS。
中文使用华为官方原始 TTF，不转换格式、不修改或裁剪字体文件。
用法：python3 scripts/gen_fonts.py [--harmony-zip /path/to/HarmonyOS-Sans.zip]
不传 --harmony-zip 时使用 static/fonts/harmonyos-sans-sc/ 中已提交的字体。
"""
import argparse
import json
import re
import shutil
import subprocess
import tarfile
import tempfile
from dataclasses import dataclass
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent

# 仅在 CSS 中限定中日韩码位，字体文件本身保持原样。
# 拉丁字母、通用符号与 emoji 继续使用原来的字体。
CJK_UNICODE_RANGE = (
    "U+2e80-2fdf,U+2ff0-2fff,U+3000-303f,U+3040-30ff,U+3100-312f,"
    "U+3190-31ff,U+3200-33ff,U+3400-4dbf,U+4e00-9fff,U+f900-faff,"
    "U+fe10-fe1f,U+fe30-fe4f,U+ff00-ffef,U+20000-3ffff"
)


@dataclass
class Font:
    package: str
    version: str
    css: list[str]  # 包内要用的 CSS，文件名决定可变轴与正斜体
    family: str
    slug: str  # static/fonts/ 下的目录名


FONTS = [
    # opsz 版带光学尺寸轴：正文与大标题自动用不同字形
    Font("@fontsource-variable/source-serif-4", "5.3.0", ["opsz.css", "opsz-italic.css"],
         "Source Serif 4", "source-serif-4"),
    Font("@fontsource-variable/cascadia-code", "5.3.0", ["wght.css", "wght-italic.css"],
         "Cascadia Code", "cascadia-code"),
]

HARMONY_SOURCE = "https://developer.huawei.com/images/download/general/HarmonyOS-Sans.zip"
HARMONY_SLUG = "harmonyos-sans-sc"
# 中文 600–900 共用原始 Bold，避免为标题再下载一份约 8 MiB 的字体。
# 只影响这个中文 font-face；西文字体仍使用自身的可变字重。
HARMONY_WEIGHTS = [("Regular", "400"), ("Medium", "500"), ("Bold", "600 900")]


def render_face(properties):
    return "@font-face {\n" + "".join(
        f"  {key}: {value};\n" for key, value in properties.items()
    ) + "}\n"


def import_harmony_fonts(archive):
    """从官方压缩包复制原始文件，不执行字体格式转换或子集化。"""
    dst = ROOT / "static/fonts" / HARMONY_SLUG
    names = [f"HarmonyOS_Sans_SC_{style}.ttf" for style, _ in HARMONY_WEIGHTS]
    with ZipFile(archive) as package:
        prefix = "HarmonyOS Sans/HarmonyOS_Sans_SC/"
        # 先读取完整组文件，避免压缩包缺项时只写入部分字体。
        files = {name: package.read(prefix + name) for name in names + ["LICENSE.txt"]}
    dst.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (dst / name).write_bytes(data)


def harmony_faces():
    dst = ROOT / "static/fonts" / HARMONY_SLUG
    names = [f"HarmonyOS_Sans_SC_{style}.ttf" for style, _ in HARMONY_WEIGHTS]
    for name in names + ["LICENSE.txt"]:
        if not (dst / name).is_file():
            raise FileNotFoundError(f"缺少 {dst / name}，请通过 --harmony-zip 导入官方字体包")
    for style, weight in HARMONY_WEIGHTS:
        name = f"HarmonyOS_Sans_SC_{style}.ttf"
        local_name = "HarmonyOS_Sans_SC" if style == "Regular" else f"HarmonyOS_Sans_SC_{style}"
        yield render_face({
            "font-family": "'HarmonyOS Sans SC CJK'",
            "font-style": "normal",
            "font-display": "swap",
            "font-weight": weight,
            "src": (f"local('{local_name}'), "
                    f"url(../fonts/{HARMONY_SLUG}/{name}) format('truetype')"),
            "unicode-range": CJK_UNICODE_RANGE,
        })


def fetch(font, tmp):
    """npm pack 下载并解压，返回包目录。"""
    out = subprocess.run(
        ["npm", "pack", "--json", f"{font.package}@{font.version}"],
        cwd=tmp, check=True, capture_output=True, text=True,
    ).stdout
    with tarfile.open(tmp / json.loads(out)[0]["filename"]) as tar:
        tar.extractall(tmp / font.slug, filter="data")
    return tmp / font.slug / "package"


def font_faces(font, pkg):
    """改写包内的 @font-face 并复制所需字体文件，逐条返回 CSS。"""
    dst = ROOT / "static/fonts" / font.slug
    shutil.rmtree(dst, ignore_errors=True)
    dst.mkdir(parents=True)
    shutil.copy2(pkg / "LICENSE", dst)

    for css in font.css:
        for body in re.findall(r"@font-face \{(.*?)\}", (pkg / css).read_text(), re.S):
            face = dict(re.findall(r"([\w-]+): ([^;]+);", body))
            file = re.search(r"url\(\./files/([^)]+)\)", face["src"]).group(1)
            shutil.copy2(pkg / "files" / file, dst)
            face["font-family"] = f"'{font.family}'"
            face["src"] = face["src"].replace("./files/", f"../fonts/{font.slug}/")
            yield render_face(face)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--harmony-zip", type=Path, help="华为官方 HarmonyOS-Sans.zip")
    args = parser.parse_args()
    if args.harmony_zip:
        import_harmony_fonts(args.harmony_zip)
    harmony = list(harmony_faces())
    header = ["/* 由 scripts/gen_fonts.py 生成，请勿手改。西文字体为 SIL Open Font License 1.1。"]
    header += [f" * {f.family}: {f.package}@{f.version}" for f in FONTS]
    header += [f" * HarmonyOS Sans SC CJK: {HARMONY_SOURCE}",
               " * HarmonyOS Sans Fonts License Agreement；原始 TTF，许可见字体目录。"]
    blocks = ["\n".join(header) + "\n */\n"]
    with tempfile.TemporaryDirectory() as tmp:
        for font in FONTS:
            blocks += font_faces(font, fetch(font, Path(tmp)))
    blocks += harmony
    (ROOT / "assets/css/fonts.css").write_text("\n".join(blocks))


if __name__ == "__main__":
    main()
