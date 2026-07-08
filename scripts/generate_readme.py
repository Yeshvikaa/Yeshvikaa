#!/usr/bin/env python3
"""
Elite GitHub Profile README Generator
Automatically fetches repository data and generates a premium README.
"""

import os
import sys
import json
import re
import requests
from datetime import datetime, timezone
from collections import defaultdict

# ─── CONFIG ───────────────────────────────────────────────────────────────────
GITHUB_TOKEN = os.environ.get("GH_TOKEN", "")
USERNAME = os.environ.get("GITHUB_USERNAME", "Yeshvikaa")
TEMPLATE_PATH = os.path.join(os.path.dirname(__file__), "..", "templates", "README.template.md")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "README.md")

HEADERS = {
    "Accept": "application/vnd.github+json",
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"token {GITHUB_TOKEN}"

# ─── DETECTION MAPS ───────────────────────────────────────────────────────────
LANG_ICON_MAP = {
    "Python": "python", "JavaScript": "javascript", "TypeScript": "typescript",
    "Kotlin": "kotlin", "Java": "java", "PHP": "php", "SQL": "mysql",
    "C++": "cpp", "C": "c", "Go": "go", "Rust": "rust", "Swift": "swift",
    "Dart": "dart", "Ruby": "ruby", "Shell": "bash",
}

FRAMEWORK_KEYWORDS = {
    "react": "React", "next": "Next.js", "vue": "Vue.js", "angular": "Angular",
    "django": "Django", "flask": "Flask", "fastapi": "FastAPI", "express": "Express.js",
    "spring": "Spring Boot", "node": "Node.js", "flutter": "Flutter",
    "retrofit": "Retrofit", "tensorflow": "TensorFlow", "pytorch": "PyTorch",
    "opencv": "OpenCV", "yolo": "YOLO", "firebase": "Firebase",
    "mongodb": "MongoDB", "mysql": "MySQL", "postgres": "PostgreSQL",
    "sqlite": "SQLite", "docker": "Docker", "kubernetes": "Kubernetes",
    "aws": "AWS", "azure": "Azure", "gcp": "GCP",
    "tailwind": "Tailwind CSS", "bootstrap": "Bootstrap",
}

CATEGORY_RULES = {
    "🤖 AI & Machine Learning": ["ai", "ml", "machine", "model", "predict", "neural", "deep", "learn",
                                   "tensorflow", "pytorch", "yolo", "opencv", "face", "recognition", "nlp"],
    "📱 Android Development": ["app", "android", "kotlin", "jetpack", "retrofit", "mvvm", "mobile"],
    "🌐 Full Stack Web": ["website", "web", "frontend", "backend", "fullstack", "next", "react",
                          "vue", "angular", "node", "express", "mind_vault", "mind-match",
                          "skin-journey", "xephora", "moodmusic", "food_bridge", "focus_shield",
                          "mind_dump", "mind_guard", "BOEW", "attendance"],
    "⚙️ Backend Systems": ["backend", "api", "server", "flask", "fastapi", "django",
                            "spring", "rest", "graphql"],
    "🔬 Healthcare & Research": ["health", "medical", "care", "scan", "endo", "maxillo",
                                  "histo", "lifescan", "quantum", "clinical"],
    "📊 Data & Analytics": ["data", "analytics", "dashboard", "report", "power", "tableau",
                             "chart", "visual", "tracking", "attendance"],
    "🛠️ Automation & Tools": ["automation", "tool", "script", "workflow", "ci", "cd",
                               "action", "deploy", "pipeline", "trackaroo", "track"],
}

PROFESSIONAL_DESCRIPTIONS = {
    "mind_guard": "Enterprise-grade mental wellness platform with comprehensive testing infrastructure (330+ automated test cases), real-time security monitoring, and multi-layer CI/CD pipeline using TypeScript/Next.js ecosystem.",
    "mind-match": "AI-powered cognitive assessment platform featuring adaptive difficulty algorithms, real-time performance analytics, and gamified mental health evaluation built with modern JavaScript.",
    "xephora": "Cutting-edge beauty-tech e-commerce platform with AI-driven product recommendations, personalized skincare analysis, and seamless checkout experience leveraging JavaScript.",
    "skin-journey2": "Advanced dermatological tracking application featuring AI-powered skin analysis, treatment progress monitoring, and personalized skincare regimen management with React.",
    "skin-journey": "Progressive web application for personalized skincare journeys, incorporating computer vision-based skin condition assessment and treatment recommendation engine.",
    "focus_shield_project": "Intelligent productivity and digital wellness platform with adaptive focus sessions, distraction blocking, and behavioral analytics to optimize cognitive performance.",
    "mind_dump": "Full-stack knowledge management platform built with TypeScript/Next.js, featuring AI-powered content organization, semantic search, and collaborative note-taking capabilities.",
    "BOEW": "Back of Envelope Web — rapid prototyping and feasibility calculation tool for engineers and product managers, enabling quick technical scoping with beautiful visualization.",
    "attendance_face_recognition": "Production-ready facial recognition attendance system with real-time biometric identification, anti-spoofing measures, and automated reporting dashboard.",
    "moodmusic": "Emotion-aware music recommendation engine leveraging sentiment analysis and user behavior patterns to curate personalized playlists that match psychological states.",
    "food_bridge": "Community-driven food redistribution platform connecting surplus food donors with hunger relief organizations, featuring intelligent logistics routing built with Python/Flask.",
    "mind_vault_website": "Professional portfolio and knowledge vault website built with TypeScript/Next.js, showcasing projects with interactive visualizations and dynamic content management.",
    "school_assessment_backend": "Scalable academic assessment management system with automated test generation, adaptive evaluation engine, and comprehensive analytics for educators. Python/FastAPI + SQLite.",
    "pinsight_backend": "RESTful API backend for the Pinsight learning platform, implementing JWT authentication, role-based access control, video tracking, and adaptive assessment workflows with Python/Flask.",
    "pinsight_app": "Android Kotlin application for structured learning featuring MVVM architecture, video lesson playback tracking, pre/post assessment modules, and Retrofit-based API integration.",
    "pinsight_app_backend": "Laravel PHP backend providing robust API infrastructure for the Pinsight e-learning platform with comprehensive CRUD operations and real-time progress tracking.",
    "endo_lifescan_app": "Medical-grade endoscopy scan management Android app with Kotlin, enabling clinical image capture, AI-assisted analysis, and secure patient data management through MVVM architecture.",
    "endo_lifescan_app_backend": "Python FastAPI backend for the EndoLifeScan medical platform, implementing secure medical image storage, patient record management, and diagnostic report generation.",
    "trackaroo_app": "Full-featured expense and activity tracking Android application built with Kotlin, featuring intuitive UX, real-time synchronization, offline-first architecture, and insightful spending analytics.",
    "trackaroo_app_backend": "PHP Laravel backend powering the Trackaroo tracking platform with RESTful APIs, secure authentication, and comprehensive financial data management endpoints.",
    "histoquanta_app": "Android application for histological data quantification in medical research, enabling precise cellular analysis, statistical reporting, and research data export via Kotlin/MVVM.",
    "histoquanta_app_backend": "PHP backend system for the HistoQuanta medical research platform, providing secure data storage, analytical computation APIs, and research report generation.",
    "maxillocare_app": "Specialized Android application for maxillofacial care management built with Kotlin, featuring patient tracking, treatment planning, appointment scheduling, and clinical progress monitoring.",
    "maxillocare_app_backend": "PHP-based RESTful backend for the MaxilloCare dental platform with patient management, appointment scheduling APIs, and clinical data security compliance.",
    "spark_app_backend": "Enterprise-grade PHP backend for the Spark social platform with scalable API architecture, real-time notifications, and comprehensive user engagement features.",
    "spark_backend": "Python microservices backend for Spark platform, implementing event-driven architecture, message queuing, and high-performance data processing pipelines.",
    "spark_app": "Feature-rich social interaction platform with real-time messaging, content discovery, and community building capabilities leveraging modern mobile architecture.",
}

# ─── API HELPERS ──────────────────────────────────────────────────────────────

def get_user_info():
    url = f"https://api.github.com/users/{USERNAME}"
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    return r.json()

def get_all_repos():
    repos = []
    page = 1
    while True:
        url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}&sort=updated"
        r = requests.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return [r for r in repos if not r.get("archived") and r["name"] != USERNAME]

