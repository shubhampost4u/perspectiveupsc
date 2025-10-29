# 🔨 Build Guide - Perspective UPSC Android App

Complete step-by-step guide to build the Android app from scratch.

---

## Prerequisites

### Required Software
1. **Android Studio** (Hedgehog 2023.1.1 or newer)
   - Download: https://developer.android.com/studio
   - Size: ~1GB download, ~4GB installed

2. **Java Development Kit (JDK 17)**
   - Included with Android Studio
   - Or download separately: https://adoptium.net/

3. **Android SDK**
   - Installed via Android Studio
   - Required: Android SDK Platform 34 (Android 14)
   - Minimum: Android SDK Platform 24 (Android 7.0)

---

## Step 1: Install Android Studio

### Windows
1. Download Android Studio from https://developer.android.com/studio
2. Run the installer (.exe file)
3. Follow installation wizard
4. Install Android SDK, Android SDK Platform, and Android Virtual Device
5. Click "Finish" when done

### macOS
1. Download Android Studio DMG
2. Drag Android Studio to Applications folder
3. Open Android Studio from Applications
4. Follow setup wizard
5. Install SDK components

### Linux
```bash
# Extract downloaded tar.gz
tar -xvf android-studio-*.tar.gz

# Move to /opt
sudo mv android-studio /opt/

# Run Android Studio
/opt/android-studio/bin/studio.sh
```

---

## Step 2: Open Project

1. Launch Android Studio
2. Click **"Open"** on welcome screen
3. Navigate to your `/app/android` folder
4. Click **"OK"**
5. Wait for **Gradle Sync** to complete (2-5 minutes first time)

### If Gradle Sync Fails:
```bash
# Option 1: Invalidate Caches
File → Invalidate Caches → Invalidate and Restart

# Option 2: Clean Project
Build → Clean Project
Build → Rebuild Project

# Option 3: Manual Gradle sync
./gradlew clean
./gradlew build
```

---

## Step 3: Configure SDK

1. Go to **File → Project Structure** (Ctrl+Alt+Shift+S)
2. Under **SDK Location**, verify:
   - Android SDK Location is set
   - JDK Location is set (JDK 17)
3. Under **Modules**, verify:
   - Compile SDK Version: 34
   - Build Tools Version: Latest
   - Source Compatibility: 17
   - Target Compatibility: 17

---

## Step 4: Add App Icon

### Method 1: Using Android Studio (Recommended)
1. Right-click on `res` folder
2. Select **New → Image Asset**
3. Configure:
   - **Icon Type:** Launcher Icons (Adaptive and Legacy)
   - **Name:** ic_launcher
   - **Path:** Select your 512x512 PNG icon
4. Click **Next → Finish**

### Method 2: Manual (Multiple Sizes)
Add icons to these folders with correct sizes:
```
res/mipmap-mdpi/ic_launcher.png (48x48)
res/mipmap-hdpi/ic_launcher.png (72x72)
res/mipmap-xhdpi/ic_launcher.png (96x96)
res/mipmap-xxhdpi/ic_launcher.png (144x144)
res/mipmap-xxxhdpi/ic_launcher.png (192x192)
```

### Icon Resources:
- Create icon: https://icon.kitchen/
- Free icons: https://www.flaticon.com/
- Icon generator: https://romannurik.github.io/AndroidAssetStudio/

---

## Step 5: Customize App

### Update BASE_URL (if needed)
Open `MainActivity.java` and modify:
```java
private static final String BASE_URL = "https://www.perspectiveupsc.com";
```

### Update Colors
Edit `res/values/colors.xml`:
```xml
<color name="colorPrimary">#YOUR_COLOR</color>
<color name="colorPrimaryDark">#YOUR_DARK_COLOR</color>
<color name="colorAccent">#YOUR_ACCENT_COLOR</color>
```

### Update Strings
Edit `res/values/strings.xml`:
```xml
<string name="app_name">Perspective UPSC</string>
```

---

## Step 6: Build Debug APK (Testing)

