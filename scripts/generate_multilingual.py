from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
from pathlib import Path
from typing import Callable


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "skills-and-connectors.json"
TEMPLATE_PATH = ROOT / "index.html"
CACHE_PATH = ROOT / "data" / "i18n-translation-cache.json"

LOCALES = ("zh-TW", "zh-CN", "en", "ja")
HTML_FILES = {
    "zh-TW": "index.html",
    "zh-CN": "index.zh-CN.html",
    "en": "index.en.html",
    "ja": "index.ja.html",
}

FIELD_NAMES = [
    "d",
    "g",
    "gd",
    "t",
    "zh",
    "de",
    "tr",
    "resource_kind",
    "translation_type",
    "review_status",
    "mode_review_status",
    "type_reference_label",
    "mode_confidence",
]

CSV_HEADERS = {
    "zh-TW": [
        "領域",
        "群組",
        "群組說明",
        "資源形態",
        "類型",
        "英文名稱",
        "中文名稱",
        "功能說明",
        "最佳使用時機",
        "翻譯方式",
        "來源網址",
        "來源原文",
        "來源版本",
        "驗證日期",
        "校對狀態",
        "校對者",
        "類型參考網址",
        "類型參考名稱",
        "首選模式",
        "次選模式",
        "模式信心",
        "模式覆核狀態",
        "在地化狀態",
    ],
    "zh-CN": [
        "领域",
        "群组",
        "群组说明",
        "资源形态",
        "类型",
        "英文名称",
        "中文名称",
        "功能说明",
        "最佳使用时机",
        "翻译方式",
        "来源网址",
        "来源原文",
        "来源版本",
        "验证日期",
        "校对状态",
        "校对者",
        "类型参考网址",
        "类型参考名称",
        "首选模式",
        "次选模式",
        "模式信心",
        "模式复核状态",
        "本地化状态",
    ],
    "en": [
        "Domain",
        "Group",
        "Group description",
        "Resource kind",
        "Type",
        "Original English name",
        "Localized name",
        "Description",
        "Best-use moment",
        "Translation method",
        "Source URL",
        "Source text",
        "Source version",
        "Verified at",
        "Review status",
        "Reviewer",
        "Type reference URL",
        "Type reference label",
        "Primary mode",
        "Secondary mode",
        "Mode confidence",
        "Mode review status",
        "Localization status",
    ],
    "ja": [
        "領域",
        "グループ",
        "グループ説明",
        "リソース種別",
        "タイプ",
        "英語原名",
        "ローカライズ名",
        "機能説明",
        "最適な使用場面",
        "翻訳方式",
        "出典URL",
        "出典原文",
        "出典バージョン",
        "検証日",
        "レビュー状態",
        "レビュアー",
        "種別参照URL",
        "種別参照名",
        "推奨モード",
        "補助モード",
        "モード信頼度",
        "モードレビュー状態",
        "ローカライズ状態",
    ],
}

MANUAL_TERMS = {
    "en": {
        "技能": "Skill",
        "連結器": "Connector",
        "外掛型技能": "Plugin-type Skill",
        "功能導向翻譯": "Functional translation",
        "保留品牌原名": "Brand name retained",
        "待逐筆查證": "Pending item-level verification",
        "待人工覆核": "Pending human review",
        "高": "High",
        "中": "Medium",
        "低": "Low",
        "Anthropic Skills 官方說明": "Anthropic Skills official documentation",
        "Claude Code 擴充方式官方說明": "Claude Code extension documentation",
        "Claude Connectors 官方說明": "Claude Connectors official documentation",
    },
    "ja": {
        "技能": "スキル",
        "連結器": "コネクター",
        "外掛型技能": "プラグイン型スキル",
        "功能導向翻譯": "機能ベースの翻訳",
        "保留品牌原名": "ブランド名を保持",
        "待逐筆查證": "項目ごとの検証待ち",
        "待人工覆核": "人手レビュー待ち",
        "高": "高",
        "中": "中",
        "低": "低",
        "Anthropic Skills 官方說明": "Anthropic Skills 公式ドキュメント",
        "Claude Code 擴充方式官方說明": "Claude Code 拡張方式の公式ドキュメント",
        "Claude Connectors 官方說明": "Claude Connectors 公式ドキュメント",
    },
}

