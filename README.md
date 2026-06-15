# OpAmp / LTspice Bayesian Optimization Demo

This repository demonstrates **Bayesian Optimization applied to LTspice circuit simulation** for automatic parameter tuning.

The system treats LTspice as a black-box evaluator and optimizes circuit parameters by iteratively updating a netlist, running simulations, and learning from results using a Gaussian Process model.

---

# Overview

The goal is to automatically optimize a circuit parameter (e.g., resistor value) under a performance constraint.

Each iteration performs:

```text id="bo_flow"
Bayesian Optimization
        ↓
Propose next R value
        ↓
Modify LTspice netlist
        ↓
Run LTspice (batch mode)
        ↓
Read simulation output (.raw)
        ↓
Compute objective function
        ↓
Update surrogate model (Gaussian Process)
```

---

# Optimization Problem

We optimize a resistor value (R_1) under a current constraint.

### Constraint

```text id="constraint"
max(|I(R_1)|) ≤ 40 mA
```

### Objective

Minimize resistor value:

```text id="objective"
minimize R_1
```

### Penalty formulation

To handle constraints, we use a penalty-based objective:

```text id="penalty"
Objective =
    R_1                    (if Imax ≤ 40 mA)
    1000 + penalty         (if Imax > 40 mA)
```

This converts the constrained problem into an unconstrained optimization problem.

---

# Repository Structure

```text id="structure"
.
├── main.py              # Bayesian optimization loop
├── base.cir             # Base LTspice circuit
├── run.cir              # Generated circuit (temporary)
├── run.raw              # LTspice simulation output
├── run.log              # LTspice log file
└── README.md
```

---

# Requirements

## System

* LTspice (must be installed)
* Python 3.9+

## Python packages

```bash id="req"
pip install numpy matplotlib scikit-optimize PyLTSpice
```

---

# How It Works

## 1. Modify Circuit Parameter

The script updates the LTspice netlist:

```python id="update"
update_circuit(R)
```

It replaces:

```text id="netlist"
R1 N003 N002 100
```

with:

```text id="netlist2"
R1 N003 N002 <optimized value>
```

---

## 2. Run LTspice

Executed in batch mode:

```bash id="run"
LTspice.exe -b run.cir
```

---

## 3. Read Simulation Results

Using PyLTSpice:

```python id="read"
raw = RawRead("run.raw")
trace = raw.get_trace("I(R1)")
current = trace.get_wave()
```

---

## 4. Evaluate Objective

We compute:

* Maximum current
* Power consumption
* Objective value

Example:

```text id="example"
R = 250 Ω
Imax = 35 mA
P = 0.30 W
```

---

## 5. Bayesian Optimization

We use Gaussian Process-based optimization:

```python id="bo"
gp_minimize(
    func=objective,
    dimensions=[Real(10, 5000)],
    n_calls=20
)
```

Search range:

* 10 Ω – 5000 Ω

---

# Example Output

```text id="output"
R=120.0 ohm | Imax=42.3 mA | P=0.21 W
R=300.0 ohm | Imax=28.1 mA | P=0.25 W

==== Result ====
Optimal R = 245.6 ohm
```

---

# Visualization

The script generates convergence plots:

* Resistor value history
* Current constraint check
* Objective convergence

Red line indicates constraint:

```text id="limit"
40 mA
```

---

# Why Bayesian Optimization?

Compared to grid search:

* Requires fewer simulations
* Learns from past evaluations
* Balances exploration and exploitation
* Efficient for expensive simulators (LTspice)

---

# Applications

This framework can be extended to:

* Op-amp parameter tuning
* Analog filter design
* Power optimization
* Reaction system modeling
* Laboratory automation
* Robotics experiment optimization

---

# Future Work

* Multi-parameter optimization
* Multi-objective optimization
* Noise-robust optimization
* Hardware-in-the-loop experiments
* Integration with robotic lab systems

---

# Author

Researcher in laboratory automation and computational chemical engineering.

Focus areas:

* Bayesian optimization
* Reaction modeling
* Spectroscopic analysis
* Robotics for chemical research

---

