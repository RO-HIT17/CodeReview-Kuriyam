# Code Review Platform

## 📃 Description

An AI-powered code review automation platform that integrates with GitHub and Bitbucket. It automatically reviews pull requests (PRs), generates contextual suggestions via a finetuned CodeLlama model (hosted on Ollama), and posts inline comments.

**Core Capabilities:**

- Fetch PR diffs via webhook
- Generate line-level suggestions
- Post inline comments
- Collect user feedback via upvotes/downvotes
- Admin moderation dashboard
- Feedback-driven LoRA model retraining
- Automatically checks for related issues linked in the PR title, body, or commit messages

---
## 🧱 Tech Stack

### 🖥️ Frontend
**Framework**: Next.js  
- Renders the admin dashboard, authentication screens, and connected repository views.
- Displays PR installation info, review suggestions, and feedback logs.

### 🧪 Backend
**Framework**: FastAPI  
- Handles GitHub/Bitbucket webhooks, OAuth installs, feedback endpoints, PR diff parsing, and model communication.
- Secures admin APIs using JWT-based auth.

### 🧠 Model
**Serving**: Ollama  
**Base Model**: CodeLlama (LoRA-finetuned)  
- Finetuned on curated datasets of real PR diffs and expert reviews.
- Trained using datasets like `code_alpaca` and a custom internal dataset (`cyber_native`) 
- Accepts structured prompts (diff + filename + language + chunk context) and returns JSON suggestions.

