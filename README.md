# AI Health Manager

A comprehensive end-to-end health management application powered by Google's Gemini AI.

## Features

### 🏥 Complete Health Tracking System
- **User Profile Setup**: BMR calculation, calorie targets based on goals
- **AI Food Analysis**: Upload food images for instant calorie and nutrition analysis
- **Exercise Tracker**: Log workouts with automatic calorie burn calculation
- **Dashboard**: Real-time daily health metrics and progress tracking
- **Progress Reports**: Visual charts showing trends and patterns
- **AI Health Coach**: Personalized health advice and recommendations

### 🤖 AI-Powered Features
- Food recognition and nutritional analysis from images
- Personalized health recommendations
- Smart calorie calculations based on user profile
- Health score assessment for meals

## Setup Instructions

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   - Ensure your `.env` file contains your Google API key:
   ```
   GOOGLE_API_KEY="your_api_key_here"
   ```

3. **Run the Application**
   ```bash
   streamlit run app.py
   ```

## How to Use

### First Time Setup
1. Navigate to "Profile Setup" in the sidebar
2. Enter your personal information (age, weight, height, etc.)
3. Select your health goal (lose/maintain/gain weight)
4. Save your profile

### Daily Usage
1. **Food Tracking**: Go to "Food Analysis" → Upload meal photos → Get AI analysis → Save to log
2. **Exercise Logging**: Go to "Exercise Tracker" → Enter workout details → Calculate calories burned → Save
3. **Monitor Progress**: Check "Dashboard" for daily summary and "Progress Reports" for trends
4. **Get Advice**: Use "AI Health Coach" for personalized health recommendations

## Key Features Explained

### Food Analysis
- Upload any food image
- AI identifies food items and estimates calories
- Provides nutritional breakdown (protein, carbs, fat)
- Gives health assessment and improvement suggestions
- Saves to daily meal log

### Exercise Tracker
- Multiple exercise types supported
- Intensity-based calorie calculations using MET values
- Automatic calorie burn computation based on user weight
- Exercise history tracking

### Dashboard
- Real-time calorie balance (consumed vs burned)
- Progress toward daily calorie target
- Today's meal and exercise summary
- Visual progress indicators

### Progress Reports
- Daily calorie intake trends
- Exercise distribution charts
- Historical data visualization

### AI Health Coach
- Personalized advice based on user profile
- Context-aware recommendations
- Nutrition and fitness guidance

## Data Storage
- All data is stored locally in `health_data.json`
- Includes user profile, meals, exercises, and goals
- Data persists between sessions

## Tips for Best Results
- Take clear, well-lit photos of your meals
- Log exercises immediately after completion
- Check your dashboard daily for motivation
- Use the AI coach for specific health questions
- Be consistent with logging for accurate progress tracking