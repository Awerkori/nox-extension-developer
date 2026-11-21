[Português (Brasil)](README.md) | [English](README.en.md)

<p align="center">
  <img src="assets/nox-emblem.webp" alt="Emblema oficial do Project Nox" width="96" />
</p>

<h1 align="center">Project Nox · Extension Developer</h1>

<p align="center">
  Skill de código aberto para auxiliar agentes de IA na criação, correção e manutenção de extensões.
</p>

## O que é a Nox Extension Developer?

A **Nox Extension Developer** é uma skill gratuita e de código aberto projetada para orientar agentes de inteligência artificial compatíveis no desenvolvimento, correção, atualização e revisão de extensões de mangás, animes e novels.

Ela **não** é uma IA independente: trata-se de um conjunto estruturado de instruções, contratos e scripts locais carregados pelo agente escolhido. Você descreve o que precisa em linguagem natural, e a IA utiliza a skill para sincronizar referências oficiais, inspecionar padrões de código e orientar implementação, testes e compilação.

> O Project Nox não é afiliado aos projetos de referência listados abaixo. Utilize somente fontes autorizadas e revise o código produzido; a skill auxilia o trabalho técnico, sem garantir funcionamento automático em qualquer site.

## Ecossistemas suportados

| Conteúdo | Referência | Aplicação | Resultado |
|---|---|---|---|
| Mangá | Keiyoushi | Mihon e aplicativos compatíveis | APK |
| Anime | Yuzono | Aniyomi e aplicativos compatíveis | APK |
| Novel | LNReader | LNReader | Plugin ou bundle |

Cada ecossistema é independente: regras, APIs e exemplos de **Keiyoushi**, **Yuzono** e **LNReader** são mantidos separados e não devem ser misturados entre si.

## Instalação rápida

### Método recomendado: instalação assistida por IA

Copie o texto abaixo, cole em seu agente de IA compatível e autorize apenas as etapas com as quais concordar:

```text
Instale e configure a skill Nox Extension Developer de:
https://github.com/ProjectNox-org/nox-extension-developer

Identifique meu sistema operacional e meu agente de IA, consulte a documentação
oficial e pergunte se desejo trabalhar com mangá, anime, novels ou todos.
Verifique as ferramentas existentes e prefira:
npx skills add ProjectNox-org/nox-extension-developer

Configure apenas as dependências necessárias (incluindo Java e Android SDK
somente se aplicável). Peça minha autorização antes de alterações relevantes,
comandos administrativos ou aceite de licenças; não sobrescreva configurações nem
exponha credenciais. Após concluir, valide o carregamento da skill em uma nova
sessão e informe como começar e o que não foi testado.
```

Prompt pronto em arquivo: [`prompts/install-pt-BR.txt`](prompts/install-pt-BR.txt) · [`prompts/install-en.txt`](prompts/install-en.txt).

### Método alternativo: instalação manual via NPX

Execute no terminal:

```bash
npx skills add ProjectNox-org/nox-extension-developer
```

Selecione seu agente quando solicitado (ou informe o alvo diretamente, por exemplo `--global --agent opencode`). Também existe o instalador manual por link simbólico em [`scripts/install.py`](scripts/install.py).

- Requer Node.js e npm compatíveis (nos testes com a Skills CLI `1.8.1`, foi exigido Node.js `22.20.0+`; verifique os requisitos atuais da CLI).
- `npx skills add` instala **somente** a skill — ele não instala nem configura Java JDK, Android SDK ou dependências do LNReader.
- Após instalar, **abra uma nova sessão do agente** e peça explicitamente: `Use a skill nox-extension-developer`. Consulte os detalhes completos no [guia de instalação](docs/pt-BR/guia.md).

## Como usar na prática

Substitua os campos entre colchetes pelas informações do site ou repositório desejado.

### Mangá — criar (Keiyoushi / Mihon)

```text
Use a skill nox-extension-developer para criar uma extensão de mangá seguindo o
padrão Keiyoushi para o Mihon a partir deste site: [URL DO SITE].
```

### Mangá — corrigir (Keiyoushi / Mihon)

```text
Use a skill nox-extension-developer para corrigir uma extensão de mangá no
padrão Keiyoushi.
Repositório: [REPOSITÓRIO KEIYOUSHI OU PROJECT NOX]
Nome da extensão: [NOME DA EXTENSÃO]
Problema: [ex.: capítulos não aparecem ou páginas não carregam]
```

