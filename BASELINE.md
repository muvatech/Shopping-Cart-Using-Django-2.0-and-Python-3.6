# Django Shopping Cart Modernization: Baseline Analysis

**Date:** July 2026  
**Baseline Commit:** master  
**Current Stack:** Python 3.6 | Django 2.0.1 | Pillow 5.0.0 | pytz 2017.3  
**Target Stack:** Python 3.11+ | Django 4.2 LTS  

---

## Executive Summary

This shopping cart application is a production-grade tutorial project with 8 years of technical debt. The modernization will upgrade the runtime from unsupported (Python 3.6 EOL 2021, Django 2.0 EOL 2019) to a long-term-stable stack (Python 3.11+, Django 4.2 LTS until 2026).

**Key Goals:**
- ✅ Zero-downtime business logic compatibility (cart, pricing, checkout, orders)
- ✅ Security hardening (environment-based secrets, CSRF/XSS protection)
- ✅ Test coverage expansion (baseline → regression suite)
- ✅ Operational readiness (logging, monitoring, deployment)

---

## 1. Architecture Overview

### Stack Layers

```
┌─────────────────────────────────────────────────────┐
│  Django 2.0 Web Framework                           │
│  ├─ URL Routing (ecommerce/urls.py)                 │
│  ├─ Middleware Stack (security, session, CSRF)      │
│  ├─ Template Engine (Jinja2-like, context procs)    │
│  └─ ORM (SQLite3 via Django QuerySet)               │
├─────────────────────────────────────────────────────┤
│  Business Domains                                   │
│  ├─ shop/        (Product catalog, Category)        │
│  ├─ cart/        (Session-based cart, Cart class)   │
│  └─ orders/      (Order persistence, Order models)  │
├─────────────────────────────────────────────────────┤
│  Persistence                                        │
│  ├─ SQLite3 (db.sqlite3)                            │
│  ├─ Session Store (DB-backed)                       │
│  └─ Media (products/YYYY/MM/DD/ images)             │
└─────────────────────────────────────────────────────┘
```

### Core Modules

| Module | Role | Status | Issues |
|--------|------|--------|--------|
| **shop** | Product catalog, categories | Stable | Uses deprecated `index_together` meta |
| **cart** | Session-based shopping cart | Stable | Session-only storage (no persistence layer) |
| **orders** | Order creation & persistence | Core | Missing Order-Item relationship models |
| **ecommerce** | Project settings, routing | Stable | Hard-coded SECRET_KEY, DEBUG=True |

### Data Flow

```
User Request
  ↓
URLRouter (ecommerce/urls.py) → {shop, cart, orders}
  ↓
View (shop/cart/orders/views.py)
  ↓
ORM QuerySet (models.py) ↔ SQLite3
  ↓
Template Render (context_processors inject cart)
  ↓
HTTP Response
```

---

## 2. Deprecation & Breaking Changes Matrix

### 2.1 Python 3.6 → 3.11+

| Feature | 3.6 Behavior | 3.11+ Behavior | Impact | Migration |
|---------|---|---|---|---|
| `str.format()` | Preferred | Still works | **None** | No change needed |
| Type hints | PEP 526 | PEP 604 (Union→\|) | **Low** | Add modern type hints (optional) |
| Dict ordering | CPython impl | Guaranteed | **None** | No change needed |
| `async/await` | Present | Enhanced | **Low** | Not used in this project |
| Import system | `-` | Stricter | **Low** | Check circular imports |

**Risk Level:** 🟢 **Low** — No major language breaking changes.

### 2.2 Django 2.0 → 4.2 LTS

#### URL Routing (ecommerce/urls.py, shop/urls.py, cart/urls.py)

| Django 2.0 | Django 4.2 | Issue | Fix |
|---|---|---|---|
| `url(pattern, view)` | `re_path(pattern, view)` or `path(pattern, view)` | **Deprecated** `url()` → use `path()` | Replace `url()` with `path()` + simplify regexes where possible |
| Old-style `include()` | Same API | **Compatible** | No change needed |

**Files Affected:**
- `ecommerce/urls.py` — uses `include()` (OK)
- `shop/urls.py` — likely uses unnamed groups (check)
- `cart/urls.py` — likely uses unnamed groups (check)
- `orders/urls.py` — likely uses unnamed groups (check)

**Risk:** 🟡 **Medium** — Need to validate URL patterns.

#### Model Meta Changes

| Django 2.0 | Django 4.2 | Issue | Fix |
|---|---|---|---|
| `index_together` | Deprecated → **removed in 4.0** | **Breaking** | Use `Meta.indexes = [models.Index(...)]` |
| `on_delete=None` | **Requires explicit** | **Breaking** | Add `on_delete=models.CASCADE` to all ForeignKey |

