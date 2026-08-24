# VoxShield Team Development & Contribution Guidelines

Welcome to the VoxShield project repository. This guide establishes team rules, Git workflows, branching conventions, and coding standards for our 2-person Smart India Hackathon development team.

---

## 👥 Team Roles & Scoping

To maintain clear domain separation and eliminate merge conflicts:

- **Developer 1 (Backend & AI Lead)**:
  - **Scope**: `backend/`, `docs/api-contract.md`
  - **Focus**: FastAPI routes, PyTorch anti-spoofing models, DSP feature extraction, Pydantic schemas, risk engine logic, backend test suite.
  
- **Developer 2 (Frontend & UX Lead)**:
  - **Scope**: `frontend/`
  - **Focus**: React UI components, Tailwind CSS styling, audio recording/uploading hooks, dashboard visualizers, Mock API service layer, API client integration.

---

## 🌿 Git Branching Strategy

Never push directly to `main` for feature work. All development must occur in feature branches.

### Core Branches
- `main`: Stable production-ready codebase.
- `develop`: Primary integration branch for upcoming releases.

### Feature Branch Naming Conventions
- `feature/backend-[feature-name]` (e.g. `feature/backend-risk-engine`)
- `feature/frontend-[feature-name]` (e.g. `feature/frontend-audio-recorder`)
- `feature/ai-[model-name]` (e.g. `feature/ai-anti-spoofing-model`)
- `feature/integration` (e.g. `feature/integration-mock-to-live`)

---

## 🚀 Workflow Step-by-Step

### 1. Create a New Feature Branch
```bash
git checkout develop
git pull origin develop
git checkout -b feature/backend-risk-engine
```

### 2. Make Small, Atomic Commits
Use descriptive commit messages following Conventional Commits format:
```bash
feat(backend): implement acoustic risk engine scoring logic
fix(frontend): adjust waveform canvas high DPI scaling
docs(api): update API contract response schema
```

### 3. Push and Open a Pull Request (PR)
```bash
git push origin feature/backend-risk-engine
```
Open a PR against `develop`. The other team member must review and approve before merging into `develop`.

---

## ⚠️ Security & Repository Hygiene Rules

1. **NEVER Commit Real Secrets or API Keys**:
   - Always use `.env.example` to document environment keys.
   - Local `.env` files are ignored by `.gitignore`.

2. **NEVER Commit Large Datasets or Pre-trained Model Weights**:
   - Do NOT commit `.pt`, `.pth`, `.onnx`, `.h5`, `.bin`, `.wav`, or `.flac` files to git.
   - Large model weights belong in external cloud storage or `backend/models/` locally (which is gitignored).

3. **Keep Codebases Decoupled**:
   - Backend development must NOT depend on frontend files.
   - Frontend development must NOT break when the backend is offline (always maintain `mockApi.ts`).

4. **Code Quality Standards**:
   - Python: Follow PEP8 standards (`black`, `flake8`, type hints).
   - TypeScript: Strict typing enabled; no implicit `any`.

---

## 🛠 Recommended Development Setup

### Terminal 1: Backend
```bash
cd backend
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```
