"""Photo quality and confidence helpers used with the single classifier."""

import cv2


def analyse_photo_quality(image_path):
    """Return an explainable score for focus and exposure of a field photo."""
    image = cv2.imread(str(image_path))
    if image is None:
        return {"score": 0, "tips": ["Use a readable JPG or PNG image."]}
    grayscale = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(grayscale.mean())
    focus = float(cv2.Laplacian(grayscale, cv2.CV_64F).var())
    exposure = max(0.0, 1.0 - abs(brightness - 130) / 130)
    focus_score = min(focus / 160, 1.0)
    score = round((exposure * 0.45 + focus_score * 0.55) * 100)
    tips = []
    if brightness < 60:
        tips.append("Use even daylight; this photo is too dark.")
    elif brightness > 215:
        tips.append("Avoid direct glare; this photo is overexposed.")
    if focus < 55:
        tips.append("Move closer and focus on the affected leaf before taking another photo.")
    return {"score": score, "tips": tips or ["Photo exposure and focus are suitable for analysis."]}


def field_trust_score(confidence, quality_score):
    """Score confidence and image quality for a single-model prediction."""
    return round(0.75 * confidence + 0.25 * quality_score)
