from __future__ import annotations
import json, time
from datetime import datetime, timezone
import psutil
import pandas as pd
import plotly.express as px
import streamlit as st
from slmbench.device import detect_device
from slmbench.dataset import PROMPTS, score
from slmbench.runtimes import DemoAdapter, OllamaAdapter
from slmbench.storage import initialize, models, add_model, save_run, runs

st.set_page_config(page_title="SLM-Bench", page_icon="🧪", layout="wide")
initialize(); device=detect_device(); db="data/slmbench.db"
PAGES=["Overview","Device Profiler","Model Registry","Runtime Registry","Benchmark Runner","Results Comparison","Research Methodology"]
st.sidebar.title("SLM-Bench")
page=st.sidebar.radio("Research workspace",PAGES,key="page_navigation")
st.sidebar.caption("Landscape Lock-In · Device-Class Specification · Cross-Platform Evaluation")
st.sidebar.markdown("---")
st.sidebar.caption("CPU-first benchmark target · Demo data is synthetic")

def device_table():
    st.dataframe(pd.DataFrame([{"Property":k.replace('_',' ').title(),"Detected value":("N/A — no NVIDIA device reported by nvidia-smi" if k=="nvidia_gpu" and v=="N/A" else "N/A — NVIDIA VRAM unavailable" if k=="nvidia_vram_gb" and v is None else v)} for k,v in device.items()]),hide_index=True,use_container_width=True)
def display_runs(df):
    if df.empty: st.info("No benchmark runs yet. Start a run in Benchmark Runner."); return
    view=df.copy(); view["mode"]=view["mode"].map({"real":"REAL","synthetic":"SYNTHETIC"}).fillna(view["mode"])
    st.dataframe(view,hide_index=True,use_container_width=True)
    st.download_button("Download results CSV",view.to_csv(index=False).encode(),"slmbench_results.csv","text/csv",key="results_csv_download")

if page=="Overview":
    st.title("Small Language Model Evaluation")
    st.caption("A reproducible, device-aware harness for comparing local SLM inference.")
    df=runs(db)
    a,b,c,d=st.columns(4); a.metric("Saved trials",len(df)); b.metric("Registered models",len(models(db))); c.metric("Host RAM",f"{device['ram_gb']} GB"); d.metric("Primary target","CPU")
    st.subheader("Recent benchmark activity"); display_runs(df.head(20))
    st.info("Demo backend results are synthetic. They validate the workflow and scoring path; do not cite them as model performance.")
elif page=="Device Profiler":
    st.title("Device Profiler"); st.write("Test host: Lenovo 83DL, Windows 11, Intel CPU with 12 physical / 14 logical cores and about 15.43 GB RAM (user-reported). Runtime detection is best-effort. CPU inference is the primary benchmark target; Intel graphics detection does not imply inference acceleration."); device_table()
    st.info("NVIDIA GPU benchmarking is outside this prototype's tested hardware scope. NVIDIA fields are reported only if the host's NVIDIA tooling detects a device.")
    st.caption(f"Process RSS currently: {psutil.Process().memory_info().rss/1024**2:.1f} MB (dashboard process, not a model runtime).")
elif page=="Model Registry":
    st.title("Model Registry"); st.dataframe(models(db),hide_index=True,use_container_width=True)
    with st.form("new_model"):
        st.subheader("Register a model"); name=st.text_input("Model name",key="model_name_input"); cols=st.columns(3); family=cols[0].text_input("Family",key="model_family_input"); size=cols[1].text_input("Parameter size",key="model_parameter_size_input"); fmt=cols[2].text_input("Model format",key="model_format_input"); cols2=st.columns(2); quant=cols2[0].text_input("Quantization",key="model_quantization_input"); source=cols2[1].text_input("Source",key="model_source_input"); submitted=st.form_submit_button("Add model",key="model_add_submit")
        if submitted:
            if not name.strip(): st.error("Model name is required.")
            else:
                try: add_model((name.strip(),family or "Unspecified",size or "Unspecified",fmt or "Unspecified",quant or "Unspecified",source or "Unspecified"),db); st.success("Model added."); st.rerun()
                except Exception as e: st.error(f"Could not add model: {e}")
