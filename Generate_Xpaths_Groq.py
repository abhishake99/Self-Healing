import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import pandas as pd

# Load API Key
load_dotenv()
GROQ_API_KEY = os.environ['GROQ_API_KEY']

# Initialize Model
model = ChatGroq(
    model='qwen-2.5-coder-32b',
    groq_api_key=GROQ_API_KEY,
    temperature=0.6,
    top_p=0.95,
    streaming=True,
    stop_sequences=None
)

# Read CSV File
df = pd.read_csv('output_xpaths.csv')
df["generalized_xpath"] = ""

# Process Each XPath
for i in range(len(df)):
    input_xpath = str(df['path'][i])

    # Strict Prompt to Ensure Only XPath is Returned
    prompt = f'''You are an expert in web scraping and XPath optimization. Your task is to rewrite the given XPath into a more generalized, robust and long lasting version by removing unnecessary specificity while keeping it accurate.  
    **Return ONLY the generalized XPath, with NO explanations, NO comments, and NO additional text.** 

    ### Input XPath:  
    "{input_xpath}"  

    Output the optimized XPath ONLY.  
    '''

    # Invoke Model with Correct Prompt
    response = model.invoke(prompt).content.strip()

    # Ensure We Only Keep the XPath (Remove Explanations If Any)
    generalized_xpath = response.split("\n")[0]  # Take only the first line

    # Save Output
    df.at[i, 'generalized_xpath'] = generalized_xpath
    print("Generalized XPath:", generalized_xpath)

# Save Updated CSV
df.to_csv('output_xpaths_generalized.csv', index=False)