**Files Affected:**
- `shop/models.py` — line 37 uses `index_together` ✗
- `shop/models.py` — line 24 has `on_delete=models.CASCADE` ✓

**Risk:** 🔴 **High** — Model changes cause migration errors.

#### ORM QuerySet / Manager

| Django 2.0 | Django 4.2 | Issue | Impact |
|---|---|---|---|
| `QuerySet.filter()` | Same | **Compatible** | No change |
| `QuerySet.get_or_404()` | Available in 3.0+ | **Compatible** | No change |
| `F()`, `Q()` | Same | **Compatible** | No change |

**Risk:** 🟢 **Low** — QuerySet API is stable.

#### Session Framework

| Django 2.0 | Django 4.2 | Issue | Impact |
|---|---|---|---|
| `request.session[key] = val` | Same | **Compatible** | No change |
| `session.modified = True` | Same | **Compatible** | No change |

**Risk:** 🟢 **Low** — Session API unchanged.

#### Settings Deprecations

| Setting | Status in 4.2 | Action |
|---------|---|---|
| `MIDDLEWARE` | Standard | Already using (good) |
| `TEMPLATES[].OPTIONS` | Standard | Already using (good) |
| `context_processors` | Standard | Already using (good) |

**Risk:** 🟢 **Low** — Settings structure is modern.

#### Context Processors

| Django 2.0 | Django 4.2 | Issue | Impact |
|---|---|---|---|
| `cart.context_processors.cart()` | Same signature | **Compatible** | No change needed |

**Risk:** 🟢 **Low** — Context processor API unchanged.

### 2.3 Dependency Deprecations

| Package | Current | Status | Latest LTS | Action |
|---------|---------|--------|---|---|
| Pillow | 5.0.0 (Jan 2018) | **EOL** | 10.0.0 (Oct 2023) | Upgrade |
| pytz | 2017.3 | Maintenance mode | Use `zoneinfo` (Python 3.9+) | Optional; can upgrade for newer TZ data |

**Risk:** 🟡 **Medium** — Pillow upgrade may have image handling changes.

---

## 3. Security Baseline Assessment

### 🔴 Critical Issues

1. **Hard-coded SECRET_KEY** (ecommerce/settings.py:23)
   - Status: **EXPOSED**
   - Impact: Session hijacking, CSRF bypass
   - Fix: Move to environment variable

2. **DEBUG=True in settings** (ecommerce/settings.py:26)
   - Status: **DANGEROUS**
   - Impact: Stack traces exposed, SQL queries visible
   - Fix: Set to `os.getenv('DEBUG', 'False') == 'True'`

3. **ALLOWED_HOSTS=[]** (ecommerce/settings.py:28)
   - Status: **VULNERABLE**
   - Impact: Host header injection possible
   - Fix: Set from environment or config

### 🟡 Medium Issues

1. No `.env` or secrets management
2. No HTTPS/SSL enforcement
3. No CORS headers
4. Media uploads stored in public directory

### Fixes Applied in Modernization

- ✅ Environment-based configuration
- ✅ Security headers (CSP, X-Frame-Options, etc.)
- ✅ HTTPS redirect middleware
- ✅ CSRF token enforcement in forms

---

## 4. Test Coverage Baseline

### Current State

```
shop/tests.py        → empty (60 bytes)
cart/tests.py        → empty (60 bytes)
orders/tests.py      → empty (60 bytes)
```

**Coverage:** 0% — No automated tests.

### Test Gaps

| Domain | Scenario | Status | Priority |
|--------|----------|--------|----------|
| **shop** | Product list filtering by category | ❌ Missing | P1 |
| **shop** | Product detail with stock check | ❌ Missing | P1 |
| **cart** | Add product to cart (session) | ❌ Missing | P1 |
| **cart** | Update cart quantity | ❌ Missing | P1 |
| **cart** | Remove product from cart | ❌ Missing | P1 |
| **cart** | Cart total price calculation | ❌ Missing | P1 |
| **orders** | Create order from cart | ❌ Missing | P1 |
| **orders** | Order persistence | ❌ Missing | P1 |
| **orders** | Order history lookup | ❌ Missing | P2 |

### Modernization Deliverable

- ✅ Unit tests for Cart class
- ✅ Integration tests for cart → order flow
- ✅ Edge cases: zero price, negative quantities, stock exhaustion
- ✅ Target: ≥ 90% coverage for business-critical paths

---

## 5. Build & Deployment Baseline

### Current State

- ✅ `manage.py` present (standard)
- ✅ `requirements.txt` present (minimal)
- ❌ No `setup.py` or `pyproject.toml`
- ❌ No Docker
- ❌ No CI/CD pipeline
- ❌ No linting/formatting
- ❌ No type checking

