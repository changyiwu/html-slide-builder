# Firebase 互動元件程式碼庫

## 共用 Firebase 設定

```js
const firebaseConfig = {
  apiKey: "{{FIREBASE_API_KEY}}",
  authDomain: "{{FIREBASE_AUTH_DOMAIN}}",
  projectId: "{{FIREBASE_PROJECT_ID}}",
  storageBucket: "{{FIREBASE_STORAGE_BUCKET}}",
  messagingSenderId: "{{FIREBASE_MESSAGING_SENDER_ID}}",
  appId: "{{FIREBASE_APP_ID}}"
};
```

請以自己的 Firebase 專案設定取代以上占位符；安裝程式也可以代為注入設定。
SDK 版本：`11.0.2`（CDN：`https://www.gstatic.com/firebasejs/11.0.2/`）

**專案需要開啟「匿名登入」**（Authentication → Sign-in method → Anonymous）。聽眾不會看到任何登入畫面，SDK 在背景取得一組臨時 uid，讓安全規則能分辨「誰寫的」。

**Firestore 路徑（子集合，不是扁平命名）：**

```
decks/<簡報slug>/wordcloud/<uid>_<詞>
decks/<簡報slug>/votes/<uid>_<題號>
```

用子集合是因為**安全規則的路徑片段只能是完整字面值或完整萬用字元**，寫不出 `match /{slug}_wordcloud/{doc}` 這種部分比對。改成子集合後，`match /decks/{slug}/wordcloud/{entry}` 一條規則就涵蓋所有簡報，日後新增簡報**不必再改規則、不必再部署**。

**文件 ID 固定為 `<uid>_<內容>`**：同一人重複送出只覆寫自己那份，天然防洗版；投票也因此變成一人一份文件，不會有多人搶寫同一份文件的熱點（單一文件持續寫入建議上限約每秒 1 次）。

## 對應的安全規則

必須先部署，否則所有寫入都會被 Firestore 預設拒絕：

```js
match /decks/{slug}/wordcloud/{entry} {
  allow read: if request.auth != null;
  allow create, update: if request.auth != null
    && slug.size() <= 40
    && request.resource.data.keys().hasOnly(['word', 'uid', 'created_at'])
    && request.resource.data.word is string
    && request.resource.data.word.size() > 0
    && request.resource.data.word.size() <= 20
    && request.resource.data.uid == request.auth.uid
    && request.resource.data.created_at == request.time
    && request.resource.data.uid + '_' + request.resource.data.word == entry;
  allow delete: if request.auth != null && resource.data.uid == request.auth.uid;
}

match /decks/{slug}/votes/{ballot} {
  allow read: if request.auth != null;
  allow create, update: if request.auth != null
    && slug.size() <= 40
    && request.resource.data.keys().hasOnly(['question', 'option', 'uid', 'updated_at'])
    && request.resource.data.question is string
    && request.resource.data.question.size() > 0
    && request.resource.data.question.size() <= 40
    && request.resource.data.option is string
    && request.resource.data.option.size() > 0
    && request.resource.data.option.size() <= 40
    && request.resource.data.uid == request.auth.uid
    && request.resource.data.updated_at == request.time
    && request.resource.data.uid + '_' + request.resource.data.question == ballot;
  allow delete: if request.auth != null && resource.data.uid == request.auth.uid;
}
```

`hasOnly()` 與長度上限是防灌爆的關鍵——沒有它，任何人都能往單份文件塞到 1 MiB 上限。**修改時務必同步調整下方程式碼的長度檢查**，兩邊要一致。

---

## ⚠️ 只能有一個 `<script type="module">`

文字雲與投票**共用同一個 `initializeApp()` 與同一次匿名登入**。把下面的「共用開頭」放最前面，再把需要的元件區塊接在後面，全部裝在**同一個** `<script type="module">` 裡（放在 `</body>` 前）。沒用到的元件整段刪掉即可。

分成兩個 module 各自 `initializeApp()` 會在設定有任何差異時炸 `app/duplicate-app`，也會多做一次匿名登入。

## 區塊 A：共用開頭（必要）

