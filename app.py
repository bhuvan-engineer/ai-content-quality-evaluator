
import pandas as pd
import streamlit as st

from prompts.templates import (
    build_prompts,
    LANGUAGE_LABELS,
    CONTENT_TYPES,
    PROMPT_STYLES,
)
from evaluation.heuristics import evaluate_content

st.set_page_config(
    page_title="AI Content Quality Evaluator",
    page_icon="🧪",
    layout="wide",
)

st.title("🧪 AI Content Quality Evaluation & Multilingual Prompt Testing")
st.caption(
    "Generate, inspect, and compare content in English, Hindi, and Hinglish."
)
st.info(
    "Demo mode is enabled. Outputs are sample content, not live AI-generated content. "
    "Quality scores are heuristic signals and do not guarantee factual accuracy."
)

# Demo mode: no API key or API credits required.
demo_mode = True


def make_demo_output(topic, language):
    """Return clearly labelled sample content for demonstration."""
    lang = str(language).lower()

    if "hinglish" in lang:
        sample = (
            f"Yeh {topic} ke baare mein ek demo sample hai. "
            "Final use se pehle details ko review aur verify karein."
        )
    elif "hindi" in lang:
        sample = (
            f"यह {topic} के बारे में एक डेमो नमूना है। "
            "इस्तेमाल करने से पहले सभी जानकारियों की जाँच करें।"
        )
    else:
        sample = (
            f"This is a demo sample about {topic}. "
            "Please review and verify all details before using it."
        )

    return (
        "[DEMO MODE — Sample content, not live AI output]\n\n"
        f"Topic: {topic}\n"
        f"Language: {language}\n\n"
        f"{sample}"
    )


def get_evaluation(output, content_type, length):
    """Run the project's existing rule-based evaluation."""
    return evaluate_content(
        output,
        content_type=content_type,
        expected_length=length,
    )


with st.sidebar:
    st.header("⚙️ Settings")
    st.success("Demo mode: Active")
    st.caption("No API credits are needed in demo mode.")
    model = st.text_input("Model label", value="gpt-4o-mini (demo)")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.4, 0.1)
    max_tokens = st.slider("Maximum response tokens", 100, 1500, 500, 50)

tab_generate, tab_compare, tab_about = st.tabs(
    ["✍️ Generate & Evaluate", "🌐 Multilingual Experiment", "ℹ️ About"]
)


# --------------------------------------------------
# TAB 1: GENERATE AND EVALUATE
# --------------------------------------------------
with tab_generate:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.subheader("Content settings")

        content_type = st.selectbox("Content type", CONTENT_TYPES)
        language = st.selectbox(
            "Output language",
            list(LANGUAGE_LABELS.keys()),
            format_func=lambda x: LANGUAGE_LABELS[x],
        )
        prompt_style = st.selectbox("Prompting technique", PROMPT_STYLES)
        tone = st.selectbox(
            "Tone",
            [
                "Professional",
                "Friendly",
                "Conversational",
                "Persuasive",
                "Academic",
                "Creative",
            ],
        )
        length = st.selectbox("Length", ["Short", "Medium", "Long"])

        topic = st.text_area(
            "Topic / brief",
            placeholder="Example: Invite students to a college theatre audition.",
            height=130,
        )
        audience = st.text_input(
            "Target audience (optional)",
            placeholder="Example: college students",
        )
        extra_instructions = st.text_area(
            "Additional instructions (optional)",
            placeholder="Example: Keep it simple and avoid exaggerated claims.",
            height=90,
        )

        generate_clicked = st.button(
            "Generate and evaluate",
            type="primary",
            use_container_width=True,
        )

    if generate_clicked:
        if not topic.strip():
            st.error("Please enter a topic or brief.")
        else:
            try:
                # Build the prompt using the project's prompt templates.
                system_prompt, user_prompt = build_prompts(
                    content_type=content_type,
                    language=language,
                    prompt_style=prompt_style,
                    tone=tone,
                    length=length,
                    audience=audience,
                    topic=topic,
                    extra_instructions=extra_instructions,
                )

                # Use sample content instead of making an API call.
                output = make_demo_output(topic, language)

                evaluation = get_evaluation(
                    output,
                    content_type,
                    length,
                )

                st.session_state["last_output"] = output
                st.session_state["last_evaluation"] = evaluation
                st.session_state["last_meta"] = {
                    "content_type": content_type,
                    "language": language,
                    "prompt_style": prompt_style,
                    "tone": tone,
                    "model": model,
                    "temperature": temperature,
                    "topic": topic,
                    "prompt_built": bool(system_prompt and user_prompt),
                    "demo_mode": demo_mode,
                }

            except Exception as exc:
                st.error(f"Could not process the content: {exc}")

    if st.session_state.get("last_output"):
        output = st.session_state["last_output"]
        evaluation = st.session_state["last_evaluation"]

        with right:
            st.subheader("Generated sample")
            st.text_area(
                "Output (editable)",
                value=output,
                height=260,
                key="editable_output",
            )

            st.download_button(
                "Download output as TXT",
                data=output,
                file_name="generated_content.txt",
                mime="text/plain",
            )

            st.subheader("Quality review")

            score_cols = st.columns(3)
            score_cols[0].metric(
                "Word count",
                evaluation.get("word_count", 0),
            )
            score_cols[1].metric(
                "Structure",
                evaluation.get("structure_label", "Not available"),
            )
            score_cols[2].metric(
                "Filler phrases",
                evaluation.get("filler_count", 0),
            )

            st.write("**Evaluation checks**")

            for item in evaluation.get("checks", []):
                status = "✅ " if item.get("passed") else "⚠️ "
                st.write(
                    status
                    + str(item.get("label", "Check"))
                    + " — "
                    + str(item.get("detail", ""))
                )

            st.warning(
                "Review names, dates, statistics, and other claims before publishing."
            )

            with st.expander("Show prompt configuration"):
                st.json(st.session_state.get("last_meta", {}))


