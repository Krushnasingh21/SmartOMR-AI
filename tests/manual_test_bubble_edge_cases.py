
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.bubble_detection import (
    classify_bubble,
    extract_answer,
    EMPTY_THRESHOLD,
    FILLED_THRESHOLD
)


# ==========================================
# SMARTOMR AI - BUBBLE EDGE CASE TESTING
# ==========================================

def create_bubble(option, status):

    return {
        "option": option,
        "status": status,
        "fill_percentage": 0.0
    }


def run_test():

    print("\n===================================")
    print(" SMARTOMR AI - EDGE CASE TESTING")
    print("===================================\n")

    passed = 0
    failed = 0

    # ======================================
    # TEST 1: EMPTY BUBBLE
    # ======================================

    print("TEST 1: Empty Bubble")

    result = classify_bubble(5)

    expected = "EMPTY"

    if result == expected:
        print("PASS: Empty bubble correctly identified.")
        passed += 1
    else:
        print("FAIL:", result)
        failed += 1

    # ======================================
    # TEST 2: DARKLY FILLED BUBBLE
    # ======================================

    print("\nTEST 2: Darkly Filled Bubble")

    result = classify_bubble(80)

    expected = "FILLED"

    if result == expected:
        print("PASS: Dark fill correctly identified.")
        passed += 1
    else:
        print("FAIL:", result)
        failed += 1

    # ======================================
    # TEST 3: PARTIALLY FILLED BUBBLE
    # ======================================

    print("\nTEST 3: Partially Filled Bubble")

    result = classify_bubble(30)

    expected = "UNCERTAIN"

    if result == expected:
        print("PASS: Partial fill marked for review.")
        passed += 1
    else:
        print("FAIL:", result)
        failed += 1

    # ======================================
    # TEST 4: LIGHTLY FILLED BUBBLE
    # ======================================

    print("\nTEST 4: Lightly Filled Bubble")

    result = classify_bubble(18)

    expected = "EMPTY"

    if result == expected:
        print("PASS: Low fill percentage classified as empty.")
        passed += 1
    else:
        print("FAIL:", result)
        failed += 1

    # ======================================
    # TEST 5: MULTIPLE MARKED ANSWERS
    # ======================================

    print("\nTEST 5: Multiple Marked Answers")

    bubbles = [
        create_bubble("A", "FILLED"),
        create_bubble("B", "EMPTY"),
        create_bubble("C", "FILLED"),
        create_bubble("D", "EMPTY")
    ]

    result = extract_answer(bubbles)

    expected = "MULTIPLE_MARKS"

    if result == expected:
        print("PASS: Multiple marks correctly identified.")
        passed += 1
    else:
        print("FAIL:", result)
        failed += 1

    # ======================================
    # TEST 6: ONE CORRECT MARK
    # ======================================

    print("\nTEST 6: Single Mark")

    bubbles = [
        create_bubble("A", "EMPTY"),
        create_bubble("B", "FILLED"),
        create_bubble("C", "EMPTY"),
        create_bubble("D", "EMPTY")
    ]

    result = extract_answer(bubbles)

    expected = "B"

    if result == expected:
        print("PASS: Single answer correctly extracted.")
        passed += 1
    else:
        print("FAIL:", result)
        failed += 1

    # ======================================
    # TEST 7: ALL BUBBLES EMPTY
    # ======================================

    print("\nTEST 7: Unanswered Question")

    bubbles = [
        create_bubble("A", "EMPTY"),
        create_bubble("B", "EMPTY"),
        create_bubble("C", "EMPTY"),
        create_bubble("D", "EMPTY")
    ]

    result = extract_answer(bubbles)

    expected = "UNANSWERED"

    if result == expected:
        print("PASS: Unanswered question identified.")
        passed += 1
    else:
        print("FAIL:", result)
        failed += 1

    # ======================================
    # TEST 8: UNCERTAIN MARK
    # ======================================

    print("\nTEST 8: Uncertain Mark")

    bubbles = [
        create_bubble("A", "EMPTY"),
        create_bubble("B", "UNCERTAIN"),
        create_bubble("C", "EMPTY"),
        create_bubble("D", "EMPTY")
    ]

    result = extract_answer(bubbles)

    expected = "REVIEW_REQUIRED"

    if result == expected:
        print("PASS: Uncertain answer flagged for review.")
        passed += 1
    else:
        print("FAIL:", result)
        failed += 1

    # ======================================
    # TEST 9: FILLED + UNCERTAIN MARK
    # ======================================

    print("\nTEST 9: Filled and Uncertain Marks")

    bubbles = [
        create_bubble("A", "FILLED"),
        create_bubble("B", "UNCERTAIN"),
        create_bubble("C", "EMPTY"),
        create_bubble("D", "EMPTY")
    ]

    result = extract_answer(bubbles)

    expected = "REVIEW_REQUIRED"

    if result == expected:
        print("PASS: Uncertain combination flagged.")
        passed += 1
    else:
        print("FAIL:", result)
        failed += 1

    # ======================================
    # FINAL SUMMARY
    # ======================================

    print("\n===================================")
    print("       FINAL TEST SUMMARY")
    print("===================================")

    print("Total Tests:", passed + failed)
    print("Passed:", passed)
    print("Failed:", failed)

    print("\nClassification Thresholds:")
    print("Empty:", f"Below {EMPTY_THRESHOLD}%")
    print(
        "Uncertain:",
        f"{EMPTY_THRESHOLD}% to below {FILLED_THRESHOLD}%"
    )
    print("Filled:", f"{FILLED_THRESHOLD}% and above")

    if failed == 0:
        print("\nSUCCESS: All edge-case logic tests passed!")
    else:
        print("\nWARNING: Some edge-case tests failed.")

    print("\nEdge-case testing completed.")


if __name__ == "__main__":

    run_test()