def get_repo_languages(repo_name):
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/languages"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception:
        return {}

def get_commit_count(repo_name, default_branch="main"):
    url = f"https://api.github.com/repos/{USERNAME}/{repo_name}/commits?per_page=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if "Link" in r.headers:
            last = r.headers["Link"].split(",")[-1]
            m = re.search(r"page=(\d+)", last)
            if m:
                return int(m.group(1))
        commits = r.json()
        return len(commits) if isinstance(commits, list) else 0
    except Exception:
        return 0

# ─── CATEGORIZATION ───────────────────────────────────────────────────────────

def categorize_repo(repo):
    name = repo["name"].lower()
    desc = (repo.get("description") or "").lower()
    lang = (repo.get("language") or "").lower()
    topics = [t.lower() for t in repo.get("topics", [])]
    
    text = f"{name} {desc} {lang} {' '.join(topics)}"
    
    for category, keywords in CATEGORY_RULES.items():
        for kw in keywords:
            if kw in text:
                return category
    return "🛠️ Automation & Tools"

def detect_frameworks(repo_name, languages, description=""):
    detected = []
    name_lower = repo_name.lower()
    desc_lower = (description or "").lower()
    lang_names = [l.lower() for l in languages.keys()]
    
    combined = f"{name_lower} {desc_lower} {' '.join(lang_names)}"
    
    for kw, framework in FRAMEWORK_KEYWORDS.items():
        if kw in combined:
            detected.append(framework)
    
    return list(set(detected))

