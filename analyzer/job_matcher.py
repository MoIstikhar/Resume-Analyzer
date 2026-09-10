import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# Skills Database
# ==========================================

SKILLS = [
    "python",
    "java",
    "c++",
    "javascript",
    "typescript",
    "php",
    "ruby",
    "go",
    "kotlin",

    "html",
    "css",
    "bootstrap",
    "react",
    "angular",
    "vue",
    "next.js",

    "node.js",
    "flask",
    "django",
    "spring boot",
    "spring",
    "express.js",

    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",
    "sqlite",

    "hibernate",
    "jpa",
    "maven",
    "servlet",
    "jsp",

    "pandas",
    "numpy",
    "matplotlib",
    "scikit-learn",

    "machine learning",
    "deep learning",
    "artificial intelligence",
    "natural language processing",
    "nlp",

    "tensorflow",
    "pytorch",

    "rest api",
    "rest",

    "git",
    "github",
    "docker",
    "aws",
    "azure",
    "linux",
    "kubernetes",

    "power bi",
    "excel"
]


# ==========================================
# Skill Normalization
# ==========================================

SKILL_ALIASES = {
    "spring": "spring boot",
    "rest": "rest api",
}


def normalize_skill(skill):

    skill = skill.strip().lower()

    return SKILL_ALIASES.get(
        skill,
        skill
    )


# ==========================================
# Extract Skills
# ==========================================

def extract_job_skills(text):

    if not text:
        return []

    text = text.lower()

    found_skills = []

    for skill in SKILLS:

        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )

        if re.search(pattern, text):

            found_skills.append(
                normalize_skill(skill)
            )

    return sorted(
        set(found_skills)
    )


# ==========================================
# Skill Matching
# ==========================================

def calculate_skill_score(
    resume_skills,
    job_skills
):

    resume_set = set(
        normalize_skill(skill)
        for skill in resume_skills
        if skill.strip()
    )

    job_set = set(
        normalize_skill(skill)
        for skill in job_skills
        if skill.strip()
    )

    if not job_set:

        return 0, [], []


    matched_skills = sorted(
        resume_set.intersection(
            job_set
        )
    )


    missing_skills = sorted(
        job_set - resume_set
    )


    skill_score = (
        len(matched_skills)
        / len(job_set)
    ) * 100


    return (
        skill_score,
        matched_skills,
        missing_skills
    )


# ==========================================
# Text Similarity
# ==========================================

def calculate_text_similarity(
    resume_text,
    job_text
):

    if not resume_text or not job_text:

        return 0


    try:

        vectorizer = TfidfVectorizer(
            stop_words="english"
        )

        documents = [
            resume_text,
            job_text
        ]

        vectors = vectorizer.fit_transform(
            documents
        )

        similarity = cosine_similarity(
            vectors[0:1],
            vectors[1:2]
        )

        return similarity[0][0] * 100


    except Exception as e:

        print(
            "TF-IDF Error:",
            e
        )

        return 0


# ==========================================
# Job Role Matching
# ==========================================

def calculate_role_score(
    resume_text,
    job_title
):

    if not resume_text or not job_title:

        return 0


    resume_text = resume_text.lower()
    job_title = job_title.lower()


    roles = {

        "java developer": [
            "java",
            "spring boot",
            "hibernate",
            "jpa"
        ],

        "backend developer": [
            "java",
            "python",
            "flask",
            "django",
            "spring boot",
            "node.js"
        ],

        "python developer": [
            "python",
            "django",
            "flask"
        ],

        "frontend developer": [
            "html",
            "css",
            "javascript",
            "react",
            "angular"
        ],

        "full stack developer": [
            "html",
            "css",
            "javascript",
            "java",
            "python",
            "react",
            "angular",
            "node.js"
        ],

        "data scientist": [
            "python",
            "pandas",
            "numpy",
            "machine learning",
            "scikit-learn"
        ],

        "machine learning engineer": [
            "python",
            "machine learning",
            "scikit-learn",
            "tensorflow",
            "pytorch"
        ]
    }


    matched_role = None


    for role, required_skills in roles.items():

        role_words = role.split()

        if all(
            word in job_title
            for word in role_words
        ):

            matched_role = required_skills
            break


    if not matched_role:

        return 0


    matched = 0

    for skill in matched_role:

        if skill in resume_text:

            matched += 1


    return (
        matched
        / len(matched_role)
    ) * 100


# ==========================================
# Main Matching Function
# ==========================================

def calculate_match(
    resume_text,
    resume_skills,
    job
):

    job_title = getattr(
        job,
        "title",
        ""
    )

    job_description = getattr(
        job,
        "description",
        ""
    )

    job_required_skills = getattr(
        job,
        "required_skills",
        ""
    )


    # --------------------------------------
    # Extract job skills
    # --------------------------------------

    title_skills = extract_job_skills(
        job_title
    )

    description_skills = extract_job_skills(
        job_description
    )


    # --------------------------------------
    # API Tags
    # --------------------------------------

    tag_skills = []

    if job_required_skills:

        tag_skills = [

            normalize_skill(skill)

            for skill in job_required_skills.split(",")

            if skill.strip()

        ]


    # --------------------------------------
    # Combine skills
    # --------------------------------------

    job_skills = sorted(
        set(
            title_skills
            + description_skills
            + tag_skills
        )
    )


    # --------------------------------------
    # Skill score
    # --------------------------------------

    (
        skill_score,
        matched_skills,
        missing_skills
    ) = calculate_skill_score(

        resume_skills,

        job_skills

    )


    # --------------------------------------
    # Text score
    # --------------------------------------

    job_text = (
        job_title
        + " "
        + job_description
    )


    text_score = calculate_text_similarity(

        resume_text,

        job_text

    )


    # --------------------------------------
    # Role score
    # --------------------------------------

    role_score = calculate_role_score(

        resume_text,

        job_title

    )


    # --------------------------------------
    # Final score
    # --------------------------------------

    final_score = (

        skill_score * 0.60

        + text_score * 0.25

        + role_score * 0.15

    )


    final_score = min(
        max(final_score, 0),
        100
    )


    return {

        "score": round(
            final_score,
            2
        ),

        "skill_score": round(
            skill_score,
            2
        ),

        "text_score": round(
            text_score,
            2
        ),

        "title_score": round(
            role_score,
            2
        ),

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "job_skills":
            job_skills
    }