STATIC_REPLACEMENTS = {
    "en": {
        '<html lang="zh-Hant">': '<html lang="en">',
        'content="用繁體中文快速查找技能與連結器，了解功能、適用情境、使用前提與提問方式。"': 'content="Search AI skills, plugin-type skills, and connectors in English. Compare capabilities, use cases, prerequisites, and prompt examples."',
        "<title>Skill &amp; Plugins｜技能 &amp; 連結器</title>": "<title>Skill &amp; Plugins | Skills &amp; Connectors</title>",
        "Knowledge System Online · 知識系統已上線": "Knowledge System Online",
        "650 Nodes Indexed · 650 個節點已索引": "650 Nodes Indexed",
        "Traditional Chinese · 繁體中文": "English",
        "公開安全版 · 繁體中文工具索引": "Public Safe Edition · English Tool Index",
        '<span class="title-zh">技能 &amp; 連結器</span>': '<span class="title-zh">Skills &amp; Connectors</span>',
        "不只告訴你有哪些工具，也幫你判斷什麼時候該用、使用前要準備什麼，以及可以怎麼向 AI 提問。": "Find what each tool does, when to use it, what to prepare, and how to ask an AI for a usable result.",
        "技能</span>": "Skills</span>",
        "外掛型技能</span>": "Plugin-type Skills</span>",
        "連結器</span>": "Connectors</span>",
        "分類</span>": "Groups</span>",
        "描述你想完成的事，例如：整理會議、做簡報、找客戶、查 Notion…": "Describe the task, such as meeting notes, slides, customer research, or Notion lookup...",
        "清除 ✕": "Clear x",
        'data-type="">全部': 'data-type="">All',
        'data-type="技能">技能': 'data-type="Skill">Skills',
        'data-type="連結器">連結器': 'data-type="Connector">Connectors',
        "切換精簡模式": "Compact mode",
        "全部展開": "Expand all",
        "全部收合": "Collapse all",
        "領域分類": "Domain",
        "全部領域": "All domains",
        "選擇領域分類": "Select domain",
        "分享此頁": "Share page",
        "匯出 CSV": "Export CSV",
        "列印／另存 PDF": "Print / Save PDF",
        "我想知道「怎麼做」": "I want a repeatable method",
        "我要安裝「擴充包」": "I want an extension package",
        "我需要「真實資料」": "I need live data",
        "我要完成整套工作": "I need the whole workflow",
        "第一次使用？展開查看完整說明": "First time here? Open the guide",
        "約 2 分鐘看懂": "About 2 minutes",
        "先描述你要完成的事": "Describe the job first",
        "看「適合何時使用」": "Check when to use it",
        "複製提問範例": "Copy the prompt example",
        "技術術語與翻譯規則": "Technical terms and translation rules",
        "避免中英混用看不懂": "For clearer terminology",
        "使用提醒：": "Usage note:",
        "模式判讀：": "Mode guidance:",
        "翻譯標示：": "Translation note:",
        "能做什麼": "What it does",
        "適配模式": "Best-fit mode",
        "首選": "Primary",
        "可搭配": "Also works with",
        "信心": "Confidence",
        "核心優勢": "Key advantage",
        "最佳使用時機": "Best-use moment",
        "術語提示": "Term hints",
        "使用前注意": "Before use",
        "翻譯方式": "Translation method",
        "來源狀態": "Source status",
        "已連結逐筆來源": "Item source linked",
        "類型參考": "Type reference",
        "驗證日期": "Verified at",
        "複製提問範例": "Copy prompt example",
        "找不到符合": "No matching results for",
        "試試其他關鍵字，或點上方「全部」。": 'Try another keyword, or choose "All".',
        "顯示": "Showing",
        "筆": "items",
        "搜尋：": "Search:",
        "類型：": "Type:",
        "領域：": "Domain:",
        "共收錄": "Total",
        "個項目": "items",
        "獨立離線網頁版": "Standalone offline page",
        "更新日期": "Updated",
        "CSV 已下載": "CSV downloaded",
        "技能與連結器完整中文對照表": "Skills and Connectors directory",
        "已複製本機網址；公開分享請先上傳至網站空間": "Local URL copied; upload the site before public sharing",
        "網址已複製": "URL copied",
        "瀏覽器未允許分享，請直接傳送 index.html": "Sharing was blocked by the browser; send the HTML file directly",
        "切換完整模式": "Full mode",
        "回到頂端": "Back to top",
        "外掛型Skills": "Plugin-type Skills",
        "領域Groups": "Domain",
        "選擇Domain": "Select domain",
        "待逐items查證": "Pending item-level verification",
        "搜尋與篩選": "Search and filters",
        "項目類型": "Item type",
        "使用方式說明": "How to use",
        "選擇 <strong>Skill</strong>。適合寫簡報、做研究、分析資料、設計流程等需要固定方法與交付格式的任務。": "Choose <strong>Skill</strong> when the work needs a repeatable method and a clear deliverable, such as slides, research, analysis, or workflow design.",
        "選擇 <strong>Plugin-type Skill</strong>。Plugin 是分享與安裝擴充功能的封裝方式，內部可以包含技能、工具或整合設定。": "Choose <strong>Plugin-type Skill</strong> when the capability is packaged as an installable extension that may include skills, tools, or integration settings.",
        "選擇 <strong>Connector</strong>。當 AI 必須讀取 Gmail、Notion、CRM、資料庫或其他服務中的實際內容時使用。": "Choose <strong>Connector</strong> when the AI needs to access real data from Gmail, Notion, CRM, databases, or other services.",
        "搭配 <strong>技能＋連結器</strong>。例如先從 Gmail 讀取客戶信件，再用提案技能整理成可交付文件。": "Combine <strong>skills + connectors</strong> when the workflow needs both real data access and a repeatable method, such as reading Gmail and turning it into a proposal.",
        "不用先知道工具名稱。直接搜尋「做簡報」「整理會議」「查客戶資料」等工作目的。": "You do not need to know the tool name first. Search by job intent, such as creating slides, summarizing meetings, or researching customers.",
        "確認這個工具是否符合你的情境，再查看使用前是否需要檔案、登入或權限。": "Check whether the tool fits your situation, then confirm whether files, sign-in, or permissions are needed before use.",
        "點卡片下方的按鈕，補上目標、資料與輸出格式，再貼給支援該工具的 AI。": "Click the button on a card, fill in the goal, data, and output format, then paste it into an AI environment that supports the tool.",
        "案例一｜只有技能": "Example 1 | Skill only",
        "案例二｜只有連結器": "Example 2 | Connector only",
        "案例三｜技能＋連結器": "Example 3 | Skill + connector",
        "你已有會議items記，想整理成重點與待辦：搜尋「會議摘要」，選擇適合的技能。": "You already have meeting notes and want highlights and tasks: search for meeting summary and choose the right skill.",
        "你想讓 AI 讀取 Notion 內的專案資料：搜尋「Notion」，先完成登入與授權。": "You want AI to read project data from Notion: search for Notion, then sign in and authorize the connector.",
        "從 Gmail 讀取合作邀請，再整理成提案與任務清單：使用 Gmail 連結器搭配提案／專案技能。": "Read a collaboration request from Gmail, then turn it into a proposal and task list using a Gmail connector with proposal or project skills.",
        "Brief（需求簡報／任務摘要）": "Brief",
        "說明目標、受眾、限制與交付需求的文件。": "A document that states goals, audience, constraints, and delivery requirements.",
        "redline（修訂標記版）": "redline",
        "Showing新增、刪除與修改內容的合約或文件版本。": "A contract or document version that marks additions, deletions, and edits.",
        "schema（資料結構定義）": "schema",
        "規範資料有哪些欄位、型別與關係。": "A definition of data fields, types, and relationships.",
        "Artifact（可互動成果物）": "Artifact",
        "由 AI 產生並可檢視、編輯或互動的獨立成果。": "A standalone AI-generated output that can be viewed, edited, or interacted with.",
        "pipeline（處理流程／管線）": "pipeline",
        "資料或任務依序經過多個處理階段的流程。": "A process where data or tasks pass through multiple stages.",
        "onboarding（到職／導入流程）": "onboarding",
        "依情境指新人到職、客戶導入或產品啟用流程。": "A setup or adoption flow for employees, customers, or products.",
        "enrichment（資料補全）": "enrichment",
        "為既有名單補上職稱、公司、聯絡方式或其他資訊。": "Adding titles, company details, contact information, or other useful data to existing records.",
        "repository／repo（程式碼儲存庫）": "repository / repo",
        "集中保存程式碼、版本紀錄與協作內容的位置。": "A place for code, version history, and collaboration.",
        "技能是「做事的方法」，連結器是「取得資料的橋樑」。實際可用項目仍取決於帳號方案、安裝狀態與權限；連結器通常需要先登入並授權。": "Skills are repeatable methods for doing work; connectors are bridges to data and actions. Availability still depends on account plan, installation status, and permissions. Connectors usually require sign-in and authorization.",
        "Claude Chat 適合對話、研究與內容迭代；Claude Code 適合程式碼庫、終端、測試與部署；Claude Cowork 適合本機檔案、跨應用程式與多步驟交付。「Best-fit mode」是依任務特性提供的使用建議，不代表只能在該模式使用。": "Claude Chat fits conversation, research, and content iteration. Claude Code fits repositories, terminals, tests, and deployment. Claude Cowork fits local files, cross-application work, and multi-step delivery. Best-fit mode is guidance based on task traits, not an exclusive rule.",
        "保留英文原名供快速比對，中文名稱採功能導向翻譯。標題中的 Plugins 是品牌呈現用語；資料內容仍依實際性質區分為「技能」與「連結器」。": "Original English names are retained for comparison. Localized names are functional translations. Plugins in the title is a presentation label; each item is still classified by its actual resource type.",
        "此英文名稱在不同工具脈絡中另有譯法：${esc(variants.join(\"／\"))}。比對時請以英文原名與所屬群組為準。": "This English name has other translations in different tool contexts: ${esc(variants.join(\" / \"))}. Compare by original English name and group.",
        "已複製「${row.zh}」提問範例": "Prompt example copied: ${row.zh}",
        "No matching results for「${esc(q)}」的項目": "No matching results for \"${esc(q)}\"",
        "先確認：服務帳號可登入、連結器已安裝，並只授予完成任務所需的權限。": "First check that the service account is available, the connector is installed, and only the minimum required permissions are granted.",
        "建議準備：清楚目標、現有素材、對象、限制條件與希望輸出的格式。": "Prepare a clear goal, existing materials, audience, constraints, and preferred output format.",
        "需要直接理解程式碼庫、修改多個檔案、執行命令、測試或部署時，Claude Code 的效益最高。": "Claude Code is the best fit when the task requires repository context, file edits, commands, tests, or deployment.",
        "需要連接真實服務資料、操作檔案或完成跨工具的多步驟工作時，Claude Cowork 最適合；若只查詢與討論資料，也可在 Claude Chat 使用。": "Claude Cowork is the best fit for live service data, file operations, or multi-tool workflows. Claude Chat can still be used for discussion and analysis.",
        "需要處理本機檔案、辦公文件、跨應用程式流程或直接交付成品時，Claude Cowork 的整體效益最高。": "Claude Cowork is the best fit for local files, office documents, cross-application workflows, or direct deliverables.",
        "適合透過對話釐清需求、研究分析、構思內容、比較方案或迭代文字成果，使用 Claude Chat 最直接。": "Claude Chat is the most direct fit for clarifying requirements, research, analysis, ideation, comparisons, and text iteration.",
        "適合先在 Claude Chat 中說明需求並取得結果；若後續涉及本機檔案或跨工具執行，再改用 Claude Cowork。": "Start in Claude Chat to clarify the request and produce the first result. Move to Claude Cowork if files or cross-tool execution are needed.",
    },
    "ja": {
        '<html lang="zh-Hant">': '<html lang="ja">',
        'content="用繁體中文快速查找技能與連結器，了解功能、適用情境、使用前提與提問方式。"': 'content="AIスキル、プラグイン型スキル、コネクターを日本語で検索し、機能、利用場面、前提条件、質問例を確認できます。"',
        "<title>Skill &amp; Plugins｜技能 &amp; 連結器</title>": "<title>Skill &amp; Plugins｜スキル &amp; コネクター</title>",
        "Knowledge System Online · 知識系統已上線": "Knowledge System Online · 知識システム稼働中",
        "650 Nodes Indexed · 650 個節點已索引": "650 Nodes Indexed · 650項目を索引化",
        "Traditional Chinese · 繁體中文": "Japanese · 日本語",
        "公開安全版 · 繁體中文工具索引": "公開安全版 · 日本語ツール索引",
        '<span class="title-zh">技能 &amp; 連結器</span>': '<span class="title-zh">スキル &amp; コネクター</span>',
        "不只告訴你有哪些工具，也幫你判斷什麼時候該用、使用前要準備什麼，以及可以怎麼向 AI 提問。": "ツール一覧だけでなく、使う場面、準備すべきこと、AIへの依頼方法まで確認できます。",
        "技能</span>": "スキル</span>",
        "外掛型技能</span>": "プラグイン型スキル</span>",
        "連結器</span>": "コネクター</span>",
        "分類</span>": "分類</span>",
        "描述你想完成的事，例如：整理會議、做簡報、找客戶、查 Notion…": "やりたいことを入力。例：会議整理、資料作成、顧客調査、Notion検索...",
        "清除 ✕": "クリア x",
        'data-type="">全部': 'data-type="">すべて',
        'data-type="技能">技能': 'data-type="スキル">スキル',
        'data-type="連結器">連結器': 'data-type="コネクター">コネクター',
        "切換精簡模式": "簡易表示",
        "全部展開": "すべて展開",
        "全部收合": "すべて閉じる",
        "領域分類": "領域",
        "全部領域": "すべての領域",
        "選擇領域分類": "領域を選択",
        "分享此頁": "このページを共有",
        "匯出 CSV": "CSV出力",
        "列印／另存 PDF": "印刷 / PDF保存",
        "我想知道「怎麼做」": "方法を知りたい",
        "我要安裝「擴充包」": "拡張パッケージを使いたい",
        "我需要「真實資料」": "実データが必要",
        "我要完成整套工作": "ワークフロー全体を進めたい",
        "第一次使用？展開查看完整說明": "初めての方はこちら",
        "約 2 分鐘看懂": "約2分",
        "先描述你要完成的事": "まず目的を説明する",
        "看「適合何時使用」": "利用場面を確認する",
        "複製提問範例": "質問例をコピー",
        "技術術語與翻譯規則": "技術用語と翻訳ルール",
        "避免中英混用看不懂": "用語をわかりやすく整理",
        "使用提醒：": "利用メモ：",
        "模式判讀：": "モード判断：",
        "翻譯標示：": "翻訳注記：",
        "能做什麼": "できること",
        "適配模式": "適したモード",
        "首選": "推奨",
        "可搭配": "併用可",
        "信心": "信頼度",
        "核心優勢": "主な利点",
        "最佳使用時機": "最適な使用場面",
        "術語提示": "用語ヒント",
        "使用前注意": "利用前の注意",
        "翻譯方式": "翻訳方式",
        "來源狀態": "出典状態",
        "已連結逐筆來源": "項目別出典あり",
        "類型參考": "種別参照",
        "驗證日期": "検証日",
        "找不到符合": "一致する項目がありません：",
        "試試其他關鍵字，或點上方「全部」。": "別のキーワードを試すか、「すべて」を選択してください。",
        "顯示": "表示",
        "筆": "件",
        "搜尋：": "検索：",
        "類型：": "タイプ：",
        "領域：": "領域：",
        "共收錄": "収録数",
        "個項目": "項目",
        "獨立離線網頁版": "スタンドアロン版",
        "更新日期": "更新日",
        "CSV 已下載": "CSVをダウンロードしました",
        "技能與連結器完整中文對照表": "スキルとコネクターのディレクトリ",
        "已複製本機網址；公開分享請先上傳至網站空間": "ローカルURLをコピーしました。公開共有前にサイトへアップロードしてください",
        "網址已複製": "URLをコピーしました",
        "瀏覽器未允許分享，請直接傳送 index.html": "ブラウザーで共有が許可されていません。HTMLファイルを直接共有してください",
        "切換完整模式": "詳細表示",
        "回到頂端": "上へ戻る",
        "外掛型スキル": "プラグイン型スキル",
        "搜尋與篩選": "検索とフィルター",
        "項目類型": "項目タイプ",
        "選擇領域": "領域を選択",
        "使用方式說明": "使い方",
        "選擇 <strong>スキル</strong>。適合寫簡報、做研究、分析資料、設計流程等需要固定方法與交付格式的任務。": "<strong>スキル</strong>は、資料作成、調査、データ分析、業務設計など、決まった方法と成果物が必要な作業に使います。",
        "選擇 <strong>プラグイン型スキル</strong>。Plugin 是分享與安裝擴充功能的封裝方式，內部可以包含技能、工具或整合設定。": "<strong>プラグイン型スキル</strong>は、スキル、ツール、連携設定を含む拡張パッケージとして提供されるものです。",
        "選擇 <strong>コネクター</strong>。當 AI 必須讀取 Gmail、Notion、CRM、資料庫或其他服務中的實際內容時使用。": "<strong>コネクター</strong>は、Gmail、Notion、CRM、データベースなど実データへの接続が必要な場合に使います。",
        "搭配 <strong>技能＋連結器</strong>。例如先從 Gmail 讀取客戶信件，再用提案技能整理成可交付文件。": "<strong>スキル＋コネクター</strong>を組み合わせると、実データの取得と成果物作成を一連の流れで進められます。",
        "不用先知道工具名稱。直接搜尋「做簡報」「整理會議」「查客戶資料」等工作目的。": "ツール名を知らなくても構いません。「資料作成」「会議整理」「顧客調査」など目的で検索してください。",
        "確認這個工具是否符合你的情境，再查看使用前是否需要檔案、登入或權限。": "そのツールが目的に合うか確認し、利用前にファイル、ログイン、権限が必要か確認します。",
        "點卡片下方的按鈕，補上目標、資料與輸出格式，再貼給支援該工具的 AI。": "カード下のボタンを押し、目的、資料、出力形式を補って、対応するAI環境に貼り付けます。",
        "案例一｜只有技能": "例1｜スキルのみ",
        "案例二｜只有連結器": "例2｜コネクターのみ",
        "案例三｜技能＋連結器": "例3｜スキル＋コネクター",
        "你已有會議件記，想整理成重點與待辦：搜尋「會議摘要」，選擇適合的技能。": "会議メモを要点とタスクに整理したい場合は、「会議要約」で検索して適切なスキルを選びます。",
        "你想讓 AI 讀取 Notion 內的專案資料：搜尋「Notion」，先完成登入與授權。": "AIにNotion内のプロジェクト資料を読ませたい場合は、「Notion」で検索し、ログインと認可を完了します。",
        "從 Gmail 讀取合作邀請，再整理成提案與任務清單：使用 Gmail 連結器搭配提案／專案技能。": "Gmailの依頼メールを読み取り、提案書やタスクリストに整理する場合は、Gmailコネクターと提案・プロジェクト系スキルを組み合わせます。",
        "Brief（需求簡報／任務摘要）": "Brief（要件ブリーフ）",
        "說明目標、受眾、限制與交付需求的文件。": "目的、対象者、制約、納品要件をまとめた文書です。",
        "redline（修訂標記版）": "redline（変更表示版）",
        "顯示新增、刪除與修改內容的合約或文件版本。": "追加、削除、変更箇所を示す契約書または文書の版です。",
        "schema（資料結構定義）": "schema（データ構造定義）",
        "規範資料有哪些欄位、型別與關係。": "データのフィールド、型、関係を定義します。",
        "Artifact（可互動成果物）": "Artifact（対話型成果物）",
        "由 AI 產生並可檢視、編輯或互動的獨立成果。": "AIが生成し、閲覧、編集、操作できる独立した成果物です。",
        "pipeline（處理流程／管線）": "pipeline（処理パイプライン）",
        "資料或任務依序經過多個處理階段的流程。": "データやタスクが複数の処理段階を順に通る流れです。",
        "onboarding（到職／導入流程）": "onboarding（導入フロー）",
        "依情境指新人到職、客戶導入或產品啟用流程。": "新人、顧客、製品利用開始などの導入プロセスを指します。",
        "enrichment（資料補全）": "enrichment（データ補完）",
        "為既有名單補上職稱、公司、聯絡方式或其他資訊。": "既存リストに役職、会社、連絡先などの情報を追加します。",
        "repository／repo（程式碼儲存庫）": "repository / repo（コードリポジトリ）",
        "集中保存程式碼、版本紀錄與協作內容的位置。": "コード、履歴、共同作業内容を保存する場所です。",
        "技能是「做事的方法」，連結器是「取得資料的橋樑」。實際可用項目仍取決於帳號方案、安裝狀態與權限；連結器通常需要先登入並授權。": "スキルは作業方法、コネクターはデータや操作への橋渡しです。実際に使えるかはアカウントプラン、インストール状態、権限に依存します。コネクターは通常ログインと認可が必要です。",
        "Claude Chat 適合對話、研究與內容迭代；Claude Code 適合程式碼庫、終端、測試與部署；Claude Cowork 適合本機檔案、跨應用程式與多步驟交付。「適したモード」是依任務特性提供的使用建議，不代表只能在該模式使用。": "Claude Chat は対話、調査、文章改善に向いています。Claude Code はコードベース、ターミナル、テスト、デプロイに向いています。Claude Cowork はローカルファイル、アプリ横断作業、複数手順の納品に向いています。適したモードは推奨であり、唯一の利用条件ではありません。",
        "保留英文原名供快速比對，中文名稱採功能導向翻譯。標題中的 Plugins 是品牌呈現用語；資料內容仍依實際性質區分為「技能」與「連結器」。": "英語原名は比較しやすいよう保持しています。ローカライズ名は機能ベースです。タイトルの Plugins は表示上の名称であり、各項目は実際の性質に応じてスキルまたはコネクターに分類されます。",
        "此英文名稱在不同工具脈絡中另有譯法：${esc(variants.join(\"／\"))}。比對時請以英文原名與所屬群組為準。": "この英語名には文脈により別訳があります：${esc(variants.join(\"／\"))}。比較時は英語原名と所属グループを基準にしてください。",
        "已複製「${row.zh}」提問範例": "「${row.zh}」の質問例をコピーしました",
        "找不到符合「${esc(q)}」的項目": "「${esc(q)}」に一致する項目がありません",
        "一致する項目がありません：「${esc(q)}」的項目": "「${esc(q)}」に一致する項目がありません",
        "先確認：服務帳號可登入、連結器已安裝，並只授予完成任務所需的權限。": "まずサービスアカウントにログインできること、コネクターがインストール済みであること、必要最小限の権限だけを付与していることを確認します。",
        "建議準備：清楚目標、現有素材、對象、限制條件與希望輸出的格式。": "目的、既存素材、対象者、制約条件、希望する出力形式を準備してください。",
        "需要直接理解程式碼庫、修改多個檔案、執行命令、測試或部署時，Claude Code 的效益最高。": "コードベース理解、複数ファイル編集、コマンド実行、テスト、デプロイが必要な場合は Claude Code が最適です。",
        "需要連接真實服務資料、操作檔案或完成跨工具的多步驟工作時，Claude Cowork 最適合；若只查詢與討論資料，也可在 Claude Chat 使用。": "実サービスのデータ接続、ファイル操作、複数ツールにまたがる作業には Claude Cowork が適しています。確認や議論だけなら Claude Chat でも利用できます。",
        "需要處理本機檔案、辦公文件、跨應用程式流程或直接交付成品時，Claude Cowork 的整體效益最高。": "ローカルファイル、オフィス文書、アプリ横断の手順、直接納品物を扱う場合は Claude Cowork が最適です。",
        "適合透過對話釐清需求、研究分析、構思內容、比較方案或迭代文字成果，使用 Claude Chat 最直接。": "要件整理、調査分析、アイデア出し、比較検討、文章の反復改善には Claude Chat が最も直接的です。",
        "適合先在 Claude Chat 中說明需求並取得結果；若後續涉及本機檔案或跨工具執行，再改用 Claude Cowork。": "まず Claude Chat で要件を整理して初稿を作り、ファイル操作やツール横断作業が必要になったら Claude Cowork に移行します。",
    },
}

