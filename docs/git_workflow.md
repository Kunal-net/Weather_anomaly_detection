# 🤝 Team Git Collaboration Guide — Weather Anomaly Detection System

A step-by-step workflow guide for our 5-member Smart India Hackathon (SIH) team to build, collaborate, and avoid merge conflicts using Git and GitHub.

---

## 👥 Member Role & Branch Assignment

To work simultaneously without stepping on each other's toes, each member owns a specific directory and branch:

| Member | Focus Area | Primary Directory | Dedicated Git Branch |
| :--- | :--- | :--- | :--- |
| **Member 1** | ML/AI Lead | `ml/` | `feature/ml-model` |
| **Member 2** | Data Engineer | `data/`, `ml/preprocessing.py` | `feature/data-engineering` |
| **Member 3** | Backend Developer | `backend/` | `feature/fastapi-backend` |
| **Member 4** | Frontend Developer | `frontend/` | `feature/react-dashboard` |
| **Member 5** | Integration & SIH Lead | `docs/`, `tests/` | `feature/integration-docs` |

---

## 📌 Phase 1: One-Time Repository Setup (Team Lead)

### 1. Push Code to GitHub
The repository is already committed locally. Now, create a new repo on GitHub and push:

```bash
# 1. Add your remote repository URL (replace with your repo link)
git remote add origin https://github.com/<your-username>/<your-repo-name>.git

# 2. Push main branch
git branch -M main
git push -u origin main
```

### 2. Add Team Members as Collaborators
1. Go to your GitHub repo $\to$ **Settings** $\to$ **Collaborators**.
2. Click **Add people** and enter each teammate's GitHub username or email.
3. Teammates must accept the email invitation to get push access.

---

## 💻 Phase 2: First-Time Setup for Every Teammate

Each team member runs these steps on their own laptop:

```bash
# 1. Clone the repository
git clone https://github.com/<team-lead-username>/<repo-name>.git
cd <repo-name>

# 2. Set up Python virtual environment
python3 -m venv venv

# Activate on Mac/Linux:
source venv/bin/activate
# Activate on Windows:
# .\venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Check that your git identity is configured
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 🔄 Phase 3: Daily Working Routine (The Golden Loop)

Follow these 6 steps **every single time** you work on the project.

### Step 1: Always Start by Pulling the Latest `main`
Before writing any code, ensure your local `main` is up to date:

```bash
git checkout main
git pull origin main
```

### Step 2: Switch to Your Feature Branch
Create or switch to your assigned feature branch:

```bash
# If creating for the first time:
git checkout -b feature/<your-assigned-branch>

# If switching to an existing branch:
git checkout feature/<your-assigned-branch>
# Update your branch with latest main changes:
git merge main
```

### Step 3: Write, Test & Verify Code
Do your work in your assigned directory (e.g. `ml/` for Member 1, `backend/` for Member 3).  
Always test your changes locally before committing!

### Step 4: Check Status and Commit
```bash
# Check what files you modified
git status

# Stage only your files
git add ml/             # or backend/, frontend/, etc.

# Commit with a clear, descriptive message
git commit -m "feat(ml): implement historical baseline calculation"
```

> **Commit Message Convention:**
> - `feat(...)`: A new feature (e.g. `feat(backend): add /predict endpoint`)
> - `fix(...)`: A bug fix (e.g. `fix(data): handle negative humidity sensor readings`)
> - `docs(...)`: Documentation changes (e.g. `docs(sih): add demo presentation script`)
> - `test(...)`: Adding tests (e.g. `test(ml): add z-score unit test`)

### Step 5: Push Your Branch to GitHub
```bash
# Push your branch (first time):
git push -u origin feature/<your-assigned-branch>

# On subsequent pushes:
git push
```

### Step 6: Create a Pull Request (PR) on GitHub
1. Go to your repository on GitHub.
2. You will see a button: **"Compare & pull request"**. Click it.
3. Set base branch as `main` and compare branch as your feature branch.
4. Add a quick bullet list of what you built.
5. Request a review from at least one teammate (e.g. Member 5 or Team Lead).
6. Once approved, click **Merge pull request** $\to$ **Confirm merge**.

---

## 🛡️ Golden Rules to Prevent Merge Conflicts

1. **Strict Directory Ownership**:
   - Do not edit files outside your assigned module unless coordinated in advance.
   - If Member 3 needs a function from Member 1, Member 1 should write and merge it first.
2. **Never Commit Directly to `main`**:
   - `main` should always be stable and runnable for demos.
3. **Pull Before You Push**:
   - Always run `git checkout main && git pull` before starting new tasks.
4. **Never Force Push (`git push --force`)**:
   - Force pushing can erase your teammates' work. Never use `--force` on shared branches.
5. **Never Commit Large Dumps or Environments**:
   - Virtual environments (`venv/`) and frontend (`node_modules/`) are ignored by `.gitignore`. Never use `git add -f` to override them.

---

## 🆘 Emergency Cheat Sheet: Resolving Merge Conflicts

If Git says `CONFLICT (content): Merge conflict in ...`:

1. Open the conflicting file in VS Code / Cursor / IDE.
2. Look for conflict markers:
   ```text
   <<<<<<< HEAD (Current Change - your code)
   your changes here
   =======
   teammate's changes from main
   >>>>>>> main (Incoming Change)
   ```
3. Choose **Accept Both Changes** or manually edit the file to combine both cleanly.
4. Delete the `<<<<<<<`, `=======`, and `>>>>>>>` marker lines.
5. Stage and finish the merge:
   ```bash
   git add <conflicted-file>
   git commit -m "fix: resolve merge conflict with main"
   git push
   ```
