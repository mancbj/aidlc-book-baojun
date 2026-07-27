# GitHub Pages 启用与排障

## 现象

- 访问 `https://mancbj.github.io/aidlc-book-baojun/` 提示 **There isn't a GitHub Pages site here.**
- Actions 中 `deploy` 失败：`Failed to create deployment (status: 404)`，并提示检查 [Pages 设置](https://github.com/mancbj/aidlc-book-baojun/settings/pages)。

## 原因

仓库需存在 **GitHub Pages 站点**，且发布源为 **GitHub Actions**（与 `.github/workflows/pages.yml` 中的 `upload-pages-artifact` / `deploy-pages` 配套）。仅把 HTML 放在 `book-site/` 或 README 里写 `github.io` 链接，不会自动创建站点。

自 v0.9.009 起，`pages.yml` 的 **deploy** job 会在首次部署前调用 `configure-pages`（`enablement: true`），在权限允许时自动为仓库启用 Pages。

## 维护者手动启用（自动启用失败时）

1. 打开 [Settings → Pages](https://github.com/mancbj/aidlc-book-baojun/settings/pages)。
2. **Build and deployment → Source** 选择 **GitHub Actions**（不要选 “Deploy from a branch” 作为长期源，以免与 workflow 产物不一致）。
3. 在 [Actions → Record Progress and Publish Pages](https://github.com/mancbj/aidlc-book-baojun/actions/workflows/pages.yml) 对 `main` 执行 **Run workflow**。
4. 等待 `build` 与 `deploy` 成功后，再打开：
   - 阅读站：<https://mancbj.github.io/aidlc-book-baojun/book-site/index.html>
   - 驾驶舱：<https://mancbj.github.io/aidlc-book-baojun/site/index.html>

## 构建失败但需审阅产物

`build` job 仍会上传 `github-pages` artifact（即使 `configure-pages` 探测失败）。可在该次 workflow run 的 **Artifacts** 中下载页面树，本地解压后用浏览器打开 `book-site/index.html`。

## 组织策略

若仓库属于 Organization 且禁止 Actions 自动启用 Pages，`enablement: true` 可能返回 403。需组织管理员在 Settings → Pages 中允许该仓库使用 Pages，或由管理员按上文手动选择 **GitHub Actions** 源。
