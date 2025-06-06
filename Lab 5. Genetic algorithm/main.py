import random
import pygame

NUM_CITIES = 20
GENERATIONS = 1500
MUTATION_RATE = 0.05
POPULATION_SIZE = 3000
MAP_SIZE = 500

# pygame
WIDTH, HEIGHT = 1000, 600

def distance_matrix(cities):
    matrix = [[0 for _ in range(NUM_CITIES)] for _ in range(NUM_CITIES)]

    for i in range(NUM_CITIES):
        for j in range(NUM_CITIES):
            dx = cities[i][0] - cities[j][0]
            dy = cities[i][1] - cities[j][1]
            matrix[i][j] = (dx**2 + dy**2)**0.5

    return matrix

def init_population():
    population = []
    for i in range(POPULATION_SIZE):
        route = random.sample(range(NUM_CITIES), NUM_CITIES)
        population.append(route)
    return population

def fitness_evaluation(population, distance_matrix):
    fitness_score = []

    for route in population:
        total_distance = 0
        for i in range(len(route)):
            from_city = route[i]
            to_city = route[(i+1) % len(route)]
            total_distance += distance_matrix[from_city][to_city]

        fitness_score.append((route, total_distance))

    return fitness_score

def select_parents(fitness_score, t=2):
    parents = []
    for _ in range(POPULATION_SIZE):
        tournament = random.sample(fitness_score, t)
        winner = min(tournament, key=lambda x: x[1])
        parents.append(winner[0])
    return parents

def crossover(parent_a, parent_b):
    start = random.randint(0, len(parent_a)-1)
    end = random.randint(start, len(parent_b))

    child = parent_a[start:end]
    for city in parent_b:
        if city not in child:
            child.append(city)

    return child

def mutation(child):
    if random.random() < MUTATION_RATE:
        i, j = random.sample(range(NUM_CITIES), 2)
        child[i], child[j] = child[j], child[i]

    return child

def generate_new_population(parents):
    new_population = []

    while len(new_population) < POPULATION_SIZE:
        parent_a, parent_b = random.sample(parents, 2)

        child_a = mutation(crossover(parent_a, parent_b))
        child_b = mutation(crossover(parent_b, parent_a))

        new_population.append(child_a)
        if len(new_population) < POPULATION_SIZE:
            new_population.append(child_b)

    return new_population

def draw_route(route, distance, generation, x_offset, title):
    pygame.draw.rect(win, (30, 30, 30), (x_offset, 0, WIDTH // 2, HEIGHT))

    for i in range(len(route)):
        from_city = (cities[route[i]][0] + x_offset, cities[route[i]][1])
        to_city = (cities[route[(i + 1) % len(route)]][0] + x_offset, cities[route[(i + 1) % len(route)]][1])
        pygame.draw.line(win, (0, 255, 0), from_city, to_city, 2)

    for x, y in cities:
        pygame.draw.circle(win, (255, 100, 100), (x + x_offset, y), 6)

    text_title = font.render(title, True, (255, 255, 255))
    text_gen = font.render(f"Покоління: {generation}", True, (255, 255, 255))
    text_dist = font.render(f"Відстань: {distance:.2f}", True, (255, 255, 255))

    win.blit(text_title, (x_offset + 150, 500))
    win.blit(text_gen, (x_offset + 150, 525))
    win.blit(text_dist, (x_offset + 150, 550))

def update_display(current_route, current_dist, best_route, best_dist, generation):
    draw_route(current_route, current_dist, generation, 0, "ПОТОЧНЕ ПОКОЛІННЯ")
    draw_route(best_route, best_dist, None, WIDTH // 2, "НАЙКРАЩИЙ МАРШРУТ")
    pygame.display.update()

if __name__ == '__main__':
    pygame.init()
    font = pygame.font.SysFont("arial", 20)
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Комівояжер: генетичний алгоритм")

    cities = [(random.randint(0, MAP_SIZE), random.randint(0, MAP_SIZE)) for _ in range(NUM_CITIES)]

    dist_matrix = distance_matrix(cities)
    population = init_population()

    best_ever = None
    best_ever_distance = float("inf")

    for generation in range(GENERATIONS):
        fitness = fitness_evaluation(population, dist_matrix)
        fitness.sort(key=lambda x: x[1])
        best_route, best_distance = fitness[0]

        if best_distance < best_ever_distance:
            best_ever = best_route
            best_ever_distance = best_distance

        update_display(best_route, best_distance, best_ever, best_ever_distance, generation + 1)
        pygame.time.delay(0)

        parents = select_parents(fitness)
        population = generate_new_population(parents)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
