# -*- coding: utf-8 -*-
"""把《附件1 AI应用创新大赛 项目说明书》官方模板填好。

直接在官方空白模板 `附件1 (1).docx` 上原地填充：替换各章节的说明性占位文字、
填写项目信息表与 AI 工具使用表，保留模板原有的标题、表格与版式。
"""
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

SRC = r"D:\陈铭志\新建文件夹\v3\附件1 (1).docx"
# 模板常被 Word/WPS 占用锁定，无法原地覆盖，故另存为新文件（内容与版式不变）。
# 若需覆盖回 `附件1 (1).docx`，先关闭 Word 后把 OUT 改回 SRC 重跑即可。
OUT = r"D:\陈铭志\新建文件夹\v3\附件1_项目说明书_已填写.docx"

doc = Document(SRC)

# ---------- 字体辅助 ----------


def _set_run(run, size=12, cn="宋体", bold=False):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.bold = bold
    rPr = run._element.get_or_add_rPr()
    rPr.get_or_add_rFonts().set(qn("w:eastAsia"), cn)


def _mk_para(text, size=12, cn="宋体", bold=False, indent=True, before=0, after=0):
    """新建一个段落（先插入再返回）。"""
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Pt(size * 2)
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    if text:
        run = p.add_run(text)
        _set_run(run, size, cn, bold)
    return p


def replace_with(anchor, blocks):
    """用 blocks（一段段 dict）替换锚点段落，然后删除锚点。"""
    for b in blocks:
        p = anchor.insert_paragraph_before()
        if b.get("indent", True):
            p.paragraph_format.first_line_indent = Pt(b.get("size", 12) * 2)
        p.paragraph_format.space_before = Pt(b.get("before", 0))
        p.paragraph_format.space_after = Pt(b.get("after", 0))
        if b.get("text"):
            run = p.add_run(b["text"])
            _set_run(run, b.get("size", 12), b.get("cn", "宋体"), b.get("bold", False))
    anchor._element.getparent().remove(anchor._element)


def H(text):
    """小节标题：黑体 12pt 加粗，不缩进。"""
    return {"text": text, "cn": "黑体", "size": 12, "bold": True, "indent": False, "before": 6, "after": 2}


def B(text):
    """正文：宋体 12pt，首行缩进两字符。"""
    return {"text": text, "cn": "宋体", "size": 12, "after": 2}


def N(text):
    """编号条目：宋体 12pt，缩进。"""
    return {"text": text, "cn": "宋体", "size": 12, "after": 2}


def fill_cell(cell, text, size=10.5, cn="宋体", bold=False, align=None):
    cell.text = ""
    p = cell.paragraphs[0]
    if align is not None:
        p.alignment = align
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(2)
    run = p.add_run(text)
    _set_run(run, size, cn, bold)
    return cell


# ---------- 定位各段落 ----------
paras = doc.paragraphs
# 用文本精确匹配锚点，避免依赖下标。
def find(text):
    for p in paras:
        if p.text.strip() == text:
            return p
    raise KeyError("not found: " + text)


# ============ 0. 项目信息表 ============
info_values = [
    "计算机硬件组成 3D 交互学习平台（Computer Architecture Lab）",
    "A类 · 应用落地类",
    "可运行 AI 应用（Web 端 3D 交互式教学应用）",
    "【请填写】",
    "【姓名｜专业｜学号】",
    "【姓名｜专业｜学号】",
    "【姓名｜专业｜学号】",
    "【姓名｜所在学院】",
    "https://computer-architecture-lab.openai.site",
]
t0 = doc.tables[0]
for i, val in enumerate(info_values):
    fill_cell(t0.cell(i, 1), val, size=10.5)

