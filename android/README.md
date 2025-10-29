# 📱 Perspective UPSC - Android App

Complete Android WebView application for the Perspective UPSC platform.

---

## 📋 App Details

- **App Name:** Perspective UPSC
- **Package Name:** com.perspectiveupsc.app
- **Target URL:** https://www.perspectiveupsc.com
- **Min SDK:** Android 7.0 (API 24)
- **Target SDK:** Android 14 (API 34)
- **Screen Orientation:** Portrait only

---

## ✨ Features

✅ **WebView Integration** - Loads your web app seamlessly  
✅ **Push Notifications** - Notify users about tests and results  
✅ **File Upload Support** - Excel/image uploads working  
✅ **Offline Page** - Shows message when no internet  
✅ **Pull to Refresh** - Swipe down to reload  
✅ **Back Navigation** - Android back button works correctly  
✅ **Share Feature** - Share app with friends  
✅ **Auto-Update Check** - Prompts users to update  
✅ **Cookie Management** - Session persistence  
✅ **Download Support** - Download files from app  
✅ **JavaScript Enabled** - Full web app functionality

---

## 🏗️ Project Structure

```
android/
├── app/
│   ├── src/
│   │   └── main/
│   │       ├── java/com/perspectiveupsc/app/
│   │       │   ├── MainActivity.java
│   │       │   ├── WebAppInterface.java
│   │       │   ├── NotificationHelper.java
│   │       │   └── FileUploadHandler.java
│   │       ├── res/
│   │       │   ├── layout/
│   │       │   │   ├── activity_main.xml
│   │       │   │   └── offline_page.xml
│   │       │   ├── values/
│   │       │   │   ├── strings.xml
│   │       │   │   ├── colors.xml
│   │       │   │   └── styles.xml
│   │       │   ├── drawable/
│   │       │   │   └── ic_launcher.xml (placeholder)
│   │       │   └── mipmap/
│   │       │       └── (app icons - you need to add)
│   │       └── AndroidManifest.xml
│   ├── build.gradle
│   └── proguard-rules.pro
├── gradle/
│   └── wrapper/
│       ├── gradle-wrapper.jar
│       └── gradle-wrapper.properties
├── build.gradle
├── settings.gradle
├── gradle.properties
└── README.md (this file)
```

---

## 🚀 Setup Instructions

### Prerequisites
1. **Android Studio** (Latest version - Hedgehog or newer)
2. **JDK 17** or higher
3. **Android SDK** with API 34

### Step 1: Open Project
1. Download/clone this android folder
2. Open Android Studio
3. Click "Open" and select the `android` folder
4. Wait for Gradle sync to complete

