# Tech Stack

## Overview

本项目采用面向 GitHub 的轻量静态技术栈，以 Markdown 作为书稿源文件、原生 Web 技术呈现鸟瞰页面，并通过 Python 与 GitHub Actions 生成进度记录和完成自动发布。该方案避免引入不必要的应用框架与构建复杂度。

## Languages

- Markdown：章节、计划、决策和写作记录的主要格式
- HTML、CSS、JavaScript：行动指南和进度鸟瞰页面
- Python：进度聚合、校验、快照生成等仓库自动化
- YAML：GitHub Actions、项目配置和结构化任务数据

选择这些语言是为了让内容易于审阅、变更易于比较，并确保自动化脚本可在本地与 GitHub Actions 中一致运行。

## Framework

不使用前端应用框架。页面保持原生 HTML、CSS、JavaScript，并以静态站点方式运行。

作者本地 `working-book/ai_dlc_book_action_guide.html` 已采用该形态；公开仓库沿用其视觉原则，但不依赖或发布该本地文件。

## Authentication

不需要应用内身份验证。协作权限由 GitHub 仓库、分支保护和 Pull Request 权限管理。

## Infrastructure & Deployment

- GitHub：版本控制、Issue、Pull Request 和协作入口
- GitHub Projects：任务状态和整体进度鸟瞰
- GitHub Actions：校验、进度聚合、关键节点快照与发布
- GitHub Pages：发布行动指南与可视化进度页

部署以静态资源为主，避免服务器、数据库和运行时运维。

## Package Manager

初期不引入包管理器。Python 自动化优先使用标准库，页面继续直接引用必要的浏览器端静态依赖。只有出现明确、持续的依赖需求时再引入包管理。

## Decision Relationships

- 无框架静态页面与 GitHub Pages 直接发布相匹配。
- Markdown、YAML 和 Git 历史共同构成可审计的写作事实源。
- Python 脚本从事实源生成可视化数据，GitHub Actions 在关键更新时自动执行并留痕。
- 协作和访问控制完全交由 GitHub，避免重复建设认证系统。
