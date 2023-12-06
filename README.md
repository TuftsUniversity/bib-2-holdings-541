**Title:** BibToHolding.py

**Author:** Henry Steele, Library Technology Services, Tufts University

**Purpose:**

- This program adds a fixed 541 field from the bib record to attached holding records

**Input:**

- a .txt file containing a list of MMS ID record numbers, one per line
- The updated records are written to Alma and recorded in the updated\_holdings XML file.  Any errors are recorded in records\_with\_errors.txt

**Installation:**

- This branch of the project is set to work with Python 2
- pull this branch (master) down from Github
- unzip
- to install the requirements necessary for this script to run
  - pip install -r requirements.txt


**Running:**


- navigate to the project&#39;s directory
- have your list of MMS IDs ready in a folder you can find in the file picker
- execute the script
  - python bibToHoldings.py
- choose the input file
- the script runs outputting the holdings it writes to the update holdings XML file
