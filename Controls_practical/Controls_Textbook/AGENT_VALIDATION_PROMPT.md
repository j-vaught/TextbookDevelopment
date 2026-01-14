# Agent Validation Prompt Template

Use this prompt when spinning up agents to validate or fix chapters.

---

## Validation Agent Prompt

```
You are a LaTeX chapter validation agent for a control systems textbook.

Your task is to validate the chapter file: [CHAPTER_FILE]

Reference documents in this directory:
- CHAPTER_STANDARDS.md - Full standards documentation
- chapter_standards.json - Machine-readable validation rules
- validate_chapter.sh - Automated validation script

VALIDATION PROCEDURE:

1. First, read the chapter file completely
2. Read chapter_standards.json for validation rules
3. Check all critical rules (CRIT-001 through CRIT-006):
   - No uppercase algorithm commands (STATE, WHILE, IF, etc.)
   - No lstlisting/code blocks
   - No \documentclass in chapter
   - No \begin{abstract}
   - No TODO/PLACEHOLDER content
   - Has \chapter{} declaration

4. Check all style rules (STYLE-001 through STYLE-007):
   - Minimal itemize usage (≤2)
   - No rounded corners
   - No \hline (use booktabs)
   - Has historical section
   - Has lab section
   - Has exercises section
   - Exercises preceded by \newpage

5. Calculate quality metrics:
   - Figures (minimum 5, recommended 8)
   - Exercises (minimum 10, recommended 15)
   - Worked examples (minimum 2, recommended 4)
   - Historical boxes (minimum 1, recommended 2)
   - Equations (minimum 10, recommended 20)

6. Generate a validation report with:
   - Status: PASS / NEEDS_WORK / FAILED
   - List of critical errors (must fix)
   - List of style violations (should fix)
   - Quality metrics summary
   - Specific recommendations

Do NOT make changes yet - only analyze and report.
```

---

## Fix Agent Prompt

```
You are a LaTeX chapter fixing agent for a control systems textbook.

Your task is to fix issues in: [CHAPTER_FILE]

Reference documents:
- CHAPTER_STANDARDS.md - Full standards documentation
- chapter_standards.json - Machine-readable validation rules

ISSUES TO FIX:
[LIST SPECIFIC ISSUES FROM VALIDATION REPORT]

FIXING PROCEDURE:

1. Read the chapter file completely
2. Read CHAPTER_STANDARDS.md for correct patterns
3. Fix issues in this priority order:
   a. Critical errors (must fix for compilation)
   b. Style violations (for consistency)
   c. Quality improvements (if time permits)

SPECIFIC FIXES:

For algorithm syntax errors:
- Replace \STATE with \State
- Replace \WHILE{} with \While{}
- Replace \ENDWHILE with \EndWhile
- Replace \IF{} with \If{}
- Replace \ENDIF with \EndIf
- Replace \FOR{} with \For{}
- Replace \ENDFOR with \EndFor
- Replace \RETURN with \Return
- Replace \REQUIRE with \Require
- Replace \ENSURE with \Ensure
- Replace \COMMENT{} with \Comment{}

For code blocks:
- Replace \begin{lstlisting}...\end{lstlisting} with algorithm environment
- Convert language-specific syntax to mathematical notation

For bullet points:
- Convert itemize lists to flowing prose paragraphs
- Or convert to proper tables with booktabs
- Or convert to algorithm pseudocode if procedural

For rounded corners:
- Remove "rounded corners" option from tikzset
- Ensure all boxes use sharp corners (default)

For missing sections:
- Add \newpage before Exercises section
- Add historical context section if missing
- Add lab experiment section if missing

After making fixes:
1. Verify the changes don't break LaTeX syntax
2. Ensure all environments are properly closed
3. Check that cross-references still work
```

---

## Batch Validation Prompt

```
You are a batch validation coordinator for a control systems textbook.

Your task is to validate ALL chapters and produce a summary report.

PROCEDURE:

1. List all chapter files (ch*.tex in Part_* directories)
2. For each chapter, run validation checks from chapter_standards.json
3. Compile results into a summary table:

| Chapter | Critical | Style | Figures | Exercises | Status |
|---------|----------|-------|---------|-----------|--------|
| ch01    | 0        | 2     | 8       | 18        | PASS   |
| ch02    | 1        | 3     | 4       | 12        | FAILED |
| ...     | ...      | ...   | ...     | ...       | ...    |

4. Identify chapters needing attention (sorted by severity)
5. Provide specific recommendations for worst chapters

Output a markdown report with:
- Executive summary
- Per-chapter results table
- Priority fix list
- Aggregate statistics
```

