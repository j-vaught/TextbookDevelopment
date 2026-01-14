#!/bin/bash
# =============================================================================
# Control Systems Textbook - Chapter Validation Script
# =============================================================================
# Usage: ./validate_chapter.sh <chapter_file.tex>
#        ./validate_chapter.sh --all    (validates all chapters)
# =============================================================================

# Colors for output
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
CRITICAL_ERRORS=0
STYLE_VIOLATIONS=0
QUALITY_WARNINGS=0

# Helper function to count pattern occurrences
count_pattern() {
    local pattern="$1"
    local file="$2"
    local count=$(grep -cE "$pattern" "$file" 2>/dev/null || true)
    echo "${count:-0}"
}

# Function to print section headers
print_header() {
    echo ""
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
}

report_critical() {
    echo -e "${RED}[CRITICAL]${NC} $1"
    ((CRITICAL_ERRORS++)) || true
}

report_style() {
    echo -e "${YELLOW}[STYLE]${NC} $1"
    ((STYLE_VIOLATIONS++)) || true
}

report_quality() {
    echo -e "${BLUE}[QUALITY]${NC} $1"
    ((QUALITY_WARNINGS++)) || true
}

report_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

report_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# =============================================================================
# Main Validation Function
# =============================================================================

validate_file() {
    local FILE="$1"
    local FILENAME=$(basename "$FILE")

    print_header "Validating: $FILENAME"

    if [ ! -f "$FILE" ]; then
        report_critical "File not found: $FILE"
        return
    fi

    # =========================================================================
    # CRITICAL CHECKS
    # =========================================================================

    echo ""
    echo "── Critical Checks ──"

    # Check for wrong algorithm syntax (uppercase)
    local WRONG_ALGO=$(count_pattern '\\(STATE|WHILE|IF|FOR|RETURN|REQUIRE|ENSURE|ENDIF|ENDWHILE|ENDFOR|ELSIF)[^a-z]' "$FILE")
    if [ "$WRONG_ALGO" -gt 0 ] 2>/dev/null; then
        report_critical "Wrong algorithm syntax (uppercase): $WRONG_ALGO instances"
    else
        report_pass "Algorithm syntax correct (algpseudocode)"
    fi

    # Check for lstlisting (code blocks)
    local CODE_BLOCKS=$(count_pattern '\\begin\{lstlisting\}' "$FILE")
    if [ "$CODE_BLOCKS" -gt 0 ] 2>/dev/null; then
        report_critical "Code blocks found (lstlisting): $CODE_BLOCKS - use algorithm instead"
    else
        report_pass "No language-specific code blocks"
    fi

    # Check for standalone document class
    local DOC_CLASS=$(count_pattern '\\documentclass' "$FILE")
    if [ "$DOC_CLASS" -gt 0 ] 2>/dev/null; then
        report_critical "Chapter contains \\documentclass - should be removed"
    else
        report_pass "No standalone document class"
    fi

    # Check for abstract environment
    local ABSTRACT=$(count_pattern '\\begin\{abstract\}' "$FILE")
    if [ "$ABSTRACT" -gt 0 ] 2>/dev/null; then
        report_critical "Abstract environment found - not valid in book chapters"
    else
        report_pass "No abstract environment"
    fi

    # Check for placeholder figures
    local PLACEHOLDERS=$(grep -ciE 'TODO|PLACEHOLDER|\[FIGURE\]|\[INSERT' "$FILE" 2>/dev/null || echo "0")
    if [ "$PLACEHOLDERS" -gt 0 ] 2>/dev/null; then
        report_critical "Placeholder content found: $PLACEHOLDERS instances"
    else
        report_pass "No placeholder content"
    fi

    # =========================================================================
    # STYLE CHECKS
    # =========================================================================

    echo ""
    echo "── Style Checks ──"

    # Check for bullet points (itemize)
    local ITEMIZE=$(count_pattern '\\begin\{itemize\}' "$FILE")
    if [ "$ITEMIZE" -gt 2 ] 2>/dev/null; then
        report_style "Excessive bullet points (itemize): $ITEMIZE - convert to prose/tables"
    elif [ "$ITEMIZE" -gt 0 ] 2>/dev/null; then
        report_quality "Some bullet points found: $ITEMIZE (acceptable in lab/procedures)"
    else
        report_pass "No bullet point lists"
    fi

    # Check for rounded corners
    local ROUNDED=$(count_pattern 'rounded corners' "$FILE")
    if [ "$ROUNDED" -gt 0 ] 2>/dev/null; then
        report_style "Rounded corners found: $ROUNDED - use sharp corners"
    else
        report_pass "Sharp corners used throughout"
    fi

    # Check for hline in tables
    local HLINE=$(count_pattern '\\hline' "$FILE")
    if [ "$HLINE" -gt 0 ] 2>/dev/null; then
        report_style "\\hline found: $HLINE - use booktabs (\\toprule/\\midrule/\\bottomrule)"
    else
        report_pass "Booktabs style tables"
    fi

    # =========================================================================
    # STRUCTURAL CHECKS
    # =========================================================================

    echo ""
    echo "── Structural Checks ──"

    # Check for chapter declaration
    local HAS_CHAPTER=$(count_pattern '\\chapter\{' "$FILE")
    if [ "$HAS_CHAPTER" -eq 0 ] 2>/dev/null; then
        report_critical "No \\chapter{} declaration found"
    else
        report_pass "Chapter declaration present"
    fi

    # Check for historical section
    local HAS_HIST=$(grep -ci '\\section{.*[Hh]istor' "$FILE" 2>/dev/null || echo "0")
    if [ "$HAS_HIST" -eq 0 ] 2>/dev/null; then
        report_style "No Historical Context section found"
    else
        report_pass "Historical section present"
    fi

    # Check for lab section
    local HAS_LAB=$(grep -ciE '\\section\{.*(Lab|Experiment)' "$FILE" 2>/dev/null || echo "0")
    if [ "$HAS_LAB" -eq 0 ] 2>/dev/null; then
        report_style "No Laboratory Experiment section found"
    else
        report_pass "Laboratory section present"
    fi

    # Check for exercises section
    local HAS_EX=$(grep -ci '\\section{.*[Ee]xercise' "$FILE" 2>/dev/null || echo "0")
    if [ "$HAS_EX" -eq 0 ] 2>/dev/null; then
        report_style "No Exercises section found"
    else
        report_pass "Exercises section present"
        # Check for newpage before exercises
        if grep -B2 '\\section{.*[Ee]xercise' "$FILE" 2>/dev/null | grep -q '\\newpage'; then
            report_pass "Exercises on new page"
        else
            report_style "Exercises section should start with \\newpage"
        fi
    fi

    # =========================================================================
    # QUALITY METRICS
    # =========================================================================

    echo ""
    echo "── Quality Metrics ──"

    local NUM_FIGURES=$(count_pattern '\\begin\{figure\}' "$FILE")
    if [ "$NUM_FIGURES" -lt 3 ] 2>/dev/null; then
        report_quality "Few figures: $NUM_FIGURES (recommend >= 5)"
    else
        report_pass "Adequate figures: $NUM_FIGURES"
    fi

    local NUM_EXERCISES=$(count_pattern '\\begin\{exercise\}' "$FILE")
    if [ "$NUM_EXERCISES" -lt 10 ] 2>/dev/null; then
        report_quality "Few exercises: $NUM_EXERCISES (recommend >= 15)"
    else
        report_pass "Good exercise count: $NUM_EXERCISES"
    fi

    local NUM_EXAMPLES=$(count_pattern '\\begin\{examplebox\}' "$FILE")
    if [ "$NUM_EXAMPLES" -lt 2 ] 2>/dev/null; then
        report_quality "Few worked examples: $NUM_EXAMPLES (recommend >= 3)"
    else
        report_pass "Good example count: $NUM_EXAMPLES"
    fi

    local NUM_HIST=$(count_pattern '\\begin\{historicalbox\}' "$FILE")
    if [ "$NUM_HIST" -lt 1 ] 2>/dev/null; then
        report_quality "No historical boxes (recommend >= 1)"
    else
        report_pass "Historical content boxes: $NUM_HIST"
    fi

    # Additional info
    local NUM_EQ=$(count_pattern '\\begin\{equation' "$FILE")
    local NUM_ALIGN=$(count_pattern '\\begin\{align' "$FILE")
    local TOTAL_EQ=$((NUM_EQ + NUM_ALIGN))
    report_info "Display equations: $TOTAL_EQ"

    local NUM_ALGO=$(count_pattern '\\begin\{algorithm\}' "$FILE")
    report_info "Algorithms: $NUM_ALGO"

    local LINE_COUNT=$(wc -l < "$FILE" | tr -d ' ')
    report_info "Total lines: $LINE_COUNT"
}

