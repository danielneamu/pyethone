python3 -m venv .venv
source /var/www/html/pyethone/pye_venv/bin/activate

# deactivate the environment
deactivate

# see all modules installed
pip3 freeze

# install & run jupyter lab in venv
https://anbasile.github.io/posts/2017-06-25-jupyter-venv/


🔹 Clean solution for subtree

Since you want repo B to exactly match your local pyethone/ folder, the simplest way is to force push the subtree, which overwrites remote master:

git subtree split --prefix=pyethone -b pyethone-temp
git push pyethone pyethone-temp:master --force
git branch -D pyethone-temp


Explanation:

git subtree split --prefix=pyethone -b pyethone-temp

Creates a temporary branch containing only the pyethone/ folder.

git push pyethone pyethone-temp:master --force

Pushes it to repo B’s master, overwriting remote contents.

git branch -D pyethone-temp

Deletes temporary branch.

✅ After this, repo B master is an exact mirror of your local pyethone/ folder.

🔹 Future workflow

Once repo B is in sync:

# Commit all changes in pyethone to repo A
git add .
git commit -m "Update pyethone"
git push origin master

# Push only pyethone/ to repo B
git subtree push --prefix=pyethone pyethone master


No --force needed unless someone edits repo B directly.

Keeps both repos synced cleanly.