# ============ 一、项目背景与现实价值 ============
replace_with(find("简述项目要解决的真实问题、目标用户群体，结合所属专业领域说明现实需求。"), [
    H("（一）要解决的真实问题"),
    B("计算机组成原理（Computer Architecture）是计算机类专业的核心课程，但长期以来存在“抽象、难懂、难上手”的教学痛点："),
    N("1. 教材以原理图、方框图和文字描述为主，学生难以把“PCIe 总线”“VRM 供电”“DDR 通道”等抽象概念与真实硬件实体对应起来，缺乏直观的空间认知。"),
    N("2. 硬件实验课受限于实物数量、成本、易损耗与设备管理，难以做到人手一套、随时拆装；真实的拆机/装机还存在触电、静电、部件损坏等安全与成本风险。"),
    N("3. 传统 3D 教学资源（三维模型、交互动画）制作成本高、周期长，需要专业建模人员或昂贵的三维扫描设备，难以针对具体型号的硬件快速、批量生产。"),
    H("（二）目标用户群体"),
    B("计算机科学与技术、电子信息、软件工程等专业的本科生（《计算机组成原理》《计算机系统基础》等课程）；计算机爱好者与 DIY 装机用户；职业技能培训机构学员；需要直观教具进行课堂演示的高校教师。"),
    H("（三）现实价值与 AI 创新点"),
    B("本作品通过 Hi3D 单图/多图三维重建 AI，将一张真实硬件照片快速转化为写实风格的 3D 模型，再经自动化的贴图压缩与网格简化流水线处理后，部署到基于 Three.js 的 Web 3D 交互平台上，形成“拍照 → AI 建模 → Web 交互学习”的完整闭环。该方案大幅降低了 3D 教学资源的制作门槛与周期，使“针对真实硬件、快速可交互”的教学场景成为可能，为计算机硬件类课程的数字化、可视化教学提供了一条可复用的技术路径。"),
])

replace_with(find("示例：面向XX群体，目前存在XX问题，现有方式存在XX不足，因此设计本AI应用。"), [])

# ============ 二、项目整体设计 ============
# 2.1 需求分析
replace_with(find("说明项目实现哪些核心功能，能够为用户提供什么价值。"), [
    B("本项目面向硬件认知与装机实践两大学习场景，实现如下核心功能："),
    N("1. 3D 硬件标本浏览：提供 9 个硬件标本（主板、CPU、GPU、内存、NVMe 固态硬盘、电源、CPU 散热、网卡、完整计算机系统），支持拖拽旋转、滚轮缩放、自动旋转与模型切换动画。"),
    N("2. 结构热点标注：35 个可点击的 3D 结构热点，悬停/点击弹出中英文结构名称与功能说明，并提供屏幕阅读器等价文本。"),
    N("3. 7 种 3D 交互工具：旋转、缩放、单独显示（隔离）、剖面、线框/分层、组件对比、重置。"),
    N("4. 结构标注测验：随机出题、点击判定、即时反馈、计分与重试，答错时自动标出正确结构位置。"),
    N("5. 装机模拟实验室：将 8 个部件（主板、CPU、内存、散热器、SSD、显卡、网卡、电源）拖拽入机箱，提供“自由组装”与“分步引导”两种模式，完成后给出完成提示。"),
    N("6. 引导课程与动画：9 个部件的中英文引导课程、数据/能量流动画、系统上下文弹窗与 6 类学习资源卡片。"),
    N("7. 个性化学习：收藏/书签、个人笔记（本地自动保存）、账户菜单与数据清除。"),
    N("8. 关键词搜索、响应式移动端适配、12 种语言入口（中英文内容完整）。"),
    B("用户价值：让学习者无需真实硬件即可随时随地进行“拆解式”与“装配式”的沉浸式学习，直观建立“物理结构—信号流—供电—散热—系统功能”的完整心智模型。"),
])

