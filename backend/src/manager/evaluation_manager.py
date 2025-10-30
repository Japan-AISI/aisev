from ..db.define_tables import Evaluation, EvaluationPerspective, DatasetCustomMapping, CustomDatasets, Dataset
from .custom_datasets_manager import CustomDatasetsManager
import datetime
import pickle
from src.db.define_tables import UseGSN
from src.gsn.gsn_explorer import GSNExplorer
from src.utils.logger import logger
from src.constants.perspectives import to_japanese_perspective


class EvaluationManager:

    def __init__(self, db):
        self.db = db

    def register_evaluation(self, name: str, custom_datasets_id: int):
        """
        Register an Evaluation to the database
        :param name: Evaluation name
        :param custom_datasets_id: Existing CustomDatasets.id (create new if not exists)
        :return: Registered Evaluation instance
        """
        db = self.db
        logger.info(f"register_evaluation: 評価 '{name}' の登録処理を開始します。")
        # Add CustomDatasets
        if not custom_datasets_id:
            custom_datasets_id = CustomDatasetsManager(
                db).add_custom_dataset(name)

        # Register Evaluation
        try:
            evaluation = Evaluation(
                name=name,
                created_date=datetime.datetime.now(),
                custom_datasets_id=custom_datasets_id
            )
            db.add(evaluation)
            db.commit()
            db.refresh(evaluation)
            logger.info(f"register_evaluation: 評価 '{name}' の登録が完了しました。")
            return evaluation
        except Exception as e:
            logger.error(f"register_evaluation: 登録処理中にエラーが発生しました: {e}")
            db.rollback()
            raise

    async def register_evaluation_from_json(self, data: dict):
        """
        Register evaluation definition JSON received from frontend to the database
        :param data: Evaluation definition JSON
        :return: Registered Evaluation instance
        """
        db = self.db
        gsn_explorer = GSNExplorer(db)
        logger.info("register_evaluation_from_json: 評価定義JSONの登録処理を開始します。")

        # Add CustomDatasets
        try:
            custom_dataset_manager = CustomDatasetsManager(db)
            custom_datasets_id = custom_dataset_manager.add_custom_dataset(
                data['evaluationName'])

            # Register Evaluation
            evaluation = self.register_evaluation(
                data['evaluationName'], custom_datasets_id)

            # Add Datasets to CustomDatasetMap
            # For each evaluation perspective
            for criterion in data["criteria"]:
                criterion_name = to_japanese_perspective(criterion["criterion"])
                # Get evaluation perspective id
                perspective = db.query(EvaluationPerspective).filter_by(
                    perspective_name=criterion_name).first()

                # FIXME: It might be better to return an error if it doesn't exist
                if not perspective:
                    # Create new evaluation perspective if it doesn't exist
                    perspective = EvaluationPerspective(
                        perspective_name=criterion_name)
                    db.add(perspective)
                    db.commit()
                    db.refresh(perspective)
                    logger.info(
                        f"register_evaluation_from_json: 新規評価観点 '{criterion_name}' を追加しました。")

                # If GSN is used for this perspective
                use_gsn = criterion.get('use_gsn', False)
                if use_gsn:
                    # Register the combination of evaluation_id and evaluation_perspective_id to USE_GSN table
                    use_gsn_entry = UseGSN(
                        evaluation_id=evaluation.id,
                        evaluation_perspective_id=perspective.id
                    )
                    db.add(use_gsn_entry)
                    db.commit()
                    db.refresh(use_gsn_entry)
                    logger.info(
                        f"register_evaluation_from_json: USE_GSNテーブルに登録しました (evaluation_id={evaluation.id}, perspective_id={perspective.id})")

                    # Add process to get GSN data and associate it with evaluation
                    gsn_datasets = gsn_explorer.get_gsn_data(perspective.id)
                    for ds in gsn_datasets:
                        custom_dataset_manager.add_dataset_custom_mapping(
                            dataset_id=ds.id,
                            custom_datasets_id=custom_datasets_id,
                            perspective_id=perspective.id,
                            # prompt=ds.gsn_leaf, # if GSN leaf is used as prompt
                            prompt="",
                            percentage=ds.score_rate
                        )
                    logger.info(
                        f"register_evaluation_from_json: GSNデータセットのマッピングを追加しました (perspective_id={perspective.id})")
                    continue

                # Register quantitative evaluation dataset
                q = criterion.get("quantitative", {})
                if q.get("checked"):
                    for dataset_id in q.get("datasets", []):
                        # Add mapping using add_dataset_custom_mapping
                        custom_dataset_manager.add_dataset_custom_mapping(
                            dataset_id=dataset_id,
                            custom_datasets_id=custom_datasets_id,
                            perspective_id=perspective.id,
                            # prompt=q.get("text"), # if prompt is used
                            prompt="",
                            percentage=q.get("percentage", 0)
                        )
                    logger.info(
                        f"register_evaluation_from_json: 定量評価データセットのマッピングを追加しました (perspective_id={perspective.id})")

                # Register qualitative evaluation dataset
                ql = criterion.get("qualitative", {})
                if ql.get("checked"):
                    for question_id in ql.get("questions", []):
                        # Add mapping using add_dataset_custom_mapping
                        custom_dataset_manager.add_dataset_custom_mapping(
                            dataset_id=question_id,
                            custom_datasets_id=custom_datasets_id,
                            perspective_id=perspective.id,
                            prompt=None,
                            percentage=ql.get("percentage", 0)
                        )
                    logger.info(
                        f"register_evaluation_from_json: 定性評価データセットのマッピングを追加しました (perspective_id={perspective.id})")

            logger.info("register_evaluation_from_json: 評価定義JSONの登録が完了しました。")
            return evaluation
        except Exception as e:
            logger.error(
                f"register_evaluation_from_json: 登録処理中にエラーが発生しました: {e}")
            db.rollback()
            raise

    def delete_evaluation_by_id(self, evaluation_id: int):
        """
        Function to delete an Evaluation with the specified ID
        :param evaluation_id: ID of the Evaluation to delete
        :return: Whether the deletion was successful (True/False)
        """
        db = self.db
        logger.info(
            f"delete_evaluation_by_id: ID={evaluation_id} のEvaluation削除処理を開始します。")
        try:
            evaluation = db.query(Evaluation).filter_by(
                id=evaluation_id).first()
            if not evaluation:
                logger.info(
                    f"delete_evaluation_by_id: ID={evaluation_id} のEvaluationは見つかりませんでした。")
                return False

            db.delete(evaluation)
            db.commit()
            logger.info(
                f"delete_evaluation_by_id: ID={evaluation_id} のEvaluation削除が完了しました。")

            # DEBUG: show use_gsn_records
            db_use_gsn_records = db.query(UseGSN).all()
            logger.debug(
                f"delete_evaluation_by_id: 現在のUseGSNレコード: {db_use_gsn_records}")

            return True
        except Exception as e:
            logger.error(f"delete_evaluation_by_id: 削除処理中にエラーが発生しました: {e}")
            db.rollback()
            return False

    def get_all(self):
        """
        Returns all id, name, created_date, custom_datasets_id, custom_dataset_name from the Evaluation table
        :return: List of dict
        """
        db = self.db
        logger.info("get_all: Evaluationテーブルの全件取得を開始します。")
        try:
            evals = db.query(Evaluation).join(
                CustomDatasets, Evaluation.custom_datasets_id == CustomDatasets.id).all()

            if not evals:
                logger.info(f"get_all: {len(evals)}件のEvaluationを取得しました。")
            logger.debug(f"get_all: 取得したEvaluationデータ: {evals}")

            # DatasetCustomMappingテーブルを経由してDatasetを取得
            used_dataset_names = []
            for ev in evals:
                dataset_names = db.query(Dataset.name).join(
                    DatasetCustomMapping, Dataset.id == DatasetCustomMapping.dataset_id
                ).filter(
                    DatasetCustomMapping.custom_datasets_id == ev.custom_datasets_id if ev else None
                ).all()
                # タプルのリストから名前のリストに変換
                names = [name[0] for name in dataset_names]
                logger.debug(f"get_all: 取得したDataset名: {names}")

                # namesにGSN_から始まるものがあれば、代わりにAISIpresetを追加してGSN_から始まるものを除外
                perspective_map = {
                    "G1": "有害情報の出力制御",
                    "G2": "偽誤情報の出力・誘導の防止",
                    "G3": "公平性と包摂性",
                    "G4": "ハイリスク利用・目的外利用への対処",
                    "G5": "プライバシー保護",
                    "G6": "セキュリティ確保",
                    "G7": "説明可能性",
                    "G8": "ロバスト性",
                    "G9": "データ品質",
                    "G10": "検証可能性"
                }
                GSN_tags = ["G1", "G2", "G3", "G4",
                            "G5", "G6", "G7", "G8", "G9", "G10"]
                for tag in GSN_tags:
                    if any(name.startswith(f"GSN_{tag}") for name in names):
                        names.append(f"Preset Data({perspective_map[tag]})")
                        logger.debug(
                            f"get_all: GSN_{tag}が見つかったため、Preset Data({perspective_map[tag]})を追加しました。")

                # GSN_から始まるものを除外
                names = [name for name in names if not name.startswith("GSN_")]

                used_dataset_names.append(names)

            return [
                {
                    "id": e.id,
                    "name": e.name,
                    "created_date": e.created_date,
                    # "custom_dataset_name": e.custom_dataset.name if e.custom_dataset else None
                    "used_dataset_names": used_dataset_names[idx]
                }
                for idx, e in enumerate(evals)
            ]
        except Exception as e:
            logger.error(f"get_all: 取得処理中にエラーが発生しました: {e}")
            return
