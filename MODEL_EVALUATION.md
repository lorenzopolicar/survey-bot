# Model Evaluation Strategy

This project may switch to different language models in the future. To ensure quality remains acceptable we propose the following evaluation approach.

1. **Benchmark Questions** – Maintain a set of sample surveys with known high quality answers. These will be used as regression tests when changing the LLM backend.
2. **Automated Comparison** – For each candidate model run the benchmark surveys, collecting the generated scores and bot responses. A script compares these to results from the reference model (e.g. GPT-4) and reports differences.
3. **LLM-Based Judging** – Use an inexpensive model to act as a judge. Provide it the question, expected guidlines, and pairs of answers from two models. Ask which answer better follows the guidlines. This helps quantify quality differences without human evaluation of every case.
4. **Cost vs Quality Reports** – Generate a report with aggregate scoring statistics and estimated API costs for each model. Stakeholders can use this data to decide if the cheaper model is acceptable.

## Testing

Tests can run on CI to exercise scoring, database storage and conversation flow. We keep transcripts produced by different models and assert that scoring stays within an acceptable range. When switching models the benchmark script should be rerun and its results reviewed.