TECH_GLOSSARY_JS = {
    "en": """const TECH_GLOSSARY=[
  {terms:["brief"],label:"Brief",zh:"requirement brief / task summary"},
  {terms:["redline"],label:"redline",zh:"marked-up revision"},
  {terms:["schema"],label:"schema",zh:"data structure definition"},
  {terms:["artifact"],label:"Artifact",zh:"interactive output"},
  {terms:["pipeline"],label:"pipeline",zh:"process pipeline"},
  {terms:["onboarding"],label:"onboarding",zh:"setup or adoption flow"},
  {terms:["enrichment"],label:"enrichment",zh:"data enrichment"},
  {terms:["repository","repo "],label:"repository / repo",zh:"code repository"},
  {terms:["webhook"],label:"webhook",zh:"event callback"},
  {terms:["playbook"],label:"playbook",zh:"operating playbook"},
  {terms:["workflow"],label:"workflow",zh:"workflow"},
  {terms:["dashboard"],label:"dashboard",zh:"dashboard"}
];""",
    "ja": """const TECH_GLOSSARY=[
  {terms:["brief"],label:"Brief",zh:"要件ブリーフ / タスク概要"},
  {terms:["redline"],label:"redline",zh:"変更箇所を示す修正版"},
  {terms:["schema"],label:"schema",zh:"データ構造定義"},
  {terms:["artifact"],label:"Artifact",zh:"対話型成果物"},
  {terms:["pipeline"],label:"pipeline",zh:"処理パイプライン"},
  {terms:["onboarding"],label:"onboarding",zh:"導入フロー"},
  {terms:["enrichment"],label:"enrichment",zh:"データ補完"},
  {terms:["repository","repo "],label:"repository / repo",zh:"コードリポジトリ"},
  {terms:["webhook"],label:"webhook",zh:"イベントコールバック"},
  {terms:["playbook"],label:"playbook",zh:"運用プレイブック"},
  {terms:["workflow"],label:"workflow",zh:"ワークフロー"},
  {terms:["dashboard"],label:"dashboard",zh:"ダッシュボード"}
];""",
}

