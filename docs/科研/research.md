---
title: 科研
tags:
  - 科研
nostatistics: false
comments: true
---

## 论文阅读

- [多模态平衡学习 On-the-fly Modulation for  Balanced Multimodal Learning 论文阅读总结 - kluster]( https://zhuanlan.zhihu.com/p/1902321276116276570)
- [LRU-K 论文阅读笔记](https://zhuanlan.zhihu.com/p/1898469067981066716)
- [多任务论文阅读 M3GAT - kluster的文章 - 知乎](https://zhuanlan.zhihu.com/p/1898154047925655393)
- [【论文阅读】非局部神经网络浅读（简介+代码）- SuXiaofei's Blog](https://xiaosuqaq.github.io/2025/04/15/%E9%9D%9E%E5%B1%80%E9%83%A8%E7%A5%9E%E7%BB%8F%E7%BD%91%E7%BB%9C.html)
- [Coaxial 论文笔记 服务器cpu上用cxl type3设备代替ddr-dram的设计 - Exce1sior](https://zhuanlan.zhihu.com/p/1888850042107978402?utm_psn=1889852364510445569)
- [Reward Hacking in Reinforcement Learning](https://lilianweng.github.io/posts/2024-11-28-reward-hacking/)
- [Foundational Models for 3D Point Clouds A Survey and Outlook - wnc 的咖啡馆](https://wncfht.github.io/notes/Blogs/posts/Foundational%20Models%20for%203D%20Point%20Clouds%20A%20Survey%20and%20Outlook/)

- [【论文阅读】TOWARDS THE GENERALIZATION OF CONTRASTIVE SELF-SUPERVISED LEARNING（人工智能之自监督对比学习的泛化性理论）\_towards the generalization of image quality assess - CSDN博客](https://blog.csdn.net/ModestCoder_/article/details/144904849)
- [用于决策的世界模型 -- 论文 World Models (2018) & PlaNet (2019) 讲解 - 伊犁纯流莱 - 博客园](https://www.cnblogs.com/tshaaa/p/18670731)

## 项目/Paper

> https://github.com/showlab/PhotoDoodle

Tiamat AI联合NUS、bytedance等单位发布PhotoDoodle，专为艺术创作设计。它通过两阶段训练策略实现高效定制化编辑：先在大规模数据上预训练通用模型OmniEditor，再通过少量艺术家提供的图像对（20-50组）微调EditLoRA模块，精准捕捉个性化风格。其核心技术位置编码克隆可精确记录原始图像像素位置，确保添加的装饰元素（如卡通怪兽、魔法特效）与背景在透视、光影上无缝融合，同时保持背景零失真。该工具支持多模态指令控制（如“让猫变白”“添加粉色烟雾”），并开源了包含6种艺术风格、300+样本的数据集及代码，为艺术创作与AI技术融合开辟了新路径。

TD;DR: PhotoDoodle是一个图像编辑框架，可以通过少量设计师给定的“before-after”图片，定制专属风格的图像编辑器。图像编辑也迎来了自己的LoRA moment。

---

