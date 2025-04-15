import os
from supabase import create_client

# Initialize Supabase client
# In production, these should be environment variables
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'xxxxxxxxxx')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'xxxxxxxxxx')

# Create a single instance of the Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
