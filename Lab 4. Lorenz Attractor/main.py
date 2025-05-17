import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
import tkinter as tk
import tkinter.ttk as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = tk.Tk()
root.title("Lorenz Attractor")

frame = ttk.Frame(root)
frame.pack(side='left', fill='y', padx=10, pady=10)

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

def add_entry(title, default):
    label = ttk.Label(master=frame, text=title)
    entry = ttk.Entry(master=frame)
    entry.insert(0, str(default))

    label.pack()
    entry.pack()

    return entry

def lorenz_equation(vector, t, sigma, beta, rho):
    x, y, z = vector    # 3д вектор, який відповідає за позицію у просторі

    d_vector = [
        sigma*(y - x),
        rho*x - y - x*z,
        x*y - beta*z
    ]
    return d_vector

def solve_lorenz(position_0, time_points, sigma, beta, rho):
    return odeint(lorenz_equation, position_0, time_points, args=(sigma, beta, rho))

def plot_lorenz():
    ax.clear()

    try:
        sigma_value = float(sigma.get())
        beta_value = float(beta.get())
        rho_value = float(rho.get())

        x0_value = float(x0.get())
        y0_value = float(y0.get())
        z0_value = float(z0.get())
    except ValueError:
        print("Введіть число!")
        return

    position_0 = [x0_value, y0_value, z0_value]  # відображає позицію при t=0
    time_points = np.linspace(0, 40, 10000)  # відображається 10000 точка впродовж 40 секунд

    positions = solve_lorenz(position_0, time_points, sigma_value, beta_value, rho_value)
    x_sol, y_sol, z_sol = positions[:, 0], positions[:, 1], positions[:, 2]

    ax.plot(x_sol, y_sol, z_sol)

    canvas.draw()

sigma = add_entry("sigma", 10)
beta = add_entry("beta", 8 / 3)
rho = add_entry("rho", 28)

x0 = add_entry("x0", 0)
y0 = add_entry("y0", 1)
z0 = add_entry("z0", 1)

button = ttk.Button(master=frame, text='Побудувати', command=plot_lorenz)
button.pack(pady=10)

if __name__ == '__main__':
    plot_lorenz()
    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()
