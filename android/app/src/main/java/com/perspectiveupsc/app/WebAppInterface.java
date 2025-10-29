package com.perspectiveupsc.app;

import android.content.Context;
import android.content.Intent;
import android.webkit.JavascriptInterface;
import android.widget.Toast;

/**
 * JavaScript Interface for WebView
 * Allows web app to call Android native functions
 * 
 * Usage in JavaScript:
 * Android.showToast("Hello from web!");
 * Android.shareContent("Check out this app!");
 */
public class WebAppInterface {
    private Context context;

    public WebAppInterface(Context context) {
        this.context = context;
    }

    /**
     * Show a toast message from web
     * Usage: Android.showToast("Your message here");
     */
    @JavascriptInterface
    public void showToast(String message) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show();
    }

    /**
     * Show a long toast message from web
     * Usage: Android.showLongToast("Your long message here");
     */
    @JavascriptInterface
    public void showLongToast(String message) {
        Toast.makeText(context, message, Toast.LENGTH_LONG).show();
    }

    /**
     * Share content via native share dialog
     * Usage: Android.shareContent("Check out Perspective UPSC!");
     */
    @JavascriptInterface
    public void shareContent(String text) {
        Intent shareIntent = new Intent(Intent.ACTION_SEND);
        shareIntent.setType("text/plain");
        shareIntent.putExtra(Intent.EXTRA_TEXT, text);
        context.startActivity(Intent.createChooser(shareIntent, 
            context.getString(R.string.share_via)));
    }

    /**
     * Get app version
     * Usage: var version = Android.getAppVersion();
     */
    @JavascriptInterface
    public String getAppVersion() {
        try {
            return context.getPackageManager()
                .getPackageInfo(context.getPackageName(), 0).versionName;
        } catch (Exception e) {
            return "1.0.0";
        }
    }

    /**
     * Check if running in Android app
     * Usage: var isAndroid = Android.isAndroidApp();
     */
    @JavascriptInterface
    public boolean isAndroidApp() {
        return true;
    }

    /**
     * Get device info
     * Usage: var deviceInfo = Android.getDeviceInfo();
     */
    @JavascriptInterface
    public String getDeviceInfo() {
        return android.os.Build.MANUFACTURER + " " + 
               android.os.Build.MODEL + " " + 
               android.os.Build.VERSION.RELEASE;
    }
}
