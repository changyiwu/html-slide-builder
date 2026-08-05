# 🎨 html-slide-builder — 跨 Agent 通用 Skill

> 給定任何主題或內容，自動生成完整的 **Reveal.js HTML 互動簡報** 並部署至 GitHub Pages。
> 支援 **Claude Code / Codex / OpenCode / Antigravity** 四個 Agent，一次安裝到本機已有的每一個。

[![Agent Skill](https://img.shields.io/badge/Agent-Skill-orange)](https://agents.md)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## ✨ 功能

| 功能 | 說明 |
|------|------|
| 🖼 **AI 背景底圖** | 每一頁皆套用 draw skill 生成的霓虹暗色底圖；依內容分群，每 3–5 頁可共用一張 |
| 😀 **emoji 與圖標** | 預設以 emoji 強化合適的標題與卡片；只有明確要求時才生成客製圖標 |
| 💬 **聽眾即時互動** | 交給 `word-cloud-page`／`poll-page` 技能產生獨立互動頁，簡報只放一頁 QR Code 連過去 |
| 🔀 **視覺化演示** | clip-path 滑桿揭露效果；需明確指定才加入 |
| 🚀 **一鍵部署** | 自動 git init → GitHub 公開 repo → GitHub Pages |

## 📺 效果展示

- **範例簡報**：[https://mathruffian-dot.github.io/html-vs-markdown/](https://mathruffian-dot.github.io/html-vs-markdown/)
- 包含：Markdown→HTML 滑桿演示、AI 生成底圖與圖標

---

## 🔧 安裝

### 必要元件

| 元件 | 用途 | 必要？ |
|------|------|--------|
| Python 3.8+ | 安裝腳本、去背 | ✅ 必要 |
| git | 版本控制 | ✅ 必要 |
| [Pillow](https://pillow.readthedocs.io/) | 圖標裁切與去背 | ⚠️ 使用者明確要求生圖圖標時需要 |
| Draw Skill（gpt-image-2 生圖技能）| AI 生圖 | ✅ 每頁底圖需要；客製圖標僅在明確要求時生成 |
| OpenAI API Key | gpt-image-2 生圖 | ✅ 每頁底圖需要；客製圖標僅在明確要求時生成 |
| [GitHub CLI (gh)](https://cli.github.com/) | GitHub Pages 部署 | ⚠️ 自動部署需要 |

### 支援的 Agent 與安裝位置

| Agent | 全域技能目錄 | 偵測依據 |
|-------|-------------|---------|
| Claude Code | `~/.claude/skills/html-slide-builder/` | `~/.claude/` 存在 |
| Codex | `~/.agents/skills/html-slide-builder/` | `~/.agents/` 存在 |
| OpenCode | `~/.config/opencode/skills/html-slide-builder/` | `~/.config/opencode/` 存在 |
| Antigravity | `~/.gemini/config/skills/html-slide-builder/` | `~/.gemini/config/` 存在 |

設定根目錄不存在＝這台沒裝那個工具，安裝腳本會自動略過，不會建垃圾目錄。四家的安裝名一律是 `html-slide-builder`，不加 agent 前綴。

### 一鍵安裝

```bash
# 1. Clone 此 repo
git clone https://github.com/changyiwu/html-slide-builder.git
cd html-slide-builder

# 2. 執行安裝腳本（會自動檢查元件並引導設定）
python install.py
```

安裝腳本會：
- ✅ 偵測本機裝了哪幾個 Agent，讓你選擇要裝到哪幾個（預設全部）
- ✅ 逐項檢查必要元件，列出缺少的項目
- ✅ 詢問是否自動安裝 Pillow
- ✅ **各 Agent 分別偵測自己的生圖技能**（`claude-draw`／`codex-draw`／`opencode-draw`／`antigravity-draw` 等名稱含 `draw` 的技能）並在安裝報告中列出，**不會改寫副本內容**——路徑是 `SKILL.md` 執行時自行解析的，所以四家副本與源檔是同一份 bytes，用位元組複製的同步工具也不會壞
- ✅ 生圖技能沒有 CLI 腳本時（例如 Codex 的內建 Image Gen），安裝報告會標示為「自然語言生圖」

### 手動安裝

```bash
# 複製 skill 目錄到你要用的 Agent 技能資料夾（有裝哪個就複製哪個）
cp -r skill/ ~/.claude/skills/html-slide-builder/
cp -r skill/ ~/.agents/skills/html-slide-builder/
cp -r skill/ ~/.config/opencode/skills/html-slide-builder/
cp -r skill/ ~/.gemini/config/skills/html-slide-builder/
```

手動安裝也可以——`SKILL.md` 會在執行時自行解析該 Agent 的生圖技能（找技能目錄下名稱含 `draw` 的資料夾），不需要任何替換。`install.py` 的額外價值在於元件檢查。

### 專案維護與輸出

- Skill 原始碼位於 `skill/`；安裝後才會複製到本機各 Agent 的技能目錄。改完原始檔要重跑 `python install.py`（或用位元組複製的同步工具）才會生效。
- **生圖技能的路徑是執行時解析的，不是安裝時注入的。**`SKILL.md` 從自己所在的技能目錄找名稱含 `draw` 的資料夾，所以四家副本可以是同一份 bytes，`sync-skills` 這類純位元組複製的同步工具也能用。2026-08-01 以前的做法是安裝時把路徑寫死進副本，那會讓四份副本互不相同、也都不等於源檔——同步工具一跑就把占位符蓋回去、生圖失效。
- 每份生成的簡報請放在 `output/<簡報英文短名>/`，例如 `output/ai-course/`；`output/` 是本機產出，不納入版本控制。
- `.env` 與其他 API 金鑰均不可提交。GitHub 的建立與部署請在需要時另行明確執行。

---

## 🚀 使用方式

安裝後，在任一已安裝的 Agent（Claude Code／Codex／OpenCode／Antigravity）對話中說：

```
幫我做一份產品提案的 HTML 互動簡報

# 或

把以下活動企劃轉成 Reveal.js 互動簡報：
[貼上你的內容]

# 也支援教材、會議內容、報告或任意主題
```

Agent 會自動：
1. 分析簡報需求與內容，列出投影片大綱（每頁均有 `[BG:<背景名稱>]`；emoji 為預設）
2. **等你確認大綱後**才開始生成
3. 為每一頁套用 AI 生成底圖（依內容分群重用），並在合適位置使用 emoji；只有明確要求時才生成圖標或視覺化滑桿
4. 部署至 GitHub Pages 並回傳網址

---

## 📁 Skill 結構

```
html-slide-builder/
├── SKILL.md                    # 主要指令（Agent 讀取）
├── scripts/
│   └── remove_bg.py            # PIL 圖標去背腳本
└── references/
    └── reveal-template.md      # Reveal.js HTML 模板 + CSS 元件庫
```

---

## 💬 聽眾即時互動（文字雲／投票）

**本 Skill 不產生互動元件。**需要聽眾用手機即時參與時，改用另外兩個技能產生**獨立的互動頁**，簡報只放一頁 QR Code 連過去：

| 需求 | 技能 | 產出 |
|------|------|------|
| 輸入字詞 → 即時文字雲 | `word-cloud-page` | 一份可獨立部署的 `.html` |
| 選選項 → 即時圓餅／長條／折線圖 | `poll-page` | 一份可獨立部署的 `.html` |

互動頁與簡報放同一個資料夾、一起部署即可。Firebase 的設定、安全規則與 App Check 全部由那兩個技能負責，本 Skill 不再需要任何 Firebase 設定。

---

## 🛠 功能詳細說明

### 底圖生成 [BG]
- **每頁必用**：所有投影片都會套用 AI 生成底圖；同一章節或相近內容的 3–5 頁可共用一張。
- 預設生成 `ceil(投影片總數 / 4)` 張，最少 1 張、最多 6 張，再依章節數微調。
- 使用 `draw.py`（gpt-image-2 模型）生成 1536×1024 橫式底圖
- 設計風格：深暗色系、霓虹發光效果、無文字
- 透明度：封面 30–40%，一般頁 12–18%

### emoji 與圖標系統 [ICON]
- **預設**：在標題、卡片、流程節點與短標籤使用語意相符的 emoji；避免在每個句子堆疊 emoji。
- **明確要求才生成圖標**：一次生成「圖標總表」→ PIL 等分裁切 → 亮度閾值去背 → 嵌入 HTML 並搭配 `drop-shadow` 發光效果。

### 互動頁 QR Code [QR]
- **非預設功能**：只有明確要求文字雲、投票或聽眾即時參與時才加入。
- 先用 `word-cloud-page`／`poll-page` 技能產生互動頁並部署，再加一頁把網址畫成 QR Code。

### 滑桿視覺化 [VIZ]
- **非預設功能**：只有明確要求滑桿或可拖曳的前後對比時才加入。
- CSS `clip-path: inset(0 X% 0 0)` 控制揭露
- 青色霓虹發光分隔線隨滑桿移動

---

## 📋 系統需求

| 環境 | 版本 |
|------|------|
| Agent | Claude Code／Codex／OpenCode／Antigravity（任一，最新版） |
| Python | 3.8+ |
| OS | Windows / macOS / Linux |

---

## 🤝 貢獻

歡迎 PR 改進 SKILL.md 的指令品質、擴充版型與視覺元件，或分享你用此 Skill 做出的簡報！

---

## 📄 授權

MIT License — 自由使用、修改、分享。

---

*由 [mathruffian-dot](https://github.com/mathruffian-dot) 製作*
*展示簡報：[html-vs-markdown](https://mathruffian-dot.github.io/html-vs-markdown/)*
