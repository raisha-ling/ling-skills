---
name: export-labeled-audio-clips
description: Split a long recording into individually labeled MP3 files using spreadsheet Sound IDs and expected text, verify segment counts before labeling, add configurable padding, and run text-vs-audio QA to flag possible mismatches. Use when working with one long MP3 plus a spreadsheet of ordered audio items.
---

# Audio Labeling & QA Skill

## About

- **Privilege level:** draft-only — reads a spreadsheet and an audio file you supply, and writes clips, a ZIP and a QA report for you to check. It publishes nothing, sends nothing, and never writes back to the source sheet.
- **Tools needed:** FFmpeg (segmentation and MP3 export) and a spreadsheet reader (`.xlsx`, `.xls`, `.csv`). Optionally a multilingual ASR model (Whisper, faster-whisper or WhisperX) for the text-vs-audio QA pass. Without ASR the split and labeling still run; the transcript and similarity columns stay empty and every clip is marked REVIEW rather than PASS.
- **Where it runs:** locally, on one long recording plus the ordered spreadsheet it was recorded from.

## Purpose

Use this skill when the user provides:

- one spreadsheet containing audio metadata, Sound IDs, expected text, and optionally speaker information;
- one long MP3 recording containing multiple words/sentences recorded in spreadsheet order.

The goal is to:

1. split the long MP3 into individual clips;
2. label each clip with the correct Sound ID;
3. preserve a small amount of silence before and after each utterance;
4. verify that the number of exported clips exactly matches the expected spreadsheet rows;
5. compare the spoken audio against the expected text;
6. flag possible text/audio mismatches for manual review;
7. export a ZIP of labeled MP3 files plus a QA report.

---

## Core Rule

**Never assume that the number of initially detected audio segments is correct.**

Before assigning Sound IDs, determine the exact number of audio items expected from the spreadsheet.

If the spreadsheet contains 73 expected rows, the final result must contain exactly 73 MP3 files.

If the first silence-detection pass finds 72 or 74 segments:

- do not label/export immediately;
- inspect suspicious gaps;
- search for unusually short pauses that may have caused two recordings to merge;
- search for false splits caused by pauses inside one sentence;
- reconcile the detected count with the expected spreadsheet count;
- only assign Sound IDs after the count is resolved.

If the count cannot be reconciled confidently, stop and flag the suspicious timestamps for manual review. **Do not guess.**

---

## Expected Inputs

### Spreadsheet

Prefer `.xlsx`, `.xls`, or `.csv`.

Identify:

- Sound ID column
- expected text column
- optional translated/original text column
- optional speaker column
- optional inclusion/exclusion flag

If both male and female rows are present, filter to the speaker represented by the supplied recording.

Preserve spreadsheet order exactly.

### Audio

Prefer `.mp3`, but `.wav`, `.m4a`, and other FFmpeg-readable formats are acceptable.

The recording is expected to contain items in spreadsheet order, typically separated by pauses.

---

## Default Audio Padding

Unless the user specifies otherwise:

- add **0.30 seconds before** each detected utterance;
- add **0.30 seconds after** each detected utterance.

Do not add padding beyond the start or end of the source recording.

---

## Segmentation Workflow

### Step 1 — Read the spreadsheet first

Before analyzing audio:

1. load the spreadsheet;
2. determine the exact set of rows expected in the recording;
3. count them;
4. store the ordered Sound ID list;
5. store the expected text for each Sound ID.

Example:

| Index | Sound ID | Expected text |
|---:|---|---|
| 1 | a3030000 | घर |
| 2 | a3030100 | यो मेरो घर हो। |
| 3 | a3030001 | कार |

If there are 73 relevant rows, set:

`expected_count = 73`

### Step 2 — Detect speech regions

Use silence detection or VAD to identify spoken regions.

Recommended approaches:

- FFmpeg `silencedetect`
- pydub silence detection
- WebRTC VAD / Silero VAD when available

Start with conservative silence detection suitable for deliberate recording pauses.

### Step 3 — Compare detected count with expected count

If:

`detected_count == expected_count`

continue to labeling, but still perform a sanity check.

If:

`detected_count < expected_count`

look for likely merged items by examining:

- short internal silences;
- unusually long speech segments;
- gaps shorter than the dominant inter-item pause;
- transitions around likely word/sentence boundaries.

Example:

The normal inter-item pause may be 3–5 seconds, but two consecutive items may have only 0.53 seconds between them. That gap should be considered as a possible missing boundary.

If:

`detected_count > expected_count`

look for false splits caused by:

- hesitations;
- pauses inside a sentence;
- retries;
- speaker corrections;
- long natural pauses.

### Step 4 — Reconcile counts before labeling

The final number of segments must equal the exact spreadsheet count.

Do not shift labels based on an unresolved mismatch.

### Step 5 — Add padding

For every final segment:

- subtract 0.30 s from start time;
- add 0.30 s to end time;
- clamp to source audio boundaries.

### Step 6 — Assign Sound IDs

Assign the ordered spreadsheet Sound IDs sequentially only after the segment count is resolved.

Filename format:

`<Sound ID>.mp3`

Example:

`a3030000.mp3`

---

## Text-vs-Audio QA

After segmentation and labeling, compare each audio clip against its expected text.

### Recommended transcription method

Use a multilingual ASR model when available, preferably:

- Whisper
- faster-whisper
- WhisperX

Use a model appropriate for the language and available compute.

Do not treat ASR output as ground truth.

