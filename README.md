# 图片水印工具 (Photo Watermark Tool)

一个基于Python的命令行程序，用于为图片添加基于EXIF拍摄时间信息的水印。

## 功能特性

- 📸 **EXIF信息提取**：自动从图片EXIF数据中提取拍摄时间
- 🎨 **自定义水印样式**：支持字体大小、颜色、位置、透明度设置
- 📁 **批量处理**：支持目录下所有图片的批量处理
- 🖥️ **多种使用方式**：命令行参数和交互式模式
- 📝 **详细日志**：处理进度和错误信息记录
- 📅 **日期格式**：水印文本格式为"YYYY-MM-DD"（如：2024-01-15）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行模式

```bash
# 基本使用
python watermark.py --input /path/to/images

# 自定义参数
python watermark.py --input /path/to/images --font-size 32 --color red --position top-left

# 查看帮助
python watermark.py --help
```

### 交互式模式

```bash
python watermark.py
```

程序会引导您输入各种参数。

## 参数说明

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--input` | `-i` | - | 输入图片目录路径 |
| `--font-size` | `-s` | 24 | 字体大小 (8-200) |
| `--color` | `-c` | white | 水印颜色 |
| `--position` | `-p` | bottom-right | 水印位置 |
| `--opacity` | `-o` | 0.8 | 透明度 (0.0-1.0) |
| `--output` | `-out` | 自动生成 | 输出目录 |

### 支持的位置

- `top-left`：左上角
- `top-right`：右上角
- `top-center`：顶部居中
- `center`：居中
- `bottom-left`：左下角
- `bottom-right`：右下角
- `bottom-center`：底部居中

### 支持的颜色格式

- 颜色名称：`white`, `black`, `red`, `green`, `blue`, `yellow`, `cyan`, `magenta`
- 十六进制：`#FF0000`, `#FFFFFF`
- RGB格式：`rgb(255,0,0)`

## 输出说明

- **输出目录**：`{原目录名}_watermark`
- **文件命名**：`{原文件名}_watermark.{扩展名}`
- **支持格式**：JPEG、PNG、TIFF、BMP

## 使用示例

### 示例1：基本使用
```bash
python watermark.py --input ./photos
```

### 示例2：自定义样式
```bash
python watermark.py --input ./photos --font-size 32 --color red --position top-left --opacity 0.6
```

### 示例3：交互式模式
```bash
python watermark.py
# 然后按提示输入参数
```

## 技术特性

- **Python版本**：3.7+
- **主要依赖**：Pillow、exifread
- **跨平台支持**：Windows、macOS、Linux
- **内存优化**：处理大图片时内存占用控制
- **错误处理**：完善的异常处理和日志记录

## 日志文件

程序运行时会生成 `watermark.log` 日志文件，记录详细的处理信息。

## 注意事项

1. 确保输入目录存在且包含支持的图片文件
2. 程序会自动创建输出目录
3. 如果EXIF信息不存在，会使用文件修改时间作为备选
4. 处理大图片时可能需要较长时间

## 开发信息

- **项目结构**：详见PRD.md文档
- **开发周期**：10周
- **测试覆盖**：功能测试、性能测试、兼容性测试

## 许可证

MIT License
