# GovBRNews MCP Server

Servidor MCP (Model Context Protocol) para buscar notícias governamentais brasileiras via Typesense.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Visão Geral

Este projeto expõe o dataset [govbrnews](https://huggingface.co/datasets/nitaibezerra/govbrnews) através de um servidor MCP, permitindo que LLMs como Claude acessem e busquem notícias governamentais brasileiras de forma natural e conversacional.

### Recursos

- 🔍 **Busca inteligente** em 295k+ notícias governamentais
- 📊 **Agregações e estatísticas** por agência, tema, período
- 🏷️ **Filtros avançados** por ano, agência, categoria, tema
- ⚡ **Respostas rápidas** (< 100ms) via Typesense
- 🤖 **Integração nativa** com Claude Desktop e outros clients MCP

## Pré-requisitos

1. **Typesense Server** rodando com o dataset govbrnews
   ```bash
   cd /path/to/govbrnews/docker-typesense
   ./run-typesense-server.sh
   ```

2. **Python 3.9+**

## Instalação

### Via Poetry (Desenvolvimento)

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/govbrnews-mcp.git
cd govbrnews-mcp

# Instale dependências
poetry install

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env com suas credenciais
```

### Via pip (Produção)

```bash
pip install govbrnews-mcp
```

## Configuração

### 1. Variáveis de Ambiente

Crie um arquivo `.env` baseado em `.env.example`:

```bash
TYPESENSE_HOST=localhost
TYPESENSE_PORT=8108
TYPESENSE_PROTOCOL=http
TYPESENSE_API_KEY=govbrnews_api_key_change_in_production
CACHE_TTL=300
LOG_LEVEL=INFO
```

### 2. Claude Desktop

Adicione ao arquivo de configuração do Claude Desktop:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "govbrnews": {
      "command": "govbrnews-mcp",
      "env": {
        "TYPESENSE_HOST": "localhost",
        "TYPESENSE_PORT": "8108",
        "TYPESENSE_API_KEY": "govbrnews_api_key_change_in_production"
      }
    }
  }
}
```

## Uso

### Tools Disponíveis

#### `search_news` - Buscar Notícias ✅

Busca inteligente com filtros avançados no dataset completo.

```
Busque notícias sobre educação publicadas pelo MEC em 2024
```

**Parâmetros:**
- `query` (obrigatório): Termos de busca
- `agencies`: Lista de agências para filtrar
- `year_from` / `year_to`: Filtro de período
- `themes`: Lista de temas
- `limit`: Máximo de resultados (1-100, padrão: 10)
- `sort`: "relevant", "newest", "oldest"

#### `get_facets` - Agregações e Estatísticas ✅

Obtenha agregações por campos específicos para análises estatísticas.

```
Mostre quantas notícias cada agência publicou sobre educação
```

**Parâmetros:**
- `facet_fields` (obrigatório): Lista de campos ("agency", "published_year", "theme_1_level_1", "category")
- `query`: Query opcional para filtrar (padrão: "*")
- `max_values`: Máximo de valores por facet (1-100, padrão: 20)

**Casos de uso:**
- Distribuição de notícias por agência
- Volume de publicações por ano
- Temas mais cobertos em um assunto
- Categorias mais comuns

#### `similar_news` - Notícias Similares ✅

Encontre notícias similares a uma notícia de referência.

```
Encontre notícias similares à notícia com ID 254647
```

**Parâmetros:**
- `reference_id` (obrigatório): ID da notícia de referência
- `limit`: Máximo de notícias similares (1-20, padrão: 5)

**Critério de similaridade:**
- Mesma agência governamental
- Mesmo tema principal
- Período temporal próximo

#### `analyze_temporal` - Análise Temporal com Granularidade Configurável ✅

Analise distribuição temporal de notícias com três níveis de granularidade.

```
Mostre a evolução mensal de notícias sobre educação em 2025
```

**Parâmetros:**
- `query` (obrigatório): Termo de busca
- `granularity`: "yearly", "monthly" (recomendado), ou "weekly"
- `year_from` / `year_to`: Filtro de período (opcional)
- `max_periods`: Máximo de períodos (padrão: 24)

**Granularidades:**
- **yearly**: Distribuição anual (máx 50 anos) - Para tendências de longo prazo
- **monthly**: Distribuição mensal (máx 60 meses) - **RECOMENDADO** - Balance ideal
- **weekly**: Distribuição semanal (máx 52 semanas) - Para análises recentes

**Casos de uso:**
- Identificar tendências e padrões temporais
- Detectar sazonalidade
- Analisar impacto de eventos específicos
- Comparar períodos

### Prompts Disponíveis ✅

Prompts são análises guiadas que combinam múltiplos tools automaticamente para criar insights profundos.

#### `analyze_theme` - Análise Completa de Tema

Análise multidimensional de um tema específico, incluindo volume, evolução temporal, principais agências, temas relacionados e notícias mais relevantes.

```
Analise completamente o tema "educação"
```

#### `compare_agencies` - Comparação Entre Agências

Comparação detalhada entre 2+ agências governamentais, analisando volumes, distribuição temporal, temas, e diferenças de cobertura.

```
Compare MEC e INEP
Compare MMA, IBAMA e ICMBio sobre meio ambiente
```

#### `temporal_evolution` - Evolução Temporal Multiescala

Análise temporal profunda combinando três granularidades (anual, mensal, semanal) para entender trajetória completa de um tema.

```
Mostre a evolução de "COP30" ao longo do tempo
Evolução de "educação" de 2020 a 2025
```

#### `discover_context` - Descoberta Contextual de Notícia

Investigação contextual profunda em torno de uma notícia específica, incluindo notícias similares, histórico do tema, e panorama temporal.

```
Me explique o contexto da notícia 5043214
```

### Resources Disponíveis ✅

Resources fornecem acesso direto a dados estruturados e estatísticas.

#### `govbrnews://stats`
Estatísticas gerais do dataset, incluindo:
- Total de documentos
- Distribuição por ano
- Top 5 agências
- Período de cobertura

#### `govbrnews://agencies`
Lista completa de agências governamentais com contagens de notícias, ordenada por volume de publicações.

#### `govbrnews://themes`
Taxonomia completa de temas com contagens, útil para entender a distribuição de conteúdo.

#### `govbrnews://news/{id}`
Notícia individual completa com todos os metadados (título, conteúdo, agência, data, categoria, tema, URL).


## Exemplos de Uso

### Busca Simples

```
Usuário: Busque notícias sobre mudanças climáticas
Claude: [usa tool search_news com query="mudanças climáticas"]
```

### Busca com Filtros

```
Usuário: Notícias do Ministério da Saúde sobre vacinas em 2024
Claude: [usa tool search_news com:
  query="vacinas",
  agencies=["Ministério da Saúde"],
  year_from=2024
]
```

### Análise Temporal

```
Usuário: Compare a cobertura de tecnologia entre 2023 e 2024
Claude: [usa get_facets para obter contagens por ano]
```

## Desenvolvimento

### Setup

```bash
# Instalar dependências de desenvolvimento
poetry install --with dev

# Criar .env
cp .env.example .env

# Rodar testes
poetry run pytest

# Formatar código
poetry run black src/ tests/
poetry run ruff check src/ tests/
```

### Estrutura do Projeto

```
govbrnews-mcp/
├── src/govbrnews_mcp/
│   ├── server.py              # Entry point FastMCP
│   ├── config.py              # Configurações
│   ├── typesense_client.py    # Cliente Typesense
│   ├── tools/                 # MCP Tools
│   ├── resources/             # MCP Resources
│   ├── prompts/               # Prompt templates
│   └── utils/                 # Utilidades
├── tests/                     # Testes
└── docs/                      # Documentação
```

## Documentação

- [Guia de Uso Completo](docs/USAGE.md)
- [Guia de Desenvolvimento](docs/DEVELOPMENT.md)
- [Dataset GovBRNews](https://huggingface.co/datasets/nitaibezerra/govbrnews)
- [Model Context Protocol](https://modelcontextprotocol.io/)

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## Suporte

Para questões ou suporte:
- Abra uma [issue](https://github.com/seu-usuario/govbrnews-mcp/issues)
- Consulte a [documentação](docs/)
- Email: nitaibezerra@protonmail.com

## Acknowledgments

- Dataset: [govbrnews](https://huggingface.co/datasets/nitaibezerra/govbrnews)
- Search Engine: [Typesense](https://typesense.org/)
- Protocol: [Model Context Protocol](https://modelcontextprotocol.io/)
- Framework: [FastMCP](https://github.com/jlowin/fastmcp)
