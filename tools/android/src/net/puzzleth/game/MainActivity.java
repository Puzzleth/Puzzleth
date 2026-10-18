package net.puzzleth.game;

import android.app.Activity;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.webkit.ConsoleMessage;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * Puzzleth for Android: the web build of the game (tools/build_web.sh), shipped inside the app as
 * assets/web and shown in a full-screen WebView.
 *
 * The page is served from https://appassets.androidplatform.net/, a secure address of the app's own,
 * where the game keeps its saved progress (localStorage). The Python runtime the page runs the game
 * with comes from pygbag's CDN; the app keeps a copy of every file of it the first time it is
 * downloaded, so after one start with a connection the game also starts offline (the leaderboard
 * still needs one).
 *
 * Updates come from the Nightly branch: .github/workflows/nightly.yml publishes each of its builds to
 * the private Puzzleth-builds repository, which the app reads with the read-only token build_apk.sh
 * packs in as assets/nightly-token.txt (without one it never looks). When the page asks for version.txt (on starting, and whenever it comes
 * back into view, see puzzleth_check_version in tools/web/puzzleth.tmpl), the app looks there for a
 * newer build, downloads it in the background, and from then on serves it instead of its own copy;
 * the page then loads it straight away, or offers it on the menu if a game is under way. Installing
 * a newer APK goes back to the copy inside it.
 */
public class MainActivity extends Activity {
    private static final String APP_HOST = "appassets.androidplatform.net";
    private static final String CDN_HOST = "pygame-web.github.io";
    private static final String NIGHTLY = "https://raw.githubusercontent.com/Puzzleth/Puzzleth-builds/nightly/";
    /** How long a cached CDN file is considered fresh before we try to refresh it in the background. */
    private static final long CDN_TTL_MS = 7L * 24 * 60 * 60 * 1000L;   // 7 days
    private static final Map<String, String> TYPES = new HashMap<>();

    static {
        TYPES.put("html", "text/html");
        TYPES.put("js", "application/javascript");
        TYPES.put("mjs", "application/javascript");
        TYPES.put("css", "text/css");
        TYPES.put("json", "application/json");
        TYPES.put("wasm", "application/wasm");
        TYPES.put("png", "image/png");
        TYPES.put("svg", "image/svg+xml");
        TYPES.put("ico", "image/x-icon");
        TYPES.put("ogg", "audio/ogg");
        TYPES.put("mp3", "audio/mpeg");
        TYPES.put("wav", "audio/wav");
        TYPES.put("txt", "text/plain");
        TYPES.put("py", "text/plain");
        TYPES.put("whl", "application/zip");
        TYPES.put("zip", "application/zip");
    }

