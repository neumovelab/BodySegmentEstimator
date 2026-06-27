# Body Segment Project

Estimating body segment mass, COM, inertia, and geometry across diverse morphologies, with data export and poser-style rendering.

## Requirements

- Python `3.11`
- Install dependencies from `bodysegmentproject/requirements.txt` (includes rendering: `matplotlib`, `Pillow`)

<details open>
<summary><strong>Installation</strong> — expand your OS</summary>

On GitHub, click your OS below to open that section (collapse the other if you only want one open). Paths, activation, and shell symbols differ by platform.

<br>

<details>
<summary><strong>Linux / macOS</strong></summary>

| Convention | Example |
|------------|---------|
| Path separator | `/` (e.g. `bodysegmentproject/requirements.txt`) |
| Activate venv | `source .venv/bin/activate` |
| Line continuation | `\` at end of line |
| Comment | `#` |

```bash
# From the repo root.
python3.11 -m venv .venv

source .venv/bin/activate
python --version    # expect 3.11.x
python -m pip install --upgrade pip
python -m pip install -r bodysegmentproject/requirements.txt
```

Multi-line commands (optional):

```bash
python examples.py custom \
  --height 1.80 \
  --weight 80 \
  --sex male
```

</details>

<details>
<summary><strong>Windows</strong></summary>

| Convention | Example |
|------------|---------|
| Path separator | `\` or `/` (both usually work in Python) |
| Activate venv (Command Prompt) | `.venv\Scripts\activate.bat` |
| Activate venv (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Line continuation (cmd) | `^` at end of line |
| Line continuation (PowerShell) | `` ` `` (backtick) at end of line |
| Comment | `REM` (cmd) or `#` (PowerShell) |

<details>
<summary>Command Prompt</summary>

```bat
REM From the repo root. Use py -3.11 if python is not on PATH.
py -3.11 -m venv .venv

.venv\Scripts\activate.bat
python --version
python -m pip install --upgrade pip
python -m pip install -r bodysegmentproject\requirements.txt
```

</details>

<details>
<summary>PowerShell</summary>

If scripts are blocked, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

```powershell
py -3.11 -m venv .venv

.\.venv\Scripts\Activate.ps1
python --version
python -m pip install --upgrade pip
python -m pip install -r bodysegmentproject/requirements.txt
```

Multi-line example:

```powershell
python examples.py custom `
  --height 1.80 `
  --weight 80 `
  --sex male
```

</details>

</details>

</details>

## Run options

The CLI is `python examples.py <mode>`. Each mode runs the inertia API, builds a personalised mesh, and by default writes data exports plus front and side view PNGs. Override subject fields with `--height`, `--weight`, `--sex`, and (where noted) `--param key=value`.

| Option | Mode | What it does |
|--------|------|----------------|
| **1. Baseline** | `baseline` | Height, weight, and sex only; all segment measures come from the model. |
| **2. Hip and waist modification** | `shape` | Same as baseline, plus preset **hip** and **waist** circumferences (SI, metres). |
| **3. Custom** | `custom` | Preset **thigh**, **waist**, and **chest** measures; any value can be changed via CLI. |

Use `--no-image` on any command to skip PNG/GIF rendering (data export only).

**Interactive 3D viewer** (rotate/zoom with the mouse):

```bash
python examples.py custom --interactive
```

Drag to orbit the model, scroll to zoom, close the window when done. Add `--save-with-interactive` to also write PNGs.

---

### Option 1 — Baseline

Uses the `baseline` preset. No manual segment overrides.

**Defaults:** height `1.80` m, weight `120` kg, sex `male`.

```bash
python examples.py baseline
```

Customize the subject:

```bash
python examples.py baseline --height 1.75 --weight 80 --sex female
```

---

### Option 2 — Hip and waist segments modification

Uses the `shape` preset. Adjusts torso/hip shape via circumferences (metres, SI).

**Defaults:**

| Parameter | Default (m) |
|-----------|-------------|
| height | 1.80 |
| weight | 120 |
| sex | male |
| hip_circumference | 1.00 |
| waist_circumference | 0.88 |

```bash
python examples.py shape
```

Customize hip/waist (and subject baseline):

```bash
python examples.py shape \
  --height 1.80 \
  --weight 80 \
  --sex male \
  --param hip_circumference=1.02 \
  --param waist_circumference=0.90
