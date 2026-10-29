# wagtail-simple-forum

**为 Wagtail 添加集成式讨论论坛，包括分类、分区、主题、帖子、审核、私信、通知、搜索以及从旧论坛应用导入的工具。**

[English](README.md) · [Русский](README.ru.md) · [Deutsch](README.de.md) · [Español](README.es.md) · [Français](README.fr.md) · [Italiano](README.it.md) · [Português (Brasil)](README.pt-BR.md) · [Nederlands](README.nl.md) · [Polski](README.pl.md) · [Türkçe](README.tr.md) · [简体中文](README.zh-CN.md) · [日本語](README.ja.md) · [한국어](README.ko.md)

## 主要功能

- 分类 → 分区 → 主题 → 帖子的层级结构和活动计数。
- 私信收件箱及线程式对话。
- 访客反垃圾、审核、搜索和频率限制。
- 旧论坛导入和重定向工具；切换流量前先验证 dry-run。

## 依赖与兼容性

- 声明的依赖: `Wagtail >= 6.0; django-prose-editor >= 0.26; nh3 >= 0.2.14`.
- Python、Django 与 Wagtail 的兼容性必须一起验证。最低依赖版本并不代表所有版本均受支持。

包元数据声明 Wagtail >= 6.0，但最低依赖版本并不代表已验证所有版本的兼容性。本归档不包含覆盖所有 Django/Wagtail 组合的完整自动化测试矩阵。升级生产环境前，请在预发布环境验证具体版本、数据库、文件存储后端和部署配置。

## 安装

请在与 Wagtail 项目相同的虚拟环境中安装此包：

```bash
pip install wagtail-simple-forum
```

按以下顺序添加应用，同时保留项目原有的其他依赖：

```python
INSTALLED_APPS = [
    # 同时保留项目需要的其他 Django/Wagtail 依赖。
    "django_prose_editor",
    "wagtail_simple_forum",
]
```

请将论坛 URL **放在 Wagtail catch-all 路由之前**；旧 URL 重定向也必须在其之前。

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls
urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,
    # 旧版路由必须放在 Wagtail 全匹配路由之前。
]
```

运行 `python manage.py migrate wagtail_simple_forum`。若要从旧 `forum` 应用导入，先运行 `python manage.py forum_import_from_app --source forum --dry-run`。.


## 初始配置

下面是最小起步示例。请根据项目调整模型名、API 字段和 URL。

```python
from django.urls import include, path
from wagtail_simple_forum.legacy_urls import urlpatterns as legacy_forum_urls

urlpatterns = [
    path("forum/", include("wagtail_simple_forum.urls")),
    *legacy_forum_urls,  # 旧版路由必须放在 Wagtail 全匹配路由之前。
]
```

运行 `python manage.py migrate wagtail_simple_forum`。若要从旧 `forum` 应用导入，先运行 `python manage.py forum_import_from_app --source forum --dry-run`。

导入旧论坛前请备份数据库并先执行 `--dry-run`。在导入和检查完成之前保留旧应用。


## 重要设置与行为

本目录中的英文 README 是规范参考文档，包含完整设置表和扩展示例。本译文覆盖实际安装步骤和关键安全注意事项；修改高级设置前请查阅英文文档。

完整设置说明请参阅[英文 README](README.md)。

### 重要注意事项

论坛 URL 和旧路由重定向必须放在 Wagtail catch-all 路由之前。导入旧论坛前先备份数据库，并先运行 `--dry-run`。

## 安全与运维建议

- 请保持依赖更新。用户编写的 HTML 应使用预期的清理和渲染路径；不要无条件对已存储的评论或论坛帖子使用 `|safe`。
- 请分别使用普通用户、受限用户、版主和管理员验证迁移与权限。
- 多站点部署时，请测试每个已配置域名以及一个未知主机。找不到 Site 时，查询不得扩大为读取所有站点的数据。
- API 令牌、SMTP 凭据和私有 URL 都应视为机密。不要提交到 Git，也不要放入公开的问题报告。
- 执行迁移、批量移动、导入或首次批量发布之前，请备份数据库和媒体文件，并先在预发布环境测试。

## 推荐组合

- `wagtail-mptt-comments` 为论坛之外的文章提供评论；Prose 图片选择器仅在自定义字段需要时使用。
- 图片目录与论坛数据相互独立。

## 验证清单

- [ ] 在预发布环境安装候选版本，并记录 Python、Django、Wagtail 和数据库版本。
- [ ] 运行 `python manage.py check` 和包迁移。
- [ ] 使用普通用户与受限用户测试主要流程。
- [ ] 检查日志、访问权限、缓存、备份和恢复。

本归档通过静态语法与打包检查，但当前环境未完成 Django/Wagtail 运行时集成测试。请将以下清单视为发布前的必检项目，而不是所有版本组合均已测试的声明。

## 故障排查

如果流程无法运行，请检查应用配置、迁移、URL 顺序、用户权限和 Django 日志，并将包版本与示例和英文 README 对照。

## 许可证与支持

MIT. 源代码: [https://github.com/vovansrnd/wagtail-simple-forum](https://github.com/vovansrnd/wagtail-simple-forum).

