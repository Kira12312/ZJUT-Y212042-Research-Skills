# arXiv AI/ML 今日速递
**2026年6月4日（周四）**

论文总数：1011 篇
涵盖：cs.AI, cs.LG, cs.CL, cs.CV, cs.RO, stat.ML

---

### 🔍 深度解读

#### Do Real-World Datasets Contain Natural Experiments? An Empirical Study Using Causal Feature Selection

**作者**：Gautam Gare, John Galeotti, Michael Mozer, Deva Ramanan, Nan Rosemary Ke
**领域**：stat.ML, cs.LG, cs.AI, cs.CV
**链接**：https://arxiv.org/abs/2606.03251

**核心贡献**：该研究提出了一个有趣的问题——现实世界的数据集中是否已经隐含着"自然实验"？所谓的自然实验，是指某些事件天然地对部分样本施加了干预（比如新冠疫情对感染人群就是一种自然干预），但以往的研究往往把这些干预性数据当作普通观测数据来处理。作者利用因果发现方法重建数据背后的因果图，然后基于因果链接进行特征选择。实验发现，如果将这些数据明确视为"干预后"数据来处理，下游任务性能会有所提升。这篇工作的意义在于：它提醒我们，许多真实数据集（医学、社会计算等）可能并非纯观测性的，正确识别其中的自然实验有助于更可靠地建模因果关系。

---

### 📋 更多值得关注

- **Cosmos 3: Omnimodal World Models for Physical AI** — NVIDIA 提出全模态世界模型家族，统一语言、图像、视频、音频、动作序列的联合处理与生成，在 Physical AI 理解和生成多个榜单上达到 SOTA。[https://arxiv.org/abs/2606.02800](https://arxiv.org/abs/2606.02800)

- **SCOPE: Real-Time Natural Language Camera Agent at the Edge** — 面向边缘部署的自然语言 PTZ 相机控制与场景理解智能体，用 LLM 连接感知和控制工具，关注延迟和错误模式等实际部署指标。[https://arxiv.org/abs/2606.02951](https://arxiv.org/abs/2606.02951)

- **P²-DPO: Grounding Hallucination in Perceptual Processing via Calibration Direct Preference Optimization** — 针对多模态大模型幻觉问题，提出基于校准的偏好优化方法，直接作用于感知瓶颈区域，提升模型对图像退化的鲁棒性。[https://arxiv.org/abs/2606.03376](https://arxiv.org/abs/2606.03376)

- **Learned Non-Maximum Suppression for 3D Object Detection** — 用可学习模块替代 NMS 后处理，提出 D2D-Rescore（Transformer 注意力）和 GossipNet3D（鸟瞰图消息传递），提升 LiDAR 3D 检测的紧凑性和可靠性。[https://arxiv.org/abs/2606.03568](https://arxiv.org/abs/2606.03568)

---
数据来源：arxiv.org RSS feeds
