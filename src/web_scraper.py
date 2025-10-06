"""
Author: Ashok Kumar B
Date: 2025-10-06
Project: Katonic Platform Portal ChatBot
Module: Web Scraping Engine
Description: Web scraping module with dual authentication for Katonic portals
"""

import asyncio
import os
import json
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
# import html2text
import nest_asyncio
from datetime import datetime
from langchain.schema import Document
from . import text_chunker, embedding_service, vector_database
from .metadata_manager import generate_chunk_id, add_chunk
from dotenv import load_dotenv
import re


nest_asyncio.apply()

def load_config_from_file(config_file_path: str = None):
    """Load configuration from JSON file or return default config"""
    if config_file_path and os.path.exists(config_file_path):
        try:
            with open(config_file_path, 'r') as f:
                config = json.load(f)
            print(f"Loaded configuration from {config_file_path}")
            return config
        except Exception as e:
            print(f"Error loading config file {config_file_path}: {e}")
            print("Using default configuration")
            return DEFAULT_CONFIG
    return DEFAULT_CONFIG

DEFAULT_CONFIG = {
    "target_urls": [
        "https://partner.katonic.ai/",
        "https://installation.katonic.ai/dashboard/",
        "https://installation.katonic.ai/infrastructure/?type=on-prem-normal",
        "https://installation.katonic.ai/installation/?type=on-prem-normal",
        "https://installation.katonic.ai/maintenance/",
        "https://installation.katonic.ai/infrastructure/?type=on-prem-multitenancy",
        "https://installation.katonic.ai/installation/?type=on-prem-multitenancy",
        "https://installation.katonic.ai/maintenance/",
        "https://installation.katonic.ai/infrastructure/?type=airgap",
        "https://installation.katonic.ai/installation/?type=airgap",
        "https://installation.katonic.ai/maintenance/",
        "https://installation.katonic.ai/infrastructure/?type=airgap-multitenancy",
        "https://installation.katonic.ai/installation/?type=airgap-multitenancy",
        "https://installation.katonic.ai/maintenance/",
        "https://installation.katonic.ai/infrastructure/?type=azure-singletenancy",
        "https://installation.katonic.ai/installation/?type=azure-singletenancy",
        "https://installation.katonic.ai/maintenance/",
        "https://installation.katonic.ai/infrastructure/?type=azure-multitenancy",
        "https://installation.katonic.ai/installation/?type=azure-multitenancy",
        "https://installation.katonic.ai/maintenance/",
        "https://installation.katonic.ai/infrastructure/?type=aws-singletenancy",
        "https://installation.katonic.ai/installation/?type=aws-singletenancy",
        "https://installation.katonic.ai/maintenance/",
        "https://installation.katonic.ai/infrastructure/?type=aws-multitenancy",
        "https://installation.katonic.ai/installation/?type=aws-multitenancy",
        "https://installation.katonic.ai/maintenance/",
        "https://installation.katonic.ai/infrastructure/?type=gcp-singletenancy",
        "https://installation.katonic.ai/installation/?type=gcp-singletenancy",
        "https://installation.katonic.ai/maintenance/",
        "https://installation.katonic.ai/infrastructure/?type=gcp-multitenancy",
        "https://installation.katonic.ai/installation/?type=gcp-multitenancyv",
        "https://installation.katonic.ai/maintenance/",



        "https://partner.katonic.ai/testing-suite",
        "https://partner.katonic.ai/uat",
        "https://guides.katonic.ai/#platform-overview",
        "https://guides.katonic.ai/#quickstart",
        "https://partner.katonic.ai/distributor?section=home",
        "https://partner.katonic.ai/distributor?section=video-tutorials",
        "https://partner.katonic.ai/distributor?section=organization-management",
        "https://partner.katonic.ai/distributor?section=dns-management",
        "https://partner.katonic.ai/distributor?section=gpu-management",
        "https://partner.katonic.ai/distributor?section=service-templates",
        "https://partner.katonic.ai/distributor?section=image-management",
        "https://partner.katonic.ai/distributor?section=platform-monitoring",
        "https://partner.katonic.ai/distributor?section=user-management",
        "https://partner.katonic.ai/distributor?section=audit-trail",
        "https://partner.katonic.ai/distributor?section=platform-setting"
    ],
    "authentication": {
        "enabled": True,
        "login_url": "https://partner.katonic.ai/auth/sign-in",
        "email_field": 'input[type="email"]',
        "password_field": 'input[type="password"]',
        "continue_button": 'button[type="submit"]',
        "email": "harshit.vyas@katonic.ai",
        "password": "Katonic@1234",
        "two_step_login": True
    },
    "scraping": {
        "wait_for": "networkidle",
        "timeout": 30000,
        "remove_scripts": True,
        "remove_styles": True,
        "follow_links": False,
        "max_depth": 1
    },
    "output": {
        "format": "text",
        "include_metadata": True,
        "clean_text": True
    }
}



