package com.perspectiveupsc.app;

import android.Manifest;
import android.annotation.SuppressLint;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.CookieManager;
import android.webkit.DownloadListener;
import android.webkit.URLUtil;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ProgressBar;
import android.widget.Toast;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.core.splashscreen.SplashScreen;
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout;

public class MainActivity extends AppCompatActivity {

    // Configuration
    private static final String BASE_URL = "https://www.perspectiveupsc.com";
    
    // For development/testing, you can switch to:
    // private static final String BASE_URL = "http://10.0.2.2:3000"; // Android emulator
    // private static final String BASE_URL = "http://192.168.1.x:3000"; // Your local IP
    
    // UI Components
    private WebView webView;
    private ProgressBar progressBar;
    private SwipeRefreshLayout swipeRefreshLayout;
    
    // File upload support
    private ValueCallback<Uri[]> fileUploadCallback;
    private final ActivityResultLauncher<Intent> fileChooserLauncher = 
        registerForActivityResult(new ActivityResultContracts.StartActivityForResult(), result -> {
            if (fileUploadCallback != null) {
                Uri[] results = null;
                if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                    String dataString = result.getData().getDataString();
                    if (dataString != null) {
                        results = new Uri[]{Uri.parse(dataString)};
                    }
                }
                fileUploadCallback.onReceiveValue(results);
                fileUploadCallback = null;
            }
        });
    
    // Back button press tracking
    private long backPressedTime;
    private Toast backToast;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        // Install splash screen
        SplashScreen splashScreen = SplashScreen.installSplashScreen(this);
        
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        // Initialize UI components
        webView = findViewById(R.id.webView);
        progressBar = findViewById(R.id.progressBar);
        swipeRefreshLayout = findViewById(R.id.swipeRefreshLayout);

        // Check permissions
        checkPermissions();
        
        // Setup WebView
        setupWebView();
        
        // Setup SwipeRefresh
        setupSwipeRefresh();
        
        // Load URL
        if (isNetworkAvailable()) {
            webView.loadUrl(BASE_URL);
        } else {
            showOfflinePage();
        }
    }

    @SuppressLint("SetJavaScriptEnabled")
    private void setupWebView() {
        WebSettings webSettings = webView.getSettings();
        
        // Enable JavaScript
        webSettings.setJavaScriptEnabled(true);
        
        // Enable DOM storage
        webSettings.setDomStorageEnabled(true);
        
        // Enable database
        webSettings.setDatabaseEnabled(true);
        
        // Enable caching
        webSettings.setCacheMode(WebSettings.LOAD_DEFAULT);
        webSettings.setAppCacheEnabled(true);
        
        // Enable zooming
        webSettings.setSupportZoom(true);
        webSettings.setBuiltInZoomControls(true);
        webSettings.setDisplayZoomControls(false);
        
        // Set user agent
        webSettings.setUserAgentString(webSettings.getUserAgentString() + 
            " PerspectiveUPSC-Android/1.0");
        
        // Support for multiple windows
        webSettings.setSupportMultipleWindows(false);
        
        // Enable mixed content (if needed)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            webSettings.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);
        }
        
        // Enable file access
        webSettings.setAllowFileAccess(true);
        
        // Allow content access
        webSettings.setAllowContentAccess(true);
        
        // Set WebViewClient
        webView.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                String url = request.getUrl().toString();
                
                // Open external links in browser
                if (!url.contains(BASE_URL.replace("https://", "").replace("http://", ""))) {
                    Intent intent = new Intent(Intent.ACTION_VIEW, Uri.parse(url));
                    startActivity(intent);
                    return true;
                }
                
                // Handle payment redirects (Razorpay, etc.)
                if (url.contains("razorpay") || url.contains("payment")) {
                    return false; // Allow WebView to handle
                }
                
                return false;
            }

            @Override
            public void onPageFinished(WebView view, String url) {
                super.onPageFinished(view, url);
                swipeRefreshLayout.setRefreshing(false);
                progressBar.setVisibility(View.GONE);
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, 
                                       WebResourceError error) {
                super.onReceivedError(view, request, error);
                if (request.isForMainFrame()) {
                    showOfflinePage();
                }
            }
        });
        
        // Set WebChromeClient for progress and file upload
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onProgressChanged(WebView view, int newProgress) {
                if (newProgress < 100) {
                    progressBar.setVisibility(View.VISIBLE);
                    progressBar.setProgress(newProgress);
                } else {
                    progressBar.setVisibility(View.GONE);
                }
            }

            // File upload support
            @Override
            public boolean onShowFileChooser(WebView webView, ValueCallback<Uri[]> filePathCallback,
                                            FileChooserParams fileChooserParams) {
                if (fileUploadCallback != null) {
                    fileUploadCallback.onReceiveValue(null);
                }
                fileUploadCallback = filePathCallback;

                Intent intent = fileChooserParams.createIntent();
                intent.setType("*/*"); // Accept all file types
                intent.putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true); // Allow multiple file selection
                
                try {
                    fileChooserLauncher.launch(intent);
                } catch (ActivityNotFoundException e) {
                    fileUploadCallback = null;
                    Toast.makeText(MainActivity.this, "Cannot open file chooser", 
                        Toast.LENGTH_SHORT).show();
                    return false;
                }
                
                return true;
            }
        });
        
        // Download listener
        webView.setDownloadListener(new DownloadListener() {
            @Override
            public void onDownloadStart(String url, String userAgent, String contentDisposition,
                                       String mimeType, long contentLength) {
                // Open download in browser
                Intent intent = new Intent(Intent.ACTION_VIEW);
                intent.setData(Uri.parse(url));
                startActivity(intent);
            }
        });
        
        // Enable cookies
        CookieManager cookieManager = CookieManager.getInstance();
        cookieManager.setAcceptCookie(true);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
            cookieManager.setAcceptThirdPartyCookies(webView, true);
        }
        
        // Add JavaScript interface (optional - for advanced features)
        webView.addJavascriptInterface(new WebAppInterface(this), "Android");
    }

    private void setupSwipeRefresh() {
        swipeRefreshLayout.setColorSchemeResources(
            R.color.colorPrimary,
            R.color.colorAccent
        );
        
        swipeRefreshLayout.setOnRefreshListener(() -> {
            if (isNetworkAvailable()) {
                webView.reload();
            } else {
                swipeRefreshLayout.setRefreshing(false);
                Toast.makeText(this, R.string.no_internet_message, Toast.LENGTH_SHORT).show();
            }
        });
    }

    private void showOfflinePage() {
        webView.setVisibility(View.GONE);
        
        // Load offline page
        String offlineHtml = "<!DOCTYPE html>" +
            "<html><head>" +
            "<meta name='viewport' content='width=device-width, initial-scale=1.0'>" +
            "<style>" +
            "body { font-family: Arial, sans-serif; text-align: center; padding: 50px; " +
            "background-color: #F9FAFB; }" +
            "h1 { color: #111827; font-size: 24px; margin-bottom: 10px; }" +
            "p { color: #6B7280; font-size: 16px; margin-bottom: 30px; }" +
            ".retry-btn { background-color: #3B82F6; color: white; padding: 12px 32px; " +
            "border: none; border-radius: 8px; font-size: 16px; cursor: pointer; }" +
            "</style>" +
            "</head><body>" +
            "<h1>No Internet Connection</h1>" +
            "<p>Please check your internet connection and try again.</p>" +
            "<button class='retry-btn' onclick='window.location.reload()'>Retry</button>" +
            "</body></html>";
        
        webView.loadDataWithBaseURL(null, offlineHtml, "text/html", "UTF-8", null);
        webView.setVisibility(View.VISIBLE);
        swipeRefreshLayout.setRefreshing(false);
    }

    private boolean isNetworkAvailable() {
        ConnectivityManager connectivityManager = 
            (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
        NetworkInfo activeNetworkInfo = connectivityManager.getActiveNetworkInfo();
        return activeNetworkInfo != null && activeNetworkInfo.isConnected();
    }

    private void checkPermissions() {
        // Check for storage permissions (Android 6.0+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (ContextCompat.checkSelfPermission(this, 
                    Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE,
                               Manifest.permission.READ_EXTERNAL_STORAGE}, 100);
            }
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                          @NonNull int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);
        if (requestCode == 100) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                // Permission granted
                Toast.makeText(this, "Permission granted", Toast.LENGTH_SHORT).show();
            }
        }
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        // Handle back button
        if (keyCode == KeyEvent.KEYCODE_BACK && webView.canGoBack()) {
            webView.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            // Double back press to exit
            if (backPressedTime + 2000 > System.currentTimeMillis()) {
                if (backToast != null) {
                    backToast.cancel();
                }
                super.onBackPressed();
                finish();
            } else {
                backToast = Toast.makeText(this, R.string.exit_app, Toast.LENGTH_SHORT);
                backToast.show();
            }
            backPressedTime = System.currentTimeMillis();
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        if (webView != null) {
            webView.onResume();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        if (webView != null) {
            webView.onPause();
        }
    }

    @Override
    protected void onDestroy() {
        if (webView != null) {
            webView.destroy();
        }
        super.onDestroy();
    }
}
