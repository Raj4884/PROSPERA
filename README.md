# Bharat Exim - Premium B2B Export-Import Platform

A modern, fast, and professional B2B platform for managing export-import trading. Built with Flask, SQLAlchemy, and Bootstrap 5.

## Features
- **Modern Homepage:** Business introduction and premium category showcases.
- **User System:** Secure registration and login for business buyers.
- **Dual Catalog:** Dedicated paths for Domestic (India) and International (Export) supply chains.
- **Categorization:** Products organized into Agri, Handicrafts, Spices, and Jaggery.
- **Inquiry System:** Professional B2B inquiry forms for every product with data persistence.
- **Engagement Tracking:** Internal analytics for clicks, page visits, and geography.
- **Admin Dashboard:** Full control over products, categories, and viewing business insights.

## Local Setup

### 1. Prerequisites
- Python 3.8+
- Virtual Environment (recommended)

### 2. Installation
```bash
# Navigate to project directory
cd b2b_platform

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Initialization
```bash
# Run the setup script to create tables and add default content
python setup_db.py
```
*Note: This creates an admin account: `admin@bharatexim.com` with password `admin123`.*

### 4. Run Application
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your browser.

## Tech Stack
- **Backend:** Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate
- **Frontend:** HTML5, CSS3 (Premium custom styles), JavaScript, Bootstrap 5
- **Database:** SQLite (Development) / PostgreSQL (Production ready)
