---
name: html-slide-builder
description: |
  給定任何簡報需求或內容（主題、文字、提案、會議內容、活動資訊、報告、PDF、教材或口述需求），自動生成完整的 Reveal.js HTML 互動簡報並部署至 GitHub Pages。

  提供五種視覺/互動強化：
  1. AI 生成背景底圖（draw 技能，data-background-image）
  2. 扁平化圖標（僅在使用者明確要求時，以 draw 技能 + PIL 裁切去背生成）
  3. CSS 微互動（卡片滑過發光／浮起、流程節點滑過輕微抖動）
  4. Firebase 即時互動元件（文字雲、單選投票，Firestore 串接）
  5. 滑桿視覺化演示（clip-path 揭露，適合前後對比內容）

  預設為每一頁簡報套用 AI 生成底圖，並依內容分群重用底圖；在標題、段落標籤、重點卡與流程節點等合適位置使用 emoji；為卡片與流程節點加入節制的 CSS 微互動。預設不得加入點擊按鈕、點擊後動畫、或左下角的互動操作提示。只有使用者明確要求圖標、生圖圖示、可點擊效果、文字雲或視覺化滑桿時，才可加入對應功能。

  當使用者說「幫我做 HTML 簡報」「把這份內容轉成互動簡報」「做 Reveal.js 簡報」「做成投影片」「做一份提案／活動／課程簡報」，或提供任何內容並要求轉成簡報格式時，務必使用此 Skill。即使使用者未明確說「互動」或「HTML」，只要目的是產出可展示的簡報，也應觸發此 Skill。
---

# HTML 智慧簡報生成器

簡報需求／內容 → 分析 → 確認大綱 → 生成 Reveal.js 簡報 → 強化（底圖/圖標/互動/視覺化）→ GitHub Pages 部署

---

## 0. 讀取簡報需求或內容

接受任何形式的輸入：

- **文字 / Markdown**：直接分析，可為教材、提案、會議筆記、活動文案或報告內容
- **PDF**：用讀檔工具讀取（若有多頁先讀摘要頁）
- **口述主題**：依主題、受眾與使用情境設計通用的溝通結構

若資訊不足，不要詢問，直接以通用簡報脈絡補充（開場→背景／問題→核心訊息→下一步→結論）。只有在內容明確是教材時，才改用教學脈絡（引言→概念→範例→練習／互動→結論）。

---

## 1. 分析大綱，等使用者確認

分析完畢後輸出大綱表格，**等使用者確認後才繼續**：

```
## 📋 簡報大綱草稿（共 N 頁）

| 頁碼 | 標題 | 內容摘要 | 功能標記 |
|------|------|----------|----------|
| 1    | 封面 | 簡報標題、提案人或活動資訊 | [BG:bg-cover] |
| 2    | 背景與目的 | 說明此簡報要解決的問題或帶來的價值 | [BG:bg-context] |
| 3    | 三大重點 | 以 ✨、🧭、📈 區分三個核心概念 | [BG:bg-context] |
| 4    | 前後對比 | A 方案與 B 方案的差異 | [BG:bg-comparison] |
...

**功能標記說明**
- [BG:<背景名稱>] 背景底圖（draw 技能，暗色風格；每頁必填，可重用）
- emoji：預設用於合適的標題、標籤、卡片與流程節點
- [HOVER] CSS 微互動：卡片滑過發光／浮起、流程節點滑過輕微抖動（預設啟用）
- [ICON] 扁平化圖標（僅在使用者明確要求生圖圖標時）
- [INTERACT:wordcloud] Firebase 即時文字雲（僅在使用者明確要求時）
- [INTERACT:poll] Firebase 單選投票
- [VIZ] 滑桿視覺化演示（clip-path；僅在使用者明確要求時）

請確認大綱，或說明要調整的地方。
```

### 功能標記的決策原則

