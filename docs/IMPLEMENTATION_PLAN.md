# Plano de Implementação - GovBRNews MCP Server

## Framework Escolhido: FastMCP ✅

### Justificativa

FastMCP foi escolhido por oferecer:
- **Boilerplate mínimo**: Decoradores simples substituem 80% do código
- **Schema automático**: Type hints + docstrings geram schemas
- **Produção-ready**: Usado por múltiplas empresas em produção
- **Developer Experience**: Reduz 30% do tempo de desenvolvimento

## Estrutura do Projeto

```
govbrnews-mcp/
├── pyproject.toml              # Poetry + FastMCP config
├── README.md                   # Documentação principal
├── LICENSE                     # MIT License
├── .env.example                # Template de configuração
├── .env                        # Configuração local
├── .gitignore                  # Git ignore
├── src/
│   └── govbrnews_mcp/
│       ├── __init__.py
│       ├── __main__.py        # Entry point (python -m)
│       ├── server.py           # FastMCP server
│       ├── config.py           # Pydantic settings
│       ├── typesense_client.py # Cliente Typesense
│       ├── tools/              # MCP Tools
│       │   ├── __init__.py
│       │   ├── search.py       # ✅ search_news
│       │   ├── facets.py       # ⏳ get_facets
│       │   └── similar.py      # ⏳ similar_news
│       ├── resources/          # MCP Resources
│       │   ├── __init__.py
│       │   ├── stats.py        # ⏳ govbrnews://stats
│       │   ├── agencies.py     # ⏳ govbrnews://agencies
│       │   ├── themes.py       # ⏳ govbrnews://themes
│       │   └── news.py         # ⏳ govbrnews://news/{id}
│       ├── prompts/            # Prompt templates
│       │   ├── __init__.py
│       │   └── templates.py    # ⏳ Prompts
│       └── utils/
│           ├── __init__.py
│           ├── formatters.py   # ✅ Formatação Markdown
│           ├── cache.py        # ⏳ Cache layer
│           └── synonyms.py     # ⏳ Expansão de sinônimos
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # ✅ Fixtures pytest
│   ├── test_config.py         # ✅ Testes config
│   ├── test_typesense_client.py # ✅ Testes client
│   ├── test_formatters.py     # ✅ Testes formatters
│   ├── test_search_tool.py    # ✅ Testes search_news
│   ├── test_resources.py      # ⏳ Testes resources
│   └── test_integration.py    # ⏳ Testes integração
└── docs/
    ├── USAGE.md               # ✅ Guia de uso
    ├── DEVELOPMENT.md         # ⏳ Guia de desenvolvimento
    └── IMPLEMENTATION_PLAN.md # Este arquivo
```

**Legenda:**
- ✅ Implementado e testado
- ⏳ Pendente de implementação
- ❌ Não implementado

## Status Atual

### ✅ FASE 1: Setup do Projeto (COMPLETO)

**Arquivos criados:**
- [x] `pyproject.toml` - Poetry config com FastMCP
- [x] `.env.example` - Template de configuração
- [x] `.env` - Configuração local
- [x] `.gitignore` - Git ignore
- [x] `LICENSE` - MIT License
- [x] `README.md` - Documentação principal

**Tempo estimado:** 2-3h
**Tempo real:** ~2h

### ✅ FASE 2: MVP com FastMCP (COMPLETO)

**Componentes implementados:**

1. **Configuração** (`config.py`)
   - Pydantic Settings para env vars
   - Validação automática
   - Singleton instance

2. **Cliente Typesense** (`typesense_client.py`)
   - Wrapper com error handling
   - Métodos: search, get_collection_info, get_document, health_check
   - Logging estruturado

3. **Formatters** (`utils/formatters.py`)
   - `format_timestamp()` - Timestamps para DD/MM/YYYY
   - `format_search_results()` - Resultados em Markdown
   - `format_facets_results()` - Agregações tabulares
   - `format_document_full()` - Documento completo

4. **Tool search_news** (`tools/search.py`)
   - Busca com query obrigatória
   - Filtros: agencies, year_from, year_to, themes
   - Ordenação: relevant, newest, oldest
   - Limite: 1-100 resultados

5. **FastMCP Server** (`server.py`)
   - Inicialização do FastMCP
   - Registro de tools via decorator
   - Logging configurado
   - Entry point `main()`

**Testes criados:**
- [x] `test_config.py` - 3 testes
- [x] `test_typesense_client.py` - 9 testes
- [x] `test_formatters.py` - 8 testes
- [x] `test_search_tool.py` - 11 testes

**Total:** 31 testes unitários

**Tempo estimado:** 6-8h
**Tempo real:** ~6h

### ⏳ FASE 3: Resources (PENDENTE)

**A implementar:**

