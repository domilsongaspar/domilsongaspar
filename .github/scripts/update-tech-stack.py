import os
import re
import requests
from collections import Counter

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]

README_PATH = "README.md"

LANG_START = "<!--START_LANGUAGE_STATS-->"
LANG_END = "<!--END_LANGUAGE_STATS-->"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


# ---------------------------------------------------------
# GitHub API
# ---------------------------------------------------------

def github_get(url, params=None):
    response = requests.get(
        url,
        headers=HEADERS,
        params=params,
        timeout=30,
    )

    response.raise_for_status()

    return response.json()


def get_repositories():
    repositories = []
    page = 1

    while True:
        data = github_get(
            f"https://api.github.com/users/{USERNAME}/repos",
            {
                "per_page": 100,
                "page": page,
                "type": "owner",
            },
        )

        if not data:
            break

        repositories.extend(data)

        if len(data) < 100:
            break

        page += 1

    return repositories


def get_repository_languages(repo):
    return github_get(repo["languages_url"])


def get_repository_file(repo, path):
    url = (
        f"https://api.github.com/repos/"
        f"{USERNAME}/{repo['name']}/contents/{path}"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    if response.status_code != 200:
        return None

    return response.json()


# ---------------------------------------------------------
# Download files
# ---------------------------------------------------------

def get_file_content(repo, path):
    data = get_repository_file(repo, path)

    if not data:
        return None

    if data.get("type") != "file":
        return None

    try:
        import base64

        return base64.b64decode(
            data["content"]
        ).decode("utf-8")

    except Exception:
        return None


# ---------------------------------------------------------
# Technology detection
# ---------------------------------------------------------

TECHNOLOGIES = {
    # Frontend
    "React": [
        "react",
        "react-dom",
    ],

    "Next.js": [
        "next",
    ],

    "Vue.js": [
        "vue",
    ],

    "Nuxt": [
        "nuxt",
    ],

    "Angular": [
        "@angular/core",
    ],

    "Svelte": [
        "svelte",
    ],

    "Astro": [
        "astro",
    ],

    # Backend / Node
    "Node.js": [
        "node",
        "@types/node",
    ],

    "Express": [
        "express",
    ],

    "NestJS": [
        "@nestjs/core",
    ],

    "Fastify": [
        "fastify",
    ],

    # CSS
    "Tailwind CSS": [
        "tailwindcss",
    ],

    "Bootstrap": [
        "bootstrap",
    ],

    "Sass": [
        "sass",
        "scss",
    ],

    # Database
    "Prisma": [
        "prisma",
        "@prisma/client",
    ],

    "Mongoose": [
        "mongoose",
    ],

    "Sequelize": [
        "sequelize",
    ],

    # Python
    "Django": [
        "django",
    ],

    "Flask": [
        "flask",
    ],

    "FastAPI": [
        "fastapi",
    ],

    "Pandas": [
        "pandas",
    ],

    "NumPy": [
        "numpy",
    ],

    # Java
    "Spring Boot": [
        "spring-boot",
        "springframework",
    ],

    "Hibernate": [
        "hibernate",
    ],

    # Mobile
    "React Native": [
        "react-native",
    ],

    "Flutter": [
        "flutter",
    ],

    "Expo": [
        "expo",
    ],

    # DevOps
    "Docker": [
        "dockerfile",
        "docker-compose",
        "docker compose",
    ],

    "GitHub Actions": [
        ".github/workflows",
        "github actions",
    ],

    "Kubernetes": [
        "kubernetes",
        "k8s",
    ],

    # Testing
    "Jest": [
        "jest",
    ],

    "Vitest": [
        "vitest",
    ],

    "Cypress": [
        "cypress",
    ],

    "Playwright": [
        "playwright",
    ],
}


# ---------------------------------------------------------
# File detection
# ---------------------------------------------------------

FILE_TECHNOLOGIES = {
    "Dockerfile": "Docker",
    "docker-compose.yml": "Docker",
    "docker-compose.yaml": "Docker",

    "Cargo.toml": "Rust",

    "go.mod": "Go",

    "pom.xml": "Java",
    "build.gradle": "Java",
    "build.gradle.kts": "Kotlin",

    "requirements.txt": "Python",
    "pyproject.toml": "Python",
    "manage.py": "Django",

    "composer.json": "PHP",

    "Gemfile": "Ruby",
}


# ---------------------------------------------------------
# Package detection
# ---------------------------------------------------------

def detect_from_package(content, detected):
    if not content:
        return

    content_lower = content.lower()

    for technology, patterns in TECHNOLOGIES.items():
        for pattern in patterns:
            if pattern.lower() in content_lower:
                detected[technology] += 1
                break


def detect_files(repo, detected):
    common_files = [
        "Dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "Cargo.toml",
        "go.mod",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts",
        "requirements.txt",
        "pyproject.toml",
        "manage.py",
        "composer.json",
        "Gemfile",
    ]

    for filename in common_files:
        content = get_file_content(repo, filename)

        if content:
            tech = FILE_TECHNOLOGIES.get(filename)

            if tech:
                detected[tech] += 1

            detect_from_package(content, detected)


# ---------------------------------------------------------
# Language detection
# ---------------------------------------------------------

def calculate_languages(repositories):
    languages = Counter()

    for repo in repositories:
        if repo["fork"]:
            continue

        try:
            data = get_repository_languages(repo)

            for language, amount in data.items():
                languages[language] += amount

        except Exception as error:
            print(
                f"Could not analyze languages "
                f"for {repo['name']}: {error}"
            )

    return languages


# ---------------------------------------------------------
# Technology analysis
# ---------------------------------------------------------

def calculate_technologies(repositories):
    detected = Counter()

    for repo in repositories:
        if repo["fork"]:
            continue

        print(f"Analyzing: {repo['name']}")

        # package.json
        package_json = get_file_content(
            repo,
            "package.json",
        )

        detect_from_package(
            package_json,
            detected,
        )

        # requirements.txt
        requirements = get_file_content(
            repo,
            "requirements.txt",
        )

        detect_from_package(
            requirements,
            detected,
        )

        # pyproject.toml
        pyproject = get_file_content(
            repo,
            "pyproject.toml",
        )

        detect_from_package(
            pyproject,
            detected,
        )

        # pom.xml
        pom = get_file_content(
            repo,
            "pom.xml",
        )

        detect_from_package(
            pom,
            detected,
        )

        # Other files
        detect_files(
            repo,
            detected,
        )

        # GitHub Actions
        workflows = github_get(
            f"https://api.github.com/repos/"
            f"{USERNAME}/{repo['name']}/contents/.github/workflows"
        ) if repository_directory_exists(
            repo,
            ".github/workflows",
        ) else None

        if workflows:
            detected["GitHub Actions"] += 1

    return detected


def repository_directory_exists(repo, path):
    url = (
        f"https://api.github.com/repos/"
        f"{USERNAME}/{repo['name']}/contents/{path}"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30,
    )

    return response.status_code == 200


# ---------------------------------------------------------
# Badges
# ---------------------------------------------------------

BADGES = {
    "JavaScript": ("javascript", "F7DF1E", "black"),
    "TypeScript": ("typescript", "3178C6", "white"),
    "Python": ("python", "3776AB", "white"),
    "Java": ("openjdk", "ED8B00", "white"),
    "Kotlin": ("kotlin", "7F52FF", "white"),
    "Go": ("go", "00ADD8", "white"),
    "Rust": ("rust", "000000", "white"),
    "PHP": ("php", "777BB4", "white"),
    "Ruby": ("ruby", "CC342D", "white"),
    "C": ("c", "A8B9CC", "black"),
    "C++": ("cplusplus", "00599C", "white"),
    "C#": ("csharp", "239120", "white"),
    "HTML": ("html5", "E34F26", "white"),
    "CSS": ("css3", "1572B6", "white"),

    "React": ("react", "61DAFB", "black"),
    "Next.js": ("nextdotjs", "000000", "white"),
    "Vue.js": ("vuedotjs", "4FC08D", "black"),
    "Nuxt": ("nuxtdotjs", "00DC82", "black"),
    "Angular": ("angular", "DD0031", "white"),
    "Svelte": ("svelte", "FF3E00", "white"),
    "Astro": ("astro", "FF5D01", "white"),

    "Node.js": ("nodedotjs", "339933", "white"),
    "Express": ("express", "000000", "white"),
    "NestJS": ("nestjs", "E0234E", "white"),
    "Fastify": ("fastify", "000000", "white"),

    "Tailwind CSS": ("tailwindcss", "06B6D4", "white"),
    "Bootstrap": ("bootstrap", "7952B3", "white"),
    "Sass": ("sass", "CC6699", "white"),

    "Prisma": ("prisma", "2D3748", "white"),
    "Mongoose": ("mongoose", "880000", "white"),
    "Sequelize": ("sequelize", "52B0E7", "white"),

    "Django": ("django", "092E20", "white"),
    "Flask": ("flask", "000000", "white"),
    "FastAPI": ("fastapi", "009688", "white"),

    "Spring Boot": ("springboot", "6DB33F", "white"),
    "Hibernate": ("hibernate", "59666C", "white"),

    "React Native": ("react", "61DAFB", "black"),
    "Flutter": ("flutter", "02569B", "white"),
    "Expo": ("expo", "000020", "white"),

    "Docker": ("docker", "2496ED", "white"),
    "GitHub Actions": ("githubactions", "2088FF", "white"),
    "Kubernetes": ("kubernetes", "326CE5", "white"),

    "Jest": ("jest", "C21325", "white"),
    "Vitest": ("vitest", "6E9F18", "white"),
    "Cypress": ("cypress", "69D3A7", "black"),
    "Playwright": ("playwright", "2EAD33", "white"),
}


def badge(technology):
    if technology not in BADGES:
        return f"`{technology}`"

    logo, color, logo_color = BADGES[technology]

    label = technology.replace(" ", "%20")
    label = label.replace("#", "%23")
    label = label.replace("+", "%2B")

    return (
        f"![{technology}]"
        f"(https://img.shields.io/badge/"
        f"{label}-{color}"
        f"?style=for-the-badge"
        f"&logo={logo}"
        f"&logoColor={logo_color})"
    )


# ---------------------------------------------------------
# README generation
# ---------------------------------------------------------

def replace_section(readme, start_marker, end_marker, content):
    start = readme.find(start_marker)
    end = readme.find(end_marker)

    if start == -1 or end == -1:
        raise RuntimeError(
            f"Markers not found: {start_marker}"
        )

    content_start = start + len(start_marker)

    return (
        readme[:content_start]
        + "\n\n"
        + content
        + "\n\n"
        + readme[end:]
    )


def generate_tech_stack(technologies):
    if not technologies:
        return "Nenhuma tecnologia detectada."

    categories = {
        "💻 Linguagens": [
            "JavaScript",
            "TypeScript",
            "Python",
            "Java",
            "Kotlin",
            "Go",
            "Rust",
            "PHP",
            "Ruby",
            "C",
            "C++",
            "C#",
            "HTML",
            "CSS",
        ],

        "🎨 Frontend": [
            "React",
            "Next.js",
            "Vue.js",
            "Nuxt",
            "Angular",
            "Svelte",
            "Astro",
            "Tailwind CSS",
            "Bootstrap",
            "Sass",
        ],

        "⚙️ Backend": [
            "Node.js",
            "Express",
            "NestJS",
            "Fastify",
            "Django",
            "Flask",
            "FastAPI",
            "Spring Boot",
            "Hibernate",
        ],

        "🗄️ Database & ORM": [
            "Prisma",
            "Mongoose",
            "Sequelize",
        ],

        "📱 Mobile": [
            "React Native",
            "Flutter",
            "Expo",
        ],

        "🚀 DevOps": [
            "Docker",
            "GitHub Actions",
            "Kubernetes",
        ],

        "🧪 Testing": [
            "Jest",
            "Vitest",
            "Cypress",
            "Playwright",
        ],
    }

    output = []

    for category, items in categories.items():
        found = [
            technology
            for technology in items
            if technology in technologies
        ]

        if not found:
            continue

        output.append(f"### {category}\n")
        output.append(
            "\n".join(
                badge(technology)
                for technology in found
            )
        )
        output.append("")

    return "\n".join(output)


def generate_language_stats(languages):
    total = sum(languages.values())

    if total == 0:
        return "Nenhuma linguagem encontrada."

    output = []

    for language, amount in languages.most_common(8):
        percentage = (amount / total) * 100

        output.append(
            f"- **{language}** — {percentage:.1f}%"
        )

    return "\n".join(output)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    print(
        f"\n🔎 Analisando projetos de @{USERNAME}\n"
    )

    repositories = get_repositories()

    print(
        f"📦 {len(repositories)} repositórios encontrados."
    )

    languages = calculate_languages(
        repositories
    )

    print("\n💻 Linguagens:")

    for language, amount in languages.most_common():
        print(
            f"  {language}: {amount}"
        )

    language_stats = generate_language_stats(
        languages
    )

    with open(
        README_PATH,
        "r",
        encoding="utf-8",
    ) as file:
        readme = file.read()

    readme = replace_section(
        readme,
        LANG_START,
        LANG_END,
        language_stats,
    )

    with open(
        README_PATH,
        "w",
        encoding="utf-8",
    ) as file:
        file.write(readme)

    print(
        "\n✅ Language statistics updated successfully!"
    )


if __name__ == "__main__":
    main()
