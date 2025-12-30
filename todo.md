# To-Do List: Writing Enhancements for the SLR Draft

This action plan focuses on refining the narrative, deepening the analysis, and ensuring the academic rigor and clarity of your systematic literature review.

---

- [ ] **High Priority: Foundational & Credibility Enhancements**

- [ ] 1.  **Systematically Complete All Citations:**
  - **Issue:** Numerous placeholder citations (`[?]`, `openai2023gpt4`) and missing citations for foundational concepts, specific models, metrics, and challenges.
  - **Suggestion:** Go through the entire document and replace every `[?]` and `openai2023gpt4` with the correct, specific citation from the provided research material (e.g.[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44]). Ensure consistent citation style throughout.
  - **Impact:** Crucial for academic credibility, proper attribution, and directly addresses the explicit request for citation gaps.

- [ ] 2.  **Transform Methodological Sections (3, 4, 5) from Template to Narrative:**
  - **Issue:** These sections currently read as internal instructions or incomplete templates (e.g., "Briefly note if snowballing was used for additional sources.", "Categories: Describe the approach using exactly three terms.").
  - **Suggestion:** Rewrite these sections to narrate *how* the systematic literature review was actually conducted. Describe the rationale behind the search query, the specific digital libraries used, the detailed steps of multi-stage filtering, how duplicate removal and snowballing were performed, and the process for data extraction and classification, including how consistency was ensured.
  - **Impact:** Essential for reproducibility, transparency, and demonstrating the rigor of your review process. This significantly elevates the paper's academic quality.

- [ ] 3.  **Deepen Analytical Discussion in "Results and Discussion" (Section 6):**
  - **Issue:** This section currently provides high-level summaries without explicitly linking findings to the data presented in Tables 1, 2, and 3.
  - **Suggestion:** For each subsection in Section 6, directly refer to and interpret the data in the tables. For example, when discussing LLM prevalence, analyze trends from Table 2; when discussing evaluation metrics, interpret the range of PPL values from Table 1 and acknowledge the limitations of cross-model comparisons as noted in the research material.[45]
  - **Impact:** Transforms the section from a summary into a data-driven analysis, directly addressing the research questions with empirical evidence and providing a more nuanced understanding of the field.

- [ ] 4.  **Refine Abstract's "Paradigm Shift" Claim:**
  - **Issue:** The abstract states a "paradigm shift towards context-aware steganographic systems," but Table 3 indicates many reviewed papers are "non-explicit" or "No" regarding context awareness.
  - **Suggestion:** Temper this claim in the abstract and in Section 6.4. Rephrase it as an "emerging trend" or "promising direction" that is still evolving, acknowledging the current prevalence of non-explicit context-awareness while highlighting the advancements.
  - **Impact:** Ensures accuracy and avoids overstatement, aligning the abstract's claims precisely with the evidence presented in the body of the review.

---

- [ ] **Medium Priority: Content Depth & Cohesion**

- [ ] 5.  **Expand "Key Terminology and Definitions" (Section 1.4):**
  - **Issue:** Definitions are clear but could be deeper, especially for complex terms like "Hallucinations (in LLMs)."
  - **Suggestion:** For terms like "Hallucinations," expand on the *types* (e.g., intrinsic vs. extrinsic, factual vs. semantic) and *causes* (e.g., training data, model architecture, decoding strategies).[31] Crucially, explain *why* these pose specific problems for steganography (e.g., introducing detectable patterns, compromising message integrity).[29]
  - **Impact:** Provides a more comprehensive understanding of key concepts and their direct implications within the context of LLM-based steganography.

