import unittest
import random
from main import (
    NUM_CITIES, POPULATION_SIZE, distance_matrix, init_population,
    fitness_evaluation, select_parents, crossover, mutation,
    generate_new_population
)

class TestTSPGeneticAlgorithm(unittest.TestCase):
    def setUp(self):
        random.seed(42)
        self.cities = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(NUM_CITIES)]
        self.dist_matrix = distance_matrix(self.cities)
        self.population = init_population()

    def test_distance_matrix(self):
        # перевірка розміру матриці
        self.assertEqual(len(self.dist_matrix), NUM_CITIES)
        for row in self.dist_matrix:
            self.assertEqual(len(row), NUM_CITIES)

        # перевірка відстані від міста до самого себе
        for i in range(NUM_CITIES):
            self.assertEqual(self.dist_matrix[i][i], 0)

        # перевірка симетричності матриці
        for i in range(NUM_CITIES):
            for j in range(NUM_CITIES):
                self.assertAlmostEqual(self.dist_matrix[i][j], self.dist_matrix[j][i])

    def test_fitness_evaluation(self):
        fitness = fitness_evaluation(self.population, self.dist_matrix)
        self.assertEqual(len(fitness), POPULATION_SIZE)
        for route, dist in fitness:
            self.assertIsInstance(route, list)
            self.assertIsInstance(dist, float)

    def test_parent_selection(self):
        fitness = fitness_evaluation(self.population, self.dist_matrix)
        parents = select_parents(fitness)
        self.assertEqual(len(parents), POPULATION_SIZE)
        for parent in parents:
            self.assertEqual(len(set(parent)), NUM_CITIES)

    def test_crossover_and_mutation(self):
        parent_a = self.population[0]
        parent_b = self.population[1]

        child = crossover(parent_a, parent_b)
        self.assertEqual(len(set(child)), NUM_CITIES)

        mutated = mutation(child[:])
        self.assertEqual(len(set(mutated)), NUM_CITIES)

    def test_fitness_new_population(self):
        fitness = fitness_evaluation(self.population, self.dist_matrix)
        parents = select_parents(fitness)
        new_population = generate_new_population(parents)

        new_fitness = fitness_evaluation(new_population, self.dist_matrix)
        self.assertEqual(len(new_fitness), POPULATION_SIZE)

    def test_final_result_return_format(self):
        fitness = fitness_evaluation(self.population, self.dist_matrix)
        fitness.sort(key=lambda x: x[1])
        best_route, best_distance = fitness[0]

        self.assertEqual(len(best_route), NUM_CITIES)
        self.assertIsInstance(best_distance, float)

if __name__ == "__main__":
    unittest.main()
