import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd


def naca_duct(length=200.0, throat_width=60.0, throat_depth=20.0, n=20):
    x = np.linspace(0, length, n)
    xi = x / length

    half_width = 0.5 * throat_width * 0.5 * (1 - np.cos(np.pi * xi))
    depth = throat_depth * 0.5 * (1 - np.cos(np.pi * xi))

    return x, half_width, depth


def create_3d_surface(x, half_width, depth, ny=50):
    X_list, Y_list, Z_list = [], [], []

    for i in range(len(x)):
        y = np.linspace(-half_width[i], half_width[i], ny)

        if half_width[i] > 1e-9:
            z = -depth[i] * (1 - (y / half_width[i])**2)
        else:
            z = np.zeros_like(y)

        X_list.append(np.full_like(y, x[i]))
        Y_list.append(y)
        Z_list.append(z)

    return np.array(X_list), np.array(Y_list), np.array(Z_list)


def export_coordinates(x, half_width, depth, filename="naca_duct.csv"):
    for i in range(len(x)):
        y = np.linspace(-half_width[i], half_width[i], 50)
        z = -depth[i] * (1 - (y / half_width[i])**2) if half_width[i] > 0 else 0
    
        section = pd.DataFrame({
            "x": np.full_like(y, x[i]),
            "y": y,
            "z": z
        })
    
        section.to_csv(f"section_{i}.csv", index=False)


def plot_naca_duct(length=200.0, throat_width=60.0, throat_depth=20.0):
    x, half_width, depth = naca_duct(length, throat_width, throat_depth)

    fig = plt.figure(figsize=(14, 10))

    # -------------------------
    # Top view with points
    # -------------------------
    ax1 = fig.add_subplot(2, 2, 1)
    ax1.plot(x, half_width)
    ax1.plot(x, -half_width)

    ax1.scatter(x, half_width, s=10)
    ax1.scatter(x, -half_width, s=10)

    # Annotate a few points (avoid clutter)
    step = len(x) // 10
    for i in range(0, len(x), step):
        ax1.text(x[i], half_width[i],
                 f"({x[i]:.0f},{half_width[i]:.0f})", fontsize=7)

    ax1.set_title("Top View (with coordinates)")
    ax1.set_xlabel("x [mm]")
    ax1.set_ylabel("y [mm]")
    ax1.axis("equal")
    ax1.grid(True)

    # -------------------------
    # Side view with points
    # -------------------------
    ax2 = fig.add_subplot(2, 2, 2)
    ax2.plot(x, -depth)
    ax2.scatter(x, -depth, s=10)

    for i in range(0, len(x), step):
        ax2.text(x[i], -depth[i],
                 f"({x[i]:.0f},{-depth[i]:.0f})", fontsize=7)

    ax2.set_title("Side View (with coordinates)")
    ax2.set_xlabel("x [mm]")
    ax2.set_ylabel("z [mm]")
    ax2.grid(True)

    # -------------------------
    # Width & depth distributions
    # -------------------------
    ax3 = fig.add_subplot(2, 2, 3)
    ax3.plot(x, 2 * half_width, label='Width')
    ax3.plot(x, depth, label='Depth')

    ax3.scatter(x, 2 * half_width, s=10)
    ax3.scatter(x, depth, s=10)

    ax3.set_title("Geometry Distributions")
    ax3.set_xlabel("x [mm]")
    ax3.set_ylabel("mm")
    ax3.legend()
    ax3.grid(True)

    # -------------------------
    # 3D plot with mesh points
    # -------------------------
    ax4 = fig.add_subplot(2, 2, 4, projection='3d')
    X, Y, Z = create_3d_surface(x, half_width, depth)

    ax4.plot_surface(X, Y, Z, alpha=0.8)

    # show mesh points (light sampling)
    ax4.scatter(X[::10], Y[::10], Z[::10], s=5)

    ax4.set_title("3D Duct with Mesh Points")
    ax4.set_xlabel("x")
    ax4.set_ylabel("y")
    ax4.set_zlabel("z")

    plt.tight_layout()
    plt.show()

    # Print sample coordinates
    print("\nSample coordinates:")
    for i in range(0, len(x), step):
        print(f"x={x[i]:.2f}, width={2*half_width[i]:.2f}, depth={depth[i]:.2f}")

    # Export full dataset
    export_coordinates(x, half_width, depth)


if __name__ == "__main__":
    plot_naca_duct(
        length=250.0,
        throat_width=80.0,
        throat_depth=25.0
    )