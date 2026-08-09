import codecs
path = r'c:\Users\Usuario\Desktop\contas mensais\extract_and_build.py'
with codecs.open(path, 'r', 'utf-8') as f:
    c = f.read()

# CSS Variables
c = c.replace(
'''        :root {
            --bg-dark: #121212; --glass-bg: rgba(30, 30, 30, 0.7); --glass-border: rgba(255, 255, 255, 0.08);
            --primary: #ffffff; --primary-hover: #d1d1d1; --success: #4caf50; --danger: #f44336; --warning: #ff9800;
            --text-main: #ffffff; --text-muted: #8a8a8a;
        }''',
'''        :root {
            --bg-dark: #121212; --glass-bg: rgba(30, 30, 30, 0.7); --glass-border: rgba(255, 255, 255, 0.08);
            --primary: #ffffff; --primary-hover: #d1d1d1; --success: #4caf50; --danger: #f44336; --warning: #ff9800;
            --text-main: #ffffff; --text-muted: #8a8a8a;
            --card-bg: rgba(30, 30, 30, 0.95);
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
            --input-bg: rgba(0, 0, 0, 0.03);
            --modal-bg: #ffffff;
            --row-hover: rgba(0, 0, 0, 0.04);
            --chart-title: #334155;
        }''')

c = c.replace('background: rgba(30, 30, 30, 0.95);', 'background: var(--card-bg);')
c = c.replace('background: rgba(255, 255, 255, 0.05); border: 1px solid var(--glass-border); color: white;', 'background: var(--input-bg); border: 1px solid var(--glass-border); color: var(--text-main);')
c = c.replace('background: var(--bg-dark); color: white;', 'background: var(--bg-dark); color: var(--text-main);')
c = c.replace('.main-header h2 { font-size: 1.8rem; font-weight: 700; color: white; }', '.main-header h2 { font-size: 1.8rem; font-weight: 700; color: var(--text-main); }')
c = c.replace('color: #f1f5f9;', 'color: var(--chart-title);')
c = c.replace('background: rgba(255,255,255,0.05);', 'background: var(--input-bg);')
c = c.replace('background: rgba(255, 255, 255, 0.02);', 'background: var(--row-hover);')
c = c.replace('background: rgba(255, 255, 255, 0.1); color: white;', 'background: var(--input-bg); color: var(--text-main);')
c = c.replace('.outline-btn { background: rgba(255,255,255,0.05); border: 1px solid var(--glass-border); color: white; } .outline-btn:hover { background: rgba(255,255,255,0.1); }', '.outline-btn { background: var(--input-bg); border: 1px solid var(--glass-border); color: var(--text-main); } .outline-btn:hover { background: var(--row-hover); }')
c = c.replace('.icon-btn:hover { background: rgba(255,255,255,0.1); color: white; }', '.icon-btn:hover { background: var(--input-bg); color: var(--text-main); }')
c = c.replace('.modal { width: 90%; max-width: 420px; background: #1e293b;', '.modal { width: 90%; max-width: 420px; background: var(--modal-bg);')
c = c.replace('background: rgba(0,0,0,0.2); border: 1px solid rgba(255,255,255,0.1); color: white;', 'background: var(--input-bg); border: 1px solid var(--glass-border); color: var(--text-main);')
c = c.replace('.inline-val-input { background: transparent; border: 1px solid transparent; color: white;', '.inline-val-input { background: transparent; border: 1px solid transparent; color: var(--text-main);')
c = c.replace('.apexcharts-tooltip, .apexcharts-tooltip-title { background: #1e293b !important; border: 1px solid rgba(255,255,255,0.1) !important; color: white !important;', '.apexcharts-tooltip, .apexcharts-tooltip-title { background: var(--modal-bg) !important; border: 1px solid var(--glass-border) !important; color: var(--text-main) !important;')

c = c.replace(
'''            <div class="brand">
                <i class="fa-solid fa-chart-pie" style="font-size:28px;"></i>
                <h1>Dashboard<br><span style="font-size:0.8rem; font-weight:400; color:var(--text-muted);">Finanças Pessoais</span></h1>
            </div>''',
'''            <div class="brand" style="display:flex; justify-content: space-between;">
                <div style="display:flex; align-items:center; gap: 12px;">
                    <i class="fa-solid fa-chart-pie" style="font-size:28px;"></i>
                    <h1>Dashboard<br><span style="font-size:0.8rem; font-weight:400; color:var(--text-muted);">Finanças Pessoais</span></h1>
                </div>
                <button id="theme-toggle" class="icon-btn"><i class="fa-solid fa-sun"></i></button>
            </div>''')

c = c.replace(
'''        function setupEventListeners() {
            document.querySelectorAll(".nav-tab").forEach(btn => {''',
'''        function setupEventListeners() {
            const themeToggle = document.getElementById("theme-toggle");
            const icon = themeToggle.querySelector("i");
            if (localStorage.getItem("theme") === "light") {
                document.body.classList.add("light-theme");
                icon.className = "fa-solid fa-moon";
            }
            themeToggle.onclick = () => {
                document.body.classList.toggle("light-theme");
                const isLight = document.body.classList.contains("light-theme");
                localStorage.setItem("theme", isLight ? "light" : "dark");
                icon.className = isLight ? "fa-solid fa-moon" : "fa-solid fa-sun";
                renderAll();
            };
            
            document.querySelectorAll(".nav-tab").forEach(btn => {'''
)

c = c.replace("theme: { mode: 'dark' },", "theme: { mode: document.body.classList.contains('light-theme') ? 'light' : 'dark' },")

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(c)

print('Rewrite complete')