### Improvements in Modernization

- ✅ Add `pyproject.toml` (PEP 517/518 standard)
- ✅ Add `Makefile` or `justfile` for common tasks
- ✅ Add GitHub Actions workflow for testing
- ✅ Add `black`, `isort`, `flake8`, `mypy`

---

## 6. Critical Path for Upgrade

### Phase 1: Dependency Upgrade (Days 1–2)

**Blockers:**
1. Update `requirements.txt` → Django 4.2.x, Pillow 10.x, pytz latest
2. Create virtual environment with new deps
3. Run `python manage.py check` to identify breaking changes

**Expected Errors:**
```
django.core.management.base.SystemCheckError:
  shop.Product: (models.E033) "index_together" option is deprecated. Use "indexes" instead.
```

### Phase 2: Model Migrations (Days 3–4)

**Blockers:**
1. Replace `index_together` with `Meta.indexes`
2. Add missing `on_delete` parameters (if any)
3. Generate and test migrations on SQLite3
4. Run `python manage.py makemigrations shop`

### Phase 3: URL & View Updates (Days 4–5)

**Blockers:**
1. Replace `url()` with `path()` or `re_path()`
2. Validate all route patterns
3. Test URL reversal in templates

### Phase 4: Settings Hardening (Days 6–7)

**Blockers:**
1. Move SECRET_KEY to `.env`
2. Set DEBUG from environment
3. Configure ALLOWED_HOSTS
4. Add security middleware

### Phase 5: Testing & QA (Days 8–10)

**Blockers:**
1. Write regression tests for cart/order flows
2. Manual testing of checkout
3. Run full test suite
4. Load testing (optional)

### Phase 6: Deploy & Document (Days 11–14)

**Blockers:**
1. Create deployment guide
2. Write upgrade runbook for team
3. Publish case study

---

## 7. Known Issues & Constraints

### Data Integrity

- **Order-Item relationship:** `orders/models.py` appears to lack an OrderItem model (needs verification).
- **Stock management:** No decrement on order; can oversell.
- **Cart persistence:** Session-only; lost on browser clear.

### Performance

- **N+1 queries:** Cart iteration may cause multiple DB hits per item (line 37, cart/cart.py).
- **No caching:** Product list fetched every request.
- **No pagination:** Product list unbounded.

### Operational

- **No logging:** Errors not captured for production debugging.
- **No monitoring:** No health checks, metrics, or alerts.
- **SQLite3 only:** Not suitable for multi-process deployments.

---

## 8. Success Criteria Checklist

- [ ] All tests pass with Django 4.2
- [ ] Cart add/remove/total calculations unchanged
- [ ] Order creation still persists to DB
- [ ] No SECRET_KEY or DEBUG leaks in code
- [ ] ALLOWED_HOSTS enforced
- [ ] Regression test coverage ≥ 90% for cart/order paths
- [ ] Deployment runs without manual intervention
- [ ] Documentation complete and publishable

---

## 9. AI-Assisted Modernization Workstreams

### Discovery Phase (Days 1–2)
- **Tool:** Semantic code analysis
- **Task:** Identify all deprecated APIs, hard-coded values, test gaps
- **Output:** Issue matrix (this file + GitHub issues)

### Refactoring Phase (Days 3–7)
- **Tool:** Code generation & constrained diffs
- **Task:** Generate model fixes, URL updates, settings migration
- **Output:** PRs with detailed commit messages

### Testing Phase (Days 8–10)
- **Tool:** Test generation & failure triage
- **Task:** Generate regression tests, identify failures, propose fixes
- **Output:** Test suite + coverage report

### Security Phase (Days 11–12)
- **Tool:** Secret scanning + hardening templates
- **Task:** Detect leaks, harden defaults, generate checklists
- **Output:** HARDENING.md + security-focused PR

### Documentation Phase (Days 13–14)
- **Tool:** Summary & narrative generation
- **Task:** Create case-study narrative + metrics + LinkedIn draft
- **Output:** CASE-STUDY.md + LinkedIn post

---

## 10. Next Steps

1. **Verify this baseline** with the team (30 min)
2. **Create GitHub issues** from the issue matrix (see section below)
3. **Assign to sprint** with AI-assisted estimation
4. **Begin Phase 1:** Dependency upgrade and `python manage.py check`

---

## Issue Matrix

See [ISSUES.md](./ISSUES.md) for the tracked work items.

---

**Prepared By:** Henry Mbugua (AI-Assisted Analysis)  
**Status:** Ready for Phase 1 Execution  
**Last Updated:** 2026-07-24
