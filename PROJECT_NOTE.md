# LeafCare: Project Note

LeafCare is a Streamlit-based plant-leaf disease detection system. It accepts a
leaf photograph, identifies the most likely plant disease, provides practical
treatment information, and can generate a short AI disease report.

## Working flow

1. **User access:** Users register and sign in through Supabase Authentication.
2. **Image upload:** The user uploads a JPG or PNG leaf image.
3. **Leaf validation:** A dedicated binary model checks whether the image is a
   plant leaf. Images below the 75% leaf-confidence threshold are rejected.
4. **Disease prediction:** The image is resized to 128 × 128 and analysed by
   the primary MobileNetV2 disease classifier.
5. **Hybrid prediction:** If the optional EfficientNetB0 model is available
   and compatible, its probabilities are averaged with MobileNetV2. Otherwise,
   the application safely uses MobileNetV2 alone.
6. **Trust and guidance:** The app shows the top three diagnoses, prediction
   confidence, photo-quality score, model agreement (when hybrid mode is on),
   and the LeafCare Field Trust Score.
7. **Report and history:** Gemini can create a 150–200 word farmer report.
   Reports, user profiles, history, dashboard data, and community alerts are
   stored through Supabase.

## Models

| Component | Model / method | Purpose |
| --- | --- | --- |
| Leaf validator | MobileNetV2-based binary classifier | Accepts leaf images and rejects non-leaf images. |
| Primary disease classifier | MobileNetV2 | Predicts one of 38 plant disease or healthy classes. |
| Optional ensemble classifier | EfficientNetB0 | Blends its class probabilities with MobileNetV2 for hybrid prediction. |
| Image-quality analysis | OpenCV | Measures focus and exposure for better field-photo advice. |
| AI report generator | Gemini API | Produces a concise farmer-oriented disease report. |

## Field Trust Score

The Field Trust Score is LeafCare's distinguishing feature. It combines model
confidence with image focus and exposure. When the EfficientNet model is
enabled, agreement between both classifiers is included as well. A low score
encourages the user to retake the photograph before making a treatment decision.

## Supported crops and conditions (38 classes)

- **Apple:** Apple scab, black rot, cedar apple rust, healthy.
- **Blueberry:** healthy.
- **Cherry:** powdery mildew, healthy.
- **Corn (maize):** Cercospora/gray leaf spot, common rust, northern leaf blight, healthy.
- **Grape:** black rot, Esca (black measles), leaf blight (Isariopsis leaf spot), healthy.
- **Orange:** Huanglongbing (citrus greening).
- **Peach:** bacterial spot, healthy.
- **Bell pepper:** bacterial spot, healthy.
- **Potato:** early blight, late blight, healthy.
- **Raspberry:** healthy.
- **Soybean:** healthy.
- **Squash:** powdery mildew.
- **Strawberry:** leaf scorch, healthy.
- **Tomato:** bacterial spot, early blight, late blight, leaf mold, Septoria leaf spot, spider-mite damage, target spot, tomato yellow leaf curl virus, tomato mosaic virus, healthy.

## Main technologies

Streamlit powers the user interface; TensorFlow/Keras and OpenCV provide image
analysis; Supabase manages authentication and data; Gemini generates reports;
and Plotly supports dashboard visualizations.
