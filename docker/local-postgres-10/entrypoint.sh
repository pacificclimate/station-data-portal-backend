# Install SDP backend
pip3 install -i https://pypi.pacificclimate.org/simple/ -e .
pip3 install -r test_requirements.txt

# Use a non-root user so that Postgres doesn't object
# Important: See README for reason user id 1000 is set here.
useradd -u 1000 test
chsh -s /bin/bash test
su test
