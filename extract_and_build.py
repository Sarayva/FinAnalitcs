import pandas as pd
import json
import codecs
import math
import os

xls_path = r'c:\Users\Usuario\Desktop\contas mensais\Contas Mensais.xlsx'
xls = pd.ExcelFile(xls_path)
app_data = {}
app_rendas = {}

for sheet_name in ['2025', '2026']:
    if sheet_name not in xls.sheet_names:
        continue
    df = pd.read_excel(xls, sheet_name=sheet_name)
    conta_col = df.columns[0]
    
    for idx_col in range(len(df.columns) - 1):
        col_name = df.columns[idx_col]
        next_col_name = str(df.columns[idx_col + 1]).upper()
        
        if next_col_name.startswith('STATUS'):
            month_str = ""
            if hasattr(col_name, 'strftime'):
                month_str = col_name.strftime('%Y-%m')
            else:
                s_name = str(col_name).strip().lower()
                if 'jan' in s_name: month_str = f"{sheet_name}-01"
                elif 'fev' in s_name: month_str = f"{sheet_name}-02"
                elif 'mar' in s_name: month_str = f"{sheet_name}-03"
                elif 'abr' in s_name: month_str = f"{sheet_name}-04"
                elif 'mai' in s_name: month_str = f"{sheet_name}-05"
                elif 'jun' in s_name: month_str = f"{sheet_name}-06"
                elif 'jul' in s_name: month_str = f"{sheet_name}-07"
                elif 'ago' in s_name: month_str = f"{sheet_name}-08"
                elif 'set' in s_name: month_str = f"{sheet_name}-09"
                elif 'out' in s_name: month_str = f"{sheet_name}-10"
                elif 'nov' in s_name: month_str = f"{sheet_name}-11"
                elif 'dez' in s_name: month_str = f"{sheet_name}-12"
                else: 
                    continue 
            
            if month_str not in app_data:
                app_data[month_str] = []
                app_rendas[month_str] = {'meu': 0, 'dela': 0}
                
            status_col = df.columns[idx_col + 1]
            for idx, row in df.iterrows():
                conta = str(row[conta_col]).strip().upper()
                c_low = conta.lower()
                    
                valor = row[col_name]
                if type(valor) is str:
                    try:
                        valor = float(valor.replace(',', '.').strip())
                    except:
                        valor = 0.0
                if pd.isna(valor) or type(valor) not in [int, float]:
                    valor = 0.0
                    
                if c_low == 'meu':
                    app_rendas[month_str]['meu'] = round(float(valor), 2)
                    continue
                elif c_low == 'dela':
                    app_rendas[month_str]['dela'] = round(float(valor), 2)
                    continue
                elif pd.isna(row[conta_col]) or c_low == 'nan' or 'total' in c_low or c_low in ['nosso', 'sobra']: 
                    continue
                    
                status = str(row[status_col]).strip().lower()
                is_ok = (status == 'ok' or status == 'pago')
                    
                account_id = int(float(f"{idx}{idx_col}{int(sheet_name)}"))
                account = {
                    "id": account_id,
                    "name": conta,
                    "value": round(float(valor), 2),
                    "ok": is_ok,
                    "isBoleto": False,
                    "dueDay": None
                }
                app_data[month_str].append(account)

app_data = {k: v for k, v in app_data.items() if len(v) > 0}
json_data = json.dumps(app_data, indent=2, ensure_ascii=False)
json_rendas_data = json.dumps(app_rendas, indent=2, ensure_ascii=False)

