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
import android.webkit.RenderProcessGoneDetail;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
import java.security.DigestInputStream;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.security.Signature;
import java.security.KeyFactory;
import java.security.PublicKey;
import java.security.spec.X509EncodedKeySpec;
import java.util.Base64;
import java.util.HashMap;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.concurrent.atomic.AtomicReference;

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
 * a public location. When the page asks for version.txt (on starting, and whenever it comes
 * back into view, see puzzleth_check_version in tools/web/puzzleth.tmpl), the app looks there for a
 * newer build, downloads it in the background, and from then on serves it instead of its own copy;
 * the page then loads it straight away, or offers it on the menu if a game is under way. Installing
 * a newer APK goes back to the copy inside it.
 */
public class MainActivity extends Activity {
    private static final String APP_HOST = "appassets.androidplatform.net";
    private static final String CDN_HOST = "pygame-web.github.io";
    // Public, unauthenticated base URL for Nightly artifacts (see PR notes for hosting options).
    private static final String NIGHTLY = "https://puzzleth.github.io/Puzzleth-builds/nightly/";
    // Nightly updates are disabled for now. Set to true to re-enable background update checks/downloads.
    private static final boolean NIGHTLY_UPDATES_ENABLED = false;
    private static final Map<String, String> TYPES = new HashMap<>();
    // Optional: base64-encoded Ed25519 public key (X.509/SPKI) to verify manifest.sig. Leave empty to disable.
    private static final String MANIFEST_PUBKEY_B64 = "";

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
    private volatile long lastCheck;
    private final Object webLock = new Object();

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        if (Build.VERSION.SDK_INT >= 28) {   // also draw beside a notch or camera hole: no bars at all
            getWindow().getAttributes().layoutInDisplayCutoutMode =
                WindowManager.LayoutParams.LAYOUT_IN_DISPLAY_CUTOUT_MODE_SHORT_EDGES;
        }
        web = new WebView(this);
        try {
            web.setRendererPriorityPolicy(WebView.RENDERER_PRIORITY_BOUND, true);
        } catch (Throwable ignored) {}
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
        public boolean onRenderProcessGone(WebView view, RenderProcessGoneDetail detail) {
            Log.i("Puzzleth", "WebView renderer " + (detail != null && detail.didCrash() ? "crashed" : "was killed"));
            runOnUiThread(() -> {
                synchronized (webLock) {
                    removeWebView();
                    createWebView();
                }
            });
            return true;
        }

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
                        if (NIGHTLY_UPDATES_ENABLED) checkNightly();
                        return respond(path, new ByteArrayInputStream(buildId().getBytes(StandardCharsets.UTF_8)));
                    }
                    if (NIGHTLY_UPDATES_ENABLED) {
                        File nightly = nightly();
                        if (nightly != null) {
                            try {   // (a song or picture not downloaded yet is fetched from the same build)
                                return respond(path, new FileInputStream(cached(NIGHTLY + path.substring(1), new File(nightly, path))));
                            } catch (IOException e) {
                                // offline: the app's own copy, if it has one
                            }
                        }
                    }
                    return respond(path, getAssets().open("web" + path));
                }
                if (CDN_HOST.equals(uri.getHost())) {
                    return respond(path, new FileInputStream(cached(uri.toString(), new File(getFilesDir(), "cdn" + path))));
                }
            } catch (IOException e) {
                if (APP_HOST.equals(uri.getHost())) {
                    return new WebResourceResponse("text/plain", "utf-8", 404, "Not Found", headers(), null);
                }
            }
            return null;   // anything else (the leaderboard) goes to the network as usual
        }
    }

    private void removeWebView() {
        try {
            if (web != null) {
                web.setWebChromeClient(null);
                web.setWebViewClient(null);
                web.removeJavascriptInterface("PuzzlethAndroid");
                web.destroy();
            }
        } catch (Exception ignored) {}
    }

    private void createWebView() {
        web = new WebView(this);
        try {
            web.setRendererPriorityPolicy(WebView.RENDERER_PRIORITY_BOUND, true);
        } catch (Throwable ignored) {}
        web.setBackgroundColor(0xff080b18);
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setAllowFileAccess(false);
        s.setAllowContentAccess(false);
        web.addJavascriptInterface(new Bridge(), "PuzzlethAndroid");
        web.setWebViewClient(new Client());
        web.setWebChromeClient(new WebChromeClient());
        setContentView(web);
        hideSystemBars();
        web.loadUrl("https://" + APP_HOST + "/index.html");
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
            return new String(readAll(in), StandardCharsets.UTF_8).trim();
        } catch (IOException e) {
            return "";
        }
    }

    /** Look for a newer Nightly build in the background (at most once a minute). */
    private void checkNightly() {
        if (!NIGHTLY_UPDATES_ENABLED) return;
        // No token is used; NIGHTLY must be publicly readable.
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
        long nowMs = System.currentTimeMillis();
        ManifestInfo m = fetchManifest();
        if (m == null) {
            String latest = new String(downloadToMemory(NIGHTLY + "version.txt?t=" + nowMs), StandardCharsets.UTF_8).trim();
            if (!latest.matches("[0-9a-f]{6,64}") || latest.equals(buildId())) return;
            m = new ManifestInfo();
            m.buildId = latest;
            m.buildNumber = prefs().getLong("current_build_number", 0);
            m.indexSha256 = null;
            m.gameSha256 = null;
        }
        long currentNumber = Math.max(prefs().getLong("current_build_number", 0), 0);
        if (m.buildNumber > 0 && m.buildNumber <= currentNumber) return;  // never go back

        File root = new File(getFilesDir(), "nightly");
        File part = new File(root, m.buildId + ".part");
        deleteTree(part);
        if (!part.mkdirs()) throw new IOException("mkdirs");
        String game = "puzzleth-" + m.buildId + ".apk";

        byte[] page = downloadToMemory(NIGHTLY + "index.html?t=" + nowMs);
        String pageStr = new String(page, StandardCharsets.UTF_8);
        if (!pageStr.contains(game)) throw new IOException("index.html isn't build " + m.buildId + " yet");

        File gameFile = new File(part, game);
        String gameSha = downloadToFile(NIGHTLY + game, gameFile);
        if (!m.buildId.matches("[0-9a-f]{6,64}")) throw new IOException("bad build id");
        if (!gameSha.startsWith(m.buildId)) throw new IOException("game sha256 mismatch for " + m.buildId);
        if (m.gameSha256 != null && !m.gameSha256.isEmpty() && !m.gameSha256.equalsIgnoreCase(gameSha))
            throw new IOException("game sha256 differs from manifest");
        String indexSha = sha256Hex(page);
        if (m.indexSha256 != null && !m.indexSha256.isEmpty() && !m.indexSha256.equalsIgnoreCase(indexSha))
            throw new IOException("index.html sha256 differs from manifest");
        saveBytes(page, new File(part, "index.html"));

        File dir = new File(root, m.buildId);
        deleteTree(dir);
        if (!part.renameTo(dir)) throw new IOException("rename");
        prefs().edit()
            .putString("build", m.buildId)
            .putLong("installed", System.currentTimeMillis())
            .putLong("current_build_number", Math.max(currentNumber, m.buildNumber))
            .apply();
        File[] old = root.listFiles();
        if (old != null) for (File f : old) if (!f.getName().equals(m.buildId)) deleteTree(f);
        Log.i("Puzzleth", "downloaded Nightly build " + m.buildId + (m.buildNumber > 0 ? " (#" + m.buildNumber + ")" : ""));
    }

    // ---------------------------------------------------------------- files

    /** A copy of ``url`` kept in ``file``, downloaded the first time it is asked for. */
    private static final Map<String, Object> LOCKS = new ConcurrentHashMap<>();
    private static File cached(String url, File file) throws IOException {
        Object lock = LOCKS.computeIfAbsent(url, k -> new Object());
        synchronized (lock) {
            if (file.isFile()) {
                File sha = new File(file.getPath() + ".sha256");
                if (sha.isFile()) {
                    String meta = new String(readAll(new FileInputStream(sha)), StandardCharsets.UTF_8);
                    String[] parts = meta.split(\" \");
                    if (parts.length > 1) {
                        long expect = parseLongSafe(parts[1], -1);
                        if (expect > 0 && file.length() != expect) {
                            //noinspection ResultOfMethodCallIgnored
                            file.delete();
                        } else {
                            return file;
                        }
                    } else {
                        return file;
                    }
                } else {
                    return file;
                }
            }
            String sha = downloadToFile(url, file);
            try (FileOutputStream out = new FileOutputStream(file.getPath() + \".sha256\")) {
                String meta = sha + \" \" + file.length();
                out.write(meta.getBytes(StandardCharsets.UTF_8));
            } catch (IOException ignored) {}
            return file;
        }
    }

    private static byte[] downloadToMemory(String url) throws IOException {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(15000);
        c.setReadTimeout(30000);
        try {
            if (c.getResponseCode() != 200) throw new IOException(\"HTTP \" + c.getResponseCode() + \" for \" + url);
            try (InputStream in = c.getInputStream()) {
                return readAll(in);
            }
        } finally {
            c.disconnect();
        }
    }

    private static String downloadToFile(String url, File file) throws IOException {
        File parent = Objects.requireNonNull(file.getParentFile());
        if (!parent.isDirectory() && !parent.mkdirs()) throw new IOException(\"mkdirs\");
        String uid = UUID.randomUUID().toString().replace(\"-\", \"\");
        File part = new File(parent, file.getName() + \".\" + uid + \".part\");
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(15000);
        c.setReadTimeout(30000);
        try {
            if (c.getResponseCode() != 200) throw new IOException(\"HTTP \" + c.getResponseCode() + \" for \" + url);
            MessageDigest md = sha256();
            try (InputStream in = new DigestInputStream(c.getInputStream(), md);
                 OutputStream out = new FileOutputStream(part)) {
                byte[] buf = new byte[65536];
                for (int n; (n = in.read(buf)) > 0; ) out.write(buf, 0, n);
            }
            String sha = hex(md.digest());
            if (!part.renameTo(file)) throw new IOException(\"rename\");
            return sha;
        } finally {
            c.disconnect();
            //noinspection ResultOfMethodCallIgnored
            part.delete();
        }
    }

    private static byte[] readAll(InputStream in) throws IOException {
        try (InputStream src = in; java.io.ByteArrayOutputStream out = new java.io.ByteArrayOutputStream()) {
            byte[] buf = new byte[65536];
            for (int n; (n = src.read(buf)) > 0; ) out.write(buf, 0, n);
            return out.toByteArray();
        }
    }

    private static void saveBytes(byte[] data, File file) throws IOException {
        File parent = file.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) throw new IOException(\"mkdirs\");
        File part = File.createTempFile(file.getName(), \".part\", parent);
        try (OutputStream out = new FileOutputStream(part)) {
            out.write(data);
        }
        if (!part.renameTo(file)) throw new IOException(\"rename\");
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

    // ---------- Manifest (optional, recommended)
    private static class ManifestInfo {
        String buildId;
        long buildNumber;
        String indexSha256;
        String gameSha256;
    }

    private ManifestInfo fetchManifest() {
        try {
            byte[] json = downloadToMemory(NIGHTLY + \"manifest.json?t=\" + System.currentTimeMillis());
            byte[] sig = null;
            try { sig = downloadToMemory(NIGHTLY + \"manifest.sig?t=\" + System.currentTimeMillis()); } catch (IOException ignored) {}
            if (!verifyManifest(json, sig)) {
                Log.i(\"Puzzleth\", \"manifest signature missing or invalid; using hashes only\");
            }
            String s = new String(json, StandardCharsets.UTF_8);
            ManifestInfo m = new ManifestInfo();
            m.buildId = extractJsonString(s, \"buildId\");
            m.indexSha256 = extractJsonString(s, \"indexSha256\");
            m.gameSha256 = extractJsonString(s, \"gameSha256\");
            m.buildNumber = parseLongSafe(extractJsonNumber(s, \"buildNumber\"), 0);
            if (m.buildId == null || !m.buildId.matches(\"[0-9a-f]{6,64}\")) return null;
            return m;
        } catch (IOException e) {
            return null;
        }
    }

    private static boolean verifyManifest(byte[] json, byte[] sig) {
        if (json == null || MANIFEST_PUBKEY_B64.isEmpty()) return false;
        if (sig == null || sig.length == 0) return false;
        try {
            byte[] keyDer = Base64.getDecoder().decode(MANIFEST_PUBKEY_B64);
            KeyFactory kf = KeyFactory.getInstance(\"Ed25519\");
            PublicKey pub = kf.generatePublic(new X509EncodedKeySpec(keyDer));
            Signature s = Signature.getInstance(\"Ed25519\");
            s.initVerify(pub);
            s.update(json);
            return s.verify(Base64.getDecoder().decode(sig));
        } catch (Throwable e) {
            return false;
        }
    }

    private static String extractJsonString(String json, String key) {
        String k = \"\\\"\" + key + \"\\\"\";  // \"key\"
        int i = json.indexOf(k);
        if (i < 0) return null;
        i = json.indexOf(':', i);
        if (i < 0) return null;
        int q1 = json.indexOf('\"', i + 1);
        if (q1 < 0) return null;
        int q2 = json.indexOf('\"', q1 + 1);
        if (q2 < 0) return null;
        return json.substring(q1 + 1, q2);
    }

    private static String extractJsonNumber(String json, String key) {
        String k = \"\\\"\" + key + \"\\\"\";  // \"key\"
        int i = json.indexOf(k);
        if (i < 0) return null;
        i = json.indexOf(':', i);
        if (i < 0) return null;
        int j = i + 1;
        while (j < json.length() && Character.isWhitespace(json.charAt(j))) j++;
        int end = j;
        while (end < json.length() && (Character.isDigit(json.charAt(end)))) end++;
        if (end == j) return null;
        return json.substring(j, end);
    }

    private static long parseLongSafe(String s, long def) {
        if (s == null) return def;
        try { return Long.parseLong(s); } catch (Exception e) { return def; }
    }

    private static MessageDigest sha256() {
        try { return MessageDigest.getInstance(\"SHA-256\"); }
        catch (NoSuchAlgorithmException e) { throw new RuntimeException(e); }
    }

    private static String sha256Hex(byte[] data) {
        MessageDigest md = sha256();
        md.update(data);
        return hex(md.digest());
    }

    private static String hex(byte[] b) {
        final char[] HEX = \"0123456789abcdef\".toCharArray();
        char[] out = new char[b.length * 2];
        for (int i = 0, j = 0; i < b.length; i++) {
            int v = b[i] & 0xff;
            out[j++] = HEX[v >>> 4];
            out[j++] = HEX[v & 0x0f];
        }
        return new String(out);
    }
}
