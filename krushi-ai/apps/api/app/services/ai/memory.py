class AIMemoryLayer:
    def __init__(self):
        self.store = {}
    def get_context(self, farmer_id: str) -> dict:
        return self.store.get(farmer_id, {})
    def update_context(self, farmer_id: str, data: dict):
        if farmer_id not in self.store:
            self.store[farmer_id] = {}
        self.store[farmer_id].update(data)
