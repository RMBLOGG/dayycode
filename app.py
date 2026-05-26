from flask import Flask, render_template, request, jsonify, session, redirect, url_for, abort, send_file
from functools import wraps
from database import get_supabase, hash_pw, init_db, get_settings, set_setting, slugify
from datetime import datetime, date, timedelta
import json, os, secrets, re, time

import cloudinary
import cloudinary.uploader

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'srcmarket-secret-2024-ganti-ini')

UPLOAD_FOLDER = os.path.join('static', 'uploads')
IMG_FOLDER    = os.path.join('static', 'img')

# ── Cloudinary Config ──────────────────────────────────────
cloudinary.config(
    cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME', 'dzfkklsza'),
    api_key    = os.environ.get('CLOUDINARY_API_KEY',    '588474134734416'),
    api_secret = os.environ.get('CLOUDINARY_API_SECRET', '9c12YJe5rZSYSg7zROQuvmVZ7mg'),
    secure     = True
)

# ── Jinja helpers ──────────────────────────────────────────
@app.context_processor
def inject_globals():
    cfg  = get_settings()
    sb   = get_supabase()
    cats = sb.table('categories').select('*').order('id').execute().data
    return dict(cfg=cfg, categories=cats, now=datetime.now())

def fmt_rp(n):
    return 'Rp ' + '{:,}'.format(int(n or 0)).replace(',', '.')
app.jinja_env.globals['fmt_rp'] = fmt_rp
app.jinja_env.globals['fmt']    = fmt_rp

def parse_json(s):
    try:    return json.loads(s) if s else []
    except: return []
app.jinja_env.globals['parse_json'] = parse_json
app.jinja_env.filters['parse_json'] = parse_json

# ── Auth ───────────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

def gen_order_number():
    sb    = get_supabase()
    today = date.today().strftime('%Y%m%d')
    prefix = f'SC{today}'
    rows  = sb.table('orders').select('order_number').like('order_number', f'{prefix}%').execute().data
    return f"{prefix}{str(len(rows)+1).zfill(4)}"

def gen_token():
    return secrets.token_urlsafe(32)

# ── PUBLIC ─────────────────────────────────────────────────
@app.route('/')
def index():
    sb = get_supabase()

    # Featured products
    featured_raw = (
        sb.table('products')
        .select('*, categories(name)')
        .eq('featured', True)
        .eq('active', True)
        .order('sales', desc=True)
        .limit(6)
        .execute().data
    )
    featured = []
    for p in featured_raw:
        row = dict(p)
        row['cat_name'] = (row.pop('categories') or {}).get('name', '')
        featured.append(row)

    # Latest products
    latest_raw = (
        sb.table('products')
        .select('*, categories(name)')
        .eq('active', True)
        .order('created_at', desc=True)
        .limit(8)
        .execute().data
    )
    latest = []
    for p in latest_raw:
        row = dict(p)
        row['cat_name'] = (row.pop('categories') or {}).get('name', '')
        latest.append(row)

    # Stats
    all_active = sb.table('products').select('sales').eq('active', True).execute().data
    stats = {
        'total_products': len(all_active),
        'total_sales':    sum(p.get('sales', 0) for p in all_active),
    }

    return render_template('index.html', featured=featured, latest=latest, stats=stats)


