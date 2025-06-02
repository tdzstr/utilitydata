import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json
import re
from openai import OpenAI

# Set your OpenAI API key
client = OpenAI()

st.set_page_config(page_title="AI Dashboard Generator", layout="wide")
st.title("📊 AI-Powered CSV Dashboard")

uploaded_file = st.file_uploader("Upload your monthly CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader("Preview of your data")
    st.dataframe(df.head())

    st.subheader("Auto-generated visualizations")

    # Generate prompt
    metadata = df.dtypes.astype(str).to_dict()
    sample_data = df.head(3).to_dict()
    prompt = (
        "You are a data visualization assistant. Based on the following dataframe metadata and sample data, "
        "suggest 3 chart ideas.\n\n"
        f"Metadata:\n{metadata}\n\n"
        f"Sample data:\n{sample_data}\n\n"
        "For each suggestion, provide:\n"
        "1. Chart type (line, bar, pie, scatter, etc.)\n"
        "2. X and Y axis columns\n"
        "3. Short reason for the suggestion\n\n"
        "Respond in JSON format like:\n"
        "[\n"
        "  {\"chart_type\": \"line\", \"x\": \"Month\", \"y\": \"Revenue\", \"reason\": \"Track revenue over time\"}\n"
        "]"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in data visualization. Only reply in valid JSON without any extra commentary."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        raw_response = response.choices[0].message.content.strip()
        clean_response = re.sub(r"^```json|```$", "", raw_response).strip()
        suggestions = json.loads(clean_response)

        for i, suggestion in enumerate(suggestions):
            chart_type = suggestion["chart_type"].lower()
            x = suggestion["x"]
            y = suggestion["y"]
