#!/usr/bin/env python3
import os
import sys
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime

# 🔒 Leer la URI desde la variable de entorno
MONGO_URI = os.getenv("MONGODB_URI")
if not MONGO_URI:
    print("❌ Error: La variable de entorno MONGODB_URI no está definida", file=sys.stderr)
    sys.exit(1)

DB_NAME = MONGO_URI.rsplit("/", 1)[-1]
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

MAX_SAMPLES = 100

def flatten(doc, parent="", sep="."):
    items = {}
    for k, v in doc.items():
        nk = f"{parent}{sep}{k}" if parent else k
        if isinstance(v, dict):
            items.update(flatten(v, nk, sep))
        elif isinstance(v, list) and v and isinstance(v[0], dict):
            items.update(flatten(v[0], nk + "[0]", sep))
        else:
            items[nk] = type(v).__name__
    return items

def analyze(col):
    fields = defaultdict(set)
    count = 0
    for doc in db[col].find().limit(MAX_SAMPLES):
        for k, t in flatten(doc).items():
            fields[k].add(t)
        count += 1
    return {
        "col": col,
        "sampled": count,
        "estimated": db[col].estimated_document_count(),
        "fields": {k: sorted(v) for k, v in fields.items()}
    }

def get_type_color(type_name):
    """Retorna color CSS para diferentes tipos de datos"""
    colors = {
        'str': '#10B981',
        'int': '#3B82F6',
        'float': '#8B5CF6',
        'bool': '#F59E0B',
        'ObjectId': '#EF4444',
        'datetime': '#06B6D4',
        'list': '#84CC16',
        'dict': '#EC4899',
        'NoneType': '#6B7280',
    }
    return colors.get(type_name, '#6B7280')

