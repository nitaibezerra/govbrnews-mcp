# Configuração do MCP no Claude Code

## Como Configurar

Claude Code suporta servidores MCP através de configuração JSON.

### Opção 1: Configuração Global

Criar/editar arquivo de configuração do Claude Code:

**Localização:**
- macOS: `~/Library/Application Support/Claude/claude_code_config.json`
- Linux: `~/.config/Claude/claude_code_config.json`
- Windows: `%APPDATA%\Claude\claude_code_config.json`

**Conteúdo:**
```json
{
  "mcpServers": {
    "govbrnews": {
      "command": "python3.12",
      "args": ["-m", "govbrnews_mcp"],
      "cwd": "/Users/nitai/Dropbox/dev-mgi/govbrnews-mcp",
      "env": {
        "PYTHONPATH": "/Users/nitai/Dropbox/dev-mgi/govbrnews-mcp/src",
        "TYPESENSE_HOST": "localhost",
        "TYPESENSE_PORT": "8108",
        "TYPESENSE_API_KEY": "govbrnews_api_key_change_in_production"
      }
    }
  }
}
```

### Opção 2: Via Poetry (Recomendado)

```json
{
  "mcpServers": {
    "govbrnews": {
      "command": "/opt/homebrew/bin/poetry",
      "args": ["run", "python", "-m", "govbrnews_mcp"],
      "cwd": "/Users/nitai/Dropbox/dev-mgi/govbrnews-mcp"
    }
  }
}
```

**Nota:** O Poetry já carrega as variáveis de ambiente do `.env` automaticamente.

### Opção 3: Script Wrapper

Criar um script wrapper:

**Arquivo:** `/Users/nitai/Dropbox/dev-mgi/govbrnews-mcp/run-mcp.sh`
```bash
#!/bin/bash
cd /Users/nitai/Dropbox/dev-mgi/govbrnews-mcp
exec poetry run python -m govbrnews_mcp
```

**Tornar executável:**
```bash
chmod +x /Users/nitai/Dropbox/dev-mgi/govbrnews-mcp/run-mcp.sh
```

**Config:**
```json
{
  "mcpServers": {
    "govbrnews": {
      "command": "/Users/nitai/Dropbox/dev-mgi/govbrnews-mcp/run-mcp.sh"
    }
  }
}
```

## Testando a Configuração

### 1. Verificar que Typesense está rodando
```bash
curl http://localhost:8108/health
```

### 2. Testar servidor MCP manualmente
```bash
cd /Users/nitai/Dropbox/dev-mgi/govbrnews-mcp
poetry run python -m govbrnews_mcp
```

Deve esperar por input via STDIN (protocolo MCP).

### 3. Reiniciar Claude Code

Após adicionar a configuração, reinicie o Claude Code para carregar o servidor MCP.

### 4. Verificar no Claude Code

Após reiniciar, o servidor MCP "govbrnews" deve aparecer na lista de servidores disponíveis.

## Exemplos de Uso no Claude Code

Uma vez configurado, você pode usar conversacionalmente:

**Exemplo 1:**
```
Você: Busque notícias sobre educação
Claude: [usa automaticamente search_news tool]
```

**Exemplo 2:**
```
Você: Mostre as últimas 10 notícias sobre tecnologia
Claude: [usa search_news com query="tecnologia", sort="newest", limit=10]
```

**Exemplo 3:**
```
Você: Busque notícias do Ministério da Saúde sobre vacinas em 2024
Claude: [usa search_news com filtros apropriados]
```

## Troubleshooting

### Servidor não aparece

1. Verificar logs do Claude Code
2. Verificar que o comando está correto
3. Testar o comando manualmente no terminal

### Erro de conexão

1. Verificar que Typesense está rodando
2. Verificar variáveis de ambiente
3. Verificar logs do servidor MCP

### Timeout

1. Aumentar timeout na configuração (se disponível)
2. Verificar performance do Typesense

## Logs

Logs do servidor MCP são escritos para:
- stdout/stderr do processo
- Podem ser capturados redirecionando para arquivo

**Exemplo com logging:**
```json
{
  "mcpServers": {
    "govbrnews": {
      "command": "poetry",
      "args": ["run", "python", "-m", "govbrnews_mcp"],
      "cwd": "/Users/nitai/Dropbox/dev-mgi/govbrnews-mcp",
      "env": {
        "LOG_LEVEL": "DEBUG"
      }
    }
  }
}
```