> 🔗 Dataset Links :  
> - [Code Alpaca Dataset](https://huggingface.co/datasets/HuggingFaceH4/CodeAlpaca_20K)  
> - [Cyber Native Review Set](https://huggingface.co/datasets/CyberNative/Code_Vulnerability_Security_DPO)

### 🗃️ Data Storage
**Engine**: SQLite  
- Built-in and used via FastAPI's ORM layer (`SQLAlchemy` / `pydantic` models).
- Used for login credentials, GitHub installations, and Bitbucket workspace tracking.

**Feedback Storage**:  
- **Not stored in the DB**.  
- All user feedback votes (👍/👎) are logged to `static/feedback.json` for moderation and model retraining.


---

## 🛠️ System Workflows
## 🔁 Workflows

### 3.1 🛠️ PR Workflow (Automated Code Review + Issue Mapping)

1. **PR Created or Updated**  
   - GitHub or Bitbucket sends a webhook to `/github/webhook` or `/bitbucket/webhook`.

2. **Backend Fetches PR Diff + Metadata**  
   - Extracts file paths, changed lines, filenames, and language hints.

3. **Linked Issue Detection**  
   - Scans the PR title, description, and commit messages for issue references (e.g., `Fixes #42`).
   - If found, issue details are fetched and included in the model prompt.

4. **Send to Model via Ollama**  
   - A structured prompt (diff, file info, and issue context) is sent to the finetuned CodeLlama model.

5. **Receive Suggestions from Model**  
   - The model returns a JSON object with:
     - Suggestion text
     - Target file and line number
     - Suggestion type (bug, style, improvement, etc.)

6. **Inline Comments Are Posted**  
   - Suggestions are posted as inline comments on the PR.

7. **General Comment (Optional)**  
   - A general comment is posted summarizing whether the PR appears to address any linked issue(s).

8. **Vote Buttons Included**  
   - Each suggestion includes 👍 / 👎 buttons for user feedback.

### 3.2 👩‍💻 User Workflow

#### 🧾 Authentication & Installation

1. **Sign Up / Login**  
   - Users register and log in through the frontend.

2. **Connect with GitHub or Bitbucket**  
   - OAuth flow allows users to link their account.

3. **Select Repositories or Workspaces**  
   - Users choose which repositories or workspaces to install the app on.

#### 📝 PR Interaction

- When a PR is created or updated:
  - The AI model automatically reviews it.
  - Inline review comments appear with suggestions.
  - Users can vote on each suggestion using 👍 or 👎 buttons.

### 3.3 🛡️ Admin Workflow

#### 🔐 Login

- Admin logs in via `/auth/login` (JWT-protected).
- Currently supports a single user via hardcoded credentials.

#### 🧾 Feedback Moderation

- `/feedback-list`: View all collected feedback entries.
- `/approve-feedback`: Mark a suggestion as useful and accurate.
- `/reject-feedback`: Mark low-quality suggestions for exclusion.

Approved feedback is used later during model finetuning.

### 3.4 🧠 Model Finetuning Workflow

> This is the internal pipeline used to train and update the CodeLlama model that powers the review system.

1. **Datasets Used**  
   - `code_alpaca`: General-purpose instruction dataset  
   - `cyber_native`: Custom PR diff + comment dataset  
   - Augmented over time with real feedback from platform users

2. **Finetuning Frameworks**  
   - Used `Unsloth`, `PEFT`, and `LoRA` for efficient, low-resource fine-tuning  
   - Training was done on diff chunks → comment pairs

3. **Model Packaging**  
   - After training, the LoRA adapters were merged with the base CodeLlama model using `ollama create`  
   - Final model is a self-contained `.ollama` model ready to be served via Ollama

4. **Deployment & Access**  
   - Model is hosted locally via Ollama for fast inference  
   - Also available on:
     - Hugging Face: [https://huggingface.co/rohits1711](https://huggingface.co/rohits1711)  
     - Ollama profile: [https://ollama.com/rohits](https://ollama.com/rohits)

---

## ⚙️ 4. Local Setup & Testing

### 4.1 🧩 Prerequisites

- **Node.js** (for the Next.js frontend)
- **Python 3.10+** (for the FastAPI backend)
- **Ollama** (for serving the finetuned CodeLlama model)
- **Ngrok** (for public webhook URL during testing)

---

### 4.2 🖥️ Frontend Setup (Next.js)

```bash
cd client
npm install
npm run dev
````

* Frontend runs on: `http://localhost:3000`

Update `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### 4.3 ⚙️ Backend Setup (FastAPI)

```bash
cd server
pip install -r requirements.txt
uvicorn main:app --port 8000
```

* Backend runs on: `http://localhost:8000`

✅ FastAPI serves:

* GitHub and Bitbucket webhooks
* PR diff processing
* Feedback handling
* Auth routes
* Admin panel APIs

---

### 4.4 🤖 Model Setup (Ollama)

1. **Install Ollama**:
   [https://ollama.com/download](https://ollama.com/download)

2. **Run the model**:

```bash
ollama run codellama:7b
```

* Model should be available in your local Ollama registry.
* Ollama listens at `http://localhost:11434` by default.

---

### 4.5 🔐 Environment Variables

Backend `.env` example:

```env
GITHUB_APP_ID=1397680
GITHUB_PRIVATE_KEY_PATH=kuriyamcodereview.2025-06-12.private-key.pem
WEBHOOK_SECRET=test-string
NGROK_URL=https://xxxx.ngrok-free.app
BITBUCKET_KEY=code-review-bot
```

> ⚠️ Only `NGROK_URL` changes frequently. Others remain static.

Frontend `.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

### 4.6 🧪 Local Testing Flow

* Use **Ngrok** to expose the backend for webhook testing:

```bash
ngrok http 8000
```

* Set the Ngrok URL in:

  * `.env` (backend)
  * GitHub App Webhook URL
  * Bitbucket App descriptor `baseUrl`

#### Test Workflow:

1. Install the GitHub or Bitbucket App to a test repo.
2. Create a PR → webhook fires to FastAPI.
3. Backend fetches the PR diff and calls the model.
4. Model generates suggestions → inline comments are posted to the PR.
5. General issue-related comment is posted if applicable.
6. Users vote 👍 or 👎 on comments → votes are saved in `static/feedback.json`.

---

# 🚀 Production Setup & Deployment Guide

## 🔧 1. Component Responsibilities

### 📦 Frontend (Next.js)

- Deploy the frontend to any production-ready host.
- Ensure `.env.local` is configured with the backend's production URL:

```env
NEXT_PUBLIC_API_URL=https://your-backend.com
````

---

### 🛠 Backend (FastAPI)

* Deploy the FastAPI app using `uvicorn main:app --port 8000`.
* Environment variables must be securely defined:

```env
GITHUB_APP_ID=...
GITHUB_PRIVATE_KEY_PATH=...
WEBHOOK_SECRET=...
BITBUCKET_KEY=code-review-bot
NGROK_URL=https://your-backend.com
```

* SQLite is used by default (via FastAPI ORM) for login and installation tracking.
* Feedback is **not stored in the database**, but in `static/feedback.json`.

> ✅ Update `MODEL_URL` in the config file if you change the model source or endpoint.

>  MODEL_URL=https://your-model-server.com  # Change this in core/config.py to match where model is hosted 


---

### 📂 GitHub App Configuration

1. Go to **GitHub Developer Settings → GitHub Apps**

2. Create a new app with:

   * **Webhook URL**:
     `https://your-backend.com/github/webhook`

   * **OAuth Callback URL**:
     `https://your-frontend.com/dashboard`

   * **Permissions**:

     * Pull Requests: Read & Write
     * Issues: Read
     * Contents: Read-only
     * Metadata: Read

   * **Events**:

     * `pull_request`
     * `push`
     * `issue_comment`
     * `installation`

3. Generate a private key and configure these values in the backend:

```env
GITHUB_APP_ID=...
GITHUB_PRIVATE_KEY_PATH=...
WEBHOOK_SECRET=...
```

---

### 🔹 Bitbucket Connect App Configuration

1. Register your app at:
   [https://bitbucket.org/account/settings/apps](https://bitbucket.org/account/settings/apps)

2. Set the **App Descriptor URL**:

```
https://your-backend.com/bitbucket/atlassian-connect.json
```

3. In the descriptor JSON, update:

```json
"baseUrl": "https://your-backend.com"
```

4. Required permissions:

* Repositories: Read
* Pull Requests: Write
* Webhooks: Read & Write
* Issues: Read

> OAuth handling is automated during installation via Bitbucket’s Connect framework.

---

### 🧠 AI Model Hosting (Ollama)

* The platform uses a **LoRA-finetuned CodeLlama** model trained using:

  * `Unsloth`, `LoRA`, and `PEFT`
  * Datasets: `code_alpaca`, `cyber_native`, and curated platform feedback

* After training, adapters were merged using `ollama create`.

* The model is served via **Ollama** and accessed at the URL configured in `MODEL_URL`.

#### 🔁 Flexibility

* You may change the model by replacing it in your Ollama environment and updating:

```env
MODEL_URL=https://your-model-server.com
```

* By default, the backend accesses the model on all origins (`localhost` or remote). 
---

## ✅ Final Production Checklist

| Task                     | Description                                                 |
| ------------------------ | ----------------------------------------------------------- |
| Frontend `.env.local`    | Set `NEXT_PUBLIC_API_URL=https://your-backend.com`          |
| Backend `.env`           | Set GitHub/Bitbucket secrets and `MODEL_URL`                |
| GitHub Webhook           | Set to `/github/webhook` on deployed backend                |
| GitHub OAuth Callback    | Set to `/dashboard` on frontend                             |
| GitHub Private Key       | Generated and stored securely on server                     |
| Bitbucket Descriptor URL | Hosted at `/bitbucket/atlassian-connect.json`               |
| Descriptor `baseUrl`     | Must point to production backend                            |
| Feedback Storage         | Ensure write access to `static/feedback.json`               |
| Model Configuration      | Update `MODEL_URL` and ensure model is hosted/available     |
| Model Source             | Optional: change base or finetuned model on Ollama instance |
| Security Settings        | Enable HTTPS and restrict CORS to frontend domain           |

---
