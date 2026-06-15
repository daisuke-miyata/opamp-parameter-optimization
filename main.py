import re
import os
import time
import subprocess
import numpy as np
import matplotlib.pyplot as plt
from skopt import gp_minimize
from skopt.space import Real
from PyLTSpice import RawRead

# =========================
# Path settings
# =========================
WORK_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_FILE = os.path.join(WORK_DIR, "base.cir")
WORK_FILE = os.path.join(WORK_DIR, "run.cir")
RAW_FILE = os.path.join(WORK_DIR, "run.raw")
LOG_FILE = os.path.join(WORK_DIR, "run.log")

LTSPICE_EXE = r"C:\Users\YOUR_NAME\AppData\Local\Programs\ADI\LTspice\LTspice.exe"

# =========================
# History buffers
# =========================
R_history = []
obj_history = []
I_history = []
P_history = []

# =========================
# Update circuit parameter
# =========================
def update_circuit(R_value):
    with open(BASE_FILE, "r", encoding="cp932", errors="ignore") as f:
        text = f.read()

    new_text = re.sub(
        r"^R1\s+(\S+)\s+(\S+)\s+\S+",
        f"R1 N003 N002 {float(R_value)}",
        text,
        flags=re.IGNORECASE | re.MULTILINE
    )

    if text == new_text:
        raise ValueError("R1 replacement failed")

    with open(WORK_FILE, "w", encoding="cp932", errors="ignore") as f:
        f.write(new_text)

# =========================
# Run LTspice simulation
# =========================
def run_ltspice():
    if os.path.exists(RAW_FILE):
        os.remove(RAW_FILE)
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)

    result = subprocess.run(
        [LTSPICE_EXE, "-b", WORK_FILE],
        capture_output=True,
        text=True,
        cwd=WORK_DIR
    )

    if result.returncode != 0:
        raise RuntimeError("LTspice failed")

    for _ in range(50):
        if os.path.exists(RAW_FILE):
            return
        time.sleep(0.1)

    raise FileNotFoundError("run.raw not generated")

# =========================
# Evaluate circuit
# =========================
def evaluate(R):
    R = float(R)

    update_circuit(R)
    run_ltspice()

    raw = RawRead(RAW_FILE)
    trace = raw.get_trace("I(R1)")
    current = trace.get_wave()

    max_I = float(np.max(np.abs(current)))
    P = max_I**2 * R

    print(f"R={R:.2f} Ω | Imax={max_I*1000:.2f} mA | P={P*1000:.2f} mW")

    return max_I, P

# =========================
# Objective function
# =========================
def objective(x):
    R = float(x[0])
    max_I, P = evaluate(R)

    # constraint handling
    if max_I > 0.04:
        obj = 1000 + (max_I - 0.04) * 1000
    else:
        obj = R

    R_history.append(R)
    obj_history.append(obj)
    I_history.append(max_I)
    P_history.append(P)

    return obj

# =========================
# Bayesian optimization
# =========================
res = gp_minimize(
    func=objective,
    dimensions=[Real(10, 5000, name="R")],
    n_calls=20,
    random_state=0
)

print("\n==== RESULT ====")
print(f"Optimal R = {res.x[0]:.2f} Ω")
print(f"Best objective = {res.fun}")

# =========================
# Plot results
# =========================
iters = np.arange(1, len(R_history) + 1)

plt.figure(figsize=(10, 8))

plt.subplot(3, 1, 1)
plt.plot(iters, R_history, marker="o")
plt.ylabel("R [Ω]")
plt.grid()

plt.subplot(3, 1, 2)
plt.plot(iters, np.array(I_history) * 1000, marker="o", color="orange")
plt.axhline(40, color="red", linestyle="--")
plt.ylabel("Imax [mA]")
plt.grid()

plt.subplot(3, 1, 3)
plt.plot(iters, obj_history, marker="o", color="green")
plt.xlabel("Iteration")
plt.ylabel("Objective")
plt.grid()

plt.tight_layout()
plt.show()