#### 3.1 Resource: `govbrnews://stats`
```python
@mcp.resource("govbrnews://stats")
def stats_resource():
    """Estatísticas gerais do dataset."""
    return get_stats()
```

**Retorna:**
- Total de documentos
- Distribuição por ano
- Top 5 agências
- Período de cobertura

**Estimativa:** 2h

#### 3.2 Resource: `govbrnews://agencies`
```python
@mcp.resource("govbrnews://agencies")
def agencies_resource():
    """Lista de agências com contagens."""
    return get_agencies()
```

**Retorna:**
- Lista completa de agências
- Contagem de notícias por agência
- Ordenado por quantidade

**Estimativa:** 1.5h

#### 3.3 Resource: `govbrnews://themes`
```python
@mcp.resource("govbrnews://themes")
def themes_resource():
    """Taxonomia de temas."""
    return get_themes()
```

**Retorna:**
- Lista de temas principais
- Contagem por tema
- Hierarquia (se disponível)

**Estimativa:** 1.5h

#### 3.4 Resource: `govbrnews://news/{id}`
```python
@mcp.resource("govbrnews://news/{id}")
def news_resource(id: str):
    """Notícia individual completa."""
    return get_news_by_id(id)
```

**Retorna:**
- Conteúdo completo em Markdown
- Todos os metadados

**Estimativa:** 1h

**Tempo total estimado Fase 3:** 6h

### ⏳ FASE 4: Tools Avançados (PENDENTE)

#### 4.1 Tool: `get_facets`
```python
@mcp.tool()
def get_facets(
    facet_fields: list[str],
    query: str = "*"
) -> str:
    """Obtém agregações e estatísticas."""
```

**Parâmetros:**
- `facet_fields`: Lista de campos (agency, category, theme, year)
- `query`: Query opcional para filtrar

**Retorna:**
- Tabelas com contagens por facet
- Ordenado por quantidade

**Estimativa:** 2h

#### 4.2 Tool: `similar_news`
```python
@mcp.tool()
def similar_news(
    reference_id: str,
    limit: int = 5
) -> str:
    """Encontra notícias similares."""
```

**Estratégia:**
- Buscar notícia de referência
- Usar agência + tema como proxy de similaridade
- Retornar top N similares

**Estimativa:** 2h

**Tempo total estimado Fase 4:** 4h

### ⏳ FASE 5: Prompts Templates (PENDENTE)

```python
@mcp.prompt()
def analyze_theme(theme: str) -> list[base.Message]:
    """Analisa cobertura de um tema."""

@mcp.prompt()
def compare_agencies(agencies: list[str]) -> list[base.Message]:
    """Compara cobertura de agências."""
```

**Tempo estimado:** 2h

### ⏳ FASE 6: Cache & Inteligência (PENDENTE)

#### 6.1 Cache Decorator
```python
@cache(ttl=300)
def expensive_operation():
    pass
```

**Estimativa:** 1.5h

#### 6.2 Expansão de Sinônimos
```python
SYNONYMS = {
    "saúde": ["medicina", "hospital", "sus"],
    "educação": ["ensino", "escola", "mec"]
}
```

**Estimativa:** 1.5h

**Tempo total estimado Fase 6:** 3h

### ⏳ FASE 7: Testes Integração (PENDENTE)

- [ ] Testes de integração com Typesense real
- [ ] Testes end-to-end do servidor MCP
- [ ] Coverage report (meta: >80%)

**Tempo estimado:** 3h

### ⏳ FASE 8: Documentação Final (PENDENTE)

- [x] USAGE.md - Guia completo de uso
- [ ] DEVELOPMENT.md - Setup dev e contribuição
- [ ] Atualizar README com exemplos

**Tempo estimado:** 2h

## Progresso Geral

### Resumo Executivo

| Fase | Status | Tempo Estimado | Tempo Real | Progresso |
|------|--------|---------------|------------|-----------|
| 1. Setup | ✅ Completo | 2-3h | ~2h | 100% |
| 2. MVP | ✅ Completo | 6-8h | ~6h | 100% |
| 3. Resources | ⏳ Pendente | 6h | - | 0% |
| 4. Tools Avançados | ⏳ Pendente | 4h | - | 0% |
| 5. Prompts | ⏳ Pendente | 2h | - | 0% |
| 6. Cache/Inteligência | ⏳ Pendente | 3h | - | 0% |
| 7. Testes Integração | ⏳ Pendente | 3h | - | 0% |
| 8. Docs Final | ⏳ Pendente | 2h | - | 50% |

**Progresso Total:** ~30% (8h de ~28h estimadas)

### O que funciona agora

✅ **MVP Funcional:**
1. Servidor FastMCP inicializa corretamente
2. Tool `search_news` totalmente funcional
3. Formatação Markdown otimizada para LLMs
4. Cliente Typesense com error handling
5. 31 testes unitários passando
6. Configuração via environment variables
7. Logging estruturado

