import codecs

html_top = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Contas Mensais</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-dark: #0f172a; --glass-bg: rgba(30, 41, 59, 0.6); --glass-border: rgba(255, 255, 255, 0.1);
            --primary: #3b82f6; --primary-hover: #2563eb; --success: #10b981; --danger: #ef4444;
            --text-main: #f8fafc; --text-muted: #94a3b8; --blob-1: #3b82f6; --blob-2: #8b5cf6; --blob-3: #10b981;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'Outfit', sans-serif; }
        body { background-color: var(--bg-dark); color: var(--text-main); min-height: 100vh; overflow-x: hidden; position: relative; }
        .background-animation { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; overflow: hidden; filter: blur(80px); }
        .blob { position: absolute; border-radius: 50%; animation: drift 20s infinite alternate; }
        .blob1 { width: 500px; height: 500px; background: var(--blob-1); top: -200px; left: -100px; opacity: 0.2; }
        .blob2 { width: 400px; height: 400px; background: var(--blob-2); bottom: -100px; right: 10%; opacity: 0.2; animation-delay: -5s; }
        .blob3 { width: 300px; height: 300px; background: var(--blob-3); top: 30%; left: 50%; opacity: 0.15; animation-delay: -10s; }
        @keyframes drift { 0% { transform: translate(0, 0) scale(1); } 100% { transform: translate(50px, -50px) scale(1.1); } }
        .app-container { display: flex; max-width: 1400px; margin: 2rem auto; min-height: calc(100vh - 4rem); border-radius: 20px; background: var(--glass-bg); backdrop-filter: blur(16px); border: 1px solid var(--glass-border); box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); overflow: hidden; }
        .sidebar { width: 280px; background: rgba(15, 23, 42, 0.4); border-right: 1px solid var(--glass-border); padding: 2rem 1.5rem; display: flex; flex-direction: column; gap: 2rem; }
        .brand { display: flex; align-items: center; gap: 12px; } .brand i { font-size: 24px; color: var(--primary); } .brand h1 { font-size: 1.5rem; font-weight: 600; }
        .months-selector h3 { font-size: 0.9rem; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1px; margin-bottom: 1rem; }
        #month-list { list-style: none; display: flex; flex-direction: column; gap: 8px; max-height: 50vh; overflow-y: auto; }
        #month-list li { padding: 12px 16px; border-radius: 10px; cursor: pointer; transition: all 0.2s ease; color: var(--text-muted); display: flex; justify-content: space-between; align-items: center; }
        #month-list li:hover { background: rgba(255, 255, 255, 0.05); color: var(--text-main); }
        #month-list li.active { background: var(--primary); color: white; box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4); }
        .main-content { flex: 1; padding: 2.5rem; display: flex; flex-direction: column; gap: 2rem; overflow-y: auto; }
        .main-header { display: flex; justify-content: space-between; align-items: center; }
        .main-header h2 { font-size: 2rem; font-weight: 700; } .subtitle { color: var(--text-muted); margin-top: 5px; }
        .dashboard-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.5rem; }
        .glass-card { background: rgba(255, 255, 255, 0.03); border: 1px solid var(--glass-border); border-radius: 16px; padding: 1.5rem; }
        .dashboard-cards .card { display: flex; align-items: center; gap: 1.5rem; transition: transform 0.2s ease; } .dashboard-cards .card:hover { transform: translateY(-5px); }
        .card-icon { width: 50px; height: 50px; border-radius: 12px; background: rgba(59, 130, 246, 0.1); color: var(--primary); display: flex; align-items: center; justify-content: center; font-size: 1.5rem; }
        .card-info h3 { font-size: 0.9rem; color: var(--text-muted); font-weight: 500; } .card-value { font-size: 1.8rem; font-weight: 700; margin-top: 5px; }
        .card-value.positive { color: var(--danger); } .card-value.negative { color: var(--success); }
        .accounts-list { flex: 1; display: flex; flex-direction: column; } .accounts-header { margin-bottom: 1.5rem; } .table-container { overflow-x: auto; }
        table { width: 100%; border-collapse: collapse; } th { text-align: left; padding: 1rem; color: var(--text-muted); font-weight: 500; border-bottom: 1px solid var(--glass-border); }
        td { padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.05); vertical-align: middle; } tbody tr { transition: background 0.2s; } tbody tr:hover { background: rgba(255, 255, 255, 0.02); }
        tfoot td { border-top: 2px solid var(--glass-border); border-bottom: none; font-size: 1.2rem; padding-top: 1.5rem; } .text-right { text-align: right; }
        td.actions { text-align: right; display: flex; justify-content: flex-end; gap: 10px; }
        .status-badge { padding: 6px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 600; display: inline-flex; align-items: center; gap: 6px; }
        .status-ok { background: rgba(16, 185, 129, 0.1); color: var(--success); border: 1px solid rgba(16, 185, 129, 0.2); }
        .status-pendente { background: rgba(245, 158, 11, 0.1); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.2); }
        .action-btn { padding: 10px 16px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.2s; border: none; display: inline-flex; align-items: center; gap: 8px; justify-content: center; }
        .primary-btn { background: var(--primary); color: white; box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3); } .primary-btn:hover { background: var(--primary-hover); transform: translateY(-2px); }
        .outline-btn { background: transparent; border: 1px solid var(--primary); color: var(--primary); } .outline-btn:hover { background: rgba(59, 130, 246, 0.1); }
        .text-btn { background: transparent; color: var(--text-muted); } .text-btn:hover { color: var(--text-main); }
        .icon-btn { background: rgba(255,255,255,0.05); border: none; color: var(--text-main); width: 32px; height: 32px; border-radius: 6px; cursor: pointer; transition: 0.2s; }
        .icon-btn:hover { background: rgba(255,255,255,0.1); } .icon-btn.delete:hover { background: rgba(239, 68, 68, 0.2); color: var(--danger); }
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.6); backdrop-filter: blur(5px); display: flex; align-items: center; justify-content: center; z-index: 100; opacity: 1; transition: opacity 0.3s ease; }
        .modal-overlay.hidden { opacity: 0; pointer-events: none; }
        .modal { width: 90%; max-width: 450px; background: var(--bg-dark); padding: 0; border-radius: 16px; overflow: hidden; transform: translateY(0); transition: transform 0.3s ease; }
        .modal-overlay.hidden .modal { transform: translateY(20px); }
        .modal-header { padding: 1.5rem; border-bottom: 1px solid var(--glass-border); display: flex; justify-content: space-between; align-items: center; }
        .close-modal { background: transparent; border: none; color: var(--text-muted); font-size: 1.2rem; cursor: pointer; }
        .modal-body { padding: 1.5rem; display: flex; flex-direction: column; gap: 15px; } .modal-body label { font-size: 0.9rem; color: var(--text-muted); }
        .input-field { width: 100%; padding: 12px 15px; border-radius: 8px; background: rgba(0,0,0,0.2); border: 1px solid var(--glass-border); color: var(--text-main); font-size: 1rem; outline: none; transition: border-color 0.2s; }
        .input-field:focus { border-color: var(--primary); }
        .checkbox-container { display: flex; align-items: center; gap: 8px; cursor: pointer; }
        .modal-footer { padding: 1.5rem; border-top: 1px solid var(--glass-border); display: flex; justify-content: flex-end; }
        ::-webkit-scrollbar { width: 8px; } ::-webkit-scrollbar-track { background: rgba(0, 0, 0, 0.1); } ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 4px; } ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.3); }
    </style>
