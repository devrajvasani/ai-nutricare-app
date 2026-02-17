# 🥗 AI_NutriCare

AI_NutriCare is an AI-powered nutrition assistant built using Python and Streamlit.  
It provides intelligent dietary recommendations and insights using machine learning and AI models.

---

## 🚀 Getting Started

Follow the steps below to set up and run the project locally.

---

## 📌 Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git (optional, for cloning)

Check your Python version:

```bash
python --version
1️⃣ Clone the Repository
git clone https://github.com/your-username/AI_NutriCare.git
cd AI_NutriCare
If you already have the project folder, navigate into it:

cd AI_NutriCare

2️⃣ Create Virtual Environment
Creating a virtual environment is recommended to manage dependencies.

🔹 Windows
python -m venv venv
venv\Scripts\activate

3️⃣ Upgrade pip (Recommended)
python -m pip install --upgrade pip

4️⃣ Install Dependencies
pip install -r requirements.txt

5️⃣ Setup Environment Variables (If Required)
If your project uses API keys (e.g., OpenAI or other AI services), create a .env file in the root directory:

touch .env
Add your keys inside:
⚠️ Do NOT upload your .env file to GitHub.

Make sure python-dotenv is included in your requirements.txt if using environment variables.

▶️ Run the Streamlit Application
Start the application with:

streamlit run app.py

The app will run at: http://localhost:8501