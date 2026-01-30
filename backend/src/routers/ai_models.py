from typing import Optional
from fastapi import APIRouter, Depends, Query, Request, HTTPException
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.manager.ai_model_manager import AIModelManager
from src.utils.logger import logger

router = APIRouter()

@router.get("/ai_models")
def list_ai_models(
    project_key: Optional[str] = Query(None),
    api_key: Optional[str] = Query(None),
    gpt_profile_id: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Get AI models.
    - No query params → return all models
    - With credentials → return filtered models
    """
    logger.info(
        "list_ai_models: project_key=%s, api_key=%s, gpt_profile_id=%s",
        project_key,
        api_key,
        gpt_profile_id,
    )

    try:
        models = AIModelManager.get_all_models(
            db=db,
            project_key=project_key,
            api_key=api_key,
            gpt_profile_id=gpt_profile_id,
        )

        if not models:
            logger.info("list_ai_models: AIModels not found.")
            raise HTTPException(status_code=404, detail="AIModels not found")

        return {
            "ai_models": [
                {
                    "id": m.id,
                    "name": m.name,
                    "model_name": m.model_name,
                    "url": m.url,
                    "promptFormat": m.api_request_format,
                    "type": m.type,
                }
                for m in models
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"list_ai_models: 取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="AIモデル一覧の取得中にエラーが発生しました。")

@router.get("/ai_models/{model_id}")
def get_ai_model(model_id: int, db: Session = Depends(get_db)):
    logger.info(f"get_ai_model: ID={model_id} のAIモデル取得処理を開始します。")
    try:
        model = AIModelManager.get_model_by_id(db, model_id)
        if not model:
            logger.info(f"get_ai_model: ID={model_id} のAIモデルは見つかりませんでした。")
            raise HTTPException(status_code=404, detail="AIModel not found")
        logger.info(f"get_ai_model: AIモデル {model.name} を取得しました。")
        return {
            "ai_model": {
                "id": model.id,
                "name": model.name,
                "model_name": model.model_name,
                "url": model.url,
                "promptFormat": model.api_request_format,
                "type": model.type,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"get_ai_model: 取得処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="AIモデルの取得中にエラーが発生しました。")

@router.post("/ai_models")
async def create_ai_model(request: Request, db: Session = Depends(get_db)):
    logger.info("create_ai_model: AIモデル追加リクエストの処理を開始します。")
    body = await request.json()
    if "projectKey" in body:
        body["project_key"] = body.pop("projectKey")
    if "apiKey" in body:
        body["api_key"] = body.pop("apiKey")
    if "promptFormat" in body:
        body["api_request_format"] = body.pop("promptFormat")
    try:
        model = AIModelManager.add_model(db, body)
        logger.info(f"create_ai_model: AIモデル {model.name} の追加が完了しました。")
        return {
            "ai_model": {
                "id": model.id,
                "name": model.name,
                "model_name": model.model_name,
                "url": model.url,
                "promptFormat": model.api_request_format,
                "type": model.type,
            }
        }
    except ValueError as e:
        logger.error(f"create_ai_model: バリデーションエラー: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"create_ai_model: 追加処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="AIモデルの追加中にエラーが発生しました。")

@router.put("/ai_models/{model_id}")
async def update_ai_model(model_id: int, request: Request, db: Session = Depends(get_db)):
    logger.info(f"update_ai_model: ID={model_id} のAIモデル更新リクエストの処理を開始します。")
    body = await request.json()
    if "projectKey" in body:
        body["project_key"] = body.pop("projectKey")
    if "apiKey" in body:
        body["api_key"] = body.pop("apiKey")
    if "promptFormat" in body:
        body["api_request_format"] = body.pop("promptFormat")
    try:
        model = AIModelManager.update_model(db, model_id, body)
        if not model:
            logger.info(f"update_ai_model: ID={model_id} のAIモデルは見つかりませんでした。")
            raise HTTPException(status_code=404, detail="AIModel not found")
        logger.info(f"update_ai_model: AIモデル {model.name} の更新が完了しました。")
        return {
            "ai_model": {
                "id": model.id,
                "name": model.name,
                "model_name": model.model_name,
                "url": model.url,
                "promptFormat": model.api_request_format,
                "type": model.type,
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"update_ai_model: 更新処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="AIモデルの更新中にエラーが発生しました。")

@router.delete("/ai_models/{model_id}")
def delete_ai_model(model_id: int, db: Session = Depends(get_db)):
    logger.info(f"delete_ai_model: ID={model_id} のAIモデル削除リクエストの処理を開始します。")
    try:
        result = AIModelManager.delete_model(db, model_id)
        if not result:
            logger.info(f"delete_ai_model: ID={model_id} のAIモデルは見つかりませんでした。")
            raise HTTPException(status_code=404, detail="AIModel not found")
        logger.info(f"delete_ai_model: ID={model_id} のAIモデル削除が完了しました。")
        return {"result": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"delete_ai_model: 削除処理中にエラーが発生しました: {e}")
        raise HTTPException(status_code=500, detail="AIモデルの削除中にエラーが発生しました。")
