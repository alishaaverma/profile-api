"""Profile content shown on the cards.

Everything that comes from GitHub (name, location, repos, stars, followers,
commits, PRs, issues, contribution calendar, activity) is fetched live.
Everything below is your own static content - edit it freely.
"""

import os

GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "alishaaverma")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

# Seconds that GitHub's image proxy / CDN may cache a card. Lower = fresher.
CACHE_SECONDS = int(os.getenv("CACHE_SECONDS", "1800"))

PROFILE = {
    # Leave empty to use the live name from GitHub.
    "name": os.getenv("PROFILE_NAME", ""),
    "role": "Full Stack Software Developer",
    "tagline": (
        "I build complete digital products — from modern user interfaces and "
        "scalable backend systems to databases, cloud infrastructure and "
        "production deployments."
    ),
    "about_subtitle": "Full Stack Developer | Problem Solver | Continuous Learner",
    "about": (
        "I'm a Full Stack Software Developer with experience in building web "
        "applications, REST APIs, admin dashboards and cloud-based solutions. "
        "I enjoy turning ideas into real products with clean code, scalable "
        "architecture and user-focused design."
    ),
    # Set to a number to override; None = years since GitHub account creation.
    "years_experience": None,
    "available": True,
    "chips": ["Frontend", "Backend", "APIs", "Databases", "Cloud", "DevOps"],
    "terminal_lines": [
        "Building Web Applications",
        "Creating Scalable APIs",
        "Solving Real-world Problems",
        "Open to Collaboration",
        "Always Learning...",
    ],
    "neon_words": ["Code", "Design", "Develop", "Deploy", "Repeat"],
    "highlights": [
        "Clean Code",
        "Scalable Systems",
        "Modern UI/UX",
        "REST APIs",
        "Database Design",
        "Cloud Deployment",
    ],
    "capabilities": [
        ("Frontend", "Responsive modern UIs"),
        ("Backend", "Scalable server logic"),
        ("Database", "MongoDB, PostgreSQL"),
        ("Cloud", "AWS, S3, Lambda, EC2"),
        ("Admin & CMS", "WordPress, Woo"),
        ("API Integration", "Third-party APIs"),
    ],
}

# name, short label, brand colour
TECH_STACK = {
    "Frontend": [
        ("HTML5", "5", "#E34F26"),
        ("CSS3", "3", "#1572B6"),
        ("JavaScript", "JS", "#F7DF1E"),
        ("TypeScript", "TS", "#3178C6"),
        ("React", "⚛", "#61DAFB"),
        ("Vite", "V", "#A259FF"),
        ("Tailwind", "TW", "#38BDF8"),
    ],
    "Backend": [
        ("Python", "Py", "#3776AB"),
        ("FastAPI", "⚡", "#05998B"),
        ("Django", "dj", "#44B78B"),
        ("DRF", "DRF", "#E2412B"),
        ("Java", "J", "#F89820"),
    ],
    "Database": [
        ("MongoDB", "M", "#47A248"),
        ("PostgreSQL", "PG", "#4169E1"),
        ("Redis", "R", "#DC382D"),
    ],
    "Cloud & DevOps": [
        ("AWS", "aws", "#FF9900"),
        ("S3", "S3", "#569A31"),
        ("Lambda", "λ", "#FF9900"),
        ("EC2", "EC2", "#F58534"),
        ("Docker", "D", "#2496ED"),
        ("Git", "G", "#F05032"),
        ("GitHub", "GH", "#E6EDF3"),
    ],
    "CMS & Tools": [
        ("WordPress", "W", "#21759B"),
        ("Elementor", "E", "#D63384"),
        ("WooCommerce", "Wo", "#96588A"),
        ("VS Code", "VS", "#007ACC"),
    ],
}

WHAT_I_BUILD = [
    ("Web Applications", "Modern, responsive, high performance web apps"),
    ("REST APIs", "Secure and scalable APIs for web and mobile"),
    ("Backend Systems", "Business logic, auth, background processing"),
    ("Admin Dashboards", "Manage content, users and application data"),
    ("Cloud Solutions", "Deploy, scale and monitor on AWS"),
    ("CMS Development", "WordPress, Elementor, WooCommerce"),
]

# Optional: pin repos by name. Empty = pick automatically (stars, then recent push).
FEATURED_REPOS: list[str] = []

ARCHITECTURE = {
    "client": ("Client", "Browser / User"),
    "frontend": ("Frontend", "React / Vite", "HTML / CSS / JS"),
    "api": ("API Layer", "FastAPI / Django", "Authentication"),
    "database": ("Database", "MongoDB / PostgreSQL", "Redis (Cache)"),
    "cloud": ("Cloud", "AWS (S3, Lambda, EC2)", ""),
    "features": [
        "Secure Auth (JWT/OAuth)",
        "RESTful APIs",
        "Database Optimization",
        "File Storage (AWS S3)",
        "Dockerized Deployment",
        "Scalable Architecture",
    ],
}

TIMELINE = [
    ("2020", "Started my journey", "Joined GitHub, Java", "& Android projects"),
    ("2022", "Web foundations", "HTML, CSS, Bootstrap,", "JavaScript sites"),
    ("2023", "Internships", "CodeClause &", "Bharat Intern projects"),
    ("2025", "Full stack", "React, TypeScript,", "Python backends"),
    ("2026", "Scaling up", "Cloud, networking,", "DevOps & automation"),
]

EXPLORING = [
    ("Advanced Backend Systems", 80),
    ("Cloud Architecture", 70),
    ("Real-time Applications", 65),
    ("System Design", 60),
    ("Automation & Integrations", 55),
]

ACHIEVEMENTS = [
    ("Web Development", "#ff8c42"),
    ("API Development", "#58a6ff"),
    ("Cloud Fundamentals", "#f0b72f"),
    ("Docker & DevOps", "#3fb950"),
    ("Problem Solving", "#ff6a3d"),
    ("Open Source Contributor", "#bc8cff"),
]

WORKFLOW = [
    ("Idea", "Understand needs"),
    ("Design", "Plan arch & UI/UX"),
    ("Develop", "Frontend + Backend"),
    ("Test", "Debug & validate"),
    ("CI/CD", "Automated build"),
    ("Deploy", "Ship to cloud"),
    ("Monitor", "Track performance"),
    ("Improve", "Feedback & iterate"),
]

PROBLEM_SOLUTION = [
    ("Slow API Performance", "API optimization & caching"),
    ("Complex UI Requirements", "Reusable components & clean architecture"),
    ("Authentication & Security", "JWT, OAuth, RBAC"),
    ("Data Management", "Database design & optimization"),
    ("Deployment Issues", "Docker + AWS + CI/CD"),
    ("Manual Processes", "Automation & integrations"),
]
