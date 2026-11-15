
# ==========================================
# SMARTOMR AI - ANSWER KEY MANAGER
# ==========================================

from pathlib import Path
import json
import uuid


# ==========================================
# 1. ANSWER KEY CONFIGURATION
# ==========================================

DEFAULT_OPTIONS = ["A", "B", "C", "D"]

DEFAULT_QUESTIONS = 100

ANSWER_KEY_DIR = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "answer_keys"
)


# ==========================================
# 2. VALIDATE ANSWER KEY
# ==========================================

def validate_answer_key(
    answer_key,
    total_questions=DEFAULT_QUESTIONS,
    options=DEFAULT_OPTIONS
):
    """
    Validate an answer key before saving it.
    """

    errors = []

    if not isinstance(answer_key, dict):
        return {
            "is_valid": False,
            "errors": ["Answer key must be a dictionary."]
        }

    if len(answer_key) != total_questions:
        errors.append(
            f"Expected {total_questions} answers, "
            f"but received {len(answer_key)}."
        )

    # Validate every question
    for question_number in range(1, total_questions + 1):

        if question_number not in answer_key:
            errors.append(
                f"Question {question_number} is missing."
            )

        elif answer_key[question_number] not in options:
            errors.append(
                f"Invalid answer for Question {question_number}: "
                f"{answer_key[question_number]}"
            )

    # Check unexpected question numbers
    for question_number in answer_key:

        if question_number not in range(1, total_questions + 1):
            errors.append(
                f"Invalid question number: {question_number}"
            )

    return {
        "is_valid": len(errors) == 0,
        "errors": errors
    }


# ==========================================
# 3. SAVE ANSWER KEY
# ==========================================

def save_answer_key(
    exam_name,
    answer_key,
    total_questions=DEFAULT_QUESTIONS,
    options=DEFAULT_OPTIONS
):
    """
    Validate and save an answer key as a JSON file.
    """

    # Validate answer key
    validation = validate_answer_key(
        answer_key,
        total_questions,
        options
    )

    if not validation["is_valid"]:
        raise ValueError(
            "Invalid answer key: "
            + "; ".join(validation["errors"])
        )

    # Create answer key directory
    ANSWER_KEY_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Generate unique ID
    answer_key_id = str(uuid.uuid4())

    # Prepare answer key data
    answer_key_data = {
        "answer_key_id": answer_key_id,
        "exam_name": exam_name,
        "total_questions": total_questions,
        "options": options,
        "answer_key": {
            str(question): answer
            for question, answer in answer_key.items()
        }
    }

    # Save JSON file
    file_path = ANSWER_KEY_DIR / f"{answer_key_id}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(
            answer_key_data,
            file,
            indent=4
        )

    return {
        "success": True,
        "answer_key_id": answer_key_id,
        "file_path": str(file_path)
    }


# ==========================================
# 4. LOAD ANSWER KEY
# ==========================================

def load_answer_key(answer_key_id):
    """
    Load an answer key from its JSON file.
    """

    file_path = ANSWER_KEY_DIR / f"{answer_key_id}.json"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Answer key not found: {answer_key_id}"
        )

    with open(file_path, "r", encoding="utf-8") as file:
        answer_key_data = json.load(file)

    # Convert question numbers back to integers
    answer_key_data["answer_key"] = {
        int(question): answer
        for question, answer in answer_key_data["answer_key"].items()
    }

    return answer_key_data


# ==========================================
# 5. LIST ALL ANSWER KEYS
# ==========================================

def list_answer_keys():
    """
    Retrieve all saved answer keys.
    """

    answer_keys = []

    # Check whether directory exists
    if not ANSWER_KEY_DIR.exists():
        return answer_keys

    # Find all JSON files
    json_files = ANSWER_KEY_DIR.glob("*.json")

    for file_path in sorted(json_files):

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Collect answer key information
        answer_key_info = {
            "answer_key_id": data["answer_key_id"],
            "exam_name": data["exam_name"],
            "total_questions": data["total_questions"],
            "options": data["options"],
            "file_path": str(file_path)
        }

        answer_keys.append(answer_key_info)

    return answer_keys

def update_answer_key(answer_key_id, updated_answer_key):
    """
    Update an existing answer key.
    """

    # Load the existing answer key
    data = load_answer_key(answer_key_id)

    # Validate the updated answers
    validation = validate_answer_key(
        updated_answer_key,
        total_questions=data["total_questions"],
        options=data["options"]
    )

    if not validation["is_valid"]:
        raise ValueError(
            "Invalid answer key: " + "; ".join(validation["errors"])
        )

    # Replace the old answers
    data["answer_key"] = {
        str(question): answer
        for question, answer in updated_answer_key.items()
    }

    # Save changes to the same JSON file
    file_path = ANSWER_KEY_DIR / f"{answer_key_id}.json"

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

    return {
        "success": True,
        "answer_key_id": answer_key_id,
        "file_path": str(file_path)
    }