html_top = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Contas Mensais</title>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <script src="https://cdn.jsdelivr.net/npm/apexcharts"></script>
    <style>
        :root {
            --bg-dark: #121212; --glass-bg: rgba(30, 30, 30, 0.7); --glass-border: rgba(255, 255, 255, 0.08);
            --primary: #ffffff; --primary-hover: #d1d1d1; --success: #4caf50; --danger: #f44336; --warning: #ff9800;
            --text-main: #ffffff; --text-muted: #8a8a8a;
            --card-bg: rgba(30, 30, 30, 0.95);
            --sidebar-bg: rgba(20, 20, 20, 0.95);
            --input-bg: rgba(255, 255, 255, 0.05);
            --modal-bg: #1e293b;
            --row-hover: rgba(255, 255, 255, 0.02);
            --chart-title: #f1f5f9;
        }
        body.light-theme {
            --bg-dark: #f1f5f9; --glass-bg: rgba(255, 255, 255, 0.9); --glass-border: rgba(0, 0, 0, 0.1);
            --primary: #1e293b; --primary-hover: #0f172a; --success: #4caf50; --danger: #f44336; --warning: #ff9800;
            --text-main: #1e293b; --text-muted: #64748b;
            --card-bg: #ffffff;
            --sidebar-bg: #ffffff;
            --input-bg: rgba(0, 0, 0, 0.03);
            --modal-bg: #ffffff;
            --row-hover: rgba(0, 0, 0, 0.04);
            --chart-title: #334155;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; font-family: 'JetBrains Mono', 'Consolas', monospace; }
        body { background-color: var(--bg-dark); color: var(--text-main); height: 100vh; overflow: hidden; position: relative; }
        .background-animation { display: none; }
        .app-container { display: flex; width: 100vw; height: 100vh; background: transparent; overflow: hidden; }
        
        .sidebar { width: 250px; background: var(--sidebar-bg); border-right: 1px solid var(--glass-border); display: flex; flex-direction: column; }
        .brand { display: flex; align-items: center; gap: 12px; padding: 2rem 1.5rem 1rem; }
        .brand i { font-size: 24px; color: var(--primary); } .brand h1 { font-size: 1.2rem; font-weight: 600; line-height:1.1; }
        .nav-tabs { display: flex; flex-direction: column; gap: 5px; padding: 1rem; border-bottom: 1px solid var(--glass-border); }
        .nav-tab { background: transparent; border: none; color: var(--text-muted); font-size: 1rem; font-weight: 500; text-align: left; padding: 12px 15px; border-radius: 8px; cursor: pointer; transition: 0.2s; display: flex; align-items: center; gap: 10px; }
        .nav-tab:hover { background: rgba(255, 255, 255, 0.05); color: var(--text-main); }
        .nav-tab.active { background: rgba(255, 255, 255, 0.06); color: var(--text-main); border-left: 3px solid var(--primary); }
        
        .months-selector { padding: 1.5rem; flex: 1; display: flex; flex-direction: column; overflow: hidden; }
        .months-selector h3 { font-size: 0.8rem; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1px; margin-bottom: 1rem; }
        
        .styled-select { background: var(--input-bg); border: 1px solid var(--glass-border); color: var(--text-main); padding: 12px 14px; border-radius: 8px; font-size: 0.95rem; outline: none; cursor: pointer; transition: 0.2s; width: 100%; font-family: 'JetBrains Mono', 'Consolas', monospace; }
        .styled-select:hover, .styled-select:focus { background: rgba(255, 255, 255, 0.1); border-color: rgba(255, 255, 255, 0.2); }
        .styled-select option { background: var(--bg-dark); color: var(--text-main); font-family: 'Inter', sans-serif; font-size: 14px; }
        
        .sidebar-actions { padding: 1.5rem; display: flex; flex-direction: column; gap: 10px; border-top: 1px solid var(--glass-border); }

        .views-container { flex: 1; position: relative; overflow: hidden; background: transparent; }
        .view { position: absolute; top:0; left:0; width:100%; height:100%; padding: 2rem; overflow-y: auto; display: none; }
        .view.active-view { display: flex; flex-direction: column; gap: 1.5rem; }
        
        .main-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem; }
        .main-header h2 { font-size: 1.8rem; font-weight: 700; color: var(--text-main); } .subtitle { color: var(--text-muted); font-size: 0.9rem; margin-top: 2px; }
        .header-actions { display: flex; gap: 10px; }

        /* Dashboard Grid Layout (Mirrors the provided screenshot) */
        .dash-grid { display: grid; grid-template-columns: repeat(4, 1fr); grid-auto-rows: minmax(130px, auto); gap: 1rem; }
        .glass-card { background: var(--card-bg); border: 1px solid var(--glass-border); border-radius: 12px; }
        
        .dash-metric { padding: 1.5rem; display: flex; flex-direction: column; justify-content: center; }
        .dash-metric h3 { font-size: 0.9rem; color: var(--text-muted); font-weight: 500; margin-bottom: 8px; }
        .dash-metric h2 { font-size: 1.8rem; font-weight: 700; }
        .saldo-color { color: #60a5fa; } .despesa-color { color: #f87171; }
        
        .chart-wrapper { padding: 1rem; display: flex; flex-direction: column; position: relative; }
        .chart-wrapper h3 { font-size: 0.95rem; font-weight: 500; margin-bottom: 0px; margin-left: 10px; margin-top: 10px; color: var(--chart-title); }
        
        .col-span-1 { grid-column: span 1; } .col-span-2 { grid-column: span 2; }
        .row-span-1 { grid-row: span 1; } .row-span-2 { grid-row: span 2; }

        /* Lancamentos View (Current Tables) */
        .dashboard-cards-linear { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom:1rem; }
        .linear-card { display: flex; align-items: center; gap: 1rem; padding: 1.2rem; }
        .linear-card i { font-size: 1.4rem; padding: 12px; border-radius: 10px; background: var(--input-bg); }
        .linear-val h3 { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 4px; }
        .linear-val p { font-size: 1.4rem; font-weight: 700; }
        
        table { width: 100%; border-collapse: collapse; } th { text-align: left; padding: 1rem; color: var(--text-muted); font-size: 0.85rem; text-transform: uppercase; border-bottom: 1px solid var(--glass-border); }
        td { padding: 1rem; border-bottom: 1px solid rgba(255,255,255,0.02); vertical-align: middle; font-size: 0.95rem; } 
        tbody tr:hover { background: var(--row-hover); }
        tfoot td { border-top: 2px solid var(--glass-border); border-bottom: none; font-size: 1.1rem; padding-top: 1.2rem; }
        
        .status-badge { padding: 4px 10px; border-radius: 6px; font-size: 0.75rem; font-weight: 600; display: inline-flex; align-items: center; gap: 5px; }
        .status-ok { background: rgba(16, 185, 129, 0.1); color: var(--success); }
        .status-pendente { background: rgba(245, 158, 11, 0.1); color: var(--warning); }
        
        .action-btn { padding: 10px 16px; border-radius: 8px; font-weight: 500; font-size:0.9rem; cursor: pointer; transition: all 0.2s; border: none; display: inline-flex; align-items: center; gap: 8px; justify-content: center; }
        .primary-btn { background: var(--input-bg); color: var(--text-main); box-shadow: none; border: 1px solid var(--glass-border); } .primary-btn:hover { background: rgba(255, 255, 255, 0.15); transform: none; }
        .outline-btn { background: var(--input-bg); border: 1px solid var(--glass-border); color: var(--text-main); } .outline-btn:hover { background: var(--row-hover); }
        .icon-btn { background: transparent; border: none; color: var(--text-muted); width: 32px; height: 32px; border-radius: 6px; cursor: pointer; transition: 0.2s; }
        .icon-btn:hover { background: var(--input-bg); color: var(--text-main); } .icon-btn.delete:hover { color: var(--danger); }
        
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0,0,0,0.7); backdrop-filter: blur(5px); display: flex; align-items: center; justify-content: center; z-index: 100; opacity: 1; transition: 0.3s; }
        .modal-overlay.hidden { opacity: 0; pointer-events: none; }
        .modal { width: 90%; max-width: 420px; background: var(--modal-bg); padding: 0; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); transform: translateY(0); transition: 0.3s; }
        .modal-overlay.hidden .modal { transform: translateY(20px); }
        .modal-header { padding: 1.2rem; border-bottom: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: space-between; align-items: center; }
        .close-modal { background: transparent; border: none; color: var(--text-muted); cursor: pointer; font-size: 1.2rem; }
        .modal-body { padding: 1.2rem; display: flex; flex-direction: column; gap: 12px; } .modal-body label { font-size: 0.85rem; color: var(--text-muted); }
        .input-field { width: 100%; padding: 10px 12px; border-radius: 6px; background: var(--input-bg); border: 1px solid var(--glass-border); color: var(--text-main); font-size: 0.95rem; outline: none; }
        .input-field:focus { border-color: var(--primary); }
        .checkbox-container { display: flex; align-items: center; gap: 8px; cursor: pointer; margin-top: 5px; font-size: 0.9rem; }
        .modal-footer { padding: 1.2rem; border-top: 1px solid rgba(255,255,255,0.05); display: flex; justify-content: flex-end; }
        
        /* ApexCharts Dark Theme overrides */
        .apexcharts-tooltip, .apexcharts-tooltip-title { background: var(--modal-bg) !important; border: 1px solid var(--glass-border) !important; color: var(--text-main) !important; font-family: 'Inter', sans-serif !important; }
        .apexcharts-legend-text { color: var(--text-muted) !important; }
        
        .inline-val-input { background: transparent; border: 1px solid transparent; color: var(--text-main); font-size: 0.95rem; font-weight: 600; width: 100px; padding: 4px 8px; outline: none; border-radius: 4px; transition: 0.2s; text-align: right; }
        .inline-val-input:focus, .inline-val-input:hover { background: var(--input-bg); border-color: rgba(255,255,255,0.2); }
        .inline-val-container { display: flex; align-items: center; gap: 4px; justify-content: flex-start; }

        ::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: transparent; } ::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 10px; } ::-webkit-scrollbar-thumb:hover { background: rgba(255, 255, 255, 0.2); }
    </style>
