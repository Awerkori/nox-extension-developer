# Android SDK para mangá e anime

[English](../en/android-sdk.md) · [Dependências](dependencias.md)

O ambiente OpenCode + Arch Linux do projeto usou JDK 21, Android SDK 37.0 e Build Tools 36.0.0/37.0.0. Esses números registram um teste, não requisitos universais. Confira `compileSdk`, arquivos de versão e wrapper do projeto de destino.

## Instalação segura

1. Verifique `java -version`, `javac -version`, `sdkmanager --version` e `adb version`. Reutilize instalações compatíveis.
2. Se faltar JDK, instale uma distribuição da versão exigida pelo projeto. Veja [OpenJDK](https://openjdk.org/install/).
3. Se faltar `sdkmanager`, obtenha [Android SDK Command-line Tools](https://developer.android.com/studio#command-line-tools-only) para seu sistema. Confira o checksum publicado pelo Google antes de extrair e siga a [estrutura oficial](https://developer.android.com/tools/sdkmanager). Não sobrescreva um SDK existente.
4. Configure `ANDROID_HOME` para o diretório escolhido e acrescente `cmdline-tools/latest/bin` e `platform-tools` ao `PATH`; veja [variáveis oficiais](https://developer.android.com/tools/variables). No Windows use `sdkmanager.bat`.
5. Execute `sdkmanager --list`, revise `sdkmanager --licenses` e aceite licenças pessoalmente. Com autorização, instale somente os pacotes exigidos. Exemplo, substituindo marcadores por versões verificadas:

```sh
sdkmanager "platform-tools" "platforms;android-<API>" "build-tools;<VERSÃO>"
```

6. Confira `adb version` e execute o Gradle Wrapper do repositório. ADB e emulador são opcionais quando não houver teste em aparelho. Leia o [guia oficial de emuladores](https://developer.android.com/studio/run/managing-avds) antes de instalá-los.

## Sistemas operacionais

Arch, Debian/Ubuntu e Fedora podem usar o mesmo procedimento oficial em terminal; veja [comandos básicos por distribuição](guia.md#preparação-por-sistema). No Windows e macOS use as ferramentas correspondentes ao sistema e siga a [instalação oficial](https://developer.android.com/studio/install). Apenas o ambiente Arch do projeto foi testado. Para executar os scripts desta skill em Windows, use WSL/Linux: `references.py` depende de `fcntl` e operações POSIX.

## Bloco para Arch Linux

O procedimento abaixo adapta a instalação isolada anteriormente executada no projeto. A versão e o SHA-256 das Command-line Tools foram verificados na época; antes de executar, confirme-os novamente na [página oficial](https://developer.android.com/studio#command-line-tools-only). Não foi executado integralmente nesta forma. Exige `curl`, `unzip`, `sha256sum` e JDK já instalados. O destino deve ser novo; o bloco não altera configurações existentes. Revise as licenças interativamente.

```bash
set -euo pipefail
SDK="$HOME/.local/share/android-sdk-nox"
test ! -e "$SDK" || { echo "Destino já existe: $SDK"; exit 1; }
java -version
javac -version
for cmd in curl unzip sha256sum; do command -v "$cmd" >/dev/null; done
mkdir -p "$SDK/cmdline-tools" "$SDK/downloads"
curl -fL --retry 2 -o "$SDK/downloads/tools.zip" https://dl.google.com/android/repository/commandlinetools-linux-15859902_latest.zip
echo "4e4c464f145a7512b57d088ac6c278c03c9eea610886b35a5e0804e74eedf583  $SDK/downloads/tools.zip" | sha256sum -c -
unzip -q "$SDK/downloads/tools.zip" -d "$SDK/cmdline-tools"
mv "$SDK/cmdline-tools/cmdline-tools" "$SDK/cmdline-tools/latest"
export ANDROID_HOME="$SDK"
export PATH="$SDK/cmdline-tools/latest/bin:$SDK/platform-tools:$PATH"
sdkmanager --sdk_root="$SDK" --licenses
sdkmanager --sdk_root="$SDK" "platform-tools" "platforms;android-37.0" "build-tools;36.0.0" "build-tools;37.0.0"
sdkmanager --sdk_root="$SDK" --list_installed
adb version
```

As variáveis `export` valem apenas no terminal atual. Configure-as permanentemente conforme a documentação oficial depois de revisar sua configuração. Se o projeto exigir outra plataforma, instale a versão correspondente; preserve o SDK anterior.
