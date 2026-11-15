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

### Etapa 1 — 📦 Instalação das dependências básicas

**👇 Clique no nome do seu sistema operacional para expandir o tutorial de instalação.**

<details>
<summary>🪟 Windows — Clique para expandir</summary>

Abra o PowerShell e execute `wsl --install`. Reinicie se necessário e abra o Ubuntu instalado. Execute os próximos comandos **no terminal Ubuntu do WSL**; Windows nativo não é suportado. WSL não foi homologado.

```bash
sudo apt update && sudo apt install git python3 nodejs npm curl unzip ca-certificates
```

Verifique as ferramentas:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

O Skills CLI 1.8.1 exige Node.js 22.20.0 ou superior; recomendamos Node 24 LTS. Se sua versão for mais antiga, use o [instalador oficial](https://nodejs.org/en/download) ou, após revisar o [nvm](https://github.com/nvm-sh/nvm), execute:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

Para novels, execute `npm install` dentro do projeto LNReader: ele instala TypeScript e bibliotecas conforme o `package.json`. Para carregar nvm em novos terminais, acrescente `export NVM_DIR="$HOME/.nvm"` e `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` ao `~/.bashrc` ou `~/.zshrc` somente após verificar entradas existentes.

</details>

<details>
<summary>🍎 macOS — Clique para expandir</summary>

Abra o Terminal. Se faltar Git, execute `xcode-select --install`. Instale Python 3 pelo [instalador oficial](https://www.python.org/downloads/) e Node 24 LTS pelo [instalador oficial](https://nodejs.org/en/download). Esta plataforma não foi homologada.

Verifique as ferramentas:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

O Skills CLI 1.8.1 exige Node.js 22.20.0 ou superior; recomendamos Node 24 LTS. Se sua versão for mais antiga, use o [instalador oficial](https://nodejs.org/en/download) ou, após revisar o [nvm](https://github.com/nvm-sh/nvm), execute:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

Para novels, execute `npm install` dentro do projeto LNReader: ele instala TypeScript e bibliotecas conforme o `package.json`. Para carregar nvm em novos terminais, acrescente `export NVM_DIR="$HOME/.nvm"` e `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` ao `~/.bashrc` ou `~/.zshrc` somente após verificar entradas existentes.

</details>

<details>
<summary>🐧 Arch Linux — Clique para expandir</summary>

Abra o Terminal e instale somente pacotes ausentes:

```bash
sudo pacman -S --needed git python nodejs npm curl unzip
```

Verifique as ferramentas:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

O Skills CLI 1.8.1 exige Node.js 22.20.0 ou superior; recomendamos Node 24 LTS. Se sua versão for mais antiga, use o [instalador oficial](https://nodejs.org/en/download) ou, após revisar o [nvm](https://github.com/nvm-sh/nvm), execute:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

Para novels, execute `npm install` dentro do projeto LNReader: ele instala TypeScript e bibliotecas conforme o `package.json`. Para carregar nvm em novos terminais, acrescente `export NVM_DIR="$HOME/.nvm"` e `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` ao `~/.bashrc` ou `~/.zshrc` somente após verificar entradas existentes.

</details>

<details>
<summary>🐧 Ubuntu — Clique para expandir</summary>

Abra o Terminal e instale somente pacotes ausentes:

```bash
sudo apt update && sudo apt install git python3 nodejs npm curl unzip ca-certificates
```

Não homologado nesta distribuição.

Verifique as ferramentas:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

O Skills CLI 1.8.1 exige Node.js 22.20.0 ou superior; recomendamos Node 24 LTS. Se sua versão for mais antiga, use o [instalador oficial](https://nodejs.org/en/download) ou, após revisar o [nvm](https://github.com/nvm-sh/nvm), execute:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

Para novels, execute `npm install` dentro do projeto LNReader: ele instala TypeScript e bibliotecas conforme o `package.json`. Para carregar nvm em novos terminais, acrescente `export NVM_DIR="$HOME/.nvm"` e `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` ao `~/.bashrc` ou `~/.zshrc` somente após verificar entradas existentes.

</details>

<details>
<summary>🐧 Debian — Clique para expandir</summary>

Abra o Terminal e instale somente pacotes ausentes:

```bash
sudo apt update && sudo apt install git python3 nodejs npm curl unzip ca-certificates
```

Não homologado nesta distribuição.

Verifique as ferramentas:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

O Skills CLI 1.8.1 exige Node.js 22.20.0 ou superior; recomendamos Node 24 LTS. Se sua versão for mais antiga, use o [instalador oficial](https://nodejs.org/en/download) ou, após revisar o [nvm](https://github.com/nvm-sh/nvm), execute:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

Para novels, execute `npm install` dentro do projeto LNReader: ele instala TypeScript e bibliotecas conforme o `package.json`. Para carregar nvm em novos terminais, acrescente `export NVM_DIR="$HOME/.nvm"` e `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` ao `~/.bashrc` ou `~/.zshrc` somente após verificar entradas existentes.

</details>

<details>
<summary>🐧 Fedora — Clique para expandir</summary>

Abra o Terminal e instale somente pacotes ausentes:

```bash
sudo dnf install git python3 nodejs npm curl unzip coreutils
```

Não homologado nesta distribuição.

Verifique as ferramentas:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

O Skills CLI 1.8.1 exige Node.js 22.20.0 ou superior; recomendamos Node 24 LTS. Se sua versão for mais antiga, use o [instalador oficial](https://nodejs.org/en/download) ou, após revisar o [nvm](https://github.com/nvm-sh/nvm), execute:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

Para novels, execute `npm install` dentro do projeto LNReader: ele instala TypeScript e bibliotecas conforme o `package.json`. Para carregar nvm em novos terminais, acrescente `export NVM_DIR="$HOME/.nvm"` e `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` ao `~/.bashrc` ou `~/.zshrc` somente após verificar entradas existentes.

</details>

### Etapa 2 — 🤖 Instalação do Android SDK

**Esta etapa é necessária para desenvolver extensões de mangá e anime. Se você deseja desenvolver apenas novels, pode pular esta etapa.**

**👇 Clique no seu sistema operacional para visualizar o tutorial completo do Android SDK.**

<details>
<summary>🪟 Windows (via WSL) — Clique para expandir</summary>

Execute no terminal Ubuntu do WSL, não no PowerShell. WSL não foi homologado. 1. Verifique `java -version` e `javac -version`. Se o projeto exigir JDK 21 e ele estiver ausente, execute o comando abaixo; para outra versão consulte os pacotes disponíveis:

```bash
sudo apt install openjdk-21-jdk
```

2. Se `sdkmanager --version` funcionar, reutilize a instalação e pule o download. Caso contrário, execute o bloco abaixo. Ele usa as Command-line Tools oficiais para Linux x86-64, verifica o SHA-256 e não sobrescreve uma instalação existente. A forma exata do bloco não foi testada integralmente; confira a [versão e checksum oficiais](https://developer.android.com/studio#command-line-tools-only):

```bash
(
set -eu
SDK="$HOME/Android/Sdk"
test ! -e "$SDK/cmdline-tools/latest" || { echo "Existing SDK: preserve and reuse"; exit 1; }
test ! -e "$SDK/cmdline-tools/cmdline-tools" && test ! -e "$SDK/downloads/commandlinetools.zip" || { echo "Existing files: preserve and review"; exit 1; }
mkdir -p "$SDK/cmdline-tools" "$SDK/downloads"
curl -fL -o "$SDK/downloads/commandlinetools.zip" https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip
echo "4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583  $SDK/downloads/commandlinetools.zip" | sha256sum -c -
unzip -q "$SDK/downloads/commandlinetools.zip" -d "$SDK/cmdline-tools"
mv "$SDK/cmdline-tools/cmdline-tools" "$SDK/cmdline-tools/latest"
)
```

3. Se seu SDK estiver em outro caminho, substitua `ANDROID_HOME` pelo caminho existente. Os comandos listam os componentes e pedem revisão das licenças; aceite-as pessoalmente:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Confira as versões exigidas pelo repositório. O exemplo abaixo é apenas para um projeto que exige API 37.0 e Build Tools 37.0.0; substitua se necessário:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

Para testar em dispositivo, instale ADB opcionalmente com `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` e confira `adb version`; emulador também é opcional. Para persistir as variáveis, adicione as duas linhas `export` ao `~/.bashrc` (Bash) ou `~/.zshrc` (Zsh), somente após verificar conflitos; abra outro terminal. Não sobrescreva configurações existentes. Gradle e Kotlin vêm do sistema de build do repositório via `./gradlew`, sem instalação global obrigatória.

</details>

<details>
<summary>🍎 macOS — Clique para expandir</summary>

macOS não foi homologado. 1. Verifique `java -version` e `javac -version`. Se o projeto exigir JDK 21 e ele estiver ausente, execute o comando abaixo; para outra versão consulte os pacotes disponíveis:

```bash
brew install --cask temurin@21
```

2. Se `sdkmanager --version` funcionar, reutilize a instalação e pule o download. Caso contrário, baixe o ZIP **Command-line Tools para macOS** do seu processador na [página oficial](https://developer.android.com/studio#command-line-tools-only). Execute `shasum -a 256 ~/Downloads/commandlinetools-*.zip` e compare com o SHA-256 publicado pelo Google. Não continue se for diferente. No Terminal, ajuste `ARQUIVO` para o nome exato baixado e execute; o bloco não substitui uma pasta existente:

```bash
(
set -eu
ARQUIVO="$HOME/Downloads/commandlinetools-mac.zip" # ajuste para o nome baixado / set downloaded name
SDK="$HOME/Android/Sdk"
test ! -e "$SDK/cmdline-tools/latest" && test ! -e "$SDK/cmdline-tools/cmdline-tools" || { echo "Existing files: preserve and review"; exit 1; }
mkdir -p "$SDK/cmdline-tools"
unzip -q "$ARQUIVO" -d "$SDK/cmdline-tools"
mv "$SDK/cmdline-tools/cmdline-tools" "$SDK/cmdline-tools/latest"
)
```

3. Se seu SDK estiver em outro caminho, substitua `ANDROID_HOME` pelo caminho existente. Os comandos listam os componentes e pedem revisão das licenças; aceite-as pessoalmente:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Confira as versões exigidas pelo repositório. O exemplo abaixo é apenas para um projeto que exige API 37.0 e Build Tools 37.0.0; substitua se necessário:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

Para testar em dispositivo, instale ADB opcionalmente com `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` e confira `adb version`; emulador também é opcional. Para persistir as variáveis, adicione as duas linhas `export` ao `~/.bashrc` (Bash) ou `~/.zshrc` (Zsh), somente após verificar conflitos; abra outro terminal. Não sobrescreva configurações existentes. Gradle e Kotlin vêm do sistema de build do repositório via `./gradlew`, sem instalação global obrigatória.

</details>

<details>
<summary>🐧 Arch Linux — Clique para expandir</summary>

1. Verifique `java -version` e `javac -version`. Se o projeto exigir JDK 21 e ele estiver ausente, execute o comando abaixo; para outra versão consulte os pacotes disponíveis:

```bash
sudo pacman -S --needed jdk21-openjdk
```

2. Se `sdkmanager --version` funcionar, reutilize a instalação e pule o download. Caso contrário, execute o bloco abaixo. Ele usa as Command-line Tools oficiais para Linux x86-64, verifica o SHA-256 e não sobrescreve uma instalação existente. A forma exata do bloco não foi testada integralmente; confira a [versão e checksum oficiais](https://developer.android.com/studio#command-line-tools-only):

```bash
(
set -eu
SDK="$HOME/Android/Sdk"
test ! -e "$SDK/cmdline-tools/latest" || { echo "Existing SDK: preserve and reuse"; exit 1; }
test ! -e "$SDK/cmdline-tools/cmdline-tools" && test ! -e "$SDK/downloads/commandlinetools.zip" || { echo "Existing files: preserve and review"; exit 1; }
mkdir -p "$SDK/cmdline-tools" "$SDK/downloads"
curl -fL -o "$SDK/downloads/commandlinetools.zip" https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip
echo "4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583  $SDK/downloads/commandlinetools.zip" | sha256sum -c -
unzip -q "$SDK/downloads/commandlinetools.zip" -d "$SDK/cmdline-tools"
mv "$SDK/cmdline-tools/cmdline-tools" "$SDK/cmdline-tools/latest"
)
```

3. Se seu SDK estiver em outro caminho, substitua `ANDROID_HOME` pelo caminho existente. Os comandos listam os componentes e pedem revisão das licenças; aceite-as pessoalmente:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Confira as versões exigidas pelo repositório. O exemplo abaixo é apenas para um projeto que exige API 37.0 e Build Tools 37.0.0; substitua se necessário:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

Para testar em dispositivo, instale ADB opcionalmente com `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` e confira `adb version`; emulador também é opcional. Para persistir as variáveis, adicione as duas linhas `export` ao `~/.bashrc` (Bash) ou `~/.zshrc` (Zsh), somente após verificar conflitos; abra outro terminal. Não sobrescreva configurações existentes. Gradle e Kotlin vêm do sistema de build do repositório via `./gradlew`, sem instalação global obrigatória.

</details>

<details>
<summary>🐧 Ubuntu — Clique para expandir</summary>

Não homologado nesta distribuição. 1. Verifique `java -version` e `javac -version`. Se o projeto exigir JDK 21 e ele estiver ausente, execute o comando abaixo; para outra versão consulte os pacotes disponíveis:

```bash
sudo apt install openjdk-21-jdk
```

2. Se `sdkmanager --version` funcionar, reutilize a instalação e pule o download. Caso contrário, execute o bloco abaixo. Ele usa as Command-line Tools oficiais para Linux x86-64, verifica o SHA-256 e não sobrescreve uma instalação existente. A forma exata do bloco não foi testada integralmente; confira a [versão e checksum oficiais](https://developer.android.com/studio#command-line-tools-only):

```bash
(
set -eu
SDK="$HOME/Android/Sdk"
test ! -e "$SDK/cmdline-tools/latest" || { echo "Existing SDK: preserve and reuse"; exit 1; }
test ! -e "$SDK/cmdline-tools/cmdline-tools" && test ! -e "$SDK/downloads/commandlinetools.zip" || { echo "Existing files: preserve and review"; exit 1; }
mkdir -p "$SDK/cmdline-tools" "$SDK/downloads"
curl -fL -o "$SDK/downloads/commandlinetools.zip" https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip
echo "4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583  $SDK/downloads/commandlinetools.zip" | sha256sum -c -
unzip -q "$SDK/downloads/commandlinetools.zip" -d "$SDK/cmdline-tools"
mv "$SDK/cmdline-tools/cmdline-tools" "$SDK/cmdline-tools/latest"
)
```

3. Se seu SDK estiver em outro caminho, substitua `ANDROID_HOME` pelo caminho existente. Os comandos listam os componentes e pedem revisão das licenças; aceite-as pessoalmente:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Confira as versões exigidas pelo repositório. O exemplo abaixo é apenas para um projeto que exige API 37.0 e Build Tools 37.0.0; substitua se necessário:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

Para testar em dispositivo, instale ADB opcionalmente com `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` e confira `adb version`; emulador também é opcional. Para persistir as variáveis, adicione as duas linhas `export` ao `~/.bashrc` (Bash) ou `~/.zshrc` (Zsh), somente após verificar conflitos; abra outro terminal. Não sobrescreva configurações existentes. Gradle e Kotlin vêm do sistema de build do repositório via `./gradlew`, sem instalação global obrigatória.

</details>

<details>
<summary>🐧 Debian — Clique para expandir</summary>

Não homologado nesta distribuição. 1. Verifique `java -version` e `javac -version`. Se o projeto exigir JDK 21 e ele estiver ausente, execute o comando abaixo; para outra versão consulte os pacotes disponíveis:

```bash
sudo apt install openjdk-21-jdk
```

2. Se `sdkmanager --version` funcionar, reutilize a instalação e pule o download. Caso contrário, execute o bloco abaixo. Ele usa as Command-line Tools oficiais para Linux x86-64, verifica o SHA-256 e não sobrescreve uma instalação existente. A forma exata do bloco não foi testada integralmente; confira a [versão e checksum oficiais](https://developer.android.com/studio#command-line-tools-only):

```bash
(
set -eu
SDK="$HOME/Android/Sdk"
test ! -e "$SDK/cmdline-tools/latest" || { echo "Existing SDK: preserve and reuse"; exit 1; }
test ! -e "$SDK/cmdline-tools/cmdline-tools" && test ! -e "$SDK/downloads/commandlinetools.zip" || { echo "Existing files: preserve and review"; exit 1; }
mkdir -p "$SDK/cmdline-tools" "$SDK/downloads"
curl -fL -o "$SDK/downloads/commandlinetools.zip" https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip
echo "4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583  $SDK/downloads/commandlinetools.zip" | sha256sum -c -
unzip -q "$SDK/downloads/commandlinetools.zip" -d "$SDK/cmdline-tools"
mv "$SDK/cmdline-tools/cmdline-tools" "$SDK/cmdline-tools/latest"
)
```

3. Se seu SDK estiver em outro caminho, substitua `ANDROID_HOME` pelo caminho existente. Os comandos listam os componentes e pedem revisão das licenças; aceite-as pessoalmente:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Confira as versões exigidas pelo repositório. O exemplo abaixo é apenas para um projeto que exige API 37.0 e Build Tools 37.0.0; substitua se necessário:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

Para testar em dispositivo, instale ADB opcionalmente com `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` e confira `adb version`; emulador também é opcional. Para persistir as variáveis, adicione as duas linhas `export` ao `~/.bashrc` (Bash) ou `~/.zshrc` (Zsh), somente após verificar conflitos; abra outro terminal. Não sobrescreva configurações existentes. Gradle e Kotlin vêm do sistema de build do repositório via `./gradlew`, sem instalação global obrigatória.

</details>

<details>
<summary>🐧 Fedora — Clique para expandir</summary>

Não homologado nesta distribuição. 1. Verifique `java -version` e `javac -version`. Se o projeto exigir JDK 21 e ele estiver ausente, execute o comando abaixo; para outra versão consulte os pacotes disponíveis:

```bash
sudo dnf install java-21-openjdk-devel
```

2. Se `sdkmanager --version` funcionar, reutilize a instalação e pule o download. Caso contrário, execute o bloco abaixo. Ele usa as Command-line Tools oficiais para Linux x86-64, verifica o SHA-256 e não sobrescreve uma instalação existente. A forma exata do bloco não foi testada integralmente; confira a [versão e checksum oficiais](https://developer.android.com/studio#command-line-tools-only):

```bash
(
set -eu
SDK="$HOME/Android/Sdk"
test ! -e "$SDK/cmdline-tools/latest" || { echo "Existing SDK: preserve and reuse"; exit 1; }
test ! -e "$SDK/cmdline-tools/cmdline-tools" && test ! -e "$SDK/downloads/commandlinetools.zip" || { echo "Existing files: preserve and review"; exit 1; }
mkdir -p "$SDK/cmdline-tools" "$SDK/downloads"
curl -fL -o "$SDK/downloads/commandlinetools.zip" https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip
echo "4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583  $SDK/downloads/commandlinetools.zip" | sha256sum -c -
unzip -q "$SDK/downloads/commandlinetools.zip" -d "$SDK/cmdline-tools"
mv "$SDK/cmdline-tools/cmdline-tools" "$SDK/cmdline-tools/latest"
)
```

3. Se seu SDK estiver em outro caminho, substitua `ANDROID_HOME` pelo caminho existente. Os comandos listam os componentes e pedem revisão das licenças; aceite-as pessoalmente:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Confira as versões exigidas pelo repositório. O exemplo abaixo é apenas para um projeto que exige API 37.0 e Build Tools 37.0.0; substitua se necessário:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

Para testar em dispositivo, instale ADB opcionalmente com `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` e confira `adb version`; emulador também é opcional. Para persistir as variáveis, adicione as duas linhas `export` ao `~/.bashrc` (Bash) ou `~/.zshrc` (Zsh), somente após verificar conflitos; abra outro terminal. Não sobrescreva configurações existentes. Gradle e Kotlin vêm do sistema de build do repositório via `./gradlew`, sem instalação global obrigatória.

</details>

## Etapa 3 — 📥 Instalação da skill

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