```

---

### Option 3 — Custom

Uses the `custom` preset. You only need to set what you want to change; anything omitted is predicted from height, weight, and sex (except the three preset overrides below).

```bash
python examples.py custom
```

#### A. Subject baseline (CLI flags)

| Flag | Description | Preset default |
|------|-------------|----------------|
| `--height` | Height (m, SI) | `1.80` |
| `--weight` | Weight (kg) | `120` |
| `--sex` | `male` or `female` | `male` |

```bash
python examples.py custom --height 1.80 --weight 80 --sex male
```

#### B. Segment measures (`--param KEY=VALUE`)

All values below are in **metres** when using SI (`unit_measure: SI` in the preset). Pass any combination; repeat `--param` for each field.

**Segment lengths** (optional; no preset unless you pass `--param`):

| Parameter | Description |
|-----------|-------------|
| `head` | Head length |
| `upper_torso` | Upper torso length |
| `middle_torso` | Middle torso length |
| `lower_torso` | Lower torso length |
| `thigh` | Thigh length |
| `shank` | Shank length |
| `foot` | Foot length |
| `ankle` | Ankle segment length |
| `upperarm` | Upper arm length |
| `forearm` | Forearm length |
| `hand` | Hand length |
| `shoulderwaistlen` | Shoulder–waist length |
| `crotchheight` | Crotch height |

**Circumferences** (optional):

| Parameter | Description |
|-----------|-------------|
| `head_circumference` | Head circumference |
| `neck_base_circumference` | Neck base circumference |
| `neck_circumference` | Neck circumference |
| `shoulder_circumference` | Shoulder circumference |
| `chest_circumference` | Chest circumference |
| `waist_circumference` | Waist circumference |
| `hip_circumference` | Hip circumference |
| `buttock_circumference` | Buttock circumference |
| `thigh_circumference` | Thigh circumference |
| `lower_thigh_circumference` | Lower thigh circumference |
| `calf_circumference` | Calf circumference |
| `ankle_circumference` | Ankle circumference |
| `balloffoot_circumference` | Ball of foot circumference |
| `bicep_circumference` | Bicep circumference |
| `forearm_circumference` | Forearm circumference |
| `wrist_circumference` | Wrist circumference |

**Breadths and depths** (optional):

| Parameter | Description |
|-----------|-------------|
| `headbreadth` | Head breadth |
| `chestdepth` | Chest depth |
| `biacromialbreadth` | Biacromial breadth |
| `waistbreadth` | Waist breadth |
| `waistdepth` | Waist depth |
| `hipbreadth` | Hip breadth |
| `buttockdepth` | Buttock depth |
| `handbreadth` | Hand breadth |

**Example — preset overrides only:**

```bash
python examples.py custom \
  --height 1.80 \
  --weight 80 \
  --sex male \
  --param thigh=0.50 \
  --param waist_circumference=0.96 \
  --param chest_circumference=1.04
```

**Example — many optional measures** (add or remove `--param` lines as needed):

```bash
python examples.py custom \
  --height 1.80 \
  --weight 80 \
  --sex male \
  --param head=0.24 \
  --param upper_torso=0.50 \
  --param middle_torso=0.35 \
  --param lower_torso=0.25 \
  --param thigh=0.45 \
  --param shank=0.40 \
  --param foot=0.27 \
  --param ankle=0.08 \
  --param upperarm=0.25 \
  --param forearm=0.30 \
  --param hand=0.20 \
  --param shoulderwaistlen=0.50 \
  --param crotchheight=0.85 \
  --param head_circumference=0.58 \
  --param headbreadth=0.15 \
  --param chestdepth=0.25 \
  --param biacromialbreadth=0.40 \
  --param neck_base_circumference=0.40 \
  --param shoulder_circumference=1.10 \
  --param chest_circumference=1.00 \
  --param hip_circumference=0.95 \
  --param waist_circumference=0.85 \
  --param waistbreadth=0.30 \
  --param waistdepth=0.25 \
  --param hipbreadth=0.35 \
  --param buttockdepth=0.30 \
  --param thigh_circumference=0.55 \
  --param lower_thigh_circumference=0.50 \
  --param calf_circumference=0.40 \
  --param ankle_circumference=0.23 \
  --param balloffoot_circumference=0.22 \
  --param buttock_circumference=1.00 \
  --param bicep_circumference=0.32 \
  --param neck_circumference=0.40 \
  --param forearm_circumference=0.28 \
  --param wrist_circumference=0.18 \
  --param handbreadth=0.09
