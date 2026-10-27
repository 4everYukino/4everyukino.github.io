# 字体维护

Hugo 使用已提交的 `assets/css/fonts.css` 和 `static/fonts/`，日常构建无需重新生成字体。

重新生成需要 Python 3.12+ 和 npm，在仓库根目录运行：

```sh
python3 scripts/gen_fonts.py
```

脚本从固定版本的 Fontsource npm 包获取西文字体，复用仓库中的中文字体。字体栈和正文样式在 `assets/css/custom.css` 中维护。

## HarmonyOS Sans SC

从[华为官方字体包](https://developer.huawei.com/images/download/general/HarmonyOS-Sans.zip)导入或更新：

```sh
python3 scripts/gen_fonts.py --harmony-zip /path/to/HarmonyOS-Sans.zip
```

- 保留原始 TTF 和 `LICENSE.txt`，不进行格式转换或子集化。
- CSS 仅覆盖中日韩字符，西文字体保持不变。
- Regular 对应 400，Medium 对应 500，600–900 共用 Bold。
- 三份 TTF 合计约 23.5 MiB，优先使用本机字体，否则按需下载。

更新后运行 `hugo --gc --minify` 验证构建。
