CONF_FILE=$1
DUMP_FILE=$2

if [[ "x$CONF_FILE" == "x" ]]; then
  echo "Please provide path to JSON conf file."
  exit
fi

if [[ "x$DUMP_FILE" == "x" ]]; then
  echo "Please provide path to database dump file."
  exit
fi

if [[ ! -f $CONF_FILE ]]; then
  echo "Provided conf file '$CONF_FILE' does not exist"
  exit
fi

if [[ ! -f $DUMP_FILE ]]; then
  echo "Provided db dump file '$DUMP_FILE' does not exist"
  exit
fi

DB_USER=$(jq -r '.DB_USER' "$CONF_FILE")
DB_NAME=$(jq -r '.DB_NAME' "$CONF_FILE")

if [[ "x$DB_NAME" == "xnull" ]]; then
  echo "Configuration file '$CONF_FILE' does not provide a DB name."
  exit
fi

if [[ "x$DB_USER" == "xnull" ]]; then
  echo "Configuration file '$CONF_FILE' does not provide a DB user name."
  exit
fi

# Drop existing db:
sudo -u postgres psql -c "DROP DATABASE $DB_NAME;"
echo "Database $DB_NAME dropped"

# Create empty db:
sudo -u postgres psql -c "CREATE DATABASE $DB_NAME WITH OWNER $DB_USER;"
echo "Database $DB_NAME re-created"

# Load db dump:
pg_restore --verbose --clean --no-acl --no-owner -h localhost -U "$DB_USER" -d "$DB_NAME" $DUMP_FILE
echo "Database $DB_NAME re-populated"

