# TextbookDevelopment

A collection of control systems textbook materials under active development, written in LaTeX. This repository contains mathematical foundations, modeling and design chapters, and a review of deep learning methods for optical flow tracking.

> **Status: Work in Progress** -- This repository is under active development and not yet ready for public use. Chapter content, structure, and organization are subject to change.

## Repository Structure

```
TextbookDevelopment/
├── Controls_Modern_Practical/
│   ├── section00/          Mathematical Foundations (12 chapters)
│   │   └── chapters/       Complex numbers, calculus, ODEs, Laplace/Fourier
│   │                       transforms, linear algebra, probability,
│   │                       optimization, discrete-time systems, special
│   │                       functions, numerical methods
│   ├── section01/          Modeling and Design (16 chapters)
│   │   └── chapters/       Physical modeling, system analogies, test inputs,
│   │                       first/second-order systems, mechanical, electrical,
│   │                       electromechanical, thermal/fluid, chemical,
│   │                       aerospace, biomedical, and industrial examples
│   ├── archive/            Earlier chapter drafts (reference only)
│   ├── archive2/           Earlier chapter drafts (reference only)
│   ├── preamble.tex        Shared LaTeX preamble
│   ├── references.bib      Bibliography
│   └── syllabus.tex        Course syllabus
│
├── Controls_practical/
│   └── Controls_Textbook/  IEEE-style textbook: "Modern Control Theory"
│       ├── main_textbook.tex
│       ├── Part_I_Foundations/
│       ├── Part_II_System_Behavior/
│       ├── Part_III_Classical_Control/
│       ├── Part_IV_State_Space/
│       ├── Part_V_Digital/
│       └── Part_VI_Modern_AI/
│
└── Review of flow tracking/
    └── sections/           Deep learning optical flow review
                            (FlowNet, RAFT, neural PIV)
```

## Building the Documents

### Requirements

- A LaTeX distribution (TeX Live, MacTeX, or MiKTeX)
- `pdflatex` and `bibtex`
- Required LaTeX packages: `tikz`, `pgfplots`, `circuitikz`, `tcolorbox`, `siunitx`, `cleveref`, `listings`, `algorithm`, `algpseudocode`

Most packages are included in a full TeX Live or MacTeX installation.

### Compiling a Section (Controls_Modern_Practical)

Individual section compilers are located in each section directory.

```bash
cd Controls_Modern_Practical/section00
pdflatex section00_mathematical_foundations.tex
pdflatex section00_mathematical_foundations.tex
```

### Compiling the Full Textbook (Controls_practical)

```bash
cd Controls_practical/Controls_Textbook
pdflatex main_textbook.tex
bibtex main_textbook
pdflatex main_textbook.tex
pdflatex main_textbook.tex
```

### Compiling the Flow Tracking Review

```bash
cd "Review of flow tracking/sections"
pdflatex deep_learning_flow.tex
bibtex deep_learning_flow
pdflatex deep_learning_flow.tex
pdflatex deep_learning_flow.tex
```

## License

This work is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](LICENSE).

## Author

J.C. Vaught
