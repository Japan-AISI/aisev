from sqlalchemy.orm import Session
from src.db.define_tables import Dataset, EvaluationPerspective
import pickle
import math
import json
from src.utils.logger import logger
from src.constants.perspectives import to_japanese_perspective


def _convert_nan_to_json_compatible(obj):
    """
    Recursive function to convert NaN values in objects to JSON-compatible values (None)
    """
    if isinstance(obj, dict):
        return {k: _convert_nan_to_json_compatible(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_nan_to_json_compatible(item) for item in obj]
    elif isinstance(obj, float) and math.isnan(obj):
        return None
    else:
        return obj


class QuantitativeDatasetService:
    """
    Service class: Aggregates DB operations related to quantitative datasets
    """
    @staticmethod
    def add_from_json(db: Session, data: dict):
        """
        Receive specified JSON data and add it to the Dataset table as quantitative data
        :param db: SQLAlchemy Session
        :param data: JSON of dataset
        :return: List of added Dataset instances
        """
        logger.info("add_from_json: 定量データセット追加処理を開始します。")
        added_datasets = []
        try:
            binary_content = pickle.dumps(data.get("contents", []))
            criterion_name = to_japanese_perspective(data.get("criterion"))
            perspective = db.query(EvaluationPerspective).filter_by(
                perspective_name=criterion_name).first()
            if not perspective and not data.get("gsn_leaf"):
                logger.error(
                    f"add_from_json: EvaluationPerspectiveが見つかりません: {criterion_name}")
                raise ValueError(
                    f"EvaluationPerspective with name {criterion_name} not found"
                )
            dataset = Dataset(
                name=f"{data.get('name', '')}",
                data_content=binary_content,
                evaluation_perspective_id=perspective.id if perspective else None,
                type="quantitative",
                score_rate=data.get("score_rate", 1.0),
                second_goal=data.get("second_goal", ""),
                gsn_leaf=data.get("gsn_leaf", "")
            )
            db.add(dataset)
            added_datasets.append(dataset)
            db.commit()
            for dataset in added_datasets:
                db.refresh(dataset)
            logger.info(f"add_from_json: データセット '{dataset.name}' の追加が完了しました。")
            return added_datasets
        except Exception as e:
            logger.error(f"add_from_json: 追加処理中にエラーが発生しました: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_all(db: Session):
        """
        Extract only those with type "quantitative" from the Dataset table,
        and return id, name, perspective, data_content as a list of dicts.
        If data_content is binary, decode it with pickle and return.
        :param db: SQLAlchemy Session
        :return: List of dicts
        """
        logger.info("get_all: 定量データセット全件取得を開始します。")
        results = (
            db.query(
                Dataset.id,
                Dataset.name,
                EvaluationPerspective.perspective_name,
                Dataset.data_content
            )
            .join(EvaluationPerspective, Dataset.evaluation_perspective_id == EvaluationPerspective.id, isouter=True)
            .filter(
                Dataset.type == "quantitative",
                ~Dataset.name.startswith("GSN_")
            )
            .all()
        )
        datasets = []
        for r in results:
            try:
                contents = pickle.loads(r.data_content)
                # Convert NaN values to JSON-compatible values
                contents = _convert_nan_to_json_compatible(contents)
            except Exception as e:
                logger.error(f"get_all: data_contentのデコードに失敗: {e}")
                contents = r.data_content
            datasets.append({
                "id": r.id,
                "name": r.name,
                "perspective": r.perspective_name,
                "contents": contents,
            })
        logger.info(f"get_all: {len(datasets)}件の定量データセットを取得しました。")
        return datasets

    @staticmethod
    def delete_by_id(db: Session, dataset_id: int):
        """
        Delete quantitative data (Dataset.type=="quantitative") with the specified ID from the Dataset table
        :param db: SQLAlchemy Session
        :param dataset_id: ID of the Dataset to delete
        :return: Number of deleted records
        """
        logger.info(f"delete_by_id: ID={dataset_id} の定量データセット削除を開始します。")
        count = 0
        dataset = db.query(Dataset).filter_by(
            id=dataset_id, type="quantitative").first()
        if dataset:
            try:
                db.delete(dataset)
                db.commit()
                count = 1
                logger.info(f"delete_by_id: ID={dataset_id} の削除が完了しました。")
            except Exception as e:
                logger.error(f"delete_by_id: 削除処理中にエラーが発生しました: {e}")
                db.rollback()
        else:
            logger.info(f"delete_by_id: ID={dataset_id} のデータセットは見つかりませんでした。")
        return count

    @staticmethod
    def get_by_name(db: Session, name: str):
        """
        Get quantitative dataset with the specified name from the Dataset table
        :param db: SQLAlchemy Session
        :param name: Name of the Dataset to retrieve
        :return: Dataset instance or None
        """
        logger.info(f"get_by_name: name='{name}' の定量データセット取得を開始します。")
        dataset = db.query(Dataset).filter_by(
            name=name, type="quantitative").first()
        if dataset:
            logger.info(f"get_by_name: 定量データセット '{name}' を取得しました。")
            return dataset
        else:
            logger.info(f"get_by_name: 定量データセット '{name}' は見つかりませんでした。")
            return None