Repositórios: [Keiyoushi](https://github.com/keiyoushi/extensions-source) · [Project Nox](https://github.com/ProjectNox-org/manga-fonte-extensoes).

### Anime — criar (Yuzono / Aniyomi)

```text
Use a skill nox-extension-developer para criar uma extensão de anime seguindo o
padrão Yuzono para o Aniyomi a partir deste site: [URL DO SITE].
```

### Anime — corrigir (Yuzono / Aniyomi)

```text
Use a skill nox-extension-developer para corrigir uma extensão de anime no padrão
Yuzono.
Repositório: [REPOSITÓRIO YUZONO OU PROJECT NOX]
Nome da extensão: [NOME DA EXTENSÃO]
Problema: [ex.: episódios não listam ou fontes de vídeo falham]
```

Repositórios: [Yuzono](https://github.com/yuzono/anime-extensions) · [Project Nox](https://github.com/ProjectNox-org/anime-fonte-extensoes).

### Novel — criar (LNReader)

```text
Use a skill nox-extension-developer para criar um plugin de novel seguindo o
padrão LNReader a partir deste site: [URL DO SITE].
```

### Novel — corrigir (LNReader)

```text
Use a skill nox-extension-developer para corrigir um plugin de novel no padrão
LNReader.
Repositório: https://github.com/LNReader/lnreader-plugins
Nome do plugin: [NOME DO PLUGIN]
Problema: [ex.: busca sem resultados ou capítulos vazios]
```

Para atualizar uma extensão existente, envie o código-fonte e peça para preservar a compatibilidade com a API local. Sempre peça o caminho do APK/bundle gerado e os passos de validação.

## Dependências

Separe o que é necessário para **executar a skill** do que é exigido para **compilar extensões**:

- **Skill e scripts locais:** **Git** e **Python 3** (ambiente POSIX em Linux, macOS ou **Windows via WSL** — `scripts/references.py` usa `fcntl`); **Node.js e npm** para usar `npx skills`.
- **Mangá e Anime (APK):** **Java JDK** e **Android SDK** (`Command-line Tools`, plataforma Android e `Build Tools`) nas versões definidas pelo repositório de destino (`compileSdk` e Gradle Wrapper `./gradlew`). Nos testes locais do projeto foram usados JDK 21, Android SDK 37.0 e Build Tools 36.0.0/37.0.0 — trate esses valores apenas como referência de teste, não como requisito fixo universal.
- **Novels (LNReader):** **Node.js** compatível (no projeto LNReader costuma-se usar Node 22+) e dependências locais via `npm install` (TypeScript e bibliotecas do repositório). **Quem trabalha exclusivamente com novels não precisa instalar o Android SDK.**

Tutoriais completos por sistema operacional (**Windows via WSL**, **Arch Linux**, **Ubuntu**, **Debian**, **Fedora** e **macOS**):
[Preparação por sistema](docs/pt-BR/guia.md#preparação-por-sistema) · [Dependências](docs/pt-BR/dependencias.md) · [Android SDK](docs/pt-BR/android-sdk.md).

## Compatibilidade com agentes

| Agente | Estado |
|---|---|
| [OpenCode](https://opencode.ai/) | ✅ Testado (`v2.2.7` em Arch Linux) |
| [Codex](https://developers.openai.com/codex/) | 🟡 Documentado (execução não testada) |
| [Claude Code](https://code.claude.com/) | 🟡 Documentado (execução não testada) |
| [Google Antigravity](https://antigravity.google/) | 🟡 Documentado (não homologado) |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | ⚪ Não verificado |

`Codex` (`~/.agents/skills/`), `Claude Code` (`~/.claude/skills/`) e `Google Antigravity` (`~/.gemini/antigravity/skills/`) possuem destinos documentados em [`scripts/install.py`](scripts/install.py), sem testes locais de link ou execução; `Hermes Agent` não possui alvo dedicado no instalador. Os testes oficiais ocorreram em **Arch Linux** (demais distros Linux, macOS e Windows via WSL não foram homologados). Veja [`COMPATIBILIDADE.md`](COMPATIBILIDADE.md).

## Documentação

- [Guia completo de instalação, uso e solução de problemas](docs/pt-BR/guia.md) ([English](docs/en/guide.md))
- [Dependências por ferramenta](docs/pt-BR/dependencias.md) ([English](docs/en/dependencies.md))
- [Instalação segura do Android SDK](docs/pt-BR/android-sdk.md) ([English](docs/en/android-sdk.md))
- [Compatibilidade com agentes e sistemas](COMPATIBILIDADE.md)
- [Segurança e limites operacionais](SEGURANCA.md) · [Política de reporte (`SECURITY.md`)](SECURITY.md)
- [Contratos e comparação de APIs](references/api-contracts.md)

## Perguntas frequentes

- **Preciso saber programar?** Não para iniciar com a IA, mas revisar alterações, testar casos difíceis e manter extensões pode exigir apoio técnico.
- **A skill é gratuita?** Sim. Custos, limites e cotas dependem apenas do agente e do modelo de IA escolhidos.
- **Preciso instalar o Android SDK?** Sim apenas para compilar APKs de mangá (Keiyoushi) ou anime (Yuzono). Para plugins LNReader de novels, **não**.
- **Quais agentes são compatíveis?** A execução foi verificada no OpenCode (`v2.2.7` em Arch Linux); Codex, Claude Code e Google Antigravity possuem caminhos documentados sem homologação oficial, e Hermes Agent não foi verificado.
- **O que fazer se a skill não for reconhecida?** Abra uma nova sessão do agente, solicite `Use nox-extension-developer` pelo nome exato e confira o caminho/link de instalação no [guia de solução de problemas](docs/pt-BR/guia.md#solução-de-problemas).
- **Onde estão as instruções de atualização ou remoção?** Veja `npx skills update --help`, `npx skills remove --help` e as instruções manuais na seção de [instalação e remoção do guia](docs/pt-BR/guia.md#instalação).

## Suporte e contribuições

- [Issues](https://github.com/ProjectNox-org/nox-extension-developer/issues) — Relate bugs reproduzíveis ou divergências técnicas.
- [Discussions](https://github.com/ProjectNox-org/nox-extension-developer/discussions) — Tire dúvidas e proponha ideias.
- [Pull Requests](https://github.com/ProjectNox-org/nox-extension-developer/pulls) — Envie melhorias conforme [`CONTRIBUTING.md`](CONTRIBUTING.md).
- [Releases](https://github.com/ProjectNox-org/nox-extension-developer/releases) — Acompanhe versões lançadas.

**Aviso de segurança:** nunca publique senhas, tokens, chaves ou dados pessoais em issues ou PRs. Reporte vulnerabilidades exclusivamente pelo fluxo descrito em [`SECURITY.md`](SECURITY.md).

**Ecossistema Project Nox:** [Central Oficial](https://projectnox-org.github.io/) · [Project Nox Mangá](https://github.com/ProjectNox-org/project-nox-manga) · [Importer](https://github.com/ProjectNox-org/project-nox-importer) · [Extensões de Mangá](https://github.com/ProjectNox-org/manga-extensoes) ([fonte](https://github.com/ProjectNox-org/manga-fonte-extensoes)) · [Extensões de Anime](https://github.com/ProjectNox-org/anime-extensoes) ([fonte](https://github.com/ProjectNox-org/anime-fonte-extensoes)) · [Central de Solicitações](https://github.com/ProjectNox-org/project-nox-requests) · [Tracker](https://github.com/ProjectNox-org/project-nox-tracker).

## Créditos e licenciamento

Criado por [**Awerkori**](https://github.com/Awerkori) para o [**Project Nox**](https://github.com/ProjectNox-org). Os projetos [Keiyoushi](https://github.com/keiyoushi/extensions-source), [Yuzono](https://github.com/yuzono/anime-extensions), [LNReader](https://github.com/LNReader/lnreader-plugins) e o padrão [Agent Skills](https://agentskills.io/) são referências técnicas independentes sem vínculo ou afiliação; veja [`ATRIBUICOES.md`](ATRIBUICOES.md).

Este software é licenciado sob a **GNU Affero General Public License v3.0 (`AGPL-3.0-only`)** — consulte [`LICENSE`](LICENSE) para o texto integral (incluindo obrigações de código-fonte para uso remoto por rede na Seção 13 e preservação das marcas **Project Nox** e **Awerkori** na Seção 7(e)). A licença aplica-se exclusivamente ao código da skill, sem garantias e sem conceder direitos sobre conteúdos, sites ou obras de terceiros.
