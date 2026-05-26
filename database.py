import hashlib, os, re
from datetime import datetime
from supabase import create_client, Client

# ── Supabase Config ────────────────────────────────────────
# Set these as env vars in Vercel dashboard (recommended)
# Fallback ke hardcoded values untuk development lokal
SUPABASE_URL         = os.environ.get('SUPABASE_URL',         'https://npiuthhiudgpjmwporyv.supabase.co')
SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5waXV0aGhpdWRncGptd3Bvcnl2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3OTc0NTIxOSwiZXhwIjoyMDk1MzIxMjE5fQ.xaFUBkAAbgrAJnK-wzcgCZd3MEELFVw3bLuyiLb4TxM')
SUPABASE_ANON_KEY    = os.environ.get('SUPABASE_ANON_KEY',    'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im5waXV0aGhpdWRncGptd3Bvcnl2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzk3NDUyMTksImV4cCI6MjA5NTMyMTIxOX0.ai9TvQhWrc60yIvoZ5gt6FFZV470OgmgvCuXE1D--qs')

def get_supabase() -> Client:
    """Return Supabase client (service role — bypasses RLS)."""
    return create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()

def slugify(text: str) -> str:
    import unicodedata
    # Normalize unicode (e.g. mathematical bold chars) ke ASCII dulu
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    text = text.strip('-')
    return text or 'product'

# ── Settings helpers ───────────────────────────────────────
def get_settings() -> dict:
    sb = get_supabase()
    rows = sb.table('settings').select('key,value').execute().data
    return {r['key']: r['value'] for r in rows}

def set_setting(key: str, value: str):
    sb = get_supabase()
    sb.table('settings').upsert({'key': key, 'value': value}).execute()

# ── Init DB (run once to seed default data) ────────────────
def init_db():
    """
    Creates tables via Supabase SQL and seeds default data.
    Safe to call multiple times (INSERT OR IGNORE equivalent via upsert/on_conflict).
    """
    sb = get_supabase()

    # Seed default settings
    defaults = [
        ('site_name',            'Dayy Code'),
        ('site_tagline',         'Source Code Premium, Harga Terjangkau'),
        ('site_description',     'Jual beli source code website & aplikasi berkualitas'),
        ('contact_email',        'admin@example.com'),
        ('contact_wa',           '6282320781747'),
        ('bank_name',            'BCA'),
        ('bank_account',         '1234567890'),
        ('bank_holder',          'Dayy Code'),
        ('bank_logo',            ''),
        ('dana_number',          ''),
        ('ovo_number',           ''),
        ('gopay_number',         ''),
        ('payment_holder',       'Dayy Code'),
        ('primary_color',        '#6366f1'),
        ('download_expiry_hours','48'),
        ('max_download',         '3'),
    ]
    for k, v in defaults:
        sb.table('settings').upsert({'key': k, 'value': v}, on_conflict='key').execute()

    # Seed admin
    sb.table('admins').upsert(
        {'username': 'kalajengking', 'password': hash_pw('Dayynime'), 'name': 'Administrator'},
        on_conflict='username'
    ).execute()

    # Seed categories
    cats = [
        ('Website',      'website',     'fa-globe'),
        ('Landing Page', 'landing-page','fa-rocket'),
        ('E-Commerce',   'ecommerce',   'fa-cart-shopping'),
        ('Dashboard',    'dashboard',   'fa-chart-line'),
        ('Mobile App',   'mobile',      'fa-mobile-screen'),
        ('Bot & Script', 'bot-script',  'fa-robot'),
    ]
    for name, slug, icon in cats:
        sb.table('categories').upsert({'name': name, 'slug': slug, 'icon': icon}, on_conflict='slug').execute()

    print("✅ Supabase seeded successfully.")