### Method 1: Using Android Studio
1. Click **Build → Build Bundle(s) / APK(s) → Build APK(s)**
2. Wait for build to complete (1-2 minutes)
3. Click **"locate"** in notification
4. APK located at: `app/build/outputs/apk/debug/app-debug.apk`

### Method 2: Using Command Line
```bash
# Navigate to android folder
cd /app/android

# Make gradlew executable (Linux/Mac)
chmod +x gradlew

# Build debug APK
./gradlew assembleDebug

# Windows
gradlew.bat assembleDebug

# Find APK
# Location: app/build/outputs/apk/debug/app-debug.apk
```

### Build Time
- First build: 5-10 minutes (downloads dependencies)
- Subsequent builds: 30-60 seconds

---

## Step 7: Test on Device

### Enable USB Debugging on Android Phone
1. Go to **Settings → About Phone**
2. Tap **Build Number** 7 times (enables Developer Options)
3. Go back to **Settings → Developer Options**
4. Enable **USB Debugging**
5. Connect phone to computer via USB
6. Allow debugging on phone popup

### Install and Test
1. In Android Studio, click **Run** (green play button)
2. Select your connected device
3. App will install and launch
4. Test all features:
   - ✅ App loads website
   - ✅ Pull to refresh works
   - ✅ Back button navigation
   - ✅ File upload works
   - ✅ Offline page shows when no internet

### Install APK Directly
```bash
# Using adb (Android Debug Bridge)
adb install app/build/outputs/apk/debug/app-debug.apk

# Or transfer APK to phone and install manually
```

---

## Step 8: Generate Signing Key (Required for Play Store)

### Create Keystore
```bash
# Using keytool (comes with JDK)
keytool -genkey -v -keystore perspectiveupsc.keystore \
  -alias perspectiveupsc \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000

# You'll be prompted for:
# 1. Keystore password (CREATE A STRONG PASSWORD!)
# 2. Key password (can be same as keystore)
# 3. Your name
# 4. Organization unit (optional)
# 5. Organization name (optional)
# 6. City
# 7. State
# 8. Country code (US, IN, etc.)
```

**CRITICAL: Backup this keystore file! You can NEVER recover it if lost!**

### Create keystore.properties
Create file `android/keystore.properties`:
```properties
storePassword=YOUR_STORE_PASSWORD
keyPassword=YOUR_KEY_PASSWORD
keyAlias=perspectiveupsc
storeFile=../perspectiveupsc.keystore
```

**Add to .gitignore:**
```
*.keystore
keystore.properties
```

### Update app/build.gradle
Add before `android {` block:
```gradle
def keystorePropertiesFile = rootProject.file("keystore.properties")
def keystoreProperties = new Properties()
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}
```

Add inside `android {` block:
```gradle
signingConfigs {
    release {
        if (keystorePropertiesFile.exists()) {
            keyAlias keystoreProperties['keyAlias']
            keyPassword keystoreProperties['keyPassword']
            storeFile file(keystoreProperties['storeFile'])
            storePassword keystoreProperties['storePassword']
        }
    }
}

buildTypes {
    release {
        signingConfig signingConfigs.release
        // ... rest of release config
    }
}
```

---

## Step 9: Build Release APK (For Play Store)

### Method 1: Using Android Studio
1. Click **Build → Generate Signed Bundle / APK**
2. Select **APK**
3. Click **Next**
4. Choose keystore file
5. Enter passwords
6. Select **release** build variant
7. Click **Finish**
8. APK located at: `app/release/app-release.apk`

### Method 2: Using Command Line
```bash
# Build release APK
./gradlew assembleRelease

# Location: app/build/outputs/apk/release/app-release.apk
```

### Verify APK
```bash
# Check APK signature
jarsigner -verify -verbose -certs app-release.apk

# Get APK info
aapt dump badging app-release.apk
```

---

## Step 10: Build Android App Bundle (AAB) - Recommended

**Google Play prefers AAB over APK (smaller download size for users)**

