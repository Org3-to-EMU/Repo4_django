import requests
# import parser
from html.parser import HTMLParser
from bs4 import BeautifulSoup
import json
import argparse
import os

# Confluence Username and Apitoken
username = os.environ["CONFLUENCE_USERNAME"]
confluence_apitoken = os.environ["CONFLUENCE_APITOKEN"]

def get_confluence_page_html(username, confluence_apitoken):
    """Get the confluence page to read the table data.

    Args:
        username (str) : email id
        confluence_apitoken (str) : confluence api token
        
    Returns:
        page_body : confluence page body where table resides
    """
    params = {"expand": "body.view"}
    auth = (username, confluence_apitoken)

    response = requests.get(confluence_rest_api, params=params, auth=auth)
    if response.status_code == 200:
        data = response.json()
        storage_content = data.get("body", {}).get("storage", {}).get("value", "")
        page_body = decode_confluence_storage(storage_content)
        return page_body
    else:
        print(
            f"Failed to retrieve Confluence page. Status code: {response.status_code}"
        )
        return None

def decode_confluence_storage(storage_content):
    """Get the decode confluence storage data.

    Args:
        storage_content (str) :html parser
          
    Returns:
        soup : decode html parser confluence storage.
    """
    soup = BeautifulSoup(storage_content, "html.parser")
    return str(soup)

def extract_table_data(html_content):
    """Get the table data.

    Args:
        html_content (str) : content of html
          
    Returns:
        table_data : Extract table data as a list.
    """  
    soup = BeautifulSoup(html_content, "html.parser")
    table = soup.find("table")
    
    if table:
        # Extract table data as a list of lists
        table_data = []
        header = [th.get_text(strip=True) for th in table.find_all('th')]
        # for row in table.find_all("tr"):
        for row in table.find_all('tr')[1:]:
            # row_data = [
                # cell.get_text(strip=True) for cell in row.find_all(["td", "th"])
            row_data = [str(td) for td in row.find_all(['td', 'th'])]
            # table_data.append(row_data)
            table_data.append(dict(zip(header, row_data)))
        return table_data
    else:
        print("No table found on the Confluence page.")
        return None

def clean_text(text):
    """Remove HTML tags and additional characters
  
    Returns:
        Data with no paragraphs, line breaks, and additional HTML tags
    """    
    # Remove HTML tags
    cleaned_text = BeautifulSoup(text, 'html.parser').get_text(separator=' ')
    # Remove additional characters
    cleaned_text = cleaned_text.replace('<br/>', '').replace('<p>', '').replace('</p>', '').replace('</td>', '').strip()
    return cleaned_text


def find_service_name(table_data, target_application_name):
#     """Get the service name from confluence page table

#     Args:
#         data (str) : table data from confluence
#         name (str) : application name
        
#     Returns:
#         app_source : Application name and service name as key and value
#     """    
    app_source = {}
    for row in table_data:
        application_name = row['Applications']
        if target_application_name.lower() in application_name.lower():
            # Clean application name
            application_name = clean_text(application_name)

            service_name_data = row['ServiceName']
            # Extract service names and corresponding values
            service_names = [item.split(':') for item in service_name_data.split('<p>') if ':' in item]
            service_data = {name.strip(): clean_text(value) for name, value in service_names if len(name) > 0 and len(value) > 0}
            
            app_source[application_name] = service_data
    return app_source

#Get confluence url and application name
argparser = argparse.ArgumentParser(prog='service-getter',
                                    description='To read table content from confluence page and providing output to jenkins pipeline')
argparser.add_argument('-u', '--url', type=str, metavar='', required=True, help='url to access confluence page')
argparser.add_argument('-a','--appname', type=str, metavar='', required=True, help='Application name')

args = argparser.parse_args()
confluence_rest_api = args.url
application_name = args.appname

#  To get confluence page data
html_content = get_confluence_page_html(username, confluence_apitoken)

if html_content:
    table_data = extract_table_data(html_content)
    if table_data:
        service_names = find_service_name(table_data, application_name)
        # Print the result in the desired format    
        if service_names:
            service_names_json = json.dumps(service_names, indent=2)
            print(service_names_json)
        else:
            print(f"service names not found ")    