# 👥 Team Workflow Guide — Daily Operations

Welcome to the team! This quick reference covers everything you need to know to work on the **Weather Anomaly Detection System** alongside your teammates without merge conflicts.

---

## 🧭 Step 0: Find Your Role & Branch

| Member | Focus | Your Folder | Your Branch Name |
| :--- | :--- | :--- | :--- |
| **Member 1** | Machine Learning & Anomaly Engine | `ml/` | `feature/ml-model` |
| **Member 2** | Data Engineering & Preprocessing | `data/`, `ml/preprocessing.py` | `feature/data-engineering` |
| **Member 3** | FastAPI Backend & REST Endpoints | `backend/` | `feature/fastapi-backend` |
| **Member 4** | React Dashboard & Maps | `frontend/` | `feature/react-dashboard` |
| **Member 5** | Integration, Testing & Docs | `docs/`, `tests/` | `feature/integration-docs` |

---

## ⚡ Daily Working Loop (Copy-Paste Commands)

### 1. Before You Start Coding
Always get the latest code from `main`:
```bash
git checkout main
git pull origin main
```

### 2. Move to Your Feature Branch
```bash
# If working on an existing branch:
git checkout feature/<your-branch-name>
git merge main   # Bring in any new updates from main

# If creating a branch for the first time:
git checkout -b feature/<your-branch-name>
```

### 3. Work Inside Your Designated Folder
- **Member 1**: Work in `ml/`
- **Member 2**: Work in `data/` and `ml/preprocessing.py`
- **Member 3**: Work in `backend/`
- **Member 4**: Work in `frontend/`
- **Member 5**: Work in `docs/` and `tests/`

### 4. Stage & Commit Your Work
```bash
# Check what changed
git status

# Stage only your folder
git add ml/             # (or backend/, frontend/, etc.)

# Commit with a clear message
git commit -m "feat(ml): add seasonal baseline calculator"
```

### 5. Push to GitHub
```bash
# First push of a new branch:
git push -u origin feature/<your-branch-name>

# Subsequent pushes:
git push
```

### 6. Create a Pull Request (PR) on GitHub
1. Open GitHub $\to$ Click **"Compare & pull request"**.
2. Base: `main` $\leftarrow$ Compare: `feature/<your-branch-name>`.
3. Check the PR template boxes.
4. GitHub Actions CI will automatically test your branch.
5. Have a teammate review and click **Merge pull request**!

---

## ⚠️ Important Rules for Everyone

1. **NEVER push directly to `main`**: All changes must go through a Pull Request (PR).
2. **Never commit secrets or virtual environments**: `.env`, `venv/`, and `node_modules/` are strictly ignored by `.gitignore`.
3. **Core Domain Rule**: NEVER use static thresholding (e.g. `temp > 35`). All anomalies must be measured as deviations from historical location & seasonal baselines.
4. **Need help or hit a merge conflict?** Check the emergency guide in [`docs/git_workflow.md`](docs/git_workflow.md).
