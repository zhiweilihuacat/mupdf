# PDF to Image Converter 📄➡️🖼️

一个基于 Python 开发的高效 PDF 转图片桌面端应用，拥有现代化的 GUI 界面，支持批量转换与多种自定义参数设置。

![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ 核心特性

* 🎨 **现代化 UI**：基于 `CustomTkinter` 构建，界面简洁优雅，支持深色/浅色模式切换。
* ⚡ **极速转换**：底层采用 `PyMuPDF (fitz)`，图像渲染速度远超传统转换工具。
* ⚙️ **灵活配置**：
  * 可选分辨率（DPI，如 72,144,216,288 等）。
  * 支持导出为 PNG 图片格式。
  * 支持指定页面范围导出（单页、多页或全部）。

---

## 🛠️ 技术栈

* **GUI 框架**：[CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
* **PDF 处理引擎**：[PyMuPDF](https://github.com/pymupdf/PyMuPDF) (fitz)

---

## 🚀 快速开始

### 1. 克隆项目

```bash

git clone https://github.com/a349058231/mupdf.git