- [ ] 6.  **Elaborate on "Role in Generative Linguistic Steganography" (Section 2.2):**
  - **Issue:** This section identifies methods but could better explain *how* LLM capabilities translate into their favorability for steganography.
  - **Suggestion:** Explicitly articulate how LLMs' ability to "approximate high-dimensional distributions" and produce "indistinguishable from human writing" text enables enhanced imperceptibility and naturalness.[43] For each method (LLM-Stega, Co-Stega, Zero-shot, ALiSa), provide a brief, clear description of its core mechanism, drawing directly from the cited sources.[10, 11, 12, 13, 15]
  - **Impact:** Deepens the explanation of LLMs' fundamental advantages and clarifies the mechanisms of different steganographic approaches.

- [ ] 7.  **Enhance "Evaluation Metrics" (Section 2.3.1):**
  - **Issue:** Metrics are listed but lack explanation of their purpose and relevance in steganography, and a critical limitation is missing.
  - **Suggestion:** Briefly explain each metric's purpose (e.g., PPL for naturalness [19], Distinct-n for diversity [20], MAUVE for statistical gap [21]). Crucially, add a discussion about the limitation that PPL and JSD "are not good metrics for assessing different stegosystems" due to "varied settings of language models".[45]
  - **Impact:** Provides necessary context for understanding evaluation and highlights a significant challenge in the field, demonstrating a nuanced academic perspective.

- [ ] 8.  **Expand "Challenges and Limitations" (Section 2.4):**
  - **Issue:** Challenges are listed but need more detailed explanations of *why* they are challenges and *how* LLMs interact with them.
  - **Suggestion:** For each challenge (e.g., Psic Effect, Low Embedding Capacity, Lack of Semantic Control, White-box vs. Black-box Access, Segmentation Ambiguity, Computational Overhead, Data Integrity, Ethical Concerns, Provable Security, Hallucinations), expand to explain its nature and specific implications for LLM-based steganography, ensuring each claim is supported by a citation.[2, 3, 9, 16, 17, 18, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 44]
  - **Impact:** Provides a comprehensive and well-supported analysis of the difficulties faced in the field.

- [ ] 9.  **Remove Redundant "Main Findings" (Section 7):**
  - **Issue:** This section largely duplicates content from the Abstract and "Results and Discussion" (Section 6).
  - **Suggestion:** Delete Section 7 entirely. Integrate any unique or particularly impactful points into an expanded Section 6 and the Conclusion (Section 8).
  - **Impact:** Improves flow, reduces redundancy, and strengthens the overall coherence and impact of the paper.

- [ ] 10. **Craft a Strong, Concise Conclusion (Section 8):**
  - **Issue:** The conclusion is currently a placeholder.
  - **Suggestion:** Synthesize the main findings, reiterate the answers to each research question, summarize the key contributions of *this specific SLR*, and briefly outline the most critical future research directions identified in Section 6.6. Avoid introducing new information.
  - **Impact:** Provides a definitive wrap-up of the review's findings and their broader implications, leaving a strong final impression.

---

- [ ] **Low Priority: Refinement & Formatting**

- [ ] 11. **Improve Introduction Flow (Section 1):**
  - **Issue:** The introduction could better foreshadow how LLMs address traditional steganography challenges.
  - **Suggestion:** After discussing text as a challenging carrier, add a sentence or two hinting at how LLMs' advanced generative capabilities offer novel solutions to overcome these inherent limitations.
  - **Impact:** Creates a clearer progression from problem identification to the proposed solution space.

- [ ] 12. **Address Formatting Remnants:**
  - **Issue:** "Preprint Notice," "Authors' addresses," and "Manuscript submitted to ACM" footers are present.
  - **Suggestion:** Remove the "Preprint Notice" if the paper is being prepared for submission. Remove or reformat the author addresses and submission footers as per the specific guidelines of your target journal or conference.
  - **Impact:** Ensures the manuscript reflects its final, professional state for publication.

---

## Human Review

### Title: "Systematic Literature Review on LLM-based Steganography"

