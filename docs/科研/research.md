---
title: 科研
tags:
  - 科研
nostatistics: false
comments: true
---

## 方法论

- [最近关于科研工作的一些思考 - 东一伊蕾娜](https://zhuanlan.zhihu.com/p/26579631480?utm_psn=1878138759716950017)

## 项目/Paper

> https://github.com/showlab/PhotoDoodle

Tiamat AI联合NUS、bytedance等单位发布PhotoDoodle，专为艺术创作设计。它通过两阶段训练策略实现高效定制化编辑：先在大规模数据上预训练通用模型OmniEditor，再通过少量艺术家提供的图像对（20-50组）微调EditLoRA模块，精准捕捉个性化风格。其核心技术位置编码克隆可精确记录原始图像像素位置，确保添加的装饰元素（如卡通怪兽、魔法特效）与背景在透视、光影上无缝融合，同时保持背景零失真。该工具支持多模态指令控制（如“让猫变白”“添加粉色烟雾”），并开源了包含6种艺术风格、300+样本的数据集及代码，为艺术创作与AI技术融合开辟了新路径。

TD;DR: PhotoDoodle是一个图像编辑框架，可以通过少量设计师给定的“before-after”图片，定制专属风格的图像编辑器。图像编辑也迎来了自己的LoRA moment。

---