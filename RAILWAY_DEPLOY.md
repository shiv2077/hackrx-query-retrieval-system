# Quick Deploy to Railway

# 1. Create railway.json
{
  "deploy": {
    "startCommand": "python main.py",
    "healthcheckPath": "/docs"
  }
}

# 2. Deploy commands:
# npm install -g @railway/cli
# railway login
# railway init
# railway up

# Your webhook URL will be: https://your-app-name.railway.app/hackrx/run