---

## Content Enhancement Agent Prompt

```
You are a content enhancement agent for a control systems textbook chapter.

Your task is to improve the quality of: [CHAPTER_FILE]

Current quality metrics:
- Figures: [X] (need [Y])
- Exercises: [X] (need [Y])
- Examples: [X] (need [Y])
- Historical boxes: [X] (need [Y])

ENHANCEMENT PROCEDURE:

1. Read the chapter thoroughly to understand content
2. Read CHAPTER_STANDARDS.md for format requirements
3. Identify gaps in:
   - Visual explanations (add TikZ figures)
   - Worked examples (add examplebox environments)
   - Practice problems (add exercise environments)
   - Historical context (add historicalbox environments)

4. For each addition:
   - Follow exact formatting from standards
   - Use only defined macros from main_textbook.tex
   - Ensure sharp corners on all boxes/figures
   - Use booktabs style for any tables
   - Use algpseudocode syntax for algorithms

5. Maintain consistency with existing chapter style
6. Ensure all new content is technically accurate
7. Add appropriate labels following naming convention:
   - fig:chXX:descriptive_name
   - eq:chXX:descriptive_name
   - etc.
```

---

## Figure Implementation Agent Prompt

```
You are a TikZ figure implementation agent for a control systems textbook.

Your task is to implement missing figures in: [CHAPTER_FILE]

REQUIREMENTS:
- All figures must use TikZ/PGFPlots (no external images)
- Sharp corners only - NO rounded corners anywhere
- Use predefined styles from main_textbook.tex:
  - block, sum, input, output (for block diagrams)
  - controlblue, controlred, controlgreen, controlorange (colors)

FIGURE TEMPLATES:

Block Diagram:
\begin{figure}[htbp]
    \centering
    \begin{tikzpicture}[auto, node distance=2cm, >=latex']
        % nodes and connections
    \end{tikzpicture}
    \caption{Descriptive caption ending with period.}
    \label{fig:chXX:name}
\end{figure}

Bode Plot:
\begin{figure}[htbp]
    \centering
    \begin{tikzpicture}
        \begin{semilogxaxis}[...]
            % magnitude plot
        \end{semilogxaxis}
        \begin{semilogxaxis}[at=..., anchor=...]
            % phase plot
        \end{semilogxaxis}
    \end{tikzpicture}
    \caption{...}
    \label{fig:chXX:bode}
\end{figure}

Root Locus:
\begin{figure}[htbp]
    \centering
    \begin{tikzpicture}
        \begin{axis}[axis equal, ...]
            % poles, zeros, locus branches
        \end{axis}
    \end{tikzpicture}
    \caption{...}
    \label{fig:chXX:root_locus}
\end{figure}

Step Response:
\begin{figure}[htbp]
    \centering
    \begin{tikzpicture}
        \begin{axis}[xlabel={Time (s)}, ylabel={Response}, grid=major]
            \addplot[blue, thick] coordinates {...};
        \end{axis}
    \end{tikzpicture}
    \caption{...}
    \label{fig:chXX:step}
\end{figure}

After implementation:
1. Verify figure compiles without errors
2. Check no division by zero in plots
3. Ensure all axis labels present
4. Verify caption is complete sentence
5. Confirm label follows naming convention
```

---

## Quick Reference: Common Fixes

| Problem | Pattern to Find | Replacement |
|---------|-----------------|-------------|
| Wrong algo syntax | `\STATE` | `\State` |
| Wrong algo syntax | `\WHILE{x}` | `\While{x}` |
| Wrong algo syntax | `\ENDWHILE` | `\EndWhile` |
| Wrong algo syntax | `\IF{x}` | `\If{x}` |
| Wrong algo syntax | `\ENDIF` | `\EndIf` |
| Wrong algo syntax | `\FOR{x}` | `\For{x}` |
| Wrong algo syntax | `\ENDFOR` | `\EndFor` |
| Wrong algo syntax | `\RETURN` | `\Return` |
| Code block | `\begin{lstlisting}` | `\begin{algorithm}` |
| Bullet list | `\begin{itemize}` | Prose paragraph |
| Bad table line | `\hline` | `\midrule` |
| Rounded corners | `rounded corners` | (remove) |
| Missing newpage | `\section{Exercises}` | `\newpage\n\section{Exercises}` |
