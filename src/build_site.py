#!/usr/bin/env python3
"""
Static portfolio generator for Omar D. Sanchez.
Reads the original CSV data files and emits a single self-contained index.html.
Re-run this after editing a CSV to regenerate the site, then redeploy.

Usage:  python3 build_site.py
"""
import pandas as pd
import html
from pathlib import Path

HERE = Path(__file__).resolve().parent   # src/
REPO = HERE / "data"         # source data
OUT  = HERE.parent / "dist"  # site output

def esc(x):
    return html.escape(str(x).strip()) if x is not None else ""

def clean_url(u):
    if u is None or str(u).strip().lower() in ("nan", "", "''"):
        return ""
    return str(u).strip().replace("\n", "").replace("\r", "")

# ---------------------------------------------------------------- static content
NAME      = "Omar D. Sanchez"
ROLE      = "Network Engineer"
TAGS      = ["USMC Veteran", "Secret Cleared", "9+ yrs DoD Networks"]
EMAIL     = "omar.sanchez008@gmail.com"
LINKEDIN  = "https://linkedin.com/in/os-networks"
GITHUB    = "https://github.com/OmrSanchez"

BIO = (
    "Network Engineer with over nine years of experience in "
    "Department of Defense network infrastructures. My path began in the U.S. Marine "
    "Corps building, securing, and maintaining mission-critical communications under "
    "pressure. I bring that same discipline and a security-first mindset to the modern "
    "enterprise — designing resilient architectures, implementing robust security "
    "controls, and automating complex operations with Python and Ansible to build "
    "faster, more intelligent networks."
)

SKILLS = [
    ("Routing &amp; Switching", [
        ("Routing", "OSPF, BGP, HSRP, Static &amp; Default"),
        ("Switching", "STP (RPVST+), EtherChannel (LACP/PAgP), VTP, VLANs, 802.1Q"),
        ("Addressing", "IPv4, IPv6, Subnetting, VLSM"),
        ("Platforms", "Cisco IOS, Brocade IOS"),
    ]),
    ("Automation &amp; Programming", [
        ("Languages", "Python, Ansible, Git &amp; version control"),
        ("Frameworks / APIs", "NETCONF, RESTCONF, REST APIs, Cisco NSO"),
    ]),
    ("Network Security", [
        ("Access Control", "ACLs, Port Security, NAC (802.1x), RADIUS"),
        ("Threat Mitigation", "DHCP Snooping, Dynamic ARP Inspection"),
        ("Infrastructure", "Firewalls, VPNs, NAT/PAT"),
        ("Compliance", "STIGs, hardening"),
    ]),
    ("Services &amp; Virtualization", [
        ("Core Services", "DHCP + Relay, DNS, NTP, SNMP, Syslog"),
        ("Virtualization", "GNS3, VMware, Docker"),
    ]),
]

TIMELINE = [
    ("Jan 2016", "Enlisted — U.S. Marine Corps. Began service and technical leadership."),
    ("Feb 2024", "Honorably concluded eight years of service as a Sergeant; pivoted full-time to network engineering."),
    ("Jun 2025", "Earned the Cisco trifecta — CCNA, DevNet Associate, and Cybersecurity Associate."),
    ("Aug 2025", "Completed university Capstone: designed, built, and tested a multi-site enterprise network."),
    ("Aug 2025", "Earned B.S. in Network Engineering and Security."),
]

# ---------------------------------------------------------------- data files
net_df  = pd.read_csv(REPO / "network_automation_projects_data.csv", sep=";")
py_df   = pd.read_csv(REPO / "python_projects_data.csv", sep=";")
cert_df = pd.read_csv(REPO / "certifications.csv", sep=";")

