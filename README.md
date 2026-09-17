# 计算机系统 3D 交互实验平台

> Computer Architecture Lab —— 基于 Web 的计算机硬件 3D 交互学习应用

一个用于**计算机组成原理 / 计算机系统**课程的交互式教学平台。通过 Three.js 在浏览器中渲染计算机各核心硬件（主板、CPU、GPU、内存、硬盘、电源、散热、网卡、机箱），支持 360° 观察、部件热点标注、知识讲解以及整机装配，帮助学习者直观理解计算机的内部结构与工作原理。

## ✨ 功能特性

- 🔍 **3D 交互查看**：基于 Three.js（WebGL）的硬件模型浏览，支持旋转 / 缩放 / 平移与热点点击
- 🧩 **整机装配模式**：将各部件逐步组装成一台完整主机，直观理解硬件连接关系
- 📖 **知识点讲解**：每个部件配套通俗易懂的讲解（取指-译码-执行循环、内存刷新、GPU 并行、NAND 闪存等）
- 🌍 **多语言支持**：12 种语言界面
- 🖼️ **图片按需优化**：基于 Cloudflare Worker 的图片处理

## 🛠️ 技术栈

| 分类 | 技术 |
|------|------|
| 框架 | Next.js 16（App Router）+ React 19 |
| 语言 | TypeScript |
| 3D 渲染 | Three.js |
| 动画 | GSAP |
| 样式 | Tailwind CSS 4 |
| 图标 | lucide-react |
| 数据库 | Drizzle ORM + Cloudflare D1 |
| 运行时 | Cloudflare Workers（vinext） |
| 部署 | Vercel / Cloudflare |

## 📁 目录结构

```
├── app/                  # Next.js 应用代码
│   ├── [locale]/         # 多语言路由（主页 + 装配页）
│   ├── components/       # 3D 查看器、装配应用
│   ├── i18n/             # 12 语言字典
│   └── lib/              # 教学数据、Three.js 渲染逻辑
├── worker/               # Cloudflare Worker（图片优化）
├── scripts/              # 3D 模型处理与 i18n 工具脚本
├── db/                   # 数据库 Schema
├── drizzle/              # Drizzle 迁移文件
├── public/               # 静态资源（模型、纹理、图标）
└── tests/                # 测试
```

## 🚀 快速开始

### 环境要求

- Node.js `>= 22.13.0`

### 安装与运行

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 启动生产服务
npm run start
```

### 常用命令

```bash
npm run lint          # ESLint 代码检查
npm run test          # 构建并运行测试
npm run db:generate   # 生成数据库迁移
npm run i18n:audit    # i18n 完整性检查
npm run i18n:export   # 导出翻译文件
```

## 🌍 支持的语言

中文 · English · 日本語 · 한국어 · Deutsch · Español · Français · Português · Русский · العربية · हिन्दी · Bahasa Indonesia

## 📦 部署

项目支持部署到 **Vercel** 或 **Cloudflare Workers**：

- **Vercel**：已配置 `vercel.json` 与 `.vercelignore`
- **Cloudflare**：使用 `wrangler` 部署

## 📝 说明

> 项目中的 3D 模型文件（`.glb`）体积较大，未包含在 Git 仓库中。如需完整运行，请将模型文件放入 `public/models/` 目录（或通过 `scripts/` 下的脚本从源模型生成）。
