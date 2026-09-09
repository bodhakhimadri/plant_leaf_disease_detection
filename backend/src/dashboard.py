from collections import Counter


def build_stats(data):

    disease_names = [
        row.get("disease_name", "")
        for row in data
    ]

    healthy = sum(
        1 for disease in disease_names
        if "healthy" in disease.lower()
    )

    diseased = len(disease_names) - healthy

    disease_counter = Counter(disease_names)

    return {

        "total_predictions": len(disease_names),

        "healthy": healthy,

        "diseased": diseased,

        "disease_counter": disease_counter

    }