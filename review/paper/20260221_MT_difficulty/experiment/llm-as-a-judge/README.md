# Workflow Description: LLM-as-a-Judge
## 1. generate_sample.py
- llama estimates machine translation difficulty (using vLLM) and creates csv files

## 2. (not committed) llama-3.1-8b-instruct_{source/target}_based_num_scores.csv
- csv files includes:
    - estimated scores
    - original datas
    - raw outputs
- datas in csv files are at:
    - https://huggingface.co/datasets/HUFS-DILAB/reproduce-MT-llama-target. 
    - https://huggingface.co/datasets/HUFS-DILAB/reproduce-MT-llama-source

## 3. eval_llama_dec.py
- calculates DEC scores from estimated scores and human annotations (ESA)

# Final Results
## In this experiment
| mode | DEC score |
| :--- | :--- |
| Llama 3.1 8B (src-based) | 0.091 |
| Llama 3.1 8B (tgt-based) | 0.093 |

## In the paper
| mode | DEC score |
| :--- | :--- |
| Command A (src-based) | 0.072 |
| Command A (tgt-based) | 0.104 |
| GPT-4o (src-based) | 0.077 |
| GPT-4o (tgt-based) | 0.080 |

## What makes the final results different from the original?
- only prompts were provided from the authors (no codes)
- llm models are different


