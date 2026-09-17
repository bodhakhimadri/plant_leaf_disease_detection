import tempfile
from pathlib import Path

import streamlit as st
from PIL import Image

from backend.src.knowledge_base import get_disease_info
from backend.src.predict import predict_disease
from backend.src.reports import save_report

try:
    from backend.src.llm_report import generate_report
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


def show_detection_page():
    st.title("LeafCare")
    st.markdown("""
    ### Detect Plant Diseases Instantly

    Upload a plant leaf image and receive:

    - Hybrid disease prediction
    - Field Trust Score
    - Symptoms and organic treatment guidance
    - Optional AI-generated report
    - Community disease alerts
    """)
    st.caption("Supported Crops: Apple • Corn • Grape • Potato • Tomato")
    st.divider()

    feature_1, feature_2, feature_3 = st.columns(3)
    feature_1.info("Disease Detection")
    feature_2.info("AI Reports")
    feature_3.info("Community Alerts")
    st.divider()

    uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "jpeg", "png"])
    if uploaded_file is None:
        return

    image = Image.open(uploaded_file).convert("RGB")
    image_column, result_column = st.columns([1, 1])
    with image_column:
        st.image(image, caption="Uploaded Leaf", use_container_width=True)

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temporary_file:
            temporary_path = Path(temporary_file.name)
            image.save(temporary_path)
        result = predict_disease(temporary_path)
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)

    if not result["success"]:
        st.error(result["message"])
        return

    disease_name = result["disease"]
    confidence = result["confidence"]
    trust_score = result["field_trust_score"]
    with result_column:
        st.success("Prediction Complete")
        st.metric("Detected Disease", disease_name.replace("_", " "))
        st.metric("Confidence", f"{confidence:.2f}%")
        st.progress(min(int(confidence), 100))
        if confidence >= 90:
            st.success("High confidence prediction")
        elif confidence >= 70:
            st.warning("Moderate confidence prediction")
        else:
            st.error("Low confidence prediction")

    st.divider()
    st.header("Field Trust Score")
    st.caption("LeafCare combines diagnosis confidence with image quality and, when available, agreement between two models.")
    trust_column, quality_column, agreement_column = st.columns(3)
    trust_column.metric("Trust Score", f"{trust_score}/100")
    quality_column.metric("Photo Quality", f"{result['photo_quality']['score']}/100")
    agreement = result["model_agreement"]
    agreement_column.metric("Model Agreement", f"{agreement:.1f}%" if agreement is not None else "Not enabled")
    if trust_score < 65:
        st.warning("Retake the photo before acting on this diagnosis.")
    with st.expander("How to improve the Field Trust Score"):
        for tip in result["photo_quality"]["tips"]:
            st.write(f"• {tip}")

    st.subheader("Top 3 possible diagnoses")
    for rank, candidate in enumerate(result["top_predictions"], start=1):
        st.write(f"{rank}. **{candidate['disease'].replace('_', ' ')}** — {candidate['confidence']:.2f}%")

    try:
        disease_info = get_disease_info(disease_name)
        st.divider()
        st.header("Disease Information")
        st.write(disease_info.get("description", "Information unavailable."))
        with st.expander("Symptoms"):
            for symptom in disease_info.get("symptoms", []):
                st.write(f"• {symptom}")
        with st.expander("Organic Treatment Recommendations"):
            for treatment in disease_info.get("organic_treatment", []):
                st.write(f"• {treatment}")
    except Exception as error:
        st.warning(f"Disease information unavailable: {error}")

    st.divider()
    st.header("AI Disease Report")
    if not LLM_AVAILABLE:
        st.warning("LLM service is unavailable.")
        return
    if st.button("Generate AI Report", use_container_width=True):
        with st.spinner("Generating AI report..."):
            try:
                report = generate_report(disease_name, confidence)
                st.markdown(report)
                try:
                    save_report(disease_name, confidence, report)
                    st.success("Report saved successfully.")
                except Exception as save_error:
                    st.warning(f"The report was generated but could not be saved: {save_error}")
            except Exception as error:
                st.error(f"Report generation failed: {error}")