PROMPT_FOR_JS = {
    "en": r'''function promptFor(r){
  const situation=(r.tr||r.de||"Help complete the related work.").replace(/[「」]/g,"");
  if(r.t==="Connector"){
    return `【Role and Task】
You are a data-integration and workflow assistant familiar with ${r.zh} (${r.en}). Use this connector only within the authorized scope to retrieve the necessary data and complete the task below.

【Background and Goal】
Use case: ${situation}
My specific goal: ______
User / business context: ______

【Data Scope】
Account, workspace, folder, or project to read: ______
Date range, project, or keywords: ______
Content that must not be accessed or processed: ______

【Instructions】
1. Confirm the connector is installed, signed in, and has only the minimum permissions required.
2. Access only data directly related to this task.
3. Separate confirmed facts from inferences and recommendations.
4. Ask for confirmation before creating, editing, deleting, sending, or publishing anything.
5. If the data, permissions, or sources are insufficient, state that clearly instead of guessing.

【Output Format】
1. Executive summary
2. Confirmed data
3. Key findings
4. Recommended actions
5. Open questions

【Quality Standard】
- Write clearly in English.
- Preserve important dates, names, and source locations.
- Avoid exposing sensitive information.
- Make the output specific, actionable, and ready to use.`;
  }
  return `【Role and Task】
You are an expert execution consultant for ${r.zh} (${r.en}). Use the best practices of this skill to produce a usable deliverable.

【Background】
Use case: ${situation}
My specific goal: ______
Audience / use context: ______
Existing materials: ______
Constraints: ______

【Instructions】
1. Confirm the objective, success criteria, and prerequisites.
2. Break the work into clear steps and prioritize the information I provide.
3. Separate known facts, professional judgment, and recommendations.
4. Fill in useful structure and common missing details without drifting from the goal.
5. If there is not enough information for a clear conclusion, write "[Insufficient information to confirm]" and list what is missing.

【Output Format】
Desired deliverable: ______
Length or specification: ______
Include:
1. Final deliverable
2. Execution notes
3. Directly usable content / steps
4. Acceptance checklist

【Quality Standard】
- Write clearly and professionally in English.
- Avoid vague filler and repetition.
- Make the result practical for the stated context.
- The final output should be ready to copy, execute, or hand off.`;
}''',
    "ja": r'''function promptFor(r){
  const situation=(r.tr||r.de||"関連作業を支援する。").replace(/[「」]/g,"");
  if(r.t==="コネクター"){
    return `【役割とタスク】
あなたは ${r.zh}（${r.en}）に詳しいデータ連携・業務フロー支援者です。許可された範囲内で必要なデータを取得し、次のタスクを完了してください。

【背景と目的】
利用場面：${situation}
具体的な目的：＿＿＿＿
利用者／業務シーン：＿＿＿＿

【データ範囲】
読み取るアカウント、ワークスペース、フォルダ：＿＿＿＿
対象期間、プロジェクト、キーワード：＿＿＿＿
読み取り・処理してはいけない内容：＿＿＿＿

【指示】
1. コネクターがインストール済み、ログイン済みで、必要最小限の権限だけを持つことを確認してください。
2. このタスクに直接関係するデータだけを扱ってください。
3. 確認済みの事実、推論、提案を分けてください。
4. 作成、編集、削除、送信、公開が必要な場合は、実行前に確認してください。
5. データ不足、権限不足、矛盾がある場合は、推測せず明記してください。

【出力形式】
1. 要約
2. 確認済みデータ
3. 重要な発見
4. 推奨アクション
5. 未確認事項

【品質基準】
- 自然で明確な日本語で書く。
- 重要な日付、名称、参照位置を残す。
- 機密情報を不用意に出さない。
- 具体的で実行可能な内容にする。`;
  }
  return `【役割とタスク】
あなたは ${r.zh}（${r.en}）領域の実行支援コンサルタントです。このスキルのベストプラクティスに沿って、すぐ使える成果物を作成してください。

【背景情報】
利用場面：${situation}
具体的な目的：＿＿＿＿
対象者／使用シーン：＿＿＿＿
既存資料：＿＿＿＿
制約条件：＿＿＿＿

【具体指示】
1. 目的、成功基準、前提条件を確認してください。
2. 作業を明確な手順に分解し、提供資料を優先してください。
3. 既知の事実、専門的判断、実行提案を分けてください。
4. 必要な構成や抜けやすい要素を補い、目的から外れないようにしてください。
5. 明確な結論に必要な情報が不足する場合は「【資料不足，無法確認】」と書き、不足情報を列挙してください。

【出力形式】
希望する成果物：＿＿＿＿
分量または仕様：＿＿＿＿
必ず含めるもの：
1. 最終成果物
2. 実行ポイント
3. そのまま使える内容／手順
4. 検収チェック項目

【品質基準】
- 自然で専門的な日本語で書く。
- 抽象論や重複を避ける。
- 実際の使用場面に合う内容にする。
- 最終出力はコピー、実行、共有できる状態にする。`;
}''',
}