def clean_text(text):

    text = re.sub(r'\n\s*\n', '\n\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n ', '\n', text)
    text = text.strip()
    return text


async def scrape_page_direct(page, url: str, config):
    try:
        scraping_config = config.get("scraping", {})
        wait_for = scraping_config.get("wait_for", "networkidle")
        timeout = scraping_config.get("timeout", 30000)
        
        await page.goto(url, wait_until=wait_for, timeout=timeout)
        content = await page.content()
        
        soup = BeautifulSoup(content, "html.parser")
        
        if scraping_config.get("remove_scripts", True):
            for script in soup(["script"]):
                script.decompose()
        
        if scraping_config.get("remove_styles", True):
            for style in soup(["style"]):
                style.decompose()
        
        title = soup.find("title")
        title_text = title.get_text().strip() if title else "Untitled"
        
        # Extract plain text instead of markdown
        if config.get("output", {}).get("format") == "html":
            page_content = str(soup)
        else:
            # Extract plain text from the cleaned HTML
            page_content = soup.get_text()
            
            # Clean the extracted text
            if config.get("output", {}).get("clean_text", True):
                # page_content = clean_text(page_content)
                page_content = page_content
        
        return {
            "url": url,
            "title": title_text,
            "content": page_content,
            "timestamp": datetime.now().isoformat(),
            "success": True
        }
        
    except Exception as e:
        return {
            "url": url,
            "title": "Error",
            "content": f"Failed to scrape {url}: {str(e)}",
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "error": str(e)
        }

async def authenticate_direct(page, config, target_url=None):
    auth_config = config.get("authentication", {})
    
    if not auth_config.get("enabled", False):
        return True
    
    try:
        email_field = auth_config.get("email_field")
        password_field = auth_config.get("password_field")
        continue_button = auth_config.get("continue_button")
        email = auth_config.get("email")
        password = auth_config.get("password")
        two_step_login = auth_config.get("two_step_login", False)
        
        # Determine which login URL to use based on target URL
        if target_url and "installation.katonic.ai" in target_url:
            login_url = "https://installation.katonic.ai/login/"
            print(f"Using installation login URL: {login_url}")
        else:
            login_url = auth_config.get("login_url", "https://partner.katonic.ai/auth/sign-in")
            print(f"Using partner login URL: {login_url}")
        
        print(f"Authenticating at {login_url}...")
        await page.goto(login_url)
        await page.wait_for_load_state("networkidle")
        
        if two_step_login:
            # Step 1: Enter email and click continue
            print("Step 1: Entering email...")
            if email_field and email:
                # Wait for email field to be visible and fillable
                await page.wait_for_selector(email_field, timeout=10000)
                await page.fill(email_field, email)
                print(f"Filled email: {email}")
            
            if continue_button:
                # Wait for button to be enabled (not disabled)
                await page.wait_for_function(
                    f"document.querySelector('{continue_button}') && !document.querySelector('{continue_button}').disabled",
                    timeout=5000
                )
                await page.click(continue_button)
                print("Clicked continue button")
                
                # Wait for the password field to appear
                try:
                    await page.wait_for_selector(password_field, timeout=10000)
                    await page.wait_for_load_state("networkidle")
                    print("Password field appeared")
                except Exception as e:
                    print(f"Password field did not appear: {e}")
                    return False
            
            # Step 2: Enter password and click continue
            print("Step 2: Entering password...")
            if password_field and password:
                await page.fill(password_field, password)
                print("Filled password")
            
            if continue_button:
                # Wait for button to be enabled again
                await page.wait_for_function(
                    f"document.querySelector('{continue_button}') && !document.querySelector('{continue_button}').disabled",
                    timeout=5000
                )
                await page.click(continue_button)
                print("Clicked continue button for password")
                await page.wait_for_load_state("networkidle")
        else:
            # Single step login (legacy support)
            if email_field and email:
                await page.fill(email_field, email)
            if password_field and password:
                await page.fill(password_field, password)
            if continue_button:
                await page.click(continue_button)
                await page.wait_for_load_state("networkidle")
        
        # Wait a bit more to ensure login is complete
        await page.wait_for_timeout(2000)
        
        # Verify authentication success
        current_url = page.url
        print(f"Current URL after authentication: {current_url}")
        
        # Check if we're redirected to dashboard or if there are error messages
        if "dashboard" in current_url.lower() or "partner.katonic.ai" in current_url or "installation.katonic.ai" in current_url:
            print("Authentication completed successfully")
            
            # Additional verification - check if we can see authenticated content
            try:
                # Look for elements that indicate successful authentication
                auth_indicators = await page.query_selector_all('[class*="dashboard"], [class*="portal"], [class*="admin"], [class*="user"], [class*="menu"]')
                if auth_indicators and len(auth_indicators) > 0:
                    print("Authentication verified - authenticated content detected")
                else:
                    print("Authentication completed but no authenticated content detected")
            except:
                pass
            
            return True
        else:
            # Check for error messages
            try:
                error_elements = await page.query_selector_all('[class*="error"], [class*="alert"], .text-red-500, .text-red-600')
                if error_elements:
                    error_text = await page.evaluate("(elements) => elements.map(el => el.textContent).join(' ')", error_elements)
                    print(f"Authentication may have failed. Error messages found: {error_text}")
                    return False
            except:
                pass
            
            print("Authentication completed (URL verification inconclusive)")
            return True
        
    except Exception as e:
        print(f"Authentication failed: {e}")
        return False