def get_tech_badge(tech):
    badges = {
        "Python": "https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white",
        "JavaScript": "https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black",
        "TypeScript": "https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white",
        "Kotlin": "https://img.shields.io/badge/Kotlin-7F52FF?style=flat&logo=kotlin&logoColor=white",
        "PHP": "https://img.shields.io/badge/PHP-777BB4?style=flat&logo=php&logoColor=white",
        "Java": "https://img.shields.io/badge/Java-ED8B00?style=flat&logo=openjdk&logoColor=white",
        "React": "https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black",
        "Next.js": "https://img.shields.io/badge/Next.js-000000?style=flat&logo=nextdotjs&logoColor=white",
        "Flask": "https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white",
        "FastAPI": "https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white",
        "Firebase": "https://img.shields.io/badge/Firebase-FFCA28?style=flat&logo=firebase&logoColor=black",
        "MongoDB": "https://img.shields.io/badge/MongoDB-47A248?style=flat&logo=mongodb&logoColor=white",
        "MySQL": "https://img.shields.io/badge/MySQL-4479A1?style=flat&logo=mysql&logoColor=white",
        "PostgreSQL": "https://img.shields.io/badge/PostgreSQL-316192?style=flat&logo=postgresql&logoColor=white",
        "SQLite": "https://img.shields.io/badge/SQLite-07405E?style=flat&logo=sqlite&logoColor=white",
        "Docker": "https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white",
        "TensorFlow": "https://img.shields.io/badge/TensorFlow-FF6F00?style=flat&logo=tensorflow&logoColor=white",
        "PyTorch": "https://img.shields.io/badge/PyTorch-EE4C2C?style=flat&logo=pytorch&logoColor=white",
        "OpenCV": "https://img.shields.io/badge/OpenCV-5C3EE8?style=flat&logo=opencv&logoColor=white",
        "Node.js": "https://img.shields.io/badge/Node.js-339933?style=flat&logo=nodedotjs&logoColor=white",
        "Express.js": "https://img.shields.io/badge/Express.js-000000?style=flat&logo=express&logoColor=white",
        "Vue.js": "https://img.shields.io/badge/Vue.js-4FC08D?style=flat&logo=vuedotjs&logoColor=white",
        "Angular": "https://img.shields.io/badge/Angular-DD0031?style=flat&logo=angular&logoColor=white",
        "Flutter": "https://img.shields.io/badge/Flutter-02569B?style=flat&logo=flutter&logoColor=white",
        "AWS": "https://img.shields.io/badge/AWS-232F3E?style=flat&logo=amazonaws&logoColor=white",
        "Azure": "https://img.shields.io/badge/Azure-0078D4?style=flat&logo=microsoftazure&logoColor=white",
        "GCP": "https://img.shields.io/badge/GCP-4285F4?style=flat&logo=googlecloud&logoColor=white",
        "Retrofit": "https://img.shields.io/badge/Retrofit-48B983?style=flat&logo=android&logoColor=white",
        "Spring Boot": "https://img.shields.io/badge/Spring_Boot-6DB33F?style=flat&logo=springboot&logoColor=white",
        "Django": "https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white",
        "Tailwind CSS": "https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=flat&logo=tailwindcss&logoColor=white",
    }
    return badges.get(tech, "")

