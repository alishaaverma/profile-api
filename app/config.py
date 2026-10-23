"""Profile content shown on the cards.

Everything that comes from GitHub (name, location, repos, stars, followers,
commits, PRs, issues, contribution calendar, activity, achievements and which
TECH_STACK items your repos use) is fetched live.
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
        "applications, REST APIs, admin dashboards, cloud-based solutions and "
        "Solidity smart contracts. I enjoy turning ideas into real products "
        "with clean code, scalable architecture and user-focused design."
    ),
    # Set to a number to override; None = years since GitHub account creation.
    "years_experience": None,
    "available": True,
    "chips": ["Frontend", "Backend", "APIs", "Databases", "Cloud", "Web3"],
    # The hero terminal shows the first 5.
    "terminal_lines": [
        "Building Web Applications",
        "Creating Scalable APIs",
        "Writing Smart Contracts",
        "Open to Collaboration",
        "Always Learning...",
    ],
    "neon_words": ["Code", "Design", "Develop", "Deploy", "Repeat"],
    # The about card shows the first 6 of each list below.
    "highlights": [
        "Clean Code",
        "Scalable Systems",
        "Modern UI/UX",
        "REST APIs",
        "Blockchain Dev",
        "Cloud Deployment",
    ],
    # Keep titles under ~15 characters and descriptions under ~22 to fit the boxes.
    "capabilities": [
        ("Frontend", "React, TypeScript, Vite"),
        ("Backend & APIs", "FastAPI, Django, Flask"),
        ("Database", "MongoDB, PostgreSQL"),
        ("Cloud", "AWS Amplify, S3, CDN"),
        ("CMS", "WordPress, Elementor"),
        ("Blockchain", "Solidity contracts"),
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
        ("Flask", "FL", "#2BE27D"),
        ("Java", "J", "#F89820"),
        ("REST API", "API", "#39C5CF"),
        ("Solidity", "Sol", "#AA6746"),
    ],
    "Database": [
        ("MongoDB", "M", "#47A248"),
        ("PostgreSQL", "PG", "#4169E1"),
    ],
    "Cloud & DevOps": [
        ("AWS", "aws", "#FF9900"),
        ("S3", "S3", "#569A31"),
        ("Lambda", "λ", "#FF9900"),
        ("Amplify", "AM", "#F58534"),
        ("Cloudfront", "CF", "#34F5F2"),
        ("Docker", "D", "#2496ED"),
        ("Git", "G", "#F05032"),
        ("GitHub", "GH", "#E6EDF3"),
    ],
    "CMS & Tools": [
        ("WordPress", "W", "#21759B"),
        ("Elementor", "E", "#D63384"),
        ("Custom CMS", "CC", "#96588A"),
        ("VS Code", "VS", "#007ACC"),
    ],
}

# How each TECH_STACK item is spotted in a repo: its languages, topics, name and
# description words, package.json / requirements.txt dependencies, and the
# "docker" / "github-actions" markers for a Dockerfile / .github/workflows.
# A trailing * matches as a prefix. Items not listed match their lowercase name.
TECH_ALIASES = {
    "HTML5": ["html", "html5"],
    "CSS3": ["css", "css3", "scss"],
    "JavaScript": ["javascript", "js", "node", "nodejs", "node.js"],
    "TypeScript": ["typescript", "ts", "tsx"],
    "React": ["react", "reactjs", "react-dom"],
    "Vite": ["vite", "@vitejs/*"],
    "Tailwind": ["tailwind", "tailwindcss"],
    "Python": ["python", "python3"],
    "FastAPI": ["fastapi", "uvicorn"],
    "Django": ["django", "djangorestframework"],
    "DRF": ["drf", "djangorestframework", "django-rest-framework"],
    "Flask": ["flask", "flask-*"],
    "Java": ["java", "spring", "spring-boot", "springboot"],
    "REST API": ["api", "apis", "rest", "rest-api", "restful", "fastapi", "flask", "express",
                 "djangorestframework", "axios"],
    "Solidity": ["solidity", "smart-contracts", "hardhat", "truffle", "foundry", "ethers", "web3",
                 "@openzeppelin/*", "blockchain", "ethereum"],
    "MongoDB": ["mongodb", "mongo", "mongoose", "pymongo", "motor"],
    "PostgreSQL": ["postgresql", "postgres", "pg", "psycopg2", "psycopg2-binary", "psycopg", "asyncpg"],
    "AWS": ["aws", "boto3", "aws-sdk", "@aws-sdk/*"],
    "S3": ["s3", "aws-s3", "@aws-sdk/client-s3"],
    "Lambda": ["lambda", "aws-lambda", "serverless", "mangum"],
    "Amplify": ["amplify", "aws-amplify", "@aws-amplify/*"],
    "Cloudfront": ["cloudfront", "cdn", "@aws-sdk/client-cloudfront"],
    "Docker": ["docker", "dockerfile", "docker-compose"],
    "Git": ["*"],     # every repo
    "GitHub": ["*"],
    "WordPress": ["wordpress", "wp"],
    "Elementor": ["elementor"],
    "Custom CMS": ["cms", "custom-cms", "headless-cms"],
    "VS Code": [],    # nothing in a repo shows this
}

WHAT_I_BUILD = [
    ("Web Applications", "Modern, responsive web apps with React & Vite"),
    ("APIs & Backends", "Custom REST APIs with FastAPI, Django & Flask"),
    ("Smart Contracts", "Solidity smart contracts for blockchain apps"),
    ("Admin Dashboards", "Manage content, users and application data"),
    ("Cloud Solutions", "Deploy on AWS with Amplify, S3 & Cloudfront"),
    ("CMS Development", "WordPress, Elementor & custom CMS builds"),
]

# Optional: pin repos by name. Empty = pick automatically (stars, then recent push).
FEATURED_REPOS: list[str] = []

ARCHITECTURE = {
    "client": ("Client", "Browser / User"),
    "frontend": ("Frontend", "React / Vite", "HTML / CSS / JS"),
    "api": ("API Layer", "FastAPI / Django / Flask", "Authentication"),
    "database": ("Database", "MongoDB / PostgreSQL", ""),
    "cloud": ("Cloud", "AWS Amplify / S3", "Lambda / CloudFront"),
    "features": [
        "Secure Auth (JWT/OAuth)",
        "RESTful APIs",
        "Database Optimization",
        "File Storage (AWS S3)",
        "CDN via CloudFront",
        "Smart Contracts (Solidity)",
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
    ("Deployment Issues", "AWS Amplify + CloudFront + CI/CD"),
    ("Trust Between Parties", "Solidity smart contracts"),
]