# 2.2 项目实现
replace_with(find("说明知识库内容、提示词设计、工作流逻辑、调用的AI能力。"), [
    H("（1）调用的 AI 能力：Hi3D 图像到 3D 生成"),
    B("输入真实硬件照片（如 ASUS ROG Strix B660 主板的实拍图），Hi3D 输出写实风格、带材质贴图的 glTF/GLB 三维模型。相比程序化占位模型，真实扫描模型在几何与纹理上高度还原实物。"),
    H("（2）知识库内容设计"),
    B("为 9 个硬件组件构建中英双语知识库（app/i18n/organs/），每个组件结构化组织：描述、工程参数（规格尺寸/重量/吞吐/系统位置/接口供电/主要功能）、工程意义、架构知识、常见故障与性能瓶颈、内部结构、结构热点说明等字段；内容依据公开的计算机组成原理教材与行业技术标准整理。"),
    H("（3）提示词 / 输入设计"),
    B("三维重建环节以“照片输入 + 生成参数”为主要控制手段：优先采用正面、均匀光照、无遮挡、高分辨率的硬件实拍图作为输入，并设定“写实风格、高细节”的生成目标，以保证模型几何与材质的还原度；知识文案环节则按组件字段模板组织，保证内容结构一致、可校验。"),
    H("（4）工作流逻辑"),
    B("后端流水线：硬件拍照 → Hi3D 生成 GLB 模型 → process_scans.py 贴图压缩（8K PNG→4K JPEG，43–55 MB 降至约 20 MB）→ process_cpu.mjs 网格简化（meshoptimizer，保留 UV，精简至约 40 万三角形）→ verify_models.py 校验（bounding box 归一化 + 水密性）→ 部署至 public/models。"),
    B("前端交互：Next.js 16 + React 19 + TypeScript + Three.js + GSAP + Tailwind CSS 4；app/lib/three/ 实现渲染器、资源加载器与热点引擎（含遮挡剔除），assembly-viewer.ts 实现装机拖拽/吸附/引导逻辑。"),
    B("部署：通过 Cloudflare Workers（vinext / OpenAI 托管平台）部署，支持静态生成、图像优化与多语言路由。"),
])

# ============ 三、测试情况与示例 ============
replace_with(find("列举1-2个实际测试/模拟案例，展示项目运行效果。"), [
    H("案例 1：结构标注测验（CPU 标本）"),
    B("输入/操作：在“中央处理器 CPU”标本中点击“测验”，系统随机提问“找出 CPU 核心”。"),
    B("输出结果：点击正确热点时显示“正确”，绿色高亮“CPU 核心”并计分 +1；点击错误（如“末级缓存”）时显示“还差一点”，提示“你点击的是末级缓存”，同时用绿色标出正确结构“CPU 核心”。全部完成后显示“测验完成，答对 X/4”，可点击“再试一次”重做。"),
    H("案例 2：装机模拟（分步引导模式）"),
    B("输入/操作：进入“组装机箱”页面，选择“分步引导”，按推荐顺序（主板→CPU→内存→散热器→SSD→显卡→网卡→电源）依次将部件拖拽到机箱对应安装位。"),
    B("输出结果：拖到正确安装位附近时部件自动吸附归位，清单逐项打勾并提示“下一步：安装 XX”；8 个部件全部就位后弹出“组装完成”，可“重新组装”。"),
    B("说明：以上为对已实现功能的模拟测试描述；实际运行可在本地执行 npm run dev 启动，访问 /zh 或 /en 使用。"),
])

replace_with(find("智能体：写输入问题、得到的输出结果；"), [])
replace_with(find("原型方案：写模拟场景、预期输出效果。"), [])

# ============ 四、作品局限性（必填） ============
replace_with(find("客观说明当前作品存在的不足、约束条件、待优化点，不夸大项目效果。"), [
    N("1. AI 模型质量依赖输入照片：Hi3D 生成效果受拍摄光线、角度、遮挡与分辨率影响，几何细节与纹理在凹陷、反光区域可能出现拉伸或瑕疵。"),
    N("2. 场景覆盖单一：当前仅覆盖桌面 PC（台式机）硬件，尚未扩展至服务器、笔记本、嵌入式或移动设备等形态。"),
    N("3. 热点标定依赖手工：结构热点坐标需人工标定，模型更换后需重新标定，自动化程度有限。"),
    N("4. 语言完整度有限：12 种语言入口中仅中文、英文为完整内容，其余为占位；装机实验室仅支持中英文。"),
    N("5. 数据存于本地浏览器：收藏、笔记与学习进度保存在浏览器 localStorage，暂无账号系统与跨设备同步。"),
    N("6. 教学定位边界：本作品为可视化教学辅助工具，不能替代真实硬件实操、电学安全训练与故障排查等工程实践。"),
])

