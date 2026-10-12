from eval.harness.dataset import MAX_PHRASE_LENGTH, check_schema, parse_questions

PAPERS = {"gfs", "raft"}


def dataset(*questions):
    return {"version": "v0", "questions": list(questions)}


def answerable(**overrides):
    question = {
        "id": "q01",
        "paper": "gfs",
        "category": "wording",
        "question": "What is a chunk?",
        "evidence": ["a fixed-size chunk"],
    }
    question.update(overrides)
    return question


def test_valid_dataset_has_no_problems():
    raw = dataset(
        answerable(),
        {"id": "q02", "category": "unanswerable", "question": "Which language is it written in?"},
    )

    assert check_schema(raw, PAPERS) == []
    assert [q.answerable for q in parse_questions(raw)] == [True, False]


def test_empty_template_is_valid():
    assert check_schema(dataset(), PAPERS) == []


def test_missing_top_level_keys():
    assert check_schema({"questions": []}, PAPERS) != []


def test_duplicate_ids_are_reported():
    problems = check_schema(dataset(answerable(), answerable()), PAPERS)

    assert any("duplicate id" in problem for problem in problems)


def test_unknown_paper_and_category_are_reported():
    problems = check_schema(dataset(answerable(paper="bigtable", category="trivia")), PAPERS)

    assert any("category" in problem for problem in problems)


def test_unknown_paper_is_reported():
    problems = check_schema(dataset(answerable(paper="bigtable")), PAPERS)

    assert any("paper" in problem for problem in problems)


def test_misspelled_field_is_reported():
    question = answerable()
    question["evidance"] = question.pop("evidence")

    problems = check_schema(dataset(question), PAPERS)

    assert any("unknown field" in problem for problem in problems)


def test_answerable_question_needs_evidence():
    problems = check_schema(dataset(answerable(evidence=[])), PAPERS)

    assert any("evidence" in problem for problem in problems)


def test_unanswerable_question_must_not_have_evidence():
    question = answerable(category="unanswerable")

    problems = check_schema(dataset(question), PAPERS)

    assert any("no `evidence`" in problem for problem in problems)


def test_long_phrase_is_reported():
    phrase = "x" * (MAX_PHRASE_LENGTH + 1)

    problems = check_schema(dataset(answerable(evidence=[phrase])), PAPERS)

    assert any("max is" in problem for problem in problems)
