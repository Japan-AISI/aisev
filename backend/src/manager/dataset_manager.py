from sqlalchemy.orm import Session
from src.db.define_tables import Dataset, EvaluationPerspective
import pickle
from src.utils.logger import logger
from src.constants.perspectives import to_japanese_perspective


class DatasetManager:
    """
    A class that consolidates database operations for datasets in general
    """
    @staticmethod
    def register_dataset(db: Session, name: str, data: str):
        """
        Register a dataset to the database
        :param db: SQLAlchemy Session
        :param data: Dataset JSON (name, contents, criterion, type)
        :return: Registered Dataset instance
        """
        logger.info(f"register_dataset: データセット '{name}' の登録処理を開始します。")
        # When data is passed as a CSV format string, convert it to pd.DataFrame
        import pandas as pd
        import io

        try:
            if isinstance(data, str):
                df = pd.read_csv(io.StringIO(data.strip()))
                df = df[df['text'].notna()]
                if "ten_perspective" in df.columns:
                    df["ten_perspective"] = df["ten_perspective"].apply(
                        to_japanese_perspective
                    )
            else:
                logger.error("register_dataset: dataがCSV形式のstrではありません。")
                raise ValueError("data must be a CSV string")
            binary_content = pickle.dumps(df)
            dataset = Dataset(
                name=name,
                data_content=binary_content,
                type="quantitative"
            )
            db.add(dataset)
            db.commit()
            db.refresh(dataset)
            logger.info(f"register_dataset: データセット '{name}' の登録が完了しました。")
            return dataset
        except Exception as e:
            logger.error(f"register_dataset: 登録処理中にエラーが発生しました: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_by_ids(db: Session, ids: list[int]):
        """
        Get datasets by multiple IDs
        :param db: SQLAlchemy Session
        :param ids: List of Dataset IDs to retrieve
        :return: List of Dataset instances
        """
        logger.info(f"get_by_ids: IDリスト {ids} のデータセット取得を開始します。")
        if not ids:
            logger.info("get_by_ids: 空のIDリストが指定されました。")
            return []
        try:
            datasets = db.query(Dataset).filter(Dataset.id.in_(ids)).all()
            logger.info(f"get_by_ids: {len(datasets)}件のデータセットを取得しました。")
            return datasets
        except Exception as e:
            logger.error(f"get_by_ids: 取得処理中にエラーが発生しました: {e}")
            return []

    @staticmethod
    def get_by_ids_and_type(db: Session, ids: list[int], type: str):
        """
        Get datasets by multiple IDs and type
        :param db: SQLAlchemy Session
        :param ids: List of Dataset IDs to retrieve
        :param type: Dataset type (quantitative/qualitative)
        :return: List of Dataset instances
        """
        logger.info(f"get_by_ids_and_type: IDリスト {ids}, type={type} のデータセット取得を開始します。")
        if not ids:
            logger.info("get_by_ids_and_type: 空のIDリストが指定されました。")
            return []
        try:
            datasets = db.query(Dataset).filter(
                Dataset.id.in_(ids), Dataset.type == type).all()
            logger.info(f"get_by_ids_and_type: {len(datasets)}件のデータセットを取得しました。")
            return datasets
        except Exception as e:
            logger.error(f"get_by_ids_and_type: 取得処理中にエラーが発生しました: {e}")
            return []
