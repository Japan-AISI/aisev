from inspect_ai.scorer import model_graded_qa, choice, Scorer, exact
from src.utils.logger import logger


class ScorerProvider():
    def __init__(self):
        logger.info("ScorerProviderの初期化が完了しました。")

    def get_exact_match_scorer(self, prompt: str | None = None) -> Scorer:
        """
        Get a scorer for exact match evaluation
        (No custom prompt)

        Returns:
            Scorer: Scorer for exact match evaluation
        """
        logger.info("get_exact_match_scorer: 完全一致スコアラーを取得します。")
        try:
            return exact()
        except Exception as e:
            logger.error(f"get_exact_match_scorer: スコアラー取得中にエラー: {e}")
            return None

    def get_graded_qa_scorer(self, model: str = "openai/gpt-4o", prompt: str | None = None, grade_pattern: str | None = None) -> Scorer:
        """
        Get a scorer for graded QA evaluation
        Default prompt for model_graded_qa is used if prompt is None.

        Returns:
            Scorer: Scorer for graded QA evaluation
        """
        logger.info(f"get_graded_qa_scorer: モデル {model} 用スコアラーを取得します。")
        if grade_pattern is None:
            logger.info("get_graded_qa_scorer: grade_pattern: default grade pattern")
        else:
            logger.info(f"get_graded_qa_scorer: grade_pattern: {grade_pattern}")
        if prompt is None:
            prompt = ""
        try:
            return model_graded_qa(
                model=model,
                grade_pattern=grade_pattern,
                template=prompt + """
You are assessing a submitted answer on a given task based on a criterion. Here is the data:

[BEGIN DATA]
***
[Task]: {question}
***
[Submission]: {answer}
***
[Criterion]: {criterion}
***
[END DATA]

Does the submission meet the criterion?

{instructions}
""")
        except Exception as e:
            logger.error(f"get_graded_qa_scorer: スコアラー取得中にエラー: {e}")
            return None

    def get_requirement_scorer(self, model: str = "openai/gpt-4o", prompt: str | None = None, grade_pattern: str | None = None) -> Scorer:
        """
        Get a scorer for evaluating whether requirements are met

        Args:
            model: Model name to use for evaluation

        Returns:
            Scorer: Scorer for requirement evaluation
        """
        logger.info(f"get_requirement_scorer: モデル {model} 用要件スコアラーを取得します。")
        if grade_pattern is None:
            logger.info("get_requirement_scorer: grade_pattern: default grade pattern")
        else:
            logger.info(f"get_requirement_scorer: grade_pattern: {grade_pattern}")
        if prompt is None:
            prompt = ""
        try:
            return model_graded_qa(
                model=model,
                grade_pattern=grade_pattern,
                template=prompt +"""  
質問: {question}  
回答: {answer}  
評価基準: {criterion}  
    
{instructions}  
""",
                instructions="""  
回答が評価基準を満たしているかを判断してください。  
思考過程を示した後、以下の形式で評価してください：  
- 完全に正しい場合: GRADE: C  
- 間違っている場合: GRADE: I  
"""
            )
        except Exception as e:
            logger.error(f"get_requirement_scorer: スコアラー取得中にエラー: {e}")
            return None

    def get_multiple_choice_scorer(self) -> Scorer:
        """
        Get a scorer for multiple choice questions
        (No custom prompt)

        Returns:
            Scorer: Scorer for multiple choice questions
        """
        logger.info("get_multiple_choice_scorer: 多肢選択スコアラーを取得します。")
        try:
            return choice()
        except Exception as e:
            logger.error(f"get_multiple_choice_scorer: スコアラー取得中にエラー: {e}")
            return None