</head>
<body>
    <div class="background-animation"><div class="blob blob1"></div><div class="blob blob2"></div></div>
    
    <div class="app-container">
        <!-- Sidebar -->
        <aside class="sidebar">
            <div class="brand" style="display:flex; justify-content: space-between;">
                <div style="display:flex; align-items:center; gap: 12px;">
                    <i class="fa-solid fa-chart-pie" style="font-size:28px;"></i>
                    <h1>Dashboard<br><span style="font-size:0.8rem; font-weight:400; color:var(--text-muted);">Finanças Pessoais</span></h1>
                </div>
                <button id="theme-toggle" class="icon-btn"><i class="fa-solid fa-sun"></i></button>
            </div>
            
            <div class="nav-tabs">
                <button class="nav-tab active" data-target="view-dashboard"><i class="fa-solid fa-chart-simple" style="width:20px;"></i> Dashboard</button>
                <button class="nav-tab" data-target="view-lancamentos"><i class="fa-solid fa-list-check" style="width:20px;"></i> Valores (Dados)</button>
            </div>
            
            <div class="months-selector">
                <h3>Histórico (Meses)</h3>
                <select id="month-select" class="styled-select"></select>
            </div>
            
            <div class="sidebar-actions">
                <button id="add-month-btn" class="action-btn outline-btn" style="width:100%;"><i class="fa-solid fa-calendar-plus"></i> Novo Mês</button>
                <button id="export-data-btn" class="action-btn outline-btn" style="width:100%;"><i class="fa-solid fa-download"></i> Salvar JSON</button>
            </div>
        </aside>

        <!-- Views Container -->
        <div class="views-container">
            
            <!-- Dashboard View -->
            <main id="view-dashboard" class="view active-view">
                <header class="main-header">
                    <div>
                        <h2>Visão Geral</h2>
                        <p class="subtitle" id="dash-subtitle">Visão estratégica do mês selecionado</p>
                    </div>
                </header>
                
                <div class="dash-grid">
                    <!-- Metric Cards -->
                    <div class="glass-card dash-metric col-span-1 row-span-1">
                        <h3>Saldo do mês (Livre)</h3>
                        <h2 class="saldo-color" id="dash-saldo">R$ 0,00</h2>
                    </div>
                    <div class="glass-card dash-metric col-span-1 row-span-1">
                        <h3>Despesas do mês</h3>
                        <h2 class="despesa-color" id="dash-despesa">R$ 0,00</h2>
                    </div>
                    
                    <!-- Donut Month Categ -->
                    <div class="glass-card chart-wrapper col-span-1 row-span-2">
                        <h3>Despesas no Mês</h2>
                        <div id="chart-donut-mes" style="margin-top:10px;"></div>
                    </div>
                    <!-- Donut Year Categ -->
                    <div class="glass-card chart-wrapper col-span-1 row-span-2">
                        <h3>Despesas no Ano</h2>
                        <div id="chart-donut-ano" style="margin-top:10px;"></div>
                    </div>

                    <div class="glass-card dash-metric" style="grid-column: span 2; grid-row: span 2;">
                        <h3 style="margin-bottom: 0;">Análise Mensal</h3>
                        <div id="chart-analise"></div>
                    </div>    
                    <!-- Horizontal Bar Top Expenses -->
                    <div class="glass-card chart-wrapper col-span-2 row-span-2">
                        <h3>Maiores Despesas (Mês)</h2>
                        <div id="chart-top-despesas" style="margin-top:10px;"></div>
                    </div>
                    
                    <div class="glass-card dash-metric" style="grid-column: span 2; grid-row: span 2;">
                        <h3 style="margin-bottom: 0;">Evolução de Patrimônio (Receita x Despesa)</h3>
                        <div id="chart-linha-ano"></div>
                    </div>
            </main>

            <!-- Lançamentos View -->
            <main id="view-lancamentos" class="view">
                <header class="main-header">
                    <div>
                        <h2 id="current-month-display">Mês Atual</h2>
                        <p class="subtitle">Gerenciamento de contas e recebíveis.</p>
                    </div>
                    <div class="header-actions">
                        <button class="action-btn outline-btn" id="edit-renda-btn"><i class="fa-solid fa-sack-dollar"></i> Rendimentos</button>
                        <button class="action-btn primary-btn" id="new-account-btn"><i class="fa-solid fa-plus"></i> Lançar Conta</button>
                    </div>
                </header>
                
                <section class="dashboard-cards-linear">
                    <div class="glass-card linear-card">
                        <i class="fa-solid fa-sack-dollar" style="color:#00cc6a;"></i>
                        <div class="linear-val"><h3>Renda Total</h3><p id="renda-total">R$ 0,00</p></div>
                    </div>
                    <div class="glass-card linear-card">
                        <i class="fa-solid fa-money-bill-trend-up" style="color:#e81123;"></i>
                        <div class="linear-val"><h3>Gasto Total</h3><p id="total-gasto">R$ 0,00</p></div>
                    </div>
                    <div class="glass-card linear-card">
                        <i class="fa-solid fa-piggy-bank" style="color:#0078d4;"></i>
                        <div class="linear-val"><h3>Sobra</h3><p id="sobra-mes">R$ 0,00</p></div>
                    </div>
                    <div class="glass-card linear-card">
                        <i class="fa-solid fa-check-double" style="color:#ffb900;"></i>
                        <div class="linear-val"><h3>Contas Pagas</h3><p id="contas-pagas">0/0</p></div>
                    </div>
                </section>
                
                <section class="glass-card" style="flex:1; padding: 1.5rem; display:flex; flex-direction:column; overflow:hidden;">
                    <div style="overflow-y:auto; flex:1;">
                        <table id="accounts-table">
                            <thead><tr><th>Conta / Descrição</th><th>Categoria</th><th>Valor</th><th>Status</th><th style="text-align:right;">Ações</th></tr></thead>
                            <tbody id="accounts-tbody"></tbody>
                            <tfoot id="accounts-tfoot"><tr><td colspan="2"><strong>Total</strong></td><td colspan="3" id="total-table-value"><strong>R$ 0,00</strong></td></tr></tfoot>
                        </table>
                    </div>
                </section>
            </main>
        </div>
    </div>

    <!-- Modals -->
    <div id="modal-month" class="modal-overlay hidden">
        <div class="modal">
            <div class="modal-header"><h3>Novo Mês</h3><button class="close-modal" id="close-modal-month"><i class="fa-solid fa-xmark"></i></button></div>
            <div class="modal-body">
                <label>Identificador (Ex: 2026-01):</label>
                <input type="text" id="new-month-input" placeholder="AAAA-MM" class="input-field">
            </div>
            <div class="modal-footer"><button class="action-btn primary-btn" id="save-month-btn">Criar</button></div>
        </div>
    </div>
    
    <div id="modal-rendas" class="modal-overlay hidden">
        <div class="modal">
            <div class="modal-header"><h3>Rendimentos</h3><button class="close-modal" id="close-modal-rendas"><i class="fa-solid fa-xmark"></i></button></div>
            <div class="modal-body">
                <label>Salário / Renda 1 (R$):</label><input type="number" step="0.01" id="renda-meu" class="input-field">
                <label>Salário / Renda 2 (R$):</label><input type="number" step="0.01" id="renda-dela" class="input-field">
            </div>
            <div class="modal-footer"><button class="action-btn primary-btn" id="save-rendas-btn">Salvar</button></div>
        </div>
    </div>
    
    <div id="modal-account" class="modal-overlay hidden">
        <div class="modal">
            <div class="modal-header"><h3 id="modal-acc-title">Conta</h3><button class="close-modal" id="close-modal-account"><i class="fa-solid fa-xmark"></i></button></div>
            <div class="modal-body">
                <div>
                    <label>Nome / Descrição:</label><input type="text" id="acc-name" class="input-field" placeholder="Ex: IPVA, C6 Bank...">
                </div>
                
                <div id="acc-val-container" style="display:flex; gap:10px; margin-top:5px;">
                    <div style="flex:1;">
                        <label>Valor (R$):</label><input type="number" step="0.01" id="acc-val" class="input-field" placeholder="0.00">
                    </div>
                </div>
                
                <div style="margin-top:5px;">
                    <label>Dia Venc. (Opcional):</label><input type="number" id="acc-due-day" class="input-field" placeholder="Ex: 5" min="1" max="31">
                </div>

                <div id="acc-parcelas-container" style="margin-top:10px;">
                    <label class="checkbox-container" style="user-select:none; margin-bottom:5px;">
                        <input type="checkbox" id="acc-is-boleto"> É Boleto?
                    </label>
                    <label class="checkbox-container" style="user-select:none; margin-bottom:5px;">
                        <input type="checkbox" id="acc-is-parcelado"> É uma compra parcelada?
                    </label>
                    <div id="parcelas-config" style="display:none; gap:10px; margin-top:10px;">
                        <div style="flex:1;"><label>Quantidade de Parcelas:</label><input type="number" id="acc-parc-total" class="input-field" value="2" min="2"></div>
                    </div>
                </div>
            </div>
            <div class="modal-footer"><button class="action-btn primary-btn" id="save-account-btn">Confirmar</button></div>
        </div>
    </div>

    <script>
        window.onerror = function(msg, url, line, col, error) {
            alert("JS Error: " + msg + " \\nLine: " + line + "\\nCol: " + col);
            return false;
        };
