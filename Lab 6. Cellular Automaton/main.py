import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

I = 0  # інфікована (червона)
S = 1  # здорова (зелена)
R = 2  # відновлена (синя)

colors = ['red', 'green', 'blue']
cmap = mcolors.ListedColormap(colors)
bounds = [0, 1, 2, 3]  # межі для I (0), S (1), R (2)
norm = mcolors.BoundaryNorm(bounds, cmap.N)

def create_population(size, infected):
    population = np.full((size, size), S, dtype=int)
    infection_time = np.zeros_like(population)

    amount_of_infected = np.random.choice(size*size, infected, replace=False)
    for i in amount_of_infected:
        x, y = divmod(i, size)
        population[x, y] = I

    return population, infection_time, amount_of_infected

def update_population(population, infection_time, P_infect, T_recover):
    size = population.shape[0]
    new_population = population.copy()
    new_infection_time = infection_time.copy()

    for x in range(size):
        for y in range(size):
            if population[x, y] == I:
                new_infection_time[x, y] += 1
                if new_infection_time[x, y] > T_recover:
                    new_population[x, y] = R
            elif population[x, y] == S:
                for dx, dy in [(-1, 0), (1, 0), (0, 1), (0, -1)]:
                    nx = x + dx
                    ny = y + dy

                    if 0 <= nx < size and 0 <= ny < size and population[nx, ny] == I:
                        if np.random.rand() < P_infect:
                            new_population[x, y] = I
                            new_infection_time[x, y] = 0
            elif population[x, y] == R:
                continue

    return new_population, new_infection_time

def visualise(size, infected, steps, P_infect, T_recover):
    current_population, current_infection_time, amount_of_infected = create_population(size,infected)

    for step in range(steps+1):
        plt.clf()
        plt.imshow(current_population, cmap=cmap, norm=norm)
        plt.title(f'Крок {step}/{steps} | Інфікованих {infected} | T_recover = {T_recover} | P_infect = {P_infect}')
        plt.pause(0.1)

        if step < steps:
            current_population, current_infection_time = update_population(current_population, current_infection_time, P_infect, T_recover)

    plt.show()

visualise(size=60, infected=3, steps=100, P_infect=0.2, T_recover=4)