**預設規則：** 每一頁都必須帶有 `[BG:<背景名稱>]`，而且必須在輸出的 HTML 套用對應的 AI 生成底圖；相鄰或同一章節的投影片可以共用同一張底圖。預設以語意相符的 emoji 強化關鍵標籤與卡片，但不在每個句子或項目符號都堆疊 emoji；適合的卡片與流程節點套用 `[HOVER]` 微互動。不得因簡報題材自行加入 `[ICON]`、點擊按鈕／點擊動畫、`[INTERACT:wordcloud]` 或 `[VIZ]`，也不得在左下角加入「滑過」「點按」等操作提示。只有使用者明確提出生圖圖標、可點擊效果、文字雲、蒐集即時文字回應、滑桿，或要求可拖曳的前後對比時，才能標記並生成；確認大綱時也要清楚列出這項使用者要求。

| 標記 | 觸發條件 | 每份簡報目標數量 |
|------|----------|-----------------|
| [BG:<背景名稱>] | 每一頁；依章節、敘事轉折與視覺調性分群 | 每頁 1 個標記；通常每 3–5 頁共用 1 張底圖 |
| [HOVER] | 重點卡、引用框、比較卡、行動卡與流程節點 | 預設啟用；每頁 1–4 個合適元素 |
| [ICON] | 使用者明確要求生圖圖標、圖示組或不用 emoji 的客製圖示 | 預設 0 頁；有要求時 1–3 頁 |
| [INTERACT:wordcloud] | 使用者明確要求文字雲或蒐集即時文字回應 | 預設 0 頁；有要求時 1 頁 |
| [INTERACT:poll] | 概念確認、意見調查、前測/後測 | 0–1 頁 |
| [VIZ] | 使用者明確要求滑桿或可拖曳的對比演示 | 預設 0 頁；有要求時 0–1 頁 |

---

## 2. 建立專案目錄與基礎 HTML

使用者確認後：

1. 建立專案目錄：`<當前工作目錄>/<簡報英文短名>/`
2. 建立 `images/` 子目錄
3. 生成 `index.html`（完整 Reveal.js 骨架）

讀取 `references/reveal-template.md` 獲得：完整 CSS 變數、元件樣式、Reveal.js 初始化程式碼。

**命名規則：**
- 專案目錄：kebab-case 英文（`ai-course`、`math-lesson`）
- Firestore 路徑：`decks/<slug>/wordcloud`、`decks/<slug>/votes`（子集合，避免不同簡報資料混用）

**調色盤（所有簡報統一使用）：**
```
--accent:  #e8643a   橘紅（主強調）
--accent2: #4fc3f7   青（次強調）
--success: #81c784   綠（正面）
--warn:    #ffb74d   琥珀（提示）
背景：     #0d1117 ~ #1a1a2e（深暗色）
```

---

## 3. 生成背景底圖 [BG]（每頁必填）

### 背景策略設定（預設啟用）

- **套用範圍**：每一頁投影片都必須使用 AI 生成底圖；不能留下純色、未設定 `data-background-image` 的投影片。
- **重用策略**：以敘事章節與視覺調性分群，通常每 3–5 頁共用一張。封面、章節轉換或結尾只有在視覺目的不同時才另生成。
- **生成數量**：預設為 `ceil(投影片總數 / 4)` 張，最少 1 張、最多 6 張；可依實際章節數微調。先列出「背景名稱 → 套用頁碼 → prompt」對照表，再生成。
- **套用方式**：同一個背景群組內的每個 `<section>` 都要寫入相同的 `data-background-image` 路徑。

<a id="resolve-draw"></a>

#### 先解析本機的生圖技能（每次工作階段做一次，結果沿用）

各家 Agent 的生圖技能安裝名不同（`claude-draw`／`codex-draw`／`opencode-draw`／`antigravity-draw`），所以**不要寫死路徑**，執行時現找：本技能所在資料夾的**上一層**就是這個 Agent 的全域技能目錄，在裡面找名稱含 `draw` 的資料夾。