replace_with(find("示例：识别受拍摄光线影响；仅覆盖部分常见场景；仅作为辅助工具，不能替代专业人员。"), [])

# ============ 五、AI工具使用说明 ============
t1 = doc.tables[1]
ai_rows = [
    ("Hi3D（单图/多图三维重建）",
     "3D 模型生成",
     "由 Hi3D 依据团队拍摄的真实硬件照片生成写实风格 3D 模型与材质贴图；后续的几何修正、贴图压缩、网格简化、结构热点标定等由人工编写的脚本完成。"),
    ("Claude（Anthropic 编程与文案辅助）",
     "代码编写、调试与文档",
     "用于辅助前端代码编写与调试、中英文知识库文案起草，以及本说明书的整理；所有生成内容均经人工审核与修改。"),
]
# 模板表结构：R0 表头，R1-R3 空行，R4 为 "..." 占位。
for i, row in enumerate(ai_rows, start=1):
    for j, val in enumerate(row):
        fill_cell(t1.cell(i, j), val, size=10)
# 清掉 "..." 占位行，改为空行供团队继续添加
for j in range(3):
    fill_cell(t1.cell(4, j), "", size=10)

# ============ 六、数据来源与知识产权声明 ============


def insert_before(anchor, texts):
    """在 anchor 之前按正序插入多个正文段落（宋体 12pt、首行缩进两字符）。"""
    for t in texts:
        p = anchor.insert_paragraph_before()
        p.paragraph_format.first_line_indent = Pt(24)
        p.paragraph_format.space_after = Pt(2)
        run = p.add_run(t)
        _set_run(run, 12, "宋体")


# "1. 数据、素材来源说明：" 之后插入 4 条来源说明（即在 "2." 之前）
insert_before(find("2. 伦理风险提示，说明使用边界："), [
    "（1）3D 硬件模型：由 Hi3D 对团队自行拍摄的硬件实拍照片生成，并经自主编写的脚本完成贴图压缩与网格简化处理；",
    "（2）金属材质贴图：来自 ambientCG（CC0 公共领域授权）的 PBR 材质贴图；",
    "（3）知识文案：依据公开的计算机组成原理教材、行业技术标准与公开资料整理编写；",
    "（4）图标与框架：lucide-react（ISC 许可）图标，Next.js / React / Three.js 等均为开源框架。",
])

# "2. 伦理风险提示" 之后插入 3 条使用边界（即在 "3." 之前）
insert_before(find("3. 声明作品原创，无侵权、无隐私涉密数据。"), [
    "（1）本作品仅用于计算机硬件教学与科普，不涉及个人隐私、身份或敏感数据；",
    "（2）3D 模型为教学示意，结构描述与参数为通用/参考值，不构成对特定品牌产品的官方描述，不用于商业用途；",
    "（3）不得将本工具用于误导性宣传、虚假测评或商业冒充。",
])

# "3. 声明作品原创..." 替换为完整的原创声明
replace_with(find("3. 声明作品原创，无侵权、无隐私涉密数据。"), [
    {"text": "3. 原创声明：本作品为团队原创，AI 生成内容均已进行人工审核与修改；未使用任何侵权素材，不含隐私及涉密数据。",
     "cn": "宋体", "size": 12, "bold": True},
])

# ============ 七、团队分工 ============
replace_with(find("明确各成员具体工作分工。"), [
    B("（模板，请按团队实际情况填写）"),
    B("成员一（姓名｜专业｜学号）：项目统筹，负责 Hi3D 三维建模与后处理流水线（贴图压缩、网格简化、模型校验）。"),
    B("成员二（姓名｜专业｜学号）：前端交互开发，负责 Three.js 渲染、结构热点引擎与装机实验室实现。"),
    B("成员三（姓名｜专业｜学号）：知识库内容编写与中英文翻译，负责功能测试与文档整理。"),
])

doc.save(OUT)
print("saved:", OUT)
