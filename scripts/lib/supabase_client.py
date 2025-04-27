# /lib/supabase_client.py
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
class SupabaseClient:
    def __init__(self):
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_KEY')
        self.client = create_client(url, key)
        self.table_name = 'git_checkpoints'

    def get_checkpoint(self):
        data = self.client.table(self.table_name).select('*').order('created_at', desc=True).limit(1).execute()
        if data.data:
            return data.data[0]
        return None

    def save_checkpoint(self, commit_hash, commit_date):
        self.client.table(self.table_name).insert({
            'last_commit': commit_hash,
            'commit_date': commit_date
        }).execute()