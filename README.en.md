[Português (Brasil)](README.md) | [English](README.en.md)

<p align="center"><img src="assets/banner.svg" alt="Project Nox — Nox Extension Developer" width="100%"></p>

# Project Nox · Extension Developer

A **free, open-source skill** that helps your AI create, fix, and update extensions. Describe what you need; the AI consults official references, analyzes the site, and guides development, testing, and builds.

| Content | Standard | App | Output |
|---|---|---|---|
| 📚 Manga | Keiyoushi | Mihon and forks | APK |
| 🎬 Anime | Yuzono | Aniyomi and forks | APK |
| 📖 Novel | LNReader | LNReader | Plugin / bundle |

Project Nox is not affiliated with the reference projects. Use only sites and content you are authorized to access. The skill assists development but cannot guarantee every site will work.

## 📦 Required tools

| Tool | Purpose | When to install |
|---|---|---|
| Git | Consult official repositories | For reference lookup |
| Python 3 | Runs skill scripts | To use the scripts |
| Node.js, npm and NPX | Install the skill from a terminal | NPX requires Node.js **22.20.0 or newer**; LNReader requires Node.js **22 or newer**. Node.js 24 LTS is recommended |
| Java JDK | Compiles Kotlin | For manga and anime, in the project-required version |
| Android SDK, Command-line Tools, platform and Build Tools | Prepare and build APKs | For manga and anime, as required by the project |
| LNReader dependencies and TypeScript | Develop novel plugins | For novels; use the project's own versions |
| ADB and emulator | Test on Android | Optional without device testing |

> **NPX installs the skill, not Java, Android SDK, or other development tools.**
>
> **If you only develop novels for LNReader, you do not need the Android SDK.**

The Gradle Wrapper and other tools may come with the project; global installation is not necessarily needed. See [dependencies](docs/en/dependencies.md).

## 💻 Install dependencies

### Step 1 — 📦 Install basic dependencies

**👇 Click your operating system to expand the installation guide.**

<details>
<summary>🪟 Windows — Click to expand</summary>

Open PowerShell and run `wsl --install`. Restart if needed and open the installed Ubuntu. Run the next commands **inside the WSL Ubuntu terminal**; native Windows is unsupported. WSL has not been validated.

```bash
sudo apt update && sudo apt install git python3 nodejs npm curl unzip ca-certificates
```

Check the tools:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

