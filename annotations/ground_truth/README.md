# Ground Truth Annotations

Each paper gets its own CSV file named after the paper ID (e.g., `AIG_UNC_2025_yamada.csv`).
Use `TEMPLATE.csv` as the starting point for each new file.

---

## CSV Schema

| Column           | Type    | Description                                                                 |
|------------------|---------|-----------------------------------------------------------------------------|
| `paper_id`       | string  | Unique paper identifier following the naming convention in the root README  |
| `authorship_type`| string  | One of: `ai_generated_curated`, `ai_generated_uncurated`, `human_ai_hybrid`, `human_accepted`, `human_rejected` |
| `source`         | string  | Dataset or origin (e.g., `ai_researcher`, `fars`, `agents4science`)         |
| `error_id`       | string  | Unique ID per error: `{paper_id}_{three-digit index}` (e.g., `..._001`)     |
| `error_type`     | string  | Code from the taxonomy: `CIT`, `CTM`, `MATH`, `LOG`, `LIN`, `HALL_I`, `HALL_E`, `CON`, `REP` |
| `severity_label` | string  | `minor`, `moderate`, `major`, or `fatal`                                    |
| `severity_score` | int     | Numeric equivalent: 1–4                                                     |
| `section`        | string  | Section name or number where the error occurs                               |
| `page`           | int     | Page number                                                                 |
| `description`    | string  | Concrete, verifiable description of the error                               |
| `automated_flag` | bool    | `True` if first identified by an automated tool                             |
| `flag_source`    | string  | Tool that flagged it: `SciCoQa`, `LanguageTool`, `TextStat`, or empty      |
| `needs_review`   | bool    | `True` if uncertain and needs a second look                                 |
| `annotator`      | string  | Annotator ID                                                                |
| `annotation_date`| date    | ISO 8601 format: YYYY-MM-DD                                                 |
