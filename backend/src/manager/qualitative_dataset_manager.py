from sqlalchemy.orm import Session
from src.db.define_tables import Dataset, EvaluationPerspective, DatasetCustomMapping, Evaluation
import pickle
from src.utils.logger import logger
from src.constants.perspectives import to_japanese_perspective


class QualitativeDatasetService:
    """
    Service class: Aggregates DB operations related to qualitative datasets
    """
    @staticmethod
    def add_from_json(db: Session, data: dict):
        """
        Receive specified JSON data and add it to the Dataset table as qualitative data
        :param db: SQLAlchemy Session
        :param data: JSON of question data
        :return: List of added Dataset instances
        """
        logger.info("add_from_json: 定性データセット追加処理を開始します。")
        # Data with second_goal is GSN data
        second_goal = data.get("second_goal", "")

        contents = data.get("contents", [])
        for i, content in enumerate(contents):
            content_id = f"GSN_{i + 1}" if second_goal else i + 1
            contents[i] = {"id": content_id, "text": content}

        binary_content = pickle.dumps(contents)
        criterion_name = to_japanese_perspective(data.get("criterion"))
        perspective = db.query(EvaluationPerspective).filter_by(
            perspective_name=criterion_name).first()
        if not perspective and not data.get("gsn_leaf"):
            logger.error(
                f"add_from_json: EvaluationPerspectiveが見つかりません: {criterion_name}")
            raise ValueError(
                f"EvaluationPerspective with name {criterion_name} not found"
            )
        try:
            dataset = Dataset(
                name=f"{data.get('name', '')}",
                data_content=binary_content,
                evaluation_perspective_id=perspective.id if perspective else None,
                type="qualitative",
                score_rate=data.get("score_rate", 1.0),
                second_goal=data.get("second_goal", ""),
                gsn_leaf=data.get("gsn_leaf", "")
            )
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
            logger.info(f"add_from_json: データセット '{dataset.name}' の追加が完了しました。")
            return [dataset]
        except Exception as e:
            logger.error(f"add_from_json: 追加処理中にエラーが発生しました: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_all(db: Session):
        """
        Extract only those with type "qualitative" from the Dataset table,
        and return id, name, perspective, data_content as a list of dicts.
        If data_content is binary, decode it with pickle and return.
        :param db: SQLAlchemy Session
        :return: List of dicts
        """
        logger.info("get_all: 定性データセット全件取得を開始します。")
        results = (
            db.query(
            Dataset.id,
            Dataset.name,
            EvaluationPerspective.perspective_name,
            Dataset.data_content
            )
            .join(EvaluationPerspective, Dataset.evaluation_perspective_id == EvaluationPerspective.id, isouter=True)
            .filter(
            Dataset.type == "qualitative",
            ~Dataset.name.startswith("GSN_")
            )
            .all()
        )
        datasets = []
        for r in results:
            try:
                contents = pickle.loads(r.data_content)
            except Exception as e:
                logger.error(f"get_all: data_contentのデコードに失敗: {e}")
                contents = r.data_content
            datasets.append({
                "id": r.id,
                "name": r.name,
                "perspective": r.perspective_name,
                "contents": contents,
                "score_rate": r.score_rate if hasattr(r, 'score_rate') else 1.0,
                "second_goal": r.second_goal if hasattr(r, 'second_goal') else "",
                "gsn_leaf": r.gsn_leaf if hasattr(r, 'gsn_leaf') else ""
            })
        logger.info(f"get_all: {len(datasets)}件の定性データセットを取得しました。")
        return datasets

    @staticmethod
    def get_by_id(db: Session, dataset_id: int):
        """
        Get qualitative data (Dataset.type=="qualitative") with the specified ID from the Dataset table
        :param db: SQLAlchemy Session
        :param dataset_id: ID of the Dataset to retrieve
        :return: Dataset information in dict format
        """
        logger.info(f"get_by_id: ID={dataset_id} の定性データセット取得を開始します。")
        dataset = db.query(Dataset).filter_by(
            id=dataset_id, type="qualitative").first()
        if not dataset:
            logger.info(f"get_by_id: ID={dataset_id} のデータセットは見つかりませんでした。")
            return None
        try:
            contents = pickle.loads(dataset.data_content)
        except Exception as e:
            logger.error(f"get_by_id: data_contentのデコードに失敗: {e}")
            contents = dataset.data_content
        logger.info(f"get_by_id: データセット '{dataset.name}' の取得が完了しました。")
        return {
            "id": dataset.id,
            "name": dataset.name,
            "perspective": dataset.evaluation_perspective.perspective_name if dataset.evaluation_perspective else None,
            "contents": contents,
        }

    @staticmethod
    def get_by_evaluation_id(db: Session, evaluation_id: int):
        """
        Get qualitative data associated with the specified evaluation ID
        :param db: SQLAlchemy Session
        :param evaluation_id: Evaluation ID
        :return: List of Dataset information in dict format
        """
        logger.info(
            f"get_by_evaluation_id: evaluation_id={evaluation_id} の定性データセット取得を開始します。")
        evaluation = db.query(Evaluation).filter_by(id=evaluation_id).first()
        if not evaluation:
            logger.info(
                f"get_by_evaluation_id: evaluation_id={evaluation_id} のEvaluationが見つかりませんでした。")
            return []
        custom_datasets_id = evaluation.custom_datasets_id

        # Get all mappings
        dataset_custom_mappings = db.query(DatasetCustomMapping).filter_by(
            custom_datasets_id=custom_datasets_id).all()
        if not dataset_custom_mappings:
            logger.info(
                f"get_by_evaluation_id: custom_datasets_id={custom_datasets_id} のマッピングが見つかりませんでした。")
            return []

        # Get all associated qualitative datasets
        dataset_ids = [m.dataset_id for m in dataset_custom_mappings]
        datasets = db.query(Dataset).filter(
            Dataset.id.in_(dataset_ids),
            Dataset.type == "qualitative"
        ).all()

        result = []
        for dataset in datasets:
            try:
                contents = pickle.loads(dataset.data_content)
            except Exception as e:
                logger.error(
                    f"get_by_evaluation_id: data_contentのデコードに失敗: {e}")
                contents = dataset.data_content
            result.append({
                "id": dataset.id,
                "name": dataset.name,
                "perspective": dataset.evaluation_perspective.perspective_name if dataset.evaluation_perspective else None,
                "contents": contents,
                "score_rate": dataset.score_rate if hasattr(dataset, 'score_rate') else 1.0,
                "second_goal": dataset.second_goal if hasattr(dataset, 'second_goal') else "",
                "gsn_leaf": dataset.gsn_leaf if hasattr(dataset, 'gsn_leaf') else ""
            })
        logger.info(f"get_by_evaluation_id: {len(result)}件の定性データセットを取得しました。")
        return result

    @staticmethod
    def delete_by_id(db: Session, dataset_id: int):
        """
        Delete qualitative data (Dataset.type=="qualitative") with the specified ID from the Dataset table
        :param db: SQLAlchemy Session
        :param dataset_id: ID of the Dataset to delete
        :return: Number of deleted records
        """
        logger.info(f"delete_by_id: ID={dataset_id} の定性データセット削除を開始します。")
        count = 0
        dataset = db.query(Dataset).filter_by(
            id=dataset_id, type="qualitative").first()
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
