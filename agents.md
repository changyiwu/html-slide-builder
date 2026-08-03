# html-slide-builder（專案藍圖）

> 本檔為跨 Agent 通用的專案藍圖（AGENTS.md 開放標準）。任何 Agent 的每個 session 都應先讀本檔＋`handoff.md`。

## 專案簡介

一個跨 Agent 通用的 Skill（Claude Code／Codex／OpenCode／Antigravity 四家共用同一份、安裝名皆為 `html-slide-builder`），把任何主題或內容（教材、提案、活動、會議、報告）轉為 Reveal.js HTML 互動簡報。主要入口 `skill/SKILL.md`，安裝程式 `install.py`。本專案 fork 自上游，已移除上游的 Firebase demo 硬編碼 key。

## 關鍵時程

<!-- 目前無固定時程 -->

## 目標與路線圖

- [x] 階段一：Skill 初始化與規則調整（每頁 AI 生成底圖、emoji 預設視覺提示、卡片 hover 微互動）
- [x] 階段二：移除上游 Firebase demo 硬編碼 key，建立 fork 並推送 `origin/main`
- [x] 階段三：專案更名為 `html-slide-builder`，`install.py` 改為四個 Agent 通用（各自偵測生圖技能）
- [x] 階段四：執行 `python install.py` 實際安裝到本機四個 Agent 並驗證
- [ ] 階段五：以一份無敏感資訊的教材測試輸出到 `output/<英文短名>/`
- [ ] 階段六：製作新簡報時依內容套用 `[HOVER]`，以實際瀏覽器預覽確認效果

## 資料夾結構

```
html-slide-builder/
├─ skill/
│  ├─ SKILL.md                              # Skill 觸發條件與簡報製作流程
│  ├─ references/reveal-template.md         # Reveal.js HTML 範本與元件樣式
│  ├─ references/firebase-config.md         # 文字雲與投票的 Firebase 片段（只留占位符）
│  └─ scripts/remove_bg.py                  # 圖標裁切後的去背工具
├─ install.py                               # 安裝程式
├─ output/                                  # 本機產出的簡報（.gitignore 排除）
├─ README.md
├─ agents.md                                # 本檔：專案藍圖
├─ handoff.md                               # 交接檔（每次收工必更新）
├─ .agents/  .gitignore
└─ LICENSE
```

## 同步層級（本專案初始化至第 3 層級）

| 層級 | 平台 | 位置 | 讀取時機 |
|------|------|------|---------|
| L1 | 本地（GDrive） | `agents.md`＋`handoff.md` | 每個 session |
| L2 | GitHub | https://github.com/changyiwu/html-slide-builder （公開） | 指定時 |
| L3 | Obsidian | `html-slide-builder/專案工作流程.md` | 有需要時 |

## 三個檔案的職責（依「時效性」分家，不是依「詳細程度」）

| 檔案 | 時效 | 寫入方式 | 放什麼 |
|------|------|---------|--------|
| `handoff.md` | **只對下一個 session 有效**，過期即丟 | 每次收工整份重寫 | 做到哪、下一步、**這次**的暫時 workaround |
| `agents.md`（本檔） | **長期有效**，每個 session 都適用 | 只有規則本身變了才改 | 目標、路線圖、常設規則、結構 |
| Obsidian／`git log` | **歷史**：發生過什麼、為什麼 | 只增不刪 | 決策紀錄、踩坑完整版、逐次進度 |

驗收標準：**`handoff.md` 整份刪掉，不應損失任何長期資訊**——會的話代表該升級進本檔卻沒升級。

**本檔不要出現的東西**：❌ `## 最近進度`／逐次工作紀錄、❌ 決策理由與踩坑完整版。2026-08-03 移除了 `## 最近進度`，內容逐條比對後已在 L3 筆記的〈🗓️ 最近更動紀錄〉——**是主動移除，不是遺漏，不要補回來**。踩過的坑只把**結論**收斂成一條祈使句寫進〈工作約定〉，原因留 L3。

## 工作約定

- 任何 Agent、任何電腦：**開工先讀 `handoff.md`，收工必更新 `handoff.md`**
- 修改共用檔案前先讀最新內容，避免覆蓋其他 Agent 的變更
- **`skill/` 改完用 `python install.py` 或位元組複製的同步工具都可以**：生圖技能改為執行時解析（見〈設計決策〉），源檔不再有 `{{DRAW_*}}` 占位符，四家副本是同一份 bytes。**但若有設定 Firebase**，`install.py` 會把金鑰注入副本的 `references/firebase-config.md`，那份就不等於源檔了——這種情況只能用 `install.py`，位元組複製會洗掉金鑰
- 所有回應與文件使用繁體中文
- 保留既有 README、Skill 指令、授權資訊與專案歷史；變更時採**最小範圍修改**
- 產出的簡報集中於 `output/<簡報英文短名>/`，不可把教材、API 金鑰、服務帳戶憑證或 Firebase 私密設定提交至 Git
- 不修改 Firebase 安全規則、不部署 GitHub Pages、不建立或連接 GitHub 儲存庫，除非使用者明確要求
- 任何提交或推送前，先確認 Git 狀態、遠端分支與提交範圍；**不使用 force push**
- Obsidian 專案筆記的建立或更新，不寫入 `02-知識庫/log.md`
