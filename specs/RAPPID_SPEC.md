> **Refresh (2026-07-15):** identity/mint sections are SUPERSEDED by RAPP/1 §6 — canonical `rappid:@owner/slug:64hex`, keyless mint `Hb("rapp/1:rappid", uuid4)`; the `rappid:v2:...@host` form shown below is legacy, read-forever, never emitted. See https://raw.githubusercontent.com/kody-w/rapp-1/main/SPEC.md

# RAPPID_SPEC — Identity v2

> **Frozen excerpt** of the canonical rappid contract (`rapp/1`, §6.1). Bundled at planting time on 2026-05-09T12:52:08Z.

> **Superseded format note (Constitution Art. XXXIV.1, locked 2026-06-03).** The
> one current rappid string is the consolidated Eternity form:
>
> ```
> rappid:@<owner>/<slug>:<hex>
> ```
>
> No `v2:`/`v3:` prefix, no inline `<kind>:` segment, no trailing `@github.com/...`
> suffix. `kind` now lives in the `rappid.json` **record** as a field (record
> schema is `rapp/1` (Art. LIV; formerly rapp-rappid/2.0)). Existing hashes are preserved (never
> regenerated); the prior string is recorded under `_migrated_from`. The legacy
> v2 grammar below is retained for read-forever compatibility only — every legacy
> form is still parsed and canonicalized (see `kody-w/RAPP::tools/door_address.py`
> `canonicalize_rappid`), but only the consolidated form above is emitted.

## Format

```
rappid:v2:<kind>:@<owner>/<repo>:<32-hex-no-dashes>@github.com/<owner>/<repo>
```

Example (this neighborhood's):

```
rappid:v2:<kind>:@kody-w/kody-twin:<32-hex>@github.com/kody-w/kody-twin
```

(See `../rappid.json` for the actual value.)

## Components

| Part | Rule |
|---|---|
| Prefix `rappid:v2:` | Literal. Tells parsers this is a legacy v2 rappid (read-forever; never minted anew). |
| `<kind>` | One of: `neighborhood`, `ant-farm`, `braintrust`, `workspace`, `twin`, `prototype`. |
| `@<owner>/<repo>` | The GitHub composite identity. The `@` prefix is literal and required. |
| `<32-hex-no-dashes>` | A UUID4 with dashes stripped — 32 lowercase hex characters. Minted ONCE at planting; permanent thereafter. |
| `@github.com/<owner>/<repo>` | The substrate URL, suffixed for self-resolution. |

## Invariants (Constitution Art. XXXIV.5)

1. **Permanence.** Once minted, a rappid is permanent for the lifetime of the neighborhood. Re-grafting, re-planting, kernel upgrades — none of these mint a new rappid.
2. **Bond preservation.** The bond technique (egg → overlay → hatch back) preserves the rappid through every kernel upgrade.
3. **Lineage chain.** A neighborhood's `parent_rappid` chains back to its ancestor (the species root for many: `rappid:@kody-w/rapp:9a8f0a4b5a710e20f4d819a0f37d2a4c9f113b5e78fb3c29e70b54fff48a38f9`).
4. **No two organisms share a rappid.** Mint the 64-hex tail via `Hb("rapp/1:rappid", uuid4_bytes)` (RAPP/1 §6.2, keyless, domain-separated) — NEVER `uuid4().hex` (only 32 hex) and NEVER `sha256(owner/slug)` (the cardinal sin).
5. **The rappid is the seed source for the neighborhood's holocard.** `derive_seed(rappid_str)` via BLAKE2b-64 produces a deterministic 64-bit ID. Same rappid → same seed → same incantation, forever.

## Required fields in `../rappid.json` (`rapp/1`)

| Field | Required | Notes |
|---|---|---|
| `schema`       | yes | `rapp/1` |
| `rappid`       | yes | The full v2 string |
| `kind`         | yes | One of the 6 kinds above |
| `name`         | yes | Slug — matches the repo name |
| `display_name` | yes | Human-readable |
| `github`       | yes | `https://github.com/<owner>/<repo>` |
| `parent_rappid`| yes (may be null for species roots) | The lineage anchor |
| `parent_repo`  | yes | Where the parent's rappid lives |
| `planted_by`   | yes | GitHub handle of the operator who planted |
| `planted_at`   | yes | ISO-8601 UTC |
| `kernel_version` | yes | The kernel version at planting time |

## Don't

- Don't change the rappid after minting — that's identity destruction. Use a new rappid for a new neighborhood instead.
- Don't synthesize rappids by hand — always mint via UUID4.
- Don't include personal data in the rappid — it travels publicly.
- Don't reuse a rappid string across neighborhoods (uniqueness is critical for seed derivation).

---

*Frozen excerpt. For full identity / lineage / bonding rules, see `CONSTITUTION.md` Art. XXXIV.5 in the parent repo if reachable.*
