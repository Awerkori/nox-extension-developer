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
| Node.js, npm and NPX | Install the skill from a terminal | For NPX; Node is also needed for LNReader |
| Java JDK | Compiles Kotlin | For manga and anime, in the project-required version |
| Android SDK, Command-line Tools, platform and Build Tools | Prepare and build APKs | For manga and anime, as required by the project |
| LNReader dependencies and TypeScript | Develop novel plugins | For novels; use the project's own versions |
| ADB and emulator | Test on Android | Optional without device testing |

> **NPX installs the skill, not Java, Android SDK, or other development tools.**
>
> **If you only develop novels for LNReader, you do not need the Android SDK.**

The Gradle Wrapper and other tools may come with the project; global installation is not necessarily needed. See [dependencies](docs/en/dependencies.md).

## 💻 Install dependencies

Open the section for your system. Install only missing tools and ask your AI for help if a command fails. Commands with `sudo` ask for your password and change your computer.

<details><summary>🐧 Arch Linux</summary>

Open Terminal and run:

```bash
sudo pacman -S --needed git python nodejs npm
```

For manga or anime, install the JDK your project requires, for example `sudo pacman -S --needed jdk21-openjdk` when it requires Java 21. Then follow the [Android SDK guide](docs/en/android-sdk.md), including the installation block and license review.

</details>

<details><summary>🐧 Ubuntu or Debian</summary>

Open Terminal and run:

```bash
sudo apt update
sudo apt install git python3 nodejs npm
```

For manga or anime, install your project's required JDK from your distribution repositories and follow the [Android SDK guide](docs/en/android-sdk.md). This procedure was not tested on this distribution.

</details>

<details><summary>🐧 Fedora</summary>

Open Terminal and run:

```bash
sudo dnf install git python3 nodejs npm
```

For manga or anime, install your project's required JDK and follow the [Android SDK guide](docs/en/android-sdk.md). This procedure was not tested on this distribution.

</details>

<details><summary>🪟 Windows</summary>

The skill's reference scripts require Linux features. Open PowerShell and install [WSL](https://learn.microsoft.com/windows/wsl/install) with `wsl --install`; restart if prompted. Open Ubuntu from the Start menu and follow the Ubuntu instructions above **inside WSL**. Install your AI in the same environment and follow the [Android SDK guide](docs/en/android-sdk.md) when needed. Windows/WSL has not been validated.

</details>

<details><summary>🍎 macOS</summary>

Open Terminal. Install [Git](https://git-scm.com/downloads), [Python 3](https://www.python.org/downloads/), and [Node.js](https://nodejs.org/en/download) using official installers. For manga or anime, install a compatible [JDK](https://openjdk.org/install/) and follow the [Android SDK guide](docs/en/android-sdk.md). This procedure was not tested on macOS.

</details>

Check installed tools in the terminal:

```bash
git --version
python3 --version
node --version
npm --version
```

For manga or anime, also check `java -version`, `javac -version`, and `sdkmanager --list`. Android versions depend on the project; review licenses before accepting them. [Detailed instructions and troubleshooting](docs/en/guide.md).

## 📥 Install the skill

### Method 1 — terminal

Open a terminal and run:

```bash
npx skills add Awerkori/nox-extension-developer
```

Choose your AI when prompted. To install globally for OpenCode:

```bash
npx skills add Awerkori/nox-extension-developer --global --agent opencode
```

Open a new AI session and ask: `Use the nox-extension-developer skill`. Confirm that it reports loading the skill. For another agent, see `npx skills add --help` and select its identifier. Installers and local copies may use different directories; check the reported destination.

### Method 2 — ask your AI ⭐

Open your agentic AI, copy the text below, send it, and authorize only the operations you agree to:

```text
Install and configure the Nox Extension Developer skill:
https://github.com/Awerkori/nox-extension-developer

Consult the official documentation and identify my operating system and AI agent. Ask whether I want to work with manga, anime, novels, or all of them. Check existing tools and install only what is needed, including Java and Android SDK only when applicable. Ask permission before installations, privileged operations, or accepting licenses. Do not overwrite settings or expose credentials. Install the skill using NPX, verify discovery in a new session, and explain how to create, fix, or update an extension.
```

[Download English prompt](prompts/install-en.txt) · [Prompt em português](prompts/install-pt-BR.txt) · [Manual installation](docs/en/guide.md#installation)

## 🚀 Practical examples

Replace the bracketed text with the website or code address.

### 📚 Manga — create
```text
Create a manga extension following the Keiyoushi standard for Mihon for this site: [SITE URL].
```

### 📚 Manga — fix
```text
Fix this extension following the Keiyoushi standard: [CODE LINK].

Chapters do not appear and pages do not load.
```

### 🎬 Anime — create
```text
Create an anime extension following the Yuzono standard for Aniyomi for this site: [SITE URL].
```

### 🎬 Anime — fix
```text
Fix this extension following the Yuzono standard: [CODE LINK].

Episodes do not load and videos do not play.
```

### 📖 Novel — create
```text
Create a novel extension for LNReader for this site: [SITE URL].
```

### 📖 Novel — fix
```text
Fix this LNReader extension: [CODE LINK].

Search does not work and chapters do not load.
```

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

- [Issues](https://github.com/Awerkori/nox-extension-developer/issues): report reproducible problems.
- [Discussions](https://github.com/Awerkori/nox-extension-developer/discussions): ask questions and share ideas.
- [Pull Requests](https://github.com/Awerkori/nox-extension-developer/pulls): submit improvements; read [how to contribute](CONTRIBUTING.en.md).
- [Releases](https://github.com/Awerkori/nox-extension-developer/releases): follow updates.

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