```powershell
# $skillRoot = 本技能（html-slide-builder）的資料夾路徑
$skillsDir = Split-Path $skillRoot -Parent
$drawDir   = Get-ChildItem $skillsDir -Directory -EA SilentlyContinue |
             Where-Object { $_.Name -match 'draw' } | Select-Object -First 1
$drawName  = if ($drawDir) { $drawDir.Name }
$py        = if ($drawDir) { @(Get-ChildItem $drawDir.FullName -Recurse -Filter '*.py' -File) }
$drawScript = @(
  $py | Where-Object { $_.Name -eq 'draw.py' }        # 優先 draw.py
  $py | Where-Object { $_.Name -match 'draw' }        # 其次檔名含 draw
  $py                                                  # 最後任意 .py
) | Select-Object -First 1
"生圖技能：$drawName　腳本：$($drawScript.FullName)"
```

```bash
# POSIX 等價寫法
skills_dir="$(dirname "$skill_root")"
draw_dir="$(find "$skills_dir" -maxdepth 1 -type d -name '*draw*' | head -1)"
draw_script="$(find "$draw_dir" -name 'draw.py' -o -name '*draw*.py' -o -name '*.py' 2>/dev/null | head -1)"
```

三種結果，分別怎麼走：

| 解析結果 | 怎麼做 |
|---------|--------|
| 找到資料夾 ＋ 找到腳本 | 用下面的 CLI 指令，`<生圖腳本路徑>` 填 `$drawScript` |
| 找到資料夾、**沒有腳本** | 該 Agent 的生圖是內建的（例如 Codex 的 Image Gen）。**不要跑 CLI**，改為載入 `$drawName` 技能、以自然語言要求同樣規格 |
| **找不到任何 draw 資料夾** | 停下來告訴使用者：這個 Agent 還沒安裝生圖技能，底圖與圖標功能無法使用 |

先依背景群組呼叫 draw 技能；不同群組可平行執行：

```bash
python "<生圖腳本路徑>" \
  "<底圖 prompt>" \
  --size 1536x1024 --quality low \
  --name <background-slug> \
  --outdir "<專案目錄>/images"
```

> 走自然語言那條路時，規格是：1536×1024 橫式、深暗霓虹配色、無文字；生成後把圖片複製到 `<專案目錄>/images/<background-slug>.png` 再往下走。

**底圖 Prompt 設計原則：**
- 深暗色系（deep navy、dark space、#0d1117 背景）
- 無文字
- 與投影片主題有關但抽象（概念視覺化，非字面圖示）
- 霓虹/發光效果，配合主題色
- 例：AI 課程封面 → `"deep navy background, glowing neural network nodes and light trails, cinematic wide, no text, abstract tech art"`

每一個 HTML section 都要加上：
```html
<section data-background-image="images/<background-slug>.png"
         data-background-opacity="0.15"
         data-background-size="cover">
```

透明度建議：封面與結尾 0.3–0.4；一般頁 0.12–0.18。即使同一張底圖被重用，每頁仍須依內容調整透明度以維持文字可讀性。

---

## 4. emoji 與圖標系統 [ICON]

### 4-1 預設：使用 emoji

在不影響專業語氣與可讀性的前提下，於下列位置使用 1 個語意相符的 emoji：

- 投影片標題旁的主題提示（例如 `📊 關鍵數字`）
- 重點卡、流程節點與段落標籤
- 正向／警示／行動呼籲的短標籤（例如 `✅`、`⚠️`、`🚀`）

不要把 emoji 用於每個句子、長段落或純裝飾；使用者要求無 emoji、極簡風格，或明確要求生圖圖標時，優先服從使用者。

### 4-2 僅在明確要求時：生成圖標總表

只有使用者明確要求圖標、生圖圖示、圖示組，或指定不用 emoji 時，才執行下列生成與去背流程。

