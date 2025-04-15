import os
from supabase import create_client

# Initialize Supabase client
# In production, these should be environment variables
SUPABASE_URL = os.environ.get('SUPABASE_URL', 'https://gghwditrxcpeakwijufz.supabase.co')
SUPABASE_KEY = os.environ.get('SUPABASE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdnaHdkaXRyeGNwZWFrd2lqdWZ6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDQyMTI1ODYsImV4cCI6MjA1OTc4ODU4Nn0.F49AbW1_qhTZKkzN0Mtoz3Xsu_YF2lqIowQxSNiZtag')

# Create a single instance of the Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)