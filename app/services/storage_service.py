import os
from supabase import create_client, Client
from app.core.config import settings

class StorageService:
    def __init__(self):
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        self.bucket = settings.SUPABASE_STORAGE_BUCKET

    def upload_file(self, file_path: str, destination_path: str) -> str:
        """Uploads a file to Supabase Storage and returns its public URL. Falls back to local."""
        try:
            with open(file_path, "rb") as f:
                res = self.supabase.storage.from_(self.bucket).upload(
                    path=destination_path,
                    file=f,
                    file_options={"x-upsert": "true"}
                )
            url = self.supabase.storage.from_(self.bucket).get_public_url(destination_path)
            return url
        except Exception as e:
            print(f"Supabase upload failed: {e}. Falling back to local storage.")
            import shutil
            local_dest = os.path.join(os.path.dirname(__file__), "..", "..", "static", destination_path)
            os.makedirs(os.path.dirname(local_dest), exist_ok=True)
            shutil.copy(file_path, local_dest)
            return f"{settings.BACKEND_URL}/static/{destination_path}"

    def delete_file(self, path: str):
        try:
            self.supabase.storage.from_(self.bucket).remove([path])
        except Exception:
            local_dest = os.path.join(os.path.dirname(__file__), "..", "..", "static", path)
            if os.path.exists(local_dest):
                os.remove(local_dest)

storage_service = StorageService()
