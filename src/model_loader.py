import logging

class ModelLoader:
    def __init__(self, model_name):
        self.model_name = model_name
        self.model = None

    def load_model(self):
        logging.info(f"Loading Ollama model: {self.model_name}")
        # In this scenario, the "model" is just the name for Ollama's API.
        # Ollama's python binding doesn't load models like a local model.
        # We'll just store the model name and use it in inference.
        self.model = self.model_name
        return self.model