- [X] Section 1: Introduction
- [X] Section 2: Background
  - [X] 2.1 Capabilities and Approximating Natural Communication
  - [X] 2.2 Role in Generative Linguistic Steganography
  - [X] 2.3 Challenges and Limitations in Steganography with LLMs
    - [X] 2.3.1 Perceptual vs. Statistical Imperceptibility (Psic Effect)
    - [ ] 2.3.2 Low Embedding Capacity
    - [ ] 2.3.3 Lack of Semantic Control and Contextual Consistency
    - [ ] 2.3.4 Challenges with LLMs in Steganography
    - [ ] 2.3.5 Segmentation Ambiguity
- [X] Section 3: Related Reviews
- [ ] Section 4: Research Method
  - [ ] 5.1 Planning
    - [ ] 5.1.1 Research Questions
    - [ ] 5.1.2 Search Strategies
    - [ ] 5.1.3 Inclusion and Exclusion Criteria
  - [ ] 5.2 Conducting the Search
  - [ ] 5.3 Data Extraction and Classification
- [ ] Section 6: Results
  - [-] 6.1 State of Published Literature on LLM-based Steganography (RQ1)
    - [X] 6.1.1 Publication Trends and Distribution
    - [X] 6.1.2 Model Preferences and Venues
    - [ ] 6.1.3 Research Gaps and Opportunities
    - [ ] 6.1.4 Key Trends and Evolution
  - [ ] 6.2 Applications of LLM-based Steganographic Techniques (RQ2)
    - [ ] 6.2.1 Primary Applications
    - [ ] 6.2.2 Covert Communication Applications
    - [ ] 6.2.3 Watermarking and Fingerprinting Applications
    - [ ] 6.2.4 Emerging Applications
    - [ ] 6.2.5 Domain-Specific Applications
    - [ ] 6.2.6 Application Requirements and Constraints
  - [ ] 6.3 Evaluation Metrics and Methods (RQ3)
    - [ ] 6.3.1 Metric Categories and Standards
    - [ ] 6.3.2 Imperceptibility Metrics
    - [ ] 6.3.3 Capacity Metrics
    - [ ] 6.3.4 Security Metrics
    - [ ] 6.3.5 Method Comparison
    - [ ] 6.3.6 Evaluation Methods and Tools
    - [ ] 6.3.7 Evaluation Challenges and Gaps
    - [ ] 6.3.8 Recent Advances in Evaluation
  - [ ] 6.4 Integration of External Knowledge Sources (RQ4)
    - [ ] 6.4.1 Knowledge Source Types
    - [ ] 6.4.2 Semantic Resources Integration
    - [ ] 6.4.3 Domain Corpora Integration
    - [ ] 6.4.4 Prompt Engineering and Context Guidance
    - [ ] 6.4.5 Integration Benefits and Performance Gains
    - [ ] 6.4.6 Integration Challenges and Trade-offs
    - [ ] 6.4.7 Integration Strategies and Architectures
    - [ ] 6.4.8 Future Directions in Knowledge Integration
  - [ ] 6.5 Limitations and Trade-offs in Current Techniques (RQ5)
    - [ ] 6.5.1 Key Limitations
    - [ ] 6.5.2 The Psic Effect: A Fundamental Trade-off
    - [ ] 6.5.3 Attack Vulnerability and Security Concerns
    - [ ] 6.5.4 Capacity Limitations in Short Texts
    - [ ] 6.5.5 Segmentation and Tokenization Issues
    - [ ] 6.5.6 Ethical Concerns and Misuse Potential
    - [ ] 6.5.7 White-box vs. Black-box Trade-offs
    - [ ] 6.5.8 Computational and Resource Constraints
    - [ ] 6.5.9 Unresolved Challenges and Future Needs
    - [ ] 6.5.10 Quantitative Impact Analysis
- [ ] Section 7: Discussion
  - [ ] 7.1 Synthesis of Key Findings
  - [ ] 7.2 Implications for Research and Practice
    - [ ] 7.2.1 Methodological Implications
    - [ ] 7.2.2 Practical Implications
  - [ ] 7.3 Addressing the Psic Effect
  - [ ] 7.4 The Role of Context and External Knowledge
  - [ ] 7.5 Ethical Considerations and Responsible Development
  - [ ] 7.6 Limitations of the Review
  - [ ] 7.7 Future Research Directions
    - [ ] 7.7.1 Technical Advancements
    - [ ] 7.7.2 Methodological Improvements
    - [ ] 7.7.3 Ethical and Social Considerations
  - [ ] 7.8 Conclusion
