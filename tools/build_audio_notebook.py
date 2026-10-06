"""Builds notebooks/generate_audio.ipynb (written by Claude Code).

Run from the project root:  python tools/build_audio_notebook.py notebooks/generate_audio.ipynb
"""
import sys

import notebook_common as common

nb = common.Notebook()
md, code = nb.md, nb.code

md(r'''
# walker-dusk-duel — sound effects and music (Google Colab, free T4)

Generates the four event sounds and the music loop for the asset slice, saves every candidate to
Google Drive, and appends **one row per generation** to the same `asset_log.csv` / `ASSET-LOG.md`
as the image notebook.

Written by Claude Code. The audio comes from the open models in cells 4 and 8, not from Claude.

| Asset | Event (CHANGE-BRIEF) | Model |
|---|---|---|
| SFX-WHIFF | attack's active window ends with no contact | Stable Audio Open 1.0 |
| SFX-HIT | hitbox meets a non-blocking hurtbox | Stable Audio Open 1.0 |
| SFX-BLOCK | hitbox meets a blocking fighter | Stable Audio Open 1.0 |
| SFX-KO | health reaches 0 | Stable Audio Open 1.0 |
| MUS-LOOP | title → fight; stops at K.O.; restarts on rematch | MusicGen (medium) |

**Before running**

1. `Runtime → Change runtime type → T4 GPU`. Use the same `MyDrive/walker-dusk-duel/` folder as the
   image notebook.
2. Stable Audio Open is a **gated** model: sign in at huggingface.co, open
   `stabilityai/stable-audio-open-1.0`, read and accept its license, create a *read* access token,
   and store it in Colab's **Secrets** panel (key icon) as `HF_TOKEN`. Never paste the token into a
   cell; it must not end up in the notebook or the repo.

**Rights rules:** no existing song, recording, composer, artist, franchise or voice in any prompt
or as reference audio. `check_prompt()` blocks a list of such words.

**Listening is the real check.** Every candidate is shown as a player. Judge it at game volume, with
the music playing underneath, and record your decision with `review()`.
''')

md("## 1 · Mount Drive and set paths")
code(r'''
import os, sys
from pathlib import Path

IN_COLAB = "google.colab" in sys.modules
if IN_COLAB:
    from google.colab import drive
    drive.mount("/content/drive")

ROOT = Path(os.environ.get("DUSK_ROOT", "/content/drive/MyDrive/walker-dusk-duel"))
RAW = ROOT / "raw" / "audio"                                  # full-size WAV: Drive only
GEN = ROOT / "design" / "generations" / "audio"               # same path in the repo
WAVES, PREVIEWS, CHECKS = GEN / "waveforms", GEN / "previews", GEN / "checks"
SFX_OUT, MUSIC_OUT = ROOT / "godot" / "audio" / "sfx", ROOT / "godot" / "audio" / "music"
for d in (RAW, WAVES, PREVIEWS, CHECKS, SFX_OUT, MUSIC_OUT):
    d.mkdir(parents=True, exist_ok=True)
LOG_CSV, LOG_MD = ROOT / "asset_log.csv", ROOT / "ASSET-LOG.md"
print("project root:", ROOT)
''')

md("## 2 · Install libraries")
code(r'''
%pip install -q -U diffusers transformers accelerate soundfile torchsde huggingface_hub
# Colab's preinstalled torchao is too old for diffusers >= 0.41 (missing FqnToConfig) and breaks the
# Stable Audio import; diffusers only needs it for quantization, so remove it.
%pip uninstall -y -q torchao
''')

