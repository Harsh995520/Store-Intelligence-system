import pandas as pd
import matplotlib.pyplot as plt

data = pd.read_csv(
    "data/positions.csv",
    names=["x", "y"]
)

plt.hist2d(
    data["x"],
    data["y"],
    bins=100
)
plt.hist2d(
    data["x"],
    data["y"],
    bins=100,
    cmap="hot"
)

plt.colorbar()

plt.title("Store Heatmap")

plt.savefig("data/heatmap.png")

plt.show()