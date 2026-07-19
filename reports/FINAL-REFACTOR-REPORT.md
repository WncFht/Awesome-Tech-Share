# Awesome Tech Share 内容重构执行报告

执行日期：2026-07-19（Asia/Shanghai）

## 1. 项目、技术栈与备份

- 项目是纯静态 MkDocs 站点；无后端、数据库或上传目录。内容数据实际存储在 `docs/**/*.md`，导航和主题配置位于 `mkdocs.yml`。
- 实测环境：conda 环境 `mkdocs`、Python 3.10.19、MkDocs 1.6.1、Material for MkDocs 9.7.7。MkDocs 已是当前 1.x 最新版，Material 已由 9.7.6 更新至 9.7.7。
- 原始完整备份：`D:\Code\Awesome-Tech-Share-backups\20260719-131034`。
- 撤销此前错误前端前的现场备份：`D:\Code\Awesome-Tech-Share-backups\20260719-132907-before-content-restructure`。
- 统一分类前的完整备份：`D:\Code\Awesome-Tech-Share-backups\20260719-140820-before-unified-classification`。
- 内容迁移前的逐文件回滚副本：`D:\Code\Awesome-Tech-Share\migration-backups\content-restructure-v1`。
- 原始备份已验证 855 个文件、10,870,092 字节，SHA-256 全部一致；Git bundle、Git fsck、严格构建及 146 个搜索文档均通过。
- 现场备份已验证 893 个文件、11,330,524 字节，文件哈希、Git bundle 和严格构建均通过。
- 统一分类前备份已验证 1,130 个文件、22,650,022 字节，逐文件 SHA-256 完全一致，Git bundle 验证通过。

## 2. 原始数据与分类结构

原始基线：40 个 Markdown 文件、107 个标题节点、655 条外部链接记录、630 个唯一 URL、6 条非空简介、3 条可恢复的 Markdown 畸形记录。项目没有独立数据库记录。

- 首页：1
- 计算机科学：57
  - 系统原理 26、编程 18、数学基础 13
- 人工智能：87
  - AI 理论基础 38、算法与实现 15、大语言模型 23、AI 应用 11
- 开发：151
  - 前后端 4、嵌入式开发 3、计算机图形学 5、开发工具 101、项目 38
- 学习成长：219
  - 学习资源 71、科研记录 20、技术思考 107、职业发展 21
- 待整理：3
- 总结：122
- 贡献者：15

完整的 101 个原始分类/标题路径及数量见 `content-audit/category-counts.csv`，全部原始记录见 `content-audit/all-records.csv`。

## 3. 原始分类主要问题

1. `学习资源/AI` 混合了 io_uring、开源架构、AFL++、GPU、推荐系统、机器人和大模型等不同主题。
2. `开发工具` 有 101 条记录，同时混用框架、环境、知识管理、论文工具、OCR、RSS 和普通项目，范围过大。
3. `技术观点`、`科研学习` 内存在大量 AI、系统、编译器、图形学及职业内容，主题边界不稳定。
4. `总结` 与学习记录、人生经验和科研复盘边界重叠。
5. 同级标题混用技术领域、课程、产品名及缩写，并存在 `Pytorch`、`obsidia`、`LaTex` 等不统一名称。
6. 分类规模极不均衡：数据库和电路理论各 1 条，开发工具 101 条，每周总结 91 条。
7. 有 25 组完全相同 URL（50 条记录），以及“强化学习”链接到 NLP 总结、“LSTM”链接到 Vanilla RNN 等明确错配。
8. 原始简介只有 6 条，其中部分是语法残留或标题后缀，无法形成一致可靠的简介体系。

## 4. 新分类结构

新体系以资源主要技术主题/用途为唯一同级划分标准，采用五个顶层主题域、最多两级子分类：

- 计算机科学基础（85）：数学与理论 13、编程与算法 32、系统与体系结构 18、网络与分布式 13、数据库与编译 7、软件分析与性能 2。
- 人工智能与机器人（189）：机器学习基础 14、深度学习 16、强化学习 31、大语言模型与智能体 70、生成式与多模态 14、具身智能与机器人 14、AI 工程与系统 30。
- 软件开发与工程（120）：Web 与后端 9、嵌入式与硬件开发 3、图形学与可视化 10、开发环境与基础设施 27、开发工具与效率 44、开源项目与工程实践 23、安全工程 4。
- 学习与研究（90）：课程与学习资源 10、科研方法 47、论文阅读 22、知识管理与写作 2、技术观点 2、社区与资讯 7。
- 成长与职业（155）：职业发展 7、学习记录与总结 122、阅读与随笔 13、人生经验 13。
- 站点功能（16）：首页 1、贡献者 15；Tags 不计外部链接记录。

分类定义保存在 `../content-governance/category-taxonomy.yml`，分类规则保存在 `../content-governance/classification-rules.json`。

## 5. 分类合并、拆分、更名与迁移

