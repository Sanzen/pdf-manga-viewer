# PDF Manga Viewer

PyQt6 と PyMuPDF で作ったシンプルな PDF 漫画ビューアです。  
A simple PDF manga viewer built with PyQt6 and PyMuPDF.

---

## 日本語

### 既存アプリとの違い

| | PDF Manga Viewer | Adobe / Foxit | SumatraPDF | ブラウザ内蔵 |
|--|:--:|:--:|:--:|:--:|
| 漫画向けシンプル UI | ✅ | ❌ 機能過多 | △ | ❌ |
| 画像 PDF を自動判定して起動振り分け | ✅ | ❌ | ❌ | ❌ |
| バックグラウンド先読みキャッシュ | ✅ | ✅ | ✅ | ❌ |
| HiDPI / 4K レンダリング | ✅ | ✅ | △ | △ |
| ホイールでページめくり | ✅ | ❌ スクロール | ✅ | ❌ |
| インストール不要（pip のみ） | ✅ | ❌ | ❌ | ➖ 標準搭載 |
| 広告・サブスク不要 | ✅ | △ 無料版は広告あり | ✅ | ✅ |

**ポイント：自動振り分け機能**

起動時に PDF の内容を解析し（先頭 3 ページの平均文字数で判定）、スキャン漫画なら本アプリで表示、テキスト中心の PDF なら PC にインストール済みの外部リーダーへ自動転送します。ファイルの関連付けをこのアプリ 1 本にまとめられるのが最大の差異点です。

### 機能

- PDF ファイルを開く（メニュー・`Ctrl+O`・ドラッグ＆ドロップ）
- キーボード・マウスホイールでページめくり
- ズームイン／アウト（`Ctrl+=` / `Ctrl+-` / `Ctrl+スクロール`）
- バックグラウンドでページを先読みし、プログレスバーで進捗表示
- 画像が含まれないテキスト PDF は Foxit / Adobe / SumatraPDF / Edge 等の外部リーダーへ自動転送
- HiDPI・4K ディスプレイ対応

### 動作環境

- Windows 10 / 11
- Python 3.11 以上

### インストール

```bash
pip install -r requirements.txt
```

### 使い方

```bash
# ビューアを起動
python main.py

# PDF を指定して起動
python main.py path/to/manga.pdf
```

### キー操作

| 操作 | キー |
|------|------|
| 次のページ | `→` `Space` `PageDown` `↓` |
| 前のページ | `←` `Backspace` `PageUp` `↑` |
| 最初のページ | `Home` |
| 最後のページ | `End` |
| ズームイン | `Ctrl+=` または `Ctrl+スクロールアップ` |
| ズームアウト | `Ctrl+-` または `Ctrl+スクロールダウン` |
| ズームリセット | `Ctrl+0` |
| ファイルを開く | `Ctrl+O` |
| 終了 | `Ctrl+Q` |

### 依存ライブラリ

| パッケージ | バージョン |
|------------|-----------|
| PyMuPDF | >= 1.23.0 |
| PyQt6 | >= 6.6.0 |

---

## English

### How It Differs from Existing Apps

| | PDF Manga Viewer | Adobe / Foxit | SumatraPDF | Browser built-in |
|--|:--:|:--:|:--:|:--:|
| Manga-focused minimal UI | ✅ | ❌ feature-heavy | △ | ❌ |
| Auto-detects image vs text PDF and routes accordingly | ✅ | ❌ | ❌ | ❌ |
| Background page pre-loading cache | ✅ | ✅ | ✅ | ❌ |
| HiDPI / 4K rendering | ✅ | ✅ | △ | △ |
| Mouse wheel to flip pages (not scroll) | ✅ | ❌ scrolls | ✅ | ❌ |
| No installer required (pip only) | ✅ | ❌ | ❌ | ➖ built-in |
| No ads or subscription | ✅ | △ free ver. has ads | ✅ | ✅ |

**Key differentiator: automatic PDF routing**

On launch, the app inspects the PDF (average character count over the first 3 pages) and decides: if it looks like scanned manga it opens natively, otherwise it hands the file off to whichever PDF reader is already installed on your PC (detected via the Windows registry). This means you can set this app as the single default handler for all `.pdf` files and never manually choose which reader to use.

### Features

- Open PDF files via menu, `Ctrl+O`, or drag & drop
- Page navigation with keyboard or mouse wheel
- Zoom in / out (`Ctrl+=` / `Ctrl+-` / `Ctrl+scroll`)
- Background page pre-loading with a progress bar
- Text-only PDFs (no images) are automatically forwarded to an external reader (Foxit / Adobe / SumatraPDF / Edge)
- HiDPI and 4K display support

### Requirements

- Windows 10 / 11
- Python 3.11 or later

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
# Launch the viewer
python main.py

# Open a specific PDF on startup
python main.py path/to/manga.pdf
```

### Keyboard Shortcuts

| Action | Key |
|--------|-----|
| Next page | `→` `Space` `PageDown` `↓` |
| Previous page | `←` `Backspace` `PageUp` `↑` |
| First page | `Home` |
| Last page | `End` |
| Zoom in | `Ctrl+=` or `Ctrl+scroll up` |
| Zoom out | `Ctrl+-` or `Ctrl+scroll down` |
| Reset zoom | `Ctrl+0` |
| Open file | `Ctrl+O` |
| Quit | `Ctrl+Q` |

### Dependencies

| Package | Version |
|---------|---------|
| PyMuPDF | >= 1.23.0 |
| PyQt6 | >= 6.6.0 |

---

## License

MIT
