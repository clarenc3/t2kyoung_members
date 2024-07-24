# t2kyoung_members
Simple python script to get members from t2k.org, run over each member and find if they are a student or postdoc, and write to a csv, including their joining date. 

## Running
Change your t2k.org credentials with the `t2k_user` and `t2k_password` variables inside `get_members.py`. Then run `./get_members.py`, which will write the `t2kyoung.csv` output file, and output the progress to screen.

## Examples
The output `csv` file can be directly inputted to Pandas dataframes, for example. The `check_members.py` shows some simple examples of performing selections on the output `csv` file.
