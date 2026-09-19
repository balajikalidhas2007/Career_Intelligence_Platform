# Step 2: GitHub OAuth Login

- [x] 1. **Environment Setup**: Update `.env.example` and `config.py` (remove NextAuth, add JWT/GitHub secrets).
- [x] 2. **Dependencies**: Add `pyjwt` and `cryptography` to backend `pyproject.toml`.
- [x] 3. **Database Models**: Implement `User`, `AuthIdentity`, and `RefreshToken` SQLAlchemy models.
- [ ] 4. **Migrations**: Generate and apply Alembic migration for auth models. (Waiting for Docker DB to be up)
- [x] 5. **Security Utils**: Implement JWT creation/validation, Fernet encryption/decryption, and token hashing.
- [x] 6. **Auth Routes**: Implement `GET /auth/github`, `GET /auth/github/callback`, and `POST /auth/refresh`.
- [x] 7. **Auth Dependency**: Create `get_current_user` FastAPI dependency.
- [x] 8. **Frontend Integration**: Update login button to point to FastAPI, implement `/auth/callback` page, add auth context (Dashboard created).
- [ ] 9. **Verification**: Run tests, lint, and manual verification.