md("## 3 · Prompts and the rights check")
code(r'''
import re

BANNED = [
    r"mortal\s*kombat", r"\bmk\d*\b", r"street\s*fighter", r"tekken", r"capcom", r"netherrealm",
    r"nintendo", r"disney", r"pixar", r"ghibli", r"marvel", r"bruce\s*lee", r"hans\s*zimmer",
    r"\bin the style of\b", r"\bstyle of\b", r"\bby [A-Z][a-z]+", r"\bcover of\b", r"\bremix of\b",
    r"\bsoundtrack from\b", r"\btheme from\b", r"\bvoice of\b", r"\bsounds like [A-Z]",
]

def check_prompt(text):
    hits = [p for p in BANNED if re.search(p, text, flags=re.IGNORECASE if not p.startswith(r"\bby") and "[A-Z]" not in p else 0)]
    if hits:
        raise ValueError(f"Prompt blocked by rights check, matched: {hits}")
    return text

SFX_NEGATIVE = ("music, melody, singing, voice, speech, talking, crowd, applause, long reverb, echo, "
                "background noise, hiss, distortion, low quality")

# asset id -> (prompt, generated length s, kept length s). Generate a little long, trim later.
SFX = {
    "SFX-WHIFF": ("a single quick swish of a fist cutting through the air, short close whoosh, "
                  "dry, no reverb, isolated sound effect", 1.0, 0.35),
    "SFX-HIT": ("a single solid punch landing on a body, dull punchy thud with weight and low end, "
                "close, dry, no reverb, isolated fighting game sound effect", 1.0, 0.40),
    "SFX-BLOCK": ("a single hard knock of a forearm blocking a strike, sharp wooden clack with a short "
                  "cloth rustle, close, dry, isolated sound effect", 1.0, 0.40),
    "SFX-KO": ("a heavy body falling onto a stone floor, followed by one deep temple gong ringing out "
               "and fading, isolated sound effect", 3.0, 2.5),
}

MUSIC_PROMPT = ("calm ceremonial temple music at dusk, slow steady taiko drum pulse, airy bamboo flute "
                "melody, sparse wooden percussion, focused and tense but quiet, 80 bpm, 4/4, "
                "instrumental, no vocals")

for p, *_ in SFX.values():
    check_prompt(p)
check_prompt(SFX_NEGATIVE); check_prompt(MUSIC_PROMPT)
print("prompts pass the rights check")
''')

md("## 4 · Hugging Face sign-in (token from Colab Secrets, never typed here)")
code(r'''
from huggingface_hub import login
if IN_COLAB:
    from google.colab import userdata
    login(token=userdata.get("HF_TOKEN"))      # reads the secret; nothing is stored in the notebook
''')

md("## 5 · Asset log helpers (shared with the image notebook)")
code(common.LOG_CELL)

md("## 6 · Audio helpers: save, waveform thumbnail, preview, players")
code(r'''
import time, torch, numpy as np, soundfile as sf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from IPython.display import Audio, display
import diffusers, transformers
from huggingface_hub import model_info

GPU = torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU"
ENV = f"Google Colab ({GPU}); torch {torch.__version__}, diffusers {diffusers.__version__}, transformers {transformers.__version__}"

def hub(repo):
    try:
        info = model_info(repo)
        lic = (info.card_data or {}).get("license", "see model card") if info.card_data else "see model card"
        return {"repo": repo, "sha": info.sha, "license": str(lic)}
    except Exception as e:
        return {"repo": repo, "sha": "unknown", "license": f"unknown ({type(e).__name__})"}

def rel(p):
    return Path(p).relative_to(ROOT).as_posix() if p else ""

def to_mono(x):
    x = np.asarray(x, dtype=np.float32)
    return x.mean(axis=1) if x.ndim == 2 else x

def waveform_png(x, sr, path, title, marks=()):
    x = to_mono(x)
    fig, ax = plt.subplots(figsize=(4, 1.2), dpi=80)
    t = np.arange(len(x)) / sr
    ax.plot(t, x, linewidth=0.5, color="#2b2733")
    for m in marks:
        ax.axvline(m, color="#d9482b", linewidth=0.8)
    ax.set_ylim(-1, 1); ax.set_yticks([]); ax.set_title(title, fontsize=7); ax.tick_params(labelsize=6)
    fig.tight_layout(); fig.savefig(path); plt.close(fig)

def write_ogg(path, x, sr, block=4096):
    """OGG Vorbis written in blocks: libsndfile can overflow the stack (hard crash) when a long
    array is written to OGG in one call; found by the offline smoke test on a 30 s take."""
    x = np.ascontiguousarray(x, dtype=np.float32)
    channels = 1 if x.ndim == 1 else x.shape[1]
    with sf.SoundFile(path, "w", samplerate=sr, channels=channels, format="OGG", subtype="VORBIS") as f:
        for i in range(0, len(x), block):
            f.write(x[i:i + block])

def write_ogg_checked(path, x, sr, ceiling_db=-1.0, tries=4):
    """Game export: Vorbis is lossy and can push peaks ~1-3 dB above the input (found by the smoke
    test: -1 dBFS in, +1.7 dBFS decoded). Read the file back and lower the gain until the decoded
    peak is under the ceiling. Returns (decoded peak dBFS, extra gain dB)."""
    extra = 0.0
    for _ in range(tries):
        write_ogg(path, x * 10 ** (extra / 20), sr)
        y, _sr = sf.read(path, dtype="float32")
        peak = 20 * np.log10(max(float(np.max(np.abs(y))), 1e-9))
        if peak <= ceiling_db:
            break
        extra -= (peak - ceiling_db) + 0.3
    return round(peak, 2), round(extra, 2)

def save_preview(x, sr, path):
    """Small mono OGG of every candidate (kept in the repo, including rejected ones)."""
    write_ogg(path, to_mono(x), sr)

def log_audio(gen_id, asset_id, raw_path, x, sr, model, license_, prompt, negative, seed, steps, cfg,
              sampler, secs, length_s):
    (WAVES / asset_id).mkdir(exist_ok=True); (PREVIEWS / asset_id).mkdir(exist_ok=True)
    wpng = WAVES / asset_id / f"{gen_id}.png"
    waveform_png(x, sr, wpng, gen_id)
    save_preview(x, sr, PREVIEWS / asset_id / f"{gen_id}.ogg")
    log_generation({
        "gen_id": gen_id, "asset_id": asset_id,
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        "file": rel(raw_path), "thumb": rel(wpng), "model": model, "where_run": ENV, "license": license_,
        "prompt": prompt, "negative_prompt": negative, "seed": seed,
        "size": f"{length_s:.2f} s @ {sr} Hz", "steps": steps, "cfg": cfg, "scheduler": sampler,
        "seconds": secs, "outcome": "pending"})
''')

