# Type, Effect, and Capability Model
Status: Normative

## Purpose

This file defines the typing surface that validators and importers must agree on.

## Core judgment

```text
Γ ; W ; K ; R ⊢ e : τ ! ε

Γ = term environment
W = witness environment
K = capability environment
R = region / alias environment
τ = type
ε = finite effect row
```

## Rules

### Call

```text
Γ ⊢ f : fn(τ1..τn) -> τ ! εf using Kf
Γ ⊢ ai : τi   for all i
Kf ⊆ K
----------------------------------------
Γ ; W ; K ; R ⊢ call f(a1..an) : τ ! εf
```

### Witness-based invoke

```text
Γ ⊢ w : witness<I<T...>>
method(I, m) = fn(self: σ, τ1..τn) -> τ ! εm
---------------------------------------------
Γ ; W ; K ; R ⊢ invoke I.m w(args) : τ ! εm
```

### Throw

```text
Γ ⊢ e : E
----------------------------------------
Γ ; W ; K ; R ⊢ throw e : α ! { throw(E) }
```

### Try catch

```text
Gamma ; W ; K ; R |- b_try : tau ! eps_try
Gamma, x:E ; W ; K ; R |- b_catch : tau ! eps_catch
----------------------------------------------------------------
Gamma ; W ; K ; R |- try b_try catch(x: E) b_catch : tau ! ((eps_try - {throw(E)}) U eps_catch)
```

### Borrow mutable

```text
place p : own<T> in R
no_live_aliases(p)
----------------------------------------
Γ ; W ; K ; R ⊢ borrow_mut p : borrow_mut<T> ! {}
```

### Spawn

```text
Γ ; W ; K ; R ⊢ e : τ ! ε
----------------------------------------
Γ ; W ; K ; R ⊢ spawn e : task<τ> ! ({spawn} ∪ sched(ε))
```

## Capability rules

- capabilities are explicit values or imports,
- ambient power is not allowed in canonical `SCIR-H`,
- a call is invalid if its declared capability requirement is not satisfied,
- capabilities must cross opaque and foreign boundaries explicitly.

## Effect rules

- effect rows are finite and explicit at public boundaries,
- hidden effects are invalid,
- `unsafe` and `opaque` are effects as well as boundary categories,
- a `catch(x: E)` boundary discharges only the exact `throw(E)` obligation from the guarded block,
- all non-throw effects remain explicit and visible across `try/catch`,
- other `throw(T)` obligations remain explicit unless a matching catch boundary is present,
- canonical v0.1 `SCIR-H` allows only the single-catch form above; `finally`, multi-catch, and pattern-heavy handlers are out of scope,
- effect elimination or specialization belongs to lowering or optimization, not canonical `SCIR-H`.

## Exported interface rule

Public or exported declarations must carry explicit type, effect, and capability signatures even when local tooling offers elided views.

## Profile interaction

- `R`, `D-PY`, and `D-JS` usually preserve more effect visibility.
- `N` and `P` may lower or specialize effects only when legal under the active preservation claim.
