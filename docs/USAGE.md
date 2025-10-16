# Guia de Uso - GovBRNews MCP Server

## Visão Geral

O GovBRNews MCP Server expõe o dataset de notícias governamentais brasileiras através do Model Context Protocol, permitindo que LLMs como Claude busquem e analisem notícias de forma conversacional.

## Instalação

### Pré-requisitos

1. **Servidor Typesense** com dataset GovBRNews indexado
   ```bash
   cd /path/to/govbrnews/docker-typesense
   ./run-typesense-server.sh
   ```

2. **Python 3.9+**

### Instalação via Poetry (Desenvolvimento)

```bash
git clone https://github.com/seu-usuario/govbrnews-mcp.git
cd govbrnews-mcp
poetry install
```

### Instalação via pip

```bash
pip install govbrnews-mcp
```

## Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
TYPESENSE_PROTOCOL=http
TYPESENSE_API_KEY=govbrnews_api_key_change_in_production
CACHE_TTL=300
LOG_LEVEL=INFO
```

### 2. Configuração no Claude Desktop

#### macOS
Edite: `~/Library/Application Support/Claude/claude_desktop_config.json`

#### Windows
Edite: `%APPDATA%\Claude\claude_desktop_config.json`

#### Linux
Edite: `~/.config/Claude/claude_desktop_config.json`

Adicione a configuração do servidor MCP:

```json
{
  "mcpServers": {
    "govbrnews": {
      "command": "python",
      "args": ["-m", "govbrnews_mcp"],
      "env": {
        "TYPESENSE_HOST": "localhost",
        "TYPESENSE_PORT": "8108",
        "TYPESENSE_API_KEY": "govbrnews_api_key_change_in_production"
      }
    }
  }
}
```

**Nota:** Se instalado globalmente via pip, pode usar:
```json
{
  "command": "govbrnews-mcp"
}
```

### 3. Reiniciar Claude Desktop

Após adicionar a configuração, reinicie o Claude Desktop para carregar o servidor MCP.

## Tools Disponíveis

### `search_news` - Buscar Notícias

Busca notícias governamentais brasileiras com filtros avançados.

#### Parâmetros

| Parâmetro | Tipo | Obrigatório | Descrição |
|-----------|------|-------------|-----------|
| `query` | string | Sim | Termos de busca |
| `agencies` | list[string] | Não | Filtrar por agências específicas |
| `year_from` | int | Não | Ano inicial (2018-2025) |
| `year_to` | int | Não | Ano final (2018-2025) |
| `themes` | list[string] | Não | Filtrar por temas |
| `limit` | int | Não | Máximo de resultados (1-100, padrão: 10) |
| `sort` | string | Não | "relevant", "newest", "oldest" (padrão: "relevant") |

#### Exemplos de Uso

**Busca Simples:**
```
Usuário: Busque notícias sobre educação
Claude: [usa search_news com query="educação"]
```

**Busca com Agência:**
```
Usuário: Notícias do Ministério da Saúde sobre vacinas
Claude: [usa search_news com:
  query="vacinas",
  agencies=["Ministério da Saúde"]
]
```

**Busca com Filtro Temporal:**
```
Usuário: Notícias sobre tecnologia publicadas em 2024
Claude: [usa search_news com:
  query="tecnologia",
  year_from=2024,
  year_to=2024
]
```

**Busca Ordenada:**
```
Usuário: Mostre as 20 notícias mais recentes sobre sustentabilidade
Claude: [usa search_news com:
  query="sustentabilidade",
  sort="newest",
  limit=20
]
```

**Busca Combinada:**
```
Usuário: Notícias do MEC sobre universidades entre 2023 e 2024
Claude: [usa search_news com:
  query="universidades",
  agencies=["Ministério da Educação"],
  year_from=2023,
  year_to=2024
]
```

#### Formato de Resposta

A tool retorna resultados formatados em Markdown:

```markdown
# Resultados da Busca

