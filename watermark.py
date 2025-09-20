#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片水印工具
根据EXIF拍摄时间信息为图片添加水印
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List

from PIL import Image, ImageDraw, ImageFont
import exifread


class WatermarkTool:
    """图片水印工具主类"""
    
    def __init__(self):
        """初始化水印工具"""
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp'}
        self.setup_logging()
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stdout),
                logging.FileHandler('watermark.log', encoding='utf-8')
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def extract_exif_datetime(self, image_path: str) -> Optional[str]:
        """
        从图片EXIF信息中提取拍摄时间
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            格式化的日期字符串，如"2024年01月15日"
        """
        try:
            with open(image_path, 'rb') as f:
                tags = exifread.process_file(f, details=False)
            
            # 尝试不同的EXIF时间字段
            datetime_fields = [
                'EXIF DateTimeOriginal',
                'EXIF DateTimeDigitized', 
                'EXIF DateTime',
                'Image DateTime'
            ]
            
            for field in datetime_fields:
                if field in tags:
                    datetime_str = str(tags[field])
                    # 解析EXIF时间格式 "YYYY:MM:DD HH:MM:SS"
                    if ':' in datetime_str:
                        try:
                            dt = datetime.strptime(datetime_str, '%Y:%m:%d %H:%M:%S')
                            return dt.strftime('%Y年%m月%d日')
                        except ValueError:
                            continue
            
            # 如果没有找到EXIF时间，使用文件修改时间
            self.logger.warning(f"未找到EXIF时间信息，使用文件修改时间: {image_path}")
            file_time = os.path.getmtime(image_path)
            dt = datetime.fromtimestamp(file_time)
            return dt.strftime('%Y年%m月%d日')
            
        except Exception as e:
            self.logger.error(f"提取EXIF信息失败 {image_path}: {e}")
            return None
    
    def get_position_coordinates(self, position: str, image_size: Tuple[int, int], 
                               text_size: Tuple[int, int], margin: int = 20) -> Tuple[int, int]:
        """
        根据位置参数计算水印坐标
        
        Args:
            position: 位置字符串
            image_size: 图片尺寸 (width, height)
            text_size: 文本尺寸 (width, height)
            margin: 边距
            
        Returns:
            水印坐标 (x, y)
        """
        img_width, img_height = image_size
        text_width, text_height = text_size
        
        position_map = {
            'top-left': (margin, margin),
            'top-right': (img_width - text_width - margin, margin),
            'top-center': ((img_width - text_width) // 2, margin),
            'center': ((img_width - text_width) // 2, (img_height - text_height) // 2),
            'bottom-left': (margin, img_height - text_height - margin),
            'bottom-right': (img_width - text_width - margin, img_height - text_height - margin),
            'bottom-center': ((img_width - text_width) // 2, img_height - text_height - margin)
        }
        
        return position_map.get(position, position_map['bottom-right'])
    
    def parse_color(self, color_str: str) -> Tuple[int, int, int]:
        """
        解析颜色字符串
        
        Args:
            color_str: 颜色字符串
            
        Returns:
            RGB颜色元组
        """
        color_map = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255)
        }
        
        if color_str.lower() in color_map:
            return color_map[color_str.lower()]
        
        # 处理十六进制颜色
        if color_str.startswith('#'):
            hex_color = color_str[1:]
            if len(hex_color) == 6:
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # 处理RGB格式
        if color_str.startswith('rgb(') and color_str.endswith(')'):
            rgb_values = color_str[4:-1].split(',')
            if len(rgb_values) == 3:
                return tuple(int(x.strip()) for x in rgb_values)
        
        # 默认返回白色
        return (255, 255, 255)
    
    def add_watermark(self, image_path: str, output_path: str, watermark_text: str,
                     font_size: int = 24, color: str = 'white', 
                     position: str = 'bottom-right', opacity: float = 0.8) -> bool:
        """
        为图片添加水印
        
        Args:
            image_path: 输入图片路径
            output_path: 输出图片路径
            watermark_text: 水印文本
            font_size: 字体大小
            color: 颜色
            position: 位置
            opacity: 透明度
            
        Returns:
            是否成功
        """
        try:
            # 打开图片
            with Image.open(image_path) as img:
                # 转换为RGBA模式以支持透明度
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                
                # 创建透明图层用于绘制水印
                watermark_layer = Image.new('RGBA', img.size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(watermark_layer)
                
                # 尝试加载字体，如果失败则使用默认字体
                try:
                    font = ImageFont.truetype("arial.ttf", font_size)
                except:
                    try:
                        font = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", font_size)
                    except:
                        font = ImageFont.load_default()
                
                # 获取文本尺寸
                bbox = draw.textbbox((0, 0), watermark_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]
                
                # 计算水印位置
                x, y = self.get_position_coordinates(position, img.size, (text_width, text_height))
                
                # 解析颜色
                rgb_color = self.parse_color(color)
                # 应用透明度
                alpha = int(255 * opacity)
                rgba_color = (*rgb_color, alpha)
                
                # 绘制水印文本
                draw.text((x, y), watermark_text, font=font, fill=rgba_color)
                
                # 将水印图层合成到原图
                watermarked = Image.alpha_composite(img, watermark_layer)
                
                # 转换回RGB模式并保存
                if watermarked.mode == 'RGBA':
                    # 创建白色背景
                    background = Image.new('RGB', watermarked.size, (255, 255, 255))
                    background.paste(watermarked, mask=watermarked.split()[-1])
                    watermarked = background
                
                watermarked.save(output_path, quality=95)
                
            return True
            
        except Exception as e:
            self.logger.error(f"添加水印失败 {image_path}: {e}")
            return False
    
    def process_directory(self, input_dir: str, output_dir: str, font_size: int = 24,
                        color: str = 'white', position: str = 'bottom-right', 
                        opacity: float = 0.8) -> Tuple[int, int]:
        """
        批量处理目录中的图片
        
        Args:
            input_dir: 输入目录
            output_dir: 输出目录
            font_size: 字体大小
            color: 颜色
            position: 位置
            opacity: 透明度
            
        Returns:
            (成功数量, 失败数量)
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        
        # 创建输出目录
        output_path.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        fail_count = 0
        
        # 获取所有支持的图片文件
        image_files = []
        for ext in self.supported_formats:
            image_files.extend(input_path.glob(f'*{ext}'))
            image_files.extend(input_path.glob(f'*{ext.upper()}'))
        
        if not image_files:
            self.logger.warning(f"在目录 {input_dir} 中未找到支持的图片文件")
            return 0, 0
        
        self.logger.info(f"找到 {len(image_files)} 个图片文件，开始处理...")
        
        for image_file in image_files:
            self.logger.info(f"处理文件: {image_file.name}")
            
            # 提取拍摄时间
            datetime_str = self.extract_exif_datetime(str(image_file))
            if not datetime_str:
                self.logger.warning(f"无法提取时间信息，跳过文件: {image_file.name}")
                fail_count += 1
                continue
            
            # 生成输出文件名
            output_file = output_path / f"{image_file.stem}_watermark{image_file.suffix}"
            
            # 添加水印
            if self.add_watermark(str(image_file), str(output_file), datetime_str,
                                font_size, color, position, opacity):
                success_count += 1
                self.logger.info(f"成功处理: {image_file.name} -> {output_file.name}")
            else:
                fail_count += 1
        
        return success_count, fail_count
    
    def interactive_mode(self):
        """交互式模式"""
        print("欢迎使用图片水印工具！")
        print("=" * 50)
        
        # 获取输入目录
        while True:
            input_dir = input("请输入图片目录路径: ").strip()
            if os.path.exists(input_dir) and os.path.isdir(input_dir):
                break
            print("目录不存在，请重新输入！")
        
        # 获取参数
        font_size_input = input("请输入字体大小 (默认24): ").strip()
        font_size = int(font_size_input) if font_size_input.isdigit() else 24
        
        color = input("请输入水印颜色 (默认white): ").strip() or 'white'
        
        position_input = input("请输入水印位置 (默认bottom-right): ").strip()
        position = position_input or 'bottom-right'
        
        opacity_input = input("请输入透明度 (默认0.8): ").strip()
        opacity = float(opacity_input) if opacity_input.replace('.', '').isdigit() else 0.8
        
        # 生成输出目录
        input_path = Path(input_dir)
        output_dir = input_path / f"{input_path.name}_watermark"
        
        print(f"\n开始处理...")
        print(f"输入目录: {input_dir}")
        print(f"输出目录: {output_dir}")
        print(f"字体大小: {font_size}")
        print(f"颜色: {color}")
        print(f"位置: {position}")
        print(f"透明度: {opacity}")
        print("-" * 50)
        
        # 处理图片
        success_count, fail_count = self.process_directory(
            input_dir, str(output_dir), font_size, color, position, opacity
        )
        
        print(f"\n处理完成！")
        print(f"成功: {success_count} 个文件")
        print(f"失败: {fail_count} 个文件")
        print(f"输出目录: {output_dir}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='图片水印工具 - 根据EXIF拍摄时间信息为图片添加水印',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python watermark.py --input /path/to/images
  python watermark.py --input /path/to/images --font-size 32 --color red --position top-left
  python watermark.py  # 进入交互式模式
        """
    )
    
    parser.add_argument('--input', '-i', 
                       help='输入图片目录路径')
    parser.add_argument('--font-size', '-s', type=int, default=24,
                       help='字体大小 (默认: 24)')
    parser.add_argument('--color', '-c', default='white',
                       help='水印颜色 (默认: white)')
    parser.add_argument('--position', '-p', default='bottom-right',
                       choices=['top-left', 'top-right', 'top-center', 'center', 
                               'bottom-left', 'bottom-right', 'bottom-center'],
                       help='水印位置 (默认: bottom-right)')
    parser.add_argument('--opacity', '-o', type=float, default=0.8,
                       help='透明度 (默认: 0.8)')
    parser.add_argument('--output', '-out',
                       help='输出目录 (可选，默认自动生成)')
    
    args = parser.parse_args()
    
    # 创建水印工具实例
    tool = WatermarkTool()
    
    # 如果没有提供输入目录，进入交互式模式
    if not args.input:
        tool.interactive_mode()
        return
    
    # 验证输入目录
    if not os.path.exists(args.input):
        print(f"错误: 目录不存在: {args.input}")
        sys.exit(1)
    
    if not os.path.isdir(args.input):
        print(f"错误: 不是目录: {args.input}")
        sys.exit(1)
    
    # 生成输出目录
    if args.output:
        output_dir = args.output
    else:
        input_path = Path(args.input)
        output_dir = str(input_path / f"{input_path.name}_watermark")
    
    print(f"输入目录: {args.input}")
    print(f"输出目录: {output_dir}")
    print(f"字体大小: {args.font_size}")
    print(f"颜色: {args.color}")
    print(f"位置: {args.position}")
    print(f"透明度: {args.opacity}")
    print("-" * 50)
    
    # 处理图片
    success_count, fail_count = tool.process_directory(
        args.input, output_dir, args.font_size, 
        args.color, args.position, args.opacity
    )
    
    print(f"\n处理完成！")
    print(f"成功: {success_count} 个文件")
    print(f"失败: {fail_count} 个文件")
    print(f"输出目录: {output_dir}")


if __name__ == '__main__':
    main()
