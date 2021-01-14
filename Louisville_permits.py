import pdfplumber
import pandas as pd
import re

df = []
with pdfplumber.open(r"C:\Users\tkravits\Github\Building-Permit-Automation\Louisville_December2020.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        df.append(text)
        str1 = ''.join(df)
        core_pat = re.compile(r"CONTACTS", re.DOTALL)
        core = re.search(core_pat, str1).group(0)

        # Test out the imagery, might help keep the order to then convert to dataframe
        im = p0.to_image()

# TODO - Getting the regex pattern to remove the extra spaces