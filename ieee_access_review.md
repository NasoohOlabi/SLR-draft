# IEEE Access Pre-Submission Review

## Recommendation

**Major revision before submission.** The topic is relevant to IEEE Access and the manuscript has a useful organizing idea in contextual compatibility. The principal remaining risks are reproducibility, traceability of quantitative synthesis, and presentation quality.

## Major Findings

### 1. The evidence base covers 32 studies

The review includes 32 studies published from 2018 through 2025. The manuscript should consistently use this corpus size and review period.

Required action:

- Record the exact query used for each database, search fields, search date, and returned count.
- Regenerate the screening flow, extraction table, bibliography, and every percentage from one canonical dataset of 32 studies.

### 2. Corpus totals and quantitative claims are inconsistent

The manuscript states that 32 studies were analyzed, but the legacy `rq1_verification_report.md` was generated from an earlier 31-record dataset. It should not be treated as the source of truth for the current manuscript. The current 32-study dataset needs a reproducible derivation tied to stable record identifiers.

Required action:

- Assign a unique study ID to each included record.
- Add explicit fields for inclusion status, publication type, year, venue, model-access category, and steganography/watermarking scope.
- Generate all counts and tables from the canonical CSV rather than editing prose manually.
- Add automated assertions that the included-study count and category totals match the manuscript.

### 3. The review process is insufficiently reproducible

The manuscript identifies databases and aggregate search counts, but omits database-specific search syntax, search dates, duplicate count, full-text exclusion reasons, quality assessment, reviewer roles, and disagreement resolution. These omissions prevent replication and make selection bias difficult to assess.

Required action:

- Report identification, deduplication, title/abstract screening, full-text assessment, exclusion reasons, and final inclusion counts.
- State how many reviewers screened and extracted each record and how disagreements were resolved.
- Add a study-quality or risk-of-bias assessment appropriate for heterogeneous software/security research.
- If screening was performed by one reviewer, disclose this directly as a limitation rather than implying independent validation.

### 4. Scope boundaries are unstable

The paper combines covert-message steganography, text watermarking, model fingerprinting, and attacks that use concealed prompts. These areas share methods but have different goals, threat models, payload definitions, and evaluation criteria. Treating them as one quantitative corpus can produce misleading comparisons.

Required action:

- Define primary-study eligibility separately for linguistic steganography and adjacent watermarking work.
- Treat watermarking papers as a clearly labeled secondary stratum or boundary evidence.
- Do not combine payload, detection, robustness, or security statistics across incompatible task types.

### 5. Cross-paper metric comparisons reflect the current state of the field

RQ3 correctly notes that perplexity and payload depend on tokenizer, model, dataset, prompt, and reporting unit. This heterogeneity is itself an important finding about the current state of evaluation. Comparisons should remain descriptive and retain their original experimental context.

Required action:

- Avoid pooled averages unless all underlying measurements are demonstrably comparable.
- Report results by task, model, tokenizer, dataset, and unit.
- Distinguish detection accuracy, anti-steganalysis accuracy, watermark detection, extraction accuracy, and bit recovery.
- Present numerical values as study-reported results, not as a common benchmark.

### 6. Contextual compatibility needs an operational definition

Contextual compatibility is the manuscript's main claimed contribution, but it is currently a broad interpretive lens. The extraction scheme lists explicit, implicit, or absent context awareness without a reproducible coding rule.

Required action:

- Define observable criteria for explicit, implicit, and absent contextual compatibility.
- Explain the coding procedure and give representative examples.
- Report ambiguous cases and reviewer agreement.
- Separate discourse fit, topic fit, factual grounding, style fit, and conversational appropriateness where the evidence permits.

### 7. The related-review comparison is too rhetorical

The novelty claim relies mainly on saying that prior reviews do not foreground contextual compatibility. The section does not systematically compare search dates, databases, included-study counts, scope, questions, and synthesis methods.

Required action:

- Add a compact comparison table for prior reviews.
- State precisely which coverage or methodological gap this SLR fills.
- Avoid claims such as "no systematic review" unless supported by the refreshed search.

### 8. Submission formatting

The full generated-text table was incompatible with the IEEE Access two-column layout and has been replaced by a compact capacity summary. Wide comparison tables should use two-column floats.

Required action:

- Redesign wide tables using `table*`, shorter cells, or a supplementary spreadsheet.
- Keep full generated examples in supplementary material rather than the main manuscript.
- Resolve remaining material overfull boxes.
- Inspect every page of the final PDF after rebuilding from a clean directory.

## Minor Findings

- Remove internal AI-conversation comments from `sections/introduction.tex`.
- Correct visible encoding corruption such as smart quotes rendered as mojibake.
- Use consistent capitalization for "large language model" and "LLM-based."
- Reduce the keyword list and avoid redundant pairs such as both full terms and acronyms.
- Replace promotional wording such as "democratization of covertness" with neutral analytical language.
- Verify that every model, numerical claim, and named method has a primary citation.
- Add author biographies and ORCID identifiers when author-approved details are available.
- Add an AI-use disclosure if required by the authors' actual writing process and IEEE policy.

## Acceptance Criteria

- One canonical included-study dataset produces every table and count.
- The manuscript and canonical dataset consistently contain 32 included studies.
- The manuscript reports a complete, reproducible screening and extraction process.
- Scope strata prevent steganography and watermarking results from being conflated.
- Quantitative claims are traceable to study IDs and compatible measurement settings.
- The final clean build has no undefined citations/references, oversized floats, or material overfull boxes.
- The abstract states the search period, final included count, synthesis method, principal evidence-backed findings, and contribution.
