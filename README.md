# t2kyoung_members
Simple python script to get members from t2k.org, run over each member and find if they are a student or postdoc, and write to a csv, including their joining date. 

## Preparation
Download membertable.xml
You can do this in: https://t2k.org/org/reports/membertable clicking in 'Download excel compatible file' at the top of the page.

## Running
Change your t2k.org credentials with the `t2k_user` and `t2k_password` variables inside `get_members.py`. Then run `./get_members.py`, which will write the `t2kyoung.csv` output file, and output the progress to screen.
IMPORTANT: Do not commit those private details to the git repository!!!

## Examples
The output `csv` file can be directly input to Pandas dataframes, for example. You can do some analysis/plots of the data using 'T2K_members_ana.ipynb' (jupyter notebook).

To identify new members you can use the script 'CheckNewMembers.ipynb'. Be sure to update the year/month to the last CM.