### Using Android Studio
1. Click **Build → Generate Signed Bundle / APK**
2. Select **Android App Bundle**
3. Follow same signing steps as APK
4. AAB located at: `app/release/app-release.aab`

### Using Command Line
```bash
./gradlew bundleRelease

# Location: app/build/outputs/bundle/release/app-release.aab
```

### Benefits of AAB over APK
- ✅ Smaller download size (Google optimizes per device)
- ✅ Required for apps over 150MB
- ✅ Supports Play Feature Delivery
- ✅ Recommended by Google

---

## Troubleshooting

### Build Fails with "SDK not found"
```bash
# Set ANDROID_HOME environment variable
export ANDROID_HOME=~/Android/Sdk  # Linux/Mac
set ANDROID_HOME=C:\Users\YourName\AppData\Local\Android\Sdk  # Windows

# Or set in Android Studio:
File → Project Structure → SDK Location
```

### "Gradle sync failed"
1. Check internet connection (needs to download dependencies)
2. Update Gradle: File → Project Structure → Project → Gradle Version
3. Invalidate caches: File → Invalidate Caches → Restart

### "Manifest merger failed"
- Check AndroidManifest.xml for errors
- Ensure all permissions are properly formatted

### "Duplicate class found"
- Clean project: Build → Clean Project
- Rebuild: Build → Rebuild Project

### Build is very slow
1. Enable offline mode: File → Settings → Build → Gradle → Offline work
2. Increase Gradle memory in `gradle.properties`:
   ```
   org.gradle.jvmargs=-Xmx4096m
   ```

---

## Build Optimization

### Speed Up Builds
1. **Enable parallel builds**
   `gradle.properties`:
   ```
   org.gradle.parallel=true
   org.gradle.configureondemand=true
   ```

2. **Use build cache**
   ```
   android.enableBuildCache=true
   ```

3. **Increase heap size**
   ```
   org.gradle.jvmargs=-Xmx4096m -XX:MaxPermSize=1024m
   ```

### Reduce APK Size
1. **Enable ProGuard/R8** (already enabled in release)
2. **Use vector drawables** instead of PNGs
3. **Enable resource shrinking**
4. **Use WebP format** for images

---

## Version Management

Update in `app/build.gradle`:
```gradle
defaultConfig {
    versionCode 1        // Increment for each release (1, 2, 3, ...)
    versionName "1.0.0"  // Display version (1.0.0, 1.1.0, 2.0.0, ...)
}
```

**Version Naming Convention:**
- **Major.Minor.Patch** (Semantic Versioning)
- 1.0.0 - Initial release
- 1.0.1 - Bug fixes
- 1.1.0 - New features
- 2.0.0 - Major changes

---

## Build Artifacts

After successful build:
```
app/build/outputs/
├── apk/
│   ├── debug/
│   │   └── app-debug.apk (for testing)
│   └── release/
│       └── app-release.apk (for Play Store)
├── bundle/
│   └── release/
│       └── app-release.aab (recommended for Play Store)
└── mapping/
    └── release/
        └── mapping.txt (ProGuard mappings - keep for crash reports)
```

---

## Next Steps

1. ✅ Test debug APK on multiple devices
2. ✅ Build release APK/AAB with signing
3. ✅ Test release build thoroughly
4. ✅ Prepare Play Store listing (see PLAYSTORE_GUIDE.md)
5. ✅ Upload to Google Play Console
6. ✅ Submit for review

---

## Useful Commands

```bash
# Clean build
./gradlew clean

# Build debug
./gradlew assembleDebug

# Build release
./gradlew assembleRelease

# Build AAB
./gradlew bundleRelease

# Install on connected device
./gradlew installDebug

# Uninstall from device
./gradlew uninstallDebug

# Run tests
./gradlew test

# Check dependencies
./gradlew dependencies

# List all tasks
./gradlew tasks
```

---

**Build time:** First build ~10 minutes, subsequent builds ~1 minute  
**APK size:** ~3-5 MB (WebView app is lightweight!)  
**Support:** Check logs in Android Studio → Logcat for errors

**Ready to build? Let's go! 🚀**