async def scrape_to_documents(config = None, config_file_path: str = None):
    if config is None:
        config = load_config_from_file(config_file_path)
    
    target_urls = config.get("target_urls", [])
    if not target_urls:
        print("No target URLs configured!")
        return []
    
    print(f"Starting to scrape {len(target_urls)} URLs directly to documents...")
    
    documents = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Track which domains we've authenticated for
        authenticated_domains = set()
        
        for i, url in enumerate(target_urls, 1):
            print(f"\n[{i}/{len(target_urls)}] Scraping {url}")
            
            # Determine the domain for this URL
            domain = "partner.katonic.ai" if "partner.katonic.ai" in url else "installation.katonic.ai"
            
            # Authenticate if we haven't authenticated for this domain yet
            if domain not in authenticated_domains:
                print(f"Authenticating for domain: {domain}")
                auth_success = await authenticate_direct(page, config, target_url=url)
                if auth_success:
                    authenticated_domains.add(domain)
                    print(f"Successfully authenticated for {domain}")
                else:
                    print(f"Authentication failed for {domain}, continuing...")
            
            # Navigate to the URL and wait for it to load properly
            try:
                await page.goto(url, wait_until="networkidle", timeout=30000)
                await page.wait_for_timeout(2000)  # Additional wait for dynamic content
                
                # Check if we're still authenticated by looking for login elements
                login_elements = await page.query_selector_all('input[type="email"], input[type="password"], button:has-text("Sign in"), button:has-text("Continue")')
                if login_elements and len(login_elements) > 0:
                    print(f"Warning: Appears to be on login page for {url}, attempting re-authentication...")
                    # Try to re-authenticate if we're on a login page
                    auth_success = await authenticate_direct(page, config, target_url=url)
                    if auth_success:
                        await page.goto(url, wait_until="networkidle", timeout=30000)
                        await page.wait_for_timeout(2000)
                
            except Exception as e:
                print(f"Navigation error for {url}: {e}")
            
            scraped_data = await scrape_page_direct(page, url, config)
            
            if scraped_data["success"]:
                content = scraped_data["content"]
                if config.get("output", {}).get("include_metadata", True):
                    content = f"Source: {url}\nTitle: {scraped_data['title']}\n\n{content}"
                
                doc = Document(
                    page_content=content,
                    metadata={
                        'source': url,
                        'title': scraped_data['title'],
                        'timestamp': scraped_data['timestamp'],
                        'scraped_at': datetime.now().isoformat()
                    }
                )
                documents.append(doc)
                print(f"[SUCCESS] Created document for {url}")
            else:
                print(f"[FAILED] Failed to scrape {url}: {scraped_data.get('error', 'Unknown error')}")
        
        await browser.close()
    
    print(f"\n{'='*50}")
    print(f"Scraping completed: {len(documents)} documents created")
    return documents

async def scrape_and_process_to_rag(config = None, config_file_path: str = None, api_key: str = None):

    if not api_key:
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found")
    
    documents = await scrape_to_documents(config, config_file_path)
    
    if not documents:
        print("No documents scraped!")
        return None
    
    embeddings_model = embedding_service.create_embeddings_model(api_key)
    
    text_splitter = text_chunker.create_text_splitter()
    chunk_documents = []
    
    for doc in documents:
        doc_chunks = text_chunker.split_into_chunks(doc.page_content, text_splitter)
        source_url = doc.metadata.get('source', 'unknown')
        total_chunks = len(doc_chunks)
        
        for i, chunk_text in enumerate(doc_chunks):
            chunk_doc = Document(
                page_content=chunk_text,
                metadata={
                    'source': source_url,
                    'chunk_index': i,
                    'title': doc.metadata.get('title', ''),
                    'timestamp': doc.metadata.get('timestamp', ''),
                    'scraped_at': doc.metadata.get('scraped_at', '')
                }
            )
            chunk_documents.append(chunk_doc)
            
            chunk_id = generate_chunk_id(source_url, i)
            add_chunk(chunk_id, source_url, total_chunks)
    
    print(f"Creating vector store with {len(chunk_documents)} document chunks...")
    
    vector_database.create_vector_store(chunk_documents, embeddings_model)
    print("Vector store created successfully!")
    print(f"Created {len(chunk_documents)} chunk metadata records")
    
    return True

async def main():
    documents = await scrape_to_documents()
    print(f"\nScraped {len(documents)} documents:")
    for doc in documents:
        print(f"- {doc.metadata['source']}: {doc.metadata['title']}")

if __name__ == "__main__":
    asyncio.run(main())