md(r'''
## 7 · Load Stable Audio Open (sound effects)

`stabilityai/stable-audio-open-1.0` — Stability AI Community License (read it on the model card:
free for research and non-commercial use and for small commercial use under its revenue limit;
attribution required). Commit hash and license field are logged per row.
''')
code(r'''
from diffusers import StableAudioPipeline
SAO = hub("stabilityai/stable-audio-open-1.0")
print(SAO)
sao = StableAudioPipeline.from_pretrained(SAO["repo"], torch_dtype=torch.float16).to("cuda")
sao.set_progress_bar_config(disable=True)
SAO_SR = sao.vae.sampling_rate
SAO_SAMPLER = type(sao.scheduler).__name__

def generate_sfx(asset_id, seeds=(11, 12, 13, 14), steps=100, cfg=7.0, prompt=None, length=None):
    p, gen_len, _ = SFX[asset_id]
    prompt = check_prompt(prompt or p)
    length = length or gen_len
    (RAW / asset_id).mkdir(parents=True, exist_ok=True)
    ids = []
    for seed in seeds:
        gen_id = f"{asset_id}_s{seed}"
        t0 = time.time()
        out = sao(prompt, negative_prompt=SFX_NEGATIVE, num_inference_steps=steps, guidance_scale=cfg,
                  audio_end_in_s=length, num_waveforms_per_prompt=1,
                  generator=torch.Generator("cuda").manual_seed(seed)).audios[0]
        secs = round(time.time() - t0, 1)
        x = out.T.float().cpu().numpy()                    # (samples, channels)
        raw = RAW / asset_id / f"{gen_id}.wav"
        sf.write(raw, x, SAO_SR)
        log_audio(gen_id, asset_id, raw, x, SAO_SR, f"Stable Audio Open 1.0 @{SAO['sha'][:10]}",
                  f"Stable Audio Open: {SAO['license']}", prompt, SFX_NEGATIVE, seed, steps, cfg,
                  SAO_SAMPLER, secs, length)
        print(f"{gen_id}: {secs} s"); display(Audio(to_mono(x), rate=SAO_SR))
        ids.append(gen_id)
    return ids
''')

