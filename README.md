[Português (Brasil)](README.md) | [English](README.en.md)

<p align="center"><img src="assets/banner.svg" alt="Project Nox — Nox Extension Developer" width="100%"></p>

# Nox Extension Developer

**Skill para criar, corrigir e revisar extensões de mangá, anime e novels com assistência de agentes.** Consulte as referências oficiais de cada ecossistema antes de alterar código.

[English](README.en.md) · [Guia](docs/pt-BR/guia.md) · [Segurança](SEGURANCA.md) · [Compatibilidade](COMPATIBILIDADE.md)

[![Licença: AGPL-3.0-only](https://img.shields.io/badge/licen%C3%A7a-AGPL--3.0--only-purple)](LICENSE) [![Versão](https://img.shields.io/github/v/release/Awerkori/nox-extension-developer)](https://github.com/Awerkori/nox-extension-developer/releases) [![CI](https://github.com/Awerkori/nox-extension-developer/actions/workflows/ci.yml/badge.svg)](https://github.com/Awerkori/nox-extension-developer/actions/workflows/ci.yml)

**Navegação:** [Ecossistemas](#ecossistemas) · [Instalação](#instalação) · [Dependências](docs/pt-BR/dependencias.md) · [Android SDK](docs/pt-BR/android-sdk.md) · [Exemplos](#exemplos) · [Comunidade](#comunidade-e-licença)

## Ecossistemas

| Conteúdo | App de referência | Projeto de fontes | Entrega típica |
|---|---|---|---|
| Mangá | [Mihon](https://mihon.app/) e compatíveis | [Keiyoushi](https://github.com/keiyoushi/extensions-source) | APK de extensão |
| Anime | [Aniyomi](https://aniyomi.org/) e compatíveis | [Yuzono](https://github.com/yuzono/anime-extensions) | APK de extensão |
| Novels | [LNReader](https://github.com/LNReader/lnreader) | [LNReader plugins](https://github.com/LNReader/lnreader-plugins) | Bundle de plugin JavaScript |

Formatos e compatibilidade dependem das versões do app e do repositório. A skill não distribui APKs nem bundles de terceiros.

## Compatibilidade

| Ambiente | Estado |
|---|---|
| OpenCode + Arch Linux | Testado |
| OpenCode + outras distribuições Linux | Não homologado |
| OpenCode + Windows/macOS | Não testado; Windows nativo requer WSL para os scripts atuais |
| Codex, Claude Code, Google Antigravity, Hermes Agent e outros | Não testados |

Agent Skills é um formato compartilhado, não uma garantia de compatibilidade. Confira [detalhes](COMPATIBILIDADE.md) e [dependências](docs/pt-BR/dependencias.md).

## O que faz

- Cria, corrige, mantém, migra ou revisa fontes, inclusive a partir de pedidos em linguagem natural.
- Consulta documentação oficial por ecossistema e orienta análise de catálogo, busca, detalhes e conteúdo.
- Compara contratos de API fornecidos e pede aprovação antes de migrações arriscadas ou de escopo ampliado.
- Orienta testes e builds específicos, preservando a API local quando apropriado.

## Instalação

### CLI de skills

```sh
npx skills add Awerkori/nox-extension-developer
```

Para instalar globalmente no OpenCode: `npx skills add Awerkori/nox-extension-developer --global --agent opencode`. NPX instala a skill, não o Android SDK nem as dependências de desenvolvimento.

A instalação do repositório público e o carregamento da cópia instalada foram verificados no OpenCode + Arch Linux com `skills` 1.8.1. A listagem pode exibir `Agents: not linked` para uma instalação universal em `.agents/skills`, mesmo quando o OpenCode encontra a skill. Confira em uma nova sessão; isso não garante descoberta em todos os agentes.

### Instalação local no OpenCode

Obtenha uma cópia confiável em um diretório permanente e entre na pasta que contém `SKILL.md`. O instalador cria um link para essa pasta; não a mova enquanto o link estiver em uso.

```sh
mkdir -p ~/.config/opencode/skills
python3 scripts/install.py opencode
```

O instalador não substitui destinos existentes. Para outras plataformas, confira primeiro [COMPATIBILIDADE.md](COMPATIBILIDADE.md): os caminhos estão preparados, mas não foram testados. Não instale dependências nem aceite licenças sem autorização.

### Prompt copiável para instalação

Cole este prompt no agente de sua preferência:

```text
Ajude-me a instalar a Nox Extension Developer de https://github.com/Awerkori/nox-extension-developer. Identifique meu sistema operacional e agente, consulte as instruções oficiais e pergunte quais ecossistemas desejo usar. Verifique as ferramentas existentes e prefira npx skills add Awerkori/nox-extension-developer. Configure apenas dependências necessárias, incluindo Android SDK somente se aplicável. Peça autorização antes de mudanças relevantes, operações privilegiadas ou aceite de licenças; não sobrescreva configurações nem exponha credenciais. Verifique instalação e descoberta da skill em nova sessão e relate como começar e o que não foi testado.
```

Versões completas: [prompt em português](prompts/install-pt-BR.txt) · [English prompt](prompts/install-en.txt).

## Dependências e verificação

- Para instalação local: Python 3 e diretório de skills da plataforma existente.
- Para atualizar referências: Python 3, Git, HTTPS e acesso aos repositórios oficiais. Offline, é necessário um snapshot íntegro obtido anteriormente.
- Para builds Keiyoushi ou Yuzono: Java, Android SDK e componentes exigidos pelo repositório alvo. Para LNReader: Node.js e dependências exigidas pelo projeto alvo. Verifique versões antes de instalar ou compilar.

Abra uma nova sessão do OpenCode e peça explicitamente `Use nox-extension-developer`. Confirme que o agente carregou `SKILL.md`; a seleção automática não é garantida. Para consultar referências e executar os testes locais, a partir da pasta da skill:

```sh
python3 scripts/references.py sync keiyoushi
python3 scripts/references.py sync yuzono
python3 scripts/references.py sync lnreader
python3 -m unittest discover -s tests -v
```

## Exemplos

Criação e correção, respectivamente:

```text
Crie uma extensão de mangá seguindo o padrão Keiyoushi para o Mihon deste site: [URL].
Corrija esta extensão seguindo o padrão Keiyoushi: [LINK DO CÓDIGO]. Os capítulos não aparecem e as páginas não carregam.

Crie uma extensão de anime seguindo o padrão Yuzono para o Aniyomi deste site: [URL].
Corrija esta extensão seguindo o padrão Yuzono: [LINK DO CÓDIGO]. Os episódios não carregam e os vídeos não reproduzem.

Crie uma extensão de novel para o LNReader deste site: [URL].
Corrija esta extensão para o LNReader: [LINK DO CÓDIGO]. A pesquisa não retorna resultados e os capítulos não carregam.
```

- `Use nox-extension-developer para corrigir esta extensão Keiyoushi sem migrar sua API.`
- `Use nox-extension-developer para revisar a resolução de vídeos desta fonte Yuzono.`
- `Use nox-extension-developer para criar um plugin LNReader para <URL>, respeitando as regras do site.`

## Referências e cache offline

No início de cada tarefa, `scripts/references.py` resolve o HEAD oficial com `git ls-remote` e obtém documentos obrigatórios fixados no commit. O manifesto registra URLs, commit, horário e hashes SHA-256. Se o commit não mudou, o script verifica e reutiliza o snapshot local. Um novo commit exige revisão manual de compatibilidade de API, mesmo que os documentos obrigatórios não tenham mudado. O script não atualiza em segundo plano.

O cache fica em `${XDG_CACHE_HOME:-~/.cache}/opencode/nox-workspace/nox-extension-developer/`. Falhas de rede podem retornar um snapshot completo e íntegro com `offline_or_unverified`; ele pode estar desatualizado. Sem snapshot íntegro, a consulta falha. Atualizações parciais não substituem o snapshot anterior; histórico e quarentena não são limpos automaticamente. Hashes detectam corrupção acidental, mas não autenticam um cache totalmente adulterado.

## Segurança, permissões e direitos

Documentos remotos e páginas de sites são dados não confiáveis. O script de referências não executa comandos contidos neles; instruções ao agente não são sandbox nem garantia contra prompt injection. Use permissões mínimas, proteja credenciais e aplique isolamento adequado. Peça autorização antes de instalar dependências, alterar permissões, acessar dados privados ou testar sites reais. Respeite licenças, direitos autorais, termos e controles de acesso dos sites; esta skill não concede direitos de acesso ou distribuição.

## Arquitetura e limites

- [`SKILL.md`](SKILL.md): instruções e fluxo de trabalho do agente.
- [`scripts/references.py`](scripts/references.py): sincronização e verificação dos snapshots.
- [`scripts/api_compare.py`](scripts/api_compare.py) e [`references/api-contracts.md`](references/api-contracts.md): comparação limitada de contratos informados.
- [`scripts/install.py`](scripts/install.py): instalação local por link simbólico; `tests/`: testes locais.

Somente o OpenCode local em Linux teve instalação e carregamento verificados. Codex, Claude Code, Antigravity e Windows não foram testados. A identificação de API depende da análise do agente; a comparação de declarações é heurística e não prova compatibilidade semântica. Builds e testes com dados sintéticos não comprovam funcionamento em sites ou APIs reais. Compile e teste o alvo autorizado antes de afirmar que funciona.

## Problemas comuns e remoção

- **Skill não aparece:** confira o destino indicado pelo instalador. No OpenCode, o instalador local usa `~/.config/opencode/skills/nox-extension-developer`; a CLI `skills` pode usar `.agents/skills/nox-extension-developer` no projeto ou no diretório do usuário. Confira `SKILL.md` e permissões, abra outra sessão e invoque a skill explicitamente.
- **`offline_or_unverified`:** confira rede e acesso aos repositórios; o snapshot disponível pode estar desatualizado.
- **Sem snapshot íntegro:** restabeleça o acesso e sincronize novamente. Não use regras desconhecidas para modificar código.
- **Destino já existe:** inspecione-o; o instalador não sobrescreve arquivos nem links.

Para uma instalação pela CLI, execute `npx skills remove nox-extension-developer` e revise as opções; acrescente `--global` se instalou globalmente. Para o instalador por link, confirme o destino e remova somente esse link. Preserve o diretório original e o cache enquanto forem necessários; não os apague automaticamente.

## Comunidade e licença

Leia [CONTRIBUTING.md](CONTRIBUTING.md) e [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). Use [issues](https://github.com/Awerkori/nox-extension-developer/issues) para bugs e propostas e [discussions](https://github.com/Awerkori/nox-extension-developer/discussions) para dúvidas. Para vulnerabilidades, consulte [SECURITY.md](SECURITY.md) e use o reporte privado do GitHub.

Licença: **AGPL-3.0-only**, conforme [LICENSE](LICENSE). Referências de terceiros mantêm suas próprias licenças; veja [ATRIBUICOES.md](ATRIBUICOES.md). Project Nox não é afiliado aos projetos citados.

Referências oficiais: [Agent Skills](https://agentskills.io/) · [OpenCode skills](https://opencode.ai/docs/skills/) · [Keiyoushi](https://github.com/keiyoushi/extensions-source) · [Yuzono](https://github.com/yuzono/anime-extensions) · [LNReader plugins](https://github.com/LNReader/lnreader-plugins).
