<!-- Generated/updated by AI assistant. Please review and iterate. -->
# Copilot / AI assistant instructions — Sarah repo

This file gives focused, actionable guidance to AI coding agents working on the Sarah repository. Keep responses short, reference concrete files, and prefer minimal, testable changes.

High-level architecture (big picture)
- The project is a multi-service AI companion named "Sarah" split into logical services under top-level folders:
  - `api_gateway/` — nginx-based gateway (see `nginx.conf` and `Dockerfile`), entry point for HTTP/ws.
  - `character_manager/` — handles character/persona lifecycle (see `main.py`, `persona_generator.py`, `models.py`).
  - `memory_subsystem/` — extracting and storing memory vectors (see `memory_extractor.py`, `milvus_manager.py`).
  - `persona_engine/` and `multimodal_engine/` — generators and trainers for persona and multimodal functionality (see their `main.py`, `prompt_manager.py`, `lora_trainer.py`).
  - `frontend/` — Next.js React app under `frontend/src/app` (character creation, chat UI). Uses TypeScript and Tailwind (see `tailwind.config.ts`, `next.config.js`).

Key files to inspect for context and examples
- Service entrypoints: `*/main.py` (each service has one). These show CLI/startup patterns and config usage.
- Config: `*/config.py` files provide env-driven configs — prefer env var usage consistent with these modules.
- DB/storage: `character_manager/database.py` and `memory_subsystem/database.py` show how persistent state is accessed.
- Prompts & persona: `character_manager/persona_generator.py` and `persona_engine/prompt_manager.py` show prompt structure and persona assembly.
- Frontend patterns: `frontend/src/app/character/*` and `frontend/src/components/*` show how server APIs are consumed and data shapes for characters and chats.

Project-specific conventions and patterns
- Small services are lightweight and executable via `main.py` — prefer adding features as small modules imported by `main.py`.
- Configs are centralized per-service in `config.py` and typically built from environment variables; avoid hardcoding secrets.
- Database access is synchronous in small modules (plain Python files). If adding async code, ensure the service's run loop supports it.
- Messaging between services occurs via REST or via vectors in the memory subsystem — inspect `memory_extractor.py` and `milvus_manager.py` for vector storage patterns.

Build, run, and developer workflows
- Local multi-service run: open `sarah-ai-companion/docker-compose.yml` (top-level compose) — this is the canonical integration flow for local end-to-end testing.
- To run a single service locally for quick dev: run `python main.py` inside the service folder after activating a virtualenv and installing `requirements.txt` for that service.
- Frontend dev: `frontend/package.json` contains npm scripts. Use `npm install` then `npm run dev` inside `frontend` for hot reload.

Practical run/debug notes (merged from service READMEs)
- Common per-service dev command (run from the service folder):
  - Install deps: `pip install -r requirements.txt`
  - Start server: `uvicorn main:app --host 0.0.0.0 --port 8000 --reload` (many services use port 8000 by default)
- Docker Compose: run just one service for faster iteration:
  - `docker-compose up persona_engine` or `docker-compose up multimodal_engine`
  - Start the full stack: `docker-compose up -d`
- Frontend quick start (from `frontend/`):
  - `npm install`
  - `cp .env.local.example .env.local` then edit
  - `npm run dev` → available at http://localhost:3000

Key env vars and heavy deps to be aware of
- Datastore (shared): `POSTGRES_HOST/PORT/USER/PASSWORD/DB` — see `character_manager/README.md` and `memory_subsystem/README.md` for names and examples.
- Milvus: `MILVUS_HOST`, `MILVUS_PORT` (used by `memory_subsystem`). Local quick start: `docker-compose -f milvus-docker-compose.yml up -d` as noted in the memory README.
- Ollama + model (persona engine): `OLLAMA_BASE_URL`, `OLLAMA_MODEL`, `OLLAMA_TIMEOUT`. Dev steps in `persona_engine/README.md` include `ollama serve` and `ollama pull <model>`.
- FLUX.1 (multimodal): `FLUX_MODEL_PATH`, `DEVICE`, `USE_FP16` and `ELEVENLABS_API_KEY` for TTS. FLUX requires significant VRAM; the multimodal README lists recommended resources.
- Frontend envs: `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_WS_URL` (see `frontend/README.md`); set these to the API Gateway (http://localhost:8080).

Non-obvious integration points / gotchas
- WebSockets go through the API Gateway. If chat WS fails, check `api_gateway/nginx.conf` (upgrade headers, timeouts) and `persona_engine` WS settings (`WS_PING_INTERVAL`, `WS_PING_TIMEOUT`).
- Memory pipeline: `persona_engine` publishes conversation turns to Redis; workers in `memory_subsystem` extract facts and push embeddings to Milvus. Check `memory_subsystem/memory_extractor.py` and `milvus_manager.py` for exact formats.
- LoRA training: `character_manager` will trigger `multimodal_engine` `/train-lora` when 5+ images are uploaded. See `character_manager/README.md` for the multipart form fields and `multimodal_engine/README.md` for training requirements.


Examples and data shapes
- Character creation API -> frontend expects a character object with fields defined in `character_manager/models.py`. Use this file as canonical shape when adding fields.
- Memory vectors: `memory_subsystem/models.py` defines stored vector metadata — when adding retrieval filters, keep same keys to avoid index splits.

Integration points and external dependencies
- Milvus (or similar vector DB) is used by `memory_subsystem/milvus_manager.py`. Tests/features that touch vector search may require a running vector DB.
- External model/training code lives in `multimodal_engine/` and `persona_engine/` — heavy tasks may assume GPU resources; keep changes non-blocking for CI.

Editing guidance for AI agents (practical rules)
- Minimal, testable changes: change one service at a time. Add a small unit or smoke test when modifying behavior that affects data shapes.
- When changing APIs, update the corresponding frontend file in `frontend/src` and `character_manager/models.py` simultaneously.
- Preserve `config.py` usage: add new env vars there and read them in `main.py` rather than sprinkling os.environ calls across modules.
- Follow naming patterns: files are snake_case, classes PascalCase. Use the existing style in nearby files.

Examples to cite in commits
- "Update persona payload to include `background` — update `character_manager/models.py` and `frontend/src/app/character/create/page.tsx` to match."
- "Add lightweight smoke test for memory retrieval: new test referencing `memory_subsystem/memory_extractor.py`."

When you can't run services locally
- If a vector DB or GPU-backed model isn't available, add mocks that follow `*/models.py` shapes; keep the mock in a `tests/fixtures` or `dev_mocks/` folder and document usage.

Where to look for more context
- Per-service READMEs (each folder has a `README.md`) — start there for service-specific commands and expectations.
- Top-level `README.md` for overall intent and orchestration pointers.

If you change this file
- Keep it short. Include concrete file references. Prefer explicit commands that developers can run (docker-compose, python main.py, npm run dev).

Questions or unclear areas
- If anything here is unclear, point to the file you inspected and suggest a short, concrete replacement sentence.

-- end of instructions --
