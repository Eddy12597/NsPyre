import ti_plotlib as plt

# Data
xs = [i/10 for i in range(-50, 51)]
ys = [0.4*x + 3 + (0.5 if i%7==0 else 0) for i, x in enumerate(xs)]

plt.cls()
plt.auto_window(xs, ys)
plt.grid(1, 1, "dotted")
plt.axes("axes")
plt.labels("X", "Y", x_row=15, y_row=2)
plt.title("Demo: scatter + line + lin_reg")

plt.pen("thin", "solid")
plt.scatter(xs, ys, mark="o")
plt.pen("thin", "dashed")
plt.plot(xs, ys, mark="")             # connect the points with dashed line

plt.pen("medium", "solid")
m, b = plt.lin_reg(xs, ys, display="right")

plt.text_at(2, f"m={m:.3f}, b={b:.3f}", "left")
plt.show_plot()
