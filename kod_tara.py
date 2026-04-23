import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ─── Taranacak uzantılar ─────────────────────────────────────────────────────
CODE_EXTENSIONS = {
    # Python
    ".py": ("Python", "#3572A5"),
    # Web
    ".html": ("HTML", "#E34C26"), ".htm": ("HTML", "#E34C26"),
    ".css": ("CSS", "#563D7C"), ".scss": ("CSS", "#563D7C"),
    ".js": ("JavaScript", "#F1E05A"), ".ts": ("TypeScript", "#2B7489"),
    ".jsx": ("React", "#61DAFB"), ".tsx": ("React", "#61DAFB"),
    ".php": ("PHP", "#4F5D95"),
    # Arduino / Embedded
    ".ino": ("Arduino", "#00979D"), ".pde": ("Arduino", "#00979D"),
    ".c": ("C", "#555555"), ".h": ("C Header", "#555555"),
    ".cpp": ("C++", "#F34B7D"),
    # Veri / Config
    ".json": ("JSON", "#888888"), ".yaml": ("YAML", "#CB171E"),
    ".yml": ("YAML", "#CB171E"), ".toml": ("TOML", "#9C4221"),
    ".xml": ("XML", "#0060AC"), ".sql": ("SQL", "#E38C00"),
    # Shell
    ".sh": ("Shell", "#89E051"), ".bat": ("Batch", "#C1F12E"),
    ".ps1": ("PowerShell", "#012456"),
    # Diğer
    ".rs": ("Rust", "#DEA584"), ".go": ("Go", "#00ADD8"),
    ".java": ("Java", "#B07219"), ".kt": ("Kotlin", "#F18E33"),
    ".rb": ("Ruby", "#701516"), ".lua": ("Lua", "#000080"),
    ".dart": ("Dart", "#00B4AB"), ".swift": ("Swift", "#FFAC45"),
}

# Proje işaretleri
PROJECT_MARKERS = {
    "requirements.txt", "setup.py", "pyproject.toml", "Pipfile",
    "package.json", "composer.json", "Cargo.toml", "go.mod",
    "CMakeLists.txt", "Makefile", "pom.xml", "build.gradle",
    ".git",
}

# Atlanacak klasörler
SKIP_DIRS = {
    "node_modules", "__pycache__", ".git", "venv", "env", ".venv",
    "dist", "build", ".next", ".nuxt", "target", "bin", "obj",
    "AppData", "Windows", "Program Files", "Program Files (x86)",
    "$Recycle.Bin", "System Volume Information", "ProgramData",
    ".npm", ".cache", "site-packages",
}

# ─── Tarayıcı ────────────────────────────────────────────────────────────────
def get_drives():
    drives = []
    if os.name == "nt":
        import ctypes
        bitmask = ctypes.windll.kernel32.GetLogicalDrives()
        for i in range(26):
            if bitmask & (1 << i):
                drives.append(f"{chr(65+i)}:\\")
    else:
        drives = ["/"]
    return drives

def file_preview(path, lines=6):
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            content = []
            for i, line in enumerate(f):
                if i >= lines: break
                content.append(line.rstrip())
            return "\n".join(content)
    except:
        return ""