elif page=="Runtime Registry":
    st.title("Runtime Registry"); ollama=OllamaAdapter(); ok,msg=ollama.available()
    rows=[{"Runtime":"Ollama","Mode":"REAL","Availability":"Available" if ok else "Unavailable","Details":msg},{"Runtime":"Demo (synthetic)","Mode":"SYNTHETIC","Availability":"Always available","Details":"Deterministic canned responses and illustrative timings; never real model performance."}]
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    if ok:
        st.subheader("Ollama models detected"); found=ollama.models(); st.write(found if found else "No models installed in Ollama.")
    st.caption("Ollama streaming provides first-chunk time as TTFT; tokens are whitespace-count estimates from returned text.")
elif page=="Benchmark Runner":
    st.title("Benchmark Runner"); st.caption("Each prompt trial is persisted separately with its device, configuration and execution mode.")
    registry=models(db); labels=registry.name.tolist(); runtime_choice=st.selectbox("Runtime",["Demo (synthetic)","Ollama (real)"],key="benchmark_runtime"); adapter=DemoAdapter() if runtime_choice.startswith("Demo") else OllamaAdapter()
    if adapter.mode=="real":
        available,msg=adapter.available()
        if available:
            st.success(msg)
        else:
            st.error(f"Ollama unavailable: {msg}")
        ollama_models=adapter.models() if available else []
        if not ollama_models: st.warning("Install/start Ollama and pull a model to run real measurements.")
        model_name=st.selectbox("Ollama model",ollama_models,key="ollama_model_select") if ollama_models else ""
    else: model_name=st.selectbox("Model",labels,key="registry_model_select")
    categories=sorted({p["category"] for p in PROMPTS})
    selected_categories=st.multiselect("Prompt categories",categories,default=categories,key="benchmark_prompt_categories")
    selected=[p for p in PROMPTS if p["category"] in selected_categories]
    trials=st.number_input("Repeated measured trials per prompt",min_value=1,max_value=10,value=2,key="benchmark_trial_count"); warmups=st.number_input("Warm-up requests per prompt",min_value=0,max_value=3,value=1,key="benchmark_warmup_count"); max_tokens=st.slider("Maximum generated tokens",8,256,64,key="benchmark_max_tokens"); execution=st.selectbox("Execution mode",["single-user / sequential","interactive local"],key="benchmark_execution_mode")
    if st.button("Run benchmark",type="primary",disabled=not selected or (adapter.mode=="real" and not model_name),key="benchmark_run_button"):
        bar=st.progress(0); status=st.empty(); proc=psutil.Process(); total=len(selected)*(int(trials)+int(warmups)); done=0; errors=0
        config={"warmups":int(warmups),"repeated_trials":int(trials),"max_tokens":int(max_tokens),"execution_mode":execution,"prompt_count":len(selected),"primary_inference_target":"CPU","ollama_num_gpu":0 if adapter.mode=="real" else None,"actual_device_placement":"Not independently reported by this runtime adapter"}
        for prompt in selected:
            for i in range(int(warmups)+int(trials)):
                status.write(f"{prompt['id']} · {'warm-up' if i<int(warmups) else 'trial'} {max(1,i-int(warmups)+1)} / {trials}")
                outcome=adapter.generate(model_name,prompt["prompt"],int(max_tokens))
                done+=1; bar.progress(done/total)
                if i<int(warmups): continue
                errors+=bool(outcome["error"])
                row={"created_at":datetime.now(timezone.utc).isoformat(),"model":model_name,"runtime":adapter.name,"mode":adapter.mode,"device_json":json.dumps(device),"config_json":json.dumps(config),"execution_mode":execution,"prompt_id":prompt["id"],"category":prompt["category"],"prompt":prompt["prompt"],"expected":prompt["expected"],"answer":outcome["text"],"ttft_s":outcome["ttft_s"],"latency_s":outcome["latency_s"],"generated_tokens":outcome["tokens"],"tokens_per_second":outcome["tps"],"process_memory_mb":round(proc.memory_info().rss/1024**2,2) if adapter.mode=="real" else None,"quality_pass":score(outcome["text"],prompt["expected"],prompt["rule"]),"error":outcome["error"]}
                save_run(row,db)
        status.success(f"Finished: {len(selected)*int(trials)} measured trials saved; {errors} errors. Mode: {adapter.mode.upper()}.")
        st.rerun()
    st.subheader("Dataset preview"); st.dataframe(pd.DataFrame(PROMPTS),hide_index=True,use_container_width=True)
