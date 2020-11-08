CONF_FILE=$1

if [[ "x$CONF_FILE" == "x" ]]; then
  echo "Please provide path to JSON conf file."
  exit
fi

if [[ ! -f $CONF_FILE ]]; then
  echo "Provided conf file '$CONF_FILE' does not exist"
  exit
fi

DB_NAME=$(jq -r '.DB_NAME' "$CONF_FILE")

if [[ "x$DB_NAME" == "xnull" ]]; then
  echo "Configuration file '$CONF_FILE' does not provide a DB name."
  exit
fi

# Drop existing db:
psql -c "DROP DATABASE $DB_NAME;"
echo "Database $DB_NAME dropped"
