import os
from medical_chatbot import app  # This is correct if your Gradio Blocks object is named 'app'

port = int(os.environ.get("PORT", 10000))
app = app.queue()
app.launch(server_name="0.0.0.0", server_port=port, share=False)
