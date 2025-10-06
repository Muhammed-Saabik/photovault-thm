from flask import Flask, jsonify

app = Flask(__name__)

# internal-only metadata (SSRF target). Will be reachable from web container but NOT from host.
@app.route("/metadata")
def metadata():
    return jsonify({
        "service": "internal-metadata",
        "internal_secret": "FLAG{THM-SSRF-PLACEHOLDER}",
        "admin_contact": "admin@photovault.local"
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
