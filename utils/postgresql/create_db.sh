CONF_FILE=$1

if [[ "x$CONF_FILE" == "x" ]]; then
  echo "Please provide path to JSON conf file."
  exit
fi

if [[ ! -f $CONF_FILE ]]; then
  echo "Provided conf file '$CONF_FILE' does not exist"
  exit
fi

DB_USER=$(jq -r '.DB_USER' "$CONF_FILE")
DB_NAME=$(jq -r '.DB_NAME' "$CONF_FILE")
DB_PASSWORD=$(jq -r '.DB_PASSWORD' "$CONF_FILE")

if [[ "x$DB_NAME" == "xnull" ]]; then
  echo "Configuration file '$CONF_FILE' does not provide a DB name."
  exit
fi

if [[ "x$DB_USER" == "xnull" ]]; then
  echo "Configuration file '$CONF_FILE' does not provide a DB user name."
  exit
fi

if [[ "x$DB_PASSWORD" == "xnull" ]]; then
  echo "Configuration file '$CONF_FILE' does not provide a DB password."
  exit
fi

# Create db user:
psql -c "CREATE ROLE $DB_USER LOGIN CREATEDB PASSWORD '$DB_PASSWORD';"

# Create db:
psql -c "CREATE DATABASE $DB_NAME WITH OWNER $DB_USER;"