Skills CLI 1.8.1 requires Node.js 22.20.0 or newer; Node 24 LTS is recommended. If your version is older, use the [official installer](https://nodejs.org/en/download) or, after reviewing [nvm](https://github.com/nvm-sh/nvm), run:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

For novels, run `npm install` inside the LNReader project: it installs TypeScript and libraries according to `package.json`. To load nvm in new terminals, add `export NVM_DIR="$HOME/.nvm"` and `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` to `~/.bashrc` or `~/.zshrc` only after checking existing entries.

</details>

<details>
<summary>🍎 macOS — Click to expand</summary>

Open Terminal. If Git is missing, run `xcode-select --install`. Install Python 3 from its [official installer](https://www.python.org/downloads/) and Node 24 LTS from the [official installer](https://nodejs.org/en/download). This platform has not been validated.

Check the tools:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

Skills CLI 1.8.1 requires Node.js 22.20.0 or newer; Node 24 LTS is recommended. If your version is older, use the [official installer](https://nodejs.org/en/download) or, after reviewing [nvm](https://github.com/nvm-sh/nvm), run:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

For novels, run `npm install` inside the LNReader project: it installs TypeScript and libraries according to `package.json`. To load nvm in new terminals, add `export NVM_DIR="$HOME/.nvm"` and `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` to `~/.bashrc` or `~/.zshrc` only after checking existing entries.

</details>

<details>
<summary>🐧 Arch Linux — Click to expand</summary>

Open Terminal and install only missing packages:

```bash
sudo pacman -S --needed git python nodejs npm curl unzip
```

Check the tools:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

Skills CLI 1.8.1 requires Node.js 22.20.0 or newer; Node 24 LTS is recommended. If your version is older, use the [official installer](https://nodejs.org/en/download) or, after reviewing [nvm](https://github.com/nvm-sh/nvm), run:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

For novels, run `npm install` inside the LNReader project: it installs TypeScript and libraries according to `package.json`. To load nvm in new terminals, add `export NVM_DIR="$HOME/.nvm"` and `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` to `~/.bashrc` or `~/.zshrc` only after checking existing entries.

</details>

<details>
<summary>🐧 Ubuntu — Click to expand</summary>

Open Terminal and install only missing packages:

```bash
sudo apt update && sudo apt install git python3 nodejs npm curl unzip ca-certificates
```

Not validated on this distribution.

Check the tools:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

Skills CLI 1.8.1 requires Node.js 22.20.0 or newer; Node 24 LTS is recommended. If your version is older, use the [official installer](https://nodejs.org/en/download) or, after reviewing [nvm](https://github.com/nvm-sh/nvm), run:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

For novels, run `npm install` inside the LNReader project: it installs TypeScript and libraries according to `package.json`. To load nvm in new terminals, add `export NVM_DIR="$HOME/.nvm"` and `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` to `~/.bashrc` or `~/.zshrc` only after checking existing entries.

</details>

<details>
<summary>🐧 Debian — Click to expand</summary>

Open Terminal and install only missing packages:

```bash
sudo apt update && sudo apt install git python3 nodejs npm curl unzip ca-certificates
```

Not validated on this distribution.

Check the tools:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

Skills CLI 1.8.1 requires Node.js 22.20.0 or newer; Node 24 LTS is recommended. If your version is older, use the [official installer](https://nodejs.org/en/download) or, after reviewing [nvm](https://github.com/nvm-sh/nvm), run:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

For novels, run `npm install` inside the LNReader project: it installs TypeScript and libraries according to `package.json`. To load nvm in new terminals, add `export NVM_DIR="$HOME/.nvm"` and `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` to `~/.bashrc` or `~/.zshrc` only after checking existing entries.

</details>

<details>
<summary>🐧 Fedora — Click to expand</summary>

Open Terminal and install only missing packages:

```bash
sudo dnf install git python3 nodejs npm curl unzip coreutils
```

Not validated on this distribution.

Check the tools:

```bash
git --version && python3 --version && node --version && npm --version && npx --version
```

Skills CLI 1.8.1 requires Node.js 22.20.0 or newer; Node 24 LTS is recommended. If your version is older, use the [official installer](https://nodejs.org/en/download) or, after reviewing [nvm](https://github.com/nvm-sh/nvm), run:

```bash
if [ ! -e "$HOME/.nvm" ]; then git clone --branch v0.40.3 --depth 1 https://github.com/nvm-sh/nvm.git "$HOME/.nvm"; fi
export NVM_DIR="$HOME/.nvm"
. "$NVM_DIR/nvm.sh"
nvm install 24
nvm use 24
node --version && npm --version && npx --version
```

For novels, run `npm install` inside the LNReader project: it installs TypeScript and libraries according to `package.json`. To load nvm in new terminals, add `export NVM_DIR="$HOME/.nvm"` and `[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"` to `~/.bashrc` or `~/.zshrc` only after checking existing entries.

</details>

### Step 2 — 🤖 Install the Android SDK

**This step is required for manga and anime extensions. If you only develop novels, you can skip it.**

**👇 Click your operating system to see the complete Android SDK guide.**

<details>
<summary>🪟 Windows (via WSL) — Click to expand</summary>

Run in the WSL Ubuntu terminal, not PowerShell. WSL has not been validated. 1. Check `java -version` and `javac -version`. If your project requires JDK 21 and it is missing, run the following; for another version check available packages:

```bash
sudo apt install openjdk-21-jdk
```

2. If `sdkmanager --version` works, reuse it and skip the download. Otherwise run the block below. It uses official Linux x86-64 Command-line Tools, checks SHA-256, and does not overwrite an existing installation. This exact block was not tested end to end; check the [official version and checksum](https://developer.android.com/studio#command-line-tools-only):

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

3. If your SDK is elsewhere, replace `ANDROID_HOME` with its existing path. These commands list components and ask you to review licenses; accept them yourself:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Check versions required by the repository. The example below is only for a project requiring API 37.0 and Build Tools 37.0.0; replace if necessary:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

For device tests, optionally install ADB with `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` and check `adb version`; an emulator is optional too. To persist variables, add the two `export` lines to `~/.bashrc` (Bash) or `~/.zshrc` (Zsh) only after checking for conflicts; open another terminal. Do not overwrite existing settings. Gradle and Kotlin come from the repository build system through `./gradlew`, without mandatory global installation.

</details>

<details>
<summary>🍎 macOS — Click to expand</summary>

macOS has not been validated. 1. Check `java -version` and `javac -version`. If your project requires JDK 21 and it is missing, run the following; for another version check available packages:

```bash
brew install --cask temurin@21
```

2. If `sdkmanager --version` works, reuse it and skip the download. Otherwise download the **macOS Command-line Tools ZIP** for your processor from the [official page](https://developer.android.com/studio#command-line-tools-only). Run `shasum -a 256 ~/Downloads/commandlinetools-*.zip` and compare it to Google’s published SHA-256. Stop if it differs. In Terminal, set `ARQUIVO` to the exact downloaded filename and run; the block does not replace an existing directory:

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

3. If your SDK is elsewhere, replace `ANDROID_HOME` with its existing path. These commands list components and ask you to review licenses; accept them yourself:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Check versions required by the repository. The example below is only for a project requiring API 37.0 and Build Tools 37.0.0; replace if necessary:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

For device tests, optionally install ADB with `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` and check `adb version`; an emulator is optional too. To persist variables, add the two `export` lines to `~/.bashrc` (Bash) or `~/.zshrc` (Zsh) only after checking for conflicts; open another terminal. Do not overwrite existing settings. Gradle and Kotlin come from the repository build system through `./gradlew`, without mandatory global installation.

</details>

<details>
<summary>🐧 Arch Linux — Click to expand</summary>

1. Check `java -version` and `javac -version`. If your project requires JDK 21 and it is missing, run the following; for another version check available packages:

```bash
sudo pacman -S --needed jdk21-openjdk
```

2. If `sdkmanager --version` works, reuse it and skip the download. Otherwise run the block below. It uses official Linux x86-64 Command-line Tools, checks SHA-256, and does not overwrite an existing installation. This exact block was not tested end to end; check the [official version and checksum](https://developer.android.com/studio#command-line-tools-only):

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

3. If your SDK is elsewhere, replace `ANDROID_HOME` with its existing path. These commands list components and ask you to review licenses; accept them yourself:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Check versions required by the repository. The example below is only for a project requiring API 37.0 and Build Tools 37.0.0; replace if necessary:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

For device tests, optionally install ADB with `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` and check `adb version`; an emulator is optional too. To persist variables, add the two `export` lines to `~/.bashrc` (Bash) or `~/.zshrc` (Zsh) only after checking for conflicts; open another terminal. Do not overwrite existing settings. Gradle and Kotlin come from the repository build system through `./gradlew`, without mandatory global installation.

</details>

<details>
<summary>🐧 Ubuntu — Click to expand</summary>

Not validated on this distribution. 1. Check `java -version` and `javac -version`. If your project requires JDK 21 and it is missing, run the following; for another version check available packages:

```bash
sudo apt install openjdk-21-jdk
```

2. If `sdkmanager --version` works, reuse it and skip the download. Otherwise run the block below. It uses official Linux x86-64 Command-line Tools, checks SHA-256, and does not overwrite an existing installation. This exact block was not tested end to end; check the [official version and checksum](https://developer.android.com/studio#command-line-tools-only):

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

3. If your SDK is elsewhere, replace `ANDROID_HOME` with its existing path. These commands list components and ask you to review licenses; accept them yourself:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Check versions required by the repository. The example below is only for a project requiring API 37.0 and Build Tools 37.0.0; replace if necessary:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

For device tests, optionally install ADB with `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` and check `adb version`; an emulator is optional too. To persist variables, add the two `export` lines to `~/.bashrc` (Bash) or `~/.zshrc` (Zsh) only after checking for conflicts; open another terminal. Do not overwrite existing settings. Gradle and Kotlin come from the repository build system through `./gradlew`, without mandatory global installation.

</details>

<details>
<summary>🐧 Debian — Click to expand</summary>

Not validated on this distribution. 1. Check `java -version` and `javac -version`. If your project requires JDK 21 and it is missing, run the following; for another version check available packages:

```bash
sudo apt install openjdk-21-jdk
```

2. If `sdkmanager --version` works, reuse it and skip the download. Otherwise run the block below. It uses official Linux x86-64 Command-line Tools, checks SHA-256, and does not overwrite an existing installation. This exact block was not tested end to end; check the [official version and checksum](https://developer.android.com/studio#command-line-tools-only):

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

3. If your SDK is elsewhere, replace `ANDROID_HOME` with its existing path. These commands list components and ask you to review licenses; accept them yourself:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Check versions required by the repository. The example below is only for a project requiring API 37.0 and Build Tools 37.0.0; replace if necessary:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

For device tests, optionally install ADB with `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` and check `adb version`; an emulator is optional too. To persist variables, add the two `export` lines to `~/.bashrc` (Bash) or `~/.zshrc` (Zsh) only after checking for conflicts; open another terminal. Do not overwrite existing settings. Gradle and Kotlin come from the repository build system through `./gradlew`, without mandatory global installation.

</details>

<details>
<summary>🐧 Fedora — Click to expand</summary>

Not validated on this distribution. 1. Check `java -version` and `javac -version`. If your project requires JDK 21 and it is missing, run the following; for another version check available packages:

```bash
sudo dnf install java-21-openjdk-devel
```

2. If `sdkmanager --version` works, reuse it and skip the download. Otherwise run the block below. It uses official Linux x86-64 Command-line Tools, checks SHA-256, and does not overwrite an existing installation. This exact block was not tested end to end; check the [official version and checksum](https://developer.android.com/studio#command-line-tools-only):

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

3. If your SDK is elsewhere, replace `ANDROID_HOME` with its existing path. These commands list components and ask you to review licenses; accept them yourself:

```bash
export ANDROID_HOME="$HOME/Android/Sdk"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager --sdk_root="$ANDROID_HOME" --list
sdkmanager --sdk_root="$ANDROID_HOME" --licenses
```

4. Check versions required by the repository. The example below is only for a project requiring API 37.0 and Build Tools 37.0.0; replace if necessary:

```bash
sdkmanager --sdk_root="$ANDROID_HOME" 'platforms;android-37.0' 'build-tools;37.0.0'
java -version && javac -version
sdkmanager --sdk_root="$ANDROID_HOME" --list_installed
```

For device tests, optionally install ADB with `sdkmanager --sdk_root="$ANDROID_HOME" "platform-tools"` and check `adb version`; an emulator is optional too. To persist variables, add the two `export` lines to `~/.bashrc` (Bash) or `~/.zshrc` (Zsh) only after checking for conflicts; open another terminal. Do not overwrite existing settings. Gradle and Kotlin come from the repository build system through `./gradlew`, without mandatory global installation.

</details>

## Step 3 — 📥 Install the skill

### Method 1 — Ask your AI ⭐ (Recommended)

Your AI will check dependencies, assist with installation, and configure the skill with your permission. Open your agentic AI, copy the text below, send it, and authorize only the operations you agree to:

```text
Install and configure the Nox Extension Developer skill:
https://github.com/ProjectNox-org/nox-extension-developer

Consult the official documentation and identify my operating system and AI agent. Ask whether I want to work with manga, anime, novels, or all of them. Check existing tools and install only what is needed, including Java and Android SDK only when applicable. Ask permission before installations, privileged operations, or accepting licenses. Do not overwrite settings or expose credentials. Install the skill using NPX, verify discovery in a new session, and explain how to create, fix, or update an extension.
```

[Download English prompt](prompts/install-en.txt) · [Prompt em português](prompts/install-pt-BR.txt) · [Manual installation](docs/en/guide.md#installation)

### Method 2 — Manual installation via NPX

Open a terminal and run:

```bash
npx skills add ProjectNox-org/nox-extension-developer
```

Choose your AI when prompted. To install globally for OpenCode:

```bash
npx skills add ProjectNox-org/nox-extension-developer --global --agent opencode
```

Open a new AI session and ask: `Use the nox-extension-developer skill`. Confirm that it reports loading the skill. For another agent, see `npx skills add --help` and select its identifier. Installers and local copies may use different directories; check the reported destination.

## 🚀 Practical examples

Replace the bracketed text with the website or code address.

### 📚 Manga — create
```text
Create a manga extension following the Keiyoushi standard for Mihon for this site: [SITE URL].
```

### 📚 Manga — fix
```text
Fix a manga extension following the Keiyoushi standard.

Repository: [LINK TO THE KEIYOUSHI OR PROJECT NOX REPOSITORY]
Extension name: [EXTENSION NAME]

Problem:
Chapters do not appear and pages do not load.
```

Repositories: [Keiyoushi](https://github.com/keiyoushi/extensions-source) · [Project Nox](https://github.com/Awerkori/manga-fonte-extensoes). Choose a repository, provide the extension name, and describe the problem; the AI can locate the source code.

### 🎬 Anime — create
```text
Create an anime extension following the Yuzono standard for Aniyomi for this site: [SITE URL].
```

### 🎬 Anime — fix
```text
Fix an anime extension following the Yuzono standard.

Repository: [LINK TO THE YUZONO OR PROJECT NOX REPOSITORY]
Extension name: [EXTENSION NAME]

Problem:
Episodes do not load and videos do not play.
```

Repositories: [Yuzono](https://github.com/yuzono/anime-extensions) · [Project Nox](https://github.com/Awerkori/anime-fonte-extensoes). Choose a repository, provide the extension name, and describe the problem; the AI can locate the source code.

### 📖 Novel — create
```text
Create a novel extension for LNReader for this site: [SITE URL].
```

### 📖 Novel — fix
```text
Fix a novel extension following the LNReader standard.

Repository: [LINK TO THE LNREADER REPOSITORY]
Extension name: [EXTENSION NAME]

Problem:
Search does not work and chapters do not load.
```

Repository: [LNReader](https://github.com/LNReader/lnreader-plugins). Provide the repository, extension name, and problem; the AI can locate the source code.

To update an extension, provide its code and ask the AI to preserve compatibility. Ask for the APK or bundle path and testing instructions. Review the result and use only authorized sources.

## 🤖 Agent compatibility

| Agent | Status |
|---|---|
| [OpenCode](https://opencode.ai/) | ✅ Tested |
| [Codex](https://developers.openai.com/codex/) | ⚪ Not tested |
| [Claude Code](https://code.claude.com/) | ⚪ Not tested |
| [Google Antigravity](https://antigravity.google/) | ⚪ Not tested |
| [Hermes Agent](https://github.com/NousResearch/hermes-agent) | ⚪ Not tested |

The skill was developed and tested with OpenCode on the developer's Arch Linux workstation. Other agents and operating systems may be compatible but have not been validated.

## ❓ Frequently asked questions

**Do I need to know programming?** Not to start, but reviewing and maintaining extensions may require technical help.

**Is the skill free? Do I need to pay for AI?** The skill is free. Costs and quotas depend on the agent and model you choose.

**Do I need a local AI?** Not necessarily; it depends on the service you use.

**Do I need Android SDK?** Yes, to build manga or anime APKs. No, if you only use LNReader.

**Can I create or fix my own extensions and contribute?** Yes, respecting the rights and rules of the sites and projects involved.

**My AI did not recognize the skill.** Open a new session, explicitly ask for its name, and check the installer's reported destination. See [troubleshooting](docs/en/guide.md#troubleshooting).

**How do I update or remove it?** See `npx skills update --help` or `npx skills remove --help`; for manual installation, preserve the source folder and check the link before removal.

## 🤝 Support and contributions

- [Issues](https://github.com/ProjectNox-org/nox-extension-developer/issues): report reproducible problems.
- [Discussions](https://github.com/ProjectNox-org/nox-extension-developer/discussions): ask questions and share ideas.
- [Pull Requests](https://github.com/ProjectNox-org/nox-extension-developer/pulls): submit improvements; read [how to contribute](CONTRIBUTING.en.md).
- [Releases](https://github.com/ProjectNox-org/nox-extension-developer/releases): follow updates.

Never publish passwords, tokens, or personal data. For vulnerabilities, use the channel described in [SECURITY.md](SECURITY.md).

## 🔗 Related projects

- [Manga Web Platform](https://github.com/Awerkori/project-nox-manga) — web reader and platform.
- [Importer](https://github.com/Awerkori/project-nox-importer) — content import.
- [Manga Extensions](https://github.com/Awerkori/manga-extensoes) · [Source code](https://github.com/Awerkori/manga-fonte-extensoes).
- [Anime Extensions](https://github.com/Awerkori/anime-extensoes) · [Source code](https://github.com/Awerkori/anime-fonte-extensoes).
- [Requests](https://github.com/Awerkori/project-nox-requests) · [Tracker](https://github.com/Awerkori/project-nox-tracker).

## 🌟 Credits and recognition

Created by **Awerkori** for **Project Nox**, with thanks to the community and contributors. [Keiyoushi](https://github.com/keiyoushi/extensions-source), [Yuzono](https://github.com/yuzono/anime-extensions), [LNReader](https://github.com/LNReader/lnreader-plugins), and the [Agent Skills](https://agentskills.io/) standard are independent technical references. See [attributions](ATRIBUICOES.md).

## ⚖️ License and Copyright

Copyright © 2026 Awerkori. Free software under the **GNU Affero General Public License version 3.0 (`AGPL-3.0-only`)**. Read the full text in [LICENSE](LICENSE).

> This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License, version 3. It is distributed WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

### 📌 Remote Network Interaction (GNU AGPLv3 Section 13)

If you modify the program and let users interact with it remotely over a network, offer them access to the corresponding source of the modified version, as required by section 13.

### 🛡️ Identity and Trademark Protection (AGPLv3 Section 7(e))

The software license does not automatically authorize use of Project Nox or Awerkori names or logos to imply official representation, approval, or endorsement.

### 🌐 Use and Redistribution

You may use, study, modify, and redistribute the skill free of charge under AGPLv3 and applicable third-party licenses.

### ⚖️ Disclaimer

The skill assists software development; it grants no rights to third-party content and cannot guarantee that extensions will work. The program is provided without warranty as stated in the license.