md(r'''
## Stage 1 · The four event sounds

Four seeds each. Listen for: does it start **immediately** (no lead-in), is it **short and dry**
(pillar *Every hit is felt*), can you tell hit / block / whiff apart **with your eyes closed**
(pillar *Read the opponent*)?
''')
code(r'''
sfx_ids = {a: generate_sfx(a) for a in SFX}
''')
code(r'''
# Objective checks on the SFX takes (Claude cannot listen; Zhaohui re-judges by ear).
# onset_ms: lead-in before the sound reaches -20 dB of its peak (pillar: starts immediately)
# dur_ms: onset to the last moment above -30 dB of peak (short and dry; KO should ring out)
# in_keep_%: share of the energy inside the kept window from cell 3 (does the trim lose the sound?)
# events: onsets detected inside the kept window (one hit wanted; KO = thud + gong)
# low_%: energy below 250 Hz (weight of a hit), centroid_hz: brightness (block clack > hit thud)
import librosa, librosa.display, pandas as pd
rows = []
fig, axes = plt.subplots(len(SFX), 4, figsize=(14, 2.0 * len(SFX)), dpi=70)
for r, (asset, ids) in enumerate(sfx_ids.items()):
    keep_s = SFX[asset][2]
    for c, gid in enumerate(ids):
        x, sr = sf.read(RAW / asset / f"{gid}.wav", dtype="float32"); x = to_mono(x)
        a = np.abs(x); peak = a.max()
        on = int(np.argmax(a > peak * 10 ** (-20 / 20)))
        above = np.where(a > peak * 10 ** (-30 / 20))[0]
        k = x[on:on + int(keep_s * sr)]
        S = np.abs(librosa.stft(k, n_fft=1024)) ** 2
        f = librosa.fft_frequencies(sr=sr, n_fft=1024)
        ev = librosa.onset.onset_detect(y=k, sr=sr, units="time", backtrack=False)
        rows.append({"gen_id": gid, "onset_ms": round(on / sr * 1000), "dur_ms": round((above[-1] - on) / sr * 1000),
                     "in_keep_%": round(100 * float((k ** 2).sum() / (x ** 2).sum()), 1), "events": len(ev),
                     "low_%": round(100 * float(S[f < 250].sum() / S.sum()), 1),
                     "centroid_hz": int(librosa.feature.spectral_centroid(y=k, sr=sr).mean()),
                     "peak_db": round(20 * np.log10(peak), 1)})
        ax = axes[r, c]
        librosa.display.specshow(librosa.amplitude_to_db(np.abs(librosa.stft(x, n_fft=1024)), ref=np.max),
                                 sr=sr, x_axis="time", y_axis="log", ax=ax)
        ax.axvline(on / sr, color="w", lw=0.8); ax.axvline(on / sr + keep_s, color="r", lw=0.8)
        ax.set_title(gid, fontsize=9); ax.set_xlabel(""); ax.set_ylabel("")
fig.tight_layout(); fig.savefig(CHECKS / "SFX_candidates_spectrograms.png"); plt.close(fig)
SFX_TABLE = pd.DataFrame(rows)
print(SFX_TABLE.to_string())
from IPython.display import Image as IPImage
display(IPImage(filename=str(CHECKS / "SFX_candidates_spectrograms.png")))
''')
code(r'''
# YOUR decisions, one line per candidate, e.g.:
# review("SFX-HIT_s12", "accepted", "dry thud, instant attack; clearly heavier than the block clack")
# review("SFX-HIT_s11", "rejected", "200 ms of silence before the hit and a long room tail")
show_log("SFX")
''')

