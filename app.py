from dotenv import load_dotenv
load_dotenv()

import io
import pandas as pd
import streamlit as st
from prompts.templates import build_prompts, LANGUAGE_LABELS, CONTENT_TYPES, PROMPT_STYLES
from utils.openai_client import generate_content, get_api_key
from evaluation.heuristics import evaluate_content, compare_outputs

st.set_page_config(page_title="AI Content Quality Evaluator", page_icon="🧪", layout="wide")

st.title("🧪 AI Content Quality Evaluation & Multilingual Prompt Testing")
st.caption("Generate, inspect, and compare AI content in English, Hindi, and Hinglish.")
st.info("Quality scores are heuristic signals to support review. They do not guarantee factual accuracy, safety, or cultural appropriateness.")

with st.sidebar:
    st.header("⚙️ Settings")
    api_key_available = bool(get_api_key())
    st.write("API key status:", "✅ configured" if api_key_available else "⚠️ not configured")
    model = st.text_input("OpenAI model", value="gpt-4o-mini", help="Use a model available to your OpenAI API account.")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.4, 0.1)
    max_tokens = st.slider("Maximum response tokens", 100, 1500, 500, 50)
    st.caption("For deployment, add OPENAI_API_KEY under Streamlit Cloud → App settings → Secrets.")

tab_generate, tab_compare, tab_about = st.tabs(["✍️ Generate & Evaluate", "🌐 Multilingual Experiment", "ℹ️ About"])

with tab_generate:
    left, right = st.columns([1, 1], gap="large")
    with left:
        content_type = st.selectbox("Content type", CONTENT_TYPES)
        language = st.selectbox("Output language", list(LANGUAGE_LABELS.keys()), format_func=lambda x: LANGUAGE_LABELS[x])
        prompt_style = st.selectbox("Prompting technique", PROMPT_STYLES)
        tone = st.selectbox("Tone", ["Professional", "Friendly", "Conversational", "Persuasive", "Academic", "Creative"])
        length = st.selectbox("Length", ["Short", "Medium", "Long"])
        topic = st.text_area("Topic / brief", placeholder="Example: Invite students to a college theatre audition.", height=130)
        audience = st.text_input("Target audience (optional)", placeholder="Example: college students")
        extra_instructions = st.text_area("Additional instructions (optional)", placeholder="Example: Keep it simple and avoid exaggerated claims.", height=90)
        generate_clicked = st.button("Generate and evaluate", type="primary", use_container_width=True)

    if generate_clicked:
        if not topic.strip():
            st.error("Please enter a topic or brief.")
        else:
            try:
                system_prompt, user_prompt = build_prompts(
                    content_type=content_type, language=language, prompt_style=prompt_style,
                    tone=tone, length=length, audience=audience, topic=topic,
                    extra_instructions=extra_instructions
                )
                with st.spinner("Generating content with the selected model..."):
                    output = generate_content(
                        system_prompt=system_prompt, user_prompt=user_prompt,
                        model=model, temperature=temperature, max_tokens=max_tokens
                    )
                evaluation = evaluate_content(output, content_type=content_type, expected_length=length)
                st.session_state["last_output"] = output
                st.session_state["last_evaluation"] = evaluation
                st.session_state["last_meta"] = {
                    "content_type": content_type, "language": language,
                    "prompt_style": prompt_style, "tone": tone, "model": model,
                    "temperature": temperature, "topic": topic
                }
            except Exception as exc:
                st.error(f"Could not generate content: {exc}")
                st.caption("Check your API key, model access, internet connection, and API billing/limits.")

    if st.session_state.get("last_output"):
        output = st.session_state["last_output"]
        evaluation = st.session_state["last_evaluation"]
        with right:
            st.subheader("Generated content")
            st.text_area("Output (editable)", value=output, height=260, key="editable_output")
            st.download_button("Download output as TXT", data=output, file_name="generated_content.txt", mime="text/plain")
            st.subheader("Quality review")
            score_cols = st.columns(3)
            score_cols[0].metric("Length", evaluation["word_count"] and f'{evaluation["word_count"]} words' or "0 words")
            score_cols[1].metric("Structure", evaluation["structure_label"])
            score_cols[2].metric("Filler phrases", str(evaluation["filler_count"]))
            st.write("**Checks**")
            for item in evaluation["checks"]:
                st.write(("✅ " if item["passed"] else "⚠️ ") + item["label"] + " — " + item["detail"])
            st.warning("Review names, dates, statistics, legal/medical claims, and cultural context before publishing.")
            with st.expander("Show prompt configuration"):
                st.json(st.session_state.get("last_meta", {}))

