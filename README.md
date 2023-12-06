**Title:** BibToHolding.py

**Author:** Henry Steele, Library Technology Services, Tufts University

**Purpose:**

- This program adds a fixed 541 field from the bib record to attached holding records

**Input:**

- a .txt file containing a list of MMS ID record numbers, one per line
- The updated records are written to Alma and recorded in the updated\_holdings XML file.  Any errors are recorded in records\_with\_errors.txt

**Installation:**

- This branch of the project is set to work with Python 3
- to install the requirements necessary for this script to run
  - pip install -r requirements.txt
  - or if you have Python 2 and 3 on your computer,
  - python3 pip -m install requirements.txt
- you'll also need to put the "secrets_local" folder from Box/Files Between LTS and Tisch Library Tech Services/541 to Holdings Record" in the root folder of this project directory (here)

**Running:**

- pull this branch (python 3) down from Github
- unzip
- navigate to the project&#39;s directory
- have your list of MMS IDs ready in a folder you can find in the file picker
- execute the script
  - python3 bibToHoldings.py
- choose the input file
- the script runs outputting the holdings it writes to the update holdings XML file
<<<<<<< HEAD
=======

>>>>>>> e4555b79733539fe3ac966ea519990fac43a1439