def delete_answer_key(answer_key_id):
    """
    Delete an existing answer key.
    """

    file_path = ANSWER_KEY_DIR / f"{answer_key_id}.json"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Answer key not found: {answer_key_id}"
        )

    file_path.unlink()

    return {
        "success": True,
        "answer_key_id": answer_key_id,
        "message": "Answer key deleted successfully."
    }

# ==========================================
# 5. TESTING
# ==========================================

if __name__ == "__main__":

    # --------------------------------------
    # TEST 1: VALID ANSWER KEY
    # --------------------------------------

    valid_answer_key = {
        question: "A"
        for question in range(1, 101)
    }

    result = validate_answer_key(valid_answer_key)

    print("\n===== VALID ANSWER KEY TEST =====")
    print("Valid:", result["is_valid"])
    print("Errors:", result["errors"])


    # --------------------------------------
    # TEST 2: INVALID ANSWER KEY
    # --------------------------------------

    invalid_answer_key = {
        1: "A",
        2: "B",
        3: "X"
    }

    result = validate_answer_key(invalid_answer_key)

    print("\n===== INVALID ANSWER KEY TEST =====")
    print("Valid:", result["is_valid"])

    for error in result["errors"]:
        print("-", error)


    # --------------------------------------
    # TEST 3: SAVE ANSWER KEY
    # --------------------------------------

    print("\n===== SAVE ANSWER KEY TEST =====")

    sample_answer_key = {
        question: "A"
        for question in range(1, 101)
    }

    saved_result = save_answer_key(
        exam_name="SmartOMR Sample Examination",
        answer_key=sample_answer_key
    )

    print("Saved:", saved_result["success"])
    print("Answer Key ID:", saved_result["answer_key_id"])
    print("File Path:", saved_result["file_path"])


    # --------------------------------------
    # TEST 4: LOAD ANSWER KEY
    # --------------------------------------

    print("\n===== LOAD ANSWER KEY TEST =====")

    loaded_data = load_answer_key(
        saved_result["answer_key_id"]
    )

    print("Exam Name:", loaded_data["exam_name"])
    print("Total Questions:", loaded_data["total_questions"])
    print("Loaded Answers:", len(loaded_data["answer_key"]))
    print("Question 1 Answer:", loaded_data["answer_key"][1])

    print("\nAll tests completed!")


    # --------------------------------------
    # TEST 5: LIST ALL ANSWER KEYS
    # --------------------------------------

    print("\n===== LIST ANSWER KEYS TEST =====")

    all_answer_keys = list_answer_keys()

    print("Total Saved Answer Keys:", len(all_answer_keys))

    for index, key in enumerate(all_answer_keys, start=1):

        print(f"\nAnswer Key {index}")
        print("Exam Name:", key["exam_name"])
        print("Answer Key ID:", key["answer_key_id"])
        print("Total Questions:", key["total_questions"])

    print("\nAnswer key listing completed!")

    print("\n===== UPDATE ANSWER KEY TEST =====")

    # Create updated answers
    updated_answers = {
        question: "A"
        for question in range(1, 101)
    }

    # Change a few answers
    updated_answers[1] = "B"
    updated_answers[2] = "C"
    updated_answers[3] = "D"

    update_result = update_answer_key(
        saved_result["answer_key_id"],
        updated_answers
    )

    print("Update Successful:", update_result["success"])

    # Verify updated answers
    updated_data = load_answer_key(
        saved_result["answer_key_id"]
    )

    print("Updated Question 1:", updated_data["answer_key"][1])
    print("Updated Question 2:", updated_data["answer_key"][2])
    print("Updated Question 3:", updated_data["answer_key"][3])

    print("\nAnswer key update completed!")

    print("\n===== DELETE ANSWER KEY TEST =====")

    delete_result = delete_answer_key(
        saved_result["answer_key_id"]
    )

    print("Delete Successful:", delete_result["success"])
    print("Message:", delete_result["message"])

    # Verify deletion
    try:
        load_answer_key(saved_result["answer_key_id"])
    except FileNotFoundError:
        print("Verification: Answer key no longer exists.")

    print("\nAnswer key deletion completed!")