def scan():
    drives = get_drives()
    projects = defaultdict(lambda: {"files": [], "langs": defaultdict(int), "marker": None})
    orphans = []  # proje klasörü olmayan tek dosyalar
    total_files = 0
    scanned_dirs = 0

    print(f"Taranıyor: {', '.join(drives)}")
    print("Bu işlem birkaç dakika sürebilir...\n")

    for drive in drives:
        for root, dirs, files in os.walk(drive):
            # atlanacak klasörleri filtrele
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            
            scanned_dirs += 1
            if scanned_dirs % 500 == 0:
                print(f"  {scanned_dirs} klasör tarandı... ({root[:60]})")

            root_path = Path(root)
            
            # bu klasör proje mi?
            found_markers = PROJECT_MARKERS.intersection(set(files) | set(dirs))
            proj_key = str(root_path)
            if found_markers:
                projects[proj_key]["marker"] = list(found_markers)[0]

            for fname in files:
                ext = Path(fname).suffix.lower()
                if ext not in CODE_EXTENSIONS:
                    continue
                
                fpath = root_path / fname
                try:
                    stat = fpath.stat()
                    size = stat.st_size
                    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                except:
                    continue

                lang, color = CODE_EXTENSIONS[ext]
                file_info = {
                    "name": fname,
                    "path": str(fpath),
                    "dir": str(root_path),
                    "ext": ext,
                    "lang": lang,
                    "color": color,
                    "size": size,
                    "mtime": mtime,
                    "preview": file_preview(fpath) if size < 50000 else "",
                }

                # hangi projeye ait?
                assigned = False
                check = root_path
                for _ in range(4):  # en fazla 4 üst klasör yukarı bak
                    key = str(check)
                    if key in projects:
                        projects[key]["files"].append(file_info)
                        projects[key]["langs"][lang] += 1
                        assigned = True
                        break
                    check = check.parent
                
                if not assigned:
                    orphans.append(file_info)

                total_files += 1

    # sadece kod dosyası olan projeleri al
    real_projects = {k: v for k, v in projects.items() if v["files"]}
    
    print(f"\nTamamlandı: {total_files} kod dosyası, {len(real_projects)} proje klasörü bulundu.")
    return real_projects, orphans, total_files

# ─── HTML rapor ──────────────────────────────────────────────────────────────
def size_fmt(b):
    for u in ["B","KB","MB","GB"]:
        if b < 1024: return f"{b:.0f} {u}"
        b /= 1024
    return f"{b:.1f} GB"

