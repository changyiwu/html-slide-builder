#!/usr/bin/env python3
"""
html-slide-builder Skill 安裝腳本（跨 Agent 通用）
支援 Claude Code / Codex / OpenCode / Antigravity
用法：python install.py
"""
import os
import sys
import shutil
import platform
import subprocess
from pathlib import Path

# ANSI 顏色
G = "\033[92m"   # 綠
Y = "\033[93m"   # 黃
R = "\033[91m"   # 紅
C = "\033[96m"   # 青
B = "\033[1m"    # 粗體
X = "\033[0m"    # 重置


def ok(msg):   print(f"  {G}✔{X}  {msg}")
def warn(msg): print(f"  {Y}⚠{X}  {msg}")
def err(msg):  print(f"  {R}✘{X}  {msg}")
def info(msg): print(f"  {C}→{X}  {msg}")
def head(msg): print(f"\n{B}{msg}{X}")


SKILL_NAME = "html-slide-builder"

# 安裝名一律用 SKILL_NAME（不加 agent 前綴）——這個 Skill 四家通用。
# root   = 該工具的設定根目錄，用來判斷「這台有沒有裝這個工具」
# skills = 該工具的全域技能目錄
AGENTS = [
    ("Claude Code", Path.home() / ".claude",              Path.home() / ".claude" / "skills"),
    ("Codex",       Path.home() / ".agents",              Path.home() / ".agents" / "skills"),
    ("OpenCode",    Path.home() / ".config" / "opencode", Path.home() / ".config" / "opencode" / "skills"),
    ("Antigravity", Path.home() / ".gemini" / "config",   Path.home() / ".gemini" / "config" / "skills"),
]

# 該 Agent 的生圖技能沒有 CLI 腳本時（例如 Codex 用內建 Image Gen），填進 SKILL.md 的字樣
NO_DRAW_SCRIPT = "（此 Agent 的生圖技能沒有 CLI 腳本，請改用下方的自然語言方式）"

# 複製時要排除的本機垃圾（`skill/scripts/__pycache__` 跑過 remove_bg.py 就會生出來）
IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store", "desktop.ini", "Thumbs.db")


def force_rmtree(path: Path):
    """刪除舊副本；遇到唯讀檔就清掉唯讀屬性再刪一次（Windows 常見）。"""
    import stat

    def onexc(func, p, exc):
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            raise exc

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=onexc)
    else:
        shutil.rmtree(path, onerror=lambda f, p, e: onexc(f, p, e[1]))


# ──────────────────────────────────────────────
# 1. 偵測本機裝了哪些 Agent
# ──────────────────────────────────────────────

def detect_agents() -> list:
    """回傳本機偵測得到的 Agent；設定根目錄不存在＝這台沒裝，直接略過。"""
    found = []
    for tool, root, skills in AGENTS:
        if root.exists():
            found.append({"tool": tool, "root": root, "skills": skills})
    return found


# ──────────────────────────────────────────────
# 2. 找該 Agent 自己的 draw（生圖）技能
# ──────────────────────────────────────────────

def find_draw_skill(skills_dir: Path):
    """在指定 Agent 的技能目錄裡找生圖技能。

    各家安裝名不同（claude-draw / codex-draw / opencode-draw / antigravity-draw），
    所以用「名稱含 draw」比對，再從裡面找生圖腳本。
    回傳 (技能名, 腳本路徑)；技能存在但沒有腳本時腳本為 None。
    """
    if not skills_dir.exists():
        return None, None

    for d in sorted(skills_dir.iterdir()):
        if not d.is_dir() or "draw" not in d.name.lower():
            continue
        py_files = sorted(d.rglob("*.py"))
        # 優先 draw.py，其次檔名含 draw 的腳本，最後才是任意 .py
        for pick in (
            [p for p in py_files if p.name == "draw.py"],
            [p for p in py_files if "draw" in p.name.lower()],
            py_files,
        ):
            if pick:
                return d.name, pick[0]
        return d.name, None
    return None, None


