# Research protocol and threats to validity

## Aim
Study how device class, runtime choices, model packaging and quantization shape SLM performance, and how evaluation tied to a narrow hardware/runtime landscape can lock out other device classes.

## Tested hardware scope
The present target is a Lenovo 83DL laptop running Windows 11, with an Intel processor (12 physical cores and 14 logical cores), approximately 15.43 GB system RAM and Intel integrated graphics, based on user-provided device specifications. The profiler also collects runtime host values and may show slight differences. CPU inference is the primary benchmark target. The Ollama adapter requests `num_gpu: 0`; this setting is recorded in run configuration, but the prototype does not independently verify actual runtime placement. Detecting Intel graphics from Windows is device inventory only and is not evidence of Intel GPU acceleration. NVIDIA GPU benchmarking is outside the tested hardware scope. No NVIDIA RTX 3050 or other NVIDIA device is assumed. Keep future NVIDIA, mobile and edge support modular through separate profiler fields and runtime adapters, and validate each on actual hardware before making performance claims.

## Minimum run record
Every measured trial records UTC timestamp, model identity, runtime, execution mode, host device snapshot, configuration, prompt identifier/category/text, response, TTFT (if exposed), end-to-end latency, generated-token estimate, estimated throughput, process memory (when meaningful), quality result (only for defined rules), and error.

## Recommended protocol
1. Record exact host and model/runtime version details; preserve model source and quantization metadata.
2. Fix prompt set, generation options, concurrency and power/thermal conditions across comparisons.
3. Run warm-ups, then at least five measured repeats per prompt for exploratory comparisons. Keep each trial and summarize median, spread and failures.
4. Randomize model order when practical; note background load and device power state.
5. Compare within device classes first. Cross-class claims require matched conditions and explicit limitations.
6. Treat exact/contains prompt checks as narrow behavioral checks; add validated datasets and scoring before broader quality claims.

## Metric limitations
Ollama TTFT is first streamed content arrival, not necessarily model-internal first-token time. Whitespace token counts differ from model tokenizer counts. Dashboard RSS includes Streamlit and Python and is not model-only memory. Windows Intel graphics discovery is best-effort and says nothing about runtime acceleration. NVIDIA GPU benchmarking is outside this prototype's tested hardware scope; optional NVIDIA inventory does not mean NVIDIA measurements were validated. Mobile/edge platforms require their own instrumentation and must not be inferred from a desktop profile. Demo values are synthetic and excluded from real performance claims.

## Threats to validity
Thermal throttling, process contention, runtime versions, model cache state, tokenizer differences, prompt adherence, sampling settings and asynchronous system load affect results. Small prompt sets and heuristic answer scoring do not establish general model quality. Runs from this prototype support exploratory engineering comparisons, not universal rankings.
