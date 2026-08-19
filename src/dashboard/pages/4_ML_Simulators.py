import os
import sys
from pathlib import Path

project_root = str(Path(__file__).resolve().parent.parent.parent.parent)
cwd = os.getcwd()
for p in [project_root, cwd]:
    if p not in sys.path:
        sys.path.insert(0, p)

import pandas as pd
import streamlit as st

from src.dashboard.api_client import APIClientError, api_client
from src.dashboard.components.auth_widget import render_auth_sidebar
from src.dashboard.components.charts import create_forecast_confidence_chart
from src.dashboard.components.ml_explainer import render_delivery_risk_explanation
from src.dashboard.components.ui_states import render_error_banner
from src.dashboard.theme import apply_custom_theme

apply_custom_theme()
render_auth_sidebar()

st.title("🔮 Predictive ML Scenario Simulator")
st.markdown("Interact directly with trained Phase 3 Machine Learning models for demand forecasting, shipment delay scoring, cross-sell recommendations, and review NLP.")

tabs = st.tabs([
    "📈 Sales Demand Forecast",
    "🚚 Delivery Delay Risk Scorer",
    "🛒 Cross-Sell Recommender",
    "💬 Review Sentiment NLP",
])

# ----------------------------------------------------
# TAB 1: SALES FORECASTING
# ----------------------------------------------------
with tabs[0]:
    st.markdown("### 📈 Forward-Looking Sales Demand Forecaster")
    st.markdown("Recursive multi-step Ridge time-series forecaster with 95% confidence intervals.")

    c_ctrl, c_chart = st.columns([1, 3])
    with c_ctrl:
        horizon = st.slider("Forecast Horizon (Days)", min_value=7, max_value=90, value=30, step=7)
        btn_forecast = st.button("Generate Forecast 🚀", use_container_width=True)

    with c_chart:
        try:
            with st.spinner("Computing forward multi-horizon demand projection..."):
                forecast_res = api_client.forecast_sales(horizon_days=horizon)

            st.success(
                f"**Projected {horizon}-Day Total Revenue:** ${float(forecast_res.get('total_projected_revenue', 0.0)):,.2f} "
                f"*(Daily Avg: ${float(forecast_res.get('daily_average_projected_revenue', 0.0)):,.2f}/day)*"
            )
            daily_recs = forecast_res.get("daily_forecasts", [])
            st.plotly_chart(create_forecast_confidence_chart(daily_recs), use_container_width=True)

        except APIClientError as e:
            render_error_banner("Forecasting Error", str(e))

# ----------------------------------------------------
# TAB 2: DELIVERY DELAY RISK SCORING
# ----------------------------------------------------
with tabs[1]:
    st.markdown("### 🚚 Real-Time Logistics Delay Risk Assessment")
    st.markdown("HistGradientBoosting classifier evaluating package physical attributes, routing, and promised SLA days.")

    with st.form("delay_form"):
        r1c1, r1c2, r1c3 = st.columns(3)
        with r1c1:
            price = st.number_input("Item Price ($)", value=129.90, step=10.0)
            freight = st.number_input("Freight Cost ($)", value=24.50, step=5.0)
        with r1c2:
            weight = st.number_input("Weight (Grams)", value=1800.0, step=100.0)
            length = st.number_input("Length (cm)", value=25.0, step=5.0)
        with r1c3:
            height = st.number_input("Height (cm)", value=15.0, step=5.0)
            width = st.number_input("Width (cm)", value=20.0, step=5.0)

        r2c1, r2c2, r2c3 = st.columns(3)
        with r2c1:
            cust_state = st.selectbox("Customer State (Destination)", ["RJ", "SP", "MG", "BA", "RS", "PR", "SC", "DF", "GO", "PE"], index=0)
        with r2c2:
            sell_state = st.selectbox("Seller State (Origin)", ["SP", "RJ", "MG", "PR", "SC", "RS"], index=0)
        with r2c3:
            sla_days = st.slider("Promised SLA Days", min_value=3.0, max_value=45.0, value=18.0, step=1.0)

        category = st.selectbox(
            "Product Category",
            ["bed_bath_table", "health_beauty", "sports_leisure", "computers_accessories", "furniture_decor", "housewares", "auto", "toys"],
            index=0,
        )

        submit_delay = st.form_submit_button("Score Delivery Delay Risk 🎯", use_container_width=True)

    if submit_delay:
        try:
            payload = {
                "price": price,
                "freight_value": freight,
                "product_weight_g": weight,
                "product_length_cm": length,
                "product_height_cm": height,
                "product_width_cm": width,
                "estimated_delivery_days": sla_days,
                "customer_state": cust_state,
                "seller_state": sell_state,
                "category_name_english": category,
            }
            res_delay = api_client.predict_delay(payload)

            prob = float(res_delay.get("delay_probability", 0.0))
            is_delayed = int(res_delay.get("is_delay_predicted", 0))
            tier = str(res_delay.get("logistics_risk_tier", "Unknown"))
            recommendation = str(res_delay.get("recommendation", "Standard"))

            dc1, dc2 = st.columns([1, 1])
            with dc1:
                st.metric("Predicted Delay Probability", f"{prob*100:.1f}%", delta="Delay Predicted" if is_delayed == 1 else "On-Time Fulfillment", delta_color="inverse" if is_delayed == 1 else "normal")
            with dc2:
                st.metric("Logistics Operational Tier", tier, delta=recommendation)

            # Feature explanation component
            render_delivery_risk_explanation(
                delay_prob=prob,
                is_interstate=(cust_state != sell_state),
                weight_g=weight,
                freight_val=freight,
                sla_days=sla_days,
            )

        except APIClientError as e:
            render_error_banner("Prediction Failed", str(e))

