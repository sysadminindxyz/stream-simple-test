
import streamlit as st
import pandas as pd
import plotly.express as px
import os
from databricks import sql


###
hide_streamlit_style = """
    <style>
        div[data-testid="stToolbar"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
        }
        div[data-testid="stDecoration"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
        }
        div[data-testid="stStatusWidget"] {
            visibility: hidden;
            height: 0%;
            position: fixed;
        }
        #MainMenu {
            visibility: hidden;
            height: 0%;
        }
        header {
            visibility: hidden;
            height: 0%;
        }
        footer {
            visibility: hidden;
            height: 0%;
        }
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Access secrets
db_host = st.secrets["databricks"]["host"]
db_token = st.secrets["databricks"]["token"]
http_path = st.secrets["databricks"]["http_path"]

conn = sql.connect(
    server_hostname=db_host,
    http_path=http_path,
    access_token=db_token,
)

# Example: query a Delta table
query = "SELECT * FROM tweets_delta_glp1"
cursor = conn.cursor()
cursor.execute(query)
rows=cursor.fetchall()
columns = [desc[0] for desc in cursor.description]
# Convert to DataFrame
df = pd.DataFrame(rows, columns=columns)

cursor.close()
conn.close()


# Load your data (replace this with your local CSV if needed)
# df = pd.read_csv("glp1_snacking_tweets_with_categorizations_and_authors.csv")
# df['created_at'] = pd.to_datetime(df['created_at'])

# --- Data summaries ---
df['created_at'] = pd.to_datetime(df['created_at'])
tweets_over_time = df.groupby(df['created_at'].dt.date).size().reset_index(name='tweet_count')
food_perception_counts = df['Food_Industry_Perceptions'].value_counts(dropna=True).reset_index()
food_perception_counts.columns = ['Perception', 'Count']

side_effect_counts = df['Personal_Experiences_and_Side_Effects'].value_counts(dropna=True).reset_index()
side_effect_counts.columns = ['SideEffectMention', 'Count']

top_tweet = df.sort_values(by='like_count', ascending=False).iloc[0]

# --- Page Config ---
st.set_page_config(page_title="GLP1 Social Media Dashboard", layout="wide")

st.title("💊 GLP1 Social Media Conversations — Snack Industry Analysis")

# --- High-level Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Tweets", len(df))
col2.metric("Top Tweet Likes", top_tweet['like_count'])
col3.metric("Top Tweet Retweets", top_tweet['retweet_count'])

# --- Tweets over time ---
st.subheader("📈 Tweet Volume Over Time")
fig_time = px.line(tweets_over_time, x='created_at', y='tweet_count', markers=True, title="Tweet Volume by Date")
st.plotly_chart(fig_time, use_container_width=True)

# --- Snack industry perception breakdown ---
st.subheader("🥨 Food Industry Perceptions in GLP1 Conversations")
fig_food = px.pie(food_perception_counts, names='Perception', values='Count', title="Food Industry Perception Breakdown")
st.plotly_chart(fig_food, use_container_width=True)

# --- Side effects mentions ---
st.subheader("⚠️ Side Effects Mentions")
fig_side = px.bar(side_effect_counts, x='SideEffectMention', y='Count', title="Side Effects Discussion Count")
st.plotly_chart(fig_side, use_container_width=True)

# --- Top tweet section ---
st.subheader("🔥 Top Tweet Highlight")
with st.container():
    st.markdown(f"""
    > **"{top_tweet['text']}"**  
    👍 {top_tweet['like_count']} likes | 🔁 {top_tweet['retweet_count']} retweets
    """)

# --- Add more optional deep dives ---
if st.checkbox("Show raw data table"):
    st.write(df)

st.markdown("---")
st.caption("Built for the snack food industry to monitor GLP1 social media trends.")