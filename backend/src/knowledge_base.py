"""Curated disease guidance used by the detection page."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
KNOWLEDGE_PATH = BASE_DIR / "ai" / "dataset" / "disease_knowledge.json"

with KNOWLEDGE_PATH.open("r", encoding="utf-8") as file:
    disease_db = json.load(file)

# The original knowledge file covered only a subset of the classifier's 38
# labels. These concise fallback cards keep symptoms and first steps available
# for every remaining label until full local guidance is curated.
_HEALTHY_INFO = {
    "description": "No disease symptoms were identified in this leaf image.",
    "symptoms": ["No obvious disease symptoms; leaves appear generally healthy."],
    "organic_treatment": ["No disease treatment is indicated; continue normal crop care."],
    "prevention": ["Monitor plants regularly and maintain good growing conditions."],
}

_SUPPLEMENTAL_INFO = {
    "Blueberry___healthy": _HEALTHY_INFO,
    "Cherry_(including_sour)___healthy": _HEALTHY_INFO,
    "Corn_(maize)___healthy": _HEALTHY_INFO,
    "Grape___healthy": _HEALTHY_INFO,
    "Peach___healthy": _HEALTHY_INFO,
    "Pepper,_bell___healthy": _HEALTHY_INFO,
    "Raspberry___healthy": _HEALTHY_INFO,
    "Soybean___healthy": _HEALTHY_INFO,
    "Strawberry___healthy": _HEALTHY_INFO,
    "Cherry_(including_sour)___Powdery_mildew": {
        "description": "Powdery mildew is a fungal disease affecting cherry leaves and shoots.",
        "symptoms": ["White powdery patches", "Curled or distorted leaves", "Stunted new growth"],
        "organic_treatment": ["Remove badly affected growth where practical", "Improve airflow and avoid excess nitrogen"],
        "prevention": ["Prune for airflow", "Monitor new growth during warm, humid weather"],
    },
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": {
        "description": "Gray leaf spot is a fungal disease that causes elongated lesions on corn leaves.",
        "symptoms": ["Long rectangular gray or tan lesions between veins", "Lesions may merge and dry leaf areas"],
        "organic_treatment": ["Manage infected crop residue after harvest", "Seek local extension advice for severe outbreaks"],
        "prevention": ["Rotate crops", "Choose locally recommended resistant hybrids", "Avoid dense planting"],
    },
    "Corn_(maize)___Common_rust_": {
        "description": "Common rust is a fungal disease that forms rust-colored pustules on corn leaves.",
        "symptoms": ["Small reddish-brown raised pustules on leaves", "Yellowing around heavily infected areas"],
        "organic_treatment": ["Monitor spread and consult a local crop adviser if infection is severe"],
        "prevention": ["Plant resistant hybrids suited to the region", "Avoid planting too densely"],
    },
    "Corn_(maize)___Northern_Leaf_Blight": {
        "description": "Northern leaf blight is a fungal disease of corn foliage.",
        "symptoms": ["Long cigar-shaped gray-green lesions", "Lesions turn tan and can merge as they age"],
        "organic_treatment": ["Manage infected crop residue after harvest", "Seek local advice if lesions spread rapidly"],
        "prevention": ["Rotate crops", "Use resistant hybrids", "Allow good airflow"],
    },
    "Grape___Black_rot": {
        "description": "Black rot is a fungal disease affecting grape leaves, shoots, and berries.",
        "symptoms": ["Brown leaf spots with dark margins", "Berries shrivel into dark, hard mummies"],
        "organic_treatment": ["Remove infected berries and mummies", "Prune infected canes during dry weather"],
        "prevention": ["Remove fallen leaves and fruit mummies", "Keep the canopy open and dry"],
    },
    "Grape___Esca_(Black_Measles)": {
        "description": "Esca is a grapevine trunk disease complex that can cause leaf and fruit symptoms.",
        "symptoms": ["Yellow or red striping between leaf veins", "Leaf tissue may dry between veins", "Dark berry spotting may occur"],
        "organic_treatment": ["Mark affected vines and seek local viticulture advice", "Remove severely affected wood using sound pruning practices"],
        "prevention": ["Use clean tools and healthy planting material", "Avoid large pruning wounds where practical"],
    },
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": {
        "description": "Grape leaf blight causes spots and blighting, often on older leaves.",
        "symptoms": ["Dark reddish-brown leaf spots", "Spots enlarge and dry leaf tissue", "Premature leaf drop in severe cases"],
        "organic_treatment": ["Remove fallen infected leaves", "Improve canopy airflow and reduce leaf wetness"],
        "prevention": ["Prune for airflow", "Remove diseased leaf litter after harvest"],
    },
    "Orange___Haunglongbing_(Citrus_greening)": {
        "description": "Citrus greening is a serious bacterial disease spread by psyllids; local confirmation is important.",
        "symptoms": ["Asymmetric blotchy yellow leaf mottling", "Yellow shoots and sparse canopy", "Small, lopsided fruit with uneven color"],
        "organic_treatment": ["There is no curative treatment; contact local plant-health authorities", "Do not move suspect citrus plants or budwood"],
        "prevention": ["Use certified disease-free planting material", "Monitor psyllids using local guidance"],
    },
    "Peach___Bacterial_spot": {
        "description": "Bacterial spot can affect peach leaves and fruit, especially in warm, wet conditions.",
        "symptoms": ["Small dark angular leaf spots", "Yellow halos or shot-hole appearance", "Sunken dark fruit spots"],
        "organic_treatment": ["Remove affected fallen leaves", "Ask local extension services about approved controls"],
        "prevention": ["Use resistant varieties where available", "Avoid overhead irrigation and prolonged leaf wetness"],
    },
    "Pepper,_bell___Bacterial_spot": {
        "description": "Bacterial spot causes lesions on pepper leaves, stems, and fruit.",
        "symptoms": ["Small dark angular leaf spots", "Yellowing and leaf drop", "Raised scabby spots on fruit"],
        "organic_treatment": ["Remove infected debris", "Avoid handling wet plants", "Consult local extension guidance"],
        "prevention": ["Use clean seed and transplants", "Rotate away from peppers and tomatoes", "Avoid overhead watering"],
    },
    "Squash___Powdery_mildew": {
        "description": "Powdery mildew is a fungal disease common on squash leaves in warm conditions.",
        "symptoms": ["White powdery patches on leaves", "Yellowing and drying of affected leaves", "Reduced vigor when severe"],
        "organic_treatment": ["Remove severely affected leaves", "Improve airflow and avoid excess nitrogen"],
        "prevention": ["Space plants for airflow", "Water at soil level and monitor early symptoms"],
    },
    "Strawberry___Leaf_scorch": {
        "description": "Strawberry leaf scorch is a fungal disease that causes reddish-brown leaf lesions.",
        "symptoms": ["Small dark purple spots with brown centers", "Spots merge into scorched-looking areas", "Leaf edges may dry"],
        "organic_treatment": ["Remove old infected leaves and plant debris", "Maintain airflow and avoid wetting foliage"],
        "prevention": ["Use healthy planting stock", "Keep beds open and remove diseased debris"],
    },
    "Tomato___Bacterial_spot": {
        "description": "Bacterial spot affects tomato foliage and fruit, particularly in warm, wet weather.",
        "symptoms": ["Small dark water-soaked leaf spots", "Yellowing and leaf drop", "Raised scabby spots on fruit"],
        "organic_treatment": ["Remove infected debris", "Avoid handling wet plants", "Ask local extension services about approved controls"],
        "prevention": ["Use clean seed and transplants", "Rotate crops", "Avoid overhead irrigation"],
    },
    "Tomato___Septoria_leaf_spot": {
        "description": "Septoria leaf spot is a fungal disease that commonly begins on older tomato leaves.",
        "symptoms": ["Many small circular spots with dark margins", "Pale centers with tiny dark specks", "Lower leaves yellow and dry"],
        "organic_treatment": ["Remove infected lower leaves and fallen debris", "Keep foliage dry and improve airflow"],
        "prevention": ["Rotate crops", "Mulch to reduce soil splash", "Avoid overhead watering"],
    },
    "Tomato___Spider_mites Two-spotted_spider_mite": {
        "description": "Two-spotted spider mites are tiny sap-feeding pests that thrive in hot, dry conditions.",
        "symptoms": ["Fine pale stippling on leaves", "Bronzing or yellowing", "Fine webbing under leaves in heavier infestations"],
        "organic_treatment": ["Check leaf undersides and rinse plants with water", "Protect beneficial predatory insects"],
        "prevention": ["Reduce plant stress with steady watering", "Inspect leaf undersides regularly"],
    },
    "Tomato___Target_Spot": {
        "description": "Target spot is a fungal disease that causes circular lesions on tomato leaves and fruit.",
        "symptoms": ["Brown circular leaf spots with faint rings", "Yellowing around lesions", "Dark sunken fruit spots may occur"],
        "organic_treatment": ["Remove infected lower leaves and crop debris", "Improve airflow and reduce leaf wetness"],
        "prevention": ["Rotate crops", "Use mulch to reduce soil splash", "Avoid overhead irrigation"],
    },
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "description": "Tomato yellow leaf curl is a viral disease commonly spread by whiteflies.",
        "symptoms": ["Upward-curling yellow leaves", "Stunted growth and shortened internodes", "Poor fruit set"],
        "organic_treatment": ["There is no curative treatment; remove severely affected plants where appropriate", "Manage whiteflies with local integrated pest guidance"],
        "prevention": ["Use resistant varieties and healthy transplants", "Monitor whiteflies and remove host weeds"],
    },
    "Tomato___Tomato_mosaic_virus": {
        "description": "Tomato mosaic virus is contagious and can spread through contact and contaminated tools.",
        "symptoms": ["Mottled light and dark green leaves", "Leaf distortion or narrowing", "Stunted growth and uneven fruit"],
        "organic_treatment": ["There is no curative treatment; remove affected plants carefully", "Clean hands and tools after handling suspect plants"],
        "prevention": ["Use certified seed and transplants", "Sanitize tools and avoid tobacco contact before handling plants"],
    },
}

def get_disease_info(disease):
    """Return a consistent info shape, even when a class lacks curated data."""
    info = disease_db.get(disease)
    if info is None:
        info = _SUPPLEMENTAL_INFO.get(disease)
    if disease.endswith("healthy") and not (info or {}).get("symptoms"):
        info = info or _HEALTHY_INFO
        info = {**info, "symptoms": _HEALTHY_INFO["symptoms"]}
    if info is not None:
        return {
            "description": info.get("description", "Disease information unavailable."),
            "symptoms": info.get("symptoms") or [],
            "organic_treatment": info.get("organic_treatment") or [],
            "prevention": info.get("prevention") or [],
        }

    return {
        "description": "Curated information is not available for this class yet.",
        "symptoms": [],
        "organic_treatment": [],
        "prevention": [],
    }
