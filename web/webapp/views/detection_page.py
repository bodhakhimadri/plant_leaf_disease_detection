import streamlit as st
from PIL import Image
import tempfile

from backend.src.predict import predict_disease
# import inspect

# st.write(inspect.getfile(predict_disease))
from backend.src.knowledge_base import get_disease_info
from backend.src.reports import save_report

try:
    from backend.src.llm_report import generate_report
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


def show_detection_page():

    
    # ---------- Hero Section ---------- 

    st.title("LeafCare")

    st.markdown("""
    ### Detect Plant Diseases Instantly

    Upload a plant leaf image and receive:

    - Disease Prediction
    - Confidence Score
    - Symptoms Analysis
    - Organic Treatments
    - AI Generated Report
    - Community Disease Alerts
    """)

    st.caption(
        "Supported Crops: Apple • Corn • Grape • Potato • Tomato"
    )

    st.divider()

    
    # ---------- Feature Cards ---------- 

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("Disease Detection")

    with col2:
        st.info("AI Reports")

    with col3:
        st.info("Community Alerts")

    st.divider()

   
    # ---------- Upload Image ---------- 

    uploaded_file = st.file_uploader(
        "Upload Leaf Image",
        type=["jpg", "jpeg", "png"]
    )

    if uploaded_file is None:
        return

    image = Image.open(uploaded_file).convert("RGB")

    col1, col2 = st.columns([1, 1])

    
    # ---------- Display Image ---------- 

    with col1:

        st.image(
            image,
            caption="Uploaded Leaf",
            use_container_width=True
        )

    
    # ---------- Prediction ---------- 

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".jpg"
    ) as tmp:

        image.save(tmp.name)

        result = predict_disease(tmp.name)
        # st.write(type(result))
        # st.write(result)
        if not result["success"]:
            st.error(result["message"])
            return

        disease_name = result["disease"]
        confidence = result["confidence"]

    with col2:

        st.success("Prediction Complete")

        st.metric(
            "Detected Disease",
            disease_name.replace("_", " ")
        )

        st.metric(
            "Confidence",
            f"{confidence:.2f}%"
        )

        if confidence >= 90:

            st.success(
                "High Confidence Prediction"
            )

        elif confidence >= 70:

            st.warning(
                "Moderate Confidence Prediction"
            )

        else:

            st.error(
                "Low Confidence Prediction"
            )

        st.progress(
            min(
                int(confidence),
                100
            )
        )


    # ---------- Disease Information ---------- 

    try:

        disease_info = get_disease_info(
            disease_name
        )

        st.divider()

        st.header(
            "Disease Information"
        )

        st.write(
            disease_info.get(
                "description",
                "Information unavailable."
            )
        )

        with st.expander(
            "Symptoms"
        ):

            symptoms = disease_info.get(
                "symptoms",
                []
            )

            for symptom in symptoms:

                st.write(
                    f"• {symptom}"
                )

        with st.expander(
            "Organic Treatment Recommendations"
        ):

            treatments = disease_info.get(
                "organic_treatment",
                []
            )

            for treatment in treatments:

                st.write(
                    f"• {treatment}"
                )

    except Exception as e:

        st.warning(
            f"Disease information unavailable: {e}"
        )


    # ---------- AI Report ---------- 

    st.divider()

    st.header(
        "AI Disease Report"
    )

    if not LLM_AVAILABLE:

        st.warning(
            "LLM service is unavailable."
        )

        return

    if st.button(
        "Generate AI Report",
        use_container_width=True
    ):

        with st.spinner(
            "Generating AI report..."
        ):

            try:

                report = generate_report(
                    disease_name,
                    confidence
                )

                st.markdown(
                    report
                )

                try:
                    save_report(
                        disease_name,
                        confidence,
                        report
                    )
                    st.success(
                        "Report saved successfully."
                    )
                except Exception as save_error:
                    st.warning(
                        f"The report was generated but could not be saved: {save_error}"
                    )

            except Exception as e:

                st.error(
                    f"Report generation failed: {e}"
                )
