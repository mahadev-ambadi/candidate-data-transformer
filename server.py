from flask import Flask, jsonify, send_from_directory, request
import os
import logging
from werkzeug.utils import secure_filename
from main import run_pipeline

app = Flask(__name__, static_folder="frontend")
app.config['JSON_SORT_KEYS'] = False

# Global cache for pipeline data
_pipeline_cache = None

@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

@app.route("/api/run", methods=["GET"])
def api_run():
    global _pipeline_cache
    try:
        logging.info("Executing pipeline from Flask...")
        _pipeline_cache = run_pipeline()
        return jsonify({"success": True})
    except Exception as e:
        logging.error(f"Pipeline execution failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/api/upload", methods=["POST"])
def api_upload():
    global _pipeline_cache
    try:
        upload_dir = os.path.join(os.path.dirname(__file__), "data", "uploads")
        os.makedirs(upload_dir, exist_ok=True)
        
        expected_files = ["ats.json", "recruiter.csv", "github_profiles.json", "recruiter_notes.txt"]
        
        # Save uploaded files
        for expected in expected_files:
            if expected in request.files:
                file = request.files[expected]
                if file.filename:
                    filename = secure_filename(expected)
                    file.save(os.path.join(upload_dir, filename))
            else:
                return jsonify({"success": False, "error": f"Missing required file: {expected}"}), 400
                
        logging.info("Files uploaded successfully. Triggering pipeline...")
        _pipeline_cache = run_pipeline(
            ats_path=os.path.join(upload_dir, "ats.json"),
            recruiter_csv_path=os.path.join(upload_dir, "recruiter.csv"),
            github_path=os.path.join(upload_dir, "github_profiles.json"),
            notes_path=os.path.join(upload_dir, "recruiter_notes.txt")
        )
        return jsonify({"success": True})
    except Exception as e:
        logging.error(f"Upload and pipeline execution failed: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

def ensure_pipeline():
    global _pipeline_cache
    if _pipeline_cache is None:
        _pipeline_cache = run_pipeline()

@app.route("/api/dashboard", methods=["GET"])
def api_dashboard():
    ensure_pipeline()
    return jsonify({
        "stats": _pipeline_cache.get("stats", {}),
        "scored_candidates": [c.model_dump(mode='json') for c in _pipeline_cache.get("scored_candidates", [])]
    })

@app.route("/api/candidates", methods=["GET"])
def api_candidates():
    ensure_pipeline()
    return jsonify([c.model_dump(mode='json') for c in _pipeline_cache.get("scored_candidates", [])])

@app.route("/api/analytics", methods=["GET"])
def api_analytics():
    ensure_pipeline()
    return jsonify({
        "stats": _pipeline_cache.get("stats", {}),
        "raw_candidates": [c.model_dump(mode='json') for c in _pipeline_cache.get("raw_candidates", [])],
        "merged_candidates": [c.model_dump(mode='json') for c in _pipeline_cache.get("merged_candidates", [])],
        "normalized_candidates": [c.model_dump(mode='json') for c in _pipeline_cache.get("normalized_candidates", [])],
        "scored_candidates": [c.model_dump(mode='json') for c in _pipeline_cache.get("scored_candidates", [])]
    })

@app.route("/api/provenance", methods=["GET"])
def api_provenance():
    ensure_pipeline()
    return jsonify([c.model_dump(mode='json') for c in _pipeline_cache.get("scored_candidates", [])])

@app.route("/api/json", methods=["GET"])
def api_json():
    ensure_pipeline()
    return jsonify(_pipeline_cache.get("projected_output", []))

if __name__ == "__main__":
    app.run(debug=True, port=5000)
