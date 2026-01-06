# Инструкция по настройке MCP-сервера в Cursor

## Настройка MCP-сервера Ref Tools

### Способ 1: Через настройки Cursor (рекомендуется)

1. Откройте настройки Cursor:
   - Нажмите `Ctrl+,` (или `Cmd+,` на Mac)
   - Или через меню: `File → Preferences → Settings`

2. Найдите раздел "MCP Servers" или "Model Context Protocol"

3. Добавьте новый сервер со следующими параметрами:

```json
{
  "mcpServers": {
    "ref-tools": {
      "type": "http",
      "url": "https://api.ref.tools/mcp?apiKey=ref-3cdfb06a03b1a1453713"
    }
  }
}
```

### Способ 2: Через файл конфигурации

Файл конфигурации Cursor обычно находится в:
- **Windows**: `%APPDATA%\Cursor\User\settings.json`
- **macOS**: `~/Library/Application Support/Cursor/User/settings.json`
- **Linux**: `~/.config/Cursor/User/settings.json`

Добавьте в этот файл секцию `mcpServers` с указанными выше параметрами.

### Использование JWT токена

Если ваш JWT токен нужно использовать для аутентификации, возможно потребуется добавить его в заголовки запросов. Уточните у документации Ref Tools, как именно использовать токен.

**ВНИМАНИЕ**: Не храните токены и ключи API в публичных репозиториях! Используйте переменные окружения или секреты.

