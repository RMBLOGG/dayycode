-- ═══════════════════════════════════════════════════════
-- SourceMarket – Supabase Schema
-- Run this once in Supabase SQL Editor
-- ═══════════════════════════════════════════════════════

-- 1. ADMINS
CREATE TABLE IF NOT EXISTS admins (
    id         BIGSERIAL PRIMARY KEY,
    username   TEXT UNIQUE NOT NULL,
    password   TEXT NOT NULL,
    name       TEXT
);

-- 2. CATEGORIES
CREATE TABLE IF NOT EXISTS categories (
    id   BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    icon TEXT DEFAULT 'fa-code'
);

-- 3. PRODUCTS
CREATE TABLE IF NOT EXISTS products (
    id             BIGSERIAL PRIMARY KEY,
    title          TEXT NOT NULL,
    slug           TEXT UNIQUE NOT NULL,
    short_desc     TEXT,
    description    TEXT,
    price          INTEGER NOT NULL DEFAULT 0,
    original_price INTEGER DEFAULT 0,
    category_id    BIGINT REFERENCES categories(id),
    tech_stack     TEXT DEFAULT '',
    features       TEXT DEFAULT '[]',
    thumbnail      TEXT DEFAULT '',
    screenshots    TEXT DEFAULT '[]',
    demo_url       TEXT DEFAULT '',
    file_url       TEXT DEFAULT '',
    file_name      TEXT DEFAULT '',
    version        TEXT DEFAULT '1.0',
    downloads      INTEGER DEFAULT 0,
    sales          INTEGER DEFAULT 0,
    featured       BOOLEAN DEFAULT FALSE,
    active         BOOLEAN DEFAULT TRUE,
    created_at     TIMESTAMPTZ DEFAULT NOW()
);

-- 4. ORDERS
CREATE TABLE IF NOT EXISTS orders (
    id                 BIGSERIAL PRIMARY KEY,
    order_number       TEXT UNIQUE NOT NULL,
    customer_name      TEXT NOT NULL,
    customer_email     TEXT NOT NULL,
    customer_whatsapp  TEXT,
    product_id         BIGINT REFERENCES products(id),
    product_title      TEXT,
    amount             INTEGER DEFAULT 0,
    payment_proof      TEXT DEFAULT '',
    download_token     TEXT UNIQUE,
    download_expires   TIMESTAMPTZ,
    download_count     INTEGER DEFAULT 0,
    status             TEXT DEFAULT 'pending',
    note               TEXT DEFAULT '',
    created_at         TIMESTAMPTZ DEFAULT NOW(),
    updated_at         TIMESTAMPTZ DEFAULT NOW()
);

-- 5. SETTINGS
CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT
);

-- ── Indexes ──────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_products_slug        ON products(slug);
CREATE INDEX IF NOT EXISTS idx_products_active      ON products(active);
CREATE INDEX IF NOT EXISTS idx_products_category_id ON products(category_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_number  ON orders(order_number);
CREATE INDEX IF NOT EXISTS idx_orders_status        ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_download_token ON orders(download_token);

-- ── Disable RLS (service key bypasses anyway) ────────────
ALTER TABLE admins     DISABLE ROW LEVEL SECURITY;
ALTER TABLE categories DISABLE ROW LEVEL SECURITY;
ALTER TABLE products   DISABLE ROW LEVEL SECURITY;
ALTER TABLE orders     DISABLE ROW LEVEL SECURITY;
ALTER TABLE settings   DISABLE ROW LEVEL SECURITY;
