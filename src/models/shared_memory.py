class SharedMemory:
    def __init__(self):
        self._shared_memory = {}

    @property
    def shared_memory(self):
        return self._shared_memory

    def shared_memory_model_read(self, model_key):
        return self._shared_memory.get(model_key, None)

    def shared_memory_model_write(self, model_key: str, data: dict):
        try:
            self._shared_memory[model_key] = data
        except Exception:
            print(f"Error storing data from {model_key} to shared memory...")
            return False
        else:
            return True
