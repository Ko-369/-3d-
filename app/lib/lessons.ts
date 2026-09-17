import type { OrganId } from "./anatomy-data";

/**
 * A short, self-contained lesson per specimen. Educational copy lives here
 * (rather than in the per-locale organ dictionaries) so the other locales can
 * share the two fully-authored editions without 90 more translation blocks.
 * The modal is what renders it; `getLesson` falls back to English for any
 * locale other than Chinese.
 */
export type Lesson = { title: string; intro: string; points: string[] };

const zh: Record<OrganId, Lesson> = {
  motherboard: {
    title: "主板如何把一切连起来",
    intro: "主板是一张多层 PCB，成千上万条铜走线把处理器、内存、存储与扩展设备连接成一台能协同工作的机器。",
    points: [
      "CPU 插座是处理器与内存、PCIe 之间的机械和电气接口。",
      "DIMM 插槽承载内存，通常以双通道提升带宽。",
      "PCIe 插槽为显卡、网卡等扩展设备提供高速数据链路。",
      "芯片组负责汇聚 USB、SATA 等较慢的 I/O 设备。",
      "VRM 把 12 V 电源转换为 CPU 所需的低压大电流。",
    ],
  },
  cpu: {
    title: "CPU 如何执行指令",
    intro: "CPU 是通用处理器，不断完成「取指 → 译码 → 执行 → 写回」的循环，同时协调内存与 I/O。",
    points: [
      "核心是能独立执行指令流的通用计算单元。",
      "末级缓存在核心与系统内存之间充当低延迟缓冲。",
      "内存控制器调度 DDR 通道上的读写请求。",
      "片上互连把核心、缓存、内存控制器与 I/O 连成高速网络。",
      "时钟频率决定每秒能完成多少次运算，但受功耗与温度限制。",
    ],
  },
  gpu: {
    title: "GPU 如何并行计算",
    intro: "GPU 用成千上万个轻量线程同时工作，在不同线程间快速切换，以隐藏显存访问的等待时间。",
    points: [
      "GPU 封装包含大量着色器与专用加速单元。",
      "显存保存纹理、帧缓冲与计算任务所需的高带宽数据。",
      "散热风扇推动气流穿过鳍片，带走 GPU 与显存的热量。",
      "PCIe 金手指连接显卡与 CPU/平台的高速主机链路。",
      "并行吞吐量远高于 CPU，但单线程延迟更高。",
    ],
  },
  memory: {
    title: "内存如何暂存数据",
    intro: "DRAM 用微小电容中的电荷保存比特，必须在数据不变时也周期性刷新每个存储单元。",
    points: [
      "DRAM 芯片由大量易失性存储单元组成，按 Bank 与 Rank 组织。",
      "金手指向主板传输命令、地址、数据与电源信号。",
      "SPD 保存模块身份与支持的时序配置。",
      "容量决定能同时容纳多少活跃数据，频率与时序决定访问速度。",
      "断电后数据立即丢失，因此只作工作内存而非长期存储。",
    ],
  },
  storage: {
    title: "固态硬盘如何持久保存",
    intro: "NAND 闪存无需持续供电就能保留数据，NVMe 主控通过并行队列把海量读写请求高效地交给闪存。",
    points: [
      "NVMe 主控负责命令调度、纠错、磨损均衡与 NAND 访问。",
      "NAND 闪存以浮栅或电荷俘获单元保存数据。",
      "M.2 接口承载 PCIe 数据通道、控制信号与电源。",
      "NVMe 的并行队列让软件能同时提交大量请求。",
      "顺序传输可达数 GB/s，随机访问远快于机械硬盘。",
    ],
  },
  power: {
    title: "电源如何转换能量",
    intro: "开关电源以高频切换能量，把交流市电转换为各硬件所需的稳定低压直流电。",
    points: [
      "高频变压器在隔离的一次侧与二次侧之间传递能量。",
      "开关器件以高频率切换，因此变压器远小于线性电源。",
      "散热风扇控制开关器件与磁性元件的温度。",
      "模组化输出接口为主板、显卡与外设提供直流电源线。",
      "稳压性能与保护电路直接影响系统稳定性。",
    ],
  },
  cooling: {
    title: "散热器如何搬运热量",
    intro: "热管内部的工作液不断蒸发与冷凝，以相变方式在极小温差下快速搬运大量热能。",
    points: [
      "底座把 CPU 封装的热量传入热管。",
      "热管利用相变把热量快速搬运到整个鳍片区域。",
      "鳍片用大面积铝材把热量传给经过的空气。",
      "PWM 风扇根据温度动态调节转速。",
      "安装压力、导热介质与风量共同决定散热效率。",
    ],
  },
  network: {
    title: "网卡如何收发数据",
    intro: "网络接口控制器把系统内存中的数据转换为以太网帧，通过 PHY 收发器与外部网络交换数据。",
    points: [
      "网卡控制器实现 DMA、数据包队列与 MAC 功能。",
      "PHY 收发器在数字数据与电信号之间完成转换。",
      "以太网接口通过磁性器件隔离并接入网线。",
      "PCIe 接口在网卡与系统内存间搬运数据包缓冲区。",
      "硬件卸载校验和与分段，减少 CPU 的重复工作。",
    ],
  },
  case: {
    title: "整机如何协同工作",
    intro: "一台电脑是分层系统：硬件提供资源，固件初始化，操作系统管理，应用程序请求服务。",
    points: [
      "主板连接整机主要硬件子系统的电气与信号骨架。",
      "图形子系统由并行处理器与本地显存承担显示与计算。",
      "供电子系统转换输入电能并向各硬件分配稳定直流电。",
      "机箱风道组织进风与排风，把内部废热持续带出。",
      "各子系统以截然不同的时间尺度协作：缓存纳秒、存储毫秒。",
    ],
  },
};

