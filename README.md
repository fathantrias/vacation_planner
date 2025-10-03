# 🏖️ Autonomous Vacation Planner

An AI-powered chatbot that autonomously plans vacations using LangGraph's ReAct agent pattern, Groq LLM API, and Streamlit.

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## ✨ Features

- 🤖 **Autonomous Planning**: AI agent that independently searches flights, hotels, and activities
- 📅 **Calendar-Aware**: Respects your availability and blocked dates
- 💰 **Budget-Conscious**: Validates expenses against your budget constraints (in IDR)
- 🎯 **Personalized**: Recommendations based on your interests and preferences
- 💳 **Secure Bookings**: Payment authorization required before flight/hotel bookings
- 💬 **Conversational**: Natural language interface powered by Groq LLM
- 🇮🇩 **Indonesia Focus**: All flights depart from Jakarta (CGK), prices in Indonesian Rupiah
- ℹ️ **Activities Discovery**: Browse activities for inspiration (external booking required)

## 🏗️ Architecture

Built with:
- **LangGraph** (0.4.8) - ReAct agent orchestration
- **LangChain Core** (0.3.76) - LangChain framework foundation
- **Groq API** - Fast LLM inference with Llama 4 Scout 17B
- **Streamlit** (1.50.0) - Interactive web interface
- **Python** 3.10+

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- Groq API key ([Get one free here](https://console.groq.com/keys))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/vacation_planner.git
cd vacation_planner
```

2. **Create a virtual environment**
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=meta-llama/llama-4-scout-17b-16e-instruct
```

5. **Run the application**
```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## 📖 Usage Guide

### 1. Configure Payment (Required for Bookings)

In the sidebar, fill out the payment form:
- Card Number (any format for PoC)
- Expiry Date
- CVV
- Cardholder Name
- ✅ Check the authorization box

⚠️ **Important**: This is a demo. Do NOT use real payment information.

### 2. Start Planning

Example prompts:
- "Plan a vacation to Bali next month"
- "I want to visit Tokyo in March under $3000"
- "Suggest a beach destination for 7 days"

### 3. Review & Approve

The agent will:
1. Check your calendar availability
2. Get your preferences and budget
3. Search for flights, hotels, and activities
4. Present a complete itinerary
5. Wait for your approval before booking

## 🎮 Example Interaction

```
You: Plan me a vacation to Bali next month

Agent:
🔍 Checking your calendar...
✓ Found availability: October 10-21, November 9-19

📊 Retrieved your preferences:
- Budget: Rp 80,000,000
- Interests: beaches, culture, food

✈️ Searching flights...
Found: Singapore Airlines - Rp 2,500,000 (CGK → DPS)

🏨 Searching hotels...
Found: Bali Beach Resort - Rp 2,000,000/night (7 nights)

🎯 Recommended Activities (for your planning):
- Uluwatu Temple Tour - Rp 700,000
- Cooking Class - Rp 850,000

💰 Budget Check (flights + hotels):
Total: Rp 16,500,000 | Remaining: Rp 63,500,000 ✓

Would you like me to book the flight and hotel?
```

## 📁 Project Structure

```
vacation_planner/
├── app.py                          # Main Streamlit application
├── agent/
│   ├── planner_agent.py           # LangGraph agent setup
│   ├── tools.py                   # Custom tools (8 total)
│   └── prompts/
│       └── system_prompt.txt      # Agent instructions
├── data/
│   ├── user_calendar.json         # Mock calendar data
│   ├── user_preferences.json      # User profile
│   ├── flights_mock.json          # Mock flight inventory
│   ├── hotels_mock.json           # Mock hotel data
│   └── activities_mock.json       # Mock activities
├── utils/                          # Helper utilities
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
├── README.md                       # This file
└── SOLUTION.md                     # Detailed documentation
```

## 🛠️ Available Tools

The AI agent has access to 8 custom tools:

1. **get_user_calendar** - Check availability and blocked dates
2. **get_user_preferences** - Retrieve user profile
3. **search_flights** - Find available flights
4. **search_hotels** - Search hotels by destination
5. **search_activities** - Discover activities for inspiration
6. **calculate_budget** - Validate flight and hotel expenses
7. **book_flight** - Make flight bookings (requires payment authorization)
8. **book_hotel** - Make hotel reservations (requires payment authorization)

**Note**: Activities are for planning purposes only. The agent can only book flights and hotels.

## 🌐 Deploy to Streamlit Cloud

1. Push your code to GitHub
2. Visit [Streamlit Cloud](https://streamlit.io/cloud)
3. Connect your repository
4. Add secrets in the dashboard:
   ```
   GROQ_API_KEY = "your_key_here"
   ```
5. Deploy!

Your app will be live at: `https://your-app.streamlit.app`

## 📊 Mock Data

The PoC uses mock JSON data to simulate real APIs:

- **Flights**: 8 routes from Jakarta (CGK) to various destinations
- **Hotels**: 8 properties across 5 cities
- **Activities**: 15 curated experiences (informational only)
- **Calendar**: Pre-configured availability for October-November 2025
- **Preferences**: Sample user profile with budget (Rp 80,000,000 IDR) and interests

## 🔒 Security Note

This is a **proof-of-concept** for demonstration purposes:

- ⚠️ No real payment processing
- ⚠️ Accepts any payment credentials
- ⚠️ No user authentication
- ⚠️ Session-based storage only

**DO NOT use real payment information or deploy without proper security measures.**

See [SOLUTION.md](SOLUTION.md) for comprehensive risk analysis.

## 📚 Documentation

- **[SOLUTION.md](SOLUTION.md)** - Detailed architecture, design decisions, and risk analysis
- **[GROQ API Docs](https://console.groq.com/docs)** - Groq API documentation
- **[LangGraph Docs](https://langchain-ai.github.io/langgraph/)** - LangGraph documentation
- **[Streamlit Docs](https://docs.streamlit.io/)** - Streamlit documentation

## 🐛 Troubleshooting

### "GROQ_API_KEY not found"
- Ensure `.env` file exists in the root directory
- Verify your API key is correct
- Restart the Streamlit app

### Agent not responding
- Check your internet connection
- Verify Groq API quota hasn't been exceeded
- Check Streamlit terminal for error messages

### Import errors
- Ensure virtual environment is activated
- Run `pip install -r requirements.txt` again

## 🤝 Contributing

This is an educational project. Feel free to:
- Fork the repository
- Create feature branches
- Submit pull requests

## 📝 License

MIT License - Feel free to use this project for learning purposes.

## 👨‍💻 Developer

Built with Claude Code (Anthropic) as a GenAI assignment demonstration.

## 🙏 Acknowledgments

- **LangChain/LangGraph** for the agent framework
- **Groq** for fast LLM inference
- **Streamlit** for the amazing UI framework
- **Anthropic** for Claude AI assistance

---

**⭐ If you found this project helpful, please star the repository!**

For detailed technical documentation, see [SOLUTION.md](SOLUTION.md).
