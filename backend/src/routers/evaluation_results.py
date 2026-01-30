from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src.db.define_tables import EvaluationResult
from src.manager.evaluation_results_manager import EvaluationResultsManager
from src.db.session import get_db
from pydantic import BaseModel
from typing import List, Optional, Any
from datetime import date
from src.utils.logger import logger

router = APIRouter()


class QualitativeResultItem(BaseModel):
    questionId: int
    answer: str
    text: str
    perspective: str
    scoreRate: float
    secondGoal: str
    gsnLeaf: str
    gsnName: str


class QualitativeResultRequest(BaseModel):
    evaluationId: int
    results: List[QualitativeResultItem]


class QuantitativeResultRequest(BaseModel):
    evaluationId: int
    results: Any


class EvaluationResultCreateRequest(BaseModel):
    name: str
    evaluation_id: int
    target_ai_model_id: int
    evaluator_ai_model_id: int
    quantitative_eval_state: Optional[str] = None
    quantitative_results: Optional[Any] = None
    qualitative_results: Optional[Any] = None


# Add Pydantic models
class EvaluationResultResponse(BaseModel):
    id: int
    name: str
    created_date: str
    evaluation_name: str
    target_ai_model_name: str
    evaluator_ai_model_name: str
    quantitative_results: Optional[Any] = None
    qualitative_results: Optional[Any] = None
    quantitative_eval_state: Optional[str] = "running"

    class Config:
        from_attributes = True


class QuantitativeRequest(BaseModel):
    evaluation_id: int
    target_ai_model_id: int
    evaluator_ai_model_id: int


