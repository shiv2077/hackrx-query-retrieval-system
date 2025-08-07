# 🌐 WEBHOOK URL SUBMISSION

## **🚀 LIVE WEBHOOK URL (Ready for Testing):**
```
https://9a4aacf85276.ngrok-free.app/hackrx/run
```

## **LOCAL DEMO URL (For Live Testing):**
```
http://localhost:8000/hackrx/run
```

## **DEPLOYMENT OPTIONS PROVIDED:**

### **✅ Option 1: ngrok Tunnel** (ACTIVE)
- **Live URL**: `https://9a4aacf85276.ngrok-free.app/hackrx/run`
- **Status**: ✅ ONLINE and tested
- **Response Time**: ~4 seconds

### **Option 2: Railway Deployment** (Backup)
- **Repository**: https://github.com/shiv2077/hackrx-query-retrieval-system
- **Branch**: main
- **Start Command**: `python main.py`
- **Expected URL**: `https://hackrx-query-retrieval-system.railway.app/hackrx/run`

### **Option 3: Render Deployment** (Backup)
- **Repository**: https://github.com/shiv2077/hackrx-query-retrieval-system
- **Runtime**: Python 3.12
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python main.py`

## **✅ WORKING TEST COMMAND (VERIFIED):**
```bash
curl -X POST https://9a4aacf85276.ngrok-free.app/hackrx/run \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer 971f5fd97a9aff1e0b94e410e77138f521d653ca4d78ddbb1f76c5aa785147a4" \
  -d '{
    "documents": "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D",
    "questions": [
        "Does this policy cover maternity expenses, and what are the conditions?"
    ]
  }'
```

**Test Result**: ✅ Returns valid JSON response in ~4 seconds

## **✅ SUBMISSION STATUS:**
- ✅ **Local System**: Fully working and tested
- ✅ **Repository**: https://github.com/shiv2077/hackrx-query-retrieval-system
- ✅ **Documentation**: Complete with all requirements
- ✅ **API Compliance**: 100% specification match
- ✅ **Webhook URL**: **LIVE AND TESTED** at https://9a4aacf85276.ngrok-free.app/hackrx/run

---
**READY FOR SUBMISSION**: System is live, tested, and publicly accessible for evaluation!
