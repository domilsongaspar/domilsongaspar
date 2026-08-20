import os
import html
import requests
from collections import Counter

USERNAME = os.environ["GITHUB_USERNAME"]
TOKEN = os.environ["GITHUB_TOKEN"]

OUTPUT_DIR = "assets"
OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "languages.svg"
)

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {TOKEN}",
    "X-GitHub-Api-Version": "2022-11-28",
}


# ---------------------------------------------------------
# Language configuration
# ---------------------------------------------------------

LANGUAGE_CONFIG = {
    "C": {
        "color": "#555555",
        "logo": "C",
    },

    "C++": {
        "color": "#00599C",
        "logo": "C++",
    },

    "C#": {
        "color": "#239120",
        "logo": "C#",
    },

    "JavaScript": {
        "color": "#F7DF1E",
        "logo": "JS",
    },

    "TypeScript": {
        "color": "#3178C6",
        "logo": "TS",
    },

    "Python": {
        "color": "#3776AB",
        "logo": "Py",
    },

    "PHP": {
        "color": "#777BB4",
        "logo": "PHP",
    },

    "Java": {
        "color": "#ED8B00",
        "logo": "Java",
    },

    "Kotlin": {
        "color": "#7F52FF",
        "logo": "Kt",
    },

    "Go": {
        "color": "#00ADD8",
        "logo": "Go",
    },

    "Rust": {
        "color": "#DEA584",
        "logo": "Rs",
    },

    "Ruby": {
        "color": "#CC342D",
        "logo": "Rb",
    },

    "HTML": {
        "color": "#E34F26",
        "logo": "HTML",
    },

    "CSS": {
        "color": "#1572B6",
        "logo": "CSS",
    },

    "Dart": {
        "color": "#0175C2",
        "logo": "Dart",
    },

    "Swift": {
        "color": "#F05138",
        "logo": "Swift",
    },
}


