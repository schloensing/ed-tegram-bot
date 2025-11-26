from flask import render_template, jsonify, request
import os
import openai
from gtts import gTTS
from io import BytesIO
from base64 import b64encode

app = Flask(__name__)


openai.api_key = os.environ.get("OPENAI_API_KEY")

@app.route("/chat", methods=["GET"])
def chat_page():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat_api():
    data = request.get_json()
    user_msg = data.get("message", "").strip()

    if not user_msg:
        return jsonify({"reply": "Bitte eine Nachricht eingeben.", "audio": None})

    try:
        # Kurze, präzise, professionelle Antwort auf Deutsch
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # funktioniert stabil mit openai==0.28.1
            messages=[
                {"role": "system", "content": "Du bist Ed, ein professioneller deutschsprachiger Assistent. Antworte kurz, präzise und wahrheitsgetreu."},
                {"role": "user", "content": user_msg}
            ],
            max_tokens=220,
            temperature=0.2
        )
        reply = completion.choices[0].message["content"].strip()

        # Optional: Sprachausgabe erzeugen (MP3 als Base64 zurückgeben)
        audio_b64 = None
        try:
            tts = gTTS(text=reply, lang="de")
            buf = BytesIO()
            tts.write_to_fp(buf)
            audio_b64 = b64encode(buf.getvalue()).decode("utf-8")
        except Exception:
            audio_b64 = None  # Falls TTS ausfällt, trotzdem Text liefern

        return jsonify({"reply": reply, "audio": audio_b64})

    except Exception as e:
        # Fallback: klare Fehlermeldung ausgeben
        return jsonify({"reply": f"Fehler bei der Antwortgenerierung: {e}", "audio": None}), 500
