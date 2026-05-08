# Zizie Mobile - Build Instructions

## Prerequisites

### macOS/Linux
```bash
# Install Node.js (>=18)
brew install node

# Install Java 17
brew install openjdk@17
export JAVA_HOME=$(brew --prefix openjdk@17)
```

### Generate Android Project

Since the android folder needs to be initialized:

```bash
cd zizie-mobile

# Install dependencies
npm install

# Initialize Android project
npx react-native-community_cli@latest init ZizieApp --pm npm

# Copy your src files to ZizieApp
cp -r src/* ZizieApp/app/src/
```

### Build APK

```bash
cd android

# Debug build
./gradlew assembleDebug

# Release build
./gradlew assembleRelease
```

## Output
- Debug APK: `android/app/build/outputs/apk/debug/app-debug.apk`
- Release APK: `android/app/build/outputs/apk/release/app-release.apk`

---

## Alternative: Use Expo EAS (Cloud Build)

```bash
# Install EAS CLI
npm install -g eas-cli

# Login
eas login

# Build for Android (creates .apk)
eas build -p android --profile development
```

This will build the APK in the cloud without needing local Java/Gradle.