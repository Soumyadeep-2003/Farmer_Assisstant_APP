import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import os
from utils.image_processing import analyze_crop_image, calculate_ndvi
from utils.data_manager import load_historical_data, save_analysis_result
from utils.visualization import plot_health_history, plot_health_metrics
from utils.auth import init_auth_db, init_session_state, login_required, display_login_page
from utils.crop_manager import save_crop_details, get_user_crops, get_user_id

# Initialize authentication database and session state
init_auth_db()
init_session_state()

# Page configuration
st.set_page_config(
    page_title="AgriSense",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        margin-top: 1rem;
    }
    .css-1v0mbdj.ebxwdo61 {
        width: 100%;
        margin-top: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

@login_required
def show_crop_details():
    st.title("🌱 Crop Details")

    # Get existing crops for the user
    user_id = get_user_id(st.session_state.username)
    existing_crops = get_user_crops(user_id)

    col1, col2 = st.columns(2)

    with col1:
        st.header("Add New Crop")
        with st.form("crop_details_form"):
            crop_name = st.text_input("Crop Name (e.g., Winter Wheat 2025)")
            crop_type = st.selectbox("Crop Type", [
                "Wheat", "Corn", "Soybeans", "Rice", "Cotton", 
                "Potatoes", "Other"
            ])
            planting_date = st.date_input("Planting Date")
            field_size = st.number_input("Field Size (hectares)", min_value=0.1, step=0.1)
            field_location = st.text_input("Field Location (optional)")

            submit = st.form_submit_button("Add Crop")
            if submit:
                if save_crop_details(user_id, crop_name, crop_type, planting_date, 
                                   field_size, field_location):
                    st.success("✅ Crop details saved successfully!")
                    st.rerun()
                else:
                    st.error("Error saving crop details. Please try again.")

    with col2:
        st.header("Your Crops")
        if existing_crops.empty:
            st.info("No crops added yet. Use the form on the left to add your first crop!")
        else:
            for _, crop in existing_crops.iterrows():
                with st.expander(f"🌾 {crop['crop_name']}"):
                    st.write(f"**Type:** {crop['crop_type']}")
                    st.write(f"**Planted:** {crop['planting_date']}")
                    st.write(f"**Field Size:** {crop['field_size']} hectares")
                    if crop['field_location']:
                        st.write(f"**Location:** {crop['field_location']}")

                    # Add a button to view this crop's dashboard
                    if st.button("View Dashboard", key=f"view_{crop['id']}"):
                        st.session_state.selected_crop_id = crop['id']
                        st.session_state.selected_crop_name = crop['crop_name']
                        st.rerun()

@login_required
def show_main_content():
    # Sidebar with navigation and info
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/farm.png", width=100)
        st.title(f"Welcome, {st.session_state.username}!")
        page = st.radio("Navigation", ["Crop Details", "Dashboard", "Crop Analysis", "Historical Data"])

        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.username = None
            st.rerun()

        st.markdown("---")
        st.markdown("### About")
        st.markdown("""
            AgriSense helps you monitor your crops through:
            - 📸 Image Analysis
            - 📊 Health Tracking
            - 📈 Historical Data
        """)

    # Main content
    if page == "Crop Details":
        show_crop_details()
    elif page == "Dashboard":
        st.title("🌾 AgriSense Dashboard")

        if hasattr(st.session_state, 'selected_crop_name'):
            st.subheader(f"Viewing: {st.session_state.selected_crop_name}")

        st.markdown("""
        Welcome to AgriSense! This tool helps you:

        1. **Analyze Crop Images** - Upload field photos for instant health assessment
        2. **Track Health Metrics** - Monitor NDVI scores and stress levels
        3. **View Historical Data** - Track changes over time with detailed analytics

        Get started by selecting an option from the sidebar! 👈
        """)

        # Display quick stats if data available
        data = load_historical_data()
        if not data.empty:
            st.markdown("### Quick Stats")
            col1, col2, col3 = st.columns(3)
            with col1:
                latest = data['ndvi'].iloc[-1]
                st.metric("Current Health", f"{latest:.2f}", "Active")
            with col2:
                avg = data['ndvi'].mean()
                st.metric("Average Health", f"{avg:.2f}")
            with col3:
                trend = data['ndvi'].iloc[-1] - data['ndvi'].iloc[0]
                st.metric("Health Trend", f"{trend:+.2f}")

    elif page == "Crop Analysis":
        st.title("📸 Crop Analysis")
        st.markdown("""
        Upload an image of your crop field for instant health analysis and disease detection. 
        The system will analyze vegetation health, detect potential diseases, and provide recommendations.
        """)

        uploaded_file = st.file_uploader("Choose a field image (JPG, PNG)", type=['jpg', 'jpeg', 'png'])

        if uploaded_file:
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["Analysis Results", "Disease Detection", "Detailed Metrics"])

            with tab1:
                col1, col2 = st.columns(2)
                with col1:
                    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)

                with col2:
                    with st.spinner("Analyzing image..."):
                        analysis_results = analyze_crop_image(uploaded_file)
                        ndvi_score = calculate_ndvi(analysis_results['green_ratio'], analysis_results['nir_estimate'])

                        st.success("✅ Analysis Complete!")
                        st.metric("Overall Health Score", f"{ndvi_score:.2f}")

                        # Color-coded stress level
                        stress_level = "Low" if ndvi_score > 0.6 else "Medium" if ndvi_score > 0.4 else "High"
                        stress_color = "green" if stress_level == "Low" else "orange" if stress_level == "Medium" else "red"
                        st.markdown(f"### Stress Level: <span style='color:{stress_color}'>{stress_level}</span>", unsafe_allow_html=True)

            with tab2:
                st.header("🔍 Disease Detection Results")
                if analysis_results['disease_detection']['success']:
                    disease_info = analysis_results['disease_detection']['disease_info']

                    # Display disease information in an organized way
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"### Detection Results")
                        st.markdown(f"**Condition:** {disease_info['name']}")
                        st.markdown(f"**Confidence:** {disease_info['confidence']}")
                        st.markdown(f"**Severity:** {disease_info['severity']}")
                        st.markdown(f"**Description:** {disease_info['description']}")

                    with col2:
                        st.markdown("### Recommendations")
                        for rec in analysis_results['disease_detection']['recommendations']:
                            st.markdown(f"- {rec}")
                else:
                    st.error("Error in disease detection. Please try again with a clearer image.")

            with tab3:
                st.markdown("### Detailed Metrics")
                metrics_col1, metrics_col2 = st.columns(2)
                with metrics_col1:
                    st.metric("Vegetation Coverage", f"{analysis_results['green_ratio']*100:.1f}%")
                with metrics_col2:
                    st.metric("NIR Reflection", f"{analysis_results['nir_estimate']:.2f}")

                if st.button("Save Analysis"):
                    save_analysis_result({
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'ndvi': ndvi_score,
                        'green_ratio': analysis_results['green_ratio'],
                        'stress_level': stress_level,
                        'disease_detection': analysis_results['disease_detection']['disease_info']['name']
                        if analysis_results['disease_detection']['success'] else 'Not detected'
                    })
                    st.success("✅ Analysis saved successfully!")

    elif page == "Historical Data":
        st.title("📊 Historical Analysis")

        historical_data = load_historical_data()

        if not historical_data.empty:
            # Time range selector
            st.markdown("### Select Time Range")
            date_range = st.date_input(
                "Choose date range",
                value=(datetime.strptime(historical_data['date'].iloc[0], '%Y-%m-%d').date(),
                       datetime.strptime(historical_data['date'].iloc[-1], '%Y-%m-%d').date())
            )

            # Filter data based on selection
            filtered_data = historical_data

            # Display interactive plots
            st.plotly_chart(plot_health_history(filtered_data), use_container_width=True)
            st.plotly_chart(plot_health_metrics(filtered_data), use_container_width=True)

            # Detailed data table
            st.markdown("### Detailed Records")
            st.dataframe(filtered_data.style.highlight_max(subset=['ndvi'], color='lightgreen')
                        .highlight_min(subset=['ndvi'], color='lightpink'))
        else:
            st.info("👋 No historical data available yet. Start by analyzing some images!")

    # Footer
    st.markdown("---")
    st.markdown("### Need Help?")
    st.markdown("""
        - 📸 For best results, take photos in good lighting conditions
        - 📊 Regular monitoring helps track crop health trends
        - 💾 All analysis results are automatically saved
    """)

def main():
    if not st.session_state.authenticated:
        display_login_page()
    else:
        show_main_content()

if __name__ == "__main__":
    main()
