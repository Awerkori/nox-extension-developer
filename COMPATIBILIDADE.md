# Compatibilidade

O ambiente efetivamente testado foi OpenCode + Arch Linux. Outras distribuições Linux não foram homologadas. Windows e macOS não foram testados. Codex, Claude Code, Google Antigravity, Hermes Agent e outros agentes não foram testados.

Windows nativo não é suportado pelo script `references.py`: ele importa `fcntl` e usa mecanismos POSIX de processo. No Windows, use WSL com uma distribuição Linux e instale o agente e as dependências dentro do WSL. macOS tem interfaces POSIX, mas não foi testado.

| Plataforma | Diretório de skills de usuário | Estado |
|---|---|---|
| OpenCode | `~/.config/opencode/skills/` | Link instalado e carregamento verificado no OpenCode local v2.2.7. |
| Codex | `~/.agents/skills/` | Caminho e suporte a links documentados no código oficial; instalação e execução não testadas. |
| Claude Code | `~/.claude/skills/` | Caminho de usuário documentado; links e execução não testados. |
| Google Antigravity | `~/.gemini/antigravity/skills/` / `~/.agents/skills/` | CLI (`nox.py`), suíte de testes e carregamento local verificados em Arch Linux (v2.0.0); instalação em dispositivo Android físico não executada (`adb devices` vazio). |
| Hermes Agent | Consulte a documentação oficial do agente | Não testado. |

Para preparar outro agente: confirme documentação e instalação locais, crie o diretório de skills pelo fluxo oficial da plataforma se necessário, e execute `python3 scripts/install.py codex`, `claude` ou `antigravity`. O instalador não cria diretórios de plataformas ausentes, não valida a versão instalada nem confirma se cada agente segue links. Retire o link criado se a plataforma não o reconhecer. Não instale múltiplos links em locais que o mesmo agente percorra simultaneamente sem verificar duplicação.

Fontes consultadas: [OpenCode skills](https://opencode.ai/docs/skills/), [Codex skills](https://developers.openai.com/codex/skills/), [Claude Code skills](https://code.claude.com/docs/en/skills), [Google Antigravity](https://antigravity.google/docs/skills). A disponibilidade e os caminhos devem ser reconfirmados quando utilizados.
