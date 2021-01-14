import pdfplumber
import pandas as pd
import re
from collections import OrderedDict

df = []
with pdfplumber.open(r"C:\Users\tkravits\Github\Building-Permit-Automation\Louisville_December2020.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        df.append(text)
        str1 = ''.join(df)
#        core_pat = re.compile(r"CONTACTS", re.DOTALL)
#        core = re.search(core_pat, str1).group(0)

# TODO - need to use regex to remove the header and footers of the total pdf to make one large list
# TODO - then I need to group the permits by each new line (aka the permit info and the description)