md(r'''
## Stage 2 · Trim and export the accepted sounds

`export_sfx` makes a game-ready file and logs every edit: mono, leading silence below
`threshold_db` removed, cut to the kept length from cell 3, 10 ms fade-in guard and a fade-out,
peak normalised. Output: `godot/audio/sfx/<name>.ogg`, which the slice's AudioDirector loads.
''')
code(r'''
def export_sfx(gen_id, name, threshold_db=-40.0, fade_out_ms=40, peak_db=-1.0, keep_s=None):
    asset_id = gen_id.rsplit("_s", 1)[0]
    x, sr = sf.read(RAW / asset_id / f"{gen_id}.wav", dtype="float32")
    x = to_mono(x)
    thr = 10 ** (threshold_db / 20) * np.max(np.abs(x))
    start = int(np.argmax(np.abs(x) > thr))
    keep_s = keep_s or SFX[asset_id][2]
    y = x[start:start + int(keep_s * sr)].copy()
    fi = int(0.010 * sr) if start > 0 else 0              # guard against a click where we cut in
    if fi:
        y[:fi] *= np.linspace(0.0, 1.0, fi)
    fo = min(int(fade_out_ms / 1000 * sr), len(y))
    y[-fo:] *= np.linspace(1.0, 0.0, fo)
    gain = 10 ** (peak_db / 20) / max(np.max(np.abs(y)), 1e-9)
    y *= gain
    out = SFX_OUT / f"{name}.ogg"
    decoded, extra = write_ogg_checked(out, y, sr, ceiling_db=peak_db)
    edit = (f"mono; trimmed {start / sr * 1000:.0f} ms leading silence (< {threshold_db} dB of peak); "
            f"kept {len(y) / sr:.2f} s; fade-in {fi / sr * 1000:.0f} ms, fade-out {fade_out_ms} ms; "
            f"peak normalised to {peak_db} dBFS (gain {20 * np.log10(gain):+.1f} dB), OGG Vorbis, "
            f"decoded peak {decoded} dBFS after {extra:+.1f} dB correction -> {rel(out)}")
    add_edit(gen_id, edit, where_used=f"{rel(out)} (AudioDirector)")
    waveform_png(y, sr, CHECKS / f"{gen_id}_export.png", f"{gen_id} exported")
    print(edit); display(Audio(y, rate=sr))
    return out

# After review(), e.g.:
# export_sfx("SFX-WHIFF_s13", "whiff")
# export_sfx("SFX-HIT_s12", "hit")
# export_sfx("SFX-BLOCK_s11", "block")
# export_sfx("SFX-KO_s14", "ko")
''')

md(r'''
## 8 · Load MusicGen (music)

`facebook/musicgen-medium` through 🤗 transformers. Weights are **CC-BY-NC 4.0** (non-commercial,
attribution) — acceptable for coursework, and it must be stated in SOURCES.md. Generation is
sampled, so the seed is set with `torch.manual_seed` right before each call.
''')
code(r'''
from transformers import AutoProcessor, MusicgenForConditionalGeneration
MG = hub("facebook/musicgen-medium")
print(MG)
mg_proc = AutoProcessor.from_pretrained(MG["repo"])
mg = MusicgenForConditionalGeneration.from_pretrained(MG["repo"]).to("cuda")
MG_SR = mg.config.audio_encoder.sampling_rate
MG_FRAME_RATE = mg.config.audio_encoder.frame_rate       # tokens per second

def generate_music(asset_id="MUS-RAW", seeds=(21, 22, 23), seconds=30, guidance=3.0, top_k=250,
                   temperature=1.0, prompt=MUSIC_PROMPT):
    check_prompt(prompt)
    (RAW / asset_id).mkdir(parents=True, exist_ok=True)
    inputs = mg_proc(text=[prompt], padding=True, return_tensors="pt").to("cuda")
    ids = []
    for seed in seeds:
        gen_id = f"{asset_id}_s{seed}"
        torch.manual_seed(seed)
        t0 = time.time()
        audio = mg.generate(**inputs, do_sample=True, guidance_scale=guidance, top_k=top_k,
                            temperature=temperature, max_new_tokens=int(seconds * MG_FRAME_RATE))
        secs = round(time.time() - t0, 1)
        x = audio[0, 0].float().cpu().numpy()
        raw = RAW / asset_id / f"{gen_id}.wav"
        sf.write(raw, x, MG_SR)
        log_audio(gen_id, asset_id, raw, x, MG_SR, f"MusicGen medium @{MG['sha'][:10]}",
                  f"MusicGen weights: {MG['license']}", prompt, "", seed, int(seconds * MG_FRAME_RATE),
                  guidance, f"sampling top_k={top_k} temperature={temperature}", secs, len(x) / MG_SR)
        print(f"{gen_id}: {secs} s"); display(Audio(x, rate=MG_SR))
        ids.append(gen_id)
    return ids
''')