ADVANTAGE_JS = {
    "en": r'''function advantage(r){
  if(r.t==="Connector"){
    return `Connects directly to real ${r.zh} content, reducing manual copy-and-paste and allowing AI to query, organize, or continue work from current data.`;
  }
  return `Turns ${r.zh}-related work into a repeatable method and output pattern, reducing repeated instructions and making results more complete, consistent, and reusable.`;
}''',
    "ja": r'''function advantage(r){
  if(r.t==="コネクター"){
    return `${r.zh} の実データに直接接続し、手作業のコピー＆ペーストを減らし、AIが最新データに基づいて検索、整理、後続処理を行えるようにします。`;
  }
  return `${r.zh} に関連する作業手順と出力形式を定型化し、説明の繰り返しを減らして、より完全で一貫した再利用可能な結果にします。`;
}''',
}

LANG_SWITCH_HTML = """<nav class="language-switcher" aria-label="Language">
        <a href="index.html">繁中</a>
        <a href="index.zh-CN.html">简中</a>
        <a href="index.en.html">English</a>
        <a href="index.ja.html">日本語</a>
      </nav>"""

LANG_SWITCH_CSS = """.language-switcher{display:flex;gap:6px;flex-wrap:wrap;margin-top:10px}
.language-switcher a{border:1px solid var(--line2);background:rgba(15,21,30,.78);color:var(--muted);border-radius:6px;padding:5px 8px;font-size:12px}
.language-switcher a:hover{color:var(--gold2);border-color:var(--gold-dim)}
"""