```

#### C. Run and output flags (CLI)

| Flag | Description | Default |
|------|-------------|---------|
| `--output-dir` | Run folder for all exports and images (timestamp prefixed) | `output/<YYYYMMDD_HHMMSS>_<mode>_<sex>_<weight>_<height>/` |
| `--no-timestamp` | Use `--output-dir` exactly as given (no suffix) | off |
| `--output-file` | Inertia export basename | `out.xlsx` (also writes `out.json`, `out.mat`, `out.pkl`) |
| `--output` | PNG filename prefix | `out` |
| `--view` | `front`, `side_view` (side view), or `both` | `both` |
| `--dpi` | PNG resolution | `150` |
| `--no-image` | Skip PNG/GIF; data export only | off |
| `--gif` | Write animated GIF | none |
| `--fps` | GIF frame rate | `10` |
| `--pose-csv` | Custom pose from CSV | none |
| `--pose-npy` | Custom pose from NumPy | none |
| `--frame` | Pose row index (CSV/npy) | `0` |

```bash
python examples.py custom --no-image
python examples.py custom --view front --output my_subject --output-dir ./output
python examples.py --help
```

---

## Outputs

Each run creates one output folder (timestamped by default so repeated runs do not overwrite). **All** artifacts go inside that folder:

- `output/<YYYYMMDD_HHMMSS>_<mode>_<sex>_<weight>_<height>/`
- example: `output/20260527_143052_custom_male_80kg_1p75m/`

Contents typically include:

- Data exports: `out.xlsx`, `out.json`, `out.mat`, `out.pkl` (override stem with `--output-file`)
- Images: `out_side_view.png`, `out_front_view.png` (prefix from `--output`, default `out`)

Use `--no-timestamp` if you need a fixed folder path. Use `--no-image` to skip image rendering.

## Custom model configurations
 
![Figure 3 model panel](docs/images/fig3_models.png)
 
Commands used to generate each model:
 
**M1** — male, 1.80 m, 80 kg
 
```bash
python examples.py baseline --height 1.80 --weight 80 --sex male
```
 
**M2** — male, 1.80 m, 130 kg
 
```bash
python examples.py baseline --height 1.80 --weight 130 --sex male
```
 
**M3** — male, 1.80 m, 130 kg, larger waist + smaller hip
 
```bash
python examples.py custom \
  --height 1.80 \
  --weight 130 \
  --sex male \
  --param waist_circumference=1.85 \
  --param hip_circumference=0.95
```
 
**M4** — male, 1.80 m, 130 kg, smaller waist + larger hip
 
```bash
python examples.py custom \
  --height 1.80 \
  --weight 130 \
  --sex male \
  --param waist_circumference=1.35 \
  --param hip_circumference=1.55
```
 
**F1** — female, 1.80 m, 80 kg
 
```bash
python examples.py baseline --height 1.80 --weight 80 --sex female
```
 
**F2** — female, 1.50 m, 50 kg
 
```bash
python examples.py baseline --height 1.50 --weight 50 --sex female
```
 
**F3** — female, 1.50 m, 50 kg, longer arms + longer legs
 
```bash
python examples.py custom \
  --height 1.50 \
  --weight 50 \
  --sex female \
  --param thigh=0.50 \
  --param shank=0.45 \
  --param upperarm=0.30 \
  --param forearm=0.25
```
 
**F4** — female, 1.50 m, 50 kg, shorter arms + shorter legs
 
```bash
python examples.py custom \
  --height 1.50 \
  --weight 50 \
  --sex female \
  --param thigh=0.30 \
  --param shank=0.25 \
  --param upperarm=0.20 \
  --param forearm=0.15
```