</head>
<body>
    <div class="background-animation"><div class="blob blob1"></div><div class="blob blob2"></div><div class="blob blob3"></div></div>
    <div class="app-container glass-effect">
        <aside class="sidebar">
            <div class="brand"><i class="fa-solid fa-wallet"></i><h1>Gestão de Contas</h1></div>
            <div class="months-selector">
                <h3>Selecione o Mês</h3>
                <ul id="month-list"></ul>
            </div>
            <button id="add-month-btn" class="action-btn outline-btn"><i class="fa-solid fa-plus"></i> Novo Mês</button>
            <button id="export-data-btn" class="action-btn text-btn"><i class="fa-solid fa-download"></i> Exportar JSON</button>
        </aside>
        <main class="main-content">
            <header class="main-header">
                <div>
                    <h2 id="current-month-display">Mês Atual</h2>
                    <p class="subtitle">Bem-vindo(a) ao seu dashboard inteligente.</p>
                </div>
                <div class="header-actions">
                    <button class="action-btn primary-btn" id="new-account-btn"><i class="fa-solid fa-plus"></i> Adicionar Conta</button>
                </div>
            </header>
            <section class="dashboard-cards">
                <div class="card glass-card">
                    <div class="card-icon"><i class="fa-solid fa-money-bill-trend-up"></i></div>
                    <div class="card-info"><h3>Total Gasto</h3><p id="total-gasto" class="card-value">R$ 0,00</p></div>
                </div>
                <div class="card glass-card">
                    <div class="card-icon"><i class="fa-solid fa-scale-unbalanced"></i></div>
                    <div class="card-info"><h3>Variação (Mês Ant.)</h3><p id="variacao-mes" class="card-value neutral">R$ 0,00</p></div>
                </div>
                <div class="card glass-card">
                    <div class="card-icon"><i class="fa-solid fa-file-invoice-dollar"></i></div>
                    <div class="card-info"><h3>Contas Pagas</h3><p id="contas-pagas" class="card-value">0/0</p></div>
                </div>
            </section>
            <section class="accounts-list glass-card">
                <div class="accounts-header"><h3>Lançamentos do Mês</h3></div>
                <div class="table-container">
                    <table id="accounts-table">
                        <thead><tr><th>Conta / Descrição</th><th>Valor (R$)</th><th>Status</th><th class="text-right">Ações</th></tr></thead>
                        <tbody id="accounts-tbody"></tbody>
                        <tfoot id="accounts-tfoot"><tr><td><strong>Total</strong></td><td colspan="3" id="total-table-value"><strong>R$ 0,00</strong></td></tr></tfoot>
                    </table>
                </div>
            </section>
        </main>
    </div>

    <!-- Modals -->
    <div id="modal-month" class="modal-overlay hidden">
        <div class="modal glass-card">
            <div class="modal-header">
                <h3>Adicionar Novo Mês</h3>
                <button class="close-modal" id="close-modal-month"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="modal-body">
                <label>Identificador (Ex: 2025-05):</label>
                <input type="text" id="new-month-input" placeholder="AAAA-MM" class="input-field">
            </div>
            <div class="modal-footer"><button class="action-btn primary-btn" id="save-month-btn">Salvar</button></div>
        </div>
    </div>
    <div id="modal-account" class="modal-overlay hidden">
        <div class="modal glass-card">
            <div class="modal-header">
                <h3>Adicionar / Editar Conta</h3>
                <button class="close-modal" id="close-modal-account"><i class="fa-solid fa-xmark"></i></button>
            </div>
            <div class="modal-body">
                <label>Nome da Conta:</label><input type="text" id="acc-name" class="input-field">
                <label>Valor (R$):</label><input type="number" step="0.01" id="acc-value" class="input-field">
                <label class="checkbox-container"><input type="checkbox" id="acc-status"><span class="checkmark"></span> Marcar como paga (OK)</label>
            </div>
            <div class="modal-footer"><button class="action-btn primary-btn" id="save-account-btn">Salvar Conta</button></div>
        </div>
    </div>

    <script>
