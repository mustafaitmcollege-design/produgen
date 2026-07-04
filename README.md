# 🚀 ProduGen — AI Product Image Generator

**ProduGen** is an AI-powered tool that generates professional product images for small businesses. It uses an intelligent questionnaire to understand your product, then generates stunning marketing-ready images for Instagram, Facebook, and website use.

## ✨ Features

- 🤖 **AI-Powered Questionnaire** — Smart questions to understand your product and brand (Powered by Google Gemini)
- 🎨 **Professional Image Generation** — Creates studio-quality product photos (Powered by Replicate FLUX Schnell)
- 📱 **Multi-Platform Output** — Optimized for Instagram, Facebook, and websites
- 💼 **Built for Small Businesses** — Simple, affordable, and effective
- ☁️ **Cloud-Ready** — Local-first architecture (FastAPI + SQLite), easily deployable on any device

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python + FastAPI |
| AI Chat | Google Gemini API (Free Tier) |
| Image Gen | Replicate API (FLUX Schnell) |
| Database | SQLite |
| Frontend | HTML + CSS + JavaScript (Vanilla) |

## 📦 Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/mustafaitmcollege-design/produgen.git
   cd produgen
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # Mac/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up API Keys**
   - Copy `.env.example` to `.env`
   - Add your **Google Gemini API Key** (Get it at https://aistudio.google.com/apikey)
   - Add your **Replicate API Token** (Get it at https://replicate.com/account/api-tokens)

5. **Run the Server**
   ```bash
   python run.py
   ```
   The application will be available at `http://localhost:8000`

## 📄 License

MIT License

---

*Built with ❤️ by [Mustafa Shirawala](https://github.com/mustafaitmcollege-design)*
