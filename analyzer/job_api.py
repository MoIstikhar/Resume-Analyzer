import os
import requests

from dotenv import load_dotenv


load_dotenv()


ADZUNA_APP_ID = os.getenv(
    "ADZUNA_APP_ID"
)

ADZUNA_APP_KEY = os.getenv(
    "ADZUNA_APP_KEY"
)


BASE_URL = (
    "https://api.adzuna.com/v1/api/jobs/in/search/1"
)


def search_jobs(
    skills,
    location="India",
    results_per_page=20
):

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:

        raise ValueError(
            "Adzuna API credentials are missing."
        )


    if not skills:

        return []


    # ==================================
    # Clean skills
    # ==================================

    skills = [

        skill.strip().lower()

        for skill in skills

        if skill.strip()

    ]


    queries = []


    # ==================================
    # Create relevant searches
    # ==================================

    if "java" in skills:

        queries.append(
            "Java Developer"
        )


    if "java" in skills and "spring boot" in skills:

        queries.append(
            "Java Spring Boot Developer"
        )


    if "spring boot" in skills:

        queries.append(
            "Spring Boot Developer"
        )


    if "python" in skills:

        queries.append(
            "Python Developer"
        )


    if "python" in skills and "flask" in skills:

        queries.append(
            "Python Flask Developer"
        )


    if "python" in skills and "django" in skills:

        queries.append(
            "Python Django Developer"
        )


    if "javascript" in skills:

        queries.append(
            "JavaScript Developer"
        )


    if "react" in skills:

        queries.append(
            "React Developer"
        )


    if "angular" in skills:

        queries.append(
            "Angular Developer"
        )


    if "sql" in skills:

        queries.append(
            "SQL Developer"
        )


    # ==================================
    # Fallback
    # ==================================

    if not queries:

        queries.append(
            "Software Developer"
        )


    # Remove duplicate queries

    queries = list(
        dict.fromkeys(queries)
    )


    all_jobs = []


    # ==================================
    # Search jobs
    # ==================================

    for query in queries[:6]:

        print(
            "Searching jobs:",
            query
        )


        params = {

            "app_id":
                ADZUNA_APP_ID,

            "app_key":
                ADZUNA_APP_KEY,

            "results_per_page":
                results_per_page,

            "what":
                query,

            "where":
                location,

            "content-type":
                "application/json"
        }


        try:

            response = requests.get(

                BASE_URL,

                params=params,

                timeout=15

            )


            response.raise_for_status()


            data = response.json()


            jobs = data.get(
                "results",
                []
            )


            print(
                "Jobs found:",
                len(jobs)
            )


            all_jobs.extend(
                jobs
            )


        except Exception as e:

            print(
                "Adzuna Error:",
                e
            )


    # ==================================
    # Remove duplicate jobs
    # ==================================

    unique_jobs = {}


    for job in all_jobs:

        job_id = job.get(
            "id"
        )


        # If API ID exists
        if job_id:

            unique_jobs[
                str(job_id)
            ] = job

        else:

            # Fallback unique key
            key = (

                str(
                    job.get(
                        "title",
                        ""
                    )
                ).lower()

                + "|"

                + str(
                    job.get(
                        "company",
                        {}
                    )
                ).lower()

            )


            unique_jobs[key] = job


    final_jobs = list(
        unique_jobs.values()
    )


    print(
        "Total unique jobs:",
        len(final_jobs)
    )


    return final_jobs