# ---------------------------------------------------------------- card builders
def project_card(row, img_dir, featured=False):
    title = esc(row["title"])
    desc  = esc(row["description"])
    goal  = esc(row.get("goal", "")).replace("Goal:", "").strip()
    url   = clean_url(row.get("url"))
    img   = clean_url(row.get("image"))
    fixme = ""
    # Flag the known-bad python "Portfolio Website" URL
    if url.lower().startswith("https://pythonhow.com"):
        url = GITHUB
        fixme = "<!-- FIXME: original CSV pointed to pythonhow.com (tutorial site). Defaulted to your GitHub. -->"
    imgtag = (f'<div class="card-media"><img src="{img_dir}/{esc(img)}" alt="{title}" loading="lazy"></div>'
              if img else "")
    link = (f'<a class="card-link" href="{url}" target="_blank" rel="noopener">View project<span class="arr">&#8599;</span></a>'
            if url else "")
    feat = '<span class="feat">Featured</span>' if featured else ""
    return f"""{fixme}
        <article class="card">
          {imgtag}
          <div class="card-body">
            <div class="card-head">{feat}<h3>{title}</h3></div>
            <p class="desc">{desc}</p>
            {'<p class="goal"><span class="goal-k">Goal</span> ' + goal + '</p>' if goal else ''}
            {link}
          </div>
        </article>"""

def cert_card(row):
    name = esc(row["name"])
    acq  = esc(row["acquired"])
    exp  = esc(row["expires"])
    ver  = clean_url(row["verification"])
    pdf  = clean_url(row["pdf"])
    fixme = ""
    if name.startswith("Cisco Certified DevNet"):
        fixme = "<!-- FIXME: acquired date in source CSV is 'Jun 27, 2028' (a future/typo date). Verify and correct. -->"
    verify = (f'<a href="{ver}" target="_blank" rel="noopener">Verify&#8599;</a>'
              if ver.startswith("http")
              else f'<span class="cred-id">ID {ver}</span>')
    pdflink = (f'<a href="cert_images/{esc(pdf)}" target="_blank" rel="noopener">Certificate&#8599;</a>'
               if pdf else "")
    expline = "" if exp.lower() == "never" else f'<span class="ck">Expires</span>{exp}'
    return f"""{fixme}
        <article class="cert">
          <div class="cert-dot"></div>
          <h3>{name}</h3>
          <div class="cert-meta">
            <span class="ck">Earned</span>{acq}
            {expline}
          </div>
          <div class="cert-actions">{pdflink}{verify}</div>
        </article>"""

# featured first for network projects
net_cards = "".join(project_card(r, "net_images", featured=(i < 2))
                    for i, (_, r) in enumerate(net_df.iterrows()))
py_cards  = "".join(project_card(r, "images") for _, r in py_df.iterrows())
certs     = "".join(cert_card(r) for _, r in cert_df.iterrows())

skills_html = ""
for domain, items in SKILLS:
    rows = "".join(f'<div class="srow"><span class="sk">{k}</span><span class="sv">{v}</span></div>'
                   for k, v in items)
    skills_html += f'<div class="skill-block"><h3>{domain}</h3>{rows}</div>'

tags_html = "".join(f'<span class="tag">{t}</span>' for t in TAGS)
tl_html = "".join(
    f'<li><span class="tl-date">{d}</span><span class="tl-node"></span><span class="tl-text">{t}</span></li>'
    for d, t in TIMELINE)

NAV = [("index","Profile"),("about","About"),("skills","Capabilities"),
       ("network","Network"),("python","Python"),("credentials","Credentials"),
       ("contact","Contact")]

def nav_for(active):
    items = ""
    for i, label in NAV:
        cls = ' class="active"' if i == active else ''
        items += f'<li><a href="{i}.html"{cls}><span class="nav-node"></span>{label}</a></li>'
    return items

index_content = f"""
    <section class="hero" id="profile">
      <div class="hero-grid">
        <div>
          <h1>{NAME}</h1>
          <div class="role">{ROLE}</div>
          <div class="tags">{tags_html}</div>
          <p class="bio">{BIO}</p>
          <div class="hero-links">
            <a class="btn primary" href="contact.html">Get in touch</a>
            <a class="btn" href="{GITHUB}" target="_blank" rel="noopener">GitHub &#8599;</a>
            <a class="btn" href="{LINKEDIN}" target="_blank" rel="noopener">LinkedIn &#8599;</a>
          </div>
        </div>
        <div class="portrait"><img src="images/photo.jpg" alt="{NAME}"></div>
      </div>
    </section>
"""

