import socket
import json
import random
import time
from itertools import product

# Configuration du serveur et du client
SERVER_HOST = "172.17.10.48"
SERVER_PORT = 3000
CLIENT_PORT = 8888

# Génère toutes les pièces possibles du jeu Quarto (16 pièces)
def generate_all_pieces():
    features = [['B', 'S'], ['D', 'L'], ['E', 'F'], ['C', 'P']]
    return [''.join(p) for p in product(*features)]

# Liste des lignes gagnantes possibles sur le plateau 4x4
def winning_lines():
    return [
        [0, 1, 2, 3], [4, 5, 6, 7], [8, 9, 10, 11], [12, 13, 14, 15],  # lignes
        [0, 4, 8, 12], [1, 5, 9, 13], [2, 6, 10, 14], [3, 7, 11, 15],  # colonnes
        [0, 5, 10, 15], [3, 6, 9, 12]  # diagonales
    ]

# Vérifie si une configuration est gagnante
def is_winning(board):
    for line in winning_lines():
        pieces = [board[i] for i in line if board[i] is not None]
        if len(pieces) != 4:
            continue
        for i in range(4):
            features = [p[i] for p in pieces]
            if all(f == features[0] for f in features):
                return True
    return False

# Détermine si la partie est terminée (victoire ou plateau plein)
def game_over(state):
    return is_winning(state["board"]) or all(cell is not None for cell in state["board"])

# Fonction d'utilité pour Minimax
def utility(state, player):
    if is_winning(state["board"]):
        return 1 if state["current"] == player else -1
    return 0

# Récupère l'index du joueur courant
def get_current_player(state):
    return state["current"]

# Récupère toutes les positions libres du plateau
def get_possible_positions(board):
    return [i for i, cell in enumerate(board) if cell is None]

# Récupère les pièces encore disponibles

def piece_restantes(board, current_piece):
    used = set(p for p in board if p is not None)
    if current_piece is not None:
        used.add(current_piece)
    return [p for p in generate_all_pieces() if p not in used]
# Applique un coup et retourne un nouvel état du jeu
def apply_move(state, pos, next_piece):
    new_board = state["board"][:]
    new_board[pos] = state["piece"]
    return {
        "players": state["players"],
        "current": 1 - state["current"],
        "board": new_board,
        "piece": next_piece
    }

# Algorithme Minimax récursif
def minimax(state, player, depth=2):
    if game_over(state) or depth == 0:
        return utility(state, player), None

    best_value = float('-inf') if state["current"] == player else float('inf')
    best_action = None

    for pos in get_possible_positions(state["board"]):
        for next_piece in piece_restantes(state["board"], state["piece"]):
            child = apply_move(state, pos, next_piece)
            val, _ = minimax(child, player, depth - 1)

            if state["current"] == player:
                if val > best_value:
                    best_value, best_action = val, (pos, next_piece)
            else:
                if val < best_value:
                    best_value, best_action = val, (pos, next_piece)

    return best_value, best_action

# Fonction principale pour calculer le meilleur coup à jouer
def compute_best_move(board, players, current_player, current_piece):
    state = {
        "players": players,
        "current": players.index(current_player),
        "board": board,
        "piece": current_piece
    }
    _, action = minimax(state, state["current"])
    if action:
        return action
    return None, None

# Répond au ping du serveur
def send_pong(conn):
    response = {"response": "pong"}
    conn.sendall(json.dumps(response).encode())
    print("pong envoyé")

# Gère une requête "play" (jouer un coup)
def play(conn, play_data):
    print("Contenu de la requête play:", json.dumps(play_data, indent=2))

    board = play_data["state"]["board"]
    piece_to_play = play_data["state"]["piece"]
    players = play_data["state"]["players"]
    current_index = play_data["state"]["current"]
    current_player = players[current_index]

    # Si aucune pièce à jouer et plateau plein : abandonner
    if piece_to_play is None and all(cell is not None for cell in board):
        response = {"response": "giveup"}
        conn.sendall(json.dumps(response).encode())
        print("Aucun coup possible, abandon envoyé.")
        return

    # Calcul du meilleur coup
    pos, given_piece = compute_best_move(board, players, current_player, piece_to_play)

    # Si aucun coup possible, abandon
    if pos is None:
        response = {"response": "giveup"}
    else:
        response = {
            "response": "move",
            "pos": pos,
            "piece": given_piece,
            "message": f"Player {current_player} is playing!"
        }

    conn.sendall(json.dumps(response).encode())
    print("Réponse envoyée:", json.dumps(response, indent=2))

# Boucle d'écoute du client pour recevoir les requêtes du serveur
def listen_for_requests():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", CLIENT_PORT))
        s.listen()
        print(f"Écoute sur le port {CLIENT_PORT}...")
        while True:
            conn, _ = s.accept()
            with conn:
                data = conn.recv(4096).decode()
                if not data:
                    continue
                request = json.loads(data)
                if request["request"] == "ping":
                    send_pong(conn)
                elif request["request"] == "play":
                    play(conn, request)
                else:
                    conn.sendall(json.dumps({"response": "error", "error": "unknown request"}).encode())

# Fonction d'abonnement au serveur
def inscription():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_HOST, SERVER_PORT))
        subscribe_msg = {
            "request": "subscribe",
            "port": CLIENT_PORT,
            "name": "QB",
            "matricules": ["23236"]
        }
        s.sendall(json.dumps(subscribe_msg).encode())
        response = s.recv(4096).decode()
        print("Réponse du serveur:", response)

# Lancement uniquement si exécuté directement
if __name__ == "__main__":
    inscription()
    listen_for_requests()
