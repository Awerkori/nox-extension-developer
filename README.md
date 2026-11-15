[Português (Brasil)](README.md) | [English](README.en.md)

<p align="center"><img src="assets/banner.svg" alt="Project Nox — Nox Extension Developer" width="100%"></p>

# Project Nox · Extension Developer

Uma **skill gratuita e de código aberto** que ajuda sua IA a criar, corrigir e atualizar extensões. Você descreve o que precisa; a IA consulta as referências oficiais, analisa o site e orienta o desenvolvimento, os testes e a compilação.

| Conteúdo | Padrão | Aplicativo | Resultado |
|---|---|---|---|
| 📚 Mangá | Keiyoushi | Mihon e forks | APK |
| 🎬 Anime | Yuzono | Aniyomi e forks | APK |
| 📖 Novel | LNReader | LNReader | Plugin / bundle |

O Project Nox não é afiliado aos projetos de referência. Use apenas sites e conteúdos que você tenha autorização para acessar. A skill auxilia o desenvolvimento, mas não garante funcionamento em qualquer site.

## 📦 Dependências necessárias

| Ferramenta | Para que serve | Quando instalar |
|---|---|---|
| Git | Consulta repositórios oficiais | Para usar as referências |
| Python 3 | Executa os scripts da skill | Para usar os scripts |
| Node.js, npm e NPX | Instalam a skill pelo terminal | Para NPX, Node.js **22.20.0 ou superior**; LNReader exige Node.js **22 ou superior**. Recomendamos Node.js 24 LTS |
| Java JDK | Compila código Kotlin | Para mangá e anime, na versão exigida pelo projeto |
| Android SDK, Command-line Tools, plataforma e Build Tools | Preparam e compilam APKs | Para mangá e anime, conforme o projeto |
| Dependências do LNReader e TypeScript | Desenvolvem plugins de novels | Para novels; use as versões do próprio projeto |
| ADB e emulador | Testam em dispositivo Android | Opcionais quando não houver teste em dispositivo |

> **NPX instala a skill, não Java, Android SDK ou as demais ferramentas de desenvolvimento.**
>
> **Para desenvolver somente novels para LNReader, você não precisa instalar o Android SDK.**

O Gradle Wrapper e outras ferramentas podem acompanhar o projeto. Não é necessário instalá-las globalmente. Veja o [guia de dependências](docs/pt-BR/dependencias.md).

## 💻 Instalação das dependências

Abra a seção do seu sistema. Instale apenas ferramentas ausentes e peça ajuda à IA se algum comando falhar. Operações com `sudo` pedem senha e alteram o computador.

**Etapa 1:** instale Git, Python e Node. **Etapa 2:** prepare Android para mangá/anime ou as dependências locais para novels. **Etapa 3:** instale a skill por NPX ou pelo prompt abaixo. Antes de trocar uma versão existente, confira `node --version`; `skills` 1.8.1 requer Node.js 22.20.0 ou superior. Recomendamos Node.js 24 LTS.

