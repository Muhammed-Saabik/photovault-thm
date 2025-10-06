from flask import Flask, jsonify, render_template_string, request
import base64
from Crypto.Cipher import AES
import urllib.request
import os
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

DB_HOST = os.environ.get("DATABASE_HOST", "db")
DB_USER = os.environ.get("DATABASE_USER", "pvuser")
DB_PASS = os.environ.get("DATABASE_PASSWORD", "pvpass")
DB_NAME = os.environ.get("DATABASE_NAME", "photovault")

INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>PhotoVault — Secure Photo Management</title>

  <!-- Bootstrap 5 (CDN) -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">

  <style>
    :root{
      --bg-1: #0f172a;
      --bg-2: #071126;
      --accent: #6ee7b7;
      --muted: rgba(255,255,255,0.75);
    }
    body {
      background: linear-gradient(120deg,var(--bg-1) 0%, var(--bg-2) 60%);
      color: #eef6fb;
      font-family: Inter, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
    }
    .navbar { background: rgba(255,255,255,0.02); backdrop-filter: blur(4px); }
    .hero {
      padding: 4rem 1rem;
    }
    .card-soft { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.04); }
    .feature-icon { width:48px;height:48px;border-radius:10px;background:rgba(255,255,255,0.03);display:flex;align-items:center;justify-content:center;color:var(--accent);font-weight:700 }
    .muted { color: var(--muted); }
    .gallery-img { height:150px; object-fit:cover; border-radius:8px; }
    footer { color: rgba(255,255,255,0.6); padding: 2rem 0; }
    h3 { color: rgba(255,255,255,0.9); }
  </style>
</head>
<body>
  <nav class="navbar navbar-expand-lg navbar-dark px-4">
    <div class="container-fluid">
      <a class="navbar-brand d-flex align-items-center" href="#">
        <div style="width:36px;height:36px;border-radius:8px;background:linear-gradient(135deg,#34d399,#60a5fa);display:inline-block;margin-right:10px"></div>
        <div style="font-weight:700;letter-spacing:0.4px">PhotoVault</div>
      </a>

      <div class="d-flex ms-auto">
        <a class="btn btn-outline-light btn-sm me-2" href="/user/profile/1">Sign in</a>
        <a class="btn btn-light btn-sm" href="/user/profile/1">Get started</a>
      </div>
    </div>
  </nav>

  <main class="container">
    <section class="row hero align-items-center">
      <div class="col-md-7">
        <h1 class="display-6" style="font-weight:700">Secure, simple photo storage for teams and creators</h1>
        <p class="muted lead">Store, organize and share high-resolution images with powerful tagging, privacy controls, and fast search.</p>

        <div class="mt-4">
          <a class="btn btn-lg btn-light me-2" href="/user/profile/1">Try PhotoVault</a>
          <a class="btn btn-outline-light btn-lg" href="/admin/page">Admin Console</a>
        </div>

        <div class="row mt-4">
          <div class="col-6 col-sm-4 col-lg-4 mt-3">
            <div class="card-soft p-3 h-100">
              <div class="feature-icon mb-2">P</div>
              <div style="font-weight:600">Private by default</div>
              <div class="muted small">Control who sees your albums and photos.</div>
            </div>
          </div>
          <div class="col-6 col-sm-4 col-lg-4 mt-3">
            <div class="card-soft p-3 h-100">
              <div class="feature-icon mb-2">S</div>
              <div style="font-weight:600">Smart search</div>
              <div class="muted small">Find photos quickly with tags, OCR and full-text notes.</div>
            </div>
          </div>
          <div class="col-6 col-sm-4 col-lg-4 mt-3">
            <div class="card-soft p-3 h-100">
              <div class="feature-icon mb-2">A</div>
              <div style="font-weight:600">Team access</div>
              <div class="muted small">Invite collaborators and manage roles for projects.</div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-md-5">
        <div class="card card-soft p-3">
          <div class="row g-2">
            <div class="col-6">
              <img class="gallery-img" src="https://picsum.photos/seed/1/400/300" alt="sample">
            </div>
            <div class="col-6">
              <img class="gallery-img" src="https://picsum.photos/seed/2/400/300" alt="sample">
            </div>
            <div class="col-6">
              <img class="gallery-img" src="https://picsum.photos/seed/3/400/300" alt="sample">
            </div>
            <div class="col-6">
              <img class="gallery-img" src="https://picsum.photos/seed/4/400/300" alt="sample">
            </div>
          </div>
        </div>
      </div>
    </section>

    <section class="row mt-4">
      <div class="col-md-8">
        <div class="card card-soft p-4">
          <h3 style="font-weight:700">Designed for creators and teams</h3>
          <p class="muted">PhotoVault helps teams organize visual assets in a central place. Powerful tagging, album sharing and integrations let you stay focused on creating.</p>

          <div class="mt-3">
            <!-- Inline search for photos (shows input, calls /vuln_search and renders results) -->
<div class="d-inline-block">
  <button id="showSearch" class="btn btn-outline-light btn-sm me-2">Search photos</button>
</div>