"""

js_script = f"""
        const DATA_KEY = "gestao_contas_data_v2";
        const RENDAS_KEY = "gestao_rendas_v2";
        
        if (localStorage.getItem("theme") === "light") {{
            document.body.classList.add("light-theme");
        }}

        let appData = {json_data}; 
        let appRendas = {json_rendas_data};
        let availableMonths = Object.keys(appData).sort().reverse();
        
        function loadData() {{
            try {{
                const savedStr = localStorage.getItem(DATA_KEY);
                if (savedStr) {{ const s = JSON.parse(savedStr); if (s && Object.keys(s).length) appData = s; }}
                const savedRnd = localStorage.getItem(RENDAS_KEY);
                if (savedRnd) appRendas = JSON.parse(savedRnd);
                availableMonths = Object.keys(appData).sort().reverse();
            }} catch(e) {{ console.warn("Erro ao ler localStorage."); }}
        }}

        let currentMonth = null;
        let editingAccountId = null;
        
        function showModal(id) {{
            const m = document.getElementById(id);
            if(m) m.classList.remove('hidden');
        }}
        function closeModal(id) {{
            const m = document.getElementById(id);
            if(m) m.classList.add('hidden');
        }}
        
        const formatCurrency = (val) => Number(val).toLocaleString("pt-BR", {{style: "currency", currency: "BRL"}});
        const formatMonthString = (yyyyMm) => {{
            const [y, m] = yyyyMm.split("-");
            return new Date(y, parseInt(m)-1, 1).toLocaleDateString("pt-BR", {{month: 'long', year: 'numeric'}}).toUpperCase();
        }};
        
        // Categorization AI logic
        function getCategory(name) {{
            const l = name.toLowerCase();
            if (l.includes("luz") || l.includes("agua") || l.includes("água") || l.includes("condominio") || l.includes("condomínio") || l.includes("iptu") || l.includes("gás") || l.includes("net") || l.includes("aluguel") || l.includes("financiamento") || l.includes("finaciamento")) return "Moradia";
            if (l.includes("vivo") || l.includes("claro") || l.includes("tim") || l.includes("celular")) return "Telecom";
            if (l.includes("facul") || l.includes("curso") || l.includes("escola") || l.includes("alura") || l.includes("inglês")) return "Educação";
            if (l.includes("terapia") || l.includes("saúde") || l.includes("saude") || l.includes("médico") || l.includes("unimed") || l.includes("farmacia") || l.includes("cartao de todos")) return "Saúde";
            if (l.includes("gasolina") || l.includes("carro") || l.includes("auto") || l.includes("estacionamento") || l.includes("uber") || l.includes("seguro")) return "Transporte";
            if (l.includes("spotify") || l.includes("apple") || l.includes("netflix") || l.includes("cinema") || l.includes("show") || l.includes("academia")) return "Lazer";
            if (l.includes("ifood") || l.includes("restaurante") || l.includes("mc") || l.includes("lanche") || l.includes("mercado")) return "Alimentação";
            if (l.includes("nu ") || l.includes("nubank") || l.includes("cartão") || l.includes("cartao") || l.includes("fatura")) return "Cartões";
            if (l.includes("havan") || l.includes("shopee") || l.includes("roupa") || l.includes("tenis") || l.includes("sapato") || l.includes("oculos")) return "Compras";
            return "Outros";
        }}
        
        const catColors = {{ "Moradia": "#0078D4", "Telecom": "#00CC6A", "Educação": "#8764B8", "Saúde": "#E81123", "Transporte": "#FF8C00", "Lazer": "#00B7C3", "Alimentação": "#FFB900", "Cartões": "#EA005E", "Compras": "#10893E", "Outros": "#a0a0a0" }};

        // Charts initialization
        let apexCharts = {{}};
        function initGlobalChart(id, options) {{
            try {{
                if (typeof ApexCharts === 'undefined') {{
                    document.getElementById(id).innerHTML = "<p style='color:#f87171; font-size:0.8rem; text-align:center;'>Gráfico requer internet para ser desenhado.</p>";
                    return;
                }}
                if (apexCharts[id]) apexCharts[id].destroy();
                apexCharts[id] = new ApexCharts(document.querySelector(`#${{id}}`), options);
                apexCharts[id].render();
            }} catch(e) {{
                console.error("Erro ao desenhar gráfico", e);
            }}
        }}
        

        function renderDashboard(monthKey) {{
            if(!monthKey) return;
            
            const commonOptions = {{
                chart: {{ background: 'transparent', toolbar: {{ show: false }}, fontFamily: "'JetBrains Mono', Consolas, monospace" }},
                theme: {{ mode: document.body.classList.contains('light-theme') ? 'light' : 'dark' }},
                dataLabels: {{ enabled: false }},
                stroke: {{ curve: 'smooth' }},
                tooltip: {{ y: {{ formatter: (val) => formatCurrency(val) }} }}
            }};

            const yearStr = monthKey.split("-")[0];
            document.getElementById("dash-subtitle").textContent = "Visão estratégica de " + formatMonthString(monthKey);
            
            // Current Month Maths
            const accs = appData[monthKey] || [];
            const r = appRendas[monthKey] || {{meu: 0, dela: 0}};
            let curDespesa = 0; accs.forEach(a => curDespesa += a.value);
            let curRenda = r.meu + r.dela;
            let curSaldo = curRenda - curDespesa;
            
            document.getElementById("dash-saldo").textContent = formatCurrency(curSaldo);
            document.getElementById("dash-despesa").textContent = formatCurrency(curDespesa);

            // Month Categorization (Donut)
            let catMonthSum = {{}};
            accs.forEach(a => {{ const c = getCategory(a.name); catMonthSum[c] = (catMonthSum[c]||0) + a.value; }});
            const mCats = Object.keys(catMonthSum).sort((a,b) => catMonthSum[b] - catMonthSum[a]);
            const mData = mCats.map(c => catMonthSum[c]);
            const mColors = mCats.map(c => catColors[c] || catColors["Outros"]);
            
            initGlobalChart("chart-donut-mes", {{ ...commonOptions, series: mData, labels: mCats, colors: mColors, chart: {{ type: 'donut', height: 260 }}, plotOptions: {{ pie: {{ donut: {{ size: '70%', labels: {{ show:true, name: {{show:true}}, value: {{show:true, formatter: (val) => formatCurrency(val) }} }} }} }} }} }});

            // Year Aggregation
            let curYearObj = {{}};
            Object.keys(appData).forEach(k => {{
                if(k.startsWith(yearStr)) curYearObj[k] = appData[k];
            }});
            const allYearMonths = Object.keys(curYearObj).sort(); // chronological
            
            let catYearSum = {{}};
            let histRendas = []; let histDespesas = []; let monthLabels = [];
            
            allYearMonths.forEach(m => {{
                monthLabels.push(m.split("-")[1] + "/" + yearStr);
                let desp = 0;
                curYearObj[m].forEach(a => {{
                    desp += a.value;
                    const c = getCategory(a.name);
                    catYearSum[c] = (catYearSum[c]||0) + a.value;
                }});
                let rend = (appRendas[m]?.meu || 0) + (appRendas[m]?.dela || 0);
                histDespesas.push(desp);
                histRendas.push(rend);
            }});
            
            // Year Categorization (Donut)
            const yCats = Object.keys(catYearSum).sort((a,b) => catYearSum[b] - catYearSum[a]);
            const yData = yCats.map(c => catYearSum[c]);
            const yColors = yCats.map(c => catColors[c] || catColors["Outros"]);
            initGlobalChart("chart-donut-ano", {{ ...commonOptions, series: yData, labels: yCats, colors: yColors, chart: {{ type: 'donut', height: 260 }}, plotOptions: {{ pie: {{ donut: {{ size: '70%', labels: {{ show:true, name: {{show:true}}, value: {{show:true, formatter: (val) => formatCurrency(val) }} }} }} }} }} }});
            
            // Year Bar Chart (Analise)
            initGlobalChart("chart-analise", {{ ...commonOptions, series: [ {{name: 'Receita', data: histRendas}}, {{name: 'Despesa', data: histDespesas}} ], chart: {{ type: 'bar', height: 280, toolbar: {{show:false}} }}, xaxis: {{ categories: monthLabels }}, colors: ['#0078D4', '#E81123'], plotOptions: {{ bar: {{ borderRadius: 4, columnWidth: '50%' }} }} }});
            
            // Year Line Chart
            initGlobalChart("chart-linha-ano", {{ ...commonOptions, series: [ {{name: 'Receitas', data: histRendas}}, {{name: 'Despesas', data: histDespesas}} ], chart: {{ type: 'area', height: 280, toolbar:{{show:false}} }}, xaxis: {{ categories: monthLabels }}, colors: ['#0078D4', '#E81123'], fill: {{ type: 'gradient', gradient: {{ shadeIntensity: 1, opacityFrom: 0.4, opacityTo: 0.05, stops: [0, 100] }} }}, stroke: {{ width: 3 }} }});
            
            // Top Expenses Horizontal Bar (Current Month)
            const topExp = [...accs].sort((a,b) => b.value - a.value).slice(0, 5);
            initGlobalChart("chart-top-despesas", {{ 
                ...commonOptions, 
                dataLabels: {{ 
                    enabled: true, 
                    textAnchor: 'start', 
                    style: {{ colors: ['#ffffff'], fontSize: '11px', fontFamily: 'JetBrains Mono' }},
                    formatter: function(val, opt) {{ return opt.w.globals.labels[opt.dataPointIndex] + ": R$ " + parseFloat(val).toFixed(2).replace('.', ','); }},
                    offsetX: 0,
                    dropShadow: {{ enabled: true, top: 1, left: 1, blur: 2, opacity: 1.0 }}
                }},
                yaxis: {{ labels: {{ show: false }} }},
                series: [ {{name: 'Valor', data: topExp.map(a => a.value)}} ], 
                chart: {{ type: 'bar', height: 260, toolbar: {{show:false}} }}, 
                plotOptions: {{ bar: {{ horizontal: true, borderRadius: 2, dataLabels: {{ position: 'bottom' }} }} }}, 
                xaxis: {{ categories: topExp.map(a => a.name) }}, 
                colors: ['#0078D4'] 
            }});
        }}

        function updateTotalsUI(monthKey) {{
            const accounts = appData[monthKey] || [];
            let totalGasto = 0; let pagas = 0;
            accounts.forEach(acc => {{ totalGasto += acc.value; if(acc.ok) pagas++; }});
            
            document.getElementById("total-gasto").textContent = formatCurrency(totalGasto);
            document.getElementById("total-table-value").innerHTML = `<strong>${{formatCurrency(totalGasto)}}</strong>`;
            document.getElementById("contas-pagas").textContent = `${{pagas}}/${{accounts.length}}`;
            
            const r = appRendas[monthKey] || {{meu: 0, dela: 0}};
            const rt = r.meu + r.dela;
            document.getElementById("renda-total").textContent = formatCurrency(rt);
            const s = rt - totalGasto;
            document.getElementById("sobra-mes").textContent = formatCurrency(s);
        }}

        function renderLancamentos(monthKey) {{
            if (!monthKey) return;
            document.getElementById("current-month-display").textContent = formatMonthString(monthKey);
            const accounts = appData[monthKey] || [];
            updateTotalsUI(monthKey);
            
            const tbody = document.getElementById("accounts-tbody");
            tbody.innerHTML = "";
            if (accounts.length === 0) tbody.innerHTML = "<tr><td colspan='5' style='text-align:center;'>Nenhum lançamento</td></tr>";
            accounts.forEach(acc => {{
                const cat = getCategory(acc.name);
                const color = catColors[cat] || catColors["Outros"];
                const tr = document.createElement("tr");
                
                tr.innerHTML = `
                    <td>
                        <strong>${{acc.name}}</strong>
                        <div style="display:flex; gap:6px; margin-top:4px;">
                            ${{acc.isBoleto ? '<span style="font-size:0.7rem; background:rgba(255,255,255,0.1); padding:2px 6px; border-radius:4px;"><i class="fa-solid fa-barcode"></i> Boleto</span>' : ''}}
                            ${{acc.dueDay ? `<span style="font-size:0.7rem; background:rgba(255,255,255,0.1); padding:2px 6px; border-radius:4px;"><i class="fa-solid fa-calendar-day"></i> Dia ${{acc.dueDay}}</span>` : ''}}
                        </div>
                    </td>
                    <td><span style="padding:4px 8px; border-radius:6px; font-size:0.75rem; background:${{color}}20; color:${{color}}; font-weight:600;">${{cat}}</span></td>
                    <td>
                        <div class="inline-val-container">
                            <span style="color:var(--text-muted); font-size:0.85rem;">R$</span>
                            <input type="text" class="inline-val-input" data-id="${{acc.id}}" value="${{acc.value.toLocaleString('pt-BR', {{minimumFractionDigits:2, maximumFractionDigits:2}})}}">
                        </div>
                    </td>
                    <td><span class="status-badge ${{acc.ok ? 'status-ok' : 'status-pendente'}}"><i class="fa-solid ${{acc.ok ? 'fa-check' : 'fa-clock'}}"></i> ${{acc.ok ? 'OK' : 'Pendente'}}</span></td>
                    <td style="text-align:right;">
                        <button class="icon-btn" onclick="toggleStatus(${{acc.id}})"><i class="fa-solid fa-check"></i></button>
                        <button class="icon-btn" onclick="editAccount(${{acc.id}})"><i class="fa-solid fa-pen"></i></button>
                        <button class="icon-btn delete" onclick="deleteAccount(${{acc.id}})"><i class="fa-solid fa-trash"></i></button>
                    </td>
                `;
                tbody.appendChild(tr);
            }});

            const inputs = document.querySelectorAll(".inline-val-input");
            inputs.forEach((inp, i) => {{
                inp.addEventListener("blur", (e) => {{
                    let str = e.target.value;
                    let numStr = str.replace(/\./g, "").replace(",", ".");
                    const val = parseFloat(numStr) || 0;
                    e.target.value = val.toLocaleString("pt-BR", {{minimumFractionDigits:2, maximumFractionDigits:2}});
                    
                    const id = parseInt(e.target.dataset.id);
                    const acc = appData[currentMonth].find(x => x.id === id);
                    if(acc && acc.value !== val) {{
                        acc.value = val;
                        try {{ localStorage.setItem(DATA_KEY, JSON.stringify(appData)); }} catch(e) {{}}
                        updateTotalsUI(currentMonth);
                        if(document.getElementById("view-dashboard").classList.contains("active-view")) renderDashboard(currentMonth);
                    }}
                }});
                inp.addEventListener("keydown", (e) => {{
                    if (e.key === "Enter" || e.key === "ArrowDown") {{
                        e.preventDefault();
                        if (i + 1 < inputs.length) inputs[i + 1].focus();
                        else e.target.blur();
                    }}
                    if (e.key === "ArrowUp") {{
                        e.preventDefault();
                        if (i - 1 >= 0) inputs[i - 1].focus();
                    }}
                }});
            }});
        }}

        function renderMonthList() {{
            const sel = document.getElementById("month-select");
            sel.innerHTML = "";
            availableMonths.forEach(m => {{
                const opt = document.createElement("option");
                opt.value = m;
                opt.textContent = formatMonthString(m);
                if (m === currentMonth) opt.selected = true;
                sel.appendChild(opt);
            }});
        }}

        function switchMonth(m) {{
            if(m === currentMonth) return;
            currentMonth = m;
            renderMonthList(); 
            if(document.getElementById("view-dashboard").classList.contains("active-view")) renderDashboard(m);
            if(document.getElementById("view-lancamentos").classList.contains("active-view")) renderLancamentos(m);
        }}

        function renderAll() {{
            renderLancamentos(currentMonth);
            if(document.getElementById("view-dashboard").classList.contains("active-view")) {{
                renderDashboard(currentMonth);
            }}
        }}

        function init() {{
            loadData();
            if (availableMonths.length === 0) {{
                const ts = new Date();
                const m = ts.getFullYear().toString() + "-" + String(ts.getMonth()+1).padStart(2, '0');
                appData[m] = [];
                availableMonths.push(m);
            }}
            
            const ts = new Date();
            const todayM = ts.getFullYear().toString() + "-" + String(ts.getMonth()+1).padStart(2, '0');
            if (availableMonths.includes(todayM)) {{
                currentMonth = todayM;
            }} else if (!currentMonth) {{
                currentMonth = availableMonths[0];
            }}
            
            setupEventListeners();
            renderMonthList();
            renderDashboard(currentMonth);
            renderLancamentos(currentMonth);
        }}

        function saveData() {{
            try {{
                localStorage.setItem(DATA_KEY, JSON.stringify(appData));
                localStorage.setItem(RENDAS_KEY, JSON.stringify(appRendas));
            }} catch(e) {{}}
            renderAll();
        }}

        function setupEventListeners() {{
            const themeToggle = document.getElementById("theme-toggle");
            const icon = themeToggle.querySelector("i");
            if (localStorage.getItem("theme") === "light") {{
                icon.className = "fa-solid fa-moon";
            }}
            themeToggle.onclick = () => {{
                document.body.classList.toggle("light-theme");
                const isLight = document.body.classList.contains("light-theme");
                localStorage.setItem("theme", isLight ? "light" : "dark");
                icon.className = isLight ? "fa-solid fa-moon" : "fa-solid fa-sun";
                renderAll();
            }};
            
            document.querySelectorAll(".nav-tab").forEach(btn => {{
                btn.onclick = () => {{
                    document.querySelectorAll(".nav-tab").forEach(b => b.classList.remove("active"));
                    btn.classList.add("active");
                    
                    document.querySelectorAll(".view").forEach(v => v.classList.remove("active-view"));
                    const target = document.getElementById(btn.dataset.target);
                    target.classList.add("active-view");
                    
                    renderAll();
                }};
            }});

            document.getElementById("add-month-btn").onclick = () => showModal("modal-month");
            document.getElementById("close-modal-month").onclick = () => closeModal("modal-month");
            document.getElementById("save-month-btn").onclick = () => {{
                const v = document.getElementById("new-month-input").value.trim();
                if(appData[v]) return alert("Já existe!");
                appData[v] = [];
                const p = Object.keys(appData).sort().reverse();
                if(p.length > 1 && confirm("Importar do último mês?")) {{
                    appData[v] = appData[p[1]].map(a => ({{id: Date.now()+Math.random(), name: a.name, value: a.value, ok: false}}));
                }}
                currentMonth = v; saveData(); closeModal("modal-month"); 
                availableMonths = Object.keys(appData).sort().reverse();
                renderMonthList();
                renderAll();
            }};

            document.getElementById("month-select").addEventListener("change", (e) => {{
                switchMonth(e.target.value);
            }});

            document.getElementById("acc-is-parcelado").onchange = (e) => {{
                document.getElementById("parcelas-config").style.display = e.target.checked ? "flex" : "none";
            }};

            document.getElementById("new-account-btn").onclick = () => {{
                editingAccountId = null;
                document.getElementById("modal-acc-title").textContent = "Lançar Conta";
                document.getElementById("acc-name").value = "";
                document.getElementById("acc-val").value = "";
                document.getElementById("acc-due-day").value = "";
                document.getElementById("acc-is-boleto").checked = false;
                document.getElementById("acc-val-container").style.display = "flex";
                document.getElementById("acc-parcelas-container").style.display = "block";
                document.getElementById("acc-is-parcelado").parentElement.style.display = "block";
                document.getElementById("acc-is-parcelado").checked = false;
                document.getElementById("parcelas-config").style.display = "none";
                document.getElementById("acc-parc-total").value = "2";
                showModal("modal-account");
            }};
            
            document.getElementById("close-modal-account").onclick = () => closeModal("modal-account");
            
            document.getElementById("save-account-btn").onclick = () => {{
                const n = document.getElementById("acc-name").value.trim().toUpperCase();
                let vStr = document.getElementById("acc-val").value;
                const v = parseFloat(vStr.replace(',', '.')) || 0;
                let ddStr = document.getElementById("acc-due-day").value;
                let dd = ddStr ? parseInt(ddStr) : null;
                const isB = document.getElementById("acc-is-boleto").checked;
                
                if(!n) return;
                
                if(editingAccountId) {{
                    const a = appData[currentMonth].find(x => x.id === editingAccountId);
                    if(a) {{ 
                        a.name = n;
                        a.dueDay = dd;
                        a.isBoleto = isB;
                    }}
                }} else {{
                    const isParc = document.getElementById("acc-is-parcelado").checked;
                    if(isParc) {{
                        let i = 1;
                        let total = parseInt(document.getElementById("acc-parc-total").value) || 2;
                        if (total >= 2) {{
                            let parts = currentMonth.split("-");
                            let year = parseInt(parts[0]);
                            let month = parseInt(parts[1]);
                            
                            let parcValue = Math.round((v / total) * 100) / 100;
                            let remaining = v;
                            const groupId = Date.now();
                            for (let parc = i; parc <= total; parc++) {{
                                let currVal = (parc === total) ? Math.round(remaining * 100) / 100 : parcValue;
                                remaining -= currVal;
                                
                                const mStr = year.toString() + "-" + month.toString().padStart(2, '0');
                                if (!appData[mStr]) appData[mStr] = [];
                                appData[mStr].push({{
                                    id: Date.now() + parc,
                                    groupId: groupId,
                                    name: n + " " + parc + "/" + total,
                                    value: currVal,
                                    ok: false,
                                    isBoleto: isB,
                                    dueDay: dd
                                }});
                                month++;
                                if (month > 12) {{ month = 1; year++; }}
                            }}
                            availableMonths = Object.keys(appData).sort().reverse();
                            renderMonthList();
                        }}
                    }} else {{
                        appData[currentMonth].push({{id: Date.now(), name: n, value: v, ok: false, isBoleto: isB, dueDay: dd}});
                    }}
                }}
                saveData(); closeModal("modal-account");
            }};
            
            window.editAccount = (id) => {{
                const a = appData[currentMonth].find(x => x.id === id);
                if(!a) return;
                editingAccountId = id;
                document.getElementById("modal-acc-title").textContent = "Editar Conta";
                document.getElementById("acc-name").value = a.name;
                document.getElementById("acc-due-day").value = a.dueDay || "";
                document.getElementById("acc-is-boleto").checked = !!a.isBoleto;
                document.getElementById("acc-val-container").style.display = "none";
                document.getElementById("acc-parcelas-container").style.display = "block";
                document.getElementById("acc-is-parcelado").parentElement.style.display = "none";
                document.getElementById("parcelas-config").style.display = "none";
                showModal("modal-account");
            }};
            
            window.deleteAccount = (id) => {
                const accToDelete = appData[currentMonth].find(x => x.id === id);
                if(!accToDelete) return;

                const isInstallment = accToDelete.groupId || / \d+\/\d+$/.test(accToDelete.name);

                if (isInstallment) {
                    if(confirm("Esta é uma compra parcelada.\n\nDeseja excluir a partir deste mês (apagando esta e as parcelas futuras)?")) {
                        const baseName = accToDelete.name.replace(/ \d+\/\d+$/, '');
                        
                        Object.keys(appData).forEach(mStr => {
                            if (mStr >= currentMonth) {
                                appData[mStr] = appData[mStr].filter(x => {
                                    if (accToDelete.groupId && x.groupId === accToDelete.groupId) return false;
                                    if (!accToDelete.groupId && x.name.startsWith(baseName) && / \d+\/\d+$/.test(x.name)) return false;
                                    return x.id !== id;
                                });
                            }
                        });
                        saveData();
                    } else if (confirm("Neste caso, deseja excluir APENAS esta parcela do mês atual?")) {
                         appData[currentMonth] = appData[currentMonth].filter(x => x.id !== id);
                         saveData();
                    }
                } else {
                    if(confirm("Excluir?")) {
                        appData[currentMonth] = appData[currentMonth].filter(x => x.id !== id);
                        saveData();
                    }
                }
            };
            
            window.toggleStatus = (id) => {{
                const a = appData[currentMonth].find(x => x.id === id);
                if(a) {{ a.ok = !a.ok; saveData(); }}
            }};

            document.getElementById("edit-renda-btn").onclick = () => {{
                const r = appRendas[currentMonth] || {{meu:0, dela:0}};
                document.getElementById("renda-meu").value = r.meu;
                document.getElementById("renda-dela").value = r.dela;
                showModal("modal-rendas");
            }};
            document.getElementById("close-modal-rendas").onclick = () => closeModal("modal-rendas");
            document.getElementById("save-rendas-btn").onclick = () => {{
                appRendas[currentMonth] = {{
                    meu: parseFloat(document.getElementById("renda-meu").value) || 0,
                    dela: parseFloat(document.getElementById("renda-dela").value) || 0
                }};
                saveData(); closeModal("modal-rendas");
            }};
            
            document.getElementById("export-data-btn").onclick = () => {{
                const d = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify({{contas: appData, rendas: appRendas}}));
                const a = document.createElement('a'); a.href = d; a.download = "backup.json"; a.click();
            }};
        }}

        init();
    </script>
</body>
</html>
"""

with codecs.open(r'c:\Users\Usuario\Desktop\contas mensais\index.html', 'w', 'utf-8') as f:
    f.write(html_top + js_script)
print("Build Complete")