# ─── PROJECT CARD BUILDER ─────────────────────────────────────────────────────

def build_project_card(repo, languages, commit_count):
    name = repo["name"]
    url = repo["html_url"]
    lang = repo.get("language") or "Multi-Language"
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    updated = repo.get("updated_at", "")[:10]
    
    desc = PROFESSIONAL_DESCRIPTIONS.get(name, repo.get("description") or f"A professional {lang} project showcasing modern software engineering practices.")
    frameworks = detect_frameworks(name, languages, desc)
    
    # Build tech stack line
    tech_items = list(languages.keys())[:3]
    if frameworks:
        tech_items += frameworks[:2]
    tech_stack = " • ".join(tech_items) if tech_items else lang
    
    # Status badge
    days_since = 0
    try:
        updated_dt = datetime.fromisoformat(repo.get("updated_at", "").replace("Z", "+00:00"))
        days_since = (datetime.now(timezone.utc) - updated_dt).days
    except Exception:
        pass
    
    if days_since < 30:
        status = "🟢 **Active Development**"
    elif days_since < 180:
        status = "🟡 **Maintained**"
    else:
        status = "🔵 **Stable**"
    
    commits_str = f"{commit_count}+" if commit_count else "N/A"
    
    card = f"""<details>
<summary><b>🔹 {name.replace('_', ' ').replace('-', ' ').title()}</b> &nbsp;·&nbsp; <code>{lang}</code> &nbsp;·&nbsp; ⭐ {stars} &nbsp; 🍴 {forks}</summary>

<br>

> {desc}

| Attribute | Details |
|-----------|---------|
| **Tech Stack** | `{tech_stack}` |
| **Language** | `{lang}` |
| **Commits** | `{commits_str}` |
| **Last Updated** | `{updated}` |
| **Status** | {status} |

**🔗 [View Repository]({url})**

---

</details>"""
    return card

# ─── TECH STACK BUILDER ───────────────────────────────────────────────────────

def build_tech_section(all_languages, all_frameworks):
    def skill_icon(name_lower):
        return f"https://skillicons.dev/icons?i={name_lower}"
    
    lang_badges = []
    for lang in sorted(all_languages):
        icon_key = LANG_ICON_MAP.get(lang)
        if icon_key:
            lang_badges.append(f'<img src="{skill_icon(icon_key)}" height="40" alt="{lang}" />')
    
    fw_badge_map = {
        "React": "react", "Next.js": "nextjs", "Node.js": "nodejs", "Express.js": "express",
        "Django": "django", "Flask": "flask", "FastAPI": "fastapi", "Vue.js": "vue",
        "Angular": "angular", "Flutter": "flutter", "Spring Boot": "spring",
        "TensorFlow": "tensorflow", "PyTorch": "pytorch", "Firebase": "firebase",
        "MongoDB": "mongodb", "MySQL": "mysql", "PostgreSQL": "postgres",
        "SQLite": "sqlite", "Docker": "docker", "AWS": "aws", "Azure": "azure",
        "GCP": "gcp", "Kotlin": "kotlin",
    }
    
    fw_badges = []
    for fw in sorted(all_frameworks):
        icon_key = fw_badge_map.get(fw)
        if icon_key:
            fw_badges.append(f'<img src="{skill_icon(icon_key)}" height="40" alt="{fw}" />')
    
    lang_row = "\n".join(lang_badges) if lang_badges else "<!-- no languages -->"
    fw_row = "\n".join(fw_badges) if fw_badges else "<!-- no frameworks -->"
    
    return lang_row, fw_row

# ─── MAIN README BUILDER ──────────────────────────────────────────────────────