# Languages that should not appear as programming languages
IGNORED_LANGUAGES = {
    "Makefile",
    "Dockerfile",
    "Shell",
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
        repos = github_get(
            f"https://api.github.com/users/{USERNAME}/repos",
            params={
                "type": "owner",
                "per_page": 100,
                "page": page,
            },
        )

        if not repos:
            break

        repositories.extend(repos)

        if len(repos) < 100:
            break

        page += 1

    return repositories


def get_languages(repository):
    return github_get(
        repository["languages_url"]
    )


# ---------------------------------------------------------
# Calculate languages
# ---------------------------------------------------------

def calculate_languages(repositories):
    languages = Counter()

    for repository in repositories:

        # Ignore forks
        if repository["fork"]:
            continue

        print(
            f"Analyzing: {repository['name']}"
        )

        try:
            data = get_languages(
                repository
            )

            for language, amount in data.items():

                if language in IGNORED_LANGUAGES:
                    continue

                languages[language] += amount

        except requests.RequestException as error:
            print(
                f"Could not analyze "
                f"{repository['name']}: {error}"
            )

    return languages


# ---------------------------------------------------------
# SVG helpers
# ---------------------------------------------------------

def escape(value):
    return html.escape(
        str(value),
        quote=True
    )


def language_color(language):
    config = LANGUAGE_CONFIG.get(language)

    if config:
        return config["color"]

    return "#8B949E"


def language_logo(language):
    config = LANGUAGE_CONFIG.get(language)

    if config:
        return config["logo"]

    return language[:3]


# ---------------------------------------------------------
# Generate SVG
# ---------------------------------------------------------

def generate_svg(languages):

    # Keep top 8 languages
    languages = languages.most_common(8)

    if not languages:
        return """
<svg xmlns="http://www.w3.org/2000/svg"
     width="720"
     height="180"
     viewBox="0 0 720 180">

  <rect
    width="720"
    height="180"
    rx="16"
    fill="#0d1117"
  />

  <text
    x="360"
    y="95"
    text-anchor="middle"
    fill="#8b949e"
    font-family="Arial, sans-serif"
    font-size="18"
  >
    No languages found
  </text>

</svg>
"""

    total = sum(
        amount
        for _, amount in languages
    )

    width = 760
    row_height = 55
    header_height = 70

    height = (
        header_height
        + len(languages) * row_height
        + 30
    )

    svg = []

    svg.append(
        f'''
<svg
  xmlns="http://www.w3.org/2000/svg"
  width="{width}"
  height="{height}"
  viewBox="0 0 {width} {height}"
>
'''
    )

    # -----------------------------------------------------
    # Definitions
    # -----------------------------------------------------

    svg.append("""
<defs>

  <filter
    id="shadow"
    x="-20%"
    y="-20%"
    width="140%"
    height="140%"
  >
    <feDropShadow
      dx="0"
      dy="3"
      stdDeviation="4"
      flood-opacity="0.25"
    />
  </filter>

  <style>

    .title {
      font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;

      font-size: 22px;
      font-weight: 700;
      fill: #f0f6fc;
    }

    .language {
      font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;

      font-size: 14px;
      font-weight: 600;
      fill: #c9d1d9;
    }

    .percentage {
      font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        Arial,
        sans-serif;

      font-size: 13px;
      fill: #8b949e;
    }

    .bar {
      transform-origin: left;
      animation: grow 1.2s ease-out forwards;
    }

    @keyframes grow {
      from {
        transform: scaleX(0);
      }

      to {
        transform: scaleX(1);
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .bar {
        animation: none;
      }
    }

  </style>

</defs>
""")

    # -----------------------------------------------------
    # Background
    # -----------------------------------------------------

    svg.append(
        f'''
<rect
  width="{width}"
  height="{height}"
  rx="18"
  fill="#0d1117"
  filter="url(#shadow)"
/>
'''
    )

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------

    svg.append(
        f'''
<text
  x="30"
  y="42"
  class="title"
>
  📊 Most Used Languages
</text>
'''
    )

    # -----------------------------------------------------
    # Rows
    # -----------------------------------------------------

    max_bar_width = 430
    bar_x = 200

    for index, (language, amount) in enumerate(
        languages
    ):

        percentage = (
            amount / total
        ) * 100

        y = (
            header_height
            + index * row_height
        )

        color = language_color(
            language
        )

        logo = language_logo(
            language
        )

        # Logo circle
        svg.append(
            f'''
<circle
  cx="34"
  cy="{y + 22}"
  r="16"
  fill="{color}"
/>
'''
        )

        # Logo text
        svg.append(
            f'''
<text
  x="34"
  y="{y + 27}"
  text-anchor="middle"
  font-family="Arial, sans-serif"
  font-size="9"
  font-weight="700"
  fill="#ffffff"
>
  {escape(logo)}
</text>
'''
        )

        # Language
        svg.append(
            f'''
<text
  x="60"
  y="{y + 27}"
  class="language"
>
  {escape(language)}
</text>
'''
        )

        # Background bar
        svg.append(
            f'''
<rect
  x="{bar_x}"
  y="{y + 10}"
  width="{max_bar_width}"
  height="10"
  rx="5"
  fill="#21262d"
/>
'''
        )

        # Actual bar
        bar_width = (
            max_bar_width
            * percentage
            / 100
        )

        svg.append(
            f'''
<rect
  class="bar"
  x="{bar_x}"
  y="{y + 10}"
  width="{bar_width}"
  height="10"
  rx="5"
  fill="{color}"
/>
'''
        )

        # Percentage
        svg.append(
            f'''
<text
  x="{bar_x + max_bar_width + 15}"
  y="{y + 20}"
  class="percentage"
>
  {percentage:.1f}%
</text>
'''
        )

    svg.append("</svg>")

    return "".join(svg)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def update_readme():
    start_marker = "<!--START_LANGUAGE_STATS-->"
    end_marker = "<!--END_LANGUAGE_STATS-->"

    with open(
        "README.md",
        "r",
        encoding="utf-8"
    ) as file:
        readme = file.read()

    start = readme.find(start_marker)
    end = readme.find(end_marker)

    if start == -1:
        raise RuntimeError(
            "START_LANGUAGE_STATS marker not found in README.md"
        )

    if end == -1:
        raise RuntimeError(
            "END_LANGUAGE_STATS marker not found in README.md"
        )

    content = f"""
<p align="center">
  <img
    src="./assets/languages.svg"
    alt="Most Used Languages"
  />
</p>
"""

    content_start = start + len(start_marker)

    new_readme = (
        readme[:content_start]
        + content
        + readme[end:]
    )

    with open(
        "README.md",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(new_readme)

    print("✅ README updated successfully!")


def main():

    print(
        f"🔎 Analyzing @{USERNAME}"
    )

    repositories = get_repositories()

    print(
        f"📦 {len(repositories)} repositories found."
    )

    languages = calculate_languages(
        repositories
    )

    print("\n📊 Languages:")

    for language, amount in languages.most_common():
        print(
            f"  {language}: {amount}"
        )

    svg = generate_svg(
        languages
    )

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    with open(
        OUTPUT_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        file.write(svg)

    print(
        f"✅ Chart generated: {OUTPUT_FILE}"
    )

    update_readme()


if __name__ == "__main__":
    main()