def build_html(projects, orphans, total_files):
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # istatistikler
    all_langs = defaultdict(int)
    for p in projects.values():
        for lang, cnt in p["langs"].items():
            all_langs[lang] += cnt
    for o in orphans:
        all_langs[o["lang"]] += 1

    lang_stats = sorted(all_langs.items(), key=lambda x: -x[1])

    # proje kartları HTML
    project_cards = ""
    sorted_projects = sorted(projects.items(), key=lambda x: -len(x[1]["files"]))
    
    for proj_path, data in sorted_projects:
        files = data["files"]
        langs = data["langs"]
        marker = data.get("marker","")
        proj_name = Path(proj_path).name
        
        lang_badges = "".join(
            f'<span class="badge" style="background:{CODE_EXTENSIONS.get(next((f["ext"] for f in files if f["lang"]==l), ".py"), ("#888","#888"))[1]}22;color:{CODE_EXTENSIONS.get(next((f["ext"] for f in files if f["lang"]==l), ".py"), ("#888","#888"))[1]};border:1px solid {CODE_EXTENSIONS.get(next((f["ext"] for f in files if f["lang"]==l), ".py"), ("#888","#888"))[1]}44">{l} <b>{c}</b></span>'
            for l,c in sorted(langs.items(), key=lambda x:-x[1])
        )

        file_rows = ""
        for fi in sorted(files, key=lambda x: -x["size"])[:20]:
            preview_escaped = fi["preview"].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
            file_rows += f"""
            <tr onclick="togglePreview(this)" style="cursor:pointer">
              <td><span class="dot" style="background:{fi['color']}"></span>{fi['name']}</td>
              <td><span class="lang-tag">{fi['lang']}</span></td>
              <td style="color:#666;font-size:11px">{size_fmt(fi['size'])}</td>
              <td style="color:#555;font-size:11px">{fi['mtime']}</td>
              <td style="color:#444;font-size:11px;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="{fi['path']}">{fi['path']}</td>
            </tr>
            <tr class="preview-row" style="display:none">
              <td colspan="5"><pre class="preview">{preview_escaped if preview_escaped else '(önizleme yok)'}</pre></td>
            </tr>"""
        
        more = f'<div class="more-files">+ {len(files)-20} dosya daha</div>' if len(files) > 20 else ""

        project_cards += f"""
        <div class="project-card" data-langs="{' '.join(langs.keys())}">
          <div class="project-header" onclick="toggleCard(this)">
            <div class="project-title">
              <span class="proj-icon">{'⚙' if any(e in ['.ino','.pde','.c','.cpp'] for e in [f['ext'] for f in files]) else '🐍' if '.py' in [f['ext'] for f in files] else '🌐'}</span>
              <div>
                <div class="proj-name">{proj_name}</div>
                <div class="proj-path">{proj_path}</div>
              </div>
            </div>
            <div class="project-meta">
              {lang_badges}
              <span class="file-count">{len(files)} dosya</span>
              {f'<span class="marker-badge">{marker}</span>' if marker else ''}
              <span class="chevron">▾</span>
            </div>
          </div>
          <div class="project-body" style="display:none">
            <table class="file-table">
              <thead><tr><th>Dosya</th><th>Dil</th><th>Boyut</th><th>Tarih</th><th>Yol</th></tr></thead>
              <tbody>{file_rows}</tbody>
            </table>
            {more}
          </div>
        </div>"""

    # sahipsiz dosyalar
    orphan_rows = ""
    for fi in sorted(orphans, key=lambda x: x["lang"])[:200]:
        preview_escaped = fi["preview"].replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
        orphan_rows += f"""
        <tr onclick="togglePreview(this)" style="cursor:pointer">
          <td><span class="dot" style="background:{fi['color']}"></span>{fi['name']}</td>
          <td><span class="lang-tag">{fi['lang']}</span></td>
          <td style="color:#666;font-size:11px">{size_fmt(fi['size'])}</td>
          <td style="color:#555;font-size:11px">{fi['mtime']}</td>
          <td style="color:#444;font-size:11px" title="{fi['path']}">{fi['dir']}</td>
        </tr>
        <tr class="preview-row" style="display:none">
          <td colspan="5"><pre class="preview">{preview_escaped if preview_escaped else '(önizleme yok)'}</pre></td>
        </tr>"""

    lang_bar = "".join(
        f'<div class="lang-bar-item" onclick="filterLang(\'{l}\')" title="{l}: {c} dosya">'
        f'<span class="dot" style="background:{CODE_EXTENSIONS.get(next((e for e,d in CODE_EXTENSIONS.items() if d[0]==l), ".py"), ("#888","#888"))[1]}"></span>'
        f'{l} <b>{c}</b></div>'
        for l,c in lang_stats[:12]
    )

    html = f"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Kod Haritası — {now}</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{background:#0D0D14;color:#CCC;font-family:"Segoe UI",sans-serif;font-size:13px;line-height:1.5}}
  a{{color:#6C63FF}}
  .header{{background:#13131E;border-bottom:1px solid #222233;padding:20px 28px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px}}
  .header h1{{font-size:20px;font-weight:700;color:#6C63FF;letter-spacing:1px}}
  .header .meta{{font-size:12px;color:#555;}}
  .stats{{display:flex;gap:0;background:#13131E;border-bottom:1px solid #222233}}
  .stat{{padding:14px 24px;border-right:1px solid #222233}}
  .stat .val{{font-size:22px;font-weight:700;color:#E8E8F0}}
  .stat .lbl{{font-size:11px;color:#555;margin-top:2px}}
  .stat .val.green{{color:#00D4AA}} .stat .val.blue{{color:#6C63FF}} .stat .val.amber{{color:#F0A500}}
  .lang-bar{{display:flex;flex-wrap:wrap;gap:8px;padding:14px 28px;background:#111119;border-bottom:1px solid #1E1E2E}}
  .lang-bar-item{{display:flex;align-items:center;gap:5px;padding:5px 12px;border-radius:99px;border:1px solid #2A2A3A;cursor:pointer;font-size:12px;color:#999;transition:all .15s}}
  .lang-bar-item:hover,.lang-bar-item.active{{background:#1E1E30;color:#CCC;border-color:#6C63FF}}
  .lang-bar-item b{{color:#E8E8F0}}
  .toolbar{{display:flex;gap:10px;padding:12px 28px;background:#0F0F1A;border-bottom:1px solid #1A1A28;align-items:center;flex-wrap:wrap}}
  .toolbar input{{background:#13131E;border:1px solid #2A2A3A;border-radius:6px;padding:7px 12px;color:#CCC;font-size:13px;width:280px}}
  .toolbar input:focus{{outline:none;border-color:#6C63FF}}
  .toolbar button{{background:#1E1E2E;border:1px solid #2A2A3A;border-radius:6px;padding:7px 14px;color:#999;cursor:pointer;font-size:12px}}
  .toolbar button:hover{{background:#2A2A3A;color:#CCC}}
  .toolbar button.active{{border-color:#6C63FF;color:#6C63FF}}
  .content{{padding:16px 28px;max-width:1400px}}
  .section-title{{font-size:13px;font-weight:600;color:#666;letter-spacing:1px;text-transform:uppercase;margin:24px 0 12px}}
  .project-card{{background:#13131E;border:1px solid #1E1E2E;border-radius:8px;margin-bottom:8px;overflow:hidden;transition:border-color .15s}}
  .project-card:hover{{border-color:#2E2E42}}
  .project-header{{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;cursor:pointer;gap:12px;flex-wrap:wrap}}
  .project-title{{display:flex;align-items:center;gap:12px}}
  .proj-icon{{font-size:20px;width:32px;text-align:center}}
  .proj-name{{font-size:14px;font-weight:600;color:#E8E8F0}}
  .proj-path{{font-size:11px;color:#444;font-family:"Cascadia Code","Consolas",monospace;margin-top:2px}}
  .project-meta{{display:flex;align-items:center;gap:8px;flex-wrap:wrap}}
  .badge{{font-size:11px;padding:3px 9px;border-radius:99px;font-weight:500}}
  .file-count{{font-size:12px;color:#555;padding:3px 8px;background:#0D0D14;border-radius:4px}}
  .marker-badge{{font-size:10px;color:#00D4AA;padding:2px 7px;background:#001A14;border:1px solid #004433;border-radius:4px}}
  .chevron{{color:#444;font-size:14px;transition:transform .2s;flex-shrink:0}}
  .project-body{{padding:0 16px 12px;border-top:1px solid #1A1A28}}
  .file-table{{width:100%;border-collapse:collapse;margin-top:8px}}
  .file-table th{{font-size:11px;color:#444;font-weight:600;letter-spacing:.5px;padding:6px 8px;border-bottom:1px solid #1A1A28;text-align:left}}
  .file-table td{{padding:6px 8px;border-bottom:1px solid #111119;vertical-align:middle}}
  .file-table tr:hover td{{background:#0F0F1A}}
  .dot{{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:7px;flex-shrink:0}}
  .lang-tag{{font-size:10px;padding:2px 7px;border-radius:4px;background:#1A1A28;color:#777}}
  .preview-row td{{padding:0}}
  .preview{{background:#080810;color:#8A8AAA;font-family:"Cascadia Code","Consolas",monospace;font-size:11px;padding:12px 16px;border-top:1px solid #111119;overflow-x:auto;max-height:180px;overflow-y:auto;white-space:pre}}
  .more-files{{font-size:12px;color:#444;padding:8px 0;text-align:center}}
  .orphan-section{{margin-top:32px}}
  #search-box::placeholder{{color:#333}}
  .hidden{{display:none!important}}
  @media(max-width:700px){{.project-header{{flex-direction:column;align-items:flex-start}}.stats{{flex-wrap:wrap}}.toolbar input{{width:100%}}}}
</style>
</head>
<body>

<div class="header">
  <h1>⬡ Kod Haritası</h1>
  <div class="meta">Oluşturuldu: {now} &nbsp;·&nbsp; Toplam {total_files} kod dosyası tarandı</div>
</div>

<div class="stats">
  <div class="stat"><div class="val green">{total_files}</div><div class="lbl">Kod Dosyası</div></div>
  <div class="stat"><div class="val blue">{len(projects)}</div><div class="lbl">Proje Klasörü</div></div>
  <div class="stat"><div class="val amber">{len(lang_stats)}</div><div class="lbl">Dil / Teknoloji</div></div>
  <div class="stat"><div class="val">{len(orphans)}</div><div class="lbl">Sahipsiz Dosya</div></div>
</div>

<div class="lang-bar">
  <div class="lang-bar-item active" onclick="filterLang('')" title="Tümünü göster">
    Tümü
  </div>
  {lang_bar}
</div>

<div class="toolbar">
  <input type="text" id="search-box" placeholder="Proje veya dosya ara…" oninput="doSearch(this.value)">
  <button onclick="expandAll()">Tümünü Aç</button>
  <button onclick="collapseAll()">Tümünü Kapat</button>
  <span style="color:#333;font-size:12px;margin-left:8px">Dosya adına tıklayarak kodu önizle</span>
</div>

<div class="content">
  <div class="section-title">Proje Klasörleri</div>
  <div id="projects-container">
    {project_cards}
  </div>

  <div class="orphan-section">
    <div class="section-title">Sahipsiz Dosyalar <span style="color:#333;font-weight:400;font-size:11px">(proje klasörü tespit edilemedi)</span></div>
    <div class="project-card">
      <div class="project-header" onclick="toggleCard(this)">
        <div class="project-title">
          <span class="proj-icon">📄</span>
          <div>
            <div class="proj-name">Dağınık Dosyalar</div>
            <div class="proj-path">Proje klasörüne ait olmayan kod dosyaları</div>
          </div>
        </div>
        <div class="project-meta">
          <span class="file-count">{len(orphans)} dosya</span>
          <span class="chevron">▾</span>
        </div>
      </div>
      <div class="project-body" style="display:none">
        <table class="file-table">
          <thead><tr><th>Dosya</th><th>Dil</th><th>Boyut</th><th>Tarih</th><th>Klasör</th></tr></thead>
          <tbody>{orphan_rows}</tbody>
        </table>
      </div>
    </div>
  </div>
</div>

<script>
function toggleCard(header) {{
  const body = header.nextElementSibling;
  const chev = header.querySelector('.chevron');
  const open = body.style.display !== 'none';
  body.style.display = open ? 'none' : 'block';
  chev.style.transform = open ? '' : 'rotate(180deg)';
}}
function togglePreview(row) {{
  const next = row.nextElementSibling;
  if (next && next.classList.contains('preview-row')) {{
    next.style.display = next.style.display === 'none' ? 'table-row' : 'none';
  }}
}}
function expandAll() {{
  document.querySelectorAll('.project-body').forEach(b => {{ b.style.display='block'; }});
  document.querySelectorAll('.chevron').forEach(c => {{ c.style.transform='rotate(180deg)'; }});
}}
function collapseAll() {{
  document.querySelectorAll('.project-body').forEach(b => {{ b.style.display='none'; }});
  document.querySelectorAll('.chevron').forEach(c => {{ c.style.transform=''; }});
}}
function doSearch(q) {{
  q = q.toLowerCase();
  document.querySelectorAll('.project-card').forEach(card => {{
    const text = card.textContent.toLowerCase();
    card.classList.toggle('hidden', q.length > 0 && !text.includes(q));
  }});
}}
function filterLang(lang) {{
  document.querySelectorAll('.lang-bar-item').forEach(el => el.classList.remove('active'));
  event.currentTarget.classList.add('active');
  document.querySelectorAll('#projects-container .project-card').forEach(card => {{
    if (!lang) {{ card.classList.remove('hidden'); return; }}
    const langs = card.dataset.langs || '';
    card.classList.toggle('hidden', !langs.toLowerCase().includes(lang.toLowerCase()));
  }});
}}
</script>
</body>
</html>"""
    return html

# ─── Ana ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    projects, orphans, total = scan()
    html = build_html(projects, orphans, total)
    
    out_path = os.path.join(os.path.expanduser("~"), "Desktop", "kod_haritasi.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\n✓ Rapor oluşturuldu: {out_path}")
    print("Tarayıcıda açılıyor...")
    
    import webbrowser
    webbrowser.open(f"file:///{out_path}")