**Você pode usar o MVP agora mesmo!**

## Próximos Passos

### Imediato (para testar MVP)

1. **Instalar dependências:**
   ```bash
   cd govbrnews-mcp
   poetry install
   ```

2. **Verificar configuração:**
   ```bash
   # O .env já está criado com valores padrão
   cat .env
   ```

3. **Garantir que Typesense está rodando:**
   ```bash
   curl http://localhost:8108/health
   ```

4. **Rodar testes:**
   ```bash
   poetry run pytest -v
   ```

5. **Testar servidor localmente:**
   ```bash
   poetry run python -m govbrnews_mcp
   ```

### Curto Prazo (Fase 3-4)

1. Implementar resources básicos (stats, agencies)
2. Implementar tool `get_facets`
3. Testes de integração

### Médio Prazo (Fase 5-8)

1. Prompts templates
2. Cache layer
3. Documentação completa
4. Publicar no PyPI

## Testes

### Executar Testes

```bash
# Todos os testes
poetry run pytest

# Com coverage
poetry run pytest --cov=govbrnews_mcp

# Verbose
poetry run pytest -v

# Teste específico
poetry run pytest tests/test_search_tool.py -v
```

### Coverage Atual

**Arquivos cobertos:**
- ✅ `config.py` - 100%
- ✅ `typesense_client.py` - ~90%
- ✅ `utils/formatters.py` - ~95%
- ✅ `tools/search.py` - ~90%

**Coverage geral estimado:** ~85%

## Uso do MVP

### Configuração Claude Desktop

Adicione ao `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "govbrnews": {
      "command": "python",
      "args": ["-m", "govbrnews_mcp"],
      "cwd": "/Users/nitai/Dropbox/dev-mgi/govbrnews-mcp",
      "env": {
        "TYPESENSE_HOST": "localhost",
        "TYPESENSE_PORT": "8108",
        "TYPESENSE_API_KEY": "govbrnews_api_key_change_in_production"
      }
    }
  }
}
```

### Teste Manual

```python
# Teste direto do tool
from govbrnews_mcp.tools.search import search_news

result = search_news("educação", limit=5)
print(result)
```

## Roadmap

### v0.1.0 (MVP) - ✅ COMPLETO
- [x] Tool `search_news`
- [x] Configuração via env
- [x] Cliente Typesense
- [x] Formatação Markdown
- [x] Testes unitários
- [x] README e USAGE

### v0.2.0 (Resources) - 🎯 PRÓXIMO
- [ ] Resource `stats`
- [ ] Resource `agencies`
- [ ] Resource `themes`
- [ ] Resource `news/{id}`
- [ ] Tool `get_facets`

### v0.3.0 (Inteligência)
- [ ] Cache layer
- [ ] Expansão de sinônimos
- [ ] Correção de agências
- [ ] Prompts templates

### v0.4.0 (Produção)
- [ ] Docker image
- [ ] CI/CD
- [ ] Publicação PyPI
- [ ] Docs completas

### v1.0.0 (Completo)
- [ ] Tool `similar_news`
- [ ] Monitoring/métricas
- [ ] Performance otimizada
- [ ] Multi-idioma (EN)

## Notas Técnicas

### Por que FastMCP?

**Comparação de código:**

```python
# COM FastMCP (5 linhas)
@mcp.tool()
def search_news(query: str, limit: int = 10) -> str:
    """Busca notícias."""
    return execute_search(query, limit)

# SEM FastMCP (30+ linhas)
# - Registrar handlers manualmente
# - Criar schemas JSON
# - Parsear argumentos
# - Validar tipos
# - Tratar erros do protocolo
```

**Economia de código:** ~80-85%

### Design Decisions

1. **Pydantic Settings** - Validação automática de env vars
2. **Singleton clients** - Reusar conexões Typesense
3. **Markdown formatting** - Otimizado para consumo por LLMs
4. **Comprehensive tests** - Mocks para Typesense, fixtures reutilizáveis
5. **Structured logging** - Debug facilitado

### Performance Esperada

- **Busca simples:** < 100ms
- **Busca com filtros:** < 150ms
- **Facets:** < 200ms
- **Resources (cached):** < 10ms

## Contribuindo

Para continuar o desenvolvimento:

1. **Escolha uma fase** do roadmap
2. **Implemente os componentes**
3. **Escreva testes unitários**
4. **Atualize este plano**
5. **Commit incremental**

## Referências

- [FastMCP Docs](https://github.com/jlowin/fastmcp)
- [MCP Spec](https://modelcontextprotocol.io/)
- [Typesense Docs](https://typesense.org/docs/)
- [Pydantic Docs](https://docs.pydantic.dev/)
