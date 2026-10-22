import os
import random
from flask import Flask, render_template_string, request, redirect, url_for, session, flash
from supabase import create_client, Client

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "super-tajny-klic")

# Supabase konfigurace
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None

# Kompletní číselník postav podle naší dohody
CHARACTERS = {
    "dimenzionalni_ztroskotanec": {
        "name": "Dimenzionální ztroskotanec",
        "rarity": "Common",
        "income": 1,
        "description": "Obyčejný poutník, který zabloudil v mezidobí. S hodinkami v ruce neustále hledá cestu zpět domů do své dimenze."
    },
    "kvantovy_prenasec": {
        "name": "Kvantový přenašeč",
        "rarity": "Rare",
        "income": 5,
        "description": "Vylepšený bojovník z kyberprostoru s pulzujícím modrým pláštěm. Sleduje digitální stopy a v síti se pohybuje s naprostou lehkostí."
    },
    "strazkyne_nuloveho_bodu": {
        "name": "Strážkyně nulového bodu",
        "rarity": "Super Rare",
        "income": 20,
        "description": "Tajemná postava ovládající temnou energii a nebezpečné stíny. Dokáže nahlédnout do budoucnosti pomocí svých záhadných krystalů."
    },
    "singularni_titan": {
        "name": "Singulární titan",
        "rarity": "Epic",
        "income": 100,
        "description": "Masivní strážce vytvořený z čisté energie a odolných krystalů. Jeho tělo dokáže absorbovat obrovské množství poškození v každém boji."
    },
    "akolyt_nekonecna": {
        "name": "Akolyt nekonečna",
        "rarity": "Mythic",
        "income": 500,
        "description": "Vznešený obránce galaxie zahalený do zářivého zlatého brnění. Vyzařuje sílu samotného slunce a chrání ty nejvzácnější dimenze."
    },
    "architekt_infinity": {
        "name": "Architekt Infinity",
        "rarity": "Legendary",
        "income": 2500,
        "description": "Nejvzácnější vesmírná entita vládnoucí síle času i prostoru. Svou neomezenou mocí udržuje rovnováhu v celé Infinity Zone."
    }
}

# Definice packů a šancí (v %)
PACKS = {
    "maly_pack": {
        "name": "Malý pack",
        "weights": [
            ("dimenzionalni_ztroskotanec", 70.0),
            ("kvantovy_prenasec", 25.0),
            ("strazkyne_nuloveho_bodu", 5.0)
        ]
    },
    "velky_pack": {
        "name": "Velký pack",
        "weights": [
            ("dimenzionalni_ztroskotanec", 35.5),
            ("kvantovy_prenasec", 30.0),
            ("strazkyne_nuloveho_bodu", 20.0),
            ("singularni_titan", 10.0),
            ("akolyt_nekonecna", 4.0),
            ("architekt_infinity", 0.5)
        ]
    }
}

def draw_character_from_pack(pack_key):
    """Vytáhne náhodnou postavu podle vah v packu."""
    pack = PACKS.get(pack_key)
    if not pack:
        return None
    keys, weights = zip(*pack["weights"])
    return random.choices(keys, weights=weights, k=1)[0]

def calculate_hourly_income(inventory):
    """Spočítá celkový pasivní příjem/hod podle postav v batohu."""
    total_income = 0
    for char_id in inventory:
        if char_id in CHARACTERS:
            total_income += CHARACTERS[char_id]["income"]
    return total_income