# --------------------------------------------------
# TAB 2: MULTILINGUAL COMPARISON
# --------------------------------------------------
with tab_compare:
    st.subheader("Multilingual prompt experiment")

    st.write(
        "Compare sample outputs for English, Hindi, and Hinglish. "
        "This demo does not call a live AI model."
    )

    exp_topic = st.text_area(
        "Experiment topic",
        placeholder="Example: A college music event announcement.",
        key="exp_topic",
    )

    exp_type = st.selectbox(
        "Experiment content type",
        CONTENT_TYPES,
        key="exp_type",
    )

    exp_style = st.selectbox(
        "Experiment prompt technique",
        PROMPT_STYLES,
        key="exp_style",
    )

    exp_tone = st.selectbox(
        "Experiment tone",
        [
            "Professional",
            "Friendly",
            "Conversational",
            "Persuasive",
            "Academic",
            "Creative",
        ],
        key="exp_tone",
    )

    exp_length = st.selectbox(
        "Experiment length",
        ["Short", "Medium", "Long"],
        key="exp_length",
    )

    exp_audience = st.text_input(
        "Experiment audience (optional)",
        key="exp_audience",
    )

    run_experiment = st.button(
        "Run English + Hindi + Hinglish comparison",
        type="primary",
    )

    if run_experiment:
        if not exp_topic.strip():
            st.error("Enter an experiment topic first.")
        else:
            try:
                rows = []
                outputs = {}

                # Match available language keys by name.
                available_languages = list(LANGUAGE_LABELS.keys())
                selected_languages = []

                for wanted in ["english", "hindi", "hinglish"]:
                    match = next(
                        (
                            lang
                            for lang in available_languages
                            if wanted in str(lang).lower()
                            or wanted in str(LANGUAGE_LABELS[lang]).lower()
                        ),
                        None,
                    )

                    if match is not None and match not in selected_languages:
                        selected_languages.append(match)

                if not selected_languages:
                    st.error(
                        "Could not find English, Hindi, and Hinglish in "
                        "LANGUAGE_LABELS. Check prompts/templates.py."
                    )
                else:
                    for lang in selected_languages:
                        system_prompt, user_prompt = build_prompts(
                            content_type=exp_type,
                            language=lang,
                            prompt_style=exp_style,
                            tone=exp_tone,
                            length=exp_length,
                            audience=exp_audience,
                            topic=exp_topic,
                            extra_instructions="",
                        )

                        output = make_demo_output(
                            exp_topic,
                            LANGUAGE_LABELS[lang],
                        )

                        evaluation = get_evaluation(
                            output,
                            exp_type,
                            exp_length,
                        )

                        outputs[lang] = output

                        rows.append(
                            {
                                "Language": LANGUAGE_LABELS[lang],
                                "Content Type": exp_type,
                                "Prompt Technique": exp_style,
                                "Word Count": evaluation.get("word_count", 0),
                                "Structure": evaluation.get(
                                    "structure_label",
                                    "Not available",
                                ),
                                "Filler Phrases": evaluation.get(
                                    "filler_count",
                                    0,
                                ),
                                "Prompt Built": bool(
                                    system_prompt and user_prompt
                                ),
                                "Output": output,
                            }
                        )

                    st.session_state["experiment_rows"] = rows
                    st.session_state["experiment_outputs"] = outputs

            except Exception as exc:
                st.error(f"Could not run the experiment: {exc}")

    if st.session_state.get("experiment_rows"):
        df = pd.DataFrame(st.session_state["experiment_rows"])

        st.subheader("Comparison results")
        st.dataframe(
            df.drop(columns=["Output"]),
            use_container_width=True,
            hide_index=True,
        )

        for lang, output in st.session_state.get(
            "experiment_outputs", {}
        ).items():
            with st.expander(f"View {LANGUAGE_LABELS[lang]} sample"):
                st.text_area(
                    "Sample output",
                    value=output,
                    height=180,
                    key=f"comparison_output_{lang}",
                )

        csv_data = df.to_csv(index=False).encode("utf-8-sig")

        st.download_button(
            "Download experiment results (CSV)",
            data=csv_data,
            file_name="multilingual_experiment.csv",
            mime="text/csv",
        )

        st.caption(
            "These are demonstration samples, not a real model comparison. "
            "For research, use live outputs and human reviewers."
        )


# --------------------------------------------------
# TAB 3: ABOUT THE PROJECT
# --------------------------------------------------
with tab_about:
    st.subheader("Project overview")

    st.markdown("""
**Problem:** AI-generated content can vary in relevance, tone, structure,
fluency, and naturalness across languages.

**Approach:** This application uses prompt templates, content evaluation
rules, and a multilingual comparison workflow.

**Prompt techniques included:**
- **Zero-shot:** Instructions without examples.
- **Few-shot:** Examples to guide the requested format or style.
- **Role-based:** Assigns a role, such as a professional content writer.
- **Constraint-based:** Adds explicit requirements and restrictions.

**Evaluation signals:** Word count, basic structural markers, and common
filler phrases. These checks do not verify facts or guarantee content quality.

**Demo limitation:** Demo mode uses sample text instead of live AI generation.
The displayed evaluation scores apply to those samples.
""")