# ──────────────────────────────────────────────
# 3. 檢查必要元件
# ──────────────────────────────────────────────

def check_requirements(agents: list) -> dict:
    head("【1】 檢查必要元件")
    results = {}

    # Python 版本
    vi = sys.version_info
    if vi >= (3, 8):
        ok(f"Python {vi.major}.{vi.minor}.{vi.micro}")
        results["python"] = True
    else:
        err(f"Python 版本過舊（{vi.major}.{vi.minor}），需要 3.8+")
        results["python"] = False

    # Pillow
    try:
        from PIL import Image
        import PIL
        ok(f"Pillow {PIL.__version__}（圖標去背）")
        results["pillow"] = True
    except ImportError:
        warn("Pillow 未安裝（圖標去背功能需要）")
        results["pillow"] = False

    # 各 Agent 的生圖技能（逐一偵測，安裝時各自注入各自的路徑）
    for a in agents:
        name, path = find_draw_skill(a["skills"])
        a["draw_name"], a["draw_path"] = name, path
        if path:
            ok(f"{a['tool']} 生圖技能：{name}（{path.name}）")
        elif name:
            warn(f"{a['tool']} 生圖技能：{name}（無 CLI 腳本，將改用自然語言生圖）")
        else:
            warn(f"{a['tool']} 找不到生圖技能（底圖 / 圖標生成需要）")
    results["draw"] = any(a.get("draw_name") for a in agents)

    # OpenAI API Key（生圖技能用）
    openai_key = os.environ.get("OPENAI_API_KEY")
    if not openai_key:
        env_files = [
            Path.home() / ".openai.env",
            Path.cwd() / ".env",
        ]
        for ef in env_files:
            if ef.exists():
                content = ef.read_text(encoding="utf-8", errors="ignore")
                if "OPENAI_API_KEY" in content:
                    openai_key = "found_in_file"
                    break
    if openai_key:
        ok("OpenAI API Key 已設定（gpt-image-2 生圖）")
        results["openai"] = True
    else:
        warn("找不到 OPENAI_API_KEY")
        info("請設定環境變數，或在 ~/.openai.env 中加入 OPENAI_API_KEY=sk-...")
        results["openai"] = False

    # GitHub CLI
    gh = shutil.which("gh")
    if gh:
        ok(f"GitHub CLI (gh)：{gh}")
        results["gh"] = True
    else:
        warn("GitHub CLI (gh) 未安裝（自動部署到 GitHub Pages 需要）")
        info("安裝：https://cli.github.com/")
        results["gh"] = False

    # git
    git = shutil.which("git")
    if git:
        ok(f"git：{git}")
        results["git"] = True
    else:
        err("git 未安裝（版本控制必要）")
        results["git"] = False

    return results


# ──────────────────────────────────────────────
# 4. Firebase 設定
# ──────────────────────────────────────────────

def configure_firebase():
    head("【2】 Firebase 設定（互動元件：文字雲、投票）")
    print(f"""
  此 Skill 的互動元件需要 Firebase Firestore 資料庫。
  文字雲與投票均為選用功能；如需使用，請提供自己的 Firebase 專案設定。
  未設定時仍可安裝 Skill，只是不會啟用 Firebase 互動元件。
""")
    configure = input("  是否現在設定自己的 Firebase？[y/N]：").strip().lower()
    if configure != "y":
        info("略過 Firebase 設定；互動元件將保留設定占位符")
        return None

    print(f"\n  請至 Firebase Console → 專案設定 → 應用程式，複製 firebaseConfig 各欄位：\n")
    config = {}
    config["apiKey"]            = input("  apiKey：").strip()
    config["authDomain"]        = input("  authDomain：").strip()
    config["projectId"]         = input("  projectId：").strip()
    config["storageBucket"]     = input("  storageBucket：").strip()
    config["messagingSenderId"] = input("  messagingSenderId：").strip()
    config["appId"]             = input("  appId：").strip()
    if not all(config.values()):
        warn("Firebase 設定不完整；互動元件將保留設定占位符")
        return None
    ok("已儲存自訂 Firebase 設定")
    return config