# HTML šablona s moderním designem pro Infinity Zone
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <title>Infinity Zone</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; }
        .card { background-color: #1e293b; padding: 20px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        h1, h2, h3 { color: #38bdf8; }
        button, .btn { background-color: #3b82f6; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
        button:hover, .btn:hover { background-color: #2563eb; }
        .btn-danger { background-color: #ef4444; }
        .btn-danger:hover { background-color: #dc2626; }
        .inventory-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; margin-top: 15px; }
        .char-card { background: #334155; padding: 15px; border-radius: 8px; border-left: 5px solid #94a3b8; }
        .rarity-Common { border-color: #94a3b8; }
        .rarity-Rare { border-color: #3b82f6; }
        .rarity-Super Rare { border-color: #a855f7; }
        .rarity-Epic { border-color: #ec4899; }
        .rarity-Mythic { border-color: #f59e0b; }
        .rarity-Legendary { border-color: #ef4444; }
        .flash { background-color: #22c55e; color: white; padding: 10px; border-radius: 5px; margin-bottom: 15px; }
        .packs-container { display: flex; gap: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🌌 Infinity Zone</h1>
        
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            {% for message in messages %}
              <div class="flash">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        {% if not user %}
            <div class="card">
                <h2>Přihlášení / Registrace</h2>
                <form action="/login" method="post">
                    <input type="email" name="email" placeholder="E-mail" required style="padding: 8px; margin-right: 5px;">
                    <input type="password" name="password" placeholder="Heslo" required style="padding: 8px; margin-right: 5px;">
                    <button type="submit">Vstoupit do hry</button>
                </form>
            </div>
        {% else %}
            <div class="card">
                <p>Přihlášen jako: <strong>{{ user.email }}</strong> | <a href="/logout" style="color: #f43f5e;">Odhlásit se</a></p>
                <h3>📊 Statistiky účtu</h3>
                <p>⚡ Pasivní příjem: <strong>+{{ hourly_income }} coinů / hodinu</strong></p>
                <form action="/reset" method="post" style="display:inline;">
                    <button type="submit" class="btn btn-danger" onclick="return confirm('Opravdu chceš vymazat svůj dynamický batoh?')">Začít od začátku</button>
                </form>
            </div>

            <div class="card">
                <h2>📦 Otevřít Pack</h2>
                <div class="packs-container">
                    <div>
                        <h3>Malý pack</h3>
                        <p>Obsahuje Common, Rare a Super Rare postavy.</p>
                        <form action="/open-pack/maly_pack" method="post">
                            <button type="submit">Otevřít Malý pack</button>
                        </form>
                    </div>
                    <div>
                        <h3>Velký pack</h3>
                        <p>Obsahuje kompletní výběr včetně šance (0.5%) na Legendary!</p>
                        <form action="/open-pack/velky_pack" method="post">
                            <button type="submit">Otevřít Velký pack</button>
                        </form>
                    </div>
                </div>
            </div>

            <div class="card">
                <h2>🎒 Dynamický batoh ({{ inventory|length }} postav)</h2>
                {% if not inventory %}
                    <p>Tvůj batoh je zatím prázdný. Zkus otevřít nějaký pack!</p>
                {% else %}
                    <div class="inventory-grid">
                        {% for char_id in inventory %}
                            {% set char = characters_db[char_id] %}
                            <div class="char-card rarity-{{ char.rarity }}">
                                <h4>{{ char.name }}</h4>
                                <p><strong>Rarita:</strong> {{ char.rarity }}</p>
                                <p><strong>Příjem:</strong> +{{ char.income }} coinů/h</p>
                                <p><small><em>{{ char.description }}</em></small></p>
                            </div>
                        {% endfor %}
                    </div>
                {% endif %}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    user = session.get('user')
    inventory = session.get('inventory', [])
    hourly_income = calculate_hourly_income(inventory)
    
    return render_template_string(
        HTML_TEMPLATE,
        user=user,
        inventory=inventory,
        characters_db=CHARACTERS,
        hourly_income=hourly_income
    )

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # Jednoduché přihlášení (přizpůsobené pro Supabase nebo testování)
    session['user'] = {'email': email}
    if 'inventory' not in session:
        session['inventory'] = []
    
    flash(f"Vítej ve hře, {email}!")
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    flash("Byl jsi úspěšně odhlášen.")
    return redirect(url_for('home'))

@app.route('/open-pack/<pack_key>', methods=['POST'])
def open_pack(pack_key):
    if 'user' not in session:
        flash("Pro otevírání packů se musíš přihlásit.")
        return redirect(url_for('home'))
        
    char_key = draw_character_from_pack(pack_key)
    if char_key:
        inventory = session.get('inventory', [])
        inventory.append(char_key)
        session['inventory'] = inventory
        
        char_info = CHARACTERS[char_key]
        flash(f"🎉 Získal jsi postavů: {char_info['name']} ({char_info['rarity']})!")
    else:
        flash("Neznámý pack.")
        
    return redirect(url_for('home'))

@app.route('/reset', methods=['POST'])
def reset_progress():
    if 'user' in session:
        session['inventory'] = []
        flash("Tvůj pokrok byl resetován (batoh je prázdný).")
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