with tab_compare:
    st.subheader("Run a small multilingual prompt experiment")
    st.write("Uses the same topic and settings for English, Hindi, and Hinglish. Each output is evaluated with the same lightweight checks.")
    exp_topic = st.text_area("Experiment topic", placeholder="Example: A short announcement for a college music event.", key="exp_topic")
    exp_type = st.selectbox("Experiment content type", CONTENT_TYPES, key="exp_type")
    exp_style = st.selectbox("Experiment prompt technique", PROMPT_STYLES, key="exp_style")
    exp_tone = st.selectbox("Experiment tone", ["Professional", "Friendly", "Conversational", "Persuasive", "Academic", "Creative"], key="exp_tone")
    exp_length = st.selectbox("Experiment length", ["Short", "Medium", "Long"], key="exp_length")
    exp_audience = st.text_input("Experiment audience (optional)", key="exp_audience")
    run_experiment = st.button("Run English + Hindi + Hinglish comparison", type="primary")
    if run_experiment:
        if not exp_topic.strip():
            st.error("Enter an experiment topic first.")
        else:
            rows = []
            outputs = {}
            try:
                for lang in LANGUAGE_LABELS:
                    sys_p, user_p = build_prompts(
                        content_type=exp_type, language=lang, prompt_style=exp_style,
                        tone=exp_tone, length=exp_length, audience=exp_audience,
                        topic=exp_topic, extra_instructions=""
                    )
                    with st.spinner(f"Generating {LANGUAGE_LABELS[lang]} output..."):
                        generated = generate_content(sys_p, user_p, model, temperature, max_tokens)
                    ev = evaluate_content(generated, exp_type, exp_length)
                    outputs[lang] = generated
                    rows.append({
                        "Language": LANGUAGE_LABELS[lang],
                        "Word count": ev["word_count"],
                        "Structure check": ev["structure_label"],
                        "Filler count": ev["filler_count"],
                        "Passed checks": sum(1 for x in ev["checks"] if x["passed"]),
                        "Total checks": len(ev["checks"]),
                        "Output": generated
                    })
                st.session_state["experiment_rows"] = rows
                st.session_state["experiment_outputs"] = outputs
            except Exception as exc:
                st.error(f"Experiment failed: {exc}")
                st.caption("Check your API key, model access, internet connection, and API billing/limits.")
    if st.session_state.get("experiment_rows"):
        df = pd.DataFrame(st.session_state["experiment_rows"])
        st.dataframe(df.drop(columns=["Output"]), use_container_width=True, hide_index=True)
        for lang, output in st.session_state.get("experiment_outputs", {}).items():
            with st.expander(f"View {LANGUAGE_LABELS[lang]} output"):
                st.write(output)
        csv_data = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button("Download experiment results (CSV)", data=csv_data, file_name="multilingual_experiment.csv", mime="text/csv")
        st.caption("For a proper study, repeat runs, rate samples with human reviewers, and document the scoring rubric. One run per language is only a quick comparison.")

with tab_about:
    st.subheader("Project overview")
    st.markdown("""
**Problem:** AI-generated content can vary in relevance, tone, structure, fluency, and naturalness across languages.

**Approach:** This application combines prompt templates, OpenAI-based content generation, lightweight rule-based checks, and a multilingual comparison workflow.

**Prompt techniques included:**
- **Zero-shot:** Gives instructions without examples.
- **Few-shot:** Includes a short example to guide format/style.
- **Role-based:** Assigns a role, such as a professional content writer.
- **Constraint-based:** Adds explicit requirements and things to avoid.

**Current evaluation signals:** word count, basic structural markers, and common filler phrases. These are not a trained evaluator and do not verify claims against reliable sources.

**Privacy:** The app does not intentionally store prompts or outputs in a database. Inputs are sent to the selected OpenAI model for generation. Do not submit confidential or sensitive information. Hosting providers may have their own logs and policies.
""")
    st.markdown("**Suggested next steps:** add a human rating rubric, test multiple runs per language, keep a record of model/version and settings, and compare human ratings with automated scores.")