# ----------------------------------------------------
# TAB 3: PRODUCT RECOMMENDATION
# ----------------------------------------------------
with tabs[2]:
    st.markdown("### 🛒 Product Cross-Sell & Complementary Recommender")
    st.markdown("Item-to-Item collaborative filtering and category affinity engine.")

    top_n = st.slider("Number of Recommendations", min_value=1, max_value=8, value=4)
    btn_rec = st.button("Generate Cross-Sell Recommendations 🛍️")

    if btn_rec:
        try:
            with st.spinner("Finding complementary product affinities..."):
                rec_res = api_client.recommend_products(top_n=top_n)

            recs = rec_res.get("recommendations", [])
            st.success(f"Generated {len(recs)} high-affinity complementary recommendations:")

            df_rec = pd.DataFrame(recs)
            if not df_rec.empty:
                st.dataframe(df_rec, use_container_width=True)

        except APIClientError as e:
            render_error_banner("Recommendation Failed", str(e))

# ----------------------------------------------------
# TAB 4: REVIEW SENTIMENT NLP
# ----------------------------------------------------
with tabs[3]:
    st.markdown("### 💬 Review Sentiment & Urgent Complaint Classifier")
    st.markdown("TF-IDF + Logistic Regression NLP classifier trained on Portuguese customer reviews.")

    sample_text = st.selectbox(
        "Select Example Review or Type Custom Text:",
        [
            "Produto excelente, entrega super rápida e embalagem perfeita!",
            "O produto chegou com defeito e a entrega atrasou mais de duas semanas. Péssimo atendimento!",
            "Chegou no prazo, porém a cor é um pouco diferente da foto do anúncio.",
            "Não recebi o meu pedido até hoje, ninguém responde no chat!",
        ],
        index=0,
    )
    user_review = st.text_area("Review Text:", value=sample_text, height=80)

    if st.button("Analyze Review Sentiment 🔍"):
        try:
            res_sent = api_client.analyze_sentiment(user_review)

            sent_tier = str(res_sent.get("sentiment_tier", "Unknown"))
            is_complaint = int(res_sent.get("is_complaint_predicted", 0))
            complaint_prob = float(res_sent.get("complaint_probability", 0.0))
            urgent = bool(res_sent.get("urgent_action_required", False))

            sc1, sc2 = st.columns(2)
            with sc1:
                st.metric("Sentiment Classification", sent_tier, delta="Priority Complaint" if is_complaint == 1 else "Positive Satisfaction", delta_color="inverse" if is_complaint == 1 else "normal")
            with sc2:
                st.metric("Dissatisfaction Probability", f"{complaint_prob*100:.1f}%", delta="⚠️ Urgent Action Required" if urgent else "Standard Routing")

        except APIClientError as e:
            render_error_banner("Sentiment Classification Failed", str(e))
