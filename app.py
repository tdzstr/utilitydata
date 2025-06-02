import streamlit as st
import pandas as pd
import openai
import plotly.express as px
import os

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

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
    prompt = f"""
You are a data visualization assistant. Based on the following dataframe metadata and sample data, suggest 3 chart ideas.

Metadata:
{metadata}

Sample data:
{sample_data}

For each suggestion, provide:
1. Chart type (line, bar, pie, scatter, etc.)
2. X and Y axis columns
3. Short reason for the suggestion

Respond in JSON format like:
[
  {"chart_type": "line", "x": "Month", "y": "Revenue", "reason": "Track revenue over time"}
]
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in data visualization."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )

        suggestions = eval(response.choices[0].message.content)

        for i, suggestion in enumerate(suggestions):
            chart_type = suggestion["chart_type"].lower()
            x = suggestion["x"]
            y = suggestion["y"]
            reason = suggestion["reason"]

            st.markdown(f"### Chart {i+1}: {chart_type.title()} – {reason}")
            if chart_type == "line":
                fig = px.line(df, x=x, y=y)
            elif chart_type == "bar":
                fig = px.bar(df, x=x, y=y)
            elif chart_type == "scatter":
                fig = px.scatter(df, x=x, y=y)
            elif chart_type == "pie":
                fig = px.pie(df, names=x, values=y)
            else:
                st.warning(f"Unsupported chart type: {chart_type}")
                continue

            st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Failed to generate visualizations: {e}")
