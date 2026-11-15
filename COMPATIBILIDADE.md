# Compatibilidade

Codex, Claude Code e Google Antigravity: **COMPATIBILIDADE PREPARADA, MAS NÃO TESTADA**. O suporte de execução dos scripts foi testado apenas em Linux; Windows não foi verificado.

| Plataforma | Diretório de skills de usuário | Estado |
|---|---|---|
| OpenCode | `~/.config/opencode/skills/` | Link instalado e carregamento verificado no OpenCode local v2.2.7. |
| Codex | `~/.agents/skills/` | Caminho e suporte a links documentados no código oficial; instalação e execução não testadas. |
| Claude Code | `~/.claude/skills/` | Caminho de usuário documentado; links e execução não testados. |
| Google Antigravity | `~/.gemini/antigravity/skills/` | Caminho relatado pela documentação consultada; links e execução não testados. |

Para preparar outro agente: confirme documentação e instalação locais, crie o diretório de skills pelo fluxo oficial da plataforma se necessário, e execute `python3 scripts/install.py codex`, `claude` ou `antigravity`. O instalador não cria diretórios de plataformas ausentes, não valida a versão instalada nem confirma se cada agente segue links. Retire o link criado se a plataforma não o reconhecer. Não instale múltiplos links em locais que o mesmo agente percorra simultaneamente sem verificar duplicação.

Fontes consultadas: [OpenCode skills](https://opencode.ai/docs/skills/), [Codex skills](https://developers.openai.com/codex/skills/), [Claude Code skills](https://code.claude.com/docs/en/skills), [Google Antigravity](https://antigravity.google/docs/skills). A disponibilidade e os caminhos devem ser reconfirmados quando utilizados.
