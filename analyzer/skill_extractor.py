import re


SKILLS = [

    "python",
    "java",
    "c++",
    "c",
    "javascript",
    "html",
    "css",

    "bootstrap",
    "react",
    "angular",
    "node.js",

    "flask",
    "django",
    "spring boot",

    "sql",
    "mysql",
    "postgresql",
    "mongodb",

    "git",
    "github",

    "docker",
    "aws",

    "pandas",
    "numpy",
    "matplotlib",

    "machine learning",
    "deep learning",
    "natural language processing",
    "nlp",

    "scikit-learn",
    "tensorflow",
    "pytorch",

    "rest api",
    "hibernate",
    "jpa",
    "maven",

    "power bi",
    "excel"
]


def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(pattern, text):

            found_skills.append(skill)

    return sorted(set(found_skills))