    private WebView web;
    private final AtomicBoolean checking = new AtomicBoolean();
    private String token;   // for NIGHTLY, or "" when this APK has none
    private volatile long lastCheck;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        if (Build.VERSION.SDK_INT >= 28) {   // also draw beside a notch or camera hole: no bars at all
            getWindow().getAttributes().layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
        }
        web = new WebView(this);
        web.setBackgroundColor(0xff080b18);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);   // music can start without waiting for a tap
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        web.addJavascriptInterface(new Bridge(), "PuzzlethAndroid");
        web.setWebViewClient(new Client());
        web.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onConsoleMessage(ConsoleMessage m) {   // adb logcat -s Puzzleth
                Log.i("Puzzleth", m.messageLevel() + " " + m.message() + " (" + m.sourceId() + ":" + m.lineNumber() + ")");
                return true;
            }
        });
        setContentView(web);
        hideSystemBars();
        if (state == null) {
            web.loadUrl("https://" + APP_HOST + "/index.html");
        } else {
            web.restoreState(state);
        }
    }

    @Override
    protected void onSaveInstanceState(Bundle state) {
        super.onSaveInstanceState(state);
        web.saveState(state);
    }

    @Override
    public void onWindowFocusChanged(boolean focused) {
        super.onWindowFocusChanged(focused);
        if (focused) hideSystemBars();
    }

    @Override
    protected void onPause() {
        super.onPause();
        web.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
    }

    @Override
    public void onBackPressed() {
        moveTaskToBack(true);   // the game has its own Back buttons; leaving it keeps it as it was
    }

    @SuppressWarnings("deprecation")
    private void hideSystemBars() {
        getWindow().getDecorView().setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY | View.SYSTEM_UI_FLAG_FULLSCREEN
                | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION | View.SYSTEM_UI_FLAG_LAYOUT_STABLE
                | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION);
    }

    /** What the page can ask of the app (see puzzleth_keep_awake and puzzleth_open_url in the page). */
    private class Bridge {
        @JavascriptInterface
        public void keepAwake(final boolean on) {
            runOnUiThread(() -> {
                if (on) getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
                else getWindow().clearFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
            });
        }

        @JavascriptInterface
        public void openUrl(String url) {
            Uri uri = Uri.parse(url);
            if (!"https".equals(uri.getScheme()) && !"http".equals(uri.getScheme())) return;
            try {
                startActivity(new Intent(Intent.ACTION_VIEW, uri));
            } catch (Exception ignored) {
            }
        }
    }

    private class Client extends WebViewClient {
        @Override
        public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
            Uri uri = request.getUrl();
            if (APP_HOST.equals(uri.getHost())) return false;   // the game itself (it reloads on updates)
            new Bridge().openUrl(uri.toString());
            return true;
        }

        @Override
        public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
            if (!"GET".equalsIgnoreCase(request.getMethod())) return null;
            Uri uri = request.getUrl();
            String path = uri.getPath() == null ? "/" : uri.getPath();
            if (path.contains("..")) return null;
            try {
                if (APP_HOST.equals(uri.getHost())) {
                    if (path.equals("/")) path = "/index.html";
                    if (path.equals("/version.txt")) {   // which build is newest: this one, unless Nightly has a newer one
                        checkNightly();
                        return respond(path, new ByteArrayInputStream(buildId().getBytes(StandardCharsets.UTF_8)));
                    }
                    File nightly = nightly();
                    if (nightly != null) {
                        try {   // (a song or picture not downloaded yet is fetched from the same build)
                            return respond(path, new FileInputStream(cached(NIGHTLY + path.substring(1), new File(nightly, path), token())));
                        } catch (IOException e) {
                            // offline: the app's own copy, if it has one
                        }
                    }
                    return respond(path, getAssets().open("web" + path));
                }
                if (CDN_HOST.equals(uri.getHost())) {
                    return respond(path, new FileInputStream(cached(uri.toString(), new File(getFilesDir(), "cdn" + path), null)));
                }
            } catch (IOException e) {
                if (APP_HOST.equals(uri.getHost())) {
                    return new WebResourceResponse("text/plain", "utf-8", 404, "Not Found", headers(), null);
                }
            }
            return null;   // anything else (the leaderboard) goes to the network as usual
        }
    }

    // ---------------------------------------------------------------- Nightly builds

    private SharedPreferences prefs() {
        return getSharedPreferences("nightly", MODE_PRIVATE);
    }

    /** The folder of the Nightly build in use, or null when the app's own copy is. */
    private File nightly() {
        SharedPreferences p = prefs();
        String id = p.getString("build", null);
        if (id == null) return null;
        File dir = new File(getFilesDir(), "nightly/" + id);
        long appInstalled;
        try {
            appInstalled = getPackageManager().getPackageInfo(getPackageName(), 0).lastUpdateTime;
        } catch (Exception e) {
            appInstalled = 0;
        }
        // an APK installed since then has a newer game inside it
        if (p.getLong("installed", 0) < appInstalled || !new File(dir, "index.html").isFile()) return null;
        return dir;
    }

    /** The build being served: its name, as in version.txt. */
    private String buildId() {
        File dir = nightly();
        if (dir != null) return dir.getName();
        try (InputStream in = getAssets().open("web/version.txt")) {
            return new String(read(in), StandardCharsets.UTF_8).trim();
        } catch (IOException e) {
            return "";
        }
    }

    private String token() {
        if (token == null) {
            try (InputStream in = getAssets().open("nightly-token.txt")) {
                token = new String(read(in), StandardCharsets.UTF_8).trim();
            } catch (IOException e) {
                token = "";
            }
        }
        return token;
    }

    /** Look for a newer Nightly build in the background (at most once a minute). */
    private void checkNightly() {
        if (token().isEmpty()) return;
        long now = System.currentTimeMillis();
        if (now - lastCheck < 60000 || !checking.compareAndSet(false, true)) return;
        lastCheck = now;
        new Thread(() -> {
            try {
                fetchNightly();
            } catch (Exception e) {
                Log.i("Puzzleth", "no Nightly update: " + e);
            } finally {
                checking.set(false);
            }
        }).start();
    }

    private void fetchNightly() throws IOException {
        String latest = new String(download(NIGHTLY + "version.txt?t=" + System.currentTimeMillis(), token()),
            StandardCharsets.UTF_8).trim();
        if (!latest.matches("[0-9a-f]{6,64}") || latest.equals(buildId())) return;
        File root = new File(getFilesDir(), "nightly");
        File part = new File(root, latest + ".part");
        deleteTree(part);
        if (!part.mkdirs()) throw new IOException("mkdirs");
        String game = "puzzleth-" + latest + ".apk";
        byte[] page = download(NIGHTLY + "index.html?t=" + System.currentTimeMillis(), token());
        if (!new String(page, StandardCharsets.UTF_8).contains(game)) {
            throw new IOException("index.html isn't build " + latest + " yet");   // a cache behind; next time
        }
        save(download(NIGHTLY + game, token()), new File(part, game));
        save(page, new File(part, "index.html"));
        File dir = new File(root, latest);
        deleteTree(dir);
        if (!part.renameTo(dir)) throw new IOException("rename");
        prefs().edit().putString("build", latest).putLong("installed", System.currentTimeMillis()).apply();
        File[] old = root.listFiles();
        if (old != null) {
            for (File f : old) {
                if (!f.getName().equals(latest)) deleteTree(f);
            }
        }
        Log.i("Puzzleth", "downloaded Nightly build " + latest);
    }

    // ---------------------------------------------------------------- files

    /** A copy of ``url`` kept in ``file``, downloaded the first time it is asked for.
     *  For CDN files (token == null), a stale file is refreshed in the background. */
    private static File cached(String url, File file, String token) throws IOException {
        if (!file.isFile()) {
            save(download(url, token), file);
            return file;
        }
        if (token == null) {   // CDN assets: refresh occasionally
            long now = System.currentTimeMillis();
            if (now - file.lastModified() > CDN_TTL_MS) {
                new Thread(() -> {
                    try {
                        save(download(url, null), file);
                        // mark fresh even if mtime was identical
                        //noinspection ResultOfMethodCallIgnored
                        file.setLastModified(System.currentTimeMillis());
                        Log.i("Puzzleth", "refreshed CDN asset " + url);
                    } catch (IOException ignored) {
                    }
                }).start();
            }
        }
        return file;
    }

    private static byte[] download(String url, String token) throws IOException {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        if (token != null && !token.isEmpty()) c.setRequestProperty("Authorization", "token " + token);
        c.setConnectTimeout(15000);
        c.setReadTimeout(30000);
        try {
            if (c.getResponseCode() != 200) throw new IOException("HTTP " + c.getResponseCode() + " for " + url);
            try (InputStream in = c.getInputStream()) {
                return read(in);
            }
        } finally {
            c.disconnect();
        }
    }

    private static byte[] read(InputStream in) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        byte[] buf = new byte[65536];
        for (int n; (n = in.read(buf)) > 0; ) out.write(buf, 0, n);
        return out.toByteArray();
    }

    /** Write ``data`` to ``file`` whole: through a .part file, so a half-written file is never served. */
    private static void save(byte[] data, File file) throws IOException {
        File parent = file.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) throw new IOException("mkdirs");
        File part = new File(file.getPath() + ".part");
        try (OutputStream out = new FileOutputStream(part)) {
            out.write(data);
        }
        if (!part.renameTo(file)) throw new IOException("rename");
    }

    private static void deleteTree(File f) {
        File[] children = f.listFiles();
        if (children != null) {
            for (File c : children) deleteTree(c);
        }
        //noinspection ResultOfMethodCallIgnored
        f.delete();
    }

    private static WebResourceResponse respond(String path, InputStream body) {
        String name = path.substring(path.lastIndexOf('/') + 1);
        int dot = name.lastIndexOf('.');
        String ext = dot < 0 ? "" : name.substring(dot + 1).toLowerCase(Locale.ROOT);
        String type = TYPES.containsKey(ext) ? TYPES.get(ext) : "application/octet-stream";
        String charset = type.startsWith("text/") || type.endsWith("javascript") || type.endsWith("json") ? "utf-8" : null;
        return new WebResourceResponse(type, charset, 200, "OK", headers(), body);
    }

    private static Map<String, String> headers() {
        Map<String, String> h = new HashMap<>();
        h.put("Access-Control-Allow-Origin", "*");
        h.put("Cross-Origin-Resource-Policy", "cross-origin");
        h.put("Cache-Control", "no-cache");
        return h;
    }
}