md(r'''
## Stage 3 · Music candidates

Generated longer (30 s) than the loop needs, as the assignment advises. Listen for a **steady
tempo** (the loop cut relies on the beat tracker) and whether it serves *Dusk ritual*: calm, sparse,
nothing that fights the impact sounds.
''')
code(r'''
music_ids = generate_music()
''')
code(r'''
# Objective checks on the music takes (Claude cannot listen; Zhaohui re-judges by ear).
# Steadiness = spread of beat-to-beat intervals (lower = steadier); loudness drift = spread of
# 1 s RMS levels; low share = energy below 250 Hz, where the hit thud lives.
import librosa, librosa.display
rows = []
for gid in music_ids:
    x, sr = sf.read(RAW / "MUS-RAW" / f"{gid}.wav", dtype="float32"); x = to_mono(x)
    tempo, beats = librosa.beat.beat_track(y=x, sr=sr, units="time")
    ibi = np.diff(beats[beats > 2.0])
    win = sr
    rms = np.array([np.sqrt(np.mean(x[i:i + win] ** 2)) + 1e-9 for i in range(0, len(x) - win, win)])
    rms_db = 20 * np.log10(rms)
    S = np.abs(librosa.stft(x, n_fft=2048)) ** 2
    f = librosa.fft_frequencies(sr=sr, n_fft=2048)
    rows.append({"gen_id": gid, "tempo": round(float(np.atleast_1d(tempo)[0]), 1), "beats": len(beats),
                 "ibi_cv_%": round(100 * float(np.std(ibi) / np.mean(ibi)), 1),
                 "rms_db_mean": round(float(rms_db.mean()), 1), "rms_db_std": round(float(rms_db.std()), 1),
                 "quiet_s": int((rms_db < rms_db.max() - 30).sum()),
                 "low_share_%": round(100 * float(S[f < 250].sum() / S.sum()), 1),
                 "centroid_hz": int(librosa.feature.spectral_centroid(y=x, sr=sr).mean())})
    fig, ax = plt.subplots(figsize=(8, 2.2), dpi=80)
    librosa.display.specshow(librosa.power_to_db(librosa.feature.melspectrogram(y=x, sr=sr), ref=np.max),
                             sr=sr, x_axis="time", y_axis="mel", ax=ax)
    for b in beats: ax.axvline(b, color="w", linewidth=0.3)
    ax.set_title(f"{gid} mel spectrogram, tracked beats"); fig.tight_layout()
    fig.savefig(CHECKS / f"{gid}_mel.png"); plt.close(fig)
import pandas as pd
print(pd.DataFrame(rows).to_string())
from IPython.display import Image as IPImage
for gid in music_ids: display(IPImage(filename=str(CHECKS / f"{gid}_mel.png")))
''')
code(r'''
# review("MUS-RAW_s22", "accepted", "steady pulse, flute stays out of the hit/block frequency range")
show_log("MUS")
''')

