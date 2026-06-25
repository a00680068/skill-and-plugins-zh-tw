# Launch Kit｜公開發布與擴散指南

這份文件用來把本專案從「已開源」推進到「更容易被找到、收藏、分享與貢獻」。

## 一句話定位

繁體中文與多語系的 Claude / AI Skills、Plugin-type Skills、Connectors 公開索引，可搜尋、篩選、匯出，適合 AI 工作者、開發者、內容創作者與教學者快速查找工具能力。

## GitHub Repo 設定

建議 Description：

```text
Public-safe multilingual catalog of Claude / AI Skills, plugin-type skills, and connectors with searchable HTML and CSV/JSON exports.
```

建議 Website：

```text
https://a00680068.github.io/skill-and-plugins-zh-tw/
```

建議 Topics：

```text
claude
claude-skills
ai-tools
connectors
mcp
prompt-engineering
zh-tw
localization
open-source
```

## GitHub Pages 設定

1. 進入 repo 的 `Settings` → `Pages`。
2. Source 選 `Deploy from a branch`。
3. Branch 選 `main`。
4. Folder 選 `/root`。
5. 儲存後等待 GitHub Pages 建置完成。

## 首波發布文案

### 繁體中文

我整理了一份公開安全版的 Claude / AI Skills、Plugin-type Skills 與 Connectors 索引。

它可以用繁體中文搜尋、篩選、查看使用情境，也能匯出 CSV / JSON。適合想快速理解 AI 工具能力、建立內部知識庫、做教學或補來源的人。

專案不是官方產品，目前仍有逐筆來源與翻譯校對待補。歡迎 Star、開 issue 或協助補官方來源。

### English

I published a public-safe multilingual catalog for Claude / AI skills, plugin-type skills, and connectors.

It includes a searchable static HTML interface plus CSV / JSON exports. The project is useful for AI workflow builders, documentation writers, educators, and anyone comparing tool capabilities.

It is not an official product. Item-level source verification and localization review are still ongoing. Stars, issues, and source-verification contributions are welcome.

## 發布順序

1. 啟用 GitHub Pages，確認首頁可開。
2. 在 GitHub About 補 Description、Website、Topics。
3. 建立第一個 release，例如 `v0.2.0-multilingual-public-index`。
4. 發布繁中貼文，主打「可搜尋的 Claude / AI 工具索引」。
5. 發布英文貼文，主打 public-safe searchable catalog。
6. 把需要貢獻的任務拆成 issue，例如來源補齊、翻譯校對、分類調整。
7. 每次補 20-50 筆來源或校對後發小更新，讓專案有持續活動紀錄。

## 成長飛輪

- 被搜尋：README、HTML meta、topics、GitHub Pages。
- 被收藏：清楚定位、可直接使用、離線 HTML。
- 被分享：短文案、CSV / JSON、公開安全聲明。
- 被貢獻：issue 模板、來源驗證指南、翻譯狀態欄位。
- 被信任：限制聲明、商標聲明、逐筆來源欄位。

## 不建議做的事

- 不宣稱這是 Claude / Anthropic 官方資料。
- 不宣稱所有項目已可用或已安裝。
- 不把未校對機器翻譯包裝成最終品質。
- 不混入私用工作流、金鑰、本機路徑或客戶資料。