```html
<script type="module">
  import { initializeApp } from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-app.js';
  import { getAuth, signInAnonymously } from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-auth.js';
  import { getFirestore, collection, doc, setDoc, onSnapshot, serverTimestamp }
    from 'https://www.gstatic.com/firebasejs/11.0.2/firebase-firestore.js';

  // ⚠️ 每份簡報換成自己的英文短名，與資料夾名一致
  const DECK_SLUG = 'ai_course';

  const firebaseConfig = {
    apiKey: "{{FIREBASE_API_KEY}}",
    authDomain: "{{FIREBASE_AUTH_DOMAIN}}",
    projectId: "{{FIREBASE_PROJECT_ID}}",
    storageBucket: "{{FIREBASE_STORAGE_BUCKET}}",
    messagingSenderId: "{{FIREBASE_MESSAGING_SENDER_ID}}",
    appId: "{{FIREBASE_APP_ID}}"
  };

  // 本機預覽時 API key 的 referrer 限制會擋掉請求（這是刻意的安全設定，
  // 不要為了方便去 GCP Console 放寬）。改跑離線示範模式，版面照樣看得到。
  const DEMO_MODE = ['localhost', '127.0.0.1', ''].includes(location.hostname);

  let fdb = null;
  let myUid = 'demo-me';

  async function initFirebase() {
    const app = initializeApp(firebaseConfig);
    fdb = getFirestore(app);
    const cred = await signInAnonymously(getAuth(app));
    myUid = cred.user.uid;
  }

  const ready = DEMO_MODE ? Promise.resolve() : initFirebase();
</script>
```

## 區塊 B：即時文字雲

需要的 CDN（加在 `<head>` 裡）：
```html
<script src="https://cdn.jsdelivr.net/npm/wordcloud@1.2.2/src/wordcloud2.min.js"></script>
```

### Section HTML

```html
<!-- ② 互動文字雲 -->
<section id="slide-wordcloud">
  <h2 style="font-size:1.1em; margin-bottom:0.4em;"><!-- 問題標題 --></h2>
  <div style="display:grid; grid-template-columns:250px 1fr; gap:14px; height:460px;">

    <!-- 左欄：輸入 + 排行 -->
    <div style="display:flex; flex-direction:column; gap:10px;">
      <div style="background:rgba(255,255,255,0.06); border-radius:10px; padding:14px;">
        <div style="font-size:0.38em; color:var(--accent2); font-weight:700; margin-bottom:8px;">輸入你的答案</div>
        <input id="wc-input" type="text" placeholder="輸入關鍵詞…" maxlength="20"
          style="width:100%; padding:8px 12px; border-radius:8px; border:1px solid rgba(79,195,247,0.3);
                 background:rgba(255,255,255,0.08); color:#fff; font-size:13px;
                 box-sizing:border-box; font-family:inherit; outline:none;" />
        <button id="wc-btn"
          style="width:100%; margin-top:8px; padding:9px; background:var(--accent2); color:#0d1117;
                 border:none; border-radius:8px; font-weight:700; font-size:13px; cursor:pointer;">
          送出 ↵
        </button>
      </div>
      <div style="background:rgba(255,255,255,0.06); border-radius:10px; padding:14px; flex:1; overflow:hidden; display:flex; flex-direction:column;">
        <div style="font-size:0.38em; color:var(--accent2); font-weight:700; margin-bottom:8px;">
          熱門答案
          <span style="display:inline-block; background:#ff4757; color:#fff; padding:2px 7px;
                       border-radius:10px; font-size:0.85em; animation:pulse 1.5s infinite;">LIVE</span>
        </div>
        <div id="wc-list" style="font-size:0.34em; overflow-y:auto; flex:1; color:#ccc;"></div>
        <div style="margin-top:8px; font-size:0.32em; color:#666; border-top:1px solid rgba(255,255,255,0.08); padding-top:6px;">
          總提交：<span id="wc-total" style="color:var(--accent); font-weight:700;">0</span>　
          不同答案：<span id="wc-unique" style="color:var(--accent2); font-weight:700;">0</span>
        </div>
      </div>
    </div>

    <!-- 右欄：文字雲 -->
    <div style="background:rgba(255,255,255,0.04); border-radius:12px; overflow:hidden;
                position:relative; border:1px solid rgba(255,255,255,0.07);">
      <canvas id="wc-canvas" style="width:100%; height:100%; display:block;"></canvas>
      <div id="wc-empty" style="position:absolute; top:50%; left:50%; transform:translate(-50%,-50%);
                                 color:#444; font-size:0.42em; text-align:center;
                                 pointer-events:none; line-height:2;">
        輸入第一個答案<br>文字雲就會出現 ✨
      </div>
    </div>
  </div>
</section>
```