- 101 个原始分类/标题路径归整为 32 个新路径（包含首页和贡献者两个功能路径）。
- 655/655 条记录均形成建议去向：高置信 451 条、中置信 204 条、低置信 0 条、未映射 0 条。
- 实际跨主题迁移 153 条，原位内容修正 11 条，复杂记录跳过 0 条。
- 第二轮将 153 条中间迁移记录全部并入 21 个正式主题页面，删除 5 个临时“资源补充”页及对应导航入口。
- 对中间清单再次逐条复核，纠正 NLP 课程、AI Native、OAuth、Redis 项目、编译器讨论和 Linux 日志 API 等明显边界错误。
- 只新增原体系确实缺失的 `AI 工程与系统`、`安全工程` 两个正式分类页。
- 每个迁移项都保留原路径、原行号和记录 ID 注释。完整逐条迁移原因见 `content-audit/adjustment-plan.csv`，聚合映射见 `content-audit/category-mapping-summary.csv`。
- 导航显示名称更名为“计算机科学基础、人工智能与机器人、软件开发与工程、学习与研究、成长与职业”；旧内容 URL 和原页面文件继续保留。

## 6. 标题、简介与语法修正

- 明确标题修正 13 条，详见 `content-audit/title-change-plan.csv`。
- 明确简介修正 8 条，详见 `content-audit/description-change-plan.csv`。
- 修复 4 条链接语法问题；迁移后畸形解析记录由 3 条降为 0 条。
- 修正包括 CacheBlend 论文错题名、DouZero+ 论文标题与简介、Vanilla RNN/NLP 总结错配、Obsidian/LaTeX 等资源名称，以及具身智能指南说明。
- 无法可靠读取页面内容的记录不改写简介，只保留原值并标记人工确认。
- 可重复执行的明确修正规则保存在 `../content-governance/content-fixes.json`。

## 7. 重复、失效与待人工确认链接

对全部 630 个唯一 URL 执行只读状态、重定向、HTML title、H1 和 meta description 检查：

- 可直接读取：340
- 访问受限：228
- 404/410：40
- 软失效：1
- 服务端错误：10
- TLS 错误：7
- 超时：3
- 网络错误：1

检测到 25 组完全相同 URL、共 50 条记录；没有自动合并或删除。链接检查级别有 302 条非正常关联记录，综合重复、标题匹配等规则后，调整清单中共有 438 条需人工确认。详细结果见 `content-audit/exact-duplicates.csv`、`content-audit/link-check-results.csv` 和 `content-audit/manual-review-plan.csv`。在线暂时不可访问不视为删除依据。

## 8. 前端撤销与微调

已撤销此前偏离需求的目录式新首页和复杂交互：恢复 `docs/index.md`、`README.md`、`mkdocs.yml`、部署工作流的原始布局/配置，并移除此前新增的 `docs/catalog.md`、`docs/assets/data/catalog.json`、`overrides/css/catalog.css`、`overrides/js/catalog.js`、`scripts/catalog.py`、`tests/test_catalog.py`、`MAINTENANCE.md` 和旧基线报告。

本次没有新增 CSS、JavaScript、浮窗、抽屉、设置中心、筛选面板、动画或全新页面组件。仅更新 MkDocs 原生导航分组、少量标题命名，并移除一个重复加载的 MathJax CDN。首页布局、配色、信息密度、主题和主要浏览方式保持原样。

## 9. 数据迁移与零丢失验证

迁移脚本在应用前检查原始数据指纹，并先写入独立迁移副本。迁移后验证结果：

| 项目 | 迁移前 | 迁移后 | 结果 |
|---|---:|---:|---|
| 内容记录 | 655 | 655 | 一致 |
| 唯一 URL | 630 | 630 | 一致 |
| 重复出现数 | 25 | 25 | 保留 |
| Markdown 文件 | 40 | 41 | 新增 2 个正式主题页；删除 1 个空页面；5 个临时迁移页已移除 |
| 非空简介 | 6 | 10 | 按已确认规则补正 |
| 可恢复畸形记录 | 3 | 0 | 已修复 |

URL 多重集合、按 URL 对应的标题多重集合、简介多重集合均与执行计划完全一致；153 个迁移标记全部存在，11 个源文件备份和 5 个生成页全部存在。机器可读验证结果见 `post-migration/validation.json`，状态为 `verified: true`。

## 10. 构建、运行和页面测试

- `requirements.txt` 与 `environment.yml` 已锁定 `mkdocs==1.6.1`、`mkdocs-material==9.7.7`；`pip check` 无依赖冲突。
- `conda run -n mkdocs mkdocs build --strict`：通过。
- `conda run --no-capture-output -n mkdocs mkdocs serve --strict --dev-addr 127.0.0.1:8000`：成功启动于 `/Awesome-Tech-Share/`。
- 首页：原布局、主题和页脚正常，无本次新增的复杂组件。
- 分类导航：五个新顶层主题、Tags 和贡献者均显示正常。
- 内容页：153 条中间记录均可在正式分类页访问，外部链接正常生成；页面和导航中不再出现“主题迁入”或“资源补充”。
- 搜索：查询 `DouZero` 返回 1 个匹配文档，并显示修正后的标题与简介。
- 移动端：390×844 视口实测无横向溢出。
- 空内容复核：删除 10 个无正文/链接/图片/子内容的空标题和空的 `docs/其他/暂时难以整理的.md`；复核后空标题、空页面均为 0。
- 链接显示修复：清理两条迁移残留断句、7 个 URL 尾部空格，修复 Ultra-Scale 完整标题和 Neural Network 错题名；无有效 URL 的 6.5840 Lab 4 记录改为明确的普通文本，不再生成错误链接。
- 构建提示：新文件尚无 Git 历史；旧 `docs/其他/暂时难以整理的.md` 保留但不进入导航；`操作系统.md` 有一条原项目已有的不可识别相对链接。以上均未造成构建失败。
- 未执行线上部署；本次只完成本地严格构建和服务测试。

