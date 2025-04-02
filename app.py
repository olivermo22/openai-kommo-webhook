from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)

# Cargar configuración desde variables de entorno
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

client = openai.OpenAI(api_key=OPENAI_API_KEY)

@app.route("/", methods=["GET"])
def home():
    return "Webhook conectado a OpenAI (Assistant v2 - gpt-4o-mini)"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    mensaje_usuario = data.get("message", {}).get("text", "")
    numero_cliente = data.get("message", {}).get("from", "")

    if not mensaje_usuario:
        return jsonify({"error": "Mensaje vacío"}), 400

    try:
        # Crear un hilo (thread)
        thread = client.beta.threads.create()

        # Añadir el mensaje del usuario al hilo
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=mensaje_usuario
        )

        # Ejecutar el asistente sobre el hilo
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=ASSISTANT_ID
        )

        # Esperar a que termine el run
        while True:
            run_status = client.beta.threads.runs.retrieve(
                thread_id=thread.id,
                run_id=run.id
            )
            if run_status.status == "completed":
                break
            elif run_status.status in ["failed", "cancelled", "expired"]:
                return jsonify({"error": f"Run falló con estado: {run_status.status}"}), 500

        # Obtener la respuesta del asistente
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        respuesta_asistente = messages.data[0].content[0].text.value

        return jsonify({
            "text": respuesta_asistente,
            "to": numero_cliente
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