@app.route('/products')
def products_page():
    sb       = get_supabase()
    cat_slug = request.args.get('cat', '')
    search   = request.args.get('q', '')
    sort     = request.args.get('sort', 'newest')
    page     = int(request.args.get('page', 1))
    limit    = 12
    offset   = (page - 1) * limit

    q = sb.table('products').select('*, categories(name, slug)').eq('active', True)

    if cat_slug:
        # resolve category id first
        cat_row = sb.table('categories').select('id').eq('slug', cat_slug).single().execute().data
        if cat_row:
            q = q.eq('category_id', cat_row['id'])

    if search:
        # PostgREST OR filter
        q = q.or_(f'title.ilike.%{search}%,short_desc.ilike.%{search}%,tech_stack.ilike.%{search}%')

    order_map = {
        'newest':     ('created_at', True),
        'popular':    ('sales', True),
        'price_asc':  ('price', False),
        'price_desc': ('price', True),
    }
    col, desc = order_map.get(sort, ('created_at', True))
    q = q.order(col, desc=desc)

    all_rows = q.execute().data
    total    = len(all_rows)
    prods_raw = all_rows[offset:offset+limit]

    prods = []
    for p in prods_raw:
        row = dict(p)
        cat_info = row.pop('categories') or {}
        row['cat_name'] = cat_info.get('name', '')
        row['cat_slug'] = cat_info.get('slug', '')
        prods.append(row)

    return render_template('products_page.html', products=prods, total=total,
                           page=page, pages=-(-total//limit),
                           cat_slug=cat_slug, search=search, sort=sort)


@app.route('/product/<slug>')
def product_detail(slug):
    sb  = get_supabase()
    raw = (
        sb.table('products')
        .select('*, categories(name, slug)')
        .eq('slug', slug)
        .eq('active', True)
        .single()
        .execute().data
    )
    if not raw:
        abort(404)

    product = dict(raw)
    cat_info = product.pop('categories') or {}
    product['cat_name'] = cat_info.get('name', '')
    product['cat_slug'] = cat_info.get('slug', '')
    product['features_list']    = parse_json(product.get('features', '[]'))
    product['screenshots_list'] = parse_json(product.get('screenshots', '[]'))

    related_raw = (
        sb.table('products')
        .select('*, categories(name)')
        .eq('category_id', product['category_id'])
        .eq('active', True)
        .neq('id', product['id'])
        .limit(4)
        .execute().data
    )
    related = []
    for p in related_raw:
        row = dict(p)
        row['cat_name'] = (row.pop('categories') or {}).get('name', '')
        related.append(row)

    return render_template('product_detail.html', product=product, related=related)


@app.route('/buy/<slug>', methods=['GET', 'POST'])
def buy(slug):
    sb  = get_supabase()
    raw = sb.table('products').select('*').eq('slug', slug).eq('active', True).single().execute().data
    if not raw:
        abort(404)
    product = dict(raw)

    if request.method == 'POST':
        data  = request.json
        name  = data.get('name', '').strip()
        email = data.get('email', '').strip()
        wa    = data.get('whatsapp', '').strip()
        if not name or not email:
            return jsonify({'error': 'Nama dan email wajib diisi'}), 400

        order_num = gen_order_number()
        sb.table('orders').insert({
            'order_number':      order_num,
            'customer_name':     name,
            'customer_email':    email,
            'customer_whatsapp': wa,
            'product_id':        product['id'],
            'product_title':     product['title'],
            'amount':            product['price'],
            'status':            'pending',
        }).execute()
        return jsonify({'ok': True, 'order_number': order_num})

    return render_template('buy.html', product=product)


@app.route('/order/<order_number>')
def order_page(order_number):
    sb  = get_supabase()
    raw = sb.table('orders').select('*').eq('order_number', order_number).single().execute().data
    if not raw:
        abort(404)
    return render_template('order_page.html', order=dict(raw))


@app.route('/api/upload-proof/<order_number>', methods=['POST'])
def upload_proof(order_number):
    sb  = get_supabase()
    raw = sb.table('orders').select('*').eq('order_number', order_number).single().execute().data
    if not raw:
        return jsonify({'error': 'Order tidak ditemukan'}), 404
    if raw['status'] not in ('pending',):
        return jsonify({'error': 'Order sudah diproses'}), 400

    file = request.files.get('proof')
    if not file:
        return jsonify({'error': 'File tidak ada'}), 400
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
        return jsonify({'error': 'Format tidak didukung'}), 400

    # Upload to Cloudinary
    try:
        result = cloudinary.uploader.upload(
            file,
            folder='srcmarket/proofs',
            public_id=f'proof_{order_number}_{int(time.time())}',
            transformation=[{'width': 1200, 'quality': 'auto'}]
        )
        proof_url = result['secure_url']
    except Exception as e:
        return jsonify({'error': f'Upload gagal: {str(e)}'}), 500

    sb.table('orders').update({
        'payment_proof': proof_url,
        'status':        'waiting_confirm',
        'updated_at':    datetime.now().isoformat(),
    }).eq('order_number', order_number).execute()

    return jsonify({'ok': True})


@app.route('/download/<token>')
def download_file(token):
    sb  = get_supabase()
    raw = sb.table('orders').select('*').eq('download_token', token).single().execute().data
    if not raw:
        abort(404)
    order = dict(raw)

    # Check expiry
    if order.get('download_expires'):
        exp = datetime.fromisoformat(order['download_expires'])
        if datetime.now() > exp:
            return render_template('download_expired.html'), 410

    # Check max downloads
    cfg    = get_settings()
    max_dl = int(cfg.get('max_download', 3))
    if (order.get('download_count') or 0) >= max_dl:
        return render_template('download_expired.html'), 410

    # Get product
    prod_raw = sb.table('products').select('*').eq('id', order['product_id']).single().execute().data
    if not prod_raw:
        abort(404)
    product = dict(prod_raw)

    # Increment counters
    sb.table('orders').update({'download_count': (order.get('download_count') or 0) + 1}).eq('id', order['id']).execute()
    sb.table('products').update({'downloads': (product.get('downloads') or 0) + 1}).eq('id', product['id']).execute()

    # Serve file — on Vercel filesystem is read-only/ephemeral, prefer file_url
    if product.get('file_url'):
        return redirect(product['file_url'])

    file_path = os.path.join(UPLOAD_FOLDER, product['file_name']) if product.get('file_name') else None
    if file_path and os.path.exists(file_path):
        return send_file(file_path, as_attachment=True, download_name=product['file_name'])

    return "File tidak tersedia", 404


@app.route('/track')
def track():
    order_number = request.args.get('no', '')
    order = None
    if order_number:
        sb  = get_supabase()
        raw = sb.table('orders').select('*').eq('order_number', order_number).single().execute().data
        if raw:
            order = dict(raw)
    return render_template('track.html', order=order, order_number=order_number)


# ── ADMIN ──────────────────────────────────────────────────
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        d  = request.json
        sb = get_supabase()
        rows = (
            sb.table('admins')
            .select('*')
            .eq('username', d['username'])
            .eq('password', hash_pw(d['password']))
            .execute().data
        )
        if rows:
            admin = rows[0]
            session['admin_id']   = admin['id']
            session['admin_name'] = admin['name']
            return jsonify({'ok': True})
        return jsonify({'error': 'Username atau password salah'}), 401
    return render_template('admin/login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))


@app.route('/admin')
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    sb    = get_supabase()
    today = date.today().isoformat()
    month_start = date.today().replace(day=1).isoformat()

    all_orders = sb.table('orders').select('*').execute().data

    def _count(fn):   return sum(1 for o in all_orders if fn(o))
    def _sum(fn, key='amount'): return sum(o.get(key, 0) or 0 for o in all_orders if fn(o))

    stats = {
        'orders_today':   _count(lambda o: o['created_at'][:10] == today),
        'revenue_today':  _sum(lambda o: o['created_at'][:10] == today and o['status'] == 'approved'),
        'orders_month':   _count(lambda o: o['created_at'][:10] >= month_start),
        'revenue_month':  _sum(lambda o: o['created_at'][:10] >= month_start and o['status'] == 'approved'),
        'pending':        _count(lambda o: o['status'] in ('pending', 'waiting_confirm')),
        'total_orders':   len(all_orders),
        'total_sales':    _sum(lambda o: o['status'] == 'approved'),
        'total_products': len(sb.table('products').select('id').eq('active', True).execute().data),
    }

    chart = []
    for i in range(6, -1, -1):
        d    = (date.today() - timedelta(days=i)).isoformat()
        day_orders = [o for o in all_orders if o['created_at'][:10] == d and o['status'] == 'approved']
        chart.append({'date': d, 'total': sum(o.get('amount', 0) or 0 for o in day_orders), 'count': len(day_orders)})

    recent_orders = sorted(all_orders, key=lambda o: o['created_at'], reverse=True)[:10]

    top_products = (
        sb.table('products')
        .select('title,sales,downloads')
        .eq('active', True)
        .order('sales', desc=True)
        .limit(5)
        .execute().data
    )

    return render_template('admin/dashboard.html', stats=stats, chart=chart,
                           recent_orders=recent_orders, top_products=top_products)


@app.route('/admin/orders')
@admin_required
def admin_orders():
    sb     = get_supabase()
    status = request.args.get('status', '')
    search = request.args.get('q', '')
    page   = int(request.args.get('page', 1))
    limit  = 20

    q = sb.table('orders').select('*')
    if status:
        q = q.eq('status', status)
    if search:
        q = q.or_(f'order_number.ilike.%{search}%,customer_name.ilike.%{search}%,customer_email.ilike.%{search}%')

    all_rows = q.order('created_at', desc=True).execute().data
    total    = len(all_rows)
    offset   = (page - 1) * limit
    orders   = all_rows[offset:offset+limit]

    return render_template('admin/orders.html', orders=orders, total=total,
                           page=page, pages=-(-total//limit), status=status, search=search)


@app.route('/admin/orders/<int:oid>')
@admin_required
def admin_order_detail(oid):
    sb  = get_supabase()
    raw = sb.table('orders').select('*').eq('id', oid).single().execute().data
    if not raw:
        abort(404)
    order   = dict(raw)
    product = None
    if order.get('product_id'):
        p = sb.table('products').select('*').eq('id', order['product_id']).single().execute().data
        if p:
            product = dict(p)
    return render_template('admin/order_detail.html', order=order, product=product)


@app.route('/admin/products')
@admin_required
def admin_products():
    sb = get_supabase()
    products_raw = (
        sb.table('products')
        .select('*, categories(name)')
        .order('created_at', desc=True)
        .execute().data
    )
    products = []
    for p in products_raw:
        row = dict(p)
        row['cat_name'] = (row.pop('categories') or {}).get('name', '')
        products.append(row)

    categories = sb.table('categories').select('*').order('id').execute().data
    return render_template('admin/products.html', products=products, categories=categories)


@app.route('/admin/settings')
@admin_required
def admin_settings():
    return render_template('admin/settings.html')


# ── ADMIN API ──────────────────────────────────────────────
@app.route('/api/admin/orders/<int:oid>/approve', methods=['POST'])
@admin_required
def api_approve_order(oid):
    cfg    = get_settings()
    hours  = int(cfg.get('download_expiry_hours', 48))
    token  = gen_token()
    expires = (datetime.now() + timedelta(hours=hours)).isoformat()

    sb  = get_supabase()
    raw = sb.table('orders').select('*').eq('id', oid).single().execute().data
    if not raw:
        return jsonify({'error': 'Not found'}), 404

    sb.table('orders').update({
        'status':           'approved',
        'download_token':   token,
        'download_expires': expires,
        'updated_at':       datetime.now().isoformat(),
    }).eq('id', oid).execute()

    sb.table('products').update({
        'sales': (sb.table('products').select('sales').eq('id', raw['product_id']).single().execute().data or {}).get('sales', 0) + 1
    }).eq('id', raw['product_id']).execute()

    download_url = url_for('download_file', token=token, _external=True)
    return jsonify({'ok': True, 'download_url': download_url, 'token': token})


@app.route('/api/admin/orders/<int:oid>/reject', methods=['POST'])
@admin_required
def api_reject_order(oid):
    d  = request.json
    sb = get_supabase()
    sb.table('orders').update({
        'status':     'rejected',
        'note':       d.get('note', ''),
        'updated_at': datetime.now().isoformat(),
    }).eq('id', oid).execute()
    return jsonify({'ok': True})


@app.route('/api/admin/products', methods=['POST'])
@admin_required
def api_add_product():
    d    = request.json
    slug = slugify(d['title'])
    sb   = get_supabase()

    # Ensure unique slug
    base = slug; i = 1
    while sb.table('products').select('id').eq('slug', slug).execute().data:
        slug = f"{base}-{i}"; i += 1

    sb.table('products').insert({
        'title':          d['title'],
        'slug':           slug,
        'short_desc':     d.get('short_desc', ''),
        'description':    d.get('description', ''),
        'price':          d['price'],
        'original_price': d.get('original_price', 0),
        'category_id':    d.get('category_id'),
        'tech_stack':     d.get('tech_stack', ''),
        'features':       json.dumps(d.get('features', [])),
        'demo_url':       d.get('demo_url', ''),
        'file_url':       d.get('file_url', ''),
        'version':        d.get('version', '1.0'),
        'featured':       bool(d.get('featured', False)),
        'active':         True,
    }).execute()
    return jsonify({'ok': True}), 201


@app.route('/api/admin/products/<int:pid>', methods=['PUT'])
@admin_required
def api_update_product(pid):
    d  = request.json
    sb = get_supabase()
    sb.table('products').update({
        'title':          d['title'],
        'short_desc':     d.get('short_desc', ''),
        'description':    d.get('description', ''),
        'price':          d['price'],
        'original_price': d.get('original_price', 0),
        'category_id':    d.get('category_id'),
        'tech_stack':     d.get('tech_stack', ''),
        'features':       json.dumps(d.get('features', [])),
        'demo_url':       d.get('demo_url', ''),
        'file_url':       d.get('file_url', ''),
        'version':        d.get('version', '1.0'),
        'featured':       bool(d.get('featured', False)),
        'active':         bool(d.get('active', True)),
        'thumbnail':      d.get('thumbnail', ''),
    }).eq('id', pid).execute()
    return jsonify({'ok': True})


@app.route('/api/admin/products/<int:pid>', methods=['DELETE'])
@admin_required
def api_delete_product(pid):
    sb = get_supabase()
    sb.table('products').update({'active': False}).eq('id', pid).execute()
    return jsonify({'ok': True})


@app.route('/api/admin/products/<int:pid>/upload-file', methods=['POST'])
@admin_required
def api_upload_product_file(pid):
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file'}), 400
    ext      = file.filename.rsplit('.', 1)[-1].lower()
    filename = f"product_{pid}_{secrets.token_hex(6)}.{ext}"
    file.save(os.path.join(UPLOAD_FOLDER, filename))
    sb = get_supabase()
    sb.table('products').update({'file_name': filename}).eq('id', pid).execute()
    return jsonify({'ok': True, 'filename': filename})


@app.route('/api/admin/products/<int:pid>/upload-thumbnail', methods=['POST'])
@admin_required
def api_upload_thumbnail(pid):
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No file'}), 400
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
        return jsonify({'error': 'Format tidak didukung'}), 400
    try:
        result = cloudinary.uploader.upload(
            file,
            folder='srcmarket/thumbnails',
            public_id=f'thumbnail_{pid}',
            overwrite=True,
            transformation=[{'width': 800, 'height': 600, 'crop': 'fill', 'quality': 'auto'}]
        )
        url = result['secure_url']
    except Exception as e:
        return jsonify({'error': f'Upload gagal: {str(e)}'}), 500

    sb = get_supabase()
    sb.table('products').update({'thumbnail': url}).eq('id', pid).execute()
    return jsonify({'ok': True, 'url': url})


@app.route('/api/admin/products/<int:pid>/upload-screenshot', methods=['POST'])
@admin_required
def api_upload_screenshot(pid):
    file = request.files.get('image')
    if not file:
        return jsonify({'error': 'No file'}), 400
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ('jpg', 'jpeg', 'png', 'gif', 'webp'):
        return jsonify({'error': 'Format tidak didukung'}), 400
    try:
        result = cloudinary.uploader.upload(
            file,
            folder='srcmarket/screenshots',
            public_id=f'ss_{pid}_{int(time.time())}',
            transformation=[{'width': 1280, 'height': 720, 'crop': 'fill', 'gravity': 'auto', 'quality': 'auto'}]
        )
        url = result['secure_url']
    except Exception as e:
        return jsonify({'error': f'Upload gagal: {str(e)}'}), 500

    sb  = get_supabase()
    raw = sb.table('products').select('screenshots').eq('id', pid).single().execute().data
    screenshots = parse_json((raw or {}).get('screenshots', '[]'))
    screenshots.append(url)
    sb.table('products').update({'screenshots': json.dumps(screenshots)}).eq('id', pid).execute()
    return jsonify({'ok': True, 'url': url})


@app.route('/api/admin/settings', methods=['POST'])
@admin_required
def api_save_settings():
    for k, v in request.json.items():
        set_setting(k, str(v))
    return jsonify({'ok': True})


@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    init_db()
    print("\n✅ SourceMarket (Supabase) siap!")
    print("🌐 Site:  http://localhost:5000")
    print("🔐 Admin: http://localhost:5000/admin")
    print("   Login: admin / admin123\n")
    app.run(debug=True, port=5000)
