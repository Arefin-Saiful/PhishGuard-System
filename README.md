Here is a complete and professional `README.md` file for your GitHub project based on the contents of your report and implementation files:

---

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
```

<details>
<summary>Click to view key dependencies</summary>

* Flask==2.3.2
* Flask-Login==0.6.3
* Flask-SQLAlchemy==3.1.1
* scikit-learn==1.5.0
* joblib==1.5.1
* gunicorn (for production deployment)

</details>

## 📂 Project Structure

```bash
phishguard/
├── static/
├── templates/
├── utils/
│   ├── email_model.py
│   ├── url_model.py
├── models/
├── app.py
├── config.py
├── requirements.txt
└── README.md
```

## ⚙️ How It Works

1. **User uploads email (.eml) or enters a URL**
2. **Backend processes input → Extracts features → Feeds into ML model**
3. **Model returns verdict (Phishing/Legitimate) + confidence score**
4. **Results shown on dashboard with visualization**
5. **Feedback stored for future retraining**

## 📈 Future Work

* Support multilingual phishing detection
* Real-time retraining from user feedback
* Cloud deployment (e.g., Heroku/AWS)
* Email gateway integration (SMTP filtering)

## 📜 License

This project is for academic and educational use. Reach out if you want to adapt or extend it commercially.

![Screenshot 2025-06-16 042340](https://github.com/user-attachments/assets/25b30360-6e0b-4a90-b835-32a5952b04c5)
![Screenshot 2025-06-15 190312](https://github.com/user-attachments/assets/9e3cb736-18b3-49c9-b0de-f9767a916fb9)
![Screenshot 2025-06-15 190514](https://github.com/user-attachments/assets/b1d88225-f6dd-4be3-b689-dcd8c9d0ec5d)
![Screenshot 2025-06-15 190532](https://github.com/user-attachments/assets/748dd55b-9f39-4e50-8d5a-e9098e3be8ac)
![Screenshot 2025-06-15 190610](https://github.com/user-attachments/assets/9597e1e2-feec-4e59-8c47-54dbd1713eba)
![Screenshot 2025-06-15 191051](https://github.com/user-attachments/assets/9826c0e8-d526-495f-9e8b-e154132a37a0)
![Screenshot 2025-06-15 191246](https://github.com/user-attachments/assets/8391b918-f84c-465e-be3b-df741a4f3d53)
![Screenshot 2025-06-15 191328](https://github.com/user-attachments/assets/9be6ea17-91a4-4a81-9fcd-c875996995e7)
![Screenshot 2025-06-15 190359](https://github.com/user-attachments/assets/3b096d18-4ea8-4e0b-baab-96f932a54fbe)
