# MoodMate: AI-Powered Emotional Intelligence Platform

![MoodMate Logo](chatbot/static/chatbot/profile.jpg)

## 📋 Overview

MoodMate is an AI-powered emotional intelligence platform that combines conversational AI with dual-mode sentiment analysis. The application tracks emotional patterns through both text analysis and facial expression recognition, providing users with valuable insights into their emotional well-being over time.

### 🌟 Key Features

- **Dual-Analysis Technology**: Combines text sentiment analysis with facial expression recognition for deeper emotional understanding
- **Mood Tracking & Visualization**: Interactive charts display emotional patterns over time
- **Empathetic Conversations**: Natural dialogue with emotional intelligence
- **Discrepancy Detection**: Identifies differences between what users say and how they appear
- **Privacy-Focused Design**: Optional camera usage with transparent data handling

## 📸 Project Screenshots

### Dashboard View
<p align="center">
  <img src="screenshots/dashboard.png" alt="Dashboard Screenshot" width="800">
  <br>
  <em>Interactive dashboard with mood tracking visualizations and statistics</em>
</p>

### Chat Interface
<p align="center">
  <img src="screenshots/chat_interface.png" alt="Chat Interface" width="800">
  <br>
  <em>AI chatbot with real-time facial expression analysis</em>
</p>

### Mood Analysis Charts
<p align="center">
  <img src="screenshots/mood_charts.png" alt="Mood Analysis Charts" width="800">
  <br>
  <em>Data visualization of emotional patterns over time</em>
</p>

### Facial Expression Detection
<p align="center">
  <img src="screenshots/facial_detection.png" alt="Facial Expression Detection" width="800">
  <br>
  <em>Real-time emotion recognition from facial expressions</em>
</p>

### Mobile Responsiveness
<div align="center">
  <img src="screenshots/mobile_view1.png" alt="Mobile View 1" width="300">
  <img src="screenshots/mobile_view2.png" alt="Mobile View 2" width="300">
  <br>
  <em>Responsive design for mobile devices</em>
</div>

## 🔧 Technology Stack

### Backend
- **Django Framework**: Robust Python web framework that powers the application
- **SQLite Database**: Stores user accounts, chat history, and emotion analysis data
- **TextBlob**: Natural language processing library for sentiment analysis
- **DialoGPT**: Transformer-based conversational model from Microsoft

### Frontend
- **HTML/CSS/JavaScript**: Core web technologies for the user interface
- **Chart.js**: Data visualization library for mood tracking graphs
- **Face-API.js**: JavaScript library for real-time facial expression analysis

## 🧠 How It Works

### Sentiment Analysis Process
1. **Text Analysis**: Messages are processed using TextBlob to determine sentiment polarity
2. **Facial Expression Analysis**: Optional webcam feed is analyzed using Face-API.js
3. **Combined Intelligence**: Both inputs are weighted to determine the user's actual emotional state
4. **Response Generation**: The DialoGPT model produces contextually appropriate responses
5. **Emotional Tracking**: All interactions are stored to build emotional pattern visualizations

### User Experience Flow
1. Users register and log in to their personal dashboard
2. The chat interface allows natural conversation with the AI
3. Optional camera access enables facial expression analysis
4. Dashboard visualizations show emotional patterns over time
5. AI responses adapt based on detected emotions and conversation history

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Django 3.2+
- Required Python packages listed in requirements.txt

### Installation
```bash
# Clone the repository
git clone https://github.com/yourusername/moodmate.git
cd moodmate

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# Run the development server
python manage.py runserver
```

### Configuration
- No API keys needed - models run locally
- Webcam permissions managed through browser settings

## 🚀 Deploying to GitHub

Follow these commands to upload your project to GitHub:

```bash
# Navigate to your project directory
cd d:\projects\sentiment

# Initialize a git repository (if not already initialized)
git init

# Add all files to git
git add .

# Commit your changes
git commit -m "Initial commit: MoodMate sentiment analysis chatbot"

# Link your local repository to the GitHub repository
git remote add origin https://github.com/Siddhu290/Mood_Mate.git

# Push your project to GitHub
git push -u origin main
```

If you encounter a branch name error, you may need to push to the 'master' branch instead:
```bash
git push -u origin master
```

For larger files or if you face issues with the initial push, you can try:
```bash
git push -u origin main --force
```

### Additional GitHub Commands

```bash
# Check the status of your repository
git status

# View commit history
git log --oneline

# Create and switch to a new branch
git checkout -b feature/new-feature

# Pull latest changes from GitHub
git pull origin main
```

## 🔍 Project Structure

```
sentiment/
├── chatbot/                     # Main application directory
│   ├── models.py                # Data models for chat and analysis
│   ├── views.py                 # Core logic and request handlers
│   ├── static/                  # Static assets
│   │   └── chatbot/             
│   │       ├── style.css        # Application styling
│   │       └── models/          # Face detection models
│   └── templates/               # HTML templates
│       └── chatbot/
│           ├── home.html        # Landing page
│           ├── dashboard.html   # User dashboard with visualizations
│           ├── chatbot_interface.html  # Chat interface
│           ├── login.html       # Login page
│           └── register.html    # Registration page
└── sentiment_analysis/          # Project settings directory
    ├── settings.py              # Django settings
    ├── urls.py                  # URL configuration
    └── wsgi.py                  # WSGI configuration
```

## 🔒 Privacy Considerations

- Facial analysis is performed client-side - no image data is sent to the server
- All emotional data is stored in the user's personal account
- Camera usage is optional and can be toggled on/off

## 🛣️ Future Enhancements

- Mobile application for on-the-go mood tracking
- Integration with external wellness applications via API
- Additional analysis modes (voice tone, typing patterns)
- Machine learning to improve personalized responses over time

## 👥 Contributors

- Siddharth More - Initial work and concept
