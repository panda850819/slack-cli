# Project Context

## Purpose
Slack CLI - 命令列工具，提供 Slack workspace 的搜尋和瀏覽功能。

目標：
- 搜尋訊息（全文搜尋）
- 瀏覽頻道列表和歷史
- 瀏覽私訊列表和內容

## Tech Stack
- Language: Python 3.13+
- CLI Framework: Typer
- Output Formatting: Rich
- API Client: slack-sdk (官方 SDK)
- Config Management: python-dotenv

## Project Conventions

### Code Style
- 使用 Python type hints
- 函數和類別使用 docstrings
- 命名規範：snake_case (變數/函數)、PascalCase (類別)

### Architecture Patterns
參照 notion-cli 架構：
```
src/slack_cli/
├── main.py          # CLI 進入點 (Typer app)
├── client.py        # Slack API 封裝
├── formatters.py    # Rich 輸出格式化
└── commands/        # 子指令模組
    ├── search.py
    ├── channel.py
    └── dm.py
```

分層設計：
- Client Layer: API 通訊和錯誤處理
- Command Layer: CLI 參數解析和流程控制
- Formatter Layer: 輸出格式化

### Testing Strategy
- pytest 作為測試框架
- Mock client layer 避免實際 API 呼叫
- Formatter 測試為純函數測試

### Git Workflow
- Conventional Commits 格式
- 主分支: main

## Domain Context
- Slack Web API 提供搜尋和對話功能
- 需要 User Token (xoxp-) 或 Bot Token (xoxb-)
- User Token 可存取更多資料（包含私訊搜尋）

## Important Constraints
- 遵循 Slack API rate limits
- 敏感資料（token）不可硬編碼

## External Dependencies
- Slack Web API
- 環境變數 SLACK_CLI_TOKEN
