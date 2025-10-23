# Guia de Testes - Claude Code

Este guia contém exemplos de consultas para testar todas as funcionalidades do servidor MCP GovBRNews no Claude Code.

## Pré-requisitos

1. ✅ Typesense rodando (http://localhost:8108)
2. ✅ Servidor MCP configurado no Claude Code
3. ✅ Claude Code reiniciado após configuração

## Status de Verificação

**Servidor MCP:**
- 3 Tools registrados: search_news, get_facets, similar_news
- 4 Resources registrados: stats, agencies, themes, news/{id}
- Typesense endpoint: http://localhost:8108

---

## 1. Testes de Tools

### Tool 1: `search_news` (Busca Textual)

#### Teste 1.1: Busca Simples
```
Busque notícias sobre educação
```

**Esperado:**
- Claude usa automaticamente `search_news`
- Retorna ~10 notícias sobre educação
- Formatação em Markdown com título, agência, data, resumo

#### Teste 1.2: Busca com Filtros
```
Mostre as últimas 5 notícias sobre saúde do Ministério da Saúde publicadas em 2025
```

**Esperado:**
- Usa `search_news` com:
  - query="saúde"
  - agencies=["Ministério da Saúde"] ou ["saude"]
  - year_from=2025, year_to=2025
  - sort="newest"
  - limit=5

#### Teste 1.3: Busca por Tema
```
Encontre notícias sobre meio ambiente e sustentabilidade, ordenadas pelas mais antigas, limite 3
```

**Esperado:**
- Usa `search_news` com:
  - query="meio ambiente sustentabilidade"
  - sort="oldest"
  - limit=3

### Tool 2: `get_facets` (Agregações)

#### Teste 2.1: Agregação por Agência
```
Quais agências publicaram mais notícias sobre educação? Mostre as top 10
```

**Esperado:**
- Usa `get_facets` com:
  - facet_fields=["agency"]
  - query="educação"
  - max_values=10
- Retorna tabela com agências e contagens

#### Teste 2.2: Distribuição Temporal
```
Mostre a distribuição de notícias sobre tecnologia por ano
```

**Esperado:**
- Usa `get_facets` com:
  - facet_fields=["published_year"]
  - query="tecnologia"
- Retorna anos com contagens

#### Teste 2.3: Múltiplas Agregações
```
Analise notícias sobre meio ambiente: mostre distribuição por agência E por tema (top 5 de cada)
```

**Esperado:**
- Usa `get_facets` com:
  - facet_fields=["agency", "theme_1_level_1"]
  - query="meio ambiente"
  - max_values=5
- Retorna duas tabelas (agências e temas)

### Tool 3: `similar_news` (Similaridade)

#### Teste 3.1: Encontrar Similares
```
Busque notícias sobre educação e me dê o ID de uma delas. Depois encontre 3 notícias similares a essa.
```

**Esperado:**
1. Primeiro usa `search_news` para encontrar notícia
2. Você fornece o ID
3. Usa `similar_news` com:
   - reference_id="<ID fornecido>"
   - limit=3
- Retorna 3 notícias com mesma agência/tema

#### Teste 3.2: Exploração de Contexto
```
Mostre a notícia com ID 254647 e depois encontre 5 notícias similares
```

**Esperado:**
1. Pode usar resource `govbrnews://news/254647` para ver detalhes
2. Usa `similar_news` com reference_id="254647", limit=5
- Retorna contexto da referência + similares

---

## 2. Testes de Resources

### Resource 1: `govbrnews://stats`

#### Teste 2.1: Estatísticas Gerais
```
Mostre as estatísticas gerais do dataset de notícias
```

**Esperado:**
- Acessa `govbrnews://stats`
- Retorna:
  - Total de documentos (295,511)
  - Distribuição por ano
  - Top 5 agências
  - Período de cobertura

### Resource 2: `govbrnews://agencies`

#### Teste 2.2: Lista de Agências
```
Quais agências estão disponíveis no dataset? Liste todas ordenadas por quantidade
```

**Esperado:**
- Acessa `govbrnews://agencies`
- Retorna lista completa (148 agências)
- Ordenado por volume decrescente

### Resource 3: `govbrnews://themes`

#### Teste 2.3: Taxonomia de Temas
```
Quais temas estão disponíveis no dataset?
```

**Esperado:**
- Acessa `govbrnews://themes`
- Retorna 25 temas com contagens
- Ex: "03 - Saúde", "02 - Educação", etc.

### Resource 4: `govbrnews://news/{id}`

#### Teste 2.4: Notícia Individual
```
Mostre o conteúdo completo da notícia com ID 254647
```

**Esperado:**
- Acessa `govbrnews://news/254647`
- Retorna notícia completa:
  - Título
  - Todos os metadados (agência, data, categoria, tema, URL)
  - Conteúdo completo

---

## 3. Testes Combinados

### Teste 3.1: Análise Completa de Tema
```
Faça uma análise completa sobre notícias de saúde:
1. Mostre estatísticas gerais do tema
2. Liste as principais agências que cobrem saúde
3. Mostre algumas notícias recentes
4. Encontre notícias similares a uma delas
```

**Esperado:**
- Usa múltiplos tools/resources:
  - `get_facets` para estatísticas
  - `search_news` para notícias recentes
  - `similar_news` para similares
- Fornece análise abrangente

### Teste 3.2: Comparação Temporal
```
Compare a cobertura de educação entre 2024 e 2025:
- Quantas notícias em cada ano?
- Quais agências mais publicaram?
- Mostre 3 notícias de cada ano
```

**Esperado:**
- Usa `get_facets` para contagens por ano
- Usa `get_facets` para agências por período
- Usa `search_news` com filtros de ano

### Teste 3.3: Exploração de Agência
```
Analise as notícias do Ministério da Educação (MEC):
1. Quantas notícias totais?
2. Distribuição por ano
3. Principais temas cobertos
4. Mostre 5 notícias mais recentes
```

**Esperado:**
- Combina `get_facets` e `search_news`
- Fornece visão completa da agência

---

## 4. Testes de Edge Cases

### Teste 4.1: Query Sem Resultados
```
Busque notícias sobre "xyzabc123" (termo inexistente)
```

**Esperado:**
- Retorna mensagem clara de "nenhum resultado encontrado"

### Teste 4.2: ID Inválido
```
Mostre a notícia com ID 999999999
```

**Esperado:**
- Erro claro: "Notícia não encontrada"

### Teste 4.3: Campo Inválido em Facets
```
Mostre agregações por campo "campo_invalido"
```

**Esperado:**
- Erro claro listando campos válidos

---

## 5. Verificação de Funcionalidades

### Checklist de Funcionalidades ✅

**Tools:**
- [ ] `search_news` funciona com query simples
- [ ] `search_news` funciona com filtros (agência, ano, tema)
- [ ] `search_news` funciona com ordenação (newest, oldest, relevant)
- [ ] `get_facets` funciona com um campo
- [ ] `get_facets` funciona com múltiplos campos
- [ ] `get_facets` funciona com query filtrada
- [ ] `similar_news` encontra notícias similares
- [ ] `similar_news` exclui a notícia de referência
- [ ] `similar_news` mostra contexto da referência

**Resources:**
- [ ] `govbrnews://stats` retorna estatísticas completas
- [ ] `govbrnews://agencies` lista todas as agências
- [ ] `govbrnews://themes` lista todos os temas
- [ ] `govbrnews://news/{id}` retorna notícia individual

**Formatação:**
- [ ] Resultados são bem formatados em Markdown
- [ ] Números são formatados com separadores (ex: 50,211)
- [ ] Datas são legíveis (ex: 13/10/2025)
- [ ] Links são clicáveis quando disponíveis

**Experiência do Usuário:**
- [ ] Claude escolhe a tool/resource correta automaticamente
- [ ] Respostas são informativas e contextualizadas
- [ ] Erros são tratados de forma amigável
- [ ] Performance é aceitável (< 2s por query)

---

## 6. Troubleshooting

### Problema: MCP não aparece no Claude Code

**Solução:**
1. Verificar configuração em `~/Library/Application Support/Claude/claude_code_config.json`
2. Reiniciar Claude Code completamente
3. Verificar logs do Claude Code para erros

### Problema: Erro ao conectar com Typesense

**Solução:**
1. Verificar que Typesense está rodando:
   ```bash
   curl http://localhost:8108/health
   ```
2. Verificar variáveis de ambiente no `.env`
3. Reiniciar Typesense se necessário

### Problema: Tool não é chamada automaticamente

**Solução:**
1. Ser mais explícito na pergunta
2. Mencionar "busque", "mostre", "encontre", etc.
3. Claude decide baseado no contexto - tente reformular

---

## Exemplo de Sessão Completa

```
Você: Olá! Quero entender o dataset de notícias governamentais. Comece mostrando as estatísticas gerais.

Claude: [Acessa govbrnews://stats e mostra estatísticas]

Você: Interessante! Agora mostre quais são os temas disponíveis, ordenados por quantidade.

Claude: [Acessa govbrnews://themes e lista os 25 temas]

Você: Vejo que Saúde é o tema mais coberto. Mostre 5 notícias recentes sobre saúde.

Claude: [Usa search_news com query="saúde", sort="newest", limit=5]

Você: Mostre mais detalhes da primeira notícia.

Claude: [Acessa govbrnews://news/{id} da primeira notícia]

Você: Legal! Agora encontre 3 notícias similares a essa.

Claude: [Usa similar_news com o ID da notícia]

Você: Excelente! Por fim, quais agências mais publicam sobre saúde?

Claude: [Usa get_facets com facet_fields=["agency"], query="saúde"]
```

---

## Notas Finais

- **Dataset:** 295,511 notícias governamentais brasileiras
- **Período:** Múltiplos anos (2016-2025)
- **Agências:** 148 agências governamentais
- **Temas:** 25 temas principais

**Divirta-se explorando o dataset! 🚀**
