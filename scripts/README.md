# 字体维护

Hugo 直接使用已提交的 `assets/css/fonts.css` 和 `static/fonts/`，日常构建、部署无需运行生成脚本或访问字体 CDN。

重新生成需要 Python 3.12+ 和 npm，在仓库根目录运行：

```sh
python3 scripts/gen_fonts.py
```

脚本从固定版本的 Fontsource npm 包获取 Source Serif 4 和 Cascadia Code，复用仓库中的 HarmonyOS Sans SC 原始字体。生成的 CSS 不手动编辑；字体栈和正文样式在 `assets/css/custom.css` 中维护。

## HarmonyOS Sans SC

来源：[华为官方字体包](https://developer.huawei.com/images/download/general/HarmonyOS-Sans.zip)。
本次使用的压缩包 SHA-256：

```text
fb02c86e358cd9aad8d4dfa957ee502381e7ee2e94499a9133add4324b6ce69a
```

首次导入或更新官方文件：

```sh
python3 scripts/gen_fonts.py --harmony-zip /path/to/HarmonyOS-Sans.zip
```

- 保留原始 TTF 和 `LICENSE.txt`，不进行格式转换或子集化。页脚声明由 `layouts/partials/extend-footer.html` 输出。
- CSS 仅声明中日韩字符范围，英文、数字、通用符号及代码英文继续使用原来的字体。
- Regular 对应 400，Medium 对应 500；中文 600–900 共用 Bold，西文仍使用自身的可变字重。
- 三份 TTF 合计约 23.5 MiB。浏览器优先使用本机同名字体，否则按需下载整个字重文件；`font-display: swap` 允许加载时先显示回退字体。

更新后检查 CSS、字体及许可的 diff，并运行 `hugo --gc --minify`。预览时检查中英文混排、代码中文、移动端、明暗模式，以及未安装本机字体时的加载。
