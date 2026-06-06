<div align="center">

# 🚀 Awesome Tech Share

**一个面向计算机科学与人工智能的知识共享平台**

*A knowledge-sharing platform for Computer Science & Artificial Intelligence*

[![Stars](https://img.shields.io/github/stars/WncFht/Awesome-Tech-Share?style=flat-square&logo=github&color=yellow)](https://github.com/WncFht/Awesome-Tech-Share/stargazers)
[![Forks](https://img.shields.io/github/forks/WncFht/Awesome-Tech-Share?style=flat-square&logo=github&color=blue)](https://github.com/WncFht/Awesome-Tech-Share/network/members)
[![Deploy](https://img.shields.io/github/actions/workflow/status/WncFht/Awesome-Tech-Share/ci.yml?branch=main&style=flat-square&label=Deploy&logo=githubactions)](https://WncFht.github.io/Awesome-Tech-Share/)
[![MkDocs Material](https://img.shields.io/badge/Built%20with-MkDocs%20Material-526CFE?style=flat-square&logo=materialformkdocs)](https://squidfunk.github.io/mkdocs-material/)

<br/>

[🌐 访问网站 · Visit Site](https://WncFht.github.io/Awesome-Tech-Share/) &nbsp;·&nbsp;
[👥 贡献者 · Contributors](https://WncFht.github.io/Awesome-Tech-Share/links/) &nbsp;·&nbsp;
[📖 关于我们 · About Us](https://zhuanlan.zhihu.com/p/12775079036) &nbsp;·&nbsp;
[🏷️ 标签索引 · Tags](https://WncFht.github.io/Awesome-Tech-Share/Tags/)

</div>

---

## 📖 项目简介 | About

**Awesome Tech Share** 是一个**持续更新**的计算机科学与人工智能知识库，收录涵盖 CS 核心课程、AI 前沿技术、工程开发实践、学习成长经验等多领域优质资源与原创思考。

网站由 [MkDocs + Material Theme](https://squidfunk.github.io/mkdocs-material/) 驱动，**部署于 GitHub Pages，无需任何账号注册，直接用浏览器打开即可访问所有内容。**

---

**Awesome Tech Share** is a **continuously updated** knowledge base covering CS fundamentals, cutting-edge AI, software engineering, and personal learning reflections.

Powered by [MkDocs + Material Theme](https://squidfunk.github.io/mkdocs-material/) and deployed on GitHub Pages — **no sign-up needed, just open your browser and start reading.**

---

## 🌐 如何访问 | How to Access

> **无需安装 · No Installation Required**

直接点击下方链接，在浏览器中打开即可：

Just click the link below to open in any browser:

### 👉 [https://WncFht.github.io/Awesome-Tech-Share/](https://WncFht.github.io/Awesome-Tech-Share/)

**网站亮点 | Highlights：**

| 功能 | 说明 |
|------|------|
| ☀️ 明/暗主题 | 自动跟随系统，支持手动切换 / Auto light-dark mode |
| 🔍 全文搜索 | 关键词高亮 + 智能补全 / Full-text search with highlight & suggestion |
| 📱 响应式布局 | 电脑 / 手机 / 平板均可流畅阅读 / Works on any device |
| 📊 阅读统计 | 实时显示字数与预计阅读时间 / Word count & reading time |
| 🔖 标签索引 | 通过 Tags 页快速定位跨领域内容 / Cross-topic tag index |
| 🕐 更新时间 | 每篇文章显示最后 Git 提交时间 / Per-page last-update timestamp |
| 🖼️ 图片灯箱 | 点击图片放大查看 / Click-to-enlarge image lightbox |

---

## 📚 内容导览 | Content Overview

### 🖥️ 计算机科学 | Computer Science

> 系统性的 CS 核心课程知识整理与优质课程资源推荐

| 模块 | 涵盖内容 |
|------|----------|
| **系统原理** | 操作系统 · 计算机网络 · 编译原理 · 数据库 · 分布式系统 · 体系结构 · 软件分析 · 电路理论 |
| **编程** | 编程基础 · 数据结构与算法 |
| **数学基础** | 数学课程精选 · 数学杂谈 |

### 🤖 人工智能 | Artificial Intelligence

> 从基础理论到前沿应用，覆盖当代 AI 全栈技术体系

| 模块 | 涵盖内容 |
|------|----------|
| **AI 理论基础** | 机器学习 · 深度学习 · 统计学基础 |
| **算法与实现** | 主流框架 · 模型训练与调优实践 |
| **大语言模型** | LLM 原理 · RAG 检索增强生成 · AI Agent 智能体 |
| **AI 应用** | AIGC 内容生成 · 多模态技术 · 具身智能（Embodied AI） |

### ⚙️ 开发 | Development

> 工程实战经验与开发工具使用心得

- 前后端开发 · 嵌入式开发 · 计算机图形学 · 开发工具 · 实战项目

### 🌱 学习成长 | Learning & Growth

> 学习方法论、科研经验、技术思考与职业规划

- 优质学习资源 · 科研记录 · 技术观点 · 读书笔记 · 工作就业 · 人生感悟

### 📝 总结 | Summaries

> 持续更新的过程回顾与每周技术总结

---

## 🛠️ 本地部署 | Local Development

> 若你想在本地阅读或贡献内容，请按以下步骤操作。
> *Follow these steps if you want to run the site locally or contribute.*

### 1. 克隆仓库 | Clone the Repo

```bash
git clone https://github.com/WncFht/Awesome-Tech-Share.git
cd Awesome-Tech-Share
```

### 2. 配置环境 | Setup Environment

```bash
# 创建并激活 conda 环境 / Create and activate conda environment
conda env create -f environment.yml
conda activate <your-env-name>

# 安装统计插件（来自独立仓库）/ Install the statistics plugin
git clone https://github.com/KinnariyaMamaTanha/mkdocs-statistics-plugin
pip install ./mkdocs-statistics-plugin

# 清理 / Cleanup
rm -rf mkdocs-statistics-plugin        # Linux / macOS
# rmdir /s /q mkdocs-statistics-plugin  # Windows

pip cache purge
```

### 3. 本地预览 | Preview Locally

```bash
mkdocs serve
```

浏览器打开 [http://127.0.0.1:8000](http://127.0.0.1:8000) 即可实时预览。

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) to preview in real time.

### 4. 构建静态文件 | Build

```bash
mkdocs build
```

---

## 🤝 如何贡献 | Contributing

欢迎任何形式的贡献！你可以：

All contributions are welcome! You can:

- 📝 **补充 / 修正内容** — 在 `docs/` 对应目录下新增或修改 Markdown 文件
- 🐛 **提交 Issue** — 通过 [Issues](https://github.com/WncFht/Awesome-Tech-Share/issues) 反馈错误或提出改进建议
- 🔀 **发起 Pull Request** — 直接贡献你的内容与修改
- ⭐ **点个 Star** — 这是对我们最直接的鼓励！

更多详情请见 [贡献者页面 · Contributors Page](https://WncFht.github.io/Awesome-Tech-Share/links/)。

---

<div align="center">

如果这个项目对你有帮助，欢迎点击右上角 ⭐ Star 支持我们！

*If this project is helpful to you, please consider giving it a ⭐ Star!*

[![Star History Chart](https://api.star-history.com/svg?repos=WncFht/Awesome-Tech-Share&type=Date)](https://star-history.com/#WncFht/Awesome-Tech-Share&Date)

</div>