"""

with open(r'c:\Users\Usuario\Desktop\contas mensais\real_data.json', 'r', encoding='utf-8') as f:
    real_data = f.read()

js_script = f"""
        const DATA_KEY = "gestao_contas_data_v2";
        const baseData = {real_data};
        
        let appData = baseData; // Sempre começamos garantindo os dados do arquivo
        
        // Tentamos mesclar com localStorage de forma defensiva
        try {{
            const savedStr = localStorage.getItem(DATA_KEY);
            if (savedStr) {{
                const savedObj = JSON.parse(savedStr);
                if (savedObj && Object.keys(savedObj).length > 0) {{
                    appData = savedObj;
                }}
            }}
        }} catch(e) {{
            console.warn("Navegador impediu localStorage, operando em memória.");
        }}

        let currentMonth = null;
        let editingAccountId = null;

        // O HTML já foi inteiramente lido quando chegamos aqui no final do body
        initMonths();
        setupEventListeners();

        function setupEventListeners() {{
            document.getElementById("add-month-btn").onclick = () => showModal("modal-month");
            document.getElementById("close-modal-month").onclick = () => closeModal("modal-month");
            document.getElementById("save-month-btn").onclick = addMonth;

            document.getElementById("new-account-btn").onclick = () => {{
                if (!currentMonth) return alert("Selecione um mês.");
                editingAccountId = null;
                document.getElementById("acc-name").value = "";
                document.getElementById("acc-value").value = "";
                document.getElementById("acc-status").checked = false;
                showModal("modal-account");
            }};
            document.getElementById("close-modal-account").onclick = () => closeModal("modal-account");
            document.getElementById("save-account-btn").onclick = saveAccount;

            document.getElementById("export-data-btn").onclick = () => {{
                const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(appData));
                const a = document.createElement('a'); a.href = dataStr; a.download = "backup_contas.json"; a.click();
            }};
        }}

        function saveData() {{
            try {{ localStorage.setItem(DATA_KEY, JSON.stringify(appData)); }} catch(e) {{ console.warn("Memória local restrita."); }}
        }}

        function initMonths() {{
            const list = document.getElementById("month-list");
            list.innerHTML = "";
            const months = Object.keys(appData).sort().reverse();
            if (months.length === 0) {{
                list.innerHTML = "<li class='text-muted'>Sem dados</li>";
                renderMain(null); return;
            }}
            if (!currentMonth || !months.includes(currentMonth)) currentMonth = months[0];
            months.forEach(month => {{
                const li = document.createElement("li");
                li.textContent = formatMonthString(month);
                if (month === currentMonth) li.className = "active";
                li.onclick = () => {{ currentMonth = month; initMonths(); }};
                list.appendChild(li);
            }});
            renderMain(currentMonth);
        }}

        function addMonth() {{
            const newMonth = document.getElementById("new-month-input").value.trim();
            if (!/^\d{{4}}-\d{{2}}$/.test(newMonth)) return alert("Use formato AAAA-MM (Ex: 2025-11)");
            if (appData[newMonth]) return alert("Mês já existe!");
            appData[newMonth] = [];
            const prev = Object.keys(appData).sort().reverse();
            if(prev.length > 1 && confirm("Importar contas do último mês?")) {{
                appData[newMonth] = appData[prev[1]].map(acc => ({{ id: Date.now() + Math.random(), name: acc.name, value: acc.value, ok: false }}));
            }}
            saveData(); currentMonth = newMonth; closeModal("modal-month"); document.getElementById("new-month-input").value = ""; initMonths();
        }}

        function renderMain(monthKey) {{
            if (!monthKey) return;
            document.getElementById("current-month-display").textContent = formatMonthString(monthKey);
            const accounts = appData[monthKey] || [];
            let totalGasto = 0; let pagas = 0;
            accounts.forEach(acc => {{ totalGasto += acc.value; if(acc.ok) pagas++; }});
            document.getElementById("total-gasto").textContent = formatCurrency(totalGasto);
            document.getElementById("total-table-value").innerHTML = `<strong>${{formatCurrency(totalGasto)}}</strong>`;
            document.getElementById("contas-pagas").textContent = `${{pagas}}/${{accounts.length}}`;
            calcularVariacao(monthKey, totalGasto);
            
            const tbody = document.getElementById("accounts-tbody");
            tbody.innerHTML = "";
            if (accounts.length === 0) tbody.innerHTML = "<tr><td colspan='4' class='text-center'>Nenhuma conta</td></tr>";
            accounts.forEach(acc => {{
                const tr = document.createElement("tr");
                tr.innerHTML = `
                    <td><strong>${{acc.name}}</strong></td>
                    <td>${{formatCurrency(acc.value)}}</td>
                    <td><span class="status-badge ${{acc.ok ? 'status-ok' : 'status-pendente'}}"><i class="fa-solid ${{acc.ok ? 'fa-check-circle' : 'fa-clock'}}"></i> ${{acc.ok ? 'OK' : 'Pendente'}}</span></td>
                    <td class="actions">
                        <button class="icon-btn" onclick="toggleStatus(${{acc.id}})"><i class="fa-solid fa-check"></i></button>
                        <button class="icon-btn" onclick="editAccount(${{acc.id}})"><i class="fa-solid fa-pen"></i></button>
                        <button class="icon-btn delete" onclick="deleteAccount(${{acc.id}})"><i class="fa-solid fa-trash"></i></button>
                    </td>
                `;
                tbody.appendChild(tr);
            }});
        }}

        function calcularVariacao(currentKey, currentTotal) {{
            const keys = Object.keys(appData).sort();
            const idx = keys.indexOf(currentKey);
            const varDisp = document.getElementById("variacao-mes");
            if (idx > 0) {{
                const prevKey = keys[idx - 1];
                const prevTotal = appData[prevKey].reduce((sum, item) => sum + item.value, 0);
                const diff = currentTotal - prevTotal;
                varDisp.textContent = `${{diff >= 0 ? '+' : ''}}${{formatCurrency(diff)}}`;
                varDisp.className = "card-value " + (diff > 0 ? "positive" : (diff < 0 ? "negative" : "neutral"));
            }} else {{
                varDisp.textContent = "-"; varDisp.className = "card-value neutral";
            }}
        }}

        function saveAccount() {{
            const name = document.getElementById("acc-name").value.trim().toUpperCase();
            const val = parseFloat(document.getElementById("acc-value").value);
            const ok = document.getElementById("acc-status").checked;
            if (!name || isNaN(val)) return alert("Preencha os campos corretamente.");
            if (editingAccountId) {{
                const ac = appData[currentMonth].find(a => a.id === editingAccountId);
                if (ac) {{ ac.name = name; ac.value = val; ac.ok = ok; }}
            }} else {{
                appData[currentMonth].push({{ id: Date.now(), name, value: val, ok }});
            }}
            saveData(); closeModal("modal-account"); renderMain(currentMonth);
        }}

        function editAccount(id) {{
            const account = appData[currentMonth].find(a => a.id === id);
            if (!account) return;
            editingAccountId = id;
            document.getElementById("acc-name").value = account.name;
            document.getElementById("acc-value").value = account.value;
            document.getElementById("acc-status").checked = account.ok;
            showModal("modal-account");
        }}

        function deleteAccount(id) {{
            if(confirm("Excluir conta?")) {{
                appData[currentMonth] = appData[currentMonth].filter(a => a.id !== id);
                saveData(); renderMain(currentMonth);
            }}
        }}

        function toggleStatus(id) {{
            const account = appData[currentMonth].find(a => a.id === id);
            if (account) {{ account.ok = !account.ok; saveData(); renderMain(currentMonth); }}
        }}

        function showModal(id) {{ document.getElementById(id).classList.remove("hidden"); }}
        function closeModal(id) {{ document.getElementById(id).classList.add("hidden"); }}
        function formatMonthString(yyyyMm) {{
            const [y, m] = yyyMm.split("-");
            return new Date(y, parseInt(m)-1, 1).toLocaleDateString("pt-BR", {{month: 'long', year: 'numeric'}}).toUpperCase();
        }}
        function formatCurrency(val) {{ return val.toLocaleString("pt-BR", {{style: "currency", currency: "BRL"}}); }}
    </script>
</body>
</html>
"""

with codecs.open(r'c:\Users\Usuario\Desktop\contas mensais\index.html', 'w', 'utf-8') as f:
    f.write(html_top + js_script)

print("Build Complete.")