<div id="searchArea" class="mt-3" style="display:none; max-width:560px;">
  <form id="searchForm" class="input-group input-group-sm" onsubmit="doSearch(event)">
    <input id="searchInput" class="form-control" type="search" placeholder="Eg: search landscape" required aria-label="Search photos">
    <button class="btn btn-light" type="submit">Go</button>
  </form>
  <div id="searchResults" class="mt-2 small muted" style="white-space:pre-wrap;"></div>
</div>

<script>
  // Toggle the inline search input
  document.getElementById('showSearch').addEventListener('click', function(){
    const a = document.getElementById('searchArea');
    a.style.display = (a.style.display === 'none') ? 'block' : 'none';
    document.getElementById('searchInput').focus();
    // Clear previous results
    document.getElementById('searchResults').textContent = '';
  });

  // Perform search by calling the vulnerable endpoint and render results
  async function doSearch(evt){
  evt.preventDefault();
  const q = document.getElementById('searchInput').value.trim();
  if (!q) return;
  // Redirect to friendly results page
  window.location.href = '/search?q=' + encodeURIComponent(q);
}
</script>

            <div class="mt-3">
  <button id="showImporter" class="btn btn-outline-light btn-sm me-2">Import from URL</button>
</div>

<div id="inlineImporter" class="mt-3" style="display:none;">
  <form id="inlineImportForm" onsubmit="doInlineImport(event)" class="d-flex gap-2">
    <input id="inlineUrl" type="url" class="form-control form-control-sm" placeholder="Enter URL to import" required>
    <button class="btn btn-light btn-sm" type="submit">Fetch</button>
  </form>
  <div id="inlineResult" class="mt-2 small muted" style="white-space:pre-wrap;"></div>
</div>

<script>
  document.getElementById('showImporter').addEventListener('click', function(){
    const area = document.getElementById('inlineImporter');
    area.style.display = (area.style.display === 'none') ? 'block' : 'none';
    document.getElementById('inlineUrl').focus();
  });

  async function doInlineImport(evt){
    evt.preventDefault();
    const url = document.getElementById('inlineUrl').value.trim();
    if(!url) return;
    const resultEl = document.getElementById('inlineResult');
    resultEl.textContent = 'Fetching ...';

    try {
      // call the intentionally vulnerable endpoint
      const res = await fetch('fetch?url=' + encodeURIComponent(url));
      const j = await res.json();
      resultEl.textContent = JSON.stringify(j, null, 2);
    } catch (err) {
      resultEl.textContent = 'Error: ' + String(err);
    }
  }
</script>
          </div>
        </div>
      </div>

      <div class="col-md-4">
        <div class="card card-soft p-3">
          <h3 style="font-weight:700">Company</h3>
          <ul class="muted small mb-0">
            <li>Privacy-first photo management</li>
            <li>Secure storage & backups</li>
            <li>Integrations with popular tools</li>
          </ul>
        </div>
      </div>
    </section>

    <footer class="text-center mt-5">
      <div class="container">
        <div class="row">
          <div class="col-md-6 text-md-start muted">
            &copy; PhotoVault Inc.
            <div class="small">Built with performance and security in mind.</div>
          </div>
        </div>
      </div>
    </footer>
  </main>

  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""



@app.route("/")
def index():
    return render_template_string(INDEX_HTML)

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/dbinfo")
def dbinfo():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return jsonify({"db_connected": True, "users_count": count})
    except Error as e:
        return jsonify({"db_connected": False, "error": str(e)}), 500

# vulnerable search endpoint (intentionally vulnerable to SQL Injection)
@app.route("/vuln_search")
def vuln_search():
    q = request.args.get("q", "")
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
        )
        cursor = conn.cursor()
        # INTENTIONAL: insecure string formatting (vulnerable to SQLi)
        sql = "SELECT name, value FROM secrets WHERE name = '%s';" % q
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        # build simple JSON-like output
        results = [{"name": r[0], "value": r[1]} for r in rows]
        return jsonify({"query": q, "results": results})
    except Error as e:
        return jsonify({"error": str(e)}), 500


