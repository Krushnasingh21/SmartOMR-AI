
from database.exam_manager import create_exam, delete_exam

from database.answer_key_manager import (
    create_answer_key,
    get_answer_key,
    get_all_answer_keys,
    update_answer_key,
    delete_answer_key
)


def run_tests():

    exam_id = None

    try:

        # ======================================
        # TEST 1: CREATE TEMPORARY EXAM
        # ======================================

        print("\n===== TEST 1: CREATE EXAM =====")

        exam = create_exam(
            exam_name="Temporary Answer Key Test",
            total_questions=5,
            options_per_question=4,
            marks_per_correct=1.0,
            negative_marking=0.25
        )

        exam_id = exam["exam_id"]

        print("Temporary Exam ID:", exam_id)
        print("Exam created successfully!")

        # ======================================
        # TEST 2: CREATE ANSWER KEY
        # ======================================

        print("\n===== TEST 2: CREATE ANSWER KEY =====")

        answers = {
            1: "A",
            2: "C",
            3: "B",
            4: "D",
            5: "A"
        }

        result = create_answer_key(
            exam_id=exam_id,
            answers=answers
        )

        print("Success:", result["success"])
        print("Answer Key ID:", result["answer_key_id"])
        print("Answers:", result["answers"])

        assert result["success"] is True

        # ======================================
        # TEST 3: GET ANSWER KEY
        # ======================================

        print("\n===== TEST 3: GET ANSWER KEY =====")

        saved_key = get_answer_key(exam_id)

        print("Retrieved Answers:", saved_key["answers"])

        assert saved_key["answers"] == answers

        # ======================================
        # TEST 4: GET ALL ANSWER KEYS
        # ======================================

        print("\n===== TEST 4: GET ALL ANSWER KEYS =====")

        all_keys = get_all_answer_keys()

        test_keys = [
            key for key in all_keys
            if key["exam_id"] == exam_id
        ]

        print("Total Answer Keys:", len(all_keys))
        print("Test Answer Key Found:", len(test_keys) == 1)

        assert len(test_keys) == 1

        # ======================================
        # TEST 5: UPDATE ANSWER KEY
        # ======================================

        print("\n===== TEST 5: UPDATE ANSWER KEY =====")

        updated_answers = {
            1: "B",
            2: "A",
            3: "C",
            4: "D",
            5: "B"
        }

        update_result = update_answer_key(
            exam_id=exam_id,
            updated_answers=updated_answers
        )

        print("Update Success:", update_result["success"])

        updated_key = get_answer_key(exam_id)

        print("Updated Answers:", updated_key["answers"])

        assert updated_key["answers"] == updated_answers

        # ======================================
        # TEST 6: INVALID ANSWER VALIDATION
        # ======================================

        print("\n===== TEST 6: INVALID ANSWER VALIDATION =====")

        # Test 6A: Missing questions

        incomplete_answers = {
            1: "A",
            2: "B"
        }

        try:

            update_answer_key(
                exam_id=exam_id,
                updated_answers=incomplete_answers
            )

            raise AssertionError(
                "Incomplete answer key was unexpectedly accepted."
            )

        except ValueError as error:

            assert "Missing answers" in str(error)

            print("Incomplete answer key rejected:", error)

        # Test 6B: Invalid option

        invalid_option_answers = {
            1: "A",
            2: "B",
            3: "C",
            4: "D",
            5: "E"
        }

        try:

            update_answer_key(
                exam_id=exam_id,
                updated_answers=invalid_option_answers
            )

            raise AssertionError(
                "Invalid option was unexpectedly accepted."
            )

        except ValueError as error:

            assert "Invalid option" in str(error)

            print("Invalid option rejected:", error)

        # ======================================
        # TEST 7: DELETE ANSWER KEY
        # ======================================

        print("\n===== TEST 7: DELETE ANSWER KEY =====")

        delete_result = delete_answer_key(exam_id)

        print("Delete Success:", delete_result["success"])

        deleted_key = get_answer_key(exam_id)

        print("Answer Key Still Exists:", deleted_key is not None)

        assert deleted_key is None

        print("\nALL ANSWER KEY TESTS PASSED!")

    finally:

        # ======================================
        # CLEANUP TEMPORARY TEST RECORDS
        # ======================================

        if exam_id is not None:

            try:

                existing_key = get_answer_key(exam_id)

                if existing_key is not None:
                    delete_answer_key(exam_id)

                delete_exam(exam_id)

                print("\nTemporary test examination cleaned up.")

            except Exception as error:

                print("\nCleanup warning:", error)


if __name__ == "__main__":
    run_tests()