`<生圖腳本路徑>` 同樣來自[前面的生圖技能解析](#resolve-draw)：

```bash
python "<生圖腳本路徑>" \
  "A clean icon sheet with exactly N flat neon icons in a single horizontal row on pure dark navy (#0d1117) background. [逐一描述每個圖標，從左到右]. Each icon large, bold, centered in equal column, no text." \
  --size 1536x1024 --quality low \
  --name icon_sheet \
  --outdir "<專案目錄>/images"
```

先用讀檔／看圖工具確認圖標總表品質，再裁切。（沒有 CLI 腳本的 Agent 同上，改用解析到的生圖技能以自然語言生成圖標總表。）

### 4-3 裁切 + 去背

執行（複製 `scripts/remove_bg.py` 到專案目錄，或用內聯 Python）：

```python
from PIL import Image
from pathlib import Path

img = Image.open("images/icon_sheet.png").convert("RGBA")
w, h = img.size
n = <圖標數量>
icons = ["icon_a", "icon_b", ...]  # 對應名稱

for i, name in enumerate(icons):
    x0 = i * (w // n)
    x1 = (i + 1) * (w // n) if i < n-1 else w
    col_w = x1 - x0
    sq = min(col_w, h)
    cx, cy = x0 + col_w // 2, h // 2
    crop = img.crop((cx-sq//2, cy-sq//2, cx+sq//2, cy+sq//2))
    crop = crop.resize((256, 256), Image.LANCZOS)
    crop.save(f"images/{name}.png")
```

然後執行去背（`scripts/remove_bg.py`）。

### 4-4 嵌入 HTML

- 在使用者明確要求的圖標頁，以 `<img src="images/icon_name.png">` 取代該位置的 emoji
- adv-card 統一用 `border-top: 4px solid var(--accent2)` + `text-align: center`
- 圖標 img 加 `filter: drop-shadow(0 0 10px rgba(79,195,247,0.6))`

---

## 5. CSS 微互動 [HOVER]（預設啟用）

在不改變簡報敘事、也不增加操作負擔的前提下，對適合的 HTML 元件加上滑過效果：

- **適用元素**：重點卡、比較卡、引用框、行動卡，以及流程節點。
- **卡片效果**：滑過時微幅上移、邊框變亮並產生青色光暈。
- **流程節點效果**：滑過時輕微左右抖動，搭配短暫光暈；不得持續自動晃動。
- **不要套用**：整張投影片、密集表格、正文段落、頁尾或純裝飾元素。
- **無障礙**：提供 `prefers-reduced-motion` 降低動態效果；觸控裝置沒有 hover 時，內容仍須完全可讀。
- **禁止預設**：不加 `<button>`、`onclick`、`addEventListener('click', ...)`、點擊後脈衝動畫，或左下角的「滑過／點按」操作說明。這些只在使用者明確要求可點擊互動時才可加入。

建議 CSS：

```css
.interactive {
  transition: transform .24s ease, box-shadow .24s ease,
              border-color .24s ease, background .24s ease;
}
@media (hover: hover) {
  .interactive:hover {
    transform: translateY(-7px);
    border-color: rgba(79,195,247,.92);
    box-shadow: 0 0 0 1px rgba(79,195,247,.2),
                0 0 29px rgba(79,195,247,.34),
                0 18px 34px rgba(0,0,0,.32);
  }
  .flow .step:hover { animation: shake .38s ease-in-out; }
}
@keyframes shake {
  0%,100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; }
}
```

---

## 6. 互動元件 [INTERACT]

文字雲屬於明確選用功能；沒有使用者要求時，不讀取、不嵌入文字雲程式碼，也不建立對應 Firestore 集合。啟用互動元件時，只能使用使用者自己的 Firebase 設定。

詳見 `references/firebase-config.md`，含完整的文字雲和投票 HTML 程式碼片段。

**通用原則：**
- 互動 section 加 `id="slide-<slug>"`
- 使用 `Reveal.on('slidechanged', e => { if (e.currentSlide?.id === '...') { /* 重繪 */ }})` 確保切頁後正確渲染
- Firestore 路徑：`decks/<簡報slug>/wordcloud` / `decks/<簡報slug>/votes`（子集合，每份簡報獨立）
- **文字雲與投票共用同一個 `<script type="module">`**：只能 `initializeApp()` 一次，兩個元件都放時務必合併（詳見 `firebase-config.md` 的區塊 A/B/C）
- 需要匿名登入與對應的 Firestore 安全規則，兩者都在 `firebase-config.md` 有說明
- 樣式：配合暗色主題，輸入框 `background: rgba(255,255,255,0.08)`

---

## 7. 視覺化演示 [VIZ]

滑桿屬於明確選用功能；沒有使用者要求時，不生成滑桿 HTML、CSS 或 JavaScript。

clip-path 滑桿揭露效果，適合「格式轉換」「前後對比」「A→B 演進」。

**核心 CSS/JS 邏輯：**
```html
<div style="position:relative; height:390px; border-radius:12px; overflow:hidden;">
  <div id="viz-before" style="position:absolute;inset:0;..."></div>
  <div id="viz-after" style="position:absolute;inset:0;clip-path:inset(0 100% 0 0);"></div>
  <div id="viz-divider" style="position:absolute;top:0;left:0;width:3px;height:100%;
    background:linear-gradient(to bottom,transparent,#4fc3f7,transparent);
    box-shadow:0 0 12px #4fc3f7;pointer-events:none;"></div>
</div>
<input id="viz-slider" type="range" min="0" max="100" value="0">
<script>
document.getElementById('viz-slider').addEventListener('input', function() {
  const v = +this.value;
  document.getElementById('viz-after').style.clipPath = `inset(0 ${100-v}% 0 0)`;
  document.getElementById('viz-divider').style.left = v + '%';
});
</script>
```

左右各加標籤（`position:absolute; top:8px`），接近邊界時用 JS 淡出。

---

## 8. 部署到 GitHub Pages

```bash
cd "<專案目錄>"
git init
git config user.email "<你的 GitHub email>"
git config user.name "<你的 GitHub 帳號>"
git add .
git commit -m "初始化：<簡報名稱>"
gh repo create <帳號>/<repo-name> --public --source=. --push \
  --description "<簡報一句話描述>"
# 用實際分支名開 Pages（新版 git 預設 main、舊版 master），避免寫死失敗
BRANCH=$(git rev-parse --abbrev-ref HEAD)
gh api repos/<帳號>/<repo-name>/pages \
  --method POST -f "source[branch]=$BRANCH" -f "source[path]=/"
```

回傳給使用者：
```
✅ 簡報已部署！
🔗 GitHub Pages：https://<帳號>.github.io/<repo-name>/
（首次約 1–3 分鐘生效）
📦 原始碼：https://github.com/<帳號>/<repo-name>
```

---

## 執行順序與平行化建議

```
Phase 0: 讀取簡報需求或內容
Phase 1: 輸出大綱 → 等待確認 ← 必須停在這裡
Phase 2: 生成 HTML 骨架
Phase 3+4: 可平行（底圖生成 + 僅在要求圖標時才生成圖標）
Phase 5: 為合適卡片與流程節點加入預設 CSS 微互動
Phase 6: 僅在明確要求時，嵌入 Firebase 互動元件
Phase 7: 僅在明確要求時，寫入 VIZ 滑桿
Phase 8: 確認一切完成後才 push
```

---

## 參考資源

| 檔案 | 用途 |
|------|------|
| `references/reveal-template.md` | Reveal.js HTML 完整模板、CSS 元件庫 |
| `references/firebase-config.md` | 文字雲、投票完整程式碼片段 |
| `scripts/remove_bg.py` | PIL 圖標去背腳本（對 images/icon_*.png 執行） |
