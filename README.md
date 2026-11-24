# SLM-Bench

**Landscape Lock-In, Device-Class Specification, and Cross-Platform Evaluation Harness for Small Language Models**

SLM-Bench is a Python 3.11 research prototype for recording reproducible local SLM inference trials. It provides host profiling, model/runtime registries, a fixed prompt dataset, SQLite persistence, comparison charts and CSV export. The built-in Demo backend is explicitly synthetic; use Ollama for real local inference measurements.

## Tested device scope

The target laptop is a Lenovo 83DL running Windows 11, with an Intel processor (12 physical cores, 14 logical cores), approximately 15.43 GB system RAM and Intel integrated graphics, as reported by the user. Host details are detected where possible and may differ slightly from those reported specifications. CPU inference is the primary benchmark target. The Ollama adapter requests CPU execution (`num_gpu: 0`); the harness does not independently verify runtime placement. Intel graphics detection is informational and does not imply Intel GPU acceleration. NVIDIA GPU benchmarking is outside the tested hardware scope; no RTX 3050 or other NVIDIA device is assumed. The profiler/runtime interfaces are modular for future NVIDIA, mobile and edge support.

## Windows quick start

Open PowerShell in the project folder. Python 3.11 is recommended (3.12 also works).

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

If script activation is blocked, skip activation and invoke `\.venv\Scripts\python.exe -m pip install -r requirements.txt` then `\.venv\Scripts\python.exe -m streamlit run app.py`.

To collect real measurements, install and start [Ollama](https://ollama.com/), pull a model (for example `ollama pull qwen2.5:1.5b`) and select Ollama in Benchmark Runner. The app never downloads models itself. If Ollama is absent, Demo mode still exercises the workflow and is labelled synthetic.

## Tests

```powershell
python -m pytest -q
```

## Pages

Overview, Device Profiler, Model Registry, Runtime Registry, Benchmark Runner, Results Comparison and Research Methodology. Runs are saved to `data/slmbench.db`; CSV export is available from results.

## Measurement caveats

See [docs/RESEARCH.md](docs/RESEARCH.md). TTFT is available for streamed Ollama output. Token counts are whitespace estimates, and memory is the dashboard process RSS rather than isolated model memory. Intel acceleration is not claimed unless a runtime supports and reports it. NVIDIA GPU benchmarking is outside the tested hardware scope. Demo measurements are not model performance results.
