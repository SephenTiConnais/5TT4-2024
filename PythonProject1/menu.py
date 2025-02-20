import pygame
import random
import pytmx

pygame.init()
clock = pygame.time.Clock()

# Configuration de la fenêtre
TILE_SIZE = 32
WIDTH, HEIGHT = 30 * TILE_SIZE, 20 * TILE_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Liste des cartes disponibles
map_files = ["map facile.tmx", "map debutant.tmx", "map intermediaire.tmx", "map master.tmx"]
selected_map = 0  # Par défaut, la première carte est sélectionnée

# Police pour le menu
font = pygame.font.SysFont('arial', 32)

# Fonction d'affichage du menu
def show_map_menu():
    global selected_map
    menu_running = True

    while menu_running:
        screen.fill((0, 0, 0))

        # Afficher les options de carte
        for i, map_name in enumerate(map_files):
            color = (255, 255, 255) if i != selected_map else (0, 255, 0)  # Vert pour la sélection
            text = font.render(map_name, True, color)
            screen.blit(text, (WIDTH // 2 - 100, 150 + i * 50))

        pygame.display.flip()

        # Gestion des événements du menu
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_map = (selected_map - 1) % len(map_files)
                elif event.key == pygame.K_DOWN:
                    selected_map = (selected_map + 1) % len(map_files)
                elif event.key == pygame.K_RETURN:
                    menu_running = False  # Sortir du menu et lancer le jeu

# Afficher le menu de sélection de carte
show_map_menu()

# Charger la carte sélectionnée
tmx_data = pytmx.load_pygame(map_files[selected_map])

# Charger les murs de la carte
walls = set()
wall_layer = tmx_data.get_layer_by_name("walls")  # Vérifie que la couche existe
if isinstance(wall_layer, pytmx.TiledTileLayer):
    for x, y, gid in wall_layer:
        if gid != 0:  # Si la tuile n'est pas vide, c'est un mur
            walls.add((x * TILE_SIZE, y * TILE_SIZE))

# Paramètres du serpent
player_speed = TILE_SIZE
player_x, player_y = 12 * TILE_SIZE, 15 * TILE_SIZE
snake_body = [(player_x, player_y)]
snake_direction = (0, 0)

# Fonction pour générer une position de nourriture qui n'est pas sur un mur
def spawn_food():
    while True:
        x = random.randint(0, WIDTH // TILE_SIZE - 1) * TILE_SIZE
        y = random.randint(0, HEIGHT // TILE_SIZE - 1) * TILE_SIZE
        if (x, y) not in walls and (x, y) not in snake_body:
            return x, y

# Placer la première nourriture
food_x, food_y = spawn_food()

# Système de score
score = 0
font = pygame.font.SysFont('arial', 24)

# Jeu en cours
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Contrôler le serpent avec les touches directionnelles
    keys = pygame.key.get_pressed()
    new_direction = snake_direction  # Garder la direction actuelle en cas de mur

    if keys[pygame.K_UP] and snake_direction != (0, player_speed):
        new_direction = (0, -player_speed)
    if keys[pygame.K_DOWN] and snake_direction != (0, -player_speed):
        new_direction = (0, player_speed)
    if keys[pygame.K_LEFT] and snake_direction != (player_speed, 0):
        new_direction = (-player_speed, 0)
    if keys[pygame.K_RIGHT] and snake_direction != (-player_speed, 0):
        new_direction = (player_speed, 0)

    # Calculer la nouvelle position
    new_head = (snake_body[0][0] + new_direction[0], snake_body[0][1] + new_direction[1])

    # Vérifier si le mouvement est possible (pas de mur)
    if new_head not in walls:
        snake_direction = new_direction  # Accepter la direction seulement si pas de mur
        snake_body.insert(0, new_head)

        # Vérifier si le serpent mange la nourriture
        if new_head == (food_x, food_y):
            food_x, food_y = spawn_food()  # Générer une nouvelle nourriture
            score += 1  # Augmenter le score lorsque la nourriture est mangée
        else:
            snake_body.pop()  # Retirer la dernière case pour garder la longueur constante

    # Vérifier si le serpent se mord lui-même
    if snake_body[0] in snake_body[1:]:
        print("GAME OVER (collision avec soi-même)")
        running = False
    if new_head[0] < 0 or new_head[0] >= WIDTH or new_head[1] < 0 or new_head[1] >= HEIGHT:
        print("GAME OVER")
        running = False

    # Dessiner la carte et les murs
    screen.fill((0, 0, 0))
    for layer in tmx_data.visible_layers:
        if isinstance(layer, pytmx.TiledTileLayer):
            for x, y, gid in layer:
                tile = tmx_data.get_tile_image_by_gid(gid)
                if tile:
                    screen.blit(tile, (x * TILE_SIZE, y * TILE_SIZE))

    # Dessiner le serpent
    for segment in snake_body:
        pygame.draw.rect(screen, (0, 255, 0), pygame.Rect(segment[0], segment[1], TILE_SIZE, TILE_SIZE))

    # Dessiner la nourriture
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(food_x, food_y, TILE_SIZE, TILE_SIZE))

    # Afficher le score
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))

    pygame.display.flip()
    clock.tick(10)  # Vitesse du jeu (fps)

pygame.quit()
