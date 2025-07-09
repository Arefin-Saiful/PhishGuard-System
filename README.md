# 🛡️ PhishGuard: Phishing Attack Detection System

PhishGuard is a web-based **Phishing Attack Detection System** that scans both **emails** and **URLs** in real-time using a **hybrid Deep Learning model** integrated with **Natural Language Processing (NLP)** techniques. Designed with user privacy, accuracy, and security in mind, it provides fast, reliable, and interactive phishing detection via a responsive web interface.

## 🚀 Features

* 🔐 Secure user authentication (Flask-Login, password hashing, reset via tokenized email)
* 📧 Email phishing detection from `.eml` files using CNN + BiLSTM models
* 🔗 URL phishing detection using TF-IDF features and dense neural networks
* 📊 Admin dashboard with logs, stats, and feedback viewer
* 📥 User dashboard with scan history and visualization
* 🔁 Feedback loop to improve model accuracy
* ⚙️ Modular three-layer architecture (Presentation, Application, Data)

## 🖼️ User Interface

* Built with **HTML**, **CSS**, **Bootstrap 5**
* Real-time scanning via **AJAX**
* Dynamic charts and dashboards for user and admin insights

## 🧠 Machine Learning

* **Email Scanner**: Uses NLP preprocessing + hybrid DL model (CNN + BiLSTM)
* **URL Scanner**: Uses 87 handcrafted features + TF-IDF + meta-classifier
* **Model Inference**: Real-time predictions with confidence scores

## 🗄️ Tech Stack

| Layer            | Technologies Used                                   |
| ---------------- | --------------------------------------------------- |
| Frontend         | HTML, CSS, Bootstrap 5, JavaScript, AJAX            |
| Backend          | Python, Flask, Flask-Login, SQLAlchemy              |
| Database         | SQLite + SQLAlchemy ORM                             |
| ML/DL Frameworks | scikit-learn, joblib, PyTorch, HuggingFace (TF-IDF) |

## 📦 Requirements

Install dependencies using:

```bash
pip install -r requirements.txt
<details> <summary>Click to view key dependencies</summary>
Flask==2.3.2

Flask-Login==0.6.3

Flask-SQLAlchemy==3.1.1

scikit-learn==1.5.0

joblib==1.5.1

gunicorn (for production deployment)

</details>
📂 Project Structure
arduino
Copy
Edit
phishguard/
├── models/
│   └── email/
│       ├── hybrid_model.h5
│       └── tokenizer.pkl
│
│   └── URL/
│       ├── Hybrid_CNN_LSTM_best.h5
│       ├── tokenizer.json
│       ├── config.json
│       └── scaler_link_count.pkl
│
├── utils/
│   ├── email_model.py
│   └── url_model.py
│
├── templates/          ← HTML pages
├── static/             ← CSS, JS
├── app.py              ← Flask main app
├── requirements.txt
├── Procfile
├── .env                ← (optional) config vars
└── README.md
⚙️ How It Works
User uploads email (.eml) or enters a URL

Backend processes input → Extracts features → Feeds into ML model

Model returns verdict (Phishing/Legitimate) + confidence score

Results shown on dashboard with visualization

Feedback stored for future retraining

📈 Future Work
Support multilingual phishing detection

Real-time retraining from user feedback

Cloud deployment (e.g., Heroku/AWS)

Email gateway integration (SMTP filtering)

📜 License
This project is for academic and educational use. Reach out if you want to adapt or extend it commercially
