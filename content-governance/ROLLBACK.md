# 内容重构恢复与回滚

本次调整没有删除原始链接记录，也没有重建数据库（项目本身不使用数据库）。恢复前应先停止 `mkdocs serve`，并另存当前工作区，避免覆盖后无法比较。

## 方案一：恢复本次任务开始前的原项目

完整备份位于：

`D:\Code\Awesome-Tech-Share-backups\20260719-131034`

1. 在备份目录运行 `D:\Program\Miniconda\envs\mkdocs\python.exe verify_backup.py`，确认校验仍通过。
2. 将当前工作区另存到一个新目录。
3. 用备份中的 `repository` 目录恢复项目；也可使用 `repository.bundle` 恢复 Git 仓库。
4. 在恢复目录执行 `conda run -n mkdocs mkdocs build --strict`。

该方案会恢复原始代码、原始 Markdown、配置、静态资源和 `.git` 历史，是最完整的回滚方式。

## 方案二：恢复撤销错误前端前的现场

现场快照位于：

`D:\Code\Awesome-Tech-Share-backups\20260719-132907-before-content-restructure`

它用于比较此前错误前端重构的状态，不建议作为当前内容站点的长期版本。

## 方案三：仅恢复迁移涉及的内容文件

迁移前文件副本位于：

`D:\Code\Awesome-Tech-Share\migration-backups\content-restructure-v1`

`migration-manifest.json` 列出 11 个被迁移脚本修改的源文件和 5 个迁移生成页。可按清单逐个恢复源文件并移除生成页。因为导航与少量标题命名也在迁移后调整，若需要完全恢复，优先使用方案一，不要只执行局部恢复。

任何恢复完成后都应重新运行：

```powershell
conda run -n mkdocs mkdocs build --strict
```

## 方案四：恢复统一分类前状态

本轮将 5 个临时迁移页的 153 条记录并入正式分类页。操作前的完整备份位于：

`D:\Code\Awesome-Tech-Share-backups\20260719-140820-before-unified-classification`

逐文件回滚副本和 153 条去向明细位于：

`D:\Code\Awesome-Tech-Share\migration-backups\unified-classification-v2\migration-manifest.json`

完整回滚优先使用外部完整备份；只回滚本轮内容归并时，可按 v2 manifest 恢复目标页和 5 个临时源页，并将 `mkdocs.yml` 恢复为完整备份中的版本。
