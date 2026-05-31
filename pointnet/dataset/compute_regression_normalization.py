import numpy as np
import json
import sys
from pathlib import Path

def compute_mean_std(parameters_dir):
    parameters_path = Path(parameters_dir)
    parameters_filenames = list(Path.iterdir(parameters_path))
    parameters_filenames.sort()

    size = len(parameters_filenames)

    regression_parameters = np.zeros((round(size * 0.8), 5), dtype=np.float32)
    for i, parameters_filename in enumerate(parameters_filenames[:round(size * 0.8)]):
        with open(parameters_filename, "r") as f:
            params = json.load(f)
        
        regression = np.array([
            params["trunk"]["Length"],
            params["trunk"]["Start Radius"],
            params["branches1"]["Length"],
            params["branches1"]["Density"],
            params["branches1"]["Up Attraction"]
        ], dtype=np.float32)

        regression_parameters[i, :] = regression

    mean = np.mean(regression_parameters, axis=0, dtype=np.float32)
    std = np.std(regression_parameters, axis=0, dtype=np.float32)

    mean_path = Path(__file__).parent.joinpath("mean.npy")
    std_path = Path(__file__).parent.joinpath("std.npy")

    np.save(mean_path, mean)
    np.save(std_path, std)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Use:\npython {sys.argv[0]} [parameters_dir]")
    else:
        compute_mean_std(sys.argv[1])