def write_local_svg_assets():
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    header_content = """<svg xmlns="http://www.w3.org/2000/svg" width="800" height="220" viewBox="0 0 800 220">
  <defs>
    <linearGradient id="violet-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#4C1D95" />
      <stop offset="70%" stop-color="#1E1B4B" />
      <stop offset="100%" stop-color="#0F172A" />
    </linearGradient>
    <linearGradient id="accent-grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#C084FC" />
      <stop offset="50%" stop-color="#F472B6" />
      <stop offset="100%" stop-color="#60A5FA" />
    </linearGradient>
    <style>
      .name-label {
        font-family: 'Segoe UI', -apple-system, system-ui, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 900;
        font-size: 40px;
        fill: url(#accent-grad);
      }
      .title-label {
        font-family: 'Segoe UI', -apple-system, system-ui, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 700;
        font-size: 16px;
        fill: #E2E8F0;
        letter-spacing: 3px;
        text-transform: uppercase;
      }
      .tagline-label {
        font-family: 'Segoe UI', -apple-system, system-ui, BlinkMacSystemFont, Roboto, sans-serif;
        font-size: 14px;
        fill: #94A3B8;
      }
    </style>
  </defs>
  
  <!-- Main Background -->
  <rect width="800" height="220" rx="15" fill="url(#violet-grad)" />
  
  <!-- Subtle Grid Pattern for tech feel -->
  <path d="M 0,20 L 800,20 M 0,40 L 800,40 M 0,60 L 800,60 M 0,80 L 800,80 M 0,100 L 800,100 M 0,120 L 800,120 M 0,140 L 800,140 M 0,160 L 800,160 M 0,180 L 800,180 M 0,200 L 800,200" stroke="#4F46E5" stroke-opacity="0.07" stroke-width="1" />
  <path d="M 50,0 L 50,220 M 100,0 L 100,220 M 150,0 L 150,220 M 200,0 L 200,220 M 250,0 L 250,220 M 300,0 L 300,220 M 350,0 L 350,220 M 400,0 L 400,220 M 450,0 L 450,220 M 500,0 L 500,220 M 550,0 L 550,220 M 600,0 L 600,220 M 650,0 L 650,220 M 700,0 L 700,220 M 750,0 L 750,220" stroke="#4F46E5" stroke-opacity="0.07" stroke-width="1" />

  <!-- Accent visual elements -->
  <circle cx="700" cy="80" r="100" fill="#7C3AED" fill-opacity="0.15" filter="blur(20px)" />
  <circle cx="680" cy="120" r="50" fill="#EC4899" fill-opacity="0.1" filter="blur(15px)" />
  
  <!-- Decorative Code Bracket Icon on right -->
  <path d="M 690,70 L 670,90 L 690,110 M 710,70 L 730,90 L 710,110" stroke="url(#accent-grad)" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round" opacity="0.6" stroke-opacity="0.7" />

  <!-- Info Box -->
  <text x="50" y="85" class="name-label">Yeshvikaa H</text>
  <text x="50" y="125" class="title-label">Software Engineer • AI &amp; Mobile Developer</text>
  <text x="50" y="160" class="tagline-label">Building secure, production-grade applications &amp; ML pipelines</text>
  <text x="50" y="180" class="tagline-label">Kotlin (Android) | Python (FastAPI/Flask) | Next.js (TypeScript) | Laravel</text>
</svg>"""

    typing_content = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 40" width="600" height="40">
  <defs>
    <style>
      .text-animate {
        font-family: 'Segoe UI', -apple-system, system-ui, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 700;
        font-size: 18px;
        fill: #C084FC;
        text-anchor: middle;
      }
    </style>
  </defs>
  <text x="50%" y="25" class="text-animate">
    Building Intelligent Mobile &amp; Web Systems 🚀
    <animate attributeName="opacity" values="0.4;1;0.4" dur="4s" repeatCount="indefinite" />
  </text>
