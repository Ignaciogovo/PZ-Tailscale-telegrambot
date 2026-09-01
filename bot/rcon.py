import os
from rcon import Client

RCON_HOST = os.getenv("RCON_HOST", "127.0.0.1")
RCON_PORT = int(os.getenv("RCON_PORT", "27015"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "")

def rcon_call(command: str) -> str:
    with Client(RCON_HOST, RCON_PORT, passwd=RCON_PASSWORD, timeout=10) as client:
        return client.run(command)

def get_players() -> list[dict]:
    response = rcon_call("players")
    players = []
    for line in response.strip().split("\n"):
        if not line.strip() or line.startswith("Players"):
            continue
        parts = line.split(",")
        if len(parts) >= 2:
            players.append({
                "name": parts[0].strip(),
                "steam_id": parts[1].strip() if len(parts) > 1 else "unknown"
            })
    return players

def save_server() -> str:
    return rcon_call("save")

def quit_server() -> str:
    return rcon_call("quit")

def kick_player(username: str) -> str:
    return rcon_call(f"kickuser {username}")

def ban_player(username: str) -> str:
    return rcon_call(f"banid {username}")

def unban_player(steam_id: str) -> str:
    return rcon_call(f"unbanid {steam_id}")

def add_user(username: str, password: str, role: str) -> str:
    return rcon_call(f"adduser {username} {password} {role}")

def remove_user(username: str) -> str:
    return rcon_call(f"removeuser {username}")