ASR is a **QA signal**, not a replacement for human review.

### Comparison process

For each clip:

1. transcribe the audio;
2. normalize the expected text;
3. normalize the ASR transcript;
4. compare them;
5. assign a QA status.

Normalization may include:

- Unicode normalization;
- trimming punctuation;
- collapsing repeated spaces;
- case folding where appropriate;
- removing harmless punctuation differences.

Do **not** transliterate automatically unless the spreadsheet and ASR output use different scripts and the language-specific comparison method is reliable.

### QA statuses

Use these statuses:

#### PASS

Use when the transcription strongly matches the expected text.

#### REVIEW

Use when:

- the ASR transcript is similar but not clearly identical;
- one or two words appear different;
- the clip is very short;
- the ASR model is uncertain;
- the language has weak ASR support;
- pronunciation or inflection may explain the difference.

#### ERROR

Use only when there is strong evidence of a substantial mismatch, for example:

- completely different phrase;
- wrong sentence;
- wrong language;
- missing expected content;
- recording appears to belong to another row.

### Important QA principle

**Do not automatically mark a clip as wrong just because Whisper produced an imperfect transcript.**

For low-resource languages or very short words, prefer `REVIEW` over `ERROR` unless the mismatch is obvious.

---

## Suggested Similarity Heuristic

A lexical similarity score can be used as one signal.

Suggested default:

- `>= 0.88` → PASS
- `0.65–0.879` → REVIEW
- `< 0.65` → REVIEW or ERROR depending on ASR confidence and semantic difference

For single-word clips, similarity scores are less reliable. Use conservative flagging.

If ASR confidence is low, downgrade `ERROR` to `REVIEW`.

---

## QA Report

Create a CSV or XLSX report containing at least:

| Column | Description |
|---|---|
| Index | sequential item number |
| Sound ID | expected filename/label |
| Expected Text | spreadsheet reference text |
| ASR Transcript | what the model heard |
| Start Time | clip start in source audio |
| End Time | clip end in source audio |
| Duration | clip duration |
| Similarity | text similarity score |
| QA Status | PASS / REVIEW / ERROR |
| Notes | mismatch or segmentation notes |

Also include:

- expected row count;
- detected segment count before reconciliation;
- final exported file count;
- any manually resolved boundaries.

---

## Final Validation Checklist

Before presenting the result, verify all of the following:

- [ ] expected spreadsheet rows were identified correctly;
- [ ] speaker filtering is correct;
- [ ] final segment count equals expected row count;
- [ ] every expected Sound ID appears exactly once;
- [ ] no unexpected Sound IDs exist;
- [ ] no duplicate filenames exist;
- [ ] every output file is non-empty;
- [ ] all clips use the requested padding;
- [ ] text/audio QA has been run when transcription is available;
- [ ] REVIEW/ERROR items are clearly listed;
- [ ] ZIP file count is verified before delivery.

If the spreadsheet expects 73 items, explicitly verify that the ZIP contains **73 MP3 files**, not 72 MP3 files plus a report.

---

## Output

Create:

1. a ZIP containing only the labeled MP3 clips;
2. a separate QA report (`.csv` or `.xlsx`);
3. optionally a plain-text summary of flagged items.

Example:

`nepali_male_split_73_padding_0.3s.zip`

`nepali_male_audio_qa.csv`

---

## Failure Handling

If confident segmentation is impossible:

- do not fabricate a missing clip;
- do not duplicate a neighboring clip;
- do not silently shift all later labels;
- report the suspicious timestamp range;
- identify the Sound IDs likely involved;
- ask for manual review only for those ambiguous items.

The priority is correct labeling, not forcing an automatic answer.

---

## Definition of done

Pass conditions, all checkable without arguing:

1. The exported ZIP contains exactly `expected_count` MP3 files — one per relevant spreadsheet row, no more and no fewer.
2. Every Sound ID from the filtered spreadsheet appears exactly once as `<Sound ID>.mp3`. No duplicates, no unexpected IDs, and no non-MP3 files inside the ZIP.
3. Every clip is non-empty and carries the requested padding (default 0.30 s each side), clamped to the source boundaries.
4. The QA report has one row per clip, each with Sound ID, expected text, start, end, duration and a QA status of PASS, REVIEW or ERROR.
5. If the count could not be reconciled, no ZIP is delivered at all. The output is the flagged timestamp range and the Sound IDs involved.

**Golden example.**

Input: a spreadsheet with 73 rows for the male speaker (`a3030000`, `a3030100`, `a3030001`, ...) and one MP3 recorded in that order, items separated by 3–5 second pauses. Silence detection finds 73 regions.

Accepted output: `nepali_male_split_73_padding_0.3s.zip` containing exactly 73 MP3 files named for their Sound IDs, plus `nepali_male_audio_qa.csv` with 73 rows — 70 PASS, 3 REVIEW (single-word clips where ASR similarity fell to roughly 0.7), 0 ERROR — and a short summary listing only the 3 REVIEW items for a human to listen to.

**Adversarial case.**

The same sheet expects 73 rows, but silence detection returns 72 because two consecutive items are separated by only 0.53 seconds against a dominant 3–5 second pause, and the boundary cannot be placed confidently.

The skill must not export 72 files and call it done, must not duplicate a neighbouring clip or insert a silent one to make the count, and must not shift labels from the merged item onward. It reports the suspicious timestamp range, names the two Sound IDs likely merged there, and asks for manual review of those items only — delivering no ZIP until the count is resolved.