md(r'''
## Stage 4 · Cut the loop at bar boundaries and check the seam

`make_loop` uses the librosa beat tracker on the accepted take, starts on a beat after `skip_s`
(skips the intro), and ends exactly `bars × beats_per_bar` beats later. Both cut points snap to a
zero crossing, and the last `xfade_ms` of the loop are crossfaded with the audio just before the
start point, so the end flows into the beginning. It then reports a seam score and renders **three
repetitions** to listen to. The beat tracker does not know where bar 1 is: if the loop feels
off-beat, try `start_beat_offset=1, 2 or 3`.
''')
code(r'''
import librosa

def _snap_zero(x, i, win):
    lo, hi = max(i - win, 1), min(i + win, len(x) - 1)
    seg = x[lo:hi]
    zc = np.where(np.signbit(seg[:-1]) != np.signbit(seg[1:]))[0]
    return lo + int(zc[np.argmin(np.abs(zc + lo - i))]) + 1 if len(zc) else i

def seam_score(loop, sr):
    """Jump across the seam vs. typical sample-to-sample change. ~1-3 is clean; >10 is a likely click."""
    d = np.abs(np.diff(loop))
    seam = abs(float(loop[0]) - float(loop[-1]))
    return seam / (np.median(d) + 1e-9)

def make_loop(gen_id, bars=8, beats_per_bar=4, skip_s=2.0, start_beat_offset=0, xfade_ms=40):
    asset_id = gen_id.rsplit("_s", 1)[0]
    x, sr = sf.read(RAW / asset_id / f"{gen_id}.wav", dtype="float32")
    x = to_mono(x)
    tempo, beats = librosa.beat.beat_track(y=x, sr=sr, units="samples")
    tempo = float(np.atleast_1d(tempo)[0])
    first = int(np.searchsorted(beats, int(skip_s * sr))) + start_beat_offset
    n = bars * beats_per_bar
    if first + n >= len(beats):
        raise ValueError(f"only {len(beats)} beats tracked at {tempo:.1f} bpm; use fewer bars or a longer take")
    win = int(0.005 * sr)
    s = _snap_zero(x, int(beats[first]), win)
    e = _snap_zero(x, int(beats[first + n]), win)
    xf = int(xfade_ms / 1000 * sr)
    if s < xf:
        raise ValueError("start too close to the beginning for the crossfade; raise skip_s")
    loop = x[s:e].copy()
    fade = np.linspace(0.0, 1.0, xf, dtype=np.float32)
    raw_seam = seam_score(loop, sr)
    loop[-xf:] = loop[-xf:] * (1 - fade) + x[s - xf:s] * fade   # tail flows into the head
    score = seam_score(loop, sr)
    peak = np.max(np.abs(loop)); loop *= 10 ** (-1.0 / 20) / peak
    raw_loop = RAW / "MUS-LOOP" / f"{gen_id}_loop.wav"; raw_loop.parent.mkdir(parents=True, exist_ok=True)
    sf.write(raw_loop, loop, sr)
    # seam close-up: 30 ms either side, as heard when the loop repeats
    z = int(0.03 * sr); around = np.concatenate([loop[-z:], loop[:z]])
    waveform_png(around, sr, CHECKS / f"{gen_id}_seam.png", f"{gen_id} seam (score {score:.1f})", marks=(z / sr,))
    three = np.tile(loop, 3)
    save_preview(three, sr, CHECKS / f"{gen_id}_loop_x3.ogg")
    info = {"tempo_bpm": round(tempo, 1), "start_s": round(s / sr, 3), "end_s": round(e / sr, 3),
            "length_s": round((e - s) / sr, 3), "bars": bars, "seam_before_xfade": round(float(raw_seam), 1),
            "seam_after_xfade": round(float(score), 1)}
    print(info)
    display(Audio(three, rate=sr))
    return loop, sr, info

# loop, sr, info = make_loop("MUS-RAW_s22")
''')
code(r'''
def export_music(gen_id, loop, sr, info):
    out = MUSIC_OUT / "loop.ogg"
    decoded, extra = write_ogg_checked(out, loop, sr)
    edit = (f"loop cut {info['bars']} bars at detected {info['tempo_bpm']} bpm, {info['start_s']}-{info['end_s']} s "
            f"({info['length_s']} s), cut points snapped to zero crossings, 40 ms tail-to-head crossfade, "
            f"peak -1 dBFS (decoded {decoded} dBFS, {extra:+.1f} dB correction); seam score {info['seam_before_xfade']} -> {info['seam_after_xfade']}; "
            f"Godot loops the OGG (AudioDirector sets loop = true) -> {rel(out)}")
    add_edit(gen_id, edit, where_used=f"{rel(out)} (AudioDirector, panels 1-5, 7)")
    print(edit)
    return out

# export_music("MUS-RAW_s22", loop, sr, info)
''')

md(r'''
## Stage 5 · Bring results back into the repo

The Drive folder mirrors the repo, so copy these to the **same paths**:

| Path (Drive = repo) | Contents |
|---|---|
| `ASSET-LOG.md`, `asset_log.csv` | the shared log (image and audio rows) |
| `design/generations/audio/` | waveform images, small OGG previews of **every** candidate (including rejected), seam checks, 3× loop renders |
| `godot/audio/sfx/*.ogg`, `godot/audio/music/loop.ogg` | the files the slice plays |

Keep `raw/` on Drive only. Then in Godot, **listen**: each event once per hit, the loop at least three
times round, pause, K.O. and rematch, and record what you heard in TEST-REPORT.md.
''')

nb.save(sys.argv[1])
