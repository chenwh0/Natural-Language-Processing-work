# AI Usage Disclosure Appendix

**Student Name:** Wen-Hsin Chen  
**Assignment/Project Title:** Assignment 101: Intermediate Web Scraping with BeautifulSoup and Data Analysis  
**Date:** 8/31/2025 

---

## Instructions
**Complete this appendix whenever you use ANY artificial intelligence tools during your coursework.** This includes grammar checkers, code assistants, search engines with AI features, chatbots, or any other AI-powered tools. Attach this completed form to your assignment submission.

**If you did NOT use any AI tools, check here:** ☐ *No AI tools were used for this assignment*

---

## AI Tool Usage Log

**Complete one section below for EACH AI tool or session used:**

### AI Tool #1

**Tool Name/Platform:** ChatGPT

**Date & Time of Use:** 8/31/2025 - 10:00am

**Purpose of Use:**  Brainstorming on how to extract content nestled inside <script type ="">  

**Exact Prompt(s) or Query(ies) Used:**
```
"How to web-scrape one "<script type="application/ld+json">" using BeautifulSoup?"
```

**Complete AI Output/Response:**
```
To web-scrape just one <script type="application/ld+json"> tag using BeautifulSoup, you can use the .find() method instead of .find_all().

✅ Minimal Example
import requests
from bs4 import BeautifulSoup
import json

# Step 1: Fetch the webpage
url = 'https://example.com'  # Replace with the actual URL
response = requests.get(url)
html = response.text

# Step 2: Parse the HTML with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')

# Step 3: Find the first <script type="application/ld+json"> tag
json_ld_tag = soup.find('script', type='application/ld+json')

# Step 4: Extract and parse the JSON
if json_ld_tag:
    try:
        json_data = json.loads(json_ld_tag.string)
        print(json.dumps(json_data, indent=2))  # Pretty-print
    except (json.JSONDecodeError, TypeError) as e:
        print(f"Error parsing JSON: {e}")
else:
    print("No <script type='application/ld+json'> found.")

```

**How You Used This Output:**  
*(Describe step-by-step what you did with the AI-generated content)*
```
1. I only used the line `soup.find('script', type='application/ld+json')` 
2. After printing out the extracted output, I recognized the content as JSON data & searched how to convert json str to json data in: https://www.w3schools.com/python/python_json.asp 

```



## Final Work Attribution

**Percentage of final work that is your original contribution:** 95%

**Brief summary of your independent work process:**  
*(Describe the parts of the assignment you completed entirely on your own)*
```
Except for that one line of code, everything else I either implemented on my own, studied through the practice example provided for Assignment 101, or studied by going to the following online tutorials:
* https://www.w3schools.com/python/python_json.asp
* https://www.geeksforgeeks.org/python/python-convert-html-characters-to-strings/
* https://www.geeksforgeeks.org/python/create-a-pandas-dataframe-from-list-of-dicts/
* https://www.geeksforgeeks.org/python/apply-a-function-to-single-or-selected-columns-or-rows-in-pandas-dataframe/
* https://www.geeksforgeeks.org/python/how-to-plot-value-counts-in-pandas/

```

**Learning reflection:**  
*(What did you learn through this process? How did the AI tool help or hinder your understanding?)*
```
I learned alot about the challenges and methods in webscraping as well as refreshed my memory on how to work with Pandas and matplotlib in this assignment.
The AI coded helped me understand that to extract from content nestled inside of a <script> tag of a certain type using BeautifulSoup, all I needed to do is add the type name afterwards like: soup.find('script', type='typeName')

```

---

## Academic Integrity Acknowledgment

By submitting this appendix, I affirm that:
- [✅] I have disclosed ALL AI tool usage for this assignment
- [✅] The prompts and outputs listed above are complete and accurate
- [✅] I understand that undisclosed AI usage constitutes academic dishonesty
- [✅] The final submitted work represents my understanding of the course material

**Student Signature:** Wen-Hsin Chen
**Date:** 8/31/2025

---

*Submit this completed appendix along with your assignment. Failure to include this form when AI tools were used will be treated as academic dishonesty under university policy.*