def load_cache() -> dict:
    if CACHE_PATH.exists():
        return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
    return {"en": {}, "ja": {}}


def save_cache(cache: dict) -> None:
    CACHE_PATH.write_text(json.dumps(cache, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def opencc_converter() -> Callable[[str], str]:
    try:
        from opencc import OpenCC

        converter = OpenCC("tw2sp")
        return converter.convert
    except Exception:
        table = str.maketrans(
            {
                "體": "体",
                "臺": "台",
                "灣": "湾",
                "與": "与",
                "連": "连",
                "結": "结",
                "器": "器",
                "開": "开",
                "關": "关",
                "發": "发",
                "資": "资",
                "訊": "讯",
                "號": "号",
                "類": "类",
                "項": "项",
                "態": "态",
                "時": "时",
                "機": "机",
                "說": "说",
                "明": "明",
                "處": "处",
                "複": "复",
                "製": "制",
                "匯": "汇",
                "檔": "档",
                "頁": "页",
                "網": "网",
                "體": "体",
                "審": "审",
                "覈": "核",
                "證": "证",
                "義": "义",
                "務": "务",
                "實": "实",
                "際": "际",
                "權": "权",
                "限": "限",
                "謂": "谓",
                "應": "应",
                "對": "对",
                "選": "选",
                "擇": "择",
                "詢": "询",
                "問": "问",
                "範": "范",
                "歸": "归",
                "屬": "属",
                "聯": "联",
                "絡": "络",
                "維": "维",
                "護": "护",
                "顯": "显",
                "示": "示",
                "單": "单",
                "測": "测",
                "試": "试",
                "標": "标",
                "籤": "签",
                "構": "构",
                "築": "筑",
                "數": "数",
            }
        )
        return lambda s: s.translate(table)


def google_translator(target: str):
    from deep_translator import GoogleTranslator

    return GoogleTranslator(source="zh-TW", target=target)


def translate_many(texts: list[str], target: str, cache: dict, use_network: bool) -> dict[str, str]:
    if target not in cache:
        cache[target] = {}
    result = cache[target]
    missing = [text for text in texts if text and text not in result]
    if not missing or not use_network:
        return result

    translator = google_translator(target)
    total = len(missing)
    sep = "\n<<<I18N_SPLIT_9F3B>>>\n"
    chunks: list[list[str]] = []
    current: list[str] = []
    current_len = 0
    for text in missing:
        text_len = len(text) + len(sep)
        if current and current_len + text_len > 2200:
            chunks.append(current)
            current = []
            current_len = 0
        current.append(text)
        current_len += text_len
    if current:
        chunks.append(current)

    def translate_chunk(chunk: list[str], label: str) -> None:
        if not chunk:
            return
        try:
            merged = sep.join(chunk)
            translated = translator.translate(merged)
            parts = translated.split("<<<I18N_SPLIT_9F3B>>>")
            if len(parts) != len(chunk):
                raise RuntimeError(f"split mismatch: expected {len(chunk)}, got {len(parts)}")
            for source, value in zip(chunk, parts):
                result[source] = value.strip()
        except Exception as exc:
            print(f"[warn] {target} chunk {label} failed: {exc}", file=sys.stderr, flush=True)
            if len(chunk) > 1:
                mid = max(1, len(chunk) // 2)
                translate_chunk(chunk[:mid], label + "a")
                translate_chunk(chunk[mid:], label + "b")
                return
            text = chunk[0]
            try:
                result[text] = translator.translate(text)
            except Exception as item_exc:
                print(f"[warn] {target} item fallback failed: {item_exc}", file=sys.stderr, flush=True)
                result[text] = text

    done = 0
    for chunk_index, chunk in enumerate(chunks, 1):
        translate_chunk(chunk, f"{chunk_index}/{len(chunks)}")
        for text in chunk:
            if text not in result:
                try:
                    result[text] = translator.translate(text)
                except Exception as item_exc:
                    print(f"[warn] {target} item fallback failed: {item_exc}", file=sys.stderr, flush=True)
                    result[text] = text
        done += len(chunk)
        print(f"[i18n] {target}: {done}/{total} translated", flush=True)
        if chunk_index % 8 == 0 or done == total:
            save_cache(cache)
            time.sleep(0.4)
    save_cache(cache)
    return result


def collect_texts(records: list[dict]) -> list[str]:
    texts: list[str] = []
    seen: set[str] = set()
    for row in records:
        for field in FIELD_NAMES:
            value = str(row.get(field, "") or "")
            if value and value not in seen:
                seen.add(value)
                texts.append(value)
    return texts


def localize_records(records: list[dict], locale: str, cache: dict, zh_cn: Callable[[str], str]) -> list[dict]:
    localized: list[dict] = []
    status = {
        "zh-TW": "人工整理基準版",
        "zh-CN": "OpenCC 簡體轉換基線，待人工覆核",
        "en": "Machine translation baseline; pending human review",
        "ja": "機械翻訳ベースライン、人手レビュー待ち",
    }[locale]

    def convert(value: str) -> str:
        if not value:
            return value
        if locale == "zh-TW":
            return value
        if locale == "zh-CN":
            return zh_cn(value)
        if value in MANUAL_TERMS.get(locale, {}):
            return MANUAL_TERMS[locale][value]
        return cache.get(locale, {}).get(value, value)

    for row in records:
        item = dict(row)
        for field in FIELD_NAMES:
            if field in item:
                item[field] = convert(str(item.get(field, "") or ""))
        item["localization_locale"] = locale
        item["localization_status"] = status
        localized.append(item)
    return localized


def write_json(path: Path, data: list[dict]) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_csv(path: Path, data: list[dict], locale: str) -> None:
    rows = []
    for r in data:
        rows.append(
            [
                r.get("d", ""),
                r.get("g", ""),
                r.get("gd", ""),
                r.get("resource_kind", ""),
                r.get("t", ""),
                r.get("en", ""),
                r.get("zh", ""),
                r.get("de", ""),
                r.get("tr", ""),
                r.get("translation_type", ""),
                r.get("source_url", ""),
                r.get("source_text", ""),
                r.get("source_version", ""),
                r.get("verified_at", ""),
                r.get("review_status", ""),
                r.get("reviewer", ""),
                r.get("type_reference_url", ""),
                r.get("type_reference_label", ""),
                r.get("mode_primary", ""),
                r.get("mode_secondary", ""),
                r.get("mode_confidence", ""),
                r.get("mode_review_status", ""),
                r.get("localization_status", ""),
            ]
        )
    with path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS[locale])
        writer.writerows(rows)


def compact_js_array(records: list[dict]) -> str:
    keys = [
        "d",
        "g",
        "gd",
        "t",
        "en",
        "zh",
        "de",
        "tr",
        "resource_kind",
        "translation_type",
        "source_url",
        "source_text",
        "source_version",
        "verified_at",
        "review_status",
        "reviewer",
        "mode_review_status",
        "type_reference_url",
        "type_reference_label",
        "mode_primary",
        "mode_secondary",
        "mode_confidence",
        "localization_locale",
        "localization_status",
    ]
    trimmed = []
    for row in records:
        item = {key: row.get(key, "") for key in keys if row.get(key, "") not in (None, "")}
        trimmed.append(item)
    return json.dumps(trimmed, ensure_ascii=False, separators=(",", ":"))


def replace_data_block(html: str, records: list[dict]) -> str:
    domains = []
    seen = set()
    for row in records:
        domain = row.get("d", "")
        if domain and domain not in seen:
            seen.add(domain)
            domains.append(domain)
    html = re.sub(
        r"const DOMAINS=\[.*?\];",
        "const DOMAINS=" + json.dumps(domains, ensure_ascii=False, separators=(",", ":")) + ";",
        html,
        flags=re.S,
    )
    html = re.sub(
        r"const DATA=\[\n.*?\n/\*__APPEND__\*/\n\];",
        "const DATA=" + compact_js_array(records) + ";",
        html,
        flags=re.S,
    )
    return html


def inject_language_switcher(html: str, locale: str) -> str:
    html = html.replace(LANG_SWITCH_CSS + "\n", "")
    html = re.sub(r"\s*<nav class=\"language-switcher\" aria-label=\"Language\">.*?</nav>\n?", "\n", html, flags=re.S)
    html = html.replace("</style>", LANG_SWITCH_CSS + "\n</style>")
    html = html.replace('<div class="tagline">', LANG_SWITCH_HTML + "\n        <div class=\"tagline\">", 1)
    active_label = {
        "zh-TW": "繁中",
        "zh-CN": "简中",
        "en": "English",
        "ja": "日本語",
    }[locale]
    html = html.replace(f">{active_label}</a>", f' aria-current="page">{active_label}</a>')
    return html


def apply_static_replacements(html: str, locale: str, zh_cn: Callable[[str], str]) -> str:
    if locale == "zh-TW":
        return html
    if locale == "zh-CN":
        html = zh_cn(html)
        html = html.replace('<html lang="zh-Hant">', '<html lang="zh-Hans">')
        html = html.replace("index.zh-cn.html", "index.zh-CN.html")
        return html
    for source, target in STATIC_REPLACEMENTS.get(locale, {}).items():
        html = html.replace(source, target)
    for source, target in MANUAL_TERMS.get(locale, {}).items():
        html = html.replace(f'"{source}"', f'"{target}"')
        html = html.replace(f"'{source}'", f"'{target}'")
        html = html.replace(f">{source}<", f">{target}<")
    for source, target in STATIC_REPLACEMENTS.get(locale, {}).items():
        html = html.replace(source, target)
    return html


def localize_runtime_blocks(html: str, locale: str) -> str:
    if locale in ("en", "ja"):
        html = re.sub(r"const GROUP_ZH_OVERRIDES=\{.*?\};", "const GROUP_ZH_OVERRIDES={};", html, flags=re.S)
        html = re.sub(r"const OPTION_ZH_OVERRIDES=\{.*?\};", "const OPTION_ZH_OVERRIDES={};", html, flags=re.S)
        html = re.sub(r"const TECH_GLOSSARY=\[.*?\];", TECH_GLOSSARY_JS[locale], html, flags=re.S)
        html = re.sub(
            r"function advantage\(r\)\{.*?\n\}\nconst GROUP_ZH_OVERRIDES",
            ADVANTAGE_JS[locale] + "\nconst GROUP_ZH_OVERRIDES",
            html,
            flags=re.S,
        )
        html = re.sub(
            r"function promptFor\(r\)\{.*?\n\}\nasync function copyText",
            PROMPT_FOR_JS[locale] + "\nasync function copyText",
            html,
            flags=re.S,
        )
    if locale == "en":
        columns = json.dumps(CSV_HEADERS["en"][:-1], ensure_ascii=False)
        html = re.sub(
            r'const columns=\[.*?\];',
            f"const columns={columns};",
            html,
            flags=re.S,
        )
    elif locale == "ja":
        columns = json.dumps(CSV_HEADERS["ja"][:-1], ensure_ascii=False)
        html = re.sub(
            r'const columns=\[.*?\];',
            f"const columns={columns};",
            html,
            flags=re.S,
        )
    return html


def generate_html(template: str, records: list[dict], locale: str, zh_cn: Callable[[str], str]) -> str:
    html = replace_data_block(template, records)
    html = inject_language_switcher(html, locale)
    html = localize_runtime_blocks(html, locale)
    html = apply_static_replacements(html, locale, zh_cn)
    download_name = {
        "zh-TW": "技能與連結器_完整繁中對照表.csv",
        "zh-CN": "技能与连接器_完整简中对照表.csv",
        "en": "skills-and-connectors_en.csv",
        "ja": "skills-and-connectors_ja.csv",
    }[locale]
    html = re.sub(r'a\.download="[^"]+";', f'a.download="{download_name}";', html)
    return html


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--no-network", action="store_true", help="Do not call machine translation service.")
    args = parser.parse_args()

    records = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    template = TEMPLATE_PATH.read_text(encoding="utf-8")
    cache = load_cache()
    zh_cn = opencc_converter()

    texts = collect_texts(records)
    use_network = not args.no_network
    if use_network:
        translate_many(texts, "en", cache, use_network=True)
        translate_many(texts, "ja", cache, use_network=True)

    for locale in LOCALES:
        localized = localize_records(records, locale, cache, zh_cn)
        suffix = {"zh-TW": "zh-TW", "zh-CN": "zh-CN", "en": "en", "ja": "ja"}[locale]
        write_json(ROOT / "data" / f"skills-and-connectors.{suffix}.json", localized)
        write_csv(ROOT / "data" / f"skills-and-connectors.{suffix}.csv", localized, locale)
        html = generate_html(template, localized, locale, zh_cn)
        (ROOT / HTML_FILES[locale]).write_text(html, encoding="utf-8")
        print(f"[i18n] wrote {HTML_FILES[locale]} and data locale {suffix}")


if __name__ == "__main__":
    main()