about_content = f"""<section id="about" class="reveal">
          <div class="eyebrow">About</div>
          <h2>From the battlefield to the backbone.</h2>
          <div class="about-grid" style="margin-top:30px">
            <div>
              <p>My passion for network engineering was forged in the U.S. Marine Corps. For eight years I engineered secure satellite networks where 99.9% uptime wasn't a goal — it was the mission. Every signal mattered.</p>
              <p>Transitioning out was an acceleration, not an end. I moved through the technologies that form the digital nervous system of modern enterprise: from the physical layer to the application, from routing and security to automation. Not just certifications — a deliberate, aggressive pursuit of deep, practical knowledge.</p>
              <p>I'm an engineer who improves systems through intelligent design and automation, not just one who maintains them. I'm not looking for a job — I'm looking for a mission.</p>
            </div>
            <ul class="timeline">{tl_html}</ul>
          </div>
        </section>
"""

skills_content = f"""<section id="skills" class="reveal">
      <div class="eyebrow">Capabilities</div>
      <h2>Technical skills &amp; expertise.</h2>
      <div class="skills" style="margin-top:30px">{skills_html}</div>
    </section>
"""

network_content = f"""<section id="network" class="reveal">
      <div class="eyebrow">Network &amp; Automation</div>
      <h2>Infrastructure, labs &amp; troubleshooting.</h2>
      <div class="cards" style="margin-top:30px">{net_cards}</div>
    </section>
"""

python_content = f"""    <section id="python" class="reveal">
      <div class="eyebrow">Python</div>
      <h2>Applications &amp; tooling.</h2>
      <div class="cards" style="margin-top:30px">{py_cards}</div>
    </section>
"""

credentials_content = f"""  <section id="credentials" class="reveal">
      <div class="eyebrow">Credentials</div>
      <h2>Certifications.</h2>
      <div class="cert-grid" style="margin-top:30px">{certs}</div>
    </section>
"""

contact_content = f"""    <section id="contact" class="reveal">
      <div class="eyebrow">Contact</div>
      <h2>Let's build something resilient.</h2>
      <div class="contact-grid" style="margin-top:30px">
        <div>
          <p class="contact-lead">Open to network engineering and automation roles. The fastest way to reach me is directly:</p>
          <div class="contact-links">
            <a class="clink" href="mailto:{EMAIL}"><span class="k">Email</span>{EMAIL}</a>
            <a class="clink" href="{LINKEDIN}" target="_blank" rel="noopener"><span class="k">LinkedIn</span>/in/os-networks &#8599;</a>
            <a class="clink" href="{GITHUB}" target="_blank" rel="noopener"><span class="k">GitHub</span>/OmrSanchez &#8599;</a>
          </div>
        </div>
        <div>
          <!-- Optional form. Wire the action to a Formspree endpoint (formspree.io) to receive
               submissions on a static host, or delete this whole block to keep contact links-only. -->
          <form action="https://formspree.io/f/xdenwrzw" method="POST">
            <label for="email">Your email</label>
            <input id="email" type="email" name="email" placeholder="you@company.com" required>
            <label for="topic">Topic</label>
            <select id="topic" name="topic">
              <option>Job Inquiries</option>
              <option>Project Proposals</option>
              <option>Other</option>
            </select>
            <label for="msg">Message</label>
            <textarea id="msg" name="message" placeholder="Your message" required></textarea>
            <button class="btn primary" type="submit" style="justify-content:center">Send message</button>
          </form>
        </div>
      </div>
    </section>
"""

