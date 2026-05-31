import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path
import json
import seaborn as sns
import matplotlib.transforms as mtrans

class_names = [
    "CYLINDRICAL",
    "CONICAL",
    "SPHERICAL",
    "HEMISPHERICAL",
    "TAPERED_CYLINDRICAL",
    "INVERSE_CONICAL",
    "TEND_FLAME",
]

regression_names = [
    "Trunk length",
    "Trunk radius",
    "Branch length",
    "Branch density",
    "Branch up attraction",
]

losses = [
    "total",
    "regression",
    "classification"
]

if len(sys.argv) <= 1:
    print(f"Use:\npython {sys.argv[0]} [path to the results file]")
    exit(-1)
    
results_filename = Path(sys.argv[1])
with open(results_filename, "r") as f:
    results = json.load(f)

print(f"RESULTS ({results_filename.name})")
print(f"losses:")
for loss in losses:
    print(f"  {loss} : {results['losses'][loss]:.3f}")
print(f"accuracy : {results['accuracy']:.3f}")
print(f"MAE:")
for regression_name in regression_names:
    print(f"  {regression_name} : {results['mae'][regression_name]:.3f}")
print("Confusion matrix")
cm = np.array(results["confusion matrix"])
print(cm)

labels = [class_name.replace("_", " ").capitalize() for class_name in class_names]
fig, ax = plt.subplots(1, 1, figsize=(7,6))
fig.suptitle("Crown shape confusion matrix")
sns.heatmap(cm, ax=ax, linecolor="#dddddd", linewidth=0.1, cmap="Greens", annot=True, yticklabels=labels)
ax.set_xticklabels(labels, rotation=45)
transforms = [
    mtrans.Affine2D().translate(-19, 0),
    mtrans.Affine2D().translate(-13, 0),
    mtrans.Affine2D().translate(-15, 0),
    mtrans.Affine2D().translate(-26, 0),
    mtrans.Affine2D().translate(-33, 0),
    mtrans.Affine2D().translate(-27, 0),
    mtrans.Affine2D().translate(-20, 0),
]
for i, t in enumerate(ax.get_xticklabels()):
    t.set_transform(t.get_transform()+transforms[i])

plt.savefig("confusion_matrix.pdf", bbox_inches = "tight")