### 接在區塊 A 後面的程式碼

```js
  const WC_MAX_LEN = 20;   // 與安全規則的 word.size() <= 20 一致
  const COLORS = ['#4fc3f7','#e8643a','#ffb74d','#81c784','#ce93d8','#80deea','#f48fb1'];
  let wcCounts = {};   // { 詞: 幾個人說過 }
  let wcData = [];

  window.wcSubmit = async function () {
    const input = document.getElementById('wc-input');
    const word = input.value.trim();
    // '/' 不能出現在 Firestore 文件 ID；長度上限與安全規則對齊
    if (!word || word.length > WC_MAX_LEN || word.includes('/')) return;

    const btn = document.getElementById('wc-btn');
    btn.disabled = true;
    try {
      if (DEMO_MODE) {
        wcCounts[word] = (wcCounts[word] || 0) + 1;
        wcRender();
      } else {
        await ready;
        // 文件 ID = <uid>_<詞>：同一人重複送同一個詞只會覆寫自己那份
        await setDoc(doc(fdb, 'decks', DECK_SLUG, 'wordcloud', `${myUid}_${word}`), {
          word, uid: myUid, created_at: serverTimestamp()
        });
      }
      input.value = '';
    } catch (e) {
      console.error(e);
    } finally {
      btn.disabled = false;
    }
  };

  document.getElementById('wc-input')?.addEventListener('keypress', e => {
    if (e.key === 'Enter') window.wcSubmit();
  });
  document.getElementById('wc-btn')?.addEventListener('click', window.wcSubmit);

  function wcRender() {
    wcData = Object.entries(wcCounts).sort((a, b) => b[1] - a[1]);
    const total = Object.values(wcCounts).reduce((a, b) => a + b, 0);

    document.getElementById('wc-total').textContent = total;
    document.getElementById('wc-unique').textContent = wcData.length;

    document.getElementById('wc-list').innerHTML = wcData.slice(0, 12).map(([w, c]) =>
      `<div style="display:flex;justify-content:space-between;padding:4px 0;
                   border-bottom:1px solid rgba(255,255,255,0.06);">
        <span>${w}</span><span style="color:var(--accent);font-weight:700;">${c}</span>
      </div>`
    ).join('') || '<div style="color:#555;padding:8px 0;">尚無資料</div>';

    const empty = document.getElementById('wc-empty');
    if (empty) empty.style.display = wcData.length > 0 ? 'none' : '';
    drawWordCloud();
  }

  if (DEMO_MODE) {
    wcCounts = { '示範詞': 5, '本機預覽': 3, '推上線才是真的': 2, 'Reveal': 1 };
    wcRender();
  } else {
    ready.then(() => {
      // 不加 orderBy：serverTimestamp() 在本地快照裡短暫為 null 會讓該筆被排除
      onSnapshot(collection(fdb, 'decks', DECK_SLUG, 'wordcloud'), snap => {
        wcCounts = {};
        snap.forEach(d => {
          const w = d.data().word;
          wcCounts[w] = (wcCounts[w] || 0) + 1;   // 一個詞的權重 = 幾個人說過
        });
        wcRender();
      });
    });
  }

  function drawWordCloud() {
    const canvas = document.getElementById('wc-canvas');
    if (!canvas || typeof WordCloud === 'undefined') return;
    const rect = canvas.getBoundingClientRect();
    if (rect.width < 10 || rect.height < 10) return;
    canvas.width = rect.width;
    canvas.height = rect.height;
    if (wcData.length === 0) return;
    const maxCount = wcData[0][1];
    WordCloud(canvas, {
      list: wcData.map(([w, c]) => [w, Math.max(18, Math.round((c / maxCount) * 76))]),
      gridSize: 6,
      weightFactor: 1,
      fontFamily: '"Microsoft JhengHei", "Noto Sans TC", sans-serif',
      color: () => COLORS[Math.floor(Math.random() * COLORS.length)],
      backgroundColor: 'transparent',
      rotateRatio: 0.3,
      shuffle: true,
    });
  }

  Reveal.on('slidechanged', e => {
    if (e.currentSlide?.id === 'slide-wordcloud') setTimeout(drawWordCloud, 150);
  });
```

## 區塊 C：單選投票

### Section HTML

