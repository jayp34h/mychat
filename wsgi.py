from medical_chatbot import app  # This is correct if your Gradio Blocks object is named 'app'

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))
    app.launch(server_name="0.0.0.0", server_port=port, share=False)