#!/usr/bin/env python3
import os
import sys
from pymongo import MongoClient
from collections import defaultdict
from datetime import datetime

# Lee la URI desde la env
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
        'str': '#10B981',      # Verde
        'int': '#3B82F6',      # Azul
        'float': '#8B5CF6',    # Púrpura
        'bool': '#F59E0B',     # Amarillo
        'ObjectId': '#EF4444', # Rojo
        'datetime': '#06B6D4', # Cyan
        'list': '#84CC16',     # Lima
        'dict': '#EC4899',     # Rosa
        'NoneType': '#6B7280', # Gris
    }
    return colors.get(type_name, '#6B7280')

def generate_html_report(schema, db_name):
    """Genera un reporte HTML moderno y profesional"""
    
    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MongoDB Schema - {db_name}</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #1f2937;
            line-height: 1.6;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}

        .header {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2.5rem;
            margin-bottom: 2rem;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        .header h1 {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea, #764ba2);
            background-clip: text;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}

        .header .subtitle {{
            color: #6b7280;
            font-size: 1.1rem;
            margin-bottom: 1.5rem;
        }}

        .db-info {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-top: 1.5rem;
        }}

        .info-card {{
            background: linear-gradient(135deg, #f8fafc, #e2e8f0);
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(255, 255, 255, 0.3);
        }}

        .info-card .value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e40af;
        }}

        .info-card .label {{
            font-size: 0.875rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.25rem;
        }}

        .collections-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 1.5rem;
        }}

        .collection-card {{
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.2);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }}

        .collection-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: linear-gradient(90deg, #667eea, #764ba2);
        }}

        .collection-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.15), 0 10px 10px -5px rgba(0, 0, 0, 0.1);
        }}

        .collection-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 1rem;
        }}

        .collection-name {{
            font-size: 1.25rem;
            font-weight: 700;
            color: #1f2937;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .collection-stats {{
            display: flex;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}

        .stat {{
            text-align: center;
            padding: 0.5rem;
            background: #f8fafc;
            border-radius: 8px;
            border: 1px solid #e2e8f0;
            flex: 1;
        }}

        .stat-value {{
            font-size: 1.1rem;
            font-weight: 600;
            color: #1e40af;
        }}

        .stat-label {{
            font-size: 0.75rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        .fields-section {{
            margin-top: 1rem;
        }}

        .fields-title {{
            font-size: 1rem;
            font-weight: 600;
            color: #374151;
            margin-bottom: 0.75rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .field {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 0.5rem 0.75rem;
            margin-bottom: 0.5rem;
            background: #f9fafb;
            border-radius: 8px;
            border: 1px solid #e5e7eb;
            transition: all 0.2s ease;
        }}

        .field:hover {{
            background: #f3f4f6;
            border-color: #d1d5db;
        }}

        .field-name {{
            font-family: 'JetBrains Mono', Monaco, monospace;
            font-size: 0.875rem;
            color: #374151;
            font-weight: 500;
        }}

        .field-types {{
            display: flex;
            gap: 0.25rem;
            flex-wrap: wrap;
        }}

        .type-tag {{
            display: inline-block;
            padding: 0.125rem 0.5rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 500;
            color: white;
            text-transform: lowercase;
        }}

        .search-container {{
            position: sticky;
            top: 2rem;
            z-index: 10;
            margin-bottom: 2rem;
        }}

        .search-box {{
            width: 100%;
            padding: 1rem 1.5rem;
            font-size: 1rem;
            border: 2px solid rgba(255, 255, 255, 0.3);
            border-radius: 50px;
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            outline: none;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }}

        .search-box:focus {{
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}

        .footer {{
            text-align: center;
            margin-top: 3rem;
            padding: 2rem;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.875rem;
        }}

        .fade-in {{
            animation: fadeIn 0.6s ease-out;
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @media (max-width: 768px) {{
            .container {{
                padding: 1rem;
            }}

            .header h1 {{
                font-size: 2rem;
            }}

            .collections-grid {{
                grid-template-columns: 1fr;
            }}

            .collection-stats {{
                flex-direction: column;
                gap: 0.5rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header fade-in">
            <h1><i class="fas fa-database"></i> Kovatek - MongoDB Docs</h1>
            <p class="subtitle">Documentación automática de la base de datos <strong>{db_name}</strong></p>
            <div class="db-info">
                <div class="info-card">
                    <div class="value">{len(schema)}</div>
                    <div class="label">Colecciones</div>
                </div>
                <div class="info-card">
                    <div class="value">{sum(s['estimated'] for s in schema):,}</div>
                    <div class="label">Documentos totales</div>
                </div>
                <div class="info-card">
                    <div class="value">{datetime.now().strftime('%d/%m/%Y')}</div>
                    <div class="label">Generado</div>
                </div>
            </div>
        </div>

        <div class="search-container">
            <input type="text" class="search-box" placeholder="🔍 Buscar colecciones o campos..." id="searchInput">
        </div>

        <div class="collections-grid" id="collectionsGrid">
"""

    # Generar cards para cada colección
    for i, collection in enumerate(schema):
        html_template += f"""
            <div class="collection-card fade-in" style="animation-delay: {i * 0.1}s;" data-collection="{collection['col'].lower()}">
                <div class="collection-header">
                    <h2 class="collection-name">
                        <i class="fas fa-folder-open"></i>
                        {collection['col']}
                    </h2>
                </div>
                
                <div class="collection-stats">
                    <div class="stat">
                        <div class="stat-value">{collection['estimated']:,}</div>
                        <div class="stat-label">Estimados</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{collection['sampled']}</div>
                        <div class="stat-label">Muestreados</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">{len(collection['fields'])}</div>
                        <div class="stat-label">Campos</div>
                    </div>
                </div>

                <div class="fields-section">
                    <h3 class="fields-title">
                        <i class="fas fa-list"></i>
                        Campos y Tipos
                    </h3>
"""
        
        # Generar campos
        for field_name, field_types in collection['fields'].items():
            html_template += f"""
                    <div class="field" data-field="{field_name.lower()}">
                        <span class="field-name">{field_name}</span>
                        <div class="field-types">
"""
            for type_name in field_types:
                color = get_type_color(type_name)
                html_template += f"""
                            <span class="type-tag" style="background-color: {color};">{type_name}</span>
"""
            
            html_template += """
                        </div>
                    </div>
"""
        
        html_template += """
                </div>
            </div>
"""

    # Cerrar HTML y agregar JavaScript
    html_template += f"""
        </div>

        <div class="footer">
            <p>📊 Generado automáticamente el {datetime.now().strftime('%d de %B de %Y a las %H:%M')} | 
            <i class="fas fa-code"></i> Powered by KovaTek Studio</p>
        </div>
    </div>

    <script>
        // Funcionalidad de búsqueda
        document.getElementById('searchInput').addEventListener('input', function(e) {{
            const searchTerm = e.target.value.toLowerCase();
            const cards = document.querySelectorAll('.collection-card');
            
            cards.forEach(card => {{
                const collectionName = card.dataset.collection;
                const fields = card.querySelectorAll('.field');
                let hasMatch = collectionName.includes(searchTerm);
                
                if (!hasMatch) {{
                    fields.forEach(field => {{
                        if (field.dataset.field.includes(searchTerm)) {{
                            hasMatch = true;
                        }}
                    }});
                }}
                
                if (hasMatch) {{
                    card.style.display = 'block';
                    card.style.animation = 'fadeIn 0.3s ease-out';
                }} else {{
                    card.style.display = 'none';
                }}
            }});
        }});

        // Efectos de hover y interactividad
        document.querySelectorAll('.collection-card').forEach(card => {{
            card.addEventListener('mouseenter', function() {{
                this.style.transform = 'translateY(-8px) scale(1.02)';
            }});
            
            card.addEventListener('mouseleave', function() {{
                this.style.transform = 'translateY(0) scale(1)';
            }});
        }});

        // Smooth scroll para mejor UX
        document.documentElement.style.scrollBehavior = 'smooth';
    </script>
</body>
</html>"""

    return html_template

schema = [analyze(c) for c in db.list_collection_names()]

# Generar tanto Markdown como HTML
os.makedirs("docs", exist_ok=True)

# Markdown output (original)
with open("docs/mongodb_schema.md", "w", encoding="utf-8") as f:
    f.write(f"# MongoDB Schema: `{DB_NAME}`\n\n")
    for s in schema:
        f.write(f"## 🗂 `{s['col']}`\n")
        f.write(f"- Estimated: {s['estimated']} docs\n")
        f.write(f"- Sampled: {s['sampled']} docs\n")
        f.write("### Fields:\n")
        for fld, types in s["fields"].items():
            f.write(f"- `{fld}`: {', '.join(types)}\n")
        f.write("\n")

# HTML output (nuevo)
html_content = generate_html_report(schema, DB_NAME)
with open("docs/mongodb_schema.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print("✅ docs/mongodb_schema.md generated")
print("✅ docs/mongodb_schema.html generated")
print(f"🌐 Open docs/mongodb_schema.html in your browser to view the modern documentation")
