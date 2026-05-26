# Klook × HUFS LAI 2026
**AI Prompt Optimization Collaborative Project**

---

## Overview

This project was conducted as an industry-academia collaboration between the **College of AI Convergence at Hankuk University of Foreign Studies (HUFS)** and **Klook** during the Spring 2026 semester.

- Covered the **Singapore** and **Europe** regions
- Selected as an **outstanding participant**, awarded a ₩50,000 Klook gift card
- Contributed to the final team presentation through data analysis, experiment design and execution, and delivery

**Resources**
- [Final Presentation Slides](https://docs.google.com/presentation/d/1QC-lOZidIhoMwaKCdq-G8iTRlcfoaN54o4dZfujGsxk/edit?usp=sharing)
- [Dataset on Hugging Face](https://huggingface.co/datasets/jsjang0104/klook_data_group6_2026-1)

---

## Purpose

**Klook**
- Identify AI translation issues at scale
- Collect well-crafted and optimized AI prompts
- Apply collected prompts to drive real impact for a better customer experience

**Students**
- Acquire practical skills in content quality management and effective AI utilization
- Develop the ability to design and refine prompts
- Enhance understanding of AI-driven translation workflows

---

## Workflow

1. **Proofreading** — Identify AI translation errors by comparing EN and KR pages
2. **Analyzing** — Define error categories and assess severity
3. **Prompt Engineering** — Develop prompts to address identified errors
4. **Evaluation** — Verify error resolution and assess quality using BLEURT scores
5. **Re-engineering** — Iterate and optimize prompts for better outcomes

---

## Repository Structure

| File | Description |
|------|-------------|
| `klook_data.json` | Annotated dataset of AI-translated Klook listings with error labels, translations, references, and QE scores |
| `qe_bleurt.py` | Computes BLEURT scores by comparing `tgt` against `ref` using `Elron/bleurt-large-512` |
| `qe_cometkiwi.py` | Computes reference-free QE scores using `Unbabel/wmt23-cometkiwi-da-xl` on `(src, tgt)` pairs |
| `qe_qwen_judge.py` | LLM-as-a-judge scoring using `Qwen/Qwen3-32B`; outputs normalized 0–1 scores |

