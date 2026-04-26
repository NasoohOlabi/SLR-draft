from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
XLSX_PATH = ROOT / "SLR.xlsx"
CSV_PATH = ROOT / "data" / "SLR - SLR-Deep.csv"
SHEET_NAME = "SLR-Deep"


NEW_PAPERS = [
    {
        "#": 43,
        "title": "A Contrastive Semantic Watermarking Framework for Large Language Models",
        "Year": 2025,
        "Type": "Watermarking",
        "input": "generated-text",
        "LLM": "GPT-2, OPT-1.3B, LLaMA-7B",
        "Category": "Contrastive",
        "Main strengths": "Keyless semantic watermarking with strong black-box robustness and high detection F1 under rewriting and token substitution.",
        "Main weaknesses": "Focused on attribution rather than covert payload transmission; robustness claims depend on detector quality and added detection infrastructure.",
        "dataset": "C4; DBpedia",
        "ER": "",
        "eval": "F1, PPL, z-score detection, robustness under rewriting/substitution/compression, runtime",
        "result": "Reports up to 99.9% F1 and >=93% F1 under several perturbation settings.",
        "code available": "",
        "pipline method used": "Contrastive semantic token selection plus shared embedding alignment with statistical and GRU-based detection.",
        "context aware": "Implicit",
        "categ context": "Semantic context",
        "representation context": "Embedding",
        "context usage in method detail text": "Uses semantic embeddings of the generated context to choose watermark-compatible tokens while preserving fluency.",
    },
    {
        "#": 44,
        "title": "DeepStego: Privacy-Preserving Natural Language Steganography Using Large Language Models and Advanced Neural Architectures",
        "Year": 2025,
        "Type": "Steganography",
        "input": "prompt/topic-guided text",
        "LLM": "GPT-4-omni",
        "Category": "Prompt-based",
        "Main strengths": "Uses LLM-guided synonym generation and semantic-aware embedding to improve naturalness, capacity, and resistance to steganalysis.",
        "Main weaknesses": "Relies on proprietary API access and prompt engineering; reproducibility and cost may be limiting factors.",
        "dataset": "Synthetic prompts/topics; curated topic list",
        "ER": "",
        "eval": "Detection rate, embedding capacity, semantic preservation, text quality",
        "result": "Paper reports lower detection rates than comparison methods while supporting higher embedding capacity.",
        "code available": "",
        "pipline method used": "GPT-4-omni prompt-based text generation with dynamic synonym substitution and semantic-aware bit embedding.",
        "context aware": "Explicit",
        "categ context": "Topic",
        "representation context": "Prompt text",
        "context usage in method detail text": "Topic prompts constrain generation and guide synonym choices so the stegotext remains semantically coherent.",
    },
    {
        "#": 45,
        "title": "Emotionally Controllable Text Steganography Based on Large Language Model and Named Entity",
        "Year": 2025,
        "Type": "Steganography",
        "input": "context-centered text",
        "LLM": "Large language model with named-entity and sentiment modules",
        "Category": "Context-aware",
        "Main strengths": "Adds named-entity and sentiment control to improve contextual relevance and emotional consistency while increasing hiding capacity.",
        "Main weaknesses": "Method quality depends on auxiliary NER and sentiment modules, and the paper gives limited detail about the underlying LLM choice.",
        "dataset": "IMDB",
        "ER": "",
        "eval": "Hiding capacity, perplexity, security, context relevance",
        "result": "Authors report improvements over mainstream baselines in capacity, perplexity, and security.",
        "code available": "",
        "pipline method used": "LLM generation constrained by named-entity extraction and sentiment analysis before secret embedding.",
        "context aware": "Explicit",
        "categ context": "Named entity and emotion",
        "representation context": "Text labels",
        "context usage in method detail text": "Named entities anchor topic context and sentiment analysis steers emotional tone during stegotext generation.",
    },
    {
        "#": 46,
        "title": "Enhancement of the Generation Quality of Generative Linguistic Steganographic Texts by a Character-Based Diffusion Embedding Algorithm (CDEA)",
        "Year": 2025,
        "Type": "Steganography",
        "input": "control-text",
        "LLM": "XLNet",
        "Category": "sampling",
        "Main strengths": "Improves word candidate balancing during generation and targets better semantic consistency and fluency in generative stegotext.",
        "Main weaknesses": "Main contribution is embedding optimization rather than broader context control, and it still inherits generative-model quality limits.",
        "dataset": "",
        "ER": "",
        "eval": "Imperceptibility, semantic consistency, fluency, embedding quality",
        "result": "Paper reports better generation quality than prior embedding algorithms by prioritizing high-probability candidates.",
        "code available": "",
        "pipline method used": "Character-level diffusion-based candidate grouping combined with generative linguistic steganography.",
        "context aware": "No",
        "categ context": "",
        "representation context": "",
        "context usage in method detail text": "No explicit external context modeling; the method focuses on candidate selection during generation.",
    },
    {
        "#": 47,
        "title": "Multi-criteria linguistic optimization for covert communication in secure LLM-based steganography",
        "Year": 2025,
        "Type": "Steganography",
        "input": "prompt-guided text",
        "LLM": "gpt-4o, gpt-4o-mini, o3-mini, claude-3.7",
        "Category": "Prompt-based",
        "Main strengths": "Encodes bits through stylistic features with history-aware optimization, preserving fluency while achieving reliable decoding.",
        "Main weaknesses": "Requires repeated candidate generation and rejection sampling, which increases compute cost and may limit throughput.",
        "dataset": "Multiple text genres and prompt contexts",
        "ER": "",
        "eval": "Bits per token, perplexity, lexical diversity, readability, linguistic acceptability, decoding accuracy",
        "result": "Reports up to 0.30 bits/token with zero decoding error under ideal conditions.",
        "code available": "",
        "pipline method used": "Prompted candidate generation, stylistic feature mapping, history-aware optimization, and rejection sampling.",
        "context aware": "Explicit",
        "categ context": "Prompt and style history",
        "representation context": "Prompt text and feature vectors",
        "context usage in method detail text": "Uses prompt context plus prior stylistic history to choose feature vectors that keep sentence transitions natural.",
    },
    {
        "#": 48,
        "title": "Position-Agnostic Probabilistic Generation for Robust Steganographic Text",
        "Year": 2025,
        "Type": "Steganography",
        "input": "control-text",
        "LLM": "GPT-2",
        "Category": "sampling",
        "Main strengths": "Improves robustness against text perturbations by avoiding fixed token positions and using semantically coherent token clusters.",
        "Main weaknesses": "Primarily validated on GPT-2-based generation and robustness comes with extra decoding-time control complexity.",
        "dataset": "IMDB",
        "ER": "",
        "eval": "Robustness under perturbations, KLD, quality metrics, embedding efficiency",
        "result": "Outperforms baselines across ten perturbation types while preserving hidden information more reliably.",
        "code available": "",
        "pipline method used": "Semantic clustering with time-aware probability boosting during autoregressive generation.",
        "context aware": "Implicit",
        "categ context": "Semantic context",
        "representation context": "Token clusters",
        "context usage in method detail text": "Semantic token clusters provide soft context constraints for robust bit embedding without position locking.",
    },
    {
        "#": 49,
        "title": "Promising Multi-Granularity Linguistic Steganography by Jointing Syntactic and Lexical Manipulations",
        "Year": 2025,
        "Type": "Steganography",
        "input": "cover-text",
        "LLM": "Paraphrase generation model plus BERT",
        "Category": "Modification",
        "Main strengths": "Combines syntactic paraphrasing with lexical substitution to improve embedding capacity, semantic coherence, and naturalness.",
        "Main weaknesses": "Depends on an existing cover sentence and on paraphrase quality; errors in either stage can affect secrecy and fluency.",
        "dataset": "",
        "ER": "",
        "eval": "Semantic coherence, embedding capacity, security",
        "result": "Authors report better semantic coherence, embedding capacity, and security than prior modification-based methods.",
        "code available": "github",
        "pipline method used": "Paraphrase generation for syntactic embedding followed by BERT-based synonym substitution for lexical embedding.",
        "context aware": "Implicit",
        "categ context": "Sentence semantics",
        "representation context": "Cover text",
        "context usage in method detail text": "Preserves the source sentence meaning while distributing bits across syntactic and lexical manipulation spaces.",
    },
    {
        "#": 50,
        "title": "Research on Making Two Models Based on the Generative Linguistic Steganography for Securing Linguistic Steganographic Texts from Active Attacks",
        "Year": 2025,
        "Type": "Steganography",
        "input": "control-text",
        "LLM": "Generative linguistic steganography model",
        "Category": "Robustness",
        "Main strengths": "Targets active attacks directly with explicit attack models and repair strategies for tampered stegotext.",
        "Main weaknesses": "Defense against synonym-substitution attacks is computationally expensive and the approach emphasizes robustness over efficiency.",
        "dataset": "",
        "ER": "",
        "eval": "Attack resistance, decoding integrity, robustness under tampering",
        "result": "Paper reports substantial improvements in hidden-message integrity against ISSA and random tampering attacks.",
        "code available": "",
        "pipline method used": "Generative steganography with attack modeling, adaptive clustering defense, and post-hoc repair mechanisms.",
        "context aware": "Implicit",
        "categ context": "Generation context",
        "representation context": "Generated text",
        "context usage in method detail text": "Uses the determinism and local generation context of the stegosystem to repair or defend against text tampering.",
    },
]


def main() -> None:
    df = pd.read_excel(XLSX_PATH, sheet_name=SHEET_NAME)
    existing_titles = set(df["title"].fillna("").str.strip())

    additions = [paper for paper in NEW_PAPERS if paper["title"] not in existing_titles]
    if not additions:
        print("No new papers to add.")
        return

    additions_df = pd.DataFrame(additions, columns=df.columns)
    updated_df = pd.concat([df, additions_df], ignore_index=True)
    updated_df.to_excel(XLSX_PATH, sheet_name=SHEET_NAME, index=False)
    updated_df.to_csv(CSV_PATH, index=False, encoding="utf-8-sig")

    print(f"Added {len(additions)} papers.")
    print(updated_df[["#", "title", "Year", "Type"]].tail(len(additions)).to_string(index=False))


if __name__ == "__main__":
    main()