def generate_html_report(schema, db_name):
    """Genera un reporte HTML moderno y profesional"""
    timestamp = datetime.now().strftime('%d de %B de %Y a las %H:%M')
    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>MongoDB Schema – {db_name}</title>
  <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
  <style>
    * {{ margin:0; padding:0; box-sizing:border-box }}
    body {{
      font-family:'Inter',sans-serif;
      background:linear-gradient(135deg,#667eea,#764ba2);
      color:#1f2937;
      line-height:1.6;
      min-height:100vh;
    }}
    .container {{ max-width:1200px; margin:2rem auto; padding:1rem; }}
    .header {{
      background:rgba(255,255,255,0.95);
      backdrop-filter:blur(10px);
      border-radius:20px;
      padding:2rem;
      margin-bottom:2rem;
      box-shadow:0 10px 15px rgba(0,0,0,0.1);
    }}
    .header h1 {{
      font-size:2rem;
      font-weight:800;
      background:linear-gradient(135deg,#667eea,#764ba2);
      -webkit-background-clip:text;
      -webkit-text-fill-color:transparent;
      display:flex; align-items:center; gap:0.5rem;
    }}
    .db-info {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(200px,1fr)); gap:1rem; margin-top:1rem; }}
    .info-card {{
      background:#f8fafc;
      padding:1rem;
      border-radius:12px;
      text-align:center;
      border:1px solid #e2e8f0;
    }}
    .info-card .value {{ font-size:1.5rem; font-weight:700; color:#1e40af; }}
    .info-card .label {{ font-size:0.75rem; color:#64748b; text-transform:uppercase; }}
    .collections-grid {{
      display:grid;
      grid-template-columns:repeat(auto-fill,minmax(400px,1fr));
      gap:1.5rem;
    }}
    .collection-card {{
      background:rgba(255,255,255,0.95);
      border-radius:16px;
      padding:1.5rem;
      box-shadow:0 4px 6px rgba(0,0,0,0.1);
      position:relative;
      overflow:hidden;
      transition:transform .3s;
    }}
    .collection-card:hover {{ transform:translateY(-4px); }}
    .collection-header {{ margin-bottom:1rem; }}
    .collection-name {{
      font-size:1.25rem;
      font-weight:700;
      display:flex;
      align-items:center;
      gap:0.5rem;
    }}
    .collection-stats {{ display:flex; gap:1rem; margin-bottom:1rem; }}
    .stat {{ flex:1; background:#f1f5f9; padding:.5rem; border-radius:8px; text-align:center; }}
    .stat-value {{ font-weight:600; color:#1e40af; }}
    .stat-label {{ font-size:.75rem; color:#64748b; text-transform:uppercase; }}
    .fields-section {{ margin-top:1rem; }}
    .fields-title {{ font-weight:600; margin-bottom:.75rem; display:flex; align-items:center; gap:.5rem; }}
    .field {{
      display:flex;
      justify-content:space-between;
      padding:.5rem;
      background:#f9fafb;
      border-radius:8px;
      margin-bottom:.5rem;
    }}
    .field-name {{ font-family:'JetBrains Mono',monospace; }}
    .field-types {{ display:flex; gap:.25rem; flex-wrap:wrap; }}
    .type-tag {{
      padding:.125rem .5rem;
      border-radius:20px;
      font-size:.75rem;
      font-weight:500;
      color:#fff;
      text-transform:lowercase;
    }}
    .search-box {{
      width:100%;
      padding:1rem;
      border-radius:50px;
      border:2px solid rgba(255,255,255,0.3);
      margin-bottom:2rem;
      outline:none;
    }}
    .footer {{ text-align:center; margin-top:2rem; color:rgba(255,255,255,0.8); }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1><i class="fas fa-database"></i> MongoDB Schema</h1>
      <p>Documentación de <strong>{db_name}</strong> generada el {timestamp}</p>
      <div class="db-info">
        <div class="info-card"><div class="value">{len(schema)}</div><div class="label">Colecciones</div></div>
        <div class="info-card"><div class="value">{sum(s['estimated'] for s in schema):,}</div><div class="label">Documentos</div></div>
        <div class="info-card"><div class="value">{timestamp.split(' a las')[0]}</div><div class="label">Fecha</div></div>
      </div>
    </div>

    <input type="text" id="searchInput" class="search-box" placeholder="🔍 Buscar colecciones o campos...">

    <div class="collections-grid" id="collectionsGrid">
"""
    # Generar cada tarjeta de colección
    for i, col in enumerate(schema):
        html += f'<div class="collection-card" data-collection="{col["col"].lower()}">\n'
        html += f'  <div class="collection-name"><i class="fas fa-folder-open"></i> {col["col"]}</div>\n'
        html += '  <div class="collection-stats">\n'
        html += f'    <div class="stat"><div class="stat-value">{col["estimated"]:,}</div><div class="stat-label">Estimados</div></div>\n'
        html += f'    <div class="stat"><div class="stat-value">{col["sampled"]}</div><div class="stat-label">Muestreados</div></div>\n'
        html += f'    <div class="stat"><div class="stat-value">{len(col["fields"])}</div><div class="stat-label">Campos</div></div>\n'
        html += '  </div>\n  <div class="fields-section">\n'
        html += '    <div class="fields-title"><i class="fas fa-list"></i> Campos y Tipos</div>\n'
        for field, types in col["fields"].items():
            html += f'    <div class="field" data-field="{field.lower()}"><span class="field-name">{field}</span><div class="field-types">\n'
            for t in types:
                color = get_type_color(t)
                html += f'      <span class="type-tag" style="background:{color}">{t}</span>\n'
            html += '    </div></div>\n'
        html += '  </div>\n</div>\n'
    # Cerrar HTML
    html += f"""
    </div>
    <div class="footer"><p>Powered by Python & MongoDB</p></div>
  </div>
  <script>
    const input = document.getElementById('searchInput');
    input.addEventListener('input', () => {{
      const term = input.value.toLowerCase();
      document.querySelectorAll('.collection-card').forEach(card => {{
        const name = card.dataset.collection;
        const fields = Array.from(card.querySelectorAll('.field')).map(f => f.dataset.field);
        const match = name.includes(term) || fields.some(f => f.includes(term));
        card.style.display = match ? 'block' : 'none';
      }});
    }});
  </script>
</body>
</html>
"""
    return html

# -- Ejecución principal --
schema = [analyze(c) for c in db.list_collection_names()]

os.makedirs("docs", exist_ok=True)
html_content = generate_html_report(schema, DB_NAME)
with open("docs/index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ docs/index.html generated")
print("🌐 Abre docs/index.html en tu navegador para ver la documentación")