elif page=="Results Comparison":
    st.title("Results Comparison"); df=runs(db); display_runs(df)
    if not df.empty:
        numeric=df[df.error.isna()]
        if not numeric.empty:
            st.subheader("Latency by model and runtime"); agg=numeric.groupby(["model","runtime","mode"],as_index=False).agg(latency_s=("latency_s","mean"),tokens_per_second=("tokens_per_second","mean"),trials=("id","count"))
            st.plotly_chart(px.bar(agg,x="model",y="latency_s",color="runtime",barmode="group",hover_data=["mode","trials"],title="Mean end-to-end latency (seconds)"),use_container_width=True)
            st.plotly_chart(px.scatter(numeric,x="latency_s",y="tokens_per_second",color="mode",symbol="runtime",hover_data=["model","prompt_id"],title="Latency vs throughput"),use_container_width=True)
        quality=df[df.quality_pass.notna()]
        if not quality.empty:
            st.subheader("Scored subset (defined rules only)"); q=quality.groupby(["model","runtime","mode"],as_index=False).agg(accuracy=("quality_pass","mean"),scored_trials=("id","count")); st.dataframe(q,hide_index=True,use_container_width=True)
        st.caption("Token counts use whitespace splitting; report tokenizer-specific counts separately when available. N/A fields are not imputed.")
elif page=="Research Methodology":
    st.title("Research Methodology")
    st.markdown("""
### Research question
How do device class and runtime configuration shape small language model latency and practical usability, and how can device-specific measurement practices create landscape lock-in?

### Protocol
1. Record host CPU, RAM, OS, architecture and graphics devices when discoverable. The current tested host is a user-reported Lenovo 83DL with Intel CPU (12 physical / 14 logical cores), about 15.43 GB RAM, Intel integrated graphics and Windows 11; detected values may vary with available OS APIs.
2. Register exact model identity, family, parameter size, format, quantization and source before comparing runs.
3. Use the fixed prompt set and report runtime, model, device snapshot, configuration, execution mode and UTC timestamp for every measured trial.
4. Exclude warm-ups from saved measurements. Repeat each prompt, preserve errors, and report distributions or per-trial values rather than treating one run as definitive.
5. Score only prompts with explicit expected answers and rules. The current exact and contains checks are narrow harness checks, not broad capability evaluations.
6. Label Ollama observations as real measurements. Demo backend metrics and answers are synthetic workflow checks and must never be represented as model results.

### Metric definitions and limitations
- **TTFT:** request start to first streamed response chunk; unavailable when a runtime cannot expose streaming.
- **End-to-end latency:** wall time around the generation request, seconds.
- **Generated tokens / throughput:** whitespace-token estimate and estimate divided by latency; not tokenizer-exact.
- **Process memory:** dashboard process RSS snapshot, only reported for real mode; it is not isolated model memory and must not be compared as model footprint.
- **GPU/mobile/edge/accuracy:** N/A unless actually detected or supported by a ground-truth scoring rule. This prototype does not simulate these measurements.
- **Hardware scope:** CPU inference is the primary benchmark target. NVIDIA GPU benchmarking is outside the tested hardware scope. Intel graphics may be identified from Windows, but acceleration is not claimed unless a runtime itself supports and reports it. Future NVIDIA, mobile and edge adapters should implement the same runtime/device interfaces and provide their own evidence.

### Reproducibility
Keep model/runtime versions, prompt set, sampling settings, hardware, warm-up count and trial count fixed or record changes. Export CSV alongside the SQLite database. Avoid cross-device claims from unbalanced, asynchronous, thermally uncontrolled runs. See `docs/RESEARCH.md` for the expanded protocol and threats to validity.
""")
