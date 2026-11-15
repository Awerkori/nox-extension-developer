# Dependências

[English](../en/dependencies.md) · [Instalação e solução de problemas](guia.md) · [Android SDK](android-sdk.md)

Instale apenas os componentes necessários. O comando `npx skills add` instala a skill, não configura automaticamente um ambiente Android ou LNReader. Confira primeiro as versões e os arquivos de build do projeto de destino.

| Ferramenta | Função e quando é necessária | Verificação |
|---|---|---|
| Node.js e npm/NPX | Instalação via Skills CLI; Node e dependências do projeto também são necessários para LNReader | `node --version`, `npm --version`, `npx --version` |
| Python 3 | Instalador manual e scripts de referências e comparação | `python3 --version` |
| Git | Consulta do HEAD oficial e acesso aos repositórios | `git --version` |
| JDK | Compilação Kotlin para mangá e anime; não exigido para LNReader | `java -version`, `javac -version` |
| Android SDK e plataforma | Bibliotecas Android exigidas pelo projeto de mangá ou anime | `sdkmanager --list` |
| Command-line Tools | `sdkmanager`, usado para gerenciar pacotes Android | `sdkmanager --version` |
| Build Tools | `aapt2`, `zipalign` e ferramentas de compilação/assinatura do APK | confira `build-tools` no resultado de `sdkmanager --list` |
| Platform Tools | ADB para conectar dispositivo ou emulador; opcional sem testes em aparelho | `adb version` |
| Gradle Wrapper | Compila com a versão definida pelo repositório; não requer Gradle global | `./gradlew --version` ou `gradlew.bat --version` |
| TypeScript e gerenciador Node | Desenvolvimento LNReader; use as versões e scripts locais do repositório, sem instalação global | `node --version`, confira `package.json` e lockfile |
| Emulador | Opcional para testar o aplicativo em Android; não substitui testes do parser | consulte o [gerenciador de AVDs](https://developer.android.com/studio/run/managing-avds) |

Instalação e comandos por sistema: [guia](guia.md). Instalação oficial e licenças do SDK: [Android SDK](android-sdk.md). Os requisitos variam por commit upstream; não fixe versões sem conferir o projeto. Windows nativo não é suportado pelos scripts atuais: use WSL/Linux. OpenCode + Arch Linux foi testado; outros ambientes não foram homologados.
