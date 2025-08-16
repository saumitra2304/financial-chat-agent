# 🚀 Financial Chat Agent

A modern, minimalistic AI-powered financial chat interface with real-time market data integration and intelligent conversation memory.

## ✨ Features

- **🤖 AI Financial Assistant**: Advanced conversational AI specialized in financial topics
- **📈 Real-time Market Data**: Live stock prices, market analysis, and financial news
- **💾 Conversation Memory**: MongoDB-backed chat history with persistent storage
- **🎨 Minimalistic UI**: Clean, Apple-inspired Dynamic Island design
- **⚡ Real-time Updates**: Instant responses with beautiful animations
- **🔒 Secure**: Environment-based configuration for API keys and sensitive data

## 🏗️ Architecture

```
financial-chat-agent/
├── frontend/                 # React + Vite frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/        # Main chat interface
│   │   │   └── ui/          # UI components (Background Boxes)
│   │   ├── stores/          # Zustand state management
│   │   └── lib/             # Utility functions
│   └── package.json
├── backend/                  # Python FastAPI backend
│   ├── agents_core.py       # Core AI agent logic
│   ├── app.py              # FastAPI application
│   ├── memory/             # Conversation memory system
│   ├── tools/              # Financial data tools
│   └── requirements.txt
└── README.md
```

## 🎯 Tech Stack

### Frontend
- **React 19** - Modern UI framework
- **Vite** - Lightning-fast build tool
- **Zustand** - Simple state management
- **Tailwind CSS** - Utility-first styling
- **Framer Motion** - Smooth animations
- **Lucide React** - Beautiful icons
- **Axios** - HTTP client

### Backend
- **Python 3.11** - Core runtime
- **FastAPI** - Modern Python web framework
- **MongoDB** - Document database for conversation storage
- **LangChain** - AI agent framework
- **Financial APIs** - Real-time market data integration

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- Python 3.11+
- MongoDB instance
- Financial data API keys

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/saumitra2304/financial-chat-agent.git
   cd financial-chat-agent
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   
   # Create .env file with your configuration
   cp .env.example .env
   # Edit .env with your API keys and MongoDB connection
   
   # Start the backend server
   python app.py
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. **Access the Application**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`

## 🎨 UI Features

- **Dynamic Island Input**: Compact, morphing input field inspired by iOS
- **Minimalistic Black Theme**: Clean, professional dark interface
- **Animated Background**: Subtle grid animation with hover effects
- **Glass Morphism**: Translucent components with backdrop blur
- **Responsive Design**: Works seamlessly on all devices
- **Smooth Animations**: Framer Motion powered transitions

## 🛠️ Configuration

### Environment Variables

**Backend (.env)**
```env
MONGODB_URI=your_mongodb_connection_string
OPENAI_API_KEY=your_openai_api_key
FINANCIAL_API_KEY=your_financial_data_api_key
```

### API Endpoints

- `GET /health` - Health check
- `POST /chat` - Send chat message
- `GET /history` - Get conversation history
- `POST /new-chat` - Start new conversation

## 📊 Financial Features

- **Stock Analysis**: Real-time price data and technical indicators
- **Portfolio Management**: Track investments and performance
- **Market News**: Latest financial news and market updates
- **Investment Advice**: AI-powered recommendations and insights

## 🔧 Development

### Code Style
- **Frontend**: ESLint + Prettier configuration
- **Backend**: Black code formatter + isort
- **Commits**: Conventional commit messages

### Testing
```bash
# Frontend
cd frontend && npm run test

# Backend
cd backend && python -m pytest
```

### Build for Production
```bash
# Frontend
cd frontend && npm run build

# Backend
cd backend && python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Aceternity UI](https://ui.aceternity.com) - Background animation components
- [Lucide](https://lucide.dev) - Beautiful icon library
- [Tailwind CSS](https://tailwindcss.com) - Utility-first CSS framework
- [FastAPI](https://fastapi.tiangolo.com) - Modern Python web framework

## 📞 Support

If you have any questions or need help, please open an issue or contact the maintainers.

---

**Made with ❤️ by [Saumitra](https://github.com/saumitra2304)**
