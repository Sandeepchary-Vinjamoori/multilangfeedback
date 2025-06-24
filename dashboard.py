import streamlit as st
import pandas as pd
from transformers import pipeline
import matplotlib.pyplot as plt
import pydeck as pdk
import pyrebase
from datetime import datetime

# --- Firebase config & init ---
firebaseConfig = {
    "apiKey": "AIzaSyBYUMGigzJo-UUzP7HglYcLQy9vYelpE7I",
    "authDomain": "multi-lingual-feedback.firebaseapp.com",
    "projectId": "multi-lingual-feedback",
    "storageBucket": "multi-lingual-feedback.appspot.com",
    "messagingSenderId": "71752941166",
    "appId": "1:71752941166:web:a3f54e6e7fe01e3579f07f",
    "databaseURL": "https://multi-lingual-feedback-default-rtdb.firebaseio.com/"
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()

# --- Authentication UI functions ---
def signup():
    st.subheader("🆕 Create New Account")
    new_email = st.text_input("Email", key="signup_email")
    new_password = st.text_input("Password", type="password", key="signup_password")
    if st.button("Sign Up"):
        try:
            auth.create_user_with_email_and_password(new_email, new_password)
            st.success("User created successfully! Please log in.")
            st.rerun()
        except Exception as e:
            try:
                error_json = e.args[1]
                error_message = eval(error_json)['error']['message']
            except Exception:
                error_message = str(e)
            st.error(f"Error creating user: {error_message}")

def login():
    st.subheader("🔐 Login to Your Account")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            st.success("Logged in successfully!")
            st.session_state['user'] = user
            st.rerun()
        except Exception as e:
            try:
                error_json = e.args[1]
                error_message = eval(error_json)['error']['message']
            except Exception:
                error_message = str(e)
            st.error(f"Login failed: {error_message}")

# --- Main app ---
if 'user' not in st.session_state:
    st.session_state['user'] = None

# Sidebar auth mode selection
auth_mode = st.sidebar.radio("Choose Authentication Mode", ["Login", "Sign Up"])

if st.session_state['user'] is None:
    if auth_mode == "Sign Up":
        signup()
    else:
        login()
else:
    st.title("📦 Multi-Lingual Product Review Analyzer")

    @st.cache_resource
    def load_pipelines():
        lang_model = pipeline("text-classification", model="papluca/xlm-roberta-base-language-detection")
        senti_model = pipeline("sentiment-analysis", model="nlptown/bert-base-multilingual-uncased-sentiment")
        return lang_model, senti_model

    language_detector, sentiment_analyzer = load_pipelines()

    def map_sentiment(label):
        if "1" in label or "2" in label:
            return "Negative"
        elif "3" in label:
            return "Neutral"
        else:
            return "Positive"

    country_coords = {
        'USA/UK/Australia': [37.0902, -95.7129],
        'Spain/Latin America': [40.4637, -3.7492],
        'France': [46.6034, 1.8883],
        'Germany': [51.1657, 10.4515],
        'China': [35.8617, 104.1954],
        'India': [20.5937, 78.9629],
        'Portugal/Brazil': [-14.2350, -51.9253],
        'Italy': [41.8719, 12.5674],
        'Japan': [36.2048, 138.2529],
        'South Korea': [35.9078, 127.7669],
        'Russia': [61.5240, 105.3188],
        'Other': [0, 0]
    }

    uploaded_file = st.file_uploader("Upload a CSV file with reviews", type="csv")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        st.subheader("📁 Uploaded Data Preview")
        st.dataframe(df.head())

        max_rows = st.number_input("Limit number of rows to analyze (0 = All)", min_value=0, value=min(500, len(df)))
        if max_rows > 0:
            df = df.head(max_rows)

        review_col = st.selectbox("📝 Select the column containing review text:", df.columns)

        feature_col = None
        if 'feature' in df.columns:
            feature_col = 'feature'
        else:
            feature_col = st.selectbox("🏷 Select a column to group reviews by feature (optional):", [None] + list(df.columns))

        if review_col:
            st.info("🔍 Analyzing reviews... This may take a few minutes.")
            results = []

            lang_to_country = {
                'en': 'USA/UK/Australia', 'es': 'Spain/Latin America',
                'fr': 'France', 'de': 'Germany', 'zh': 'China',
                'hi': 'India', 'pt': 'Portugal/Brazil', 'it': 'Italy',
                'ja': 'Japan', 'ko': 'South Korea', 'ru': 'Russia',
            }

            progress = st.progress(0)
            for i, (_, row) in enumerate(df.iterrows()):
                try:
                    review = str(row[review_col])
                    feature = row[feature_col] if feature_col else "General"
                    lang = language_detector(review)[0]['label']
                    raw_senti = sentiment_analyzer(review)[0]
                    senti = map_sentiment(raw_senti['label'])
                    score = raw_senti['score']
                    country = lang_to_country.get(lang, 'Other')

                    results.append({
                        "Review": review,
                        "Feature": feature,
                        "Language": lang,
                        "Country": country,
                        "Sentiment": senti,
                        "Confidence": round(score, 2)
                    })
                except:
                    continue
                finally:
                    progress.progress((i + 1) / len(df))

            st.success("✅ Analysis complete!")

            output_df = pd.DataFrame(results)

            # 📝 Save to Firebase Realtime DB per user session
            user_id = st.session_state['user']['localId']
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            session_ref = db.child("users").child(user_id).child("sessions").child(timestamp)

            sentiment_counts = output_df['Sentiment'].value_counts()
            majority_sentiment = sentiment_counts.idxmax()

            session_ref.update({
                "filename": uploaded_file.name,
                "review_count": len(results),
                "analyzed_at": timestamp,
                "majority_sentiment": majority_sentiment
            })

            st.success("📤 Analysis results saved to your Firebase account.")

            st.subheader("📝 All Reviews Analyzed")
            st.dataframe(output_df)

            # ✅ Negative Alert Block
            with st.expander("🔍 Insights & Alerts"):
                total_reviews = len(output_df)
                negative_count = output_df[output_df['Sentiment'] == 'Negative'].shape[0]
                negative_percentage = (negative_count / total_reviews) * 100 if total_reviews > 0 else 0

                st.write(f"📊 Total Reviews: {total_reviews}")
                st.write(f"📉 Negative Reviews: {negative_count} ({negative_percentage:.2f}%)")

                if negative_percentage > 20:
                    st.error(f"🚨 High Negative Sentiment Detected: {negative_percentage:.2f}% of reviews are negative.")
                else:
                    st.success(f"✅ Negative Sentiment is within acceptable range: {negative_percentage:.2f}%")

            st.subheader("📊 Feature-wise Sentiment Summary")
            summary = output_df.groupby(['Feature', 'Sentiment']).size().unstack(fill_value=0)
            st.dataframe(summary)
            st.bar_chart(summary)

            st.subheader("🌍 Reviews Count by Country")
            country_counts = output_df['Country'].value_counts()
            st.bar_chart(country_counts)

            st.subheader("🟢 Positive Reviews by Country")
            positive_counts = output_df[output_df['Sentiment'] == 'Positive']['Country'].value_counts()
            st.bar_chart(positive_counts)

            st.subheader("🗺 Positive Review Hotspots (World Map)")
            map_data = output_df[output_df['Sentiment'] == 'Positive'].groupby('Country').size().reset_index(name='Count')
            map_data[['lat', 'lon']] = map_data['Country'].apply(lambda x: pd.Series(country_coords.get(x, [0, 0])))

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_data,
                get_position='[lon, lat]',
                get_color='[0, 180, 0, 160]',
                get_radius='Count * 20000',
                pickable=True,
            )

            view_state = pdk.ViewState(latitude=20, longitude=0, zoom=1.2)
            deck = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "{Country}\nPositive Reviews: {Count}"})
            st.pydeck_chart(deck)

            st.subheader("🧠 Overall Sentiment Summary")
            overall = output_df['Sentiment'].value_counts()
            st.write(overall)

            st.subheader("📈 Sentiment Distribution Pie Chart")
            fig, ax = plt.subplots()
            ax.pie(overall, labels=overall.index, autopct='%1.1f%%', startangle=90)
            ax.axis('equal')
            st.pyplot(fig)

            st.success("🎯 Dashboard Ready!")

    if st.button("Logout"):
        st.session_state['user'] = None
        st.experimental_rerun()