- [ ] Section 8: Conclusion
- [ ] Table of Contents (TOC)
  - [ ] Verify all sections are included correctly
  - [ ] Check page numbers are accurate
  - [ ] Confirm subsection and subsubsection hierarchy is correct
  - [ ] Ensure "Steganography and Large Language Models" section appears properly

@sections/llm_approaches.tex:55-59 I want a new line between the subsub section and what's after it

---

## Paragraph-Level Review Time Schedule

- **Assumptions**
  - You will review and finalize the paper paragraph by paragraph, focusing on clarity, coherence, citations, and alignment with the SLR goals.
  - Paragraph sizes are approximated as:
    - **Short**: \(\approx\) 3–5 lines (\(\approx\) 60–120 words)
    - **Medium**: \(\approx\) 6–10 lines (\(\approx\) 120–200 words)
    - **Long**: \(\ge\) 11 lines (\(\ge\) 200–300+ words)

- **Per-paragraph time budget**
  - **Short paragraphs** (e.g., brief motivation, linking sentences, simple definitions): **8–10 minutes** each.
  - **Medium paragraphs** (most body paragraphs, related work, method descriptions): **12–15 minutes** each.
  - **Long paragraphs** (dense results discussion, limitations, or multi-point arguments): **18–20 minutes** each.

- **Suggested daily schedule (2–3 hours/day)**
  - **Day 1** – Sections 1 & 2 (Introduction + Background)  
    - 4–6 **short/medium** paragraphs in Introduction \(\Rightarrow\) ~1–1.5 hours  
    - 6–8 **medium/long** paragraphs in Background (incl. terminology, challenges) \(\Rightarrow\) ~1–1.5 hours  
    - Goal: finalize all intro/background paragraphs and mark any missing citations/tables for follow-up.
  - **Day 2** – Sections 3 & 4 (Related Reviews + Research Method)  
    - 3–5 **medium** paragraphs in Related Reviews \(\Rightarrow\) ~45–60 minutes  
    - 6–8 **medium/long** paragraphs in Research Method \(\Rightarrow\) ~1–1.5 hours  
    - Goal: ensure methodological narrative is clear, reproducible, and consistently cited.
  - **Day 3** – Section 6.1–6.3 (Results: RQ1–RQ3)  
    - 8–10 **medium/long** paragraphs describing trends, applications, and metrics linked to tables \(\Rightarrow\) ~2–2.5 hours  
    - Goal: for each paragraph, explicitly tie statements to data in Tables 1–3 and refine transitions.
  - **Day 4** – Section 6.4–6.5 (Knowledge Integration & Limitations/Trade-offs)  
    - 6–8 **long** analytical paragraphs \(\Rightarrow\) ~2–2.5 hours  
    - Goal: sharpen argumentation, ensure each limitation/trade-off paragraph is well-supported and clearly scoped.
  - **Day 5** – Sections 7 & 8 (Discussion & Conclusion) + TOC/Formatting  
    - 4–6 **medium** discussion/conclusion paragraphs \(\Rightarrow\) ~1.5–2 hours  
    - 30–45 minutes for **global pass** (TOC, cross-references, redundant sentences, consistent terminology).

- **How to use this schedule**
  - At the start of each session, count how many **short**, **medium**, and **long** paragraphs you have in the target section and multiply by the per-paragraph time above to set a concrete block.
  - After completing each block, tick off the corresponding bullets in this `todo.md` (e.g., sections and subsections under *Human Review*).
  - If you finish early, use leftover time for a quick read-through of already finalized paragraphs to check global coherence and style.
