📦 Multi-Lingual Product Review Analyzer
A powerful, Streamlit-based interactive dashboard to automatically detect languages, analyze sentiments, and visualize global insights from product reviews — integrated seamlessly with Firebase for user authentication and real-time data storage.

🚀 Key Features
✅ User Authentication
Secure sign-up and login using Firebase Authentication.

✅ Multi-Language Detection
Uses papluca/xlm-roberta-base-language-detection to identify the language of each review.

✅ Sentiment Analysis
Leverages nlptown/bert-base-multilingual-uncased-sentiment to classify sentiments (Positive, Neutral, Negative).

✅ Real-Time Storage
Saves session analytics to Firebase Realtime Database for audit and user-specific tracking.

✅ Insightful Visualizations
Generates sentiment distributions, negative sentiment alerts, bar charts, pie charts, and a world map highlighting positive review hotspots.

🗂 Project Structure

📁 feedback/
 ├─ dashboard.py        # Main Streamlit app
 ├─ requirements.txt    # All Python dependencies
 ├─ .venv/              # Local virtual environment (optional)
⚙️ Setup Instructions
1️⃣ Clone the Repository

git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
2️⃣ Create and Activate a Virtual Environment
# Replace with your installed Python version
py -3.10 -m venv .venv
# Activate on Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Or for CMD
.\.venv\Scripts\activate.bat
3️⃣ Install Dependencies

pip install --upgrade pip
pip install -r requirements.txt
👉 Note for PyTorch:
To ensure correct CPU wheels, use:
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

▶️ Run the App
streamlit run dashboard.py
Open the local URL in your browser. Sign up or log in to start uploading CSV reviews and exploring the dashboard.

✅ Requirements
Python >= 3.10 (recommended)

Firebase project configured (update firebaseConfig in dashboard.py if you fork the repo)

📌 Technologies Used
Streamlit for interactive web app.

Transformers by Hugging Face for NLP.

Firebase for user authentication and real-time database.

Matplotlib & PyDeck for data visualization.

📈 Sample Data Format
Upload a .csv file containing at least one column with textual product reviews. Optionally include a feature column for feature-wise grouping.

🙌 Contribution
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

