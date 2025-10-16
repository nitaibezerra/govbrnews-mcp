# Configuração do MCP Server no Claude Code

## Status da Configuração

✅ **Concluído** - O servidor MCP foi configurado e está pronto para uso no Claude Code.

## Arquivos de Configuração

### 1. Claude Code Config
**Localização:** `~/Library/Application Support/Claude/claude_code_config.json`

**Conteúdo:**
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

### 2. Correções Aplicadas

#### server.py
Removido o parâmetro `version` que não é suportado pelo FastMCP:

**Antes:**
```python
mcp = FastMCP(
    name="GovBRNews",
    version="0.1.0",
)
```

**Depois:**
```python
mcp = FastMCP(
    name="GovBRNews",
)
```

## Verificações Realizadas

### ✅ Typesense Container
```bash
docker ps --filter "name=typesense"
```
**Status:** Running (Up 11 minutes, Port 8108 exposed)

### ✅ Typesense Health
```bash
curl http://localhost:8108/health
```
**Resposta:** `{"ok":true}`

### ✅ MCP Server Startup
```bash
poetry run python -m govbrnews_mcp
```
**Log de inicialização:**
```
2025-10-17 00:03:43,124 - govbrnews_mcp.server - INFO - Initializing GovBRNews MCP Server
2025-10-17 00:03:43,125 - govbrnews_mcp.server - INFO - Registered tools: search_news
2025-10-17 00:03:43,125 - govbrnews_mcp.server - INFO - Starting GovBRNews MCP Server...
2025-10-17 00:03:43,125 - govbrnews_mcp.server - INFO - Typesense endpoint: http://localhost:8108
```

## Como Testar no Claude Code

### 1. Reiniciar Claude Code
Após criar o arquivo de configuração, **você precisa reiniciar completamente o Claude Code** para que ele carregue o servidor MCP.

### 2. Verificar se o Servidor foi Carregado
Após reiniciar, o Claude Code deve:
- Detectar automaticamente o servidor "govbrnews"
- Iniciar o processo via Poetry
- Conectar-se ao servidor MCP via protocolo STDIO

### 3. Testar Conversacionalmente

#### Exemplo 1: Busca Simples
```
Você: Busque notícias sobre educação
```
**Esperado:** Claude Code deve automaticamente usar a tool `search_news` e retornar notícias formatadas em Markdown.

#### Exemplo 2: Busca com Filtros
```
Você: Mostre as últimas 10 notícias sobre tecnologia do Ministério da Ciência e Tecnologia
```
**Esperado:** Claude Code deve usar `search_news` com:
- `query="tecnologia"`
- `agencies=["Ministério da Ciência e Tecnologia"]`
- `sort="newest"`
- `limit=10`

#### Exemplo 3: Busca com Período
```
Você: Busque notícias sobre vacinas em 2024
```
**Esperado:** Claude Code deve usar `search_news` com:
- `query="vacinas"`
- `year_from=2024`
- `year_to=2024`

#### Exemplo 4: Busca Complexa
```
Você: Encontre notícias sobre educação do MEC publicadas entre 2023 e 2024, ordenadas pelas mais recentes, limite 20 resultados
```
**Esperado:** Claude Code deve usar `search_news` com todos os parâmetros apropriados.

## Troubleshooting

### Servidor não aparece após reiniciar
1. **Verificar logs do Claude Code**
   - Procure por mensagens de erro relacionadas ao MCP
   - Verificar se o caminho do Poetry está correto

2. **Testar comando manualmente**
   ```bash
   cd /Users/nitai/Dropbox/dev-mgi/govbrnews-mcp
   /opt/homebrew/bin/poetry run python -m govbrnews_mcp
   ```
   Se funcionar, o problema está na configuração do Claude Code.

3. **Verificar que o .env existe**
   ```bash
   ls -la /Users/nitai/Dropbox/dev-mgi/govbrnews-mcp/.env
   ```
   O Poetry carrega automaticamente as variáveis de ambiente do `.env`.

### Erro de conexão com Typesense
1. **Verificar que Typesense está rodando**
   ```bash
   docker ps --filter "name=typesense"
   curl http://localhost:8108/health
   ```

2. **Verificar variáveis de ambiente no .env**
   ```bash
   cat /Users/nitai/Dropbox/dev-mgi/govbrnews-mcp/.env
   ```
   Deve conter:
   ```
   TYPESENSE_HOST=localhost
   TYPESENSE_PORT=8108
   TYPESENSE_API_KEY=govbrnews_api_key_change_in_production
   ```

### Tool não é chamada automaticamente
- Certifique-se de fazer perguntas naturais que indicam busca por notícias
- Claude Code decide automaticamente quando usar a tool baseado no contexto
- Você pode ser explícito: "Use a ferramenta de busca para encontrar..."

## Logs do Servidor MCP

### Onde encontrar logs
Os logs do servidor MCP são gerenciados pelo Claude Code. Quando o servidor é iniciado via Claude Code:
- stdout/stderr são capturados pelo Claude Code
- Logs aparecem no console de desenvolvedor do Claude Code (se disponível)

### Aumentar verbosidade
Para mais detalhes, você pode adicionar `LOG_LEVEL=DEBUG` no `.env`:
```bash
echo "LOG_LEVEL=DEBUG" >> /Users/nitai/Dropbox/dev-mgi/govbrnews-mcp/.env
```

Depois reinicie o Claude Code.

## Dataset Disponível

- **Total de documentos:** 295,511 notícias
- **Período:** Anos variados (filtráveis via `year_from`, `year_to`)
- **Agências:** Diversos ministérios e órgãos governamentais
- **Temas:** Classificação temática em múltiplos níveis
- **Campos indexados:** `title`, `content` (busca textual completa)

## Próximos Passos

Após testar no Claude Code:
1. Validar que as respostas são relevantes e bem formatadas
2. Testar diferentes tipos de consultas (simples, complexas, com filtros)
3. Verificar performance e tempo de resposta
4. Considerar implementar recursos adicionais (Phase 3 do plano original):
   - Resources para acesso direto a notícias específicas
   - Prompts pré-configurados para casos de uso comuns
   - Cache mais agressivo se necessário

## Referências

- **Documentação MCP:** [MCP_CONFIG_CLAUDE_CODE.md](MCP_CONFIG_CLAUDE_CODE.md)
- **Status da Implementação:** [STATUS.md](STATUS.md)
- **Resultados dos Testes:** [TEST_RESULTS_FINAL.md](TEST_RESULTS_FINAL.md)
- **Guia de Uso:** [USAGE.md](USAGE.md)
