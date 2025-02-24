from AIOdriver.functions import createwebdriver
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import time
import re
import pandas as pd

driver=createwebdriver('',driver_type='uc')
# Load the webpage
web_page_url=""
driver.get(web_page_url)  # Replace with the actual URL
time.sleep(10)  # Wait for page to load

filter_xpath=""
# Extract elements using XPath
elements = driver.find_elements(By.XPATH, "//*" if filter_xpath=="" else filter_xpath)

def clean_html(html):
    """Removes unnecessary tags but keeps the HTML structure intact."""
    soup = BeautifulSoup(html, "html.parser")

    # Remove unwanted tags
    for tag in soup(["script", "style", "meta", "noscript", "link", "iframe", "svg"]):
        tag.decompose()

    # Return cleaned HTML as a structured string
    return soup.prettify()

# Store extracted HTML content in a file
html_content = "".join([element.get_attribute("outerHTML") for element in elements])

cleaned_html = clean_html(html_content)
with open("output.html", "w", encoding="utf-8") as file:
    file.write(cleaned_html)


# Close the driver
driver.quit()

print("Step 1: HTML content saved to output.html")


def dom_to_json(element):
    """Recursively converts an HTML element to JSON."""
    return {
        "tag": element.name,
        "attributes": element.attrs,
        "text": element.find(text=True,recursive=False).strip() if element.find(text=True,recursive=False)!=None else element.find(text=True,recursive=False) ,
        "children": [dom_to_json(child) for child in element.find_all(recursive=False)]
    } if element else None

def html_to_json(html):
    """Converts entire HTML body into JSON structure."""
    soup = BeautifulSoup(html, "html.parser")
    # print(soup.find_all())
    return dom_to_json(soup)

with open('output.html', 'r',encoding='utf-8') as file:
    cleaned_html = file.read()  
    # print(cleaned_html)
html_json = html_to_json(cleaned_html)
# Save JSON structure
with open("output.json", "w") as f:
    json.dump(html_json, f, indent=2)

print("Step 2: HTML content converted to JSON and saved to output.json")

def get_attribute_xpath(attributes):
    """Constructs an XPath condition from element attributes (prefers id > class > other attributes)."""
    if "id" in attributes:
        return f'[@id="{attributes["id"]}"]'
    elif "class" in attributes and attributes["class"]:
        class_value = " ".join(attributes["class"])  # Join class list into a string
        return f'[@class="{class_value}"]'
    else:
        conditions = [f'[@{key}="{value}"]' for key, value in attributes.items()]
        return "".join(conditions) if conditions else ""

def extract_relative_xpaths(json_obj, path=""):
    """
    Recursively extracts relative XPaths for elements containing text, using attributes instead of indexes.
    
    Args:
    - json_obj (dict): The nested JSON object representing the HTML structure.
    - path (str): The current relative XPath being constructed.

    Returns:
    - List of relative XPaths for elements that contain text.
    """
    xpaths = []

    # Base case: If the element h as text, add the relative path
    if json_obj["text"]!=None and "text" in json_obj and len(json_obj["text"].strip())>0:
        # print(path)
        temp={
            "path":path,
            "text":json_obj["text"]
        }
        xpaths.append(temp)

    # If the element has children, traverse them recursively
    if "children" in json_obj and isinstance(json_obj["children"], list):
        for child in json_obj["children"]:
            tag = child.get("tag", "unknown")
            attributes = child.get("attributes", {})

            # Construct XPath using attributes instead of index
            attr_condition = get_attribute_xpath(attributes)
            new_path = f"{path}/{tag}{attr_condition}" if path else f"{tag}{attr_condition}"
            
            xpaths.extend(extract_relative_xpaths(child, new_path))

    return xpaths

with open('output.json') as f:
    nested_json= json.load(f)
relative_xpaths = extract_relative_xpaths(nested_json)

df=pd.DataFrame(relative_xpaths)
df.drop_duplicates(subset='text', keep="first",inplace=True)
df=df.drop(df[df['text'].str.len()<5].index)
df.to_csv('output_xpaths.csv',index=False)

print("Step 3: Extracted relative XPaths saved to output_xpaths.csv")