def render_page(main_content, active):
    html_page = f"""<!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{NAME} — {ROLE}</title>
    <meta name="description" content="{NAME}, Network & Automation Engineer. USMC veteran, secret cleared. DoD and enterprise network design, security, and automation.">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
    :root{{
      --bg:#0d1218; --panel:#141c26; --panel-2:#18212d; --line:#243244;
      --ink:#e7edf4; --mut:#8695a8; --dim:#5d6b7e;
      --sig:#4fd1c9; --sig-dim:#2b9a94; --sig-glow:rgba(79,209,201,.16);
      --warn:#e0a458;
      --r:10px;
      --sans:'IBM Plex Sans',system-ui,sans-serif;
      --mono:'IBM Plex Mono',ui-monospace,monospace;
      --disp:'Space Grotesk',var(--sans);
    }}
    *{{box-sizing:border-box;margin:0;padding:0}}
    html{{scroll-behavior:smooth}}
    body{{
      background:var(--bg);color:var(--ink);font-family:var(--sans);
      font-size:15.5px;line-height:1.6;-webkit-font-smoothing:antialiased;
      background-image:
        linear-gradient(var(--line) 1px,transparent 1px),
        linear-gradient(90deg,var(--line) 1px,transparent 1px);
      background-size:44px 44px;background-position:-1px -1px;
    }}
    body::before{{content:"";position:fixed;inset:0;pointer-events:none;
      background:radial-gradient(120% 80% at 20% 0%,transparent 55%,var(--bg) 100%);z-index:0}}
    a{{color:var(--sig);text-decoration:none}}
    img{{max-width:100%;display:block}}
    .wrap{{position:relative;z-index:1;display:grid;grid-template-columns:264px 1fr;
      max-width:1240px;margin:0 auto;min-height:100vh}}
    main,.hero-grid>*,.card{{min-width:0}}
    
    /* ---------- sidebar ---------- */
    .side{{position:sticky;top:0;align-self:start;height:100vh;padding:34px 26px;
      border-right:1px solid var(--line);background:linear-gradient(180deg,var(--panel),var(--bg) 90%);
      display:flex;flex-direction:column;gap:30px}}
    .brand .mark{{font-family:var(--mono);font-size:11px;letter-spacing:.22em;color:var(--sig);text-transform:uppercase}}
    .brand h1{{font-family:var(--disp);font-weight:700;font-size:22px;line-height:1.15;margin-top:8px}}
    .brand .role{{font-family:var(--mono);font-size:11.5px;color:var(--mut);margin-top:6px;letter-spacing:.02em}}
    .nav{{list-style:none;position:relative}}
    .nav::before{{content:"";position:absolute;left:4px;top:14px;bottom:14px;width:1px;
      background:linear-gradient(180deg,transparent,var(--line) 12%,var(--line) 88%,transparent)}}
    .nav li a{{display:flex;align-items:center;gap:14px;padding:8px 0;color:var(--mut);
      font-family:var(--mono);font-size:13px;letter-spacing:.02em;transition:color .18s}}
    .nav-node{{width:9px;height:9px;border-radius:50%;border:1px solid var(--line);
      background:var(--bg);flex:0 0 9px;transition:.18s;z-index:1}}
    .nav li a:hover,.nav li a.active{{color:var(--ink)}}
    .nav li a:hover .nav-node,.nav li a.active .nav-node{{border-color:var(--sig);
      background:var(--sig);box-shadow:0 0 0 3px var(--sig-glow)}}
    .status{{margin-top:auto;font-family:var(--mono);font-size:11px;color:var(--dim);
      border-top:1px solid var(--line);padding-top:18px;line-height:2}}
    .status .live{{color:var(--sig)}}
    .status .dot{{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--sig);
      margin-right:7px;box-shadow:0 0 0 3px var(--sig-glow);animation:pulse 2.6s ease-in-out infinite}}
    @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:.4}}}}
    
    /* ---------- main ---------- */
    main{{padding:0 clamp(24px,5vw,72px);display:flex;flex-direction:column;min-height:100vh}}
    section{{padding:76px 0;border-bottom:1px solid var(--line)}}
    section:last-of-type{{border-bottom:0}}
    .eyebrow{{display:flex;align-items:center;gap:10px;font-family:var(--mono);font-size:11.5px;
      letter-spacing:.24em;text-transform:uppercase;color:var(--sig-dim);margin-bottom:22px}}
    .eyebrow::before{{content:"";width:8px;height:8px;border-radius:50%;background:var(--sig);
      box-shadow:0 0 0 3px var(--sig-glow)}}
    h2{{font-family:var(--disp);font-weight:600;font-size:clamp(26px,3.4vw,36px);letter-spacing:-.01em;line-height:1.1}}
    
    /* hero */
    .hero{{padding-top:64px}}
    .hero-grid{{display:grid;grid-template-columns:1.5fr .9fr;gap:44px;align-items:center}}
    .hero h1{{font-family:var(--disp);font-weight:700;font-size:clamp(33px,6vw,62px);
      line-height:1.02;letter-spacing:-.02em}}
    .hero .role{{font-family:var(--mono);color:var(--sig);font-size:15px;margin-top:14px;letter-spacing:.02em}}
    .tags{{display:flex;flex-wrap:wrap;gap:8px;margin:22px 0}}
    .tag{{font-family:var(--mono);font-size:11.5px;letter-spacing:.04em;color:var(--mut);
      border:1px solid var(--line);border-radius:999px;padding:5px 12px;background:var(--panel)}}
    .hero p.bio{{color:var(--mut);max-width:56ch;margin-top:6px}}
    .hero-links{{display:flex;gap:12px;margin-top:26px}}
    .btn{{font-family:var(--mono);font-size:13px;padding:10px 18px;border-radius:8px;
      border:1px solid var(--line);color:var(--ink);transition:.18s;display:inline-flex;gap:8px;align-items:center}}
    .btn:hover{{border-color:var(--sig);color:var(--sig);box-shadow:0 0 0 3px var(--sig-glow)}}
    .btn.primary{{background:var(--sig);color:#04211f;border-color:var(--sig);font-weight:500}}
    .btn.primary:hover{{background:#6bdcd4;box-shadow:0 0 24px var(--sig-glow)}}
    .portrait{{position:relative;border:1px solid var(--line);border-radius:var(--r);overflow:hidden;
      background:var(--panel)}}
    .portrait::after{{content:"";position:absolute;inset:0;
      box-shadow:inset 0 0 60px rgba(0,0,0,.5);pointer-events:none}}
    .portrait img{{width:100%;height:100%;object-fit:cover;object-position:50% 22%}}
    
    /* about + timeline */
    .about-grid{{display:grid;grid-template-columns:1fr 1fr;gap:44px}}
    .about-grid p{{color:var(--mut);margin-bottom:16px;max-width:52ch}}
    .timeline{{list-style:none;position:relative;padding-left:4px}}
    .timeline li{{display:grid;grid-template-columns:88px 22px 1fr;align-items:start;
        gap:0;padding:10px 0}}
    .tl-date{{font-family:var(--mono);font-size:12px;color:var(--sig);padding-top:2px}}
    .tl-node{{position:relative;width:22px;display:flex;justify-content:center}}
    .tl-node::before{{content:"";width:9px;height:9px;border-radius:50%;background:var(--bg);
        border:1px solid var(--sig);margin-top:6px;z-index:1}}
    .timeline li:not(:last-child) .tl-node::after{{content:"";position:absolute;top:12px;bottom:-18px;
        width:1px;background:var(--line);left:50%}}
    .tl-text{{color:var(--mut);font-size:14px}}
    
    /* skills */
    .skills{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}
    .skill-block{{border:1px solid var(--line);border-radius:var(--r);padding:22px 24px;
      background:linear-gradient(180deg,var(--panel),var(--panel-2))}}
    .skill-block h3{{font-family:var(--disp);font-size:16px;font-weight:600;margin-bottom:14px;
      padding-bottom:12px;border-bottom:1px solid var(--line)}}
    .srow{{display:grid;grid-template-columns:118px 1fr;gap:14px;padding:7px 0;align-items:baseline}}
    .sk{{font-family:var(--mono);font-size:11px;letter-spacing:.04em;color:var(--sig-dim);text-transform:uppercase}}
    .sv{{font-size:13.5px;color:var(--ink)}}
    
    /* project cards */
    .cards{{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}}
    .card{{border:1px solid var(--line);border-radius:var(--r);overflow:hidden;background:var(--panel);
      display:flex;flex-direction:column;position:relative;transition:transform .2s,border-color .2s}}
    .card::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:2px;background:var(--sig);
      transform:scaleY(0);transform-origin:top;transition:transform .22s}}
    .card:hover{{transform:translateY(-3px);border-color:var(--sig-dim)}}
    .card:hover::before{{transform:scaleY(1)}}
    .card-media{{aspect-ratio:16/10;overflow:hidden;background:#0a0e13;border-bottom:1px solid var(--line)}}
    .card-media img{{width:100%;height:100%;object-fit:cover;object-position:center;
      filter:saturate(.9) contrast(1.02);transition:transform .3s}}
    .card:hover .card-media img{{transform:scale(1.03)}}
    .card-body{{padding:20px 22px;display:flex;flex-direction:column;gap:10px;flex:1}}
    .card-head{{display:flex;align-items:center;gap:10px;flex-wrap:wrap}}
    .card-head h3{{font-family:var(--disp);font-size:17px;font-weight:600}}
    .feat{{font-family:var(--mono);font-size:9.5px;letter-spacing:.12em;text-transform:uppercase;
      color:var(--warn);border:1px solid var(--warn);border-radius:4px;padding:2px 7px;opacity:.9}}
    .desc{{color:var(--mut);font-size:13.5px}}
    .goal{{font-size:12.5px;color:var(--dim);border-left:1px solid var(--line);padding-left:12px;margin-top:2px}}
    .goal-k{{font-family:var(--mono);font-size:10px;letter-spacing:.1em;text-transform:uppercase;
      color:var(--sig-dim);display:block;margin-bottom:3px}}
    .card-link{{font-family:var(--mono);font-size:12.5px;margin-top:auto;padding-top:6px;
      display:inline-flex;align-items:center;gap:6px;width:fit-content}}
    .card-link .arr{{transition:transform .18s}}
    .card-link:hover .arr{{transform:translate(2px,-2px)}}
    
    /* certs */
    .cert-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}}
    .cert{{border:1px solid var(--line);border-radius:var(--r);padding:20px;background:var(--panel);
      position:relative;transition:border-color .2s}}
    .cert:hover{{border-color:var(--sig-dim)}}
    .cert-dot{{width:8px;height:8px;border-radius:50%;background:var(--sig-dim);margin-bottom:14px;
      box-shadow:0 0 0 3px var(--sig-glow)}}
    .cert h3{{font-family:var(--disp);font-size:15px;font-weight:600;line-height:1.25;min-height:38px}}
    .cert-meta{{display:flex;flex-wrap:wrap;gap:4px 16px;margin:14px 0;font-family:var(--mono);
      font-size:12px;color:var(--ink)}}
    .ck{{color:var(--dim);margin-right:6px;text-transform:uppercase;letter-spacing:.06em;font-size:10px}}
    .cert-actions{{display:flex;gap:16px;font-family:var(--mono);font-size:12px;
      border-top:1px solid var(--line);padding-top:12px}}
    .cred-id{{color:var(--dim);letter-spacing:.02em}}
    
    /* contact */
    .contact-grid{{display:grid;grid-template-columns:1fr 1fr;gap:44px;align-items:start}}
    .contact-lead{{color:var(--mut);max-width:40ch;margin-bottom:26px}}
    .contact-links{{display:flex;flex-direction:column;gap:12px}}
    .clink{{display:flex;align-items:center;gap:14px;border:1px solid var(--line);border-radius:8px;
      padding:14px 18px;background:var(--panel);font-family:var(--mono);font-size:13.5px;
      color:var(--ink);transition:.18s}}
    .clink:hover{{border-color:var(--sig);color:var(--sig);box-shadow:0 0 0 3px var(--sig-glow)}}
    .clink .k{{color:var(--dim);font-size:11px;letter-spacing:.08em;text-transform:uppercase;width:76px}}
    form{{display:flex;flex-direction:column;gap:14px}}
    label{{font-family:var(--mono);font-size:11px;letter-spacing:.08em;text-transform:uppercase;
      color:var(--sig-dim);margin-bottom:-6px}}
    input,select,textarea{{font-family:var(--sans);font-size:14px;background:var(--panel-2);
      border:1px solid var(--line);border-radius:8px;padding:11px 14px;color:var(--ink);width:100%}}
    input:focus,select:focus,textarea:focus{{outline:none;border-color:var(--sig);
      box-shadow:0 0 0 3px var(--sig-glow)}}
    textarea{{resize:vertical;min-height:120px}}
    .form-note{{font-family:var(--mono);font-size:11px;color:var(--dim)}}
    
    footer{{margin-top:auto;padding:30px 0 50px;font-family:var(--mono);font-size:11.5px;color:var(--dim);
      display:flex;justify-content:space-between;flex-wrap:wrap;gap:10px}}
    
    /* mobile */
    .menu-btn{{display:none}}
    @media(max-width:900px){{
      .wrap{{grid-template-columns:1fr}}
      .side{{position:fixed;inset:0 auto 0 0;width:250px;height:100vh;z-index:40;
        transform:translateX(-100%);transition:transform .25s;box-shadow:0 0 40px rgba(0,0,0,.6)}}
      .side.open{{transform:none}}
      .menu-btn{{display:flex;position:fixed;top:16px;right:16px;z-index:50;width:44px;height:44px;
        border:1px solid var(--line);border-radius:8px;background:var(--panel);color:var(--sig);
        align-items:center;justify-content:center;font-family:var(--mono);cursor:pointer}}
      main{{padding-top:20px}}
      .hero-grid,.about-grid,.skills,.cards,.contact-grid{{grid-template-columns:1fr}}
      .cert-grid{{grid-template-columns:1fr 1fr}}
      .portrait{{max-width:280px;order:-1}}
    }}
    @media(max-width:560px){{.cert-grid{{grid-template-columns:1fr}}}}
    @media(prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important;scroll-behavior:auto}}}}
    
    .reveal{{opacity:0;transform:translateY(14px);transition:opacity .5s,transform .5s}}
    .reveal.in{{opacity:1;transform:none}}
    </style>
    </head>
    <body>
    <button class="menu-btn" id="menuBtn" aria-label="Toggle navigation">MENU</button>
    <div class="wrap">
      <aside class="side" id="side">
        <div class="brand">
          <div class="mark">// network engineer</div>
          <h1>{NAME}</h1>
          <div class="role">Network &amp; Automation</div>
        </div>
        <ul class="nav" id="nav">{nav_for(active)}</ul>
        <div class="status">
          <div><span class="dot"></span><span class="live">OPEN TO OPPORTUNITIES</span></div>
          <div>USMC VETERAN &middot; SECRET CLEARED</div>
          <div>B.S. NETWORK ENG &amp; SECURITY</div>
        </div>
      </aside>
    <main>
     {main_content}  
    <footer>
         <span>&copy; 2026 {NAME}</span>
     </footer>
    </main>
    </div>

    <script>
    // mobile nav
    const side=document.getElementById('side'),btn=document.getElementById('menuBtn');
    btn.addEventListener('click',()=>side.classList.toggle('open'));
    document.querySelectorAll('#nav a').forEach(a=>a.addEventListener('click',()=>side.classList.remove('open')));
    // scroll reveal + active nav
    const io=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting){{e.target.classList.add('in');io.unobserve(e.target)}}}}),{{threshold:.04}});
    document.querySelectorAll('.reveal').forEach(el=>io.observe(el));
    const secs=[...document.querySelectorAll('section')],links=[...document.querySelectorAll('#nav a')];
    const spy=new IntersectionObserver(es=>es.forEach(e=>{{if(e.isIntersecting){{
      links.forEach(l=>l.classList.toggle('active',l.getAttribute('href')==='#'+e.target.id));}}}}),{{rootMargin:'-45% 0px -50% 0px'}});
    secs.forEach(s=>spy.observe(s));
    </script>
    </body>
    </html>
    """
    return html_page

CONTENT = {
    "index":     index_content,
    "about":    about_content,
    "skills":      skills_content,
    "network":     network_content,
    "python":      python_content,
    "credentials": credentials_content,
    "contact":     contact_content,
}

OUT.mkdir(parents=True, exist_ok=True)
for i,label in NAV:
    html_out = render_page(CONTENT[i], i)
    (OUT / f"{i}.html").write_text(html_out, encoding="utf-8")
    print(f"Wrote {OUT/ f'{i}.html'}  ({len(f"{i}_content"):,} bytes)")
print(f"Network projects: {len(net_df)} | Python projects: {len(py_df)} | Certs: {len(cert_df)}")
