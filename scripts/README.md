# 字体维护

Hugo 使用已提交的 `assets/css/fonts.css` 和 `static/fonts/`，日常构建无需重新生成字体。

重新生成需要 Python 3.12+ 和 npm，在仓库根目录运行：

```sh
python3 scripts/gen_fonts.py
```

脚本从固定版本的 Fontsource npm 包获取西文字体，复用仓库中的中文字体。字体栈、标题和正文样式在 `assets/css/custom.css` 中维护。

## HarmonyOS Sans SC

从[华为官方字体包](https://developer.huawei.com/images/download/general/HarmonyOS-Sans.zip)导入或更新：

```sh
python3 scripts/gen_fonts.py --harmony-zip /path/to/HarmonyOS-Sans.zip
```

- 保留原始 TTF 和 `LICENSE.txt`，不进行格式转换或子集化。
- CSS 仅覆盖中日韩字符，西文字体保持不变。
- Regular 对应 400，Medium 对应 500，600–900 共用 Bold。
- 三份 TTF 合计约 23.5 MiB，优先使用本机字体，否则按需下载。

## 思源宋体（中文标题）

使用 Adobe 官方的简体地区子集可变字体 `SourceHanSerifCN-VF.otf.woff2`，字重范围为 250–900。
原始字体及许可证保存在 `static/fonts/source-han-serif-cn/`，不自行转换或裁剪。

`--font-heading` 用于各级标题、标签目录和搜索结果中的文章标题。
它仅替换中文字体，英文、正文和代码的字体分别由原有字体栈决定。
字体约 9.9 MiB，使用 `font-display: swap`。

如需重新下载，在仓库根目录运行：

```sh
mkdir -p static/fonts/source-han-serif-cn
curl -fLsS -o static/fonts/source-han-serif-cn/SourceHanSerifCN-VF.otf.woff2 \
  https://raw.githubusercontent.com/adobe-fonts/source-han-serif/7889f11bf31170b5d092a083b357c8c8130f89e0/Variable/WOFF2/OTF/Subset/SourceHanSerifCN-VF.otf.woff2
curl -fLsS -o static/fonts/source-han-serif-cn/LICENSE.txt \
  https://raw.githubusercontent.com/adobe-fonts/source-han-serif/7889f11bf31170b5d092a083b357c8c8130f89e0/LICENSE.txt
```

更新后运行 `hugo --gc --minify` 验证构建。
