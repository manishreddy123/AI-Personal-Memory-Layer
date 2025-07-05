from notion_client import Client
from notion_client.errors import APIResponseError
import os

def load_notion_pages():
    """Load pages from Notion database with proper error handling"""
    
    # Check if Notion is configured
    notion_key = os.getenv("NOTION_API_KEY")
    database_id = os.getenv("NOTION_DB_ID")
    
    if not notion_key or not database_id:
        print("WARNING: Notion API credentials not configured. Skipping Notion data loading.")
        print("See NOTION_SETUP.md for setup instructions.")
        return []
    
    if notion_key == "your-notion-api-key" or database_id == "your-database-id":
        print("WARNING: Notion API credentials contain placeholder values. Skipping Notion data loading.")
        print("Please update your .env file with actual Notion credentials.")
        return []
    
    try:
        notion = Client(auth=notion_key)
        results = notion.databases.query(database_id=database_id)
        
        pages = []
        for page in results["results"]:
            try:
                # Handle different property structures
                if "Name" in page["properties"]:
                    title_prop = page["properties"]["Name"]
                    if title_prop.get("title") and len(title_prop["title"]) > 0:
                        title = title_prop["title"][0]["plain_text"]
                    else:
                        title = "Untitled"
                else:
                    # Try to find any title property
                    title = "Untitled"
                    for prop_name, prop_value in page["properties"].items():
                        if prop_value.get("type") == "title" and prop_value.get("title"):
                            if len(prop_value["title"]) > 0:
                                title = prop_value["title"][0]["plain_text"]
                                break
                
                pages.append(title)
            except (KeyError, IndexError, TypeError) as e:
                print(f"WARNING: Error parsing page data: {e}")
                pages.append("Error parsing page")
        
        print(f"Successfully loaded {len(pages)} pages from Notion")
        return pages
        
    except APIResponseError as e:
        if "API token is invalid" in str(e):
            print("ERROR: Invalid Notion API token.")
            print("Please check your NOTION_API_KEY in the .env file.")
            print("See NOTION_SETUP.md for instructions on getting a valid API token.")
        elif "Object not found" in str(e):
            print("ERROR: Notion database not found.")
            print("Please check your NOTION_DB_ID in the .env file.")
            print("Make sure the database ID is correct and the integration has access to it.")
        else:
            print(f"ERROR: Notion API error: {e}")
        
        print("Continuing without Notion data...")
        return []
        
    except Exception as e:
        print(f"ERROR: Unexpected error loading Notion data: {e}")
        print("Continuing without Notion data...")
        return []

