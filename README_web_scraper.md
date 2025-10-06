# Katonic AI Partner Portal Web Scraper

This web scraper has been updated to handle the two-step authentication process used by the Katonic AI Partner Portal.

## Features

- **Two-Step Authentication**: Handles the email → continue → password → continue flow
- **Robust Error Handling**: Includes timeout handling and error detection
- **Configuration File Support**: Easy configuration via JSON file
- **Screenshot Capture**: Takes screenshots for debugging authentication issues
- **Legacy Support**: Still supports single-step authentication for other sites

## Authentication Process

The Katonic AI Partner Portal uses a two-step login process:

1. **Step 1**: User enters email address and clicks "Continue"
2. **Step 2**: Password field appears, user enters password and clicks "Continue" again

## Configuration

### Using JSON Configuration File

1. Copy `katonic_config.json` and modify it with your credentials:

```json
{
    "authentication": {
        "enabled": true,
        "login_url": "https://partner.katonic.ai/auth/sign-in",
        "email_field": "input[type=\"email\"]",
        "password_field": "input[type=\"password\"]",
        "continue_button": "button[type=\"submit\"]",
        "email": "your-email@katonic.ai",
        "password": "your-password",
        "two_step_login": true
    }
}
```

2. Run the scraper with your config file:

```python
from src.web_scraper import scrape_to_documents

# Load from config file
documents = await scrape_to_documents(config_file_path="katonic_config.json")
```

### Using Default Configuration

The default configuration is already set up for Katonic AI Partner Portal. You just need to update the email and password:

```python
from src.web_scraper import DEFAULT_CONFIG

# Update credentials
DEFAULT_CONFIG["authentication"]["email"] = "your-email@katonic.ai"
DEFAULT_CONFIG["authentication"]["password"] = "your-password"

# Run scraper
documents = await scrape_to_documents(DEFAULT_CONFIG)
```

## Testing Authentication

Use the provided test script to verify your authentication works:

```bash
python test_auth.py
```

This will:
- Open a browser window (non-headless mode)
- Attempt the two-step authentication
- Take screenshots for debugging
- Show the final URL after authentication

## Key Changes Made

### 1. Updated Configuration
- Changed login URL to `https://partner.katonic.ai/auth/sign-in`
- Updated field selectors to match the actual HTML structure
- Added `two_step_login: true` flag

### 2. Enhanced Authentication Function
- **Step 1**: Waits for email field, fills it, clicks continue
- **Step 2**: Waits for password field to appear, fills it, clicks continue
- **Robust Waiting**: Uses `wait_for_selector` and `wait_for_function` for better reliability
- **Error Detection**: Checks for error messages and validates final URL
- **Button State Checking**: Ensures buttons are enabled before clicking

### 3. Improved Error Handling
- Timeout handling for each step
- Error message detection
- Screenshot capture for debugging
- URL validation after authentication

### 4. Configuration File Support
- Added `load_config_from_file()` function
- Updated main functions to accept config file path
- Created example `katonic_config.json`

## Usage Examples

### Basic Usage
```python
import asyncio
from src.web_scraper import scrape_to_documents

async def main():
    documents = await scrape_to_documents()
    print(f"Scraped {len(documents)} documents")

asyncio.run(main())
```

### With Custom Config File
```python
import asyncio
from src.web_scraper import scrape_to_documents

async def main():
    documents = await scrape_to_documents(config_file_path="my_config.json")
    print(f"Scraped {len(documents)} documents")

asyncio.run(main())
```

### Full RAG Pipeline
```python
import asyncio
from src.web_scraper import scrape_and_process_to_rag

async def main():
    success = await scrape_and_process_to_rag(
        config_file_path="katonic_config.json",
        api_key="your-openai-api-key"
    )
    if success:
        print("RAG pipeline completed successfully!")

asyncio.run(main())
```

## Troubleshooting

### Authentication Issues

1. **Check credentials**: Ensure email and password are correct
2. **Run test script**: Use `python test_auth.py` to debug
3. **Check screenshots**: Look at generated PNG files for visual debugging
4. **Verify selectors**: The field selectors might change if the website is updated

### Common Issues

- **Timeout errors**: Increase timeout values in configuration
- **Button not clickable**: The scraper waits for buttons to be enabled
- **Password field not appearing**: Check if email is valid and continue button works

### Debug Mode

Set `headless=False` in the test script to see the browser in action:

```python
browser = await p.chromium.launch(headless=False)
```

## File Structure

```
├── src/
│   └── web_scraper.py          # Main scraper with two-step auth
├── katonic_config.json         # Example configuration file
├── test_auth.py               # Authentication test script
└── README_web_scraper.md      # This documentation
```

## Dependencies

- `playwright` - Browser automation
- `beautifulsoup4` - HTML parsing
- `langchain` - Document processing
- `python-dotenv` - Environment variables

Install with:
```bash
pip install playwright beautifulsoup4 langchain python-dotenv
playwright install chromium
```

