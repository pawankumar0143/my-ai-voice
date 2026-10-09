
from flask import Flask, request, send_file, jsonify, render_template
import edge_tts
import asyncio
import io

app = Flask(__name__)

VOICES = {
    "hi-male": "hi-IN-MadhurNeural",
    "hi-female": "hi-IN-SwaraNeural",
    "en-male": "en-IN-PrabhatNeural",
    "en-female": "en-IN-NeerjaNeural"
}

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "").strip()
    voice_key = data.get("voice", "hi-female")

    if not text:
        return jsonify({"error": "Pehle script likho."}), 400

    if voice_key not in VOICES:
        return jsonify({"error": "Voice select karo."}), 400

    async def make_audio():
        output = io.BytesIO()
        communicate = edge_tts.Communicate(
            text, VOICES[voice_key]
        )
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                output.write(chunk["data"])
        output.seek(0)
        return output

    try:
        audio = asyncio.run(make_audio())
        return send_file(
            audio,
            mimetype="audio/mpeg",
            as_attachment=False,
            download_name="my-ai-voice.mp3"
        )
    except Exception:
        app.logger.exception("Voice generation failed")
        return jsonify({
            "error": "Voice nahi bani. Internet check karo."
        }), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,  debug=True)