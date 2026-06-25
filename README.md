# Skill & Plugins｜技能 & 連結器

一套以繁體中文為主的 AI 技能、外掛型技能與連結器查詢工具，協助 Claude 與 AI 工作者快速理解「哪些能力適合什麼任務」。

這是公開安全版：不包含 U.AI Logo、私用設定、金鑰、token、本機絕對路徑或外部 CDN。

> 可作為 GitHub Pages 靜態網站、離線 HTML 工具，或 AI 工具索引資料集使用。

## 一句話定位

給 AI 工作者、開發者、內容創作者與中文使用者使用的公開目錄：把零散的 Skills、Plugin-type Skills 與 Connectors 整理成可搜尋、可匯出、可離線部署的多語資料集。

適合：

- 想快速查找 Claude / AI 工作流程能力的人
- 想建立中文 AI 工具索引、教學或內部知識庫的人
- 想比較技能、連結器與適配模式的開發者
- 想協助補來源、校對翻譯、改善中文術語的貢獻者

## 目前收錄

- 578 個技能
- 其中 547 個標記為外掛型技能
- 72 個連結器
- 74 個功能群組
- 共 650 筆中英文對照資料

## 主要功能

- 中英文即時搜尋
- 技能／連結器類型篩選
- 點擊式領域選單
- 中文功能說明與最佳使用時機
- Claude Chat／Claude Code／Claude Cowork 適配模式建議
- 適配模式信心等級與人工覆核狀態
- 逐筆來源、版本與校對狀態欄位
- 技術術語提示與情境翻譯提示
- 一鍵複製結構化提問範例
- CSV 匯出
- 列印或另存 PDF
- 桌機與手機響應式介面
- 無外部 CDN，可作為純靜態網站部署

## 直接使用

雙擊 `index.html` 即可離線瀏覽。

多語版本：

- `index.html`：繁體中文主版
- `index.zh-CN.html`：簡體中文版本
- `index.en.html`：英文版本
- `index.ja.html`：日文版本

對應資料檔位於 `data/skills-and-connectors.<locale>.json` 與 `data/skills-and-connectors.<locale>.csv`。

若瀏覽器限制本機剪貼簿功能，可在本資料夾執行：

```bash
python -m http.server 8765
```

再開啟：

```text
http://127.0.0.1:8765/
```

這個網址只適用於當前電腦。若要給別人使用，請部署到 GitHub Pages、Cloudflare Pages、Netlify、Vercel 或其他靜態網站空間。

## 部署

這是純靜態網站。部署時保留以下內容即可：

```text
index.html
index.*.html
data/
*.md
LICENSE
DATA-LICENSE.md
.nojekyll
robots.txt
sitemap.xml
```

本公開安全版已移除品牌圖片資產，因此不需要 `assets/` 資料夾。

### GitHub Pages 快速設定

1. 到 GitHub repo 的 `Settings` → `Pages`。
2. Source 選 `Deploy from a branch`。
3. Branch 選 `main`，folder 選 `/root`。
4. 啟用後，把 repo About 的 Website 填成：

```text
https://a00680068.github.io/skill-and-plugins-zh-tw/
```

建議 repo topics：

```text
claude, claude-skills, ai-tools, connectors, mcp, prompt-engineering, zh-tw, localization, open-source
```

## 授權

- 程式碼：MIT License，見 [LICENSE](LICENSE)。
- 對照資料與文件：Creative Commons Attribution 4.0 International，見 [DATA-LICENSE.md](DATA-LICENSE.md)。
- 第三方名稱與商標：僅作識別與對照用途，權利歸各自權利人所有，見 [TRADEMARKS.md](TRADEMARKS.md)。

## 重要限制

- 本專案是查詢與理解工具，不代表列出的項目已安裝或可立即使用。
- 實際功能取決於平台、帳號方案、版本、安裝狀態與權限。
- 「適配模式」為依任務特性產生的使用建議，不是平台官方逐項認證。
- 尚未逐筆完成 650 筆官方來源驗證；未驗證項目會標示「待逐筆查證」。
- 簡體中文為 OpenCC 轉換基線；英文與日文為機器翻譯基線，皆保留「待人工覆核」狀態，不應視為最終人工審校版本。
- 本專案不是 Anthropic、Claude 或任何第三方平台的官方產品。

## 相關文件

- [TRANSLATION_REVIEW.md](TRANSLATION_REVIEW.md)：翻譯品質評估
- [TRANSLATION_COVERAGE_AUDIT.md](TRANSLATION_COVERAGE_AUDIT.md)：中文覆蓋檢查
- [README.zh-CN.md](README.zh-CN.md)：簡體中文說明
- [README.en.md](README.en.md)：英文說明
- [README.ja.md](README.ja.md)：日文說明
- [GLOSSARY.md](GLOSSARY.md)：術語規則
- [SOURCES_AND_SCOPE.md](SOURCES_AND_SCOPE.md)：來源與範圍
- [SOURCE_VERIFICATION_GUIDE.md](SOURCE_VERIFICATION_GUIDE.md)：逐筆來源補齊方式
- [SECURITY.md](SECURITY.md)：安全說明
- [PRIVACY.md](PRIVACY.md)：隱私說明
- [DISCLAIMER.md](DISCLAIMER.md)：免責聲明
- [LAUNCH_KIT.md](LAUNCH_KIT.md)：公開發布、社群貼文與 GitHub 曝光設定建議

## 幫忙擴散

如果這個專案對你有幫助，可以：

- 在 GitHub 按 Star，方便之後回來查。
- 分享給正在使用 Claude、AI Agent、提示詞或自動化工具的朋友。
- 開 issue 回報翻譯、分類、來源或功能建議。
- 依 [SOURCE_VERIFICATION_GUIDE.md](SOURCE_VERIFICATION_GUIDE.md) 協助補官方來源。

## 專案身份

整理與介面設計：UNO
