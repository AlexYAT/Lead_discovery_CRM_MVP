# Lead Discovery CRM MVP - Human Run Guide

## Runtime prerequisites
- Python 3.12 (recommended)
- PowerShell (Windows) or any shell with Python available

## 1) Create virtual environment
```powershell
python -m venv .venv
```

## 2) Activate virtual environment
```powershell
.\.venv\Scripts\Activate.ps1
```

## 3) Install dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 4) Run application
```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## 5) URLs for human validation
- Home: http://127.0.0.1:8000/
- Leads: http://127.0.0.1:8000/leads
- Dashboard: http://127.0.0.1:8000/dashboard