# SSRF-vulnerable fetch endpoint (intentional)
@app.route("/fetch")
def fetch():
    """
    Fetches the URL provided in `url` query param and returns the response body.
    This is intentionally insecure for the CTF — no validation/scheme/host filtering.
    Example: /fetch?url=http://example.com
    """
    target = request.args.get("url", "")
    if not target:
        return jsonify({"error": "missing url parameter"}), 400

    try:
        # Use urllib to fetch the remote resource.
        # NOTE: this will follow redirects and return raw body as text.
        with urllib.request.urlopen(target, timeout=5) as resp:
            content = resp.read()
            # try to decode as utf-8 to return readable JSON/text for the CTF
            try:
                text = content.decode("utf-8", errors="replace")
            except Exception:
                text = str(content)
            return jsonify({"url": target, "status": resp.status, "body_preview": text[:2000]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/user/profile/<int:user_id>")
def user_profile(user_id):
    """
    IDOR demonstration: returns profile info for any user_id without authentication.
    Players can enumerate user IDs to view other users' info (including admin).
    """
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
        )
        cursor = conn.cursor()
        # INTENTIONAL: allow reading any user by ID with no auth checks
        cursor.execute("SELECT id, username, role FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return jsonify({"error": "user not found"}), 404
        return jsonify({"id": row[0], "username": row[1], "role": row[2]})
    except Error as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/page")
def admin_page():
    """
    Simulated client-side admin link hiding. The page contains JS that will show an
    "Admin Console" link only if document.cookie contains 'role=admin'. This is
    purely client-side — server does NOT validate role when /admin/secret is requested.
    The serious vulnerability: /admin/secret is NOT protected server-side.
    """
    html = """
    <!doctype html>
    <title>Admin Panel (client-hidden)</title>
    <h1>PhotoVault — Dashboard</h1>
    <p>Welcome to PhotoVault. If you are admin you will see a link to the admin console.</p>
    <div id="admin-link" style="display:none;">
      <a href="/admin/secret">Admin Console (server-side NOT protected)</a>
    </div>
    <script>
      // Client-side role check (intentionally weak/insufficient for the CTF)
      if (document.cookie && document.cookie.indexOf('role=admin') !== -1) {
        document.getElementById('admin-link').style.display = 'block';
      }
    </script>
    """
    return html


@app.route("/admin/secret")
def admin_secret():
    """
    INTENTIONAL: This endpoint returns the admin secret (BAC flag) without verifying
    the requester's role. This models a missing server-side ACL check.
    """
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM secrets WHERE name = 'bac_flag' LIMIT 1")
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify({"admin_secret": row[0]})
    except Error as e:
        return jsonify({"error": str(e)}), 500

# Hard-coded key & IV (16 bytes each) — THIS IS THE CRYPTO FLAW
AES_KEY = b"Th1sIsAHardC0d3Key"[:16]   # 16 bytes
AES_IV  = b"0000000000000000"         # 16 bytes fixed IV

def pad(s: bytes) -> bytes:
    pad_len = 16 - (len(s) % 16)
    return s + bytes([pad_len]) * pad_len

def unpad(s: bytes) -> bytes:
    pad_len = s[-1]
    return s[:-pad_len]

def aes_encrypt(plaintext: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv=AES_IV)
    return cipher.encrypt(pad(plaintext))

def aes_decrypt(ciphertext: bytes) -> bytes:
    cipher = AES.new(AES_KEY, AES.MODE_CBC, iv=AES_IV)
    return unpad(cipher.decrypt(ciphertext))

@app.route("/crypto_blob")
def crypto_blob():
    """
    Returns the AES-CBC ciphertext (base64) of the cryptographic flag.
    The key and IV are intentionally hard-coded above to demonstrate cryptographic failure.
    """
    # In a real CTF we would store ciphertext in DB; here we generate it on-demand from plaintext flag.
    plaintext = b"FLAG{THM-CRYPTO-a1z9}"
    ct = aes_encrypt(plaintext)
    b64 = base64.b64encode(ct).decode()
    # return ciphertext only (players will need to use the key/IV from source to decrypt)
    return jsonify({"ciphertext_b64": b64, "note": "key and iv are hard-coded in source (insecure)"})


@app.route("/search")
def search_page():
    """
    Friendly search results page that queries the same vulnerable SQL (intentionally)
    and renders a results page. This is what the inline search will redirect to.
    """
    q = request.args.get("q", "")
    # Perform the same insecure query as /vuln_search on purpose for the CTF
    try:
        conn = mysql.connector.connect(
            host=DB_HOST, user=DB_USER, password=DB_PASS, database=DB_NAME
        )
        cursor = conn.cursor()
        # INTENTIONAL: insecure string formatting (vulnerable to SQLi)
        sql = "SELECT name, value FROM secrets WHERE name = '%s';" % q
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
    except Error as e:
        rows = []
        err = str(e)
    else:
        err = None

    # Render a simple HTML page with results
    rows_html = ""
    if rows:
        for r in rows:
            name = r[0]
            val = r[1]
            rows_html += f'<div class="card card-soft mb-2 p-3"><div class="fw-bold">{name}</div><div class="muted small monos">{val}</div></div>'
    else:
        rows_html = '<div class="alert alert-light">No photo found</div>'

    page = f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width,initial-scale=1">
      <title>Search results — PhotoVault</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
      <style>
        body {{ background: linear-gradient(120deg,#0f172a 0%, #071126 60%); color:#eef6fb; font-family:Inter, system-ui; }}
        .container {{ padding:2rem 1rem; }}
        .card-soft {{ background: rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.04); }}
        .muted {{ color: rgba(255,255,255,0.75); }}
        .monos {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", monospace; word-break:break-all; }}
      </style>
    </head>
    <body>
      <div class="container">
        <a href="/" class="text-decoration-none mb-3 d-inline-block">&larr; Back to home</a>
        <h1 class="h4">Search results for: <span class="fw-bold">{q}</span></h1>
        <div class="mt-3">
          {rows_html}
        </div>
      </div>
    </body>
    </html>
    """
    return page



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