**Total encontrado:** 1,234 notícias
**Mostrando:** 10 resultados

---

## 1. Título da Notícia

**Agência:** Ministério da Educação | **Publicado:** 15/03/2024 | **Categoria:** Educação | **URL:** https://...

**Resumo:**
Conteúdo da notícia...

---

## 2. Outra Notícia
...
```

## Casos de Uso

### 1. Pesquisa Exploratória

```
Usuário: O que está sendo discutido sobre mudanças climáticas no governo?
Claude: [busca "mudanças climáticas" e analisa resultados]
```

### 2. Análise Temporal

```
Usuário: Compare quantas notícias sobre educação foram publicadas em 2023 vs 2024
Claude: [faz duas buscas e compara]
```

### 3. Análise por Agência

```
Usuário: Quais são as principais iniciativas do Ministério da Saúde em 2024?
Claude: [busca filtrando por agência e ano]
```

### 4. Monitoramento de Temas

```
Usuário: Me mostre as últimas notícias sobre inteligência artificial no governo
Claude: [busca "inteligência artificial" ordenado por "newest"]
```

### 5. Pesquisa Específica

```
Usuário: Encontre notícias sobre o programa Bolsa Família
Claude: [busca "Bolsa Família" com contexto relevante]
```

## Agências Disponíveis

Principais agências governamentais no dataset:

- Ministério da Educação
- Ministério da Saúde
- Ministério da Economia
- Ministério da Justiça e Segurança Pública
- Ministério do Meio Ambiente
- Ministério da Ciência, Tecnologia e Inovações
- Ministério do Desenvolvimento Social
- Agência Brasil
- Governo Federal

## Temas Disponíveis

Principais temas de classificação:

- Educação e Cultura
- Saúde e Vigilância Sanitária
- Economia e Gestão Pública
- Ciência, Tecnologia e Inovação
- Meio Ambiente e Clima
- Trabalho e Emprego
- Desenvolvimento Social
- Segurança Pública
- Infraestrutura e Transporte

## Troubleshooting

### Erro: "Connection refused"

**Problema:** Servidor Typesense não está rodando

**Solução:**
```bash
cd /path/to/govbrnews/docker-typesense
./run-typesense-server.sh
```

### Erro: "Unauthorized"

**Problema:** API Key incorreta

**Solução:** Verifique a variável `TYPESENSE_API_KEY` no `.env` ou na configuração do Claude Desktop

### Erro: "Collection not found"

**Problema:** Dataset não foi indexado

**Solução:**
```bash
cd /path/to/govbrnews/docker-typesense
./run-typesense-server.sh refresh
```

### Servidor MCP não aparece no Claude

**Soluções:**
1. Verifique se o arquivo de configuração está no local correto
2. Verifique se o JSON está válido (sem vírgulas extras)
3. Reinicie o Claude Desktop completamente
4. Verifique os logs do Claude Desktop

**Logs do Claude Desktop:**
- macOS: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\logs\`

## Limitações

- **Limite de resultados:** Máximo de 100 notícias por busca
- **Cache:** Resultados são cacheados por 5 minutos (configurável via `CACHE_TTL`)
- **Dataset:** Notícias de 2018 a 2025 (última atualização)
- **Idioma:** Apenas português brasileiro

## Suporte

Para questões ou problemas:

1. Verifique a [documentação do MCP](https://modelcontextprotocol.io/)
2. Consulte o [README](../README.md)
3. Abra uma [issue no GitHub](https://github.com/seu-usuario/govbrnews-mcp/issues)
4. Email: nitaibezerra@protonmail.com

## Próximos Passos

- Explore outros tools (aguardando implementação):
  - `get_facets` - Agregações e estatísticas
  - `similar_news` - Notícias similares
- Recursos (resources):
  - `govbrnews://stats` - Estatísticas do dataset
  - `govbrnews://agencies` - Lista de agências
