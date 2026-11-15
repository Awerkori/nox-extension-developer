# Dependencies

[Português](../pt-BR/dependencias.md) · [Installation and troubleshooting](guide.md) · [Android SDK](android-sdk.md)

Install only what your task needs. `npx skills add` installs the skill; it does not configure Android or LNReader development dependencies. Check existing versions and target project build files first.

| Tool | Purpose and when required | Verify |
|---|---|---|
| Node.js and npm/NPX | Skills CLI installation; Node and project dependencies are also required for LNReader | `node --version`, `npm --version`, `npx --version` |
| Python 3 | Manual installer and reference/comparison scripts | `python3 --version` |
| Git | Resolves upstream HEAD and accesses repositories | `git --version` |
| JDK | Kotlin builds for manga and anime; not required for LNReader | `java -version`, `javac -version` |
| Android SDK and platform | Android libraries required by the manga or anime project | `sdkmanager --list` |
| Command-line Tools | Supplies `sdkmanager` to manage Android packages | `sdkmanager --version` |
| Build Tools | `aapt2`, `zipalign`, and APK build/signing tools | check `build-tools` in `sdkmanager --list` |
| Platform Tools | ADB for devices and emulators; optional without device testing | `adb version` |
| Gradle Wrapper | Builds using the repository's chosen version; global Gradle is unnecessary | `./gradlew --version` or `gradlew.bat --version` |
| TypeScript and Node package manager | LNReader development; use repository-local versions and scripts, not global installs | `node --version`, inspect `package.json` and lockfile |
| Emulator | Optional for testing the Android application; does not replace parser tests | see the [AVD manager](https://developer.android.com/studio/run/managing-avds) |

Installation and OS-specific commands: [guide](guide.md). Official SDK installation and licenses: [Android SDK](android-sdk.md). Requirements vary by upstream commit; inspect the project before selecting versions. Native Windows is not supported by the current scripts: use WSL/Linux. OpenCode + Arch Linux was tested; other environments are not validated.
