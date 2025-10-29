# 🪟 Complete Android Studio Installation Guide for Windows

**For:** Perspective UPSC Android App Development  
**Platform:** Windows 10/11  
**Time Required:** 30-45 minutes

---

## ✅ Prerequisites Check

Before starting, make sure you have:
- ✅ Windows 10 or Windows 11
- ✅ At least 8GB RAM (16GB recommended)
- ✅ At least 10GB free disk space (20GB recommended)
- ✅ Internet connection (for downloading ~1GB)
- ✅ Administrator access on your computer

---

## 📥 Step 1: Download Android Studio

### 1.1 Open Your Web Browser
- Open **Google Chrome**, **Edge**, or **Firefox**

### 1.2 Go to Android Studio Website
- Visit: **https://developer.android.com/studio**
- You should see a big green button saying **"Download Android Studio"**

### 1.3 Download the Installer
1. Click the **"Download Android Studio"** button
2. A terms dialog will appear
3. **Check the box** "I have read and agree with the above terms and conditions"
4. Click **"Download Android Studio Hedgehog"** (or whatever current version)
5. File will download: `android-studio-2023.x.x.xx-windows.exe` (~1GB)
6. Wait for download to complete (5-15 minutes depending on internet speed)

**Download Location:** Usually goes to your `Downloads` folder

---

## 🔧 Step 2: Install Android Studio

### 2.1 Run the Installer
1. Go to your **Downloads** folder
2. Find `android-studio-2023.x.x.xx-windows.exe`
3. **Right-click** on it
4. Select **"Run as administrator"**
5. If Windows asks "Do you want to allow this app to make changes?", click **"Yes"**

### 2.2 Installation Wizard - Screen 1: Welcome
- Click **"Next"**

### 2.3 Installation Wizard - Screen 2: Choose Components
You should see checkboxes:
- ✅ **Android Studio** (already checked)
- ✅ **Android Virtual Device** (CHECK THIS - for testing without phone)

Click **"Next"**

### 2.4 Installation Wizard - Screen 3: License Agreement
- Read the license (or scroll to bottom)
- Click **"I Agree"**

### 2.5 Installation Wizard - Screen 4: Installation Location
- Default location is fine: `C:\Program Files\Android\Android Studio`
- If you have limited space on C: drive, you can change it
- Click **"Next"**

### 2.6 Installation Wizard - Screen 5: Start Menu Folder
- Keep default: "Android Studio"
- Click **"Install"**

### 2.7 Wait for Installation
- Progress bar will show installation progress
- This takes 5-10 minutes
- **DO NOT close the window**

### 2.8 Installation Complete
- You'll see "Completing Android Studio Setup"
- ✅ **Check** "Start Android Studio"
- Click **"Finish"**

---

## ⚙️ Step 3: First Time Setup

### 3.1 Import Settings
- A dialog will appear: "Import Android Studio Settings From..."
- Select **"Do not import settings"**
- Click **"OK"**

### 3.2 Data Sharing
- "Help improve Android Studio..."
- Choose **"Don't send"** or **"Send"** (your choice)
- Click **"Next"**

### 3.3 Welcome Screen
- You'll see "Welcome to Android Studio"
- Click **"Next"**

### 3.4 Install Type
- Select **"Standard"** (recommended)
- Click **"Next"**

### 3.5 Select UI Theme
- Choose theme (Light or Dark)
- **Recommendation:** Darcula (dark theme, easier on eyes)
- Click **"Next"**

### 3.6 Verify Settings
- Review what will be installed:
  - Android SDK
  - Android SDK Platform
  - Performance (Intel HAXM if available)
  - Android Virtual Device
- Click **"Next"**

### 3.7 License Agreements
You'll see multiple license agreements:
1. **android-sdk-license** 
   - Click to expand
   - Scroll to bottom
   - Click **"Accept"**
2. **android-sdk-arm-dbt-license** (if shown)
   - Click to expand
   - Click **"Accept"**
