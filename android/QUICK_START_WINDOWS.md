# ⚡ Quick Start - Build Your Android App on Windows

**Goal:** Build Perspective UPSC Android app from scratch  
**Time:** 2 hours  
**Difficulty:** Beginner-friendly

---

## 📝 Phase 1: Download & Install (45 mins)

### ✅ Step 1: Download Android Studio (10 mins)
1. Open browser: https://developer.android.com/studio
2. Click green "Download Android Studio" button
3. Accept terms
4. Download starts (~1GB file)
5. Wait for download to finish

### ✅ Step 2: Install Android Studio (10 mins)
1. Find downloaded file in Downloads folder
2. Right-click → "Run as administrator"
3. Click "Yes" to allow changes
4. Follow wizard:
   - Click "Next"
   - Check ✅ "Android Virtual Device"
   - Click "Next" → "I Agree" → "Next" → "Install"
5. Wait for installation (5-10 mins)
6. Check ✅ "Start Android Studio"
7. Click "Finish"

### ✅ Step 3: First Time Setup (25 mins)
1. "Do not import settings" → OK
2. "Don't send" → Next
3. "Standard" → Next
4. Choose theme (Darcula recommended) → Next
5. Next
6. **Accept all licenses** → Finish
7. **WAIT for downloads** (15-30 mins) ⏳
   - This downloads ~3GB
   - DO NOT close!
8. Click "Finish" when done

**✅ Android Studio is installed!**

---

## 📂 Phase 2: Open & Build Project (30 mins)

### ✅ Step 4: Get Project Files
Your Android project is in: `/app/android/`

**If on same computer:**
- Note the path: `/app/android/`

**If need to transfer:**
- Copy entire `android` folder to: `C:\Users\YourName\AndroidProjects\android`

### ✅ Step 5: Open Project (15 mins)
1. Android Studio Welcome screen
2. Click "Open"
3. Navigate to `android` folder
4. Select the folder
5. Click "OK"
6. Click "Trust Project"
7. **WAIT for Gradle Sync** (5-15 mins) ⏳
   - Shows "Gradle Sync in progress..."
   - First time takes long
   - DO NOT close!
8. Success: "Gradle sync finished" ✅

### ✅ Step 6: Build APK (5 mins)
1. Click "Build" menu
2. "Build Bundle(s) / APK(s)"
3. "Build APK(s)"
4. Wait (1-2 mins)
5. Notification: "Build APK(s) completed successfully"
6. Click "locate"

**✅ Your APK is built!**
**Location:** `android\app\build\outputs\apk\debug\app-debug.apk`

---

## 📱 Phase 3: Test App (15 mins)

### ✅ Step 7: Test on Phone

**7.1 Enable USB Debugging:**
1. Phone Settings → About Phone
2. Tap "Build Number" 7 times
3. Back → Developer Options
4. Enable "USB Debugging"

**7.2 Connect & Run:**
1. Connect phone to computer (USB cable)
2. Allow USB debugging on phone
3. In Android Studio, click green ▶️ button
4. Select your phone
5. Click "OK"
6. App installs and opens!

**✅ App is working on your phone!**

---

## 🎨 Phase 4: Add App Icon (10 mins)

### ✅ Step 8: Add Icon
1. Prepare 512x512 PNG icon
2. In Android Studio left panel, find `res` folder
3. Right-click `res` → New → Image Asset
4. Path: Select your icon
5. Next → Finish

**✅ App icon added!**

---

## 🔐 Phase 5: Build Release (20 mins)

### ✅ Step 9: Generate Signing Key (10 mins)
1. Open Command Prompt (search "cmd")
2. Run this command:
```cmd
"C:\Program Files\Android\Android Studio\jbr\bin\keytool" -genkey -v -keystore perspectiveupsc.keystore -alias perspectiveupsc -keyalg RSA -keysize 2048 -validity 10000
```
3. Enter password (REMEMBER IT!)
4. Answer questions (name, city, country)
5. File created: `perspectiveupsc.keystore`

**⚠️ BACKUP THIS FILE! SAVE PASSWORD!**

### ✅ Step 10: Build Signed APK (10 mins)
1. Build → Generate Signed Bundle / APK
2. Select "APK" → Next
3. Key store path: Select `perspectiveupsc.keystore`
4. Enter password
5. Key alias: perspectiveupsc
6. Next
7. Check "release" → Finish
8. Wait (1-2 mins)
9. Click "locate"

**✅ Release APK ready!**
**Location:** `android\app\release\app-release.apk`

---

## 🎉 You're Done!

### What You Have Now:
- ✅ Android Studio installed and configured
- ✅ Project opened and built successfully
- ✅ Debug APK for testing
- ✅ Release APK for Play Store
- ✅ App icon added
- ✅ Signing key created

### Next Steps:
1. **Test thoroughly** on multiple devices
2. **Take 2+ screenshots** for Play Store
3. **Follow PLAYSTORE_GUIDE.md** to publish

---

## 📞 Quick Help

### Stuck on Gradle Sync?
- Wait! First time takes 5-15 minutes
- Check internet connection
- If fails: File → Invalidate Caches → Restart

### Build Failed?
- Build → Clean Project
- Build → Rebuild Project

### Can't Find APK?
**Debug APK:**
```
android\app\build\outputs\apk\debug\app-debug.apk
```

**Release APK:**
```
android\app\release\app-release.apk
```

### Emulator Instead of Phone?
1. Tools → Device Manager
2. Create Device
3. Select Pixel 5
4. Download system image
5. Finish
6. Click green ▶️ → Select emulator

---

## ⏱️ Time Breakdown

| Phase | Time | What Happens |
|-------|------|--------------|
| Download Android Studio | 10 mins | Download ~1GB |
| Install | 10 mins | Install software |
| First setup | 25 mins | Download SDK ~3GB |
| Open project | 15 mins | Gradle sync |
| Build APK | 5 mins | First build |
| Test | 15 mins | Run on device |
| Add icon | 10 mins | Generate icons |
| Generate key | 10 mins | Create keystore |
| Build release | 10 mins | Final APK |
| **TOTAL** | **~2 hours** | **Complete!** |

---

## 💾 Important Files to Backup

After completing, backup these files:
- ✅ `perspectiveupsc.keystore` (CRITICAL!)
- ✅ Password (write it down!)
- ✅ `app-release.apk` (for Play Store)

**Store keystore password safely! You can NEVER recover it if lost!**

---

## 🎯 Your APK is Ready!

**For Play Store submission:**
1. Go to https://play.google.com/console
2. Create developer account ($25 one-time)
3. Follow PLAYSTORE_GUIDE.md
4. Upload your `app-release.apk`
5. Wait 2-7 days for approval
6. Your app goes LIVE! 🎉

---

**Need detailed help?** See: `WINDOWS_INSTALLATION_GUIDE.md`  
**Build issues?** See: `BUILD_GUIDE.md`  
**Publishing?** See: `PLAYSTORE_GUIDE.md`

**Good luck! 🚀**