</svg>"""

    with open(os.path.join(assets_dir, "header.svg"), "w", encoding="utf-8") as f:
        f.write(header_content)
    with open(os.path.join(assets_dir, "typing.svg"), "w", encoding="utf-8") as f:
        f.write(typing_content)
    print("[INFO] Local SVG assets created successfully.")

def write_analytics_svg(total_repos, total_stars, total_forks, language_bytes):
    assets_dir = os.path.join(os.path.dirname(__file__), "..", "assets")
    os.makedirs(assets_dir, exist_ok=True)
    
    LANG_COLORS = {
        "Python": "#3776AB",
        "JavaScript": "#F7DF1E",
        "TypeScript": "#3178C6",
        "Kotlin": "#7F52FF",
        "PHP": "#777BB4",
        "Java": "#ED8B00",
        "CSS": "#563D7C",
        "HTML": "#E34F26",
        "PowerShell": "#012456",
        "SQL": "#E38A00",
        "C++": "#F34B7D",
        "C": "#555555",
        "Shell": "#89E051",
    }
    
    total_bytes = sum(language_bytes.values())
    languages_svg_items = []
    y_offset = 88
    if total_bytes > 0:
        sorted_langs = sorted(language_bytes.items(), key=lambda x: x[1], reverse=True)[:6]
        for lang_name, byte_count in sorted_langs:
            percentage = (byte_count / total_bytes) * 100
            lang_color = LANG_COLORS.get(lang_name, "#6E7681")
            bar_width = int((percentage / 100) * 330) # maximum width of 330px
            
            lang_item = f"""
  <!-- {lang_name} -->
  <text x="420" y="{y_offset}" class="lang-lbl">{lang_name}</text>
  <text x="750" y="{y_offset}" class="lang-percent" text-anchor="end">{percentage:.1f}%</text>
  <rect x="420" y="{y_offset + 8}" width="330" height="8" rx="4" fill="#1E293B" />
  <rect x="420" y="{y_offset + 8}" width="{bar_width}" height="8" rx="4" fill="{lang_color}" />"""
            languages_svg_items.append(lang_item)
            y_offset += 45
            
    languages_svg_str = "\n".join(languages_svg_items)
    
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="360" viewBox="0 0 800 360">
  <defs>
    <linearGradient id="violet-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2D1B4E" />
      <stop offset="70%" stop-color="#14112E" />
      <stop offset="100%" stop-color="#0B091A" />
    </linearGradient>
    <style>
      .card-title {{
        font-family: 'Segoe UI', -apple-system, system-ui, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 700;
        font-size: 18px;
        fill: #C084FC;
        letter-spacing: 1px;
      }}
      .stat-val {{
        font-family: 'Segoe UI', -apple-system, system-ui, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 800;
        font-size: 24px;
        fill: #F3F4F6;
      }}
      .stat-lbl {{
        font-family: 'Segoe UI', -apple-system, system-ui, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 500;
        font-size: 13px;
        fill: #9CA3AF;
      }}
      .lang-lbl {{
        font-family: 'Segoe UI', -apple-system, system-ui, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 600;
        font-size: 13px;
        fill: #E5E7EB;
      }}
      .lang-percent {{
        font-family: 'Segoe UI', -apple-system, system-ui, BlinkMacSystemFont, Roboto, sans-serif;
        font-weight: 700;
        font-size: 13px;
        fill: #A78BFA;
      }}
    </style>
  </defs>

  <!-- Background -->
  <rect width="800" height="360" rx="15" fill="url(#violet-grad)" stroke="#4C1D95" stroke-opacity="0.3" stroke-width="1.5" />

  <!-- Left Section (Stats) -->
  <text x="40" y="45" class="card-title">📊 GitHub Analytics</text>

  <!-- Repo Stat Box -->
  <rect x="40" y="75" width="310" height="70" rx="10" fill="#161334" fill-opacity="0.7" stroke="#4C1d95" stroke-opacity="0.2" stroke-width="1" />
  <!-- Repo Icon -->
  <g transform="translate(60, 93)" stroke="#A78BFA" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
  </g>
  <text x="105" y="105" class="stat-val">{total_repos}</text>
  <text x="105" y="125" class="stat-lbl">Public Repositories</text>

  <!-- Stars Stat Box -->
  <rect x="40" y="160" width="310" height="70" rx="10" fill="#161334" fill-opacity="0.7" stroke="#4C1d95" stroke-opacity="0.2" stroke-width="1" />
  <!-- Star Icon -->
  <g transform="translate(60, 178)" stroke="#FBBF24" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
  </g>
  <text x="105" y="190" class="stat-val">{total_stars}</text>
  <text x="105" y="210" class="stat-lbl">Total Stars Received</text>

  <!-- Forks Stat Box -->
  <rect x="40" y="245" width="310" height="70" rx="10" fill="#161334" fill-opacity="0.7" stroke="#4C1D95" stroke-opacity="0.2" stroke-width="1" />
  <!-- Fork Icon -->
  <g transform="translate(60, 263)" stroke="#60A5FA" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="18" r="3"></circle>
    <circle cx="6" cy="6" r="3"></circle>
    <circle cx="18" cy="6" r="3"></circle>
    <path d="M18 9v2a6 6 0 0 1-12 0V9M12 15V11"></path>
  </g>
  <text x="105" y="275" class="stat-val">{total_forks}</text>
  <text x="105" y="295" class="stat-lbl">Total Forks Created</text>

  <!-- Vertical Divider -->
  <line x1="390" y1="40" x2="390" y2="320" stroke="#4C1D95" stroke-opacity="0.2" stroke-width="1.5" />

  <!-- Right Section (Languages) -->
  <text x="420" y="45" class="card-title">⚡ Languages Distribution</text>
{languages_svg_str}
</svg>"""
    
    with open(os.path.join(assets_dir, "analytics.svg"), "w", encoding="utf-8") as f:
        f.write(svg_content)
    print("[INFO] Analytics SVG asset created successfully.")