3. Repeat for any other licenses shown

After accepting all, click **"Finish"**

### 3.8 Downloading Components
- Android Studio will now download required components
- This takes 15-30 minutes (downloads ~3GB)
- Progress shows: "Downloading..."
- **Wait patiently, don't close!**

### 3.9 Setup Complete
- When done, you'll see "Finish" button
- Click **"Finish"**

---

## 🎉 Step 4: Android Studio is Installed!

You should now see the **Android Studio Welcome Screen** with options:
- New Project
- Open
- Get from VCS

**Congratulations! Android Studio is installed! 🎉**

---

## 📱 Step 5: Open Your Perspective UPSC Project

### 5.1 Prepare Your Project Files

First, you need to get the Android project files from `/app/android/` to your local computer.

**Option A: If files are already on your computer**
- Make sure you have the `/app/android/` folder accessible

**Option B: If files need to be downloaded**
- Download/copy the entire `android` folder from your project
- Save it somewhere accessible, like: `C:\Users\YourName\AndroidProjects\android`

### 5.2 Open the Project

1. On Android Studio Welcome Screen, click **"Open"**
2. A file browser will open
3. Navigate to where you saved the `android` folder
4. Select the `android` folder (the one containing `build.gradle`, `app` folder, etc.)
5. Click **"OK"**

### 5.3 Trust Project
- Android Studio may ask "Trust and Open Project?"
- Click **"Trust Project"**

### 5.4 Gradle Sync (First Time - Takes Time!)
- Android Studio will start **"Gradle Sync"**
- Bottom of screen shows: "Gradle Sync in progress..."
- **This is NORMAL and takes 5-15 minutes the first time**
- It's downloading project dependencies
- **DO NOT close Android Studio!**

You'll see progress messages like:
- "Syncing..."
- "Downloading dependencies..."
- "Building Gradle project info..."

### 5.5 Gradle Sync Complete
When done, you'll see one of these:
- ✅ **"Gradle sync finished"** (Success! ✅)
- ❌ **"Gradle sync failed"** (See troubleshooting below)

---

## 🔨 Step 6: Build Your APK

### 6.1 Build Debug APK (For Testing)

1. In Android Studio menu bar, click **"Build"**
2. Select **"Build Bundle(s) / APK(s)"**
3. Click **"Build APK(s)"**
4. Wait for build to complete (1-3 minutes)
5. You'll see notification: **"Build APK(s) completed successfully"**
6. Click **"locate"** in the notification

**Your APK is at:**
```
android\app\build\outputs\apk\debug\app-debug.apk
```

### 6.2 What You Can Do With This APK
- Transfer to Android phone and install
- Test the app
- Share with others for testing

**Note:** This is DEBUG APK - for testing only, NOT for Play Store!

---

## 📲 Step 7: Test Your App

### Option A: Test on Real Android Phone (Recommended)

#### 7.1 Enable Developer Options on Phone
1. On your Android phone, go to **Settings**
2. Scroll to **About Phone**
3. Find **Build Number**
4. **Tap Build Number 7 times** quickly
5. You'll see message "You are now a developer!"

#### 7.2 Enable USB Debugging
1. Go back to **Settings**
2. Find **Developer Options** (now visible)
3. Enable **USB Debugging**
4. Toggle it ON

#### 7.3 Connect Phone to Computer
1. Connect phone to computer with USB cable
2. Phone will show popup: "Allow USB debugging?"
3. Check "Always allow from this computer"
4. Tap **"OK"**

#### 7.4 Run App from Android Studio
1. In Android Studio, click green **"Run"** button (▶️) at top
2. Select your connected device from list
3. Click **"OK"**
4. App will install and launch on your phone!

### Option B: Test on Emulator (If No Phone)

#### 7.1 Create Virtual Device
1. In Android Studio, click **"Tools"** menu
2. Select **"Device Manager"**
3. Click **"Create Device"**
4. Select **"Phone"** category
5. Choose **"Pixel 5"** (recommended)
6. Click **"Next"**