def inject_firebase_config(firebase_config_path: Path, fb: dict):
    """將 Firebase 設定注入 firebase-config.md"""
    content = firebase_config_path.read_text(encoding="utf-8")
    replacements = {
        "{{FIREBASE_API_KEY}}":              fb["apiKey"],
        "{{FIREBASE_AUTH_DOMAIN}}":          fb["authDomain"],
        "{{FIREBASE_PROJECT_ID}}":           fb["projectId"],
        "{{FIREBASE_STORAGE_BUCKET}}":       fb["storageBucket"],
        "{{FIREBASE_MESSAGING_SENDER_ID}}":  fb["messagingSenderId"],
        "{{FIREBASE_APP_ID}}":               fb["appId"],
    }
    for old, new in replacements.items():
        content = content.replace(old, new)
    firebase_config_path.write_text(content, encoding="utf-8")


# ──────────────────────────────────────────────
# 5. 注入該 Agent 的生圖技能名稱與腳本路徑到 SKILL.md
# ──────────────────────────────────────────────

def inject_draw_info(skill_md_path: Path, draw_name, draw_path):
    content = skill_md_path.read_text(encoding="utf-8")
    content = content.replace("{{DRAW_SKILL_NAME}}", draw_name or "draw")
    content = content.replace(
        "{{DRAW_SKILL_PATH}}",
        str(draw_path) if draw_path else NO_DRAW_SCRIPT,
    )
    skill_md_path.write_text(content, encoding="utf-8")


# ──────────────────────────────────────────────
# 6. 選擇要安裝到哪些 Agent
# ──────────────────────────────────────────────

def choose_targets(agents: list) -> list:
    head("【3】 選擇安裝目標")
    print()
    for i, a in enumerate(agents, 1):
        state = "已安裝過" if (a["skills"] / SKILL_NAME).exists() else "尚未安裝"
        print(f"    {i}. {a['tool']:<14} {a['skills']}  [{state}]")
    print()
    raw = input("  要安裝到哪幾個？[Enter=全部，或輸入編號如 1,3]：").strip()
    if not raw:
        return agents

    picked = []
    for token in raw.replace("，", ",").split(","):
        token = token.strip()
        if not token.isdigit():
            continue
        idx = int(token)
        if 1 <= idx <= len(agents) and agents[idx - 1] not in picked:
            picked.append(agents[idx - 1])
    if not picked:
        warn("沒有辨識到有效編號，改為安裝全部")
        return agents
    return picked


# ──────────────────────────────────────────────
# 7. 安裝
# ──────────────────────────────────────────────

def install_one(agent: dict, fb, overwrite_all):
    """安裝到單一 Agent。回傳 (是否成功, 更新後的 overwrite_all)。"""
    src = Path(__file__).parent / "skill"
    dst = agent["skills"] / SKILL_NAME

    if dst.exists():
        if overwrite_all is None:
            print(f"\n  目標目錄已存在：{dst}")
            ans = input("  覆蓋安裝？[y=這個 / a=全部覆蓋 / N=略過]：").strip().lower()
            if ans == "a":
                overwrite_all = True
            elif ans != "y":
                warn(f"{agent['tool']}：略過")
                return False, overwrite_all
        elif not overwrite_all:
            warn(f"{agent['tool']}：略過")
            return False, overwrite_all
        try:
            force_rmtree(dst)
        except Exception as e:
            # 單一 Agent 刪不掉不該讓其他 Agent 一起陣亡（常見原因：該檔正被編輯器或 Agent 開著）
            err(f"{agent['tool']}：舊副本刪不掉，略過 —— {e}")
            return False, overwrite_all

    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst, ignore=IGNORE)
    except Exception as e:
        err(f"{agent['tool']}：複製失敗，略過 —— {e}")
        return False, overwrite_all

    # 注入 Firebase 設定
    fb_cfg = dst / "references" / "firebase-config.md"
    if fb and fb_cfg.exists():
        inject_firebase_config(fb_cfg, fb)

    # 注入該 Agent 自己的生圖技能資訊
    inject_draw_info(dst / "SKILL.md", agent.get("draw_name"), agent.get("draw_path"))

    detail = agent.get("draw_name") or "無生圖技能"
    if agent.get("draw_name") and not agent.get("draw_path"):
        detail += "（自然語言生圖）"
    ok(f"{agent['tool']:<14} → {dst}　[生圖：{detail}]")
    return True, overwrite_all


