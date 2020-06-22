# First argument is password:
PW=$1

# Create 'books' db user:
sudo -u postgres psql -c "CREATE ROLE books LOGIN CREATEDB PASSWORD '$PW';"

# Create 'django-progress' db table:
sudo -u postgres createdb django-progress -O books
