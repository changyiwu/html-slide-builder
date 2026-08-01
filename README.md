# 🎨 html-slide-builder — Claude Code Skill

> 給定任何主題或內容，自動生成完整的 **Reveal.js HTML 互動簡報** 並部署至 GitHub Pages。

[![Claude Code Skill](https://img.shields.io/badge/Claude%20Code-Skill-orange?logo=anthropic)](https://claude.ai/code)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## ✨ 功能

| 功能 | 說明 |
|------|------|
| 🖼 **AI 背景底圖** | 每一頁皆套用 draw skill 生成的霓虹暗色底圖；依內容分群，每 3–5 頁可共用一張 |
| 😀 **emoji 與圖標** | 預設以 emoji 強化合適的標題與卡片；只有明確要求時才生成客製圖標 |
| 💬 **即時互動元件** | Firebase Firestore 串接的文字雲（wordcloud2.js）與單選投票；文字雲需明確指定才加入 |
| 🔀 **視覺化演示** | clip-path 滑桿揭露效果；需明確指定才加入 |
| 🚀 **一鍵部署** | 自動 git init → GitHub 公開 repo → GitHub Pages |

## 📺 效果展示

- **範例簡報**：[https://mathruffian-dot.github.io/html-vs-markdown/](https://mathruffian-dot.github.io/html-vs-markdown/)
- 包含：文字雲互動、Markdown→HTML 滑桿演示、AI 生成底圖與圖標

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
| Firebase 專案 | 互動元件資料庫 | ⚠️ 互動功能需要（使用自己的專案） |

### 一鍵安裝

```bash
# 1. Clone 此 repo
git clone https://github.com/changyiwu/html-slide-builder.git
cd html-slide-builder

# 2. 執行安裝腳本（會自動檢查元件並引導設定）
python install.py
```

安裝腳本會：
- ✅ 逐項檢查必要元件，列出缺少的項目
- ✅ 詢問是否自動安裝 Pillow
- ✅ 可選擇設定自己的 Firebase 專案
- ✅ 將 Skill 複製到 `~/.claude/skills/html-slide-builder/`
- ✅ 自動偵測 draw skill 路徑並注入設定

### 手動安裝

```bash
# 複製 skill 目錄到 Claude skills 資料夾
cp -r skill/ ~/.claude/skills/html-slide-builder/
```

### 專案維護與輸出

- Skill 原始碼位於 `skill/`；安裝後才會複製到本機的 Claude skills 目錄。
- 每份生成的簡報請放在 `output/<簡報英文短名>/`，例如 `output/ai-course/`；`output/` 是本機產出，不納入版本控制。
- `.env`、Firebase 服務帳戶憑證與其他 API 金鑰均不可提交。GitHub 或 Firebase 的建立、部署與安全規則調整，請在需要時另行明確執行。

---

## 🚀 使用方式

安裝後，在 Claude Code 對話中說：

```
幫我做一份產品提案的 HTML 互動簡報

# 或

把以下活動企劃轉成 Reveal.js 互動簡報：
[貼上你的內容]

# 也支援教材、會議內容、報告或任意主題
```

Claude 會自動：
1. 分析簡報需求與內容，列出投影片大綱（每頁均有 `[BG:<背景名稱>]`；emoji 為預設）
2. **等你確認大綱後**才開始生成
3. 為每一頁套用 AI 生成底圖（依內容分群重用），並在合適位置使用 emoji；只有明確要求時才生成圖標、嵌入文字雲或視覺化滑桿
4. 部署至 GitHub Pages 並回傳網址

---

## 📁 Skill 結構

```
html-slide-builder/
├── SKILL.md                    # 主要指令（Claude 讀取）
├── scripts/
│   └── remove_bg.py            # PIL 圖標去背腳本
└── references/
    ├── reveal-template.md      # Reveal.js HTML 模板 + CSS 元件庫
    └── firebase-config.md      # Firebase 互動元件程式碼（文字雲/投票）
```

---

## ⚙️ Firebase 設定說明

互動元件使用你自己的 Firebase 專案。安裝時可選擇輸入設定值；若略過，文字雲與投票的設定占位符會保留在安裝後的 Skill 中。

### 設定自己的 Firebase 專案
1. 至 [Firebase Console](https://console.firebase.google.com/) 建立專案
2. 建立 Firestore 資料庫（測試模式）
3. 在「專案設定 → 一般」取得 `firebaseConfig`
4. 安裝時選擇設定 Firebase，並輸入各欄位

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

### 即時文字雲 [INTERACT:wordcloud]
- **非預設功能**：只有明確要求文字雲或蒐集即時文字回應時才加入。
- `wordcloud2.js` 渲染，字級隨頻率縮放，微旋轉 30%
- Firebase `onSnapshot` 即時更新，毫秒級同步

### 滑桿視覺化 [VIZ]
- **非預設功能**：只有明確要求滑桿或可拖曳的前後對比時才加入。
- CSS `clip-path: inset(0 X% 0 0)` 控制揭露
- 青色霓虹發光分隔線隨滑桿移動

---

## 📋 系統需求

| 環境 | 版本 |
|------|------|
| Claude Code | 最新版 |
| Python | 3.8+ |
| OS | Windows / macOS / Linux |

---

## 🤝 貢獻

歡迎 PR 改進 SKILL.md 的指令品質、新增互動元件、或分享你用此 Skill 做出的簡報！

---

## 📄 授權

MIT License — 自由使用、修改、分享。

---

*由 [mathruffian-dot](https://github.com/mathruffian-dot) 製作*
*展示簡報：[html-vs-markdown](https://mathruffian-dot.github.io/html-vs-markdown/)*
