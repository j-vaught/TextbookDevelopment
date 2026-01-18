#!/bin/bash
# ============================================================================
# FIGURE COMPILATION SCRIPT
# ============================================================================
# Usage: ./compile_figure.sh [figure_name]
#
# Examples:
#   ./compile_figure.sh                          # List all available figures
#   ./compile_figure.sh fig_ch00_complex_plane   # Compile specific figure
#   ./compile_figure.sh complex                  # Fuzzy match (finds first match)
#   ./compile_figure.sh --open complex           # Compile and open PDF
# ============================================================================

FIGURES_DIR="figures"
HARNESS_FILE="figure_harness.tex"
OUTPUT_PDF="figure_harness.pdf"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check for --open flag
OPEN_PDF=false
if [[ "$1" == "--open" ]]; then
    OPEN_PDF=true
    shift
fi

# Function to list all figures
list_figures() {
    echo -e "${BLUE}Available figures:${NC}"
    echo ""

    echo -e "${YELLOW}Chapter 0 - Mathematical Foundations:${NC}"
    ls -1 $FIGURES_DIR/fig_ch00_*.tex 2>/dev/null | sed 's|.*/||; s|\.tex$||' | sed 's/^/  /'
    echo ""

    echo -e "${YELLOW}Chapter 1a - Modeling Fundamentals:${NC}"
    ls -1 $FIGURES_DIR/fig_ch01a_*.tex 2>/dev/null | sed 's|.*/||; s|\.tex$||' | sed 's/^/  /'
    echo ""

    echo -e "${YELLOW}Chapter 1b - Mechanical Systems:${NC}"
    ls -1 $FIGURES_DIR/fig_ch01b_*.tex 2>/dev/null | sed 's|.*/||; s|\.tex$||' | sed 's/^/  /'
    echo ""

    echo -e "${YELLOW}Chapter 1c - Electrical Systems:${NC}"
    ls -1 $FIGURES_DIR/fig_ch01c_*.tex 2>/dev/null | sed 's|.*/||; s|\.tex$||' | sed 's/^/  /'
    echo ""

    echo -e "${YELLOW}Chapter 1d - Electromechanical Systems:${NC}"
    ls -1 $FIGURES_DIR/fig_ch01d_*.tex 2>/dev/null | sed 's|.*/||; s|\.tex$||' | sed 's/^/  /'
    echo ""

    echo -e "${YELLOW}Chapter 1e - Thermal and Fluid Systems:${NC}"
    ls -1 $FIGURES_DIR/fig_ch01e_*.tex 2>/dev/null | sed 's|.*/||; s|\.tex$||' | sed 's/^/  /'
    echo ""

    echo -e "${YELLOW}Chapter 1f - Chemical Systems:${NC}"
    ls -1 $FIGURES_DIR/fig_ch01f_*.tex 2>/dev/null | sed 's|.*/||; s|\.tex$||' | sed 's/^/  /'
    echo ""

    echo -e "${YELLOW}Chapter 1g - Aerospace Systems:${NC}"
    ls -1 $FIGURES_DIR/fig_ch01g_*.tex 2>/dev/null | sed 's|.*/||; s|\.tex$||' | sed 's/^/  /'
    echo ""

    echo -e "${YELLOW}Chapter 1h - Biomedical Systems:${NC}"
    ls -1 $FIGURES_DIR/fig_ch01h_*.tex 2>/dev/null | sed 's|.*/||; s|\.tex$||' | sed 's/^/  /'
    echo ""

    echo -e "${YELLOW}Chapter 1i - Industrial and Computer Systems:${NC}"
    ls -1 $FIGURES_DIR/fig_ch01i_*.tex 2>/dev/null | sed 's|.*/||; s|\.tex$||' | sed 's/^/  /'
    echo ""

    echo -e "${GREEN}Usage: ./compile_figure.sh [figure_name]${NC}"
    echo -e "${GREEN}       ./compile_figure.sh --open [figure_name]${NC}"
}

# If no argument, list figures
if [[ -z "$1" ]]; then
    list_figures
    exit 0
fi

# Find matching figure
SEARCH_TERM="$1"
MATCHING_FILE=$(ls -1 $FIGURES_DIR/*.tex 2>/dev/null | grep -i "$SEARCH_TERM" | head -1)

if [[ -z "$MATCHING_FILE" ]]; then
    echo -e "${RED}Error: No figure found matching '$SEARCH_TERM'${NC}"
    echo ""
    list_figures
    exit 1
fi

FIGURE_NAME=$(basename "$MATCHING_FILE")
FIGURE_PATH="figures/$FIGURE_NAME"

echo -e "${BLUE}Compiling: ${GREEN}$FIGURE_PATH${NC}"

# Create temporary harness with the selected figure
cat > /tmp/figure_harness_temp.tex << 'ENDOFHARNESS'
\documentclass[11pt,letterpaper]{article}
\input{preamble.tex}
\geometry{margin=0.5in}
ENDOFHARNESS

echo "\\newcommand{\\figurefile}{$FIGURE_PATH}" >> /tmp/figure_harness_temp.tex

cat >> /tmp/figure_harness_temp.tex << 'ENDOFHARNESS'
\begin{document}
\begin{center}
    {\Large\bfseries\color{UofSCGarnet} Figure Preview}\\[0.5em]
    {\ttfamily\small\detokenize\expandafter{\figurefile}}\\[1em]
    {\color{UofSC50Black}\hrule}
\end{center}
\vspace{1em}
\input{\figurefile}
\end{document}
ENDOFHARNESS

# Copy temp file to working directory
cp /tmp/figure_harness_temp.tex figure_harness.tex

# Compile
pdflatex -interaction=nonstopmode figure_harness.tex > /dev/null 2>&1

if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}Success! Output: $OUTPUT_PDF${NC}"

    # Open PDF if requested
    if [[ "$OPEN_PDF" == true ]]; then
        if [[ "$OSTYPE" == "darwin"* ]]; then
            open "$OUTPUT_PDF"
        elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
            xdg-open "$OUTPUT_PDF"
        fi
    fi
else
    echo -e "${RED}Compilation failed. Running again with full output:${NC}"
    pdflatex -interaction=nonstopmode figure_harness.tex | tail -30
fi

# Clean up auxiliary files
rm -f figure_harness.aux figure_harness.log figure_harness.out 2>/dev/null