### Step 2: Configure App
1. Open `app/src/main/java/com/perspectiveupsc/app/MainActivity.java`
2. Update `BASE_URL` if needed (default: https://www.perspectiveupsc.com)
3. Customize colors in `res/values/colors.xml`

### Step 3: Add App Icon
1. Go to `res` folder
2. Right-click → New → Image Asset
3. Upload your app icon (512x512 PNG recommended)
4. Generate all sizes

### Step 4: Build APK
1. Click **Build** → **Build Bundle(s) / APK(s)** → **Build APK(s)**
2. Find APK in `app/build/outputs/apk/debug/`
3. For release: Build → Generate Signed Bundle / APK

---

## 🔑 Generate Signing Key

For Google Play Store release, you need a signing key:

```bash
# Generate keystore
keytool -genkey -v -keystore perspectiveupsc.keystore \
  -alias perspectiveupsc -keyalg RSA -keysize 2048 -validity 10000

# You'll be asked:
# - Password (remember this!)
# - Name, Organization, City, State, Country
```

**Store this keystore file safely - you can never recover it!**

Create `keystore.properties` file:
```properties
storePassword=your_store_password
keyPassword=your_key_password
keyAlias=perspectiveupsc
storeFile=../perspectiveupsc.keystore
```

---

## 📦 Building Release APK

### Method 1: Using Android Studio
1. **Build** → **Generate Signed Bundle / APK**
2. Select **APK**
3. Choose your keystore file
4. Enter passwords
5. Select **release** build variant
6. Click **Finish**

### Method 2: Using Command Line
```bash
# Debug build (for testing)
./gradlew assembleDebug

# Release build (for Play Store)
./gradlew assembleRelease

# Find APK in:
# app/build/outputs/apk/debug/app-debug.apk
# app/build/outputs/apk/release/app-release.apk
```

---

## 📱 Testing on Device

### Via USB Debugging
1. Enable **Developer Options** on your Android phone
2. Enable **USB Debugging**
3. Connect phone to computer
4. In Android Studio, click **Run** (green play button)
5. Select your device

### Via APK Installation
1. Build debug APK
2. Transfer APK to phone
3. Enable "Install from Unknown Sources"
4. Open APK file to install
5. Test the app

---

## 🚀 Publishing to Google Play Store

### Step 1: Google Play Console Setup
1. Go to https://play.google.com/console
2. Pay $25 one-time registration fee
3. Create developer account

### Step 2: Create App Listing
1. Click **Create App**
2. Fill in:
   - **App name:** Perspective UPSC
   - **Default language:** English
   - **App or Game:** App
   - **Free or Paid:** Free
3. Accept policies and create

### Step 3: Store Listing
Fill in required information:

**App Details:**
- **Short description** (80 chars):
  ```
  Master UPSC with comprehensive tests and analytics. Prepare smarter, succeed faster!
  ```

- **Full description** (4000 chars):
  ```
  Perspective UPSC is your comprehensive preparation companion for UPSC Civil Services Examination. 
  
  🎯 KEY FEATURES:
  
  📚 Comprehensive Test Library
  • Access hundreds of high-quality mock tests
  • Subject-wise tests covering entire UPSC syllabus
  • Previous year question patterns
  • Regularly updated content
  
  💰 Smart Pricing with Bundles
  • Individual test purchases
  • Bundle discounts up to 25% off
  • Affordable pricing for students
  • Secure payment gateway
  
  📊 Advanced Analytics
  • Detailed performance reports
  • Subject-wise strength analysis
  • Progress tracking over time
  • Compare with top performers
  
  ⏱️ Timed Tests
  • Real exam environment simulation
  • Strict time management practice
  • Auto-submit on timeout
  • Timer display throughout test
  
  ✅ Instant Results
  • Immediate score after submission
  • Question-wise breakdown
  • Correct answers with explanations
  • Performance percentile
  
  🎓 For UPSC Aspirants
  Whether you're preparing for Prelims, Mains, or Interview, Perspective UPSC provides 
  the tools you need to excel. Our platform is designed by experienced educators and 
  successful UPSC candidates.
  
  🔐 Secure & Reliable
  • Secure payment processing
  • Data privacy protection
  • Regular backups
  • 24/7 availability
  
  📱 Features in App:
  • Smooth and fast interface
  • Offline mode for purchased tests
  • Push notifications for new content
  • Easy navigation and user-friendly design
  
  Download now and start your journey to becoming an IAS officer!
  
  For support: admin@perspectiveupsc.com
  ```

- **Category:** Education
- **Email:** admin@perspectiveupsc.com
- **Phone:** (Your contact number)

### Step 4: Upload Assets

**Screenshots (Required):**
- Phone: At least 2 screenshots (16:9 ratio recommended)
- 7-inch tablet: At least 2 screenshots
- 10-inch tablet: At least 2 screenshots
- Take screenshots of:
  1. Login/Home screen
  2. Test listing
  3. Taking a test
  4. Results page

**App Icon:**
- 512x512 PNG (32-bit with alpha)
- High quality, no transparency in corners

**Feature Graphic:**
- 1024x500 PNG or JPG
- Eye-catching banner for Play Store

**Optional:**
- Promotional video (YouTube link)
- Banner images

### Step 5: Content Rating
1. Click **Content Rating**
2. Fill out questionnaire
3. Answer questions about your app
4. Get rating (likely: Everyone or Teen)

### Step 6: App Content
1. **Privacy Policy:** 
   - Required for apps with user data
   - Create privacy policy (use generator: https://app-privacy-policy-generator.firebaseapp.com/)
   - Host on your website: https://www.perspectiveupsc.com/privacy-policy
   - Add URL in Play Console

2. **Target Audience:**
   - Select age groups: 18+ (UPSC aspirants)
   - Not designed for children

3. **News Apps:**
   - Select "No" (not a news app)

4. **COVID-19 Contact Tracing:**
   - Select "No"

5. **Data Safety:**
   - Describe data collection and sharing
   - User data: Email, Name, Payment info
   - Data encrypted in transit: Yes
   - Users can request data deletion: Yes

### Step 7: App Access
- **All functionality is available:** Yes
- Or provide demo credentials if restricted

### Step 8: Ads
- **Contains ads:** No (unless you add ads)

### Step 9: Upload Release
1. Go to **Production** → **Create new release**
2. Upload your signed APK or AAB (Android App Bundle recommended)
3. Add release notes:
   ```
   Initial release of Perspective UPSC app
   
   ✨ Features:
   - Browse and purchase UPSC mock tests
   - Take timed tests with real exam experience
   - View detailed results and analytics
   - Bundle discounts up to 25%
   - Secure payment processing
   - User-friendly interface
   
   🎯 Start your UPSC preparation journey today!
   ```
4. Save and review release

### Step 10: Submit for Review
1. Review all sections (green checkmarks)
2. Click **Submit for review**
3. Wait for approval (usually 3-7 days)

### Step 11: After Approval
- App will be live on Google Play Store
- Share the link: `https://play.google.com/store/apps/details?id=com.perspectiveupsc.app`
- Monitor reviews and ratings
- Respond to user feedback

---

## 🔔 Push Notifications Setup

### Firebase Setup (Optional but Recommended)
1. Go to https://console.firebase.google.com/
2. Create new project: "Perspective UPSC"
3. Add Android app with package name: `com.perspectiveupsc.app`
4. Download `google-services.json`
5. Place in `app/` folder
6. Uncomment Firebase dependencies in `build.gradle`

### Sending Notifications
- Use Firebase Console to send notifications
- Or integrate with your backend to send programmatically

---

## 🎨 Customization

### Change Colors
Edit `app/src/main/res/values/colors.xml`:
```xml
<color name="colorPrimary">#3B82F6</color>    <!-- Your brand color -->
<color name="colorPrimaryDark">#2563EB</color>
<color name="colorAccent">#8B5CF6</color>
```

### Change App Name
Edit `app/src/main/res/values/strings.xml`:
```xml
<string name="app_name">Perspective UPSC</string>
```

### Change URL
Edit `MainActivity.java`:
```java
private static final String BASE_URL = "https://www.perspectiveupsc.com";
```

---

## 🐛 Troubleshooting

### Gradle Sync Failed
```bash
# Clean and rebuild
./gradlew clean
./gradlew build
```

### App Crashes on Start
- Check Logcat in Android Studio
- Ensure BASE_URL is correct
- Check internet permissions in Manifest

### File Upload Not Working
- Ensure INTERNET permission is granted
- Check WebView settings in MainActivity
- Test on device (not emulator)

### Back Button Not Working
- Check `onBackPressed()` in MainActivity
- Ensure WebView can go back

---

## 📊 Analytics (Optional)

Add Google Analytics or Firebase Analytics:
1. Add dependencies in `build.gradle`
2. Track screen views, events, user engagement
3. Monitor app performance

---

## 🔄 Updating the App

### Release New Version
1. Update `versionCode` and `versionName` in `build.gradle`
2. Build new signed APK/AAB
3. Upload to Play Console
4. Add release notes
5. Submit for review

**Version Naming:**
- 1.0.0 - Initial release
- 1.1.0 - Minor updates
- 2.0.0 - Major updates

---

## 📝 Best Practices

### Security
- ✅ Always use HTTPS
- ✅ Enable SSL pinning for production
- ✅ Obfuscate code with ProGuard
- ✅ Keep keystore safe and backed up

### Performance
- ✅ Enable WebView caching
- ✅ Optimize images on website
- ✅ Use lazy loading
- ✅ Minimize JavaScript

### User Experience
- ✅ Show loading indicators
- ✅ Handle offline gracefully
- ✅ Implement pull-to-refresh
- ✅ Smooth animations

---

## 🎯 Next Steps

1. ✅ Build and test the app
2. ✅ Add your app icon
3. ✅ Customize colors and branding
4. ✅ Test on multiple devices
5. ✅ Generate signing key
6. ✅ Build release APK
7. ✅ Create Play Store listing
8. ✅ Upload screenshots and assets
9. ✅ Submit for review
10. ✅ Launch and celebrate! 🎉

---

## 📞 Support

For issues or questions:
- Check Android Studio Logcat
- Review this documentation
- Test on physical device (not just emulator)
- Ensure website is mobile-responsive

---

**Good luck with your Android app launch! 🚀**

**App Package:** com.perspectiveupsc.app  
**Target Platform:** Android 7.0+ (API 24+)  
**Last Updated:** October 2025
