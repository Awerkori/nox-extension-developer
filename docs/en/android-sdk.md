# Android SDK for manga and anime

[Português](../pt-BR/android-sdk.md) · [Dependencies](dependencies.md)

The project's OpenCode + Arch Linux environment used JDK 21, Android SDK 37.0 and Build Tools 36.0.0/37.0.0. These record one test, not universal requirements. Inspect the target project's `compileSdk`, version files and wrapper.

## Safe installation

1. Check `java -version`, `javac -version`, `sdkmanager --version`, and `adb version`. Reuse compatible installations.
2. If the JDK is missing, install a distribution of the project-required version. See [OpenJDK](https://openjdk.org/install/).
3. If `sdkmanager` is missing, obtain [Android SDK Command-line Tools](https://developer.android.com/studio#command-line-tools-only) for your OS. Verify Google's published checksum before extraction and follow the [official layout](https://developer.android.com/tools/sdkmanager). Do not overwrite an existing SDK.
4. Set `ANDROID_HOME` to the chosen SDK directory and add `cmdline-tools/latest/bin` and `platform-tools` to `PATH`; see [official variables](https://developer.android.com/tools/variables). On Windows use `sdkmanager.bat`.
5. Run `sdkmanager --list`, review `sdkmanager --licenses`, and accept licenses yourself. With authorization, install only required packages. Example, replacing placeholders with verified versions:

```sh
sdkmanager "platform-tools" "platforms;android-<API>" "build-tools;<VERSION>"
```

6. Check `adb version` and run the repository's Gradle Wrapper. ADB and the emulator are optional without device testing. Read the [official emulator guide](https://developer.android.com/studio/run/managing-avds) before installing them.

## Operating systems

Arch, Debian/Ubuntu and Fedora can use the same official terminal procedure; see [distribution basics](guide.md#operating-system-preparation). On Windows and macOS use the OS-specific tools and [official installation instructions](https://developer.android.com/studio/install). Only the project's Arch environment was tested. To run this skill's scripts on Windows use WSL/Linux: `references.py` depends on `fcntl` and POSIX operations.

## Arch Linux block

The following adapts the isolated SDK installation previously performed for this project. The Command-line Tools version and SHA-256 were verified at that time; recheck them on the [official page](https://developer.android.com/studio#command-line-tools-only) before running. This exact block was not executed end to end. It requires `curl`, `unzip`, `sha256sum`, and a JDK already installed. The destination must be new; existing configurations are not changed. Review licenses interactively.

```bash
set -euo pipefail
SDK="$HOME/.local/share/android-sdk-nox"
test ! -e "$SDK" || { echo "Destination exists: $SDK"; exit 1; }
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

The `export` variables apply only to the current terminal. To make them available in new Bash terminals, open `~/.bashrc`, check for existing Android definitions, and add these lines only if they do not conflict; save and open a new terminal:

```bash
export ANDROID_HOME="$HOME/.local/share/android-sdk-nox"
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
```

For Zsh, use `~/.zshrc`. Do not overwrite existing settings. If the project requires another platform, install the corresponding version; preserve the previous SDK.