#### 7.2 Select System Image
1. You'll see Android versions (API levels)
2. Find **"S"** (API 31) or **"Tiramisu"** (API 33)
3. Click **"Download"** next to it
4. Wait for download (500MB-1GB)
5. Click **"Next"** after download

#### 7.3 Configure Virtual Device
1. Give it a name: "Pixel 5 API 31"
2. Click **"Finish"**

#### 7.4 Run App on Emulator
1. Click green **"Run"** button (▶️)
2. Select your emulator from list
3. Click **"OK"**
4. Emulator will start (takes 2-3 minutes first time)
5. App will install and launch in emulator!

---

## 🎨 Step 8: Add Your App Icon

### 8.1 Prepare Your Icon
- Create or download app icon
- **Size:** 512x512 pixels
- **Format:** PNG
- **No transparency:** Solid background
- Save it as `app_icon.png`

### 8.2 Generate All Icon Sizes
1. In Android Studio, in left panel, find `res` folder
2. **Right-click** on `res` folder
3. Select **New → Image Asset**

### 8.3 Configure Icon
1. **Icon Type:** Launcher Icons (Adaptive and Legacy)
2. **Name:** ic_launcher
3. **Asset Type:** Image
4. **Path:** Click folder icon, select your `app_icon.png`
5. **Resize:** 100% (default)
6. Click **"Next"**
7. Click **"Finish"**

**Done!** Your app icon is now added in all required sizes!

---

## 🚀 Step 9: Build Release APK (For Play Store)

### 9.1 Generate Signing Key

1. Open **Command Prompt** (search "cmd" in Windows)
2. Navigate to Android folder:
```cmd
cd C:\Users\YourName\AndroidProjects\android
```

3. Run this command (copy-paste):
```cmd
"%JAVA_HOME%\bin\keytool" -genkey -v -keystore perspectiveupsc.keystore -alias perspectiveupsc -keyalg RSA -keysize 2048 -validity 10000
```

If above doesn't work, try:
```cmd
"C:\Program Files\Android\Android Studio\jbr\bin\keytool" -genkey -v -keystore perspectiveupsc.keystore -alias perspectiveupsc -keyalg RSA -keysize 2048 -validity 10000
```

4. You'll be asked questions:
   - **Keystore password:** Create a strong password (REMEMBER THIS!)
   - **Re-enter password:** Type same password again
   - **First and last name:** Your name
   - **Organizational unit:** Press Enter (skip)
   - **Organization:** Press Enter (skip)
   - **City:** Your city
   - **State:** Your state
   - **Country code:** Your country (US, IN, etc.)
   - **Is this correct?** Type `yes` and press Enter
   - **Key password:** Press Enter (uses same password)

5. File `perspectiveupsc.keystore` is created!

**CRITICAL: Backup this file! Store password safely! You can NEVER recover it!**

### 9.2 Create Signing Configuration

1. In Android Studio, click **"Build"** menu
2. Select **"Generate Signed Bundle / APK"**
3. Select **"APK"** (or AAB for Play Store)
4. Click **"Next"**

### 9.3 Configure Signing
1. **Key store path:** Click folder icon, select `perspectiveupsc.keystore`
2. **Key store password:** Enter your password
3. **Key alias:** perspectiveupsc
4. **Key password:** Same as keystore password
5. ✅ Check "Remember passwords"
6. Click **"Next"**

### 9.4 Build Release
1. **Destination folder:** Keep default or change
2. **Build Variants:** Check ✅ release
3. **Signature Versions:** Check both V1 and V2
4. Click **"Finish"**

### 9.5 Build Complete
- Wait 1-2 minutes for build
- Notification: "Generated Signed APK"
- Click **"locate"**

**Your RELEASE APK is at:**
```
android\app\release\app-release.apk
```

**This APK is ready for Google Play Store! 🎉**

---

## ⚠️ Troubleshooting