```html
<section id="slide-poll">
  <h2><!-- 投票問題 --></h2>
  <div id="poll-options" style="display:flex; flex-direction:column; gap:12px; margin-top:0.8em;">
    <!-- 動態生成 -->
  </div>
  <div style="font-size:0.38em; color:#666; text-align:center; margin-top:0.8em;">
    已投票：<span id="poll-total">0</span> 人
  </div>
</section>
```

### 接在區塊 A 後面的程式碼

```js
  // ⚠️ 同一份簡報有多題投票時，每題換一個 QUESTION_ID（q1 / q2 / …），
  //    並把下面的 DOM id 一併加上題號，避免兩題互相覆蓋。
  const QUESTION_ID = 'q1';

  const OPTIONS = [
    { id: 'a', label: '選項 A' },
    { id: 'b', label: '選項 B' },
    { id: 'c', label: '選項 C' },
  ];

  let myVote = null;
  let pollCounts = {};

  const container = document.getElementById('poll-options');
  OPTIONS.forEach(opt => {
    const btn = document.createElement('button');
    btn.id = `poll-btn-${opt.id}`;
    btn.innerHTML = `
      <div style="display:flex;align-items:center;gap:12px;">
        <span style="flex:0 0 24px;height:24px;border-radius:50%;border:2px solid rgba(255,255,255,0.3);
                     display:flex;align-items:center;justify-content:center;font-size:12px;"
              id="poll-check-${opt.id}"></span>
        <span style="flex:1;text-align:left;">${opt.label}</span>
        <span style="flex:0 0 120px;height:8px;background:rgba(255,255,255,0.1);border-radius:4px;overflow:hidden;">
          <div id="poll-bar-${opt.id}" style="height:100%;width:0;background:var(--accent2);border-radius:4px;transition:width 0.4s;"></div>
        </span>
        <span id="poll-pct-${opt.id}" style="flex:0 0 36px;text-align:right;font-size:0.75em;color:#888;">0%</span>
      </div>
    `;
    btn.style.cssText = `width:100%;padding:12px 16px;background:rgba(255,255,255,0.06);
      border:1px solid rgba(255,255,255,0.12);border-radius:10px;color:#fff;
      font-size:0.48em;cursor:pointer;font-family:inherit;text-align:left;`;
    btn.onclick = () => vote(opt.id);
    container.appendChild(btn);
  });

  async function vote(optId) {
    const prev = myVote;
    myVote = optId;
    if (DEMO_MODE) {
      if (prev) pollCounts[prev]--;
      pollCounts[optId] = (pollCounts[optId] || 0) + 1;
      pollRender();
      return;
    }
    await ready;
    // 一人一題一份文件：改投票是覆寫自己那份，不會多人搶寫同一份文件
    await setDoc(doc(fdb, 'decks', DECK_SLUG, 'votes', `${myUid}_${QUESTION_ID}`), {
      question: QUESTION_ID, option: optId, uid: myUid, updated_at: serverTimestamp()
    });
  }

  function pollRender() {
    const total = Object.values(pollCounts).reduce((a, b) => a + b, 0);
    document.getElementById('poll-total').textContent = total;
    OPTIONS.forEach(opt => {
      const pct = total > 0 ? Math.round(((pollCounts[opt.id] || 0) / total) * 100) : 0;
      document.getElementById(`poll-bar-${opt.id}`).style.width = pct + '%';
      document.getElementById(`poll-pct-${opt.id}`).textContent = pct + '%';
      const check = document.getElementById(`poll-check-${opt.id}`);
      if (myVote === opt.id) {
        check.textContent = '✓';
        check.style.background = 'var(--accent2)';
        check.style.borderColor = 'var(--accent2)';
      } else {
        check.textContent = '';
        check.style.background = 'transparent';
        check.style.borderColor = 'rgba(255,255,255,0.3)';
      }
    });
  }

  if (DEMO_MODE) {
    pollCounts = { a: 4, b: 7, c: 2 };
    pollRender();
  } else {
    ready.then(() => {
      onSnapshot(collection(fdb, 'decks', DECK_SLUG, 'votes'), snap => {
        pollCounts = {};
        OPTIONS.forEach(o => pollCounts[o.id] = 0);
        snap.forEach(d => {
          const v = d.data();
          if (v.question === QUESTION_ID && pollCounts[v.option] !== undefined) {
            pollCounts[v.option]++;
          }
        });
        pollRender();
      });
    });
  }
```