const en: Record<OrganId, Lesson> = {
  motherboard: {
    title: "How the motherboard connects everything",
    intro: "A motherboard is a multi-layer PCB whose thousands of copper traces link the processor, memory, storage and expansion devices into one coordinated machine.",
    points: [
      "The CPU socket is the mechanical and electrical interface to memory and PCIe.",
      "DIMM slots carry memory, usually in dual channel for more bandwidth.",
      "PCIe slots provide high-speed links for graphics, networking and accelerators.",
      "The chipset aggregates slower I/O such as USB and SATA.",
      "The VRM converts 12 V input into the low-voltage, high-current rails the CPU needs.",
    ],
  },
  cpu: {
    title: "How the CPU executes instructions",
    intro: "The CPU is a general-purpose processor that runs a continuous fetch → decode → execute → write-back loop while coordinating memory and I/O.",
    points: [
      "Cores are independent engines that run instruction streams.",
      "Last-level cache buffers data between cores and system RAM.",
      "The memory controller schedules reads and writes across DDR channels.",
      "The on-die interconnect links cores, cache, memory and I/O into a fast network.",
      "Clock rate sets the ceiling on operations per second, bounded by power and thermals.",
    ],
  },
  gpu: {
    title: "How the GPU computes in parallel",
    intro: "A GPU keeps thousands of lightweight threads in flight and switches rapidly among them to hide the latency of memory access.",
    points: [
      "The GPU package holds many shader and accelerator blocks.",
      "VRAM stores textures, frame buffers and compute data at high bandwidth.",
      "Cooling fans push air through the fins to remove heat from the GPU and VRAM.",
      "The PCIe connector links the card to the CPU and platform.",
      "Parallel throughput is far higher than a CPU, at higher per-thread latency.",
    ],
  },
  memory: {
    title: "How RAM holds working data",
    intro: "DRAM stores each bit as charge in a tiny capacitor, so every cell must be refreshed repeatedly even when its data is not changing.",
    points: [
      "DRAM chips are arrays of volatile cells organized into banks and ranks.",
      "Edge contacts carry command, address, data and power to the motherboard.",
      "The SPD stores module identity and supported timing profiles.",
      "Capacity sets how much can stay active; frequency and timings set access speed.",
      "Data vanishes without power, so RAM is working memory, not storage.",
    ],
  },
  storage: {
    title: "How an SSD stores persistently",
    intro: "NAND flash retains data without power, and the NVMe controller schedules thousands of parallel requests straight into the flash.",
    points: [
      "The NVMe controller handles scheduling, error correction and wear leveling.",
      "NAND flash keeps data in floating-gate or charge-trap cells.",
      "The M.2 connector carries PCIe lanes, control signals and power.",
      "NVMe parallel queues let software submit many requests at once.",
      "Sequential transfers reach several GB/s; random access is far faster than disk.",
    ],
  },
  power: {
    title: "How the PSU converts energy",
    intro: "A switched-mode supply switches energy at high frequency, turning mains AC into the stable low-voltage DC rails each part needs.",
    points: [
      "The switching transformer transfers energy between isolated primary and secondary stages.",
      "High-frequency switching allows a much smaller transformer than a linear supply.",
      "The cooling fan controls temperature across switching devices and magnetics.",
      "Modular outputs provide detachable DC cables for the board, GPU and peripherals.",
      "Regulation and protection circuitry determine system stability.",
    ],
  },
  cooling: {
    title: "How the cooler moves heat",
    intro: "A heat pipe's working fluid evaporates and condenses repeatedly, moving a lot of heat through a tiny temperature difference by phase change.",
    points: [
      "The base plate takes heat out of the CPU package.",
      "Heat pipes carry that heat quickly to the whole fin stack.",
      "Fins spread heat into the passing air over a large aluminium area.",
      "The PWM fan varies speed with temperature.",
      "Mounting pressure, interface material and airflow set efficiency.",
    ],
  },
  network: {
    title: "How the NIC moves data",
    intro: "A network interface controller turns system-memory traffic into Ethernet frames and exchanges them through the PHY transceiver.",
    points: [
      "The NIC controller implements DMA, packet queues and MAC functions.",
      "The PHY converts digital symbols to and from the electrical link signal.",
      "The Ethernet port isolates and connects to network cabling via magnetics.",
      "The PCIe interface moves packet buffers between the NIC and system memory.",
      "Offloading checksums and segmentation saves the CPU repetitive work.",
    ],
  },
  case: {
    title: "How the system works together",
    intro: "A computer is layered: hardware provides resources, firmware initializes them, the OS manages them, and applications request services.",
    points: [
      "The motherboard is the electrical backbone linking the primary subsystems.",
      "The graphics subsystem handles display and compute with a parallel processor and local memory.",
      "The power subsystem converts incoming energy into regulated DC rails.",
      "System airflow routes intake and exhaust to carry waste heat out of the chassis.",
      "Subsystems cooperate at very different timescales — nanosecond cache, millisecond storage.",
    ],
  },
};

export function getLesson(id: OrganId, locale: string): Lesson {
  return (locale === "zh" ? zh : en)[id];
}
