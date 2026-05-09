from app.db.supabase import get_supabase_client

class AIMemoryLayer:
    def __init__(self):
        self.supabase = get_supabase_client()

    def get_context(self, farmer_id: str) -> dict:
        response = self.supabase.table("farmer_context").select("*").eq("farmer_id", farmer_id).execute()
        if response.data:
            return response.data[0]
        return {}

    def update_context(self, farmer_id: str, new_context: dict):
        response = self.supabase.table("farmer_context").select("id").eq("farmer_id", farmer_id).execute()
        if response.data:
            self.supabase.table("farmer_context").update(new_context).eq("farmer_id", farmer_id).execute()
        else:
            new_context["farmer_id"] = farmer_id
            self.supabase.table("farmer_context").insert(new_context).execute()