@router.get("/evaluation_results/", response_model=List[EvaluationResultResponse])
def get_all_evaluation_results(
    project_key: Optional[str] = Query(None),
    api_key: Optional[str] = Query(None),
    gpt_profile_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get all evaluation results
    """
    logger.info("get_all_evaluation_results: 全ての評価結果取得処理を開始します。")
    try:
        evaluation_results = EvaluationResultsManager.get_all_evaluation_results(
            project_key=project_key,
            api_key=api_key,
            gpt_profile_id=gpt_profile_id,
            db=db,
        )
        if not evaluation_results:
            logger.info("get_all_evaluation_results: 評価結果が見つかりませんでした。")
            raise HTTPException(
                status_code=404, detail="No evaluation results found")
        # Convert to YYYY-MM-DD hh:mm:ss format from created_date
        for result in evaluation_results:
            result["created_date"] = result["created_date"].strftime(
                "%Y-%m-%d %H:%M:%S")
        logger.info(
            f"get_all_evaluation_results: {len(evaluation_results)}件の評価結果を取得しました。")
        return evaluation_results
    except Exception as e:
        logger.error(f"get_all_evaluation_results: 取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="評価結果一覧の取得中にエラーが発生しました。")


@router.post("/evaluation_result/", response_model=int)
def create_evaluation_result(request: EvaluationResultCreateRequest, db: Session = Depends(get_db)):
    """
    The following is normally empty
    quantitative_eval_state
    quantitative_results
    qualitative_results
    """
    logger.info(
        f"create_evaluation_result: 評価結果 '{request.name}' の作成処理を開始します。")
    eval_result = EvaluationResult(
        name=request.name,
        evaluation_id=request.evaluation_id,
        target_ai_model_id=request.target_ai_model_id,
        evaluator_ai_model_id=request.evaluator_ai_model_id,
        quantitative_eval_state="running",
        quantitative_results=request.quantitative_results,
        qualitative_results=request.qualitative_results
    )
    try:
        # NOTE: create a empty result
        result_id = EvaluationResultsManager.create_evaluation_result(
            db, eval_result)
        logger.info(
            f"create_evaluation_result: 評価結果(ID={result_id}) の作成が完了しました。")
        return result_id
    except Exception as e:
        logger.error(f"create_evaluation_result: 作成処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="評価結果の作成中にエラーが発生しました。")


@router.post("/evaluation_results/{eval_result_id}/quantitative_result", response_model=int)
def exec_quantitative_evaluation(
    eval_result_id: int,
    request: QuantitativeRequest,
    db: Session = Depends(get_db)
):
    """
    request must contains:
        evaluation_id: int
        target_ai_model_id: int
        evaluator_ai_model_id: int
    """
    logger.info(
        f"exec_quantitative_evaluation: ID={eval_result_id} の定量評価処理を開始します。")
    try:
        dataset_ids = EvaluationResultsManager.get_dataset_ids_from_evaluation_id(
            db, request.evaluation_id)

        # Search for UseGSN by evaluation_id
        use_gsn = EvaluationResultsManager.get_gsn_by_evaluation_id(
            db, request.evaluation_id)
        logger.info(f"exec_quantitative_evaluation: UseGSN={use_gsn}")
        if not dataset_ids and not use_gsn:
            logger.info("exec_quantitative_evaluation: データセットが見つかりませんでした。")
            raise HTTPException(
                status_code=404, detail="No datasets found for the evaluation")

        # NOTE: Execute quantitative evaluation in background and return result_id when complete
        result_id = EvaluationResultsManager.register_quantitative_result(
            db, eval_result_id, dataset_ids, request.target_ai_model_id, request.evaluator_ai_model_id, use_gsn)

        logger.info(
            f"exec_quantitative_evaluation: 定量評価(ID={result_id}) の登録が完了しました。")
        return result_id
    except ValueError:
        logger.error(
            "exec_quantitative_evaluation: 評価用データセットまたはモデルが見つかりませんでした。")
        raise HTTPException(
            status_code=404, detail="No datasets found for the evaluation")
    except Exception as e:
        logger.error(f"exec_quantitative_evaluation: 定量評価処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="定量評価の登録中にエラーが発生しました。")


@router.post("/evaluation_results/{eval_result_id}/qualitative_result", response_model=int)
def register_qualitative_result(eval_result_id: int, qualitative_result: QualitativeResultRequest, db: Session = Depends(get_db)):
    logger.info(
        f"register_qualitative_result: ID={eval_result_id} の定性評価結果登録処理を開始します。")
    try:
        result_id = EvaluationResultsManager.register_qualitative_result(
            db, eval_result_id, qualitative_result.model_dump())
        logger.info(
            f"register_qualitative_result: 定性評価結果(ID={result_id}) の登録が完了しました。")
        return result_id
    except ValueError:
        logger.error("register_qualitative_result: EvaluationResultが見つかりません。")
        raise HTTPException(
            status_code=404, detail="EvaluationResult not found")
    except Exception as e:
        logger.error(f"register_qualitative_result: 登録処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="定性評価結果の登録中にエラーが発生しました。")


@router.get("/evaluation_results/{eval_result_id}/status", response_model=str)
def get_eval_status(eval_result_id: int, db: Session = Depends(get_db)):
    logger.info(f"get_eval_status: ID={eval_result_id} のステータス取得処理を開始します。")
    try:
        status = EvaluationResultsManager.get_eval_status(db, eval_result_id)
        if status is None:
            logger.info("get_eval_status: EvaluationResultが見つかりません。")
            raise HTTPException(
                status_code=404, detail="EvaluationResult not found")
        logger.info(f"get_eval_status: ステータスは '{status}' です。")
        return status
    except ValueError:
        logger.error("get_eval_status: EvaluationResultが見つかりません。")
        raise HTTPException(
            status_code=404, detail="EvaluationResult not found")
    except Exception as e:
        logger.error(f"get_eval_status: ステータス取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="ステータス取得中にエラーが発生しました。")


@router.get("/evaluation_results/{eval_result_id}/10perspective_scores", response_model=dict)
def get_10perspective_scores(eval_result_id: int, db: Session = Depends(get_db)):
    """
    Get 10-perspective scores
    """
    logger.info(
        f"get_10perspective_scores: ID={eval_result_id} の10観点スコア取得処理を開始します。")
    try:
        scores = EvaluationResultsManager.calculate_10perspective_scores(
            db, eval_result_id)
        logger.info("get_10perspective_scores: 10観点スコアの取得が完了しました。")
        return scores
    except ValueError:
        logger.error("get_10perspective_scores: EvaluationResultが見つかりません。")
        raise HTTPException(
            status_code=404, detail="EvaluationResult not found")
    except Exception as e:
        logger.error(f"get_10perspective_scores: 取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="10観点スコアの取得中にエラーが発生しました。")


@router.get("/evaluation_results/{eval_result_id}/detail", response_model=Any)
def get_evaluation_result_detail(eval_result_id: int, db: Session = Depends(get_db)):
    """
    Get detailed information for the specified evaluation result ID and return quantitative_results and qualitative_results in a readable format
    """
    logger.info(
        f"get_evaluation_result_detail: ID={eval_result_id} の詳細取得処理を開始します。")
    try:
        detail = EvaluationResultsManager.get_result_detail(db, eval_result_id)
        logger.info("get_evaluation_result_detail: 詳細取得が完了しました。")
        return detail
    except ValueError:
        logger.exception(
            "get_evaluation_result_detail: EvaluationResultが見つかりません。")
        raise HTTPException(
            status_code=404, detail="EvaluationResult not found")
    except Exception as e:
        logger.exception(
            f"get_evaluation_result_detail: 詳細取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="評価結果詳細の取得中にエラーが発生しました。")
