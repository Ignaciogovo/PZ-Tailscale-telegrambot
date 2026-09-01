#!/bin/bash
# shellcheck source=scripts/functions.sh
source "/home/steam/server/functions.sh"

# Configure RCON settings
LogAction "Configuring RCON settings"
cat >/home/steam/server/rcon.yml  <<EOL
default:
  address: "127.0.0.1:${RCON_PORT}"
  password: "${RCON_PASSWORD}"
EOL

config_file="$CONFIG_DIR/Server/${SERVER_NAME}.ini"
mkdir -p "$(dirname "$config_file")"
touch "$config_file"

set_ini_value "$config_file" DefaultPort "${DEFAULT_PORT}"
set_ini_value "$config_file" UDPPort "${UDP_PORT}"
set_ini_value "$config_file" RCONPort "${RCON_PORT}"
set_ini_value "$config_file" RCONPassword "${RCON_PASSWORD}"
if [ -n "${MAX_PLAYERS}" ]; then
    set_ini_value "$config_file" MaxPlayers "${MAX_PLAYERS}"
fi

cd /project-zomboid || exit

LogAction "Starting server"
./start-server.sh \
    -cachedir="$CONFIG_DIR" \
    -adminusername "$ADMIN_USERNAME" \
    -adminpassword "$ADMIN_PASSWORD" \
    -port "$DEFAULT_PORT" \
    -servername "$SERVER_NAME" \
    -steamvac "$STEAM_VAC" "$USE_STEAM"