### Problem: Gradle Sync Failed

**Solution 1: Check Internet Connection**
- Make sure you're connected to internet
- Gradle needs to download dependencies

**Solution 2: Invalidate Caches**
1. Click **"File"** menu
2. Select **"Invalidate Caches"**
3. Click **"Invalidate and Restart"**
4. Wait for Android Studio to restart

**Solution 3: Update Gradle**
1. Click **"File"** → **"Project Structure"**
2. Check Gradle version
3. Update if needed

### Problem: SDK Not Found

**Solution:**
1. Click **"File"** → **"Settings"**
2. Go to **"Appearance & Behavior"** → **"System Settings"** → **"Android SDK"**
3. Note the SDK Location path
4. Click **"SDK Platforms"** tab
5. Check ✅ **Android 14.0 (API 34)**
6. Click **"Apply"** → **"OK"**

### Problem: Build Failed - Missing Dependencies

**Solution:**
1. Open **"Build"** menu
2. Click **"Clean Project"**
3. Wait for cleaning to finish
4. Click **"Build"** menu again
5. Click **"Rebuild Project"**

### Problem: Emulator Won't Start

**Solution:**
- Make sure **Hyper-V** is disabled on Windows
- Or use a real Android phone instead

### Problem: Can't Find keytool

**Solution:**
The keytool is in Java folder. Try these paths:
```cmd
"C:\Program Files\Android\Android Studio\jbr\bin\keytool" -version
```
or
```cmd
"C:\Program Files\Java\jdk-17\bin\keytool" -version
```

---

## 📋 Quick Reference

### Build Commands (in Android Studio)

1. **Build Debug APK:**
   - Build → Build Bundle(s) / APK(s) → Build APK(s)

2. **Build Release APK:**
   - Build → Generate Signed Bundle / APK → APK → Next → (enter signing info)

3. **Run on Device:**
   - Click green Run button (▶️)

4. **Clean Project:**
   - Build → Clean Project

5. **Rebuild Project:**
   - Build → Rebuild Project

### File Locations

```
Debug APK:
android\app\build\outputs\apk\debug\app-debug.apk

Release APK:
android\app\release\app-release.apk

Keystore:
android\perspectiveupsc.keystore
```

---

## 🎯 What's Next?

After building your APK:

1. ✅ **Test thoroughly** on multiple devices
2. ✅ **Take screenshots** for Play Store (2+ required)
3. ✅ **Create feature graphic** (1024x500)
4. ✅ **Write privacy policy** (host on your website)
5. ✅ **Follow PLAYSTORE_GUIDE.md** to publish

---

## 🆘 Need More Help?

### Common Questions

**Q: How long does first Gradle sync take?**
A: 5-15 minutes depending on internet speed. Be patient!

**Q: Can I close Android Studio during Gradle sync?**
A: NO! Let it complete, even if it seems stuck.

**Q: Do I need a real Android phone?**
A: No, you can use emulator, but real phone testing is better.

**Q: How big is the APK?**
A: About 3-5 MB (WebView apps are small!)

**Q: Can I build APK without Android Studio?**
A: Yes, using command line, but Android Studio is easier for beginners.

---

## ✅ Success Checklist

- [ ] Android Studio installed
- [ ] Android SDK downloaded
- [ ] Project opened successfully
- [ ] Gradle sync completed
- [ ] Debug APK built
- [ ] App tested on device/emulator
- [ ] App icon added
- [ ] Signing key generated
- [ ] Release APK built
- [ ] Ready to publish to Play Store!

---

**Estimated Total Time:**
- Installation: 30-45 minutes
- First build: 15-20 minutes
- Testing: 30 minutes
- **Total: ~1.5-2 hours**

**Congratulations on building your first Android app! 🎉🚀**

---

**For Play Store publishing, see:** `PLAYSTORE_GUIDE.md`  
**For build issues, see:** `BUILD_GUIDE.md`  
**For app features, see:** `README.md`