Os comandos das distribuições podem oferecer Node antigo. Caso `node --version` seja inferior a 22.20.0, instale Node 24 pelo [instalador oficial](https://nodejs.org/en/download) e abra um novo terminal. Não sobrescreva uma instalação existente sem revisá-la.

No Linux, WSL ou macOS, uma alternativa é instalar Node 24 no usuário com [nvm](https://github.com/nvm-sh/nvm):

```bash
# Se ~/.nvm já existir, use a instalação existente; não a substitua.
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version
npm --version
npx --version
```

Para carregar o nvm em novos terminais Bash, adicione `export NVM_DIR="$HOME/.nvm"` e `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` ao `~/.bashrc` apenas depois de conferir que não existem entradas equivalentes. No Zsh use `~/.zshrc`.

Para novels, execute `npm install` na pasta do projeto LNReader, normalmente com ajuda da IA. TypeScript e bibliotecas são instalados conforme o `package.json` do projeto. Para mangá/anime, use `./gradlew` do repositório: Gradle, Kotlin e suas dependências são resolvidos pelo sistema de build; não instale Gradle ou Kotlin globalmente sem necessidade. ADB e emulador são opcionais para testes em dispositivos.

<details><summary>🐧 Arch Linux</summary>

Abra o Terminal e execute:

```bash
sudo pacman -S --needed git python nodejs npm curl unzip
```

Para mangá ou anime, instale o JDK exigido pelo projeto, por exemplo `sudo pacman -S --needed jdk21-openjdk` quando ele exigir Java 21. No bloco Android abaixo, instale Command-line Tools, plataforma e Build Tools conforme o projeto. Para novels, siga `npm install` acima.

</details>

<details><summary>🐧 Ubuntu ou Debian</summary>

Abra o Terminal e execute:

```bash
sudo apt update
sudo apt install git python3 nodejs npm curl unzip ca-certificates
```

Para mangá ou anime, se o projeto exigir Java 21 e o pacote existir em sua distribuição, execute `sudo apt install openjdk-21-jdk`. Para outra versão, consulte os pacotes da distribuição. Use o bloco Android abaixo. Para novels, siga `npm install` acima. Procedimento não testado nesta distribuição.

</details>

<details><summary>🐧 Fedora</summary>

Abra o Terminal e execute:

```bash
sudo dnf install git python3 nodejs npm curl unzip coreutils
```

Para mangá ou anime, quando o projeto exigir Java 21, execute `sudo dnf install java-21-openjdk-devel`. Para outra versão, consulte os pacotes disponíveis. Use o bloco Android abaixo. Para novels, siga `npm install` acima. Procedimento não testado nesta distribuição.

</details>

<details><summary>🪟 Windows</summary>

Os scripts de referências não funcionam no Windows nativo. No PowerShell, execute `wsl --install`, reinicie se solicitado e abra Ubuntu pelo menu Iniciar. Dentro do WSL, execute `sudo apt update && sudo apt install git python3 nodejs npm curl unzip ca-certificates`; verifique a versão do Node e instale Node 24 LTS se necessário. Para mangá/anime com Java 21, execute `sudo apt install openjdk-21-jdk` e use o bloco Android abaixo dentro do WSL. Para novels, use `npm install` no projeto. Instale sua IA no mesmo ambiente. Windows/WSL não foi homologado.

</details>

<details><summary>🍎 macOS</summary>

Abra o Terminal. Instale [Git](https://git-scm.com/downloads), [Python 3](https://www.python.org/downloads/) e [Node.js 24 LTS](https://nodejs.org/en/download) pelos instaladores oficiais. Para mangá ou anime, caso use Homebrew e o projeto exija Java 21, execute `brew install --cask temurin@21`; abra um novo terminal e confira `java -version`. Use o bloco Android abaixo com as ferramentas macOS. Para novels, siga `npm install` no projeto. Procedimento não testado no macOS.

</details>

Verifique as ferramentas instaladas no terminal:

```bash
git --version
python3 --version
node --version
npm --version
```

Para mangá ou anime, verifique também `java -version`, `javac -version` e `sdkmanager --list`. As versões Android dependem do projeto; não aceite licenças sem revisá-las. [Instruções detalhadas e solução de problemas](docs/pt-BR/guia.md).

### Etapa 2 — Android SDK para mangá e anime

Se você já possui `sdkmanager`, reutilize-o e pule o download. Caso contrário, baixe as **Command-line Tools** oficiais para seu sistema na [página Android](https://developer.android.com/studio#command-line-tools-only), confira o SHA-256 publicado e extraia o diretório `cmdline-tools` como `latest` dentro de `~/Android/Sdk/cmdline-tools/` (no WSL, dentro do Linux). Não substitua uma pasta `latest` existente. No Linux/WSL, o bloco abaixo baixa a versão 15859902 cujo checksum foi conferido na página oficial; se o destino já existir, pare e use sua instalação:

```bash
(
set -eu
SDK="$HOME/Android/Sdk"
test ! -e "$SDK/cmdline-tools/latest" || { echo "SDK existente: preserve e reutilize"; exit 1; }
test ! -e "$SDK/cmdline-tools/cmdline-tools" && test ! -e "$SDK/downloads/commandlinetools.zip" || { echo "Arquivos existentes: preserve e revise"; exit 1; }
mkdir -p "$SDK/cmdline-tools" "$SDK/downloads"
curl -fL -o "$SDK/downloads/commandlinetools.zip" https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip
echo "4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583  $SDK/downloads/commandlinetools.zip" | sha256sum -c -
unzip -q "$SDK/downloads/commandlinetools.zip" -d "$SDK/cmdline-tools"
mv "$SDK/cmdline-tools/cmdline-tools" "$SDK/cmdline-tools/latest"
)
```

No macOS, baixe o ZIP para seu processador pela página oficial; no Terminal execute `shasum -a 256 ~/Downloads/commandlinetools-*.zip` e compare o resultado com a página. Em seguida execute `mkdir -p ~/Android/Sdk/cmdline-tools`, extraia o ZIP com `unzip` nesse diretório e renomeie a pasta extraída `cmdline-tools` para `latest` somente se `latest` não existir. No Terminal Linux/WSL ou macOS:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

Leia e aceite as licenças pessoalmente. Verifique as versões no projeto; por exemplo, para um projeto que exige API 37.0 e Build Tools 37.0.0:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
```

Para usar ADB, instale opcionalmente `sdkmanager --sdk_root="$ANDROID_HOME" 'platform-tools'` e execute `adb version`. Acrescente as duas linhas `export` acima a `~/.bashrc` (Bash) ou `~/.zshrc` (Zsh) **somente após verificar que não conflitam com configurações existentes**, e abra outro terminal. Não modifique arquivos de configuração automaticamente. Emulador é opcional.

## 📥 Como instalar a skill

### Método 1 — Peça à sua IA ⭐ (Recomendado)

Sua IA verificará as dependências, ajudará na instalação e configurará a skill mediante sua autorização. Abra sua IA agêntica, copie o texto abaixo, envie e autorize apenas as operações com as quais concordar:

```text
Instale e configure a skill Nox Extension Developer:
https://github.com/Awerkori/nox-extension-developer

Consulte a documentação oficial e identifique meu sistema operacional e minha IA. Pergunte se desejo trabalhar com mangá, anime, novels ou todos. Verifique as ferramentas existentes e instale somente as necessárias, incluindo Java e Android SDK apenas quando aplicável. Solicite minha autorização antes de instalações, operações administrativas ou aceite de licenças. Não sobrescreva configurações nem exponha credenciais. Instale a skill via NPX, confirme sua descoberta em uma nova sessão e explique como criar, corrigir ou atualizar uma extensão.
```

[Baixar prompt em português](prompts/install-pt-BR.txt) · [English prompt](prompts/install-en.txt) · [Instalação manual](docs/pt-BR/guia.md#instalação)

### Método 2 — Instalação manual via NPX

Abra um terminal e execute:

```bash
npx skills add Awerkori/nox-extension-developer
```

Escolha sua IA quando o instalador perguntar. Para instalar globalmente no OpenCode:

```bash
npx skills add Awerkori/nox-extension-developer --global --agent opencode
```

Abra uma nova sessão da IA e peça: `Use a skill nox-extension-developer`. Confira se ela informa que carregou a skill. Para instalar em outro agente, consulte as opções de `npx skills add --help` e escolha o identificador correspondente. O instalador e as cópias locais podem usar pastas diferentes; consulte o destino informado na tela.

## 🚀 Como utilizar na prática

Substitua os textos entre colchetes pelo endereço do site ou do código.

### 📚 Mangá — criar
```text
Crie uma extensão de mangá seguindo o padrão Keiyoushi para o Mihon deste site: [URL DO SITE].
```

### 📚 Mangá — corrigir
```text
Corrija uma extensão de mangá seguindo o padrão Keiyoushi.

Repositório: [LINK DO REPOSITÓRIO DO KEIYOUSHI OU PROJECT NOX]
Nome da extensão: [NOME DA EXTENSÃO]

Problema:
Os capítulos não aparecem e as páginas não carregam.
```

Repositórios: [Keiyoushi](https://github.com/keiyoushi/extensions-source) · [Project Nox](https://github.com/Awerkori/manga-fonte-extensoes). Escolha o repositório, informe o nome da extensão e descreva o problema; a IA poderá localizar o código-fonte.

### 🎬 Anime — criar
```text
Crie uma extensão de anime seguindo o padrão Yuzono para o Aniyomi deste site: [URL DO SITE].
```

### 🎬 Anime — corrigir
```text
Corrija uma extensão de anime seguindo o padrão Yuzono.

Repositório: [LINK DO REPOSITÓRIO DO YUZONO OU PROJECT NOX]
Nome da extensão: [NOME DA EXTENSÃO]

Problema:
Os episódios não carregam e os vídeos não reproduzem.
```

Repositórios: [Yuzono](https://github.com/yuzono/anime-extensions) · [Project Nox](https://github.com/Awerkori/anime-fonte-extensoes). Escolha o repositório, informe o nome da extensão e descreva o problema; a IA poderá localizar o código-fonte.

### 📖 Novel — criar
```text
Crie uma extensão de novel para o LNReader deste site: [URL DO SITE].
```

### 📖 Novel — corrigir
```text
Corrija uma extensão de novel seguindo o padrão LNReader.

Repositório: [LINK DO REPOSITÓRIO DO LNREADER]
Nome da extensão: [NOME DA EXTENSÃO]

Problema:
A pesquisa não funciona e os capítulos não carregam.
```

Repositório: [LNReader](https://github.com/LNReader/lnreader-plugins). Informe o repositório, o nome da extensão e o problema; a IA poderá localizar o código-fonte.

Para atualizar uma extensão, envie seu código e peça à IA que preserve a compatibilidade. Peça o caminho do APK ou bundle e instruções para testá-lo. Revise o resultado e use somente fontes autorizadas.

## 🤖 Compatibilidade com IAs agênticas

| Agente | Status |
|---|---|
| [OpenCode](https://opencode.ai/) | ✅ Testado |
| [Codex](https://developers.openai.com/codex/) | ⚪ Não testado |
| [Claude Code](https://code.claude.com/) | ⚪ Não testado |
| [Google Antigravity](https://antigravity.google/) | ⚪ Não testado |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | ⚪ Não testado |

A skill foi desenvolvida e testada com OpenCode no ambiente Arch Linux do desenvolvedor. Outros agentes e sistemas podem ser compatíveis, mas não foram homologados.

## ❓ Perguntas frequentes

**Preciso saber programar?** Não para começar, mas revisar e manter extensões pode exigir ajuda técnica.

**A skill é gratuita? Preciso pagar pela IA?** A skill é gratuita. Custos e cotas dependem do agente e do modelo escolhidos.

**Preciso instalar uma IA local?** Não necessariamente; depende do serviço que você usar.

**Preciso do Android SDK?** Para compilar APKs de mangá ou anime, sim. Para apenas LNReader, não.

**Posso usar para criar ou corrigir extensões próprias e contribuir?** Sim, respeitando os direitos e regras dos sites e projetos envolvidos.

**Minha IA não reconheceu a skill.** Abra uma nova sessão, peça seu nome explicitamente e confira o destino informado pelo instalador. Veja [solução de problemas](docs/pt-BR/guia.md#solução-de-problemas).

**Como atualizo ou removo?** Consulte a CLI com `npx skills update --help` ou `npx skills remove --help`; para o instalador manual, preserve a pasta de origem e confira o link antes de removê-lo.

## 🤝 Suporte e contribuições

- [Issues](https://github.com/Awerkori/nox-extension-developer/issues): reporte problemas reproduzíveis.
- [Discussions](https://github.com/Awerkori/nox-extension-developer/discussions): tire dúvidas e compartilhe ideias.
- [Pull Requests](https://github.com/Awerkori/nox-extension-developer/pulls): envie melhorias; leia [como contribuir](CONTRIBUTING.md).
- [Releases](https://github.com/Awerkori/nox-extension-developer/releases): acompanhe atualizações.

Nunca publique senhas, tokens ou dados pessoais. Para vulnerabilidades, use o canal descrito em [SECURITY.md](SECURITY.md).

## 🔗 Projetos relacionados

- [Plataforma Web de Mangá](https://github.com/Awerkori/project-nox-manga) — leitor e plataforma web.
- [Importer](https://github.com/Awerkori/project-nox-importer) — importação de conteúdo.
- [Extensões de Mangá](https://github.com/Awerkori/manga-extensoes) · [Código-fonte](https://github.com/Awerkori/manga-fonte-extensoes).
- [Extensões de Anime](https://github.com/Awerkori/anime-extensoes) · [Código-fonte](https://github.com/Awerkori/anime-fonte-extensoes).
- [Central de Pedidos](https://github.com/Awerkori/project-nox-requests) · [Tracker](https://github.com/Awerkori/project-nox-tracker).

## 🌟 Créditos e reconhecimento

Criado por **Awerkori** para o **Project Nox**, com agradecimento à comunidade e aos colaboradores. [Keiyoushi](https://github.com/keiyoushi/extensions-source), [Yuzono](https://github.com/yuzono/anime-extensions), [LNReader](https://github.com/LNReader/lnreader-plugins) e o padrão [Agent Skills](https://agentskills.io/) são referências técnicas independentes. Consulte [atribuições](ATRIBUICOES.md).

## ⚖️ Licença e Copyright

Copyright © 2026 Awerkori. Software livre sob **GNU Affero General Public License versão 3.0 (`AGPL-3.0-only`)**. Leia o texto integral em [LICENSE](LICENSE).

> This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License, version 3. It is distributed WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

### 📌 Interação Remota de Rede (GNU AGPLv3 Seção 13)

Ao modificar o programa e permitir interação remota pela rede, ofereça aos usuários remotos acesso ao código-fonte correspondente da versão modificada, conforme a seção 13 da licença.

### 🛡️ Proteção de Identidade e Marca (AGPLv3 Seção 7(e))

A licença do software não concede automaticamente autorização para usar nomes ou logotipos do Project Nox e Awerkori para insinuar representação, aprovação ou endosso oficial.

### 🌐 Utilização e Redistribuição

Você pode usar, estudar, modificar e redistribuir a skill gratuitamente, observando os termos da AGPLv3 e as licenças de terceiros aplicáveis.

### ⚖️ Isenção de Responsabilidade

A skill auxilia o desenvolvimento; ela não concede direitos sobre conteúdo de terceiros nem garante o funcionamento das extensões. O programa é fornecido sem garantias, conforme a licença.
