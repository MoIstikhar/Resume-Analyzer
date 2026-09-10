def get_recommendations(
    missing_skills
):

    recommendations = []

    for skill in missing_skills:

        recommendations.append({

            "skill": skill.title(),

            "message":
                f"Improve your {skill.title()} skills "
                f"by building a small practical project."
        })

    return recommendations