def install_skill(targets: list, fb) -> list:
    head("【4】 安裝 Skill")
    installed = []
    overwrite_all = None
    for a in targets:
        success, overwrite_all = install_one(a, fb, overwrite_all)
        if success:
            installed.append(a)
    if installed:
        if fb:
            info("Firebase 設定已注入所有安裝副本")
        else:
            info("未設定 Firebase；互動元件設定占位符已保留")
    return installed


# ──────────────────────────────────────────────
# 主程式
# ──────────────────────────────────────────────

def main():
    print(f"""
{B}{C}╔════════════════════════════════════════════════════╗
║   html-slide-builder Skill 安裝程式                ║
║   內容 → AI 互動 HTML 簡報 + GitHub Pages         ║
║   Claude Code / Codex / OpenCode / Antigravity     ║
╚════════════════════════════════════════════════════╝{X}
""")

    # 0. 偵測 Agent
    agents = detect_agents()
    if not agents:
        err("找不到任何支援的 Agent 設定目錄：")
        for tool, root, _ in AGENTS:
            info(f"{tool}：{root}")
        info("請先安裝其中至少一個工具再執行本腳本。")
        sys.exit(1)

    # 1. 檢查元件
    results = check_requirements(agents)

    # 2. 必要元件驗證
    if not results.get("python"):
        err("Python 版本不符，無法安裝。")
        sys.exit(1)
    if not results.get("git"):
        err("git 未安裝，無法繼續。請先安裝 git。")
        sys.exit(1)

    # 缺少 Pillow → 詢問自動安裝
    if not results.get("pillow"):
        install_pillow = input("\n  是否自動安裝 Pillow？[Y/n]：").strip().lower()
        if install_pillow != "n":
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
                ok("Pillow 安裝完成")
            except Exception as e:
                warn(f"Pillow 安裝失敗：{e}（圖標去背功能將無法使用）")

    # 3. Firebase 設定
    fb = configure_firebase()

    # 4. 選擇目標並安裝
    targets = choose_targets(agents)
    installed = install_skill(targets, fb)

    # 5. 結果報告
    head("【5】 安裝完成報告")
    if not installed:
        warn("安裝未完成（沒有任何目標被安裝）。")
        return

    print(f"""
  {G}{B}✔ html-slide-builder Skill 已安裝到 {len(installed)} 個 Agent！{X}

  {B}使用方式：{X}
    在任一已安裝的 Agent 對話中說：
    「幫我把這份內容做成 HTML 互動簡報」
    「把這個大綱轉成 Reveal.js 簡報」

  {B}安裝位置：{X}""")
    for a in installed:
        print(f"    {a['tool']:<14} {a['skills'] / SKILL_NAME}")

    print(f"\n  {B}元件狀態：{X}")
    components = [
        ("圖標去背（Pillow）",          results.get("pillow", False)),
        ("AI 生圖（OpenAI API Key）",  results.get("openai", False)),
        ("GitHub Pages 部署（gh CLI）", results.get("gh", False)),
    ]
    for name, status in components:
        symbol = f"{G}✔{X}" if status else f"{Y}⚠ 需手動設定{X}"
        print(f"    {symbol}  {name}")

    no_draw = [a["tool"] for a in installed if not a.get("draw_name")]
    if no_draw:
        print(f"""
  {Y}提示：下列 Agent 找不到生圖技能 —— {"、".join(no_draw)}{X}
    請先在該 Agent 安裝生圖（draw）技能，安裝後重新執行本腳本以更新路徑設定。
""")


if __name__ == "__main__":
    main()
