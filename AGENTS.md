# AGENTS.md

## 專案概要

- 專案：`claude-html-slide-builder`
- 用途：將任何主題或內容（包含教材、提案、活動、會議與報告）轉為 Reveal.js HTML 互動簡報的 Claude Code Skill。
- 主要入口：`skill/SKILL.md`
- 安裝程式：`install.py`
- 文件入口：`README.md`

## 主要結構

- `skill/SKILL.md`：Skill 的觸發條件與簡報製作流程。
- `skill/references/reveal-template.md`：Reveal.js HTML 範本與元件樣式。
- `skill/references/firebase-config.md`：文字雲與投票的 Firebase 程式碼片段；只保留使用者設定的占位符。
- `skill/scripts/remove_bg.py`：圖標裁切後的去背工具。
- `output/`：執行 Skill 時產出的簡報；為本機生成內容，不提交版本控制。

## 工作規則

- 保留既有 README、Skill 指令、授權資訊與專案歷史；變更時採最小範圍修改。
- 產出的簡報集中於 `output/<簡報英文短名>/`，不可把教材、API 金鑰、服務帳戶憑證或 Firebase 私密設定提交至 Git。
- 不修改 Firebase 安全規則、不部署 GitHub Pages、不建立或連接 GitHub 儲存庫，除非使用者明確要求。
- 任何提交或推送前，先確認 Git 狀態、遠端分支與提交範圍；不使用 force push。

## Obsidian 專案駕駛艙

- Vault：`C:\\Users\\chang\\我的雲端硬碟\\2ndbrain`
- 駕駛艙：`claude-html-slide-builder-專案駕駛艙.md`（Vault 根目錄）
- 駕駛艙的建立或更新不寫入 `知識庫/log.md`。
