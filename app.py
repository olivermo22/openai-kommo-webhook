from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Cargar configuración desde variables de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return "Webhook conectado a OpenAI (gpt-4o-mini)"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    mensaje_usuario = data.get("message", {}).get("text", "")
    numero_cliente = data.get("message", {}).get("from", "")

    if not mensaje_usuario:
        return jsonify({"error": "Mensaje vacío"}), 400

    try:
        client = openai.OpenAI(api_key=OPENAI_API_KEY)

        respuesta = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Eres un asistente profesional, claro y servicial."},
                {"role": "user", "content": mensaje_usuario}
            ]
        )

        mensaje_respuesta = respuesta.choices[0].message.content

        return jsonify({
            "text": mensaje_respuesta,
            "to": numero_cliente
        })

    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500