# =============================================================================
# Main
# =============================================================================

print_header "Control Systems Textbook - Chapter Validator"
echo "Standards Document: CHAPTER_STANDARDS.md"
echo "Validation Date: $(date)"

if [ "$1" == "--all" ]; then
    CHAPTERS=$(find . -path "./Part_*" -name "ch*.tex" -type f | sort)
    for chapter in $CHAPTERS; do
        validate_file "$chapter"
    done
elif [ -n "$1" ]; then
    validate_file "$1"
else
    echo "Usage: $0 <chapter_file.tex>"
    echo "       $0 --all"
    exit 1
fi

# =============================================================================
# Summary
# =============================================================================

print_header "VALIDATION SUMMARY"

echo ""
echo -e "Critical Errors:    ${RED}$CRITICAL_ERRORS${NC}"
echo -e "Style Violations:   ${YELLOW}$STYLE_VIOLATIONS${NC}"
echo -e "Quality Warnings:   ${BLUE}$QUALITY_WARNINGS${NC}"
echo ""

if [ "$CRITICAL_ERRORS" -gt 0 ]; then
    echo -e "${RED}STATUS: FAILED - Critical errors must be fixed${NC}"
    exit 1
elif [ "$STYLE_VIOLATIONS" -gt 0 ]; then
    echo -e "${YELLOW}STATUS: NEEDS WORK - Style violations should be fixed${NC}"
    exit 2
elif [ "$QUALITY_WARNINGS" -gt 0 ]; then
    echo -e "${BLUE}STATUS: ACCEPTABLE - Quality improvements recommended${NC}"
    exit 3
else
    echo -e "${GREEN}STATUS: PASSED - All checks passed${NC}"
    exit 0
fi
