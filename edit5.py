import codecs
path = r'c:\Users\Usuario\Desktop\contas mensais\extract_and_build.py'
with codecs.open(path, 'r', 'utf-8') as f:
    c = f.read()

old_create = '''                            let parcValue = Math.round((v / total) * 100) / 100;
                            let remaining = v;
                            
                            for (let parc = i; parc <= total; parc++) {
                                let currVal = (parc === total) ? Math.round(remaining * 100) / 100 : parcValue;
                                remaining -= currVal;
                                
                                const mStr = year.toString() + "-" + month.toString().padStart(2, '0');
                                if (!appData[mStr]) appData[mStr] = [];
                                appData[mStr].push({
                                    id: Date.now() + parc,
                                    name: n + " " + parc + "/" + total,
                                    value: currVal,
                                    ok: false
                                });'''

new_create = '''                            let parcValue = Math.round((v / total) * 100) / 100;
                            let remaining = v;
                            const groupId = Date.now();
                            for (let parc = i; parc <= total; parc++) {
                                let currVal = (parc === total) ? Math.round(remaining * 100) / 100 : parcValue;
                                remaining -= currVal;
                                
                                const mStr = year.toString() + "-" + month.toString().padStart(2, '0');
                                if (!appData[mStr]) appData[mStr] = [];
                                appData[mStr].push({
                                    id: Date.now() + parc,
                                    groupId: groupId,
                                    name: n + " " + parc + "/" + total,
                                    value: currVal,
                                    ok: false
                                });'''

old_f = old_create.replace('{', '{{').replace('}', '}}')
new_f = new_create.replace('{', '{{').replace('}', '}}')

if old_create in c: c = c.replace(old_create, new_create)
elif old_f in c: c = c.replace(old_f, new_f)
else: print('Failed to find create block')

old_delete = '''            window.deleteAccount = (id) => {
                if(confirm("Excluir?")) {
                    appData[currentMonth] = appData[currentMonth].filter(x => x.id !== id);
                    saveData();
                }
            };'''

new_delete = '''            window.deleteAccount = (id) => {
                const accToDelete = appData[currentMonth].find(x => x.id === id);
                if(!accToDelete) return;

                const isInstallment = accToDelete.groupId || / \d+\/\d+$/.test(accToDelete.name);

                if (isInstallment) {
                    if(confirm("Esta é uma compra parcelada.\\n\\nDeseja excluir TODAS as parcelas dela em todos os meses?")) {
                        const baseName = accToDelete.name.replace(/ \d+\/\d+$/, '');
                        
                        Object.keys(appData).forEach(mStr => {
                            appData[mStr] = appData[mStr].filter(x => {
                                if (accToDelete.groupId && x.groupId === accToDelete.groupId) return false;
                                if (!accToDelete.groupId && x.name.startsWith(baseName) && / \d+\/\d+$/.test(x.name)) return false;
                                return x.id !== id;
                            });
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
            };'''
            
old_d_f = old_delete.replace('{', '{{').replace('}', '}}')
new_d_f = new_delete.replace('{', '{{').replace('}', '}}')

if old_delete in c: c = c.replace(old_delete, new_delete)
elif old_d_f in c: c = c.replace(old_d_f, new_d_f)
else: print('Failed to find delete block')

with codecs.open(path, 'w', 'utf-8') as f:
    f.write(c)

print('Success')
