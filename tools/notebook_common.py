"""Shared pieces for the Colab notebook builders (written by Claude Code).

Both notebooks write to the same asset_log.csv / ASSET-LOG.md on Drive, so the log code lives here
once and is pasted into each notebook as a cell.
"""
import json
from pathlib import Path


class Notebook:
    def __init__(self):
        self.cells = []

    def md(self, s):
        self.cells.append(("markdown", s.strip("\n")))

    def code(self, s):
        self.cells.append(("code", s.strip("\n")))

    def save(self, path):
        nb = {"cells": [], "metadata": {
                "accelerator": "GPU", "colab": {"gpuType": "T4", "provenance": []},
                "kernelspec": {"display_name": "Python 3", "name": "python3"},
                "language_info": {"name": "python"}},
              "nbformat": 4, "nbformat_minor": 0}
        for kind, src in self.cells:
            lines = src.split("\n")
            c = {"cell_type": kind, "metadata": {},
                 "source": [l + "\n" for l in lines[:-1]] + [lines[-1]]}
            if kind == "code":
                c.update(execution_count=None, outputs=[])
            nb["cells"].append(c)
        out = Path(path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
        print("cells:", len(self.cells), "->", out)


# One row per generation, shared by the image and audio notebooks. Empty fields are left out of
# the Markdown settings column, so image rows (control image, IP reference) and audio rows
# (duration, sample rate) both read cleanly.
LOG_CELL = r'''
import csv, json, datetime

COLUMNS = ["gen_id", "asset_id", "timestamp_utc", "file", "thumb", "model", "where_run", "license",
           "prompt", "negative_prompt", "seed", "size", "steps", "cfg", "scheduler",
           "control_image", "controlnet_scale", "ip_reference", "ip_scale", "init_image", "strength", "seconds",
           "outcome", "reason", "edits", "where_used"]
OUTCOMES = {"pending", "accepted", "edited", "rejected"}

def _read_log():
    if not LOG_CSV.exists():
        return []
    with open(LOG_CSV, newline="", encoding="utf-8") as f:
        return [{c: r.get(c) or "" for c in COLUMNS} for r in csv.DictReader(f)]   # old rows lack new columns

def _write_log(rows):
    tmp = LOG_CSV.with_suffix(".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader(); w.writerows(rows)
    tmp.replace(LOG_CSV)
    _write_md(rows)

def _cell(s):
    return str(s).replace("|", "\\|").replace("\n", " ")

def _settings(r):
    parts = [f"seed {r['seed']}", r["size"]]
    if r["steps"]: parts.append(f"{r['steps']} steps")
    if r["cfg"] != "": parts.append(f"cfg {r['cfg']}")
    if r["scheduler"]: parts.append(r["scheduler"])
    if r["control_image"]: parts.append(f"control `{r['control_image']}` @ {r['controlnet_scale']}")
    if r["ip_reference"]: parts.append(f"IP ref `{r['ip_reference']}` @ {r['ip_scale']}")
    if r.get("init_image"): parts.append(f"img2img from `{r['init_image']}` @ strength {r.get('strength', '')}")
    parts.append(f"{r['seconds']} s to generate")
    neg = f"<br>**negative:** {r['negative_prompt']}" if r["negative_prompt"] else ""
    return f"**prompt:** {r['prompt']}{neg}<br>" + " · ".join(p for p in parts if p)

def _write_md(rows):
    lines = ["# ASSET-LOG — walker-dusk-duel", "",
             "Generated automatically by `notebooks/generate_images.ipynb` and `notebooks/generate_audio.ipynb`;",
             "one row per generation. Outcome and reason are written by Zhaohui with `review()`. Settings are",
             "sufficient to reproduce an output on the same model commits (small GPU-to-GPU differences are possible).",
             "Audio rows link a waveform image; the full-size raw files stay on Drive (`file` column).", "",
             "| Gen ID | Asset ID | Model and version · where run · license | Prompt and settings | Outcome | Edits | Where used |",
             "|---|---|---|---|---|---|---|"]
    for r in rows:
        outcome = r["outcome"] + (f": {r['reason']}" if r["reason"] else "")
        lines.append("| " + " | ".join(_cell(x) for x in (
            f"`{r['gen_id']}`<br>![]({r['thumb']})", r["asset_id"],
            f"{r['model']} · {r['where_run']} · {r['license']}", _settings(r), outcome,
            r["edits"] or "—", r["where_used"] or "—")) + " |")
    LOG_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

def log_generation(row):
    rows = [r for r in _read_log() if r["gen_id"] != row["gen_id"]]
    rows.append({c: row.get(c, "") for c in COLUMNS})
    _write_log(rows)

def review(gen_id, outcome, reason, where_used=None):
    """Record YOUR judgment, e.g. review("SFX-HIT_s11", "accepted", "dry thud, no tail; reads under the music")"""
    assert outcome in OUTCOMES, f"outcome must be one of {OUTCOMES}"
    assert reason.strip() or outcome == "pending", "write the reason, judged against the sheet/storyboard/pillars"
    rows = _read_log()
    for r in rows:
        if r["gen_id"] == gen_id:
            r["outcome"], r["reason"] = outcome, reason
            if where_used is not None:
                r["where_used"] = where_used
            _write_log(rows); print("logged:", gen_id, outcome); return
    raise KeyError(gen_id)

def add_edit(gen_id, edit, where_used=None):
    rows = _read_log()
    for r in rows:
        if r["gen_id"] == gen_id:
            r["edits"] = (r["edits"] + "; " if r["edits"] else "") + edit
            if r["outcome"] == "accepted":
                r["outcome"] = "edited"
            if where_used:
                r["where_used"] = where_used
            _write_log(rows); return
    raise KeyError(gen_id)

def show_log(asset_prefix=""):
    for r in _read_log():
        if r["asset_id"].startswith(asset_prefix):
            print(f"{r['gen_id']:28s} {r['outcome']:9s} {r['reason'][:70]}")
print("log:", LOG_CSV)
'''
