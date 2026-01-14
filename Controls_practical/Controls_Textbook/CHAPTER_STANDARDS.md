# Control Systems Textbook - Chapter Standards & Design Document

**Version:** 1.0
**Purpose:** Standardized reference for chapter formatting, quality gates, and automated validation

---

## Table of Contents

1. [Document Philosophy](#1-document-philosophy)
2. [Chapter Structure](#2-chapter-structure)
3. [Text & Prose Standards](#3-text--prose-standards)
4. [Mathematical Content](#4-mathematical-content)
5. [Figures & Diagrams](#5-figures--diagrams)
6. [Algorithms & Pseudocode](#6-algorithms--pseudocode)
7. [Boxes & Environments](#7-boxes--environments)
8. [Tables](#8-tables)
9. [Exercises & Problems](#9-exercises--problems)
10. [Historical Content](#10-historical-content)
11. [Cross-References & Labels](#11-cross-references--labels)
12. [Prohibited Patterns](#12-prohibited-patterns)
13. [Required Macros](#13-required-macros)
14. [Quality Gates & Validation](#14-quality-gates--validation)
15. [Agent Validation Checklist](#15-agent-validation-checklist)

---

## 1. Document Philosophy

### 1.1 Core Principles

- **Historical Motivation First**: Every concept must be introduced with the real-world problem that necessitated its invention
- **Mathematical Rigor with Clarity**: Complete derivations that prioritize elegance and physical intuition
- **Practical Implementation**: Every chapter includes hands-on experiments with accessible equipment
- **Self-Contained Chapters**: Each chapter stands alone; instructors may reorder without losing coherence
- **IEEE-Style Professionalism**: Academic quality suitable for publication

### 1.2 Target Audience

- Upper-division undergraduate and graduate engineering students
- Assumes calculus, linear algebra, and differential equations background
- No prior control systems knowledge required

### 1.3 Equipment Assumptions

All experiments should be implementable with:
- 3D-printed mechanical components
- Arduino or similar microcontrollers (ESP32, Raspberry Pi Pico)
- DC motors, servos, stepper motors
- Basic sensors (encoders, potentiometers, IMUs)
- Simple masses, springs, and dampers

---

## 2. Chapter Structure

### 2.1 Required Sections (in order)

```
\chapter{Chapter Title}

1. Opening Quote (optional but encouraged)
2. Chapter Introduction (1-2 paragraphs, no section heading)
3. \section{Historical Context / Motivation}
4. \section{Mathematical Foundations}
   - Core theory development
   - Theorem/Definition/Proof structure where appropriate
5. \section{Analysis Methods / Design Procedures}
6. \section{Practical Implementation}
7. \section{Worked Examples}
8. \section{Laboratory Experiment}
   - Objectives
   - Equipment list
   - Procedure
   - Expected results
   - Discussion questions
9. \section{Summary}
   - Key concepts (as prose, not bullets)
10. \section{Exercises}
    - Must start on new page: \newpage before section
    - Graduated difficulty (basic → intermediate → advanced)
```

### 2.2 Section Depth

- Maximum depth: `\subsubsection` (three levels)
- Prefer `\paragraph{}` for fourth-level organization
- Each section should have introductory text before first subsection

### 2.3 Length Guidelines

- Target: 25-40 pages per chapter (compiled)
- Historical section: 2-4 pages
- Lab experiment: 3-5 pages
- Exercises: 2-4 pages (15-25 problems)

---

## 3. Text & Prose Standards

### 3.1 Prohibited Text Patterns

| Prohibited | Replace With |
|------------|--------------|
| Bullet points (`\begin{itemize}`) | Flowing paragraphs, tables, or algorithms |
| Numbered lists for concepts | Prose with transitional phrases |
| Code blocks (`\begin{lstlisting}`) | Algorithm environments (language-agnostic) |
| "We will..." or "In this section..." | Direct statements |
| Excessive passive voice | Active voice where natural |
| Emojis or informal language | Professional academic prose |

### 3.2 Acceptable List Usage

Lists ARE permitted only for:
- Equipment lists in lab sections (enumitem with specific formatting)
- Step-by-step experimental procedures
- Explicit enumerations (e.g., "three conditions for stability")

When lists are necessary:
```latex
\begin{enumerate}[(1)]  % For numbered items
\begin{enumerate}[(a)]  % For sub-items
```

### 3.3 Paragraph Structure

- Each paragraph: single coherent idea
- Minimum 3 sentences per paragraph
- Topic sentence first
- Transitional phrases between paragraphs
- Technical terms: define on first use, italicize

### 3.4 Voice & Tense

- Mathematical derivations: present tense ("The transfer function is...")
- Historical content: past tense ("Bode developed...")
- Procedures: imperative mood ("Connect the motor to...")
- Analysis: present tense ("This equation shows...")

---

## 4. Mathematical Content

### 4.1 Required Macros

All chapters MUST use these predefined macros (defined in `main_textbook.tex`):

**Vectors and Matrices:**
```latex
\vect{x}        % Bold vector: x
\mat{A}         % Bold matrix: A
\bA, \bB, ...   % Quick bold capitals
\bx, \bu, ...   % Quick bold lowercase
\bzero, \bone   % Zero and one vectors
```

**State-Space:**
```latex
\state          % State vector x
\stateder       % State derivative dx/dt
\inputvec       % Input vector u
\outputvec      % Output vector y
```

**Transforms:**
```latex
\Laplace        % Laplace transform L
\invLaplace     % Inverse Laplace L^{-1}
\ztrans         % Z-transform Z
```

**Sets and Spaces:**
```latex
\Real, \R       % Real numbers R
\Complex        % Complex numbers C
\N, \Z          % Natural, integers
```

**Operators:**
```latex
\transpose, \trans  % Transpose ^T
\inv            % Inverse ^{-1}
\rank, \trace, \diag
\argmin, \argmax
\eig            % Eigenvalues
```

**Frequency Response:**
```latex
\jw             % j*omega
\magn{G}        % |G| magnitude
\phase{G}       % angle G
\dB             % decibels unit
\degrees        % degree symbol
```

**PID Control:**
```latex
\Kp, \Ki, \Kd   % Gain parameters
\Ti, \Td        % Time constants
```

**Calculus:**
```latex
\e              % Euler's e (upright)
\j              % Imaginary unit (upright)
\diff           % Differential d (upright)
\pd{f}{x}       % Partial derivative
\grad           % Gradient nabla
```

**Reinforcement Learning:**
```latex
\policy         % Policy pi
\vfunc, \qfunc  % Value functions V, Q
\discount       % Discount gamma
\states, \actions % State/action spaces
\E              % Expectation
```

### 4.2 Equation Formatting

**Display Equations (numbered):**
```latex
\begin{equation}
    G(s) = \frac{K}{s(s+a)(s+b)}
    \label{eq:ch5:transfer_function}
\end{equation}
```

**Display Equations (unnumbered):**
```latex
\begin{equation*}
    y = Cx + Du
\end{equation*}
```

**Multi-line Equations:**
```latex
\begin{align}
    \dot{x} &= Ax + Bu \label{eq:ch4:state}\\
    y &= Cx + Du \label{eq:ch4:output}
\end{align}
```

**Inline Math:**
- Use `$...$` for inline
- Complex expressions: prefer display mode
- Fractions inline: use `\tfrac` for small fractions

### 4.3 Equation Labeling Convention

```
eq:<chapter_number>:<descriptive_name>
```

Examples:
- `eq:ch5:damping_ratio`
- `eq:ch12:root_locus_angle`
- `eq:ch17:riccati`

### 4.4 Mathematical Environments

```latex
\begin{theorem}[Optional Name]
    Statement of theorem.
\end{theorem}

\begin{proof}
    Proof content.
\end{proof}

\begin{definition}[Term Being Defined]
    Definition content.
\end{definition}

\begin{lemma}
\begin{corollary}
\begin{proposition}
\begin{property}
\begin{remark}
```

---

## 5. Figures & Diagrams

### 5.1 General Requirements

- **ALL figures must be implemented** - no placeholder text or TODO comments
- **Sharp corners only** - no rounded corners on any element
- **TikZ/PGFPlots preferred** - vector graphics, not images
- **Consistent color scheme** - use predefined colors
- **Proper labels and captions** - descriptive, standalone meaning

### 5.2 TikZ Style Requirements

```latex
% All blocks: sharp corners (default rectangle is sharp)
\tikzset{
    block/.style = {draw, rectangle, minimum height=2em, minimum width=3em},
    % NO rounded corners option
}

% For tcolorbox: sharp corners is set globally
% sharp corners  % This is already in box definitions
```

### 5.3 Predefined Colors

```latex
controlblue     % Blue for primary signals/paths
controlred      % Red for error signals
controlgreen    % Green for feedback paths
controlorange   % Orange for disturbances
```

### 5.4 Block Diagram Standards

```latex
\begin{figure}[htbp]
    \centering
    \begin{tikzpicture}[auto, node distance=2cm, >=latex']
        % Input
        \node[input] (input) {};
        % Summing junction
        \node[sum, right of=input] (sum) {};
        % Controller
        \node[block, right of=sum] (controller) {$C(s)$};
        % Plant
        \node[block, right of=controller] (plant) {$G(s)$};
        % Output
        \node[output, right of=plant] (output) {};

        % Connections with labels
        \draw[->] (input) -- node{$r$} (sum);
        \draw[->] (sum) -- node{$e$} (controller);
        \draw[->] (controller) -- node{$u$} (plant);
        \draw[->] (plant) -- node[name=y]{$y$} (output);

        % Feedback
        \draw[->] (y) |- ++(0,-1.5) -| node[pos=0.99]{$-$} (sum);
    \end{tikzpicture}
    \caption{Standard feedback control system with controller $C(s)$ and plant $G(s)$.}
    \label{fig:ch9:feedback_block}
\end{figure}
```

### 5.5 Plot Standards (PGFPlots)

```latex
\begin{figure}[htbp]
    \centering
    \begin{tikzpicture}
        \begin{axis}[
            width=0.8\textwidth,
            height=0.5\textwidth,
            xlabel={Time (s)},
            ylabel={Response},
            grid=major,
            legend pos=north east,
            sharp plot,  % No smoothing
        ]
            \addplot[blue, thick] coordinates {(0,0) (1,0.63) (2,0.86)};
            \addlegendentry{Step response}
        \end{axis}
    \end{tikzpicture}
    \caption{Unit step response showing exponential approach to steady state.}
    \label{fig:ch5:step_response}
\end{figure}
```

### 5.6 Bode Plot Template

```latex
\begin{figure}[htbp]
    \centering
    \begin{tikzpicture}
        \begin{semilogxaxis}[
            name=mag,
            width=0.85\textwidth,
            height=0.35\textwidth,
            xlabel={},
            ylabel={Magnitude (dB)},
            grid=both,
            xticklabels={},
        ]
            % Magnitude data
        \end{semilogxaxis}

        \begin{semilogxaxis}[
            at=(mag.below south west),
            anchor=north west,
            width=0.85\textwidth,
            height=0.35\textwidth,
            xlabel={Frequency (rad/s)},
            ylabel={Phase (deg)},
            grid=both,
        ]
            % Phase data
        \end{semilogxaxis}
    \end{tikzpicture}
    \caption{Bode plot of the open-loop transfer function.}
    \label{fig:ch13:bode_plot}
\end{figure}
```

### 5.7 Root Locus Template

```latex
\begin{figure}[htbp]
    \centering
    \begin{tikzpicture}
        \begin{axis}[
            width=0.7\textwidth,
            height=0.7\textwidth,
            xlabel={Real Axis},
            ylabel={Imaginary Axis},
            axis equal,
            grid=major,
            xmin=-5, xmax=1,
            ymin=-3, ymax=3,
        ]
            % Poles as x markers
            \addplot[only marks, mark=x, mark size=4pt, thick]
                coordinates {(-2,0) (-1,1) (-1,-1)};
            % Zeros as o markers
            \addplot[only marks, mark=o, mark size=4pt, thick]
                coordinates {(-3,0)};
            % Root locus branches
            \addplot[blue, thick] coordinates {...};
        \end{axis}
    \end{tikzpicture}
    \caption{Root locus showing pole migration as gain increases.}
    \label{fig:ch12:root_locus}
\end{figure}
```

### 5.8 Figure Labeling Convention

```
fig:<chapter_number>:<descriptive_name>
```

Examples:
- `fig:ch5:second_order_response`
- `fig:ch13:bode_margin`
- `fig:ch17:lqr_block`

### 5.9 Caption Requirements

- Complete sentence ending with period
- Standalone meaning (reader should understand without reading text)
- Reference specific elements: "showing the relationship between..."
- Include key parameter values when relevant

---

## 6. Algorithms & Pseudocode

### 6.1 Syntax Standard: algpseudocode

**REQUIRED:** Use `algpseudocode` package syntax (mixed-case commands)

```latex
\begin{algorithm}[htbp]
    \caption{Descriptive algorithm name}
    \label{alg:ch11:ziegler_nichols}
    \begin{algorithmic}[1]
        \Require Input parameters and preconditions
        \Ensure Output guarantees and postconditions
        \State $x \gets 0$ \Comment{Initialization}
        \While{condition}
            \State computation
            \If{test}
                \State action
            \ElsIf{other test}
                \State other action
            \Else
                \State default action
            \EndIf
        \EndWhile
        \For{$i = 1$ \To $n$}
            \State indexed operation
        \EndFor
        \Return result
    \end{algorithmic}
\end{algorithm}
```

### 6.2 Prohibited Algorithm Syntax

**DO NOT USE** (algorithmic package - uppercase):
```latex
% WRONG - DO NOT USE
\STATE, \WHILE, \IF, \FOR, \RETURN, \REQUIRE, \ENSURE
\ENDIF, \ENDWHILE, \ENDFOR
```

### 6.3 Algorithm Command Reference

| Correct (algpseudocode) | Wrong (algorithmic) |
|------------------------|---------------------|
| `\State` | `\STATE` |
| `\If{cond}` | `\IF{cond}` |
| `\ElsIf{cond}` | `\ELSIF{cond}` |
| `\Else` | `\ELSE` |
| `\EndIf` | `\ENDIF` |
| `\While{cond}` | `\WHILE{cond}` |
| `\EndWhile` | `\ENDWHILE` |
| `\For{range}` | `\FOR{range}` |
| `\EndFor` | `\ENDFOR` |
| `\Return` | `\RETURN` |
| `\Require` | `\REQUIRE` |
| `\Ensure` | `\ENSURE` |
| `\Comment{text}` | `\COMMENT{text}` |
| `\Function{name}{args}` | `\FUNCTION{name}{args}` |
| `\EndFunction` | `\ENDFUNCTION` |
| `\Procedure{name}{args}` | `\PROCEDURE{name}{args}` |
| `\EndProcedure` | `\ENDPROCEDURE` |
| `\Call{func}{args}` | `\CALL{func}{args}` |

### 6.4 Language Agnosticism

- NO programming language-specific syntax
- NO code blocks (`lstlisting`, `verbatim`, `minted`)
- Use mathematical notation within algorithms
- Describe operations conceptually

**Wrong:**
```latex
\State \texttt{for i in range(n):}
\State \texttt{x = np.zeros(n)}
```

**Correct:**
```latex
\For{$i = 1$ \To $n$}
\State $\bx \gets \bzero_n$ \Comment{Initialize to zero vector}
```

### 6.5 Algorithm Labeling Convention

```
alg:<chapter_number>:<descriptive_name>
```

---

## 7. Boxes & Environments

### 7.1 Available Box Types

| Environment | Color | Use For |
|-------------|-------|---------|
| `examplebox` | Blue | Worked examples with solutions |
| `historicalbox` | Brown | Historical context and anecdotes |
| `conceptbox` | Green | Key concept explanations |
| `warningbox` | Red | Common mistakes, pitfalls |
| `notebox` | Yellow | Important notes, clarifications |
| `keyconceptbox` | Purple | Fundamental definitions/theorems |
| `keypoint` | Light Blue | Summary points |
| `designtip` | Light Green | Practical design advice |
| `experimentbox` | Orange | Lab procedure highlights |
| `applicationbox` | Teal | Real-world applications |

### 7.2 Box Syntax

```latex
\begin{examplebox}[Example Title]
    Content of the example box.

    Can contain equations:
    \begin{equation*}
        G(s) = \frac{1}{s+1}
    \end{equation*}

    And multiple paragraphs.
\end{examplebox}
```

### 7.3 Box Style Requirements

- **Sharp corners**: All boxes use `sharp corners` (already set in definitions)
- **Breakable**: Long boxes can span pages (already set)
- **Titles**: Always provide descriptive title in brackets
- **No nesting**: Do not nest boxes inside other boxes

### 7.4 When to Use Each Box

**examplebox**: Step-by-step worked problems
```latex
\begin{examplebox}[PID Tuning for First-Order System]
    Given a plant $G(s) = \frac{1}{s+2}$, design a PI controller...
\end{examplebox}
```

**historicalbox**: Background stories
```latex
\begin{historicalbox}[Bode's Innovation at Bell Labs]
    In 1938, Hendrik Bode faced a critical challenge...
\end{historicalbox}
```

**warningbox**: Common errors
```latex
\begin{warningbox}[Derivative Kick]
    Direct differentiation of the error signal causes...
\end{warningbox}
```

**keyconceptbox**: Fundamental definitions
```latex
\begin{keyconceptbox}[BIBO Stability]
    A system is Bounded-Input Bounded-Output stable if...
\end{keyconceptbox}
```

---

## 8. Tables

### 8.1 Table Style: booktabs

```latex
\begin{table}[htbp]
    \centering
    \caption{Ziegler-Nichols tuning parameters for different controller types.}
    \label{tab:ch11:zn_params}
    \begin{tabular}{lccc}
        \toprule
        Controller & $K_p$ & $T_i$ & $T_d$ \\
        \midrule
        P & $0.5 K_u$ & --- & --- \\
        PI & $0.45 K_u$ & $T_u/1.2$ & --- \\
        PID & $0.6 K_u$ & $T_u/2$ & $T_u/8$ \\
        \bottomrule
    \end{tabular}
\end{table}
```

### 8.2 Table Requirements

- Use `\toprule`, `\midrule`, `\bottomrule` (no `\hline`)
- Caption ABOVE table
- Label after caption
- Center table with `\centering`
- Use `[htbp]` float specifier
- Column alignment: `l` for text, `c` for symbols, `r` for numbers

### 8.3 Table Labeling Convention

```
tab:<chapter_number>:<descriptive_name>
```

### 8.4 Multi-row and Multi-column

```latex
\usepackage{multirow}

\multirow{2}{*}{Text} % Spans 2 rows
\multicolumn{3}{c}{Header} % Spans 3 columns, centered
```

---

## 9. Exercises & Problems

### 9.1 Section Placement

```latex
\newpage  % REQUIRED: Exercises start on new page
\section{Exercises}
```

### 9.2 Problem Structure

```latex
\begin{exercise}
    Problem statement as a complete paragraph. Include all necessary
    information for the student to solve the problem. State what is
    given and what must be found.

    For multi-part problems, use enumeration:
    \begin{enumerate}[(a)]
        \item First part of the problem.
        \item Second part building on the first.
        \item Extension or application.
    \end{enumerate}
\end{exercise}
```

### 9.3 Difficulty Progression

Organize exercises in three tiers:

1. **Basic** (Problems 1-5): Direct application of formulas
2. **Intermediate** (Problems 6-12): Require synthesis of concepts
3. **Advanced** (Problems 13+): Design problems, proofs, extensions

### 9.4 Problem Types to Include

- Computational (calculate specific values)
- Analytical (derive expressions, prove properties)
- Design (meet specifications)
- Simulation (verify with computational tools)
- Conceptual (explain phenomena)
- Laboratory extensions (additional experiments)

---

## 10. Historical Content

### 10.1 Purpose

- Motivate why mathematical tools were developed
- Connect abstract concepts to tangible problems
- Humanize the engineering discipline
- Provide context for design decisions

### 10.2 Placement

- Chapter opening: 1-2 paragraphs introducing historical context
- Dedicated section: `\section{Historical Context}` (2-4 pages)
- Inline `historicalbox` environments for specific anecdotes

### 10.3 Required Elements

- Name and dates of key contributors
- The specific problem they faced
- How their solution evolved into modern techniques
- Connection to chapter's mathematical content

### 10.4 Example Historical Box

```latex
\begin{historicalbox}[The Stability Crisis of 1927]
    When Bell Telephone Company attempted to install transcontinental
    telephone amplifier chains, engineers discovered that cascading
    multiple amplifiers created unexpected oscillations. Harold Black,
    working at Bell Labs, had a revolutionary insight during his
    morning ferry commute: deliberately introducing negative feedback
    could stabilize the system at the cost of reduced gain. His 1927
    notebook sketch became the foundation of modern control theory.
\end{historicalbox}
```

---

## 11. Cross-References & Labels

### 11.1 Label Naming Convention

```
<type>:<chapter>:<descriptive_name>
```

| Type | Prefix | Example |
|------|--------|---------|
| Equation | `eq:` | `eq:ch5:damping_ratio` |
| Figure | `fig:` | `fig:ch13:bode_plot` |
| Table | `tab:` | `tab:ch11:tuning_params` |
| Algorithm | `alg:` | `alg:ch17:lqr_design` |
| Section | `sec:` | `sec:ch9:sensitivity` |
| Theorem | `thm:` | `thm:ch6:routh_hurwitz` |
| Definition | `def:` | `def:ch15:controllability` |
| Example | `ex:` | `ex:ch10:pid_tuning` |
| Chapter | `ch:` | `ch:feedback` |

### 11.2 Reference Commands

```latex
\cref{eq:ch5:damping}      % "Equation (5.1)"
\Cref{fig:ch13:bode}       % "Figure 13.2" (sentence start)
\cref{sec:ch9:sensitivity} % "Section 9.3"
\cref{thm:ch6:routh}       % "Theorem 6.1"
```

### 11.3 Cross-Chapter References

When referencing other chapters:
```latex
As discussed in \cref{ch:state_space}, the state-space representation...
See \cref{sec:ch4:canonical_forms} for canonical form derivations.
```

---

## 12. Prohibited Patterns

### 12.1 Compilation Errors (MUST FIX)

| Pattern | Problem | Fix |
|---------|---------|-----|
| `\STATE` | Wrong algorithm package | Use `\State` |
| `\begin{lstlisting}` | Language-specific code | Use `\begin{algorithm}` |
| Unmatched `$` | Math mode error | Check all math delimiters |
| `\begin{abstract}` | Not valid in book class | Remove entirely |
| Undefined `\command` | Missing macro | Use defined macros or define in preamble |
| `\begin{algorithmic}` outside algorithm | Environment error | Wrap in `\begin{algorithm}` |

### 12.2 Style Violations (SHOULD FIX)

| Pattern | Problem | Fix |
|---------|---------|-----|
| `\begin{itemize}` | Bullet points | Convert to prose or table |
| `rounded corners` | Style violation | Use `sharp corners` |
| `print()`, `numpy` | Language-specific | Use mathematical notation |
| TODO comments | Incomplete content | Implement fully |
| `[FIGURE]` placeholder | Missing figure | Create TikZ diagram |
| `\hline` in tables | Wrong style | Use `\toprule/\midrule/\bottomrule` |

### 12.3 Quality Violations (CONSIDER FIXING)

| Pattern | Problem | Recommendation |
|---------|---------|----------------|
| Section without intro | Poor flow | Add 1-2 intro sentences |
| Equation without explanation | Not self-documenting | Add surrounding prose |
| Figure without reference | Orphan figure | Reference in text |
| Single-sentence paragraph | Poor writing | Expand or merge |

---

## 13. Required Macros

### 13.1 Macros Defined in main_textbook.tex

All chapters can use these without additional definition:

```latex
% Vectors and Matrices
\vect{x}, \mat{A}
\bA, \bB, \bC, \bD, \bF, \bG, \bH, \bI, \bJ, \bK, \bL, \bM
\bN, \bP, \bQ, \bR, \bS, \bT, \bU, \bV, \bW, \bX, \bY, \bZ
\bx, \bu, \by, \bz, \bw, \bv, \bq, \bp, \br, \be
\bzero, \bone

% State-Space
\state, \stateder, \inputvec, \outputvec

% Transforms
\Laplace, \invLaplace, \ztrans

% Sets
\Real, \R, \Complex, \N, \Z

% Operators
\transpose, \trans, \inv, \half
\rank, \trace, \diag, \eig
\argmin, \argmax

% Frequency Response
\jw, \magn{}, \phase{}, \dB, \degrees

% PID
\Kp, \Ki, \Kd, \Ti, \Td

% Calculus
\e, \j, \diff, \pd{}{}, \grad

% RL
\policy, \vfunc, \qfunc, \discount
\states, \actions, \reward, \returns, \advantage
\E, \Prob, \Var

% Utility
\norm{}, \abs{}, \real, \imag, \lr, \To
```

### 13.2 Adding New Macros

If a chapter needs a macro not in the above list:

1. Check if an existing macro serves the purpose
2. If new macro needed, add to `main_textbook.tex` in appropriate section
3. Document in this standards file
4. Use semantic naming (describes meaning, not appearance)

---

## 14. Quality Gates & Validation

### 14.1 Compilation Requirements (MUST PASS)

- [ ] Compiles with `lualatex` without fatal errors
- [ ] No undefined control sequences
- [ ] No runaway arguments
- [ ] No missing `\end{...}` environments
- [ ] All figures render (no missing files)

### 14.2 Structural Requirements (MUST PASS)

- [ ] Chapter begins with `\chapter{Title}`
- [ ] Has Historical Context section
- [ ] Has Laboratory Experiment section
- [ ] Exercises section starts with `\newpage`
- [ ] All required sections present

### 14.3 Style Requirements (SHOULD PASS)

- [ ] No `\begin{itemize}` or `\begin{enumerate}` outside allowed contexts
- [ ] No `lstlisting` or code blocks
- [ ] All algorithm environments use algpseudocode syntax
- [ ] All figures implemented (no placeholders)
- [ ] All boxes use sharp corners
- [ ] Tables use booktabs style

### 14.4 Quality Requirements (RECOMMENDED)

- [ ] All equations referenced in text
- [ ] All figures referenced in text
- [ ] Historical motivation present
- [ ] Minimum 15 exercises
- [ ] Lab experiment has all subsections

---

## 15. Agent Validation Checklist

### 15.1 Automated Checks (grep/regex)

```bash
# Check for prohibited bullet points
grep -c "\\\\begin{itemize}" chapter.tex
# Should be: 0 (or only in lab/exercise sections)

# Check for wrong algorithm syntax
grep -E "\\\\(STATE|WHILE|IF|FOR|RETURN|REQUIRE|ENSURE)\\b" chapter.tex
# Should be: 0

# Check for code blocks
grep -c "\\\\begin{lstlisting}" chapter.tex
# Should be: 0

# Check for placeholder figures
grep -ci "TODO\|PLACEHOLDER\|\[FIGURE\]" chapter.tex
# Should be: 0

# Check for rounded corners
grep -c "rounded corners" chapter.tex
# Should be: 0

# Check for abstract environment
grep -c "\\\\begin{abstract}" chapter.tex
# Should be: 0

# Check exercises section has newpage
grep -B1 "\\\\section{Exercises}" chapter.tex | grep -c "\\\\newpage"
# Should be: 1
```

### 15.2 Structural Validation

```bash
# Required sections (check presence)
grep -c "\\\\section{Historical" chapter.tex      # >= 1
grep -c "\\\\section{Laboratory" chapter.tex     # >= 1
grep -c "\\\\section{Exercises}" chapter.tex     # >= 1
grep -c "\\\\section{Summary}" chapter.tex       # >= 1

# Chapter structure
head -20 chapter.tex | grep -c "\\\\chapter{"    # == 1
```

### 15.3 Compilation Validation

```bash
# Compile and check for errors
lualatex -interaction=nonstopmode main_textbook.tex

# Count specific errors
grep "^! Undefined control sequence" main_textbook.log | wc -l
grep "^! Missing" main_textbook.log | wc -l
grep "^! LaTeX Error" main_textbook.log | wc -l
```

### 15.4 Quality Metrics

```bash
# Count exercises
grep -c "\\\\begin{exercise}" chapter.tex
# Target: >= 15

# Count figures
grep -c "\\\\begin{figure}" chapter.tex
# Target: >= 5

# Count worked examples
grep -c "\\\\begin{examplebox}" chapter.tex
# Target: >= 3

# Count historical boxes
grep -c "\\\\begin{historicalbox}" chapter.tex
# Target: >= 1
```

---

## Appendix A: Quick Reference Card

### A.1 Common Patterns

**Starting a chapter:**
```latex
\chapter{Chapter Title}

Opening paragraph introducing the chapter topic and its importance...

\section{Historical Context}
\begin{historicalbox}[The Origin of This Concept]
...
\end{historicalbox}
```

**Worked example:**
```latex
\begin{examplebox}[Descriptive Title]
    Given: ...

    Find: ...

    Solution: ...
    \begin{align}
        ...
    \end{align}

    Therefore, the result is...
\end{examplebox}
```

**Algorithm:**
```latex
\begin{algorithm}[htbp]
    \caption{Algorithm Name}
    \label{alg:chX:name}
    \begin{algorithmic}[1]
        \Require inputs
        \Ensure outputs
        \State initialization
        \While{condition}
            \State computation
        \EndWhile
        \Return result
    \end{algorithmic}
\end{algorithm}
```

### A.2 File Checklist

Before submitting a chapter:

- [ ] File compiles without errors independently
- [ ] No `\documentclass` in chapter file
- [ ] No package imports in chapter file
- [ ] Begins with `\chapter{}`
- [ ] All sections present
- [ ] No prohibited patterns
- [ ] All figures implemented
- [ ] Exercises on new page

---

*Document maintained by textbook editors. Last updated: January 2026*
