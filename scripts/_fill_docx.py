# -*- coding: utf-8 -*-
"""生成填写完成的《附件1 AI应用创新大赛 项目说明书》Word 文档。"""
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn

OUT = r"D:\陈铭志\新建文件夹\v3\附件1_项目说明书_完成版.docx"

doc = Document()

# 页面边距
for s in doc.sections:
    s.top_margin = Cm(2.2)
    s.bottom_margin = Cm(2.2)
    s.left_margin = Cm(2.4)
    s.right_margin = Cm(2.4)

# 全局默认字体：中文宋体，西文 Times New Roman
normal = doc.styles["Normal"]
normal.font.name = "Times New Roman"
normal.font.size = Pt(11)
normal._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")


def set_font(run, size=11, cn="宋体", en="Times New Roman", bold=False, color=None):
    run.font.name = en
    run.font.size = Pt(size)
    run.font.bold = bold
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn("w:eastAsia"), cn)
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_para(text="", size=11, cn="宋体", bold=False, align=None, space_after=6,
             space_before=0, indent=False, color=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.space_before = Pt(space_before)
    if indent:
        p.paragraph_format.first_line_indent = Pt(size * 2)
    if text:
        run = p.add_run(text)
        set_font(run, size, cn, bold=bold, color=color)
    return p


def add_heading(text, level=1):
    """黑体标题。level 1 = 章标题, 2 = 小节标题。"""
    if level == 1:
        p = add_para(text, size=14, cn="黑体", bold=True, space_before=14, space_after=6)
    else:
        p = add_para(text, size=12, cn="黑体", bold=True, space_before=8, space_after=4)
    return p


def fill_cell(cell, text, size=10.5, cn="宋体", bold=False, align=None):
    cell.text = ""
    p = cell.paragraphs[0]
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.space_before = Pt(2)
    run = p.add_run(text)
    set_font(run, size, cn, bold=bold)
    return cell


# ============ 封面标题 ============
add_para("附件1", size=14, cn="黑体", bold=True, align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=2)
add_para("AI应用创新大赛 项目说明书", size=20, cn="黑体", bold=True,
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
add_para("（A类 · 应用落地类）", size=12, cn="楷体", align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2)
add_para("适用：智能体成品 / 原型解决方案", size=10, cn="楷体",
         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=12)

# ============ 项目信息表 ============
info = [
    ("项目名称", "计算机硬件组成 3D 交互学习平台（Computer Architecture Lab）"),
    ("参赛赛道", "A类 · 应用落地类"),
    ("作品类型", "可运行 AI 应用（Web 端 3D 交互式教学应用）"),
    ("团队名称", "【请填写】"),
    ("团队成员", "【姓名｜专业｜学号】"),
    ("团队成员", "【姓名｜专业｜学号】"),
    ("团队成员", "【姓名｜专业｜学号】"),
    ("指导教师", "【姓名｜所在学院】"),
    ("作品链接", "https://computer-architecture-lab.openai.site（部署地址，以最终提交为准）"),
]
tbl = doc.add_table(rows=len(info), cols=2)
tbl.style = "Table Grid"
tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
tbl.columns[0].width = Cm(3.2)
tbl.columns[1].width = Cm(11.6)
for i, (k, v) in enumerate(info):
    fill_cell(tbl.cell(i, 0), k, size=10.5, cn="黑体", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
    fill_cell(tbl.cell(i, 1), v, size=10.5)

add_para("", size=6, space_after=2)

# ============ 一、项目背景与现实价值 ============
add_heading("一、项目背景与现实价值")
add_para("（一）要解决的真实问题", size=11.5, cn="黑体", bold=True, space_after=3)
add_para("计算机组成原理（Computer Architecture）是计算机类专业的核心课程，但长期以来存在“抽象、难懂、难上手”的教学痛点：",
         indent=True)
add_para("1. 教材以原理图、方框图和文字描述为主，学生难以把“PCIe 总线”“VRM 供电”“DDR 通道”等抽象概念与真实硬件实体对应起来，缺乏直观的空间认知。", indent=True)
add_para("2. 硬件实验课受限于实物数量、成本、易损耗与设备管理，难以做到人手一套、随时拆装；真实的拆机/装机还存在触电、静电、部件损坏等安全与成本风险。", indent=True)
add_para("3. 传统 3D 教学资源（三维模型、交互动画）制作成本高、周期长，需要专业建模人员或昂贵的三维扫描设备，难以针对具体型号的硬件快速、批量生产。", indent=True)

add_para("（二）目标用户群体", size=11.5, cn="黑体", bold=True, space_after=3, space_before=6)
add_para("计算机科学与技术、电子信息、软件工程等专业的本科生（《计算机组成原理》《计算机系统基础》等课程）；计算机爱好者与 DIY 装机用户；职业技能培训机构学员；需要直观教具进行课堂演示的高校教师。", indent=True)

add_para("（三）现实价值与 AI 创新点", size=11.5, cn="黑体", bold=True, space_after=3, space_before=6)
add_para("本作品通过 Hi3D 单图/多图三维重建 AI，将一张真实硬件照片快速转化为写实风格的 3D 模型，再经自动化的贴图压缩与网格简化流水线处理后，部署到基于 Three.js 的 Web 3D 交互平台上，形成“拍照 → AI 建模 → Web 交互学习”的完整闭环。该方案大幅降低了 3D 教学资源的制作门槛与周期，使“针对真实硬件、快速可交互”的教学场景成为可能，为计算机硬件类课程的数字化、可视化教学提供了一条可复用的技术路径。", indent=True)

# ============ 二、项目整体设计 ============
add_heading("二、项目整体设计")

add_heading("2.1 需求分析", 2)
add_para("本项目面向硬件认知与装机实践两大学习场景，实现如下核心功能：", indent=True)
add_para("1. 3D 硬件标本浏览：提供 9 个硬件标本（主板、CPU、GPU、内存、NVMe 固态硬盘、电源、CPU 散热、网卡、完整计算机系统），支持拖拽旋转、滚轮缩放、自动旋转与模型切换动画。", indent=True)
add_para("2. 结构热点标注：35 个可点击的 3D 结构热点，悬停/点击弹出中英文结构名称与功能说明，并提供屏幕阅读器等价文本。", indent=True)
add_para("3. 7 种 3D 交互工具：旋转、缩放、单独显示（隔离）、剖面、线框/分层、组件对比、重置。", indent=True)
add_para("4. 结构标注测验：随机出题、点击判定、即时反馈、计分与重试，答错时自动标出正确结构位置。", indent=True)
add_para("5. 装机模拟实验室：将 8 个部件（主板、CPU、内存、散热器、SSD、显卡、网卡、电源）拖拽入机箱，提供“自由组装”与“分步引导”两种模式，完成后给出完成提示。", indent=True)
add_para("6. 组件对比、引导课程、数据/能量流动画、系统上下文弹窗与 6 类学习资源卡片。", indent=True)
add_para("7. 关键词搜索、响应式移动端适配、12 种语言入口（中英文内容完整）。", indent=True)
add_para("用户价值：让学习者无需真实硬件即可随时随地进行“拆解式”与“装配式”的沉浸式学习，直观建立“物理结构—信号流—供电—散热—系统功能”的完整心智模型。", indent=True, space_before=4)

add_heading("2.2 项目实现", 2)
add_para("（1）调用的 AI 能力：Hi3D 图像到 3D 生成", cn="黑体", bold=True, space_after=2)
add_para("输入真实硬件照片（如 ASUS ROG Strix B660 主板的实拍图），Hi3D 输出写实风格、带材质贴图的 glTF/GLB 三维模型。相比程序化占位模型，真实扫描模型在几何与纹理上高度还原实物。", indent=True)

add_para("（2）知识库内容设计", cn="黑体", bold=True, space_after=2, space_before=4)
add_para("为 9 个硬件组件构建中英双语知识库（app/i18n/organs/），每个组件结构化组织：描述、工程参数（规格尺寸/重量/吞吐/系统位置/接口供电/主要功能）、工程意义、架构知识、常见故障与性能瓶颈、内部结构、结构热点说明等字段；内容依据公开的计算机组成原理教材与行业技术标准整理。", indent=True)

add_para("（3）提示词 / 输入设计", cn="黑体", bold=True, space_after=2, space_before=4)
add_para("三维重建环节以“照片输入 + 生成参数”为主要控制手段：优先采用正面、均匀光照、无遮挡、高分辨率的硬件实拍图作为输入，并设定“写实风格、高细节”的生成目标，以保证模型几何与材质的还原度；知识文案环节则按组件字段模板组织，保证内容结构一致、可校验。", indent=True)

add_para("（4）工作流逻辑", cn="黑体", bold=True, space_after=2, space_before=4)
add_para("后端流水线：硬件拍照 → Hi3D 生成 GLB 模型 → process_scans.py 贴图压缩（8K PNG→4K JPEG，43–55 MB 降至约 20 MB）→ process_cpu.mjs 网格简化（meshoptimizer，保留 UV，精简至约 40 万三角形）→ verify_models.py 校验（bounding box 归一化 + 水密性）→ 部署至 public/models。", indent=True)
add_para("前端交互：Next.js 16 + React 19 + TypeScript + Three.js + GSAP + Tailwind CSS 4；app/lib/three/ 实现渲染器、资源加载器与热点引擎（含遮挡剔除），assembly-viewer.ts 实现装机拖拽/吸附/引导逻辑。", indent=True)
add_para("部署：通过 Cloudflare Workers（vinext / OpenAI 托管平台）部署，支持静态生成、图像优化与多语言路由。", indent=True)

# ============ 三、测试情况与示例 ============
add_heading("三、测试情况与示例")
add_para("案例 1：结构标注测验（CPU 标本）", cn="黑体", bold=True, space_after=2)
add_para("输入/操作：在“中央处理器 CPU”标本中点击“测验”，系统随机提问“找出 CPU 核心”。", indent=True)
add_para("输出结果：点击正确热点时显示“正确”，绿色高亮“CPU 核心”并计分 +1；点击错误（如“末级缓存”）时显示“还差一点”，提示“你点击的是末级缓存”，同时用绿色标出正确结构“CPU 核心”。全部完成后显示“测验完成，答对 X/4”，可点击“再试一次”重做。", indent=True)

add_para("案例 2：装机模拟（分步引导模式）", cn="黑体", bold=True, space_after=2, space_before=4)
add_para("输入/操作：进入“组装机箱”页面，选择“分步引导”，按推荐顺序（主板→CPU→内存→散热器→SSD→显卡→网卡→电源）依次将部件拖拽到机箱对应安装位。", indent=True)
add_para("输出结果：拖到正确安装位附近时部件自动吸附归位，清单逐项打勾并提示“下一步：安装 XX”；8 个部件全部就位后弹出“组装完成”，可“重新组装”。", indent=True)
add_para("说明：以上为对已实现功能的模拟测试描述；实际运行可在本地执行 npm run dev 启动，访问 /zh 或 /en 使用。", indent=True, space_before=4)

# ============ 四、作品局限性 ============
add_heading("四、作品局限性（必填）")
add_para("1. 模型覆盖有限：主板、CPU 等核心部件已替换为 Hi3D 真实扫描模型，但 GPU、内存、SSD、电源、散热、网卡、机箱等部件的结构热点尚未针对新模型重新标定（代码中 hotspots 待补全），部分标本的“结构标注测验”暂不可用。", indent=True)
add_para("2. AI 模型质量依赖输入照片：Hi3D 生成效果受拍摄光线、角度、遮挡与分辨率影响，几何细节与纹理在凹陷、反光区域可能出现拉伸或瑕疵。", indent=True)
add_para("3. 场景覆盖单一：当前仅覆盖桌面 PC（台式机）硬件，尚未扩展至服务器、笔记本、嵌入式或移动设备等形态。", indent=True)
add_para("4. 热点标定依赖手工：结构热点坐标需人工标定，模型更换后需重新标定，自动化程度有限。", indent=True)
add_para("5. 语言完整度有限：12 种语言入口中仅中文、英文为完整内容，其余为占位；装机实验室仅支持中英文。", indent=True)
add_para("6. 教学定位边界：本作品为可视化教学辅助工具，不能替代真实硬件实操、电学安全训练与故障排查等工程实践。", indent=True)

# ============ 五、AI工具使用说明 ============
add_heading("五、AI工具使用说明")
add_para("本项目使用的 AI 工具及使用情况如下（第 2 行为示例，请按团队实际使用情况增删）：",
         space_after=4)

ai_header = ["AI工具名称", "使用环节", "生成内容说明（哪些内容 AI 生成 / 哪些人工编写）"]
ai_rows = [
    ("Hi3D（单图/多图三维重建）",
     "3D 模型生成",
     "AI 根据真实硬件照片生成写实风格 3D 模型与材质贴图；几何修正、贴图压缩、网格简化、结构热点标定等由人工编写脚本完成。"),
    ("【示例】Claude / ChatGPT / Copilot 等编程辅助工具",
     "代码与文案辅助",
     "如使用请如实填写：用于辅助代码编写、调试与中英文知识文案起草，最终内容均由人工审核修改。"),
    ("【待补充】",
     "",
     ""),
]
tbl2 = doc.add_table(rows=1 + len(ai_rows), cols=3)
tbl2.style = "Table Grid"
tbl2.alignment = WD_TABLE_ALIGNMENT.CENTER
widths = [Cm(4.6), Cm(3.2), Cm(7.0)]
for j, h in enumerate(ai_header):
    fill_cell(tbl2.cell(0, j), h, size=10, cn="黑体", bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
for i, row in enumerate(ai_rows, start=1):
    for j, val in enumerate(row):
        fill_cell(tbl2.cell(i, j), val, size=10)
for j, w in enumerate(widths):
    for c in tbl2.columns[j].cells:
        c.width = w

add_para("", size=6, space_after=2)

# ============ 六、数据来源与知识产权声明 ============
add_heading("六、数据来源与知识产权声明")
add_para("1. 数据、素材来源说明：", bold=True, space_after=2)
add_para("（1）3D 硬件模型：由 Hi3D 对团队自行拍摄的硬件实拍照片生成，并经自主编写的脚本完成贴图压缩与网格简化处理；", indent=True)
add_para("（2）金属材质贴图：来自 ambientCG（CC0 公共领域授权）的 PBR 材质贴图；", indent=True)
add_para("（3）知识文案：依据公开的计算机组成原理教材、行业技术标准与公开资料整理编写；", indent=True)
add_para("（4）图标与框架：lucide-react（ISC 许可）图标，Next.js / React / Three.js 等均为开源框架。", indent=True)

add_para("2. 伦理风险提示与使用边界：", bold=True, space_after=2, space_before=4)
add_para("（1）本作品仅用于计算机硬件教学与科普，不涉及个人隐私、身份或敏感数据；", indent=True)
add_para("（2）3D 模型为教学示意，结构描述与参数为通用/参考值，不构成对特定品牌产品的官方描述，不用于商业用途；", indent=True)
add_para("（3）不得将本工具用于误导性宣传、虚假测评或商业冒充。", indent=True)

add_para("3. 原创声明：本作品为团队原创，AI 生成内容均已进行人工审核与修改；未使用任何侵权素材，不含隐私及涉密数据。", bold=True, space_before=4, indent=True)

# ============ 七、团队分工 ============
add_heading("七、团队分工")
add_para("（模板，请按团队实际情况填写）", size=10, cn="楷体", space_after=3)
add_para("成员一（姓名｜专业｜学号）：项目统筹，负责 Hi3D 三维建模与后处理流水线（贴图压缩、网格简化、模型校验）。", indent=True)
add_para("成员二（姓名｜专业｜学号）：前端交互开发，负责 Three.js 渲染、结构热点引擎与装机实验室实现。", indent=True)
add_para("成员三（姓名｜专业｜学号）：知识库内容编写与中英文翻译，负责功能测试与文档整理。", indent=True)

# ============ 指导教师意见 ============
add_heading("指导教师意见")
add_para("指导教师意见：", space_after=6)
tbl3 = doc.add_table(rows=2, cols=2)
tbl3.style = "Table Grid"
tbl3.alignment = WD_TABLE_ALIGNMENT.CENTER
fill_cell(tbl3.cell(0, 0), "指导教师签字：____________________", size=10.5)
fill_cell(tbl3.cell(0, 1), "日期：________年____月____日", size=10.5)
fill_cell(tbl3.cell(1, 0), "", size=10.5)
fill_cell(tbl3.cell(1, 1), "", size=10.5)
tbl3.columns[0].width = Cm(8.0)
tbl3.columns[1].width = Cm(6.8)

doc.save(OUT)
print("saved:", OUT)