## 11. 尚未解决及待人工确认事项

- 438 条记录需要人工确认，主要受站点反爬、登录、TLS、超时、404/410、重复链接或页面标题不足影响。
- 25 组重复 URL 全部保留，需要内容维护者判断哪些是有意跨分类引用。
- 40 个 404/410 和 1 个软失效地址仍保留，需人工判断永久失效、迁址或暂时异常。
- `docs/其他/暂时难以整理的.md` 已迁空但保留原文件用于历史兼容，未删除。
- 原项目绝大多数记录没有简介；本次遵守“无法确认不编写”原则，没有批量生成未经证实的说明。

## 12. 启动与部署方法

```powershell
conda activate mkdocs
mkdocs build --strict
mkdocs serve --strict --dev-addr 127.0.0.1:8000
```

本地地址为 `http://127.0.0.1:8000/Awesome-Tech-Share/`。现有 GitHub Pages 工作流仍保留；部署前应先通过严格构建并审阅待人工确认清单。

## 13. 回滚与恢复

完整说明见 `../content-governance/ROLLBACK.md`。完整恢复优先使用原始备份 `D:\Code\Awesome-Tech-Share-backups\20260719-131034`；恢复本轮统一分类前状态可使用 `D:\Code\Awesome-Tech-Share-backups\20260719-140820-before-unified-classification`；逐文件恢复可参考两个迁移 manifest。恢复后必须重新执行严格构建。

## 14. 修改、新增及删除文件清单

修改文件：

- `mkdocs.yml`
- `docs/AI/AI应用/具身智能.md`
- `docs/AI/AI应用/AIGC内容生成.md`
- `docs/AI/AI应用/多模态技术.md`
- `docs/AI/AI理论基础.md`
- `docs/AI/算法与实现.md`
- `docs/AI/大语言模型/LLM原理.md`
- `docs/AI/大语言模型/RAG检索增强.md`
- `docs/AI/大语言模型/AI-Agent智能体.md`
- `docs/CS/数学基础/数学杂项.md`
- `docs/CS/系统原理/计算机网络.md`
- `docs/CS/系统原理/操作系统.md`
- `docs/CS/系统原理/体系结构.md`
- `docs/CS/系统原理/分布式.md`
- `docs/CS/系统原理/编译原理.md`
- `docs/CS/编程/编程.md`
- `docs/CS/编程/算法.md`
- `docs/links/index.md`
- `docs/其他/暂时难以整理的.md`
- `docs/学习成长/学习资源.md`
- `docs/学习成长/技术思考/技术观点.md`
- `docs/学习成长/技术思考/科研学习.md`
- `docs/学习成长/科研记录.md`
- `docs/学习成长/职业发展/工作就业.md`
- `docs/开发/前后端.md`
- `docs/开发/计算机图形学.md`
- `docs/开发/开发工具.md`
- `docs/开发/项目.md`

新增内容页：

- `docs/AI/AI工程与系统.md`
- `docs/开发/安全工程.md`

新增治理、迁移和验证文件：

- `content-governance/category-taxonomy.yml`
- `content-governance/classification-rules.json`
- `content-governance/content-fixes.json`
- `content-governance/ROLLBACK.md`
- `scripts/content_audit.py`
- `scripts/check_links.py`
- `scripts/build_adjustment_plan.py`
- `scripts/apply_content_migration.py`
- `scripts/validate_content_migration.py`
- `scripts/integrate_migrated_resources.py`
- `scripts/__init__.py`
- `migration-backups/content-restructure-v1/**`
- `migration-backups/unified-classification-v2/**`
- `reports/content-audit/**`
- `reports/post-migration/**`
- `reports/FINAL-REFACTOR-REPORT.md`

本次内容重构没有删除任何原始内容记录。删除的 5 个 `资源补充.md` 均为第一轮迁移生成的临时文件，其 153 条内容已逐条并入正式主题页，并保留于统一分类前备份和 v2 迁移副本中。此前错误前端的新增文件仍可从第二份现场备份恢复。

空内容与链接显示清理前的完整备份位于 `D:\Code\Awesome-Tech-Share-backups\20260719-142442-before-empty-heading-link-fixes`，已验证 1,214 个文件、22,847,209 字节逐文件一致。该轮仅删除空页面/空标题和非链接断句，655 条外部链接记录与 630 个唯一 URL 均保持不变。
