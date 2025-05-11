# GitHub Repository Setup Guide

This guide covers setting up a GitHub repository for a Python-based finance tool using web scraping and MongoDB on an Oracle VM.

## Initial Setup

### Cloning the Empty Repository
```bash
git clone https://github.com/your-username/finance_tool.git
cd finance_tool
```

### Creating a Basic README.md
From terminal:
```bash
echo "# Finance Tool" > README.md
echo "" >> README.md
echo "A web scraping application for financial data using Python and MongoDB, deployed on Oracle VM." >> README.md
```

Alternatively, use a text editor:
```bash
nano README.md
```

### Creating a Project Structure
```bash
mkdir -p src/scrapers src/models src/utils tests config
touch README.md .gitignore requirements.txt
```

## Project Structure Explanation

```
/config
* oracle_vm_setup.md - instructions for running this on the oracle vm

/src
* contains main script as application entry point

/src/models
* contains data models/schemas for MongoDB

/src/scrapers
* contains web scraping scripts

/src/utils
* database connection and other utility functions

/tests
* units and integration tests

/venv
* this is unique per machine and not pulled to github

.gitignore
* contains files and folders that are not pulled to github e.g. venv
```

## Setting Up .gitignore

Create a Python-specific .gitignore file:
```bash
curl https://raw.githubusercontent.com/github/gitignore/main/Python.gitignore > .gitignore
```

Add MongoDB, environment-specific, and macOS-specific ignores:
```bash
echo "# MongoDB" >> .gitignore
echo "data/" >> .gitignore
echo "# Environment" >> .gitignore
echo ".env" >> .gitignore
echo "# macOS" >> .gitignore
echo ".DS_Store" >> .gitignore
echo "**/.DS_Store" >> .gitignore
echo ".DS_Store?" >> .gitignore
```

If `.DS_Store` has already been committed and you need to remove it:
```bash
# Remove .DS_Store from repository but keep it on filesystem
git rm --cached .DS_Store
git commit -m "Remove .DS_Store from repository"
```

## Setting Up a Virtual Environment

### Local Development Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it (macOS/Linux)
source venv/bin/activate

# Activate it (Windows)
venv\Scripts\activate

# Install required packages
pip install requests beautifulsoup4 pymongo python-dotenv pandas

# Generate requirements.txt
pip freeze > requirements.txt
```

The virtual environment (`venv` folder) is local to your machine and is not pushed to GitHub. VS Code will automatically recognize this environment once created.

## Setting Up Environment Variables

Create a template .env.example file:
```bash
cat > .env.example << EOL
# Database Configuration
MONGODB_URI=mongodb://username:password@host:port/database
MONGODB_DATABASE=finance_data

# API Keys
FINANCIAL_API_KEY=your_api_key_here

# Scraping Settings
SCRAPE_INTERVAL=3600  # In seconds
USER_AGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64)...
EOL
```

Create your actual .env file (which will be gitignored):
```bash
cp .env.example .env
```

## Oracle VM Setup Instructions

Create a setup guide for the Oracle VM:
```bash
cat > config/oracle_vm_setup.md << EOL
# Oracle VM Setup

## Prerequisites
- Oracle VM with Ubuntu Server 20.04+
- Python 3.9+
- MongoDB 5.0+

## Installation Steps

### 1. Update System
\`\`\`bash
sudo apt update && sudo apt upgrade -y
\`\`\`

### 2. Install Python and Requirements
\`\`\`bash
sudo apt install -y python3-pip python3-venv git
\`\`\`

### 3. Install MongoDB
\`\`\`bash
# Import MongoDB public key
wget -qO - https://www.mongodb.org/static/pgp/server-5.0.asc | sudo apt-key add -

# Create list file
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/5.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-5.0.list

# Update and install
sudo apt update
sudo apt install -y mongodb-org

# Start MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod
\`\`\`

### 4. Clone and Set Up Application
\`\`\`bash
git clone https://github.com/your-username/finance_tool.git
cd finance_tool
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
\`\`\`

### 5. Create .env File
\`\`\`bash
cp .env.example .env
# Edit .env with actual values
nano .env
\`\`\`

### 6. Run Application
\`\`\`bash
python src/main.py
\`\`\`
EOL
```

## Database Connection Setup

Create a basic database connection utility:
```bash
mkdir -p src/utils
cat > src/utils/database.py << EOL
"""Database connection utilities"""
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database():
    """Returns a connection to the MongoDB database"""
    connection_string = os.getenv('MONGODB_URI')
    if not connection_string:
        raise EnvironmentError("MONGODB_URI environment variable not set")
    
    client = MongoClient(connection_string)
    db_name = os.getenv('MONGODB_DATABASE', 'finance_data')
    return client[db_name]
EOL
```

## Create a Sample Scraper Base Class

```bash
mkdir -p src/scrapers
cat > src/scrapers/base_scraper.py << EOL
"""Base scraper class for all scrapers"""
import requests
from bs4 import BeautifulSoup
import logging
import re

class BaseScraper:
    """Base class for all web scrapers"""
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_soup(self, url=None):
        """Get BeautifulSoup object from URL"""
        target_url = url or self.url
        self.logger.info(f"Fetching page: {target_url}")
        try:
            response = self.session.get(target_url)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            self.logger.error(f"Error fetching {target_url}: {str(e)}")
            raise
    
    def scrape(self):
        """Implement in child classes"""
        raise NotImplementedError("Subclasses must implement scrape()")
EOL
```

## Main Application Entry Point

```bash
cat > src/main.py << EOL
#!/usr/bin/env python3
"""
Finance Tool - Main application entry point
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for the application"""
    logger.info("Starting Finance Tool - Web Scraping Application")
    
    # Import your scrapers and models here
    # from scrapers.your_scraper import YourScraper
    # from utils.database import get_database
    
    # Add your application logic here
    
    logger.info("Application completed successfully")

if __name__ == "__main__":
    main()
EOL
```

## Committing and Pushing Changes

```bash
# Check status of changes
git status

# Add all files to staging
git add .

# Commit changes
git commit -m "Initial project setup with folder structure and base files"

# Push to GitHub
git push origin main
```

## VS Code Integration

VS Code will automatically detect your Python virtual environment when you open the project folder. To select it:

1. Open VS Code with your project:
   ```bash
   code finance_tool
   ```

2. Press `Ctrl+Shift+P` (Windows/Linux) or `Command+Shift+P` (macOS)

3. Type "Python: Select Interpreter" and select it

4. Choose the interpreter from your virtual environment

## Next Steps

1. Develop your specific web scrapers in the `src/scrapers` directory
2. Create MongoDB models in the `src/models` directory
3. Write tests in the `tests` directory
4. Deploy to your Oracle VM following the instructions in `config/oracle_vm_setup.md`