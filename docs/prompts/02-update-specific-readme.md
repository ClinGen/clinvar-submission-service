I'm going to supply a directory to you. Let's call this directory `dir` for now. Please
do the following tasks making sure to replace `dir` with the name of the directory I
provide to you.

1. Save the old README to a backup file: `mv dir/README.md dir/README.md.bak`. (Only do
   this step if there's a README to back up. Sometimes, there is no README.)
2. Scaffold a new README: `uv run docs.py generate --directory dir`.
3. Read the files listed in the new README.
4. Fill out the directory overview and the descriptions of the files listed in the new
   README.
