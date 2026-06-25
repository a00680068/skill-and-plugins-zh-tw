# 資料範圍與來源說明

本專案整理 AI 技能、外掛與連結器的英文名稱、中文名稱、功能摘要及適用情境。

## 已建立的逐筆欄位

每筆資料目前都包含以下維護欄位：

- `resource_kind`
- `translation_type`
- `source_url`
- `source_text`
- `source_version`
- `verified_at`
- `review_status`
- `reviewer`
- `type_reference_url`
- `type_reference_label`
- `mode_primary`
- `mode_secondary`
- `mode_confidence`
- `mode_review_status`

尚未取得單項官方來源的資料會保留空白，並標記為「待逐筆查證」，不會用推測內容填滿。

## 官方類型參考

- Skills：[Anthropic Claude Code Skills](https://docs.anthropic.com/en/docs/claude-code/skills)
- Connectors：[Use connectors to extend Claude's capabilities](https://support.claude.com/en/articles/11176164-use-connectors-to-extend-claude-s-capabilities)
- Claude Code：[Claude Code overview](https://docs.anthropic.com/en/docs/claude-code/overview)
- Claude Cowork：[Claude Cowork](https://www.anthropic.com/product/claude-cowork)
- Claude Code 擴充方式：[Automate actions with hooks](https://docs.anthropic.com/en/docs/claude-code/hooks-guide)

以上連結用於確認資源類型與使用模式，不代表完成每個第三方工具的逐筆功能驗證。

## 更新原則

- 平台功能、名稱與可用性可能隨時變更。
- 重大功能說明應優先查閱官方文件。
- 若來源不足，應標記待查證，不應自行補成確定事實。
- 逐筆完成驗證後，才填寫 `source_url`、`source_text`、`source_version` 與 `verified_at`。
- `review_status` 建議依序使用：`待逐筆查證`、`機器校對`、`人工校對`、`官方來源已驗證`。
