# PropoxarMathnb

> AI-Powered Calculus Learning Assistant for macOS
> 
> AI驱动的高数学习助手 - macOS桌面应用

[English](#english) | [中文](#中文)

---

## English

### Overview

PropoxarMathnb is a macOS desktop application designed to help students learn calculus (advanced mathematics) more effectively. It uses AI to analyze study materials, identify key concepts, and organize them by importance.

### Current Status

**Version 1.0.0** - This is the first release with basic GUI framework and upload functionality. Many features are still under development.

#### ✅ Implemented
- macOS Liquid Glass UI effect (native NSVisualEffectView)
- Drag & drop file upload (PDF, images, Markdown)
- AI-powered knowledge point extraction
- Importance classification (Must Memorize / Understand / Overview)
- Memory type tagging (Memorize / Practice to Understand)
- Difficulty rating (1-5 stars)
- Async task processing (non-blocking UI)

#### 🚧 Coming Soon
- Structured note generation
- Daily review plan
- Knowledge graph visualization
- PDF export
- Settings panel
- System tray integration

### Tech Stack

- **GUI**: PySide6 + PyObjC (macOS native glass effect)
- **AI**: DeepSeek / OpenAI API
- **PDF**: PyMuPDF
- **Image**: Pillow

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/PropoxarMathnb.git
cd PropoxarMathnb

# Install dependencies
pip3 install -r requirements.txt

# Run the application
python3 app.py
```

### Configuration

Set your API key before running:

```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

Or configure through the app settings (coming soon).

### Usage

1. Launch the app: `python3 app.py`
2. Drag & drop your calculus study materials (PDF, images, notes)
3. Click "Analyze" to let AI extract and classify knowledge points
4. View results with importance tags and difficulty ratings

---

## 中文

### 概述

PropoxarMathnb 是一款 macOS 桌面应用，旨在帮助学生更高效地学习高等数学。它利用 AI 分析学习资料，识别关键知识点，并按重要性进行分类整理。

### 当前状态

**v1.0.0** - 这是第一个版本，包含基础 GUI 框架和上传功能。许多功能仍在开发中。

#### ✅ 已实现
- macOS 液态玻璃 UI 效果（原生 NSVisualEffectView）
- 拖拽上传文件（PDF、图片、Markdown）
- AI 智能提取知识点
- 重要性分类（必背 / 理解 / 了解）
- 记忆方式标注（背诵 / 做题理解）
- 难度评级（1-5 星）
- 异步任务处理（不阻塞 UI）

#### 🚧 即将推出
- 结构化笔记生成
- 每日复习计划
- 知识图谱可视化
- 导出为 PDF
- 设置面板
- 系统托盘集成

### 技术栈

- **GUI**: PySide6 + PyObjC（macOS 原生玻璃效果）
- **AI**: DeepSeek / OpenAI API
- **PDF**: PyMuPDF
- **图片**: Pillow

### 安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/PropoxarMathnb.git
cd PropoxarMathnb

# 安装依赖
pip3 install -r requirements.txt

# 运行应用
python3 app.py
```

### 配置

运行前设置 API Key：

```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

或通过应用设置配置（即将推出）。

### 使用方法

1. 启动应用：`python3 app.py`
2. 拖拽高数学习资料（PDF、图片、笔记）
3. 点击"分析"让 AI 提取并分类知识点
4. 查看带有重要性标签和难度评级的结果

---

## License / 许可证

MIT License

---

## License / 许可证

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

本项目基于 MIT 许可证开源 - 详见 [LICENSE](LICENSE) 文件。
