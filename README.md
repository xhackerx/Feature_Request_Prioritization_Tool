# Feature Request Prioritization Tool

A simple, open-source tool for product managers to prioritize feature requests efficiently.

## Features

- Feature request submission form with impact, effort, and strategic alignment scoring
- Automated priority scoring algorithm
- Visual dashboard with charts
- Integration capabilities with Jira/Trello via API
- Feedback mechanism
- RESTful API endpoints

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/feature-prioritization-tool.git
cd feature-prioritization-tool

2. Create and activate virtual environment:
```
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt

4. Create .env file and set environment variables:
```
cp .env.example .env
# Edit .env with your settings
```

5. Initialize the database and load sample data:
```
python run.py
python sample_data.py
```

## Usage
1. Start the application:
```
python run.py
```

2. Access the application at http://localhost:5000