def build_readme(user, repos):
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total_repos = len(repos)
    
    # Aggregate stats
    all_languages = set()
    all_frameworks = set()
    categorized = defaultdict(list)
    language_bytes = defaultdict(int)
    total_stars = 0
    total_forks = 0
    
    for repo in repos:
        total_stars += repo.get("stargazers_count", 0)
        total_forks += repo.get("forks_count", 0)
        
        lang = repo.get("language")
        if lang:
            all_languages.add(lang)
        
        languages = get_repo_languages(repo["name"])
        all_languages.update(languages.keys())
        
        for lang_name, byte_count in languages.items():
            language_bytes[lang_name] += byte_count
            
        frameworks = detect_frameworks(repo["name"], languages, repo.get("description", ""))
        all_frameworks.update(frameworks)
        
        category = categorize_repo(repo)
        categorized[category].append((repo, languages))
    
    lang_icons, fw_icons = build_tech_section(all_languages, all_frameworks)
    
    # Build featured projects (top 8 by size)
    top_repos = sorted(repos, key=lambda r: r.get("size", 0), reverse=True)[:8]
    featured_cards = []
    for repo in top_repos:
        if repo["name"] in ["sample", "spark_app", "spark_backend"]:
            continue
        langs = get_repo_languages(repo["name"])
        commits = get_commit_count(repo["name"])
        card = build_project_card(repo, langs, commits)
        featured_cards.append(card)
    
    # Build category sections
    category_sections = []
    for cat, repo_list in sorted(categorized.items()):
        if not repo_list:
            continue
        section_lines = [f"\n### {cat}\n"]
        for repo, languages in repo_list:
            if repo["name"] in ["sample", "Yeshvikaa"]:
                continue
            lang = repo.get("language") or "Multi"
            url = repo["html_url"]
            name_fmt = repo["name"].replace("_", " ").replace("-", " ").title()
            desc_short = PROFESSIONAL_DESCRIPTIONS.get(repo["name"], repo.get("description") or f"Professional {lang} project")
            desc_short = desc_short[:120] + "..." if len(desc_short) > 120 else desc_short
            section_lines.append(f"- **[{name_fmt}]({url})** — {desc_short}")
        category_sections.append("\n".join(section_lines))
    
    write_analytics_svg(total_repos, total_stars, total_forks, language_bytes)
    
    profile_stats = f"""<div align="center">
  <img src="https://raw.githubusercontent.com/Yeshvikaa/Yeshvikaa/main/assets/analytics.svg" width="100%" alt="GitHub Analytics"/>
</div>"""

    # Read template
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()
    
    featured_str = "\n\n".join(featured_cards[:6])
    category_str = "\n".join(category_sections)
    
    readme = template\
        .replace("{{USERNAME}}", USERNAME)\
        .replace("{{TOTAL_REPOS}}", str(total_repos))\
        .replace("{{TOTAL_LANGUAGES}}", str(len(all_languages)))\
        .replace("{{LANG_ICONS}}", lang_icons)\
        .replace("{{FRAMEWORK_ICONS}}", fw_icons)\
        .replace("{{FEATURED_PROJECTS}}", featured_str)\
        .replace("{{ALL_PROJECTS}}", category_str)\
        .replace("{{PROFILE_STATS}}", profile_stats)\
        .replace("{{LAST_UPDATED}}", now)
    
    return readme

# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

def main():
    print(f"[INFO] Fetching data for @{USERNAME}...")
    
    try:
        user = get_user_info()
        print(f"[INFO] User found: {user.get('name', USERNAME)}")
    except Exception as e:
        print(f"[ERROR] Could not fetch user: {e}")
        user = {"login": USERNAME, "name": USERNAME}
    
    try:
        repos = get_all_repos()
        print(f"[INFO] Found {len(repos)} public repositories")
    except Exception as e:
        print(f"[ERROR] Could not fetch repos: {e}")
        sys.exit(1)
        
    write_local_svg_assets() # Generate local header.svg and typing.svg
    
    print("[INFO] Building README...")
    readme_content = build_readme(user, repos)
    
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print(f"[SUCCESS] README.md generated at {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
