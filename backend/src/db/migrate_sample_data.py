"""
Sample data insertion script based on DB table definitions.
Data insertion is separated by making it a function for easy testing.
"""
import asyncio
from datetime import date, datetime
from src.manager.evaluation_manager import EvaluationManager
from src.db.define_tables import (
    Base, Dataset, CustomDatasets, EvaluationPerspective, DatasetCustomMapping,
    AIModel, EvaluationResult, Evaluation
)
from src.db.session import engine
from sqlalchemy.orm import sessionmaker
from src.manager.evaluation_results_manager import EvaluationResultsManager
import pickle
from src.db.define_tables import UseGSN, Evaluation, EvaluationPerspective
from pathlib import Path
import pandas as pd
from src.gsn.register_dataset_for_gsn import RegisterDatasetForGSN
from src.utils.gn_data import PRESET_EVALUATION_JSON

Session = sessionmaker(bind=engine)



def recreate_all_tables():
    """
    Function to re-create all tables.
    """
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("全てのテーブルを再作成しました。")


def initialize_AISI_preset_data():
    """
    Register preset data (auto RT, Theory of mind)
    """
    session = Session()
    try:
        data_dir = Path(__file__).parent.parent.parent / "dataset" / "output"
        gsn_yaml_list = RegisterDatasetForGSN.prepare_gsn_yaml_data()


        # # Toxic
        # gsn_dataset = pd.read_csv(data_dir / "01_aisi_toxic_v0.1.csv")
        # gsn_dataset.insert(0, 'ID', range(1, len(gsn_dataset) + 1))
        # gsn_dataset['ID'] = 'Toxic_' + gsn_dataset['ID'].astype(str)
        # gsn_yaml = gsn_yaml_list[0]
        # register = RegisterDatasetForGSN(
        #     session, gsn_yaml, gsn_dataset)
        # register.register_gsn_dataset()
        # print("AISIのプリセットデータ(有害情報)を初期化しました。")

        # # Misinformation
        # gsn_dataset = pd.read_csv(data_dir / "02_aisi_misinformation_v0.1.csv")
        # gsn_dataset.insert(0, 'ID', range(1, len(gsn_dataset) + 1))
        # gsn_dataset['ID'] = 'Misinfo_' + gsn_dataset['ID'].astype(str)
        # gsn_yaml = gsn_yaml_list[1]
        # register = RegisterDatasetForGSN(
        #     session, gsn_yaml, gsn_dataset)
        # register.register_gsn_dataset()
        # print("AISIのプリセットデータ(偽誤情報)を初期化しました。")

        # Toxic
        gsn_dataset = pd.read_csv(data_dir / "01_aisi_toxic_v0.1.csv")
        gsn_dataset.insert(0, 'ID', range(1, len(gsn_dataset) + 1))
        gsn_dataset['ID'] = 'Toxic_' + gsn_dataset['ID'].astype(str)
        gsn_yaml = gsn_yaml_list[0]
        register = RegisterDatasetForGSN(
            session, gsn_yaml, gsn_dataset)
        register.register_gsn_dataset()
        print("AISIのプリセットデータ(有害情報)を初期化しました。")

        # Misinformation
        gsn_dataset = pd.read_csv(data_dir / "02_aisi_misinformation_v0.1.csv")
        gsn_dataset.insert(0, 'ID', range(1, len(gsn_dataset) + 1))
        gsn_dataset['ID'] = 'Misinfo_' + gsn_dataset['ID'].astype(str)
        gsn_yaml = gsn_yaml_list[1]
        register = RegisterDatasetForGSN(
            session, gsn_yaml, gsn_dataset)
        register.register_gsn_dataset()
        print("AISIのプリセットデータ(偽誤情報)を初期化しました。")

        # Fairness
        gsn_dataset = pd.read_csv(data_dir / "03_aisi_fairness_v0.1.csv")
        gsn_dataset.insert(0, 'ID', range(1, len(gsn_dataset) + 1))
        gsn_dataset['ID'] = 'Fairness_' + gsn_dataset['ID'].astype(str)
        gsn_yaml = gsn_yaml_list[2]
        register = RegisterDatasetForGSN(
            session, gsn_yaml, gsn_dataset)
        register.register_gsn_dataset()
        print("AISIのプリセットデータ(公平性)を初期化しました。")

        # Security
        gsn_dataset = pd.read_csv(data_dir / "06_aisi_security_v0.1.csv")
        gsn_dataset.insert(0, 'ID', range(1, len(gsn_dataset) + 1))
        gsn_dataset['ID'] = 'Security_' + gsn_dataset['ID'].astype(str)
        gsn_yaml = gsn_yaml_list[5]
        register = RegisterDatasetForGSN(
            session, gsn_yaml, gsn_dataset)
        register.register_gsn_dataset()
        print("AISIのプリセットデータ(セキュリティ)を初期化しました。")

        # Explainability
        gsn_dataset = pd.read_csv(data_dir / "07_aisi_explainability_v0.1.csv")
        gsn_dataset.insert(0, 'ID', range(1, len(gsn_dataset) + 1))
        gsn_dataset['ID'] = 'Explain_' + gsn_dataset['ID'].astype(str)
        gsn_yaml = gsn_yaml_list[6]
        register = RegisterDatasetForGSN(
            session, gsn_yaml, gsn_dataset)
        register.register_gsn_dataset()
        print("AISIのプリセットデータ(説明可能性)を初期化しました。")

        # Robustness
        gsn_dataset = pd.read_csv(data_dir / "08_aisi_robustness_v0.1.csv")
        gsn_dataset.insert(0, 'ID', range(1, len(gsn_dataset) + 1))
        gsn_dataset['ID'] = 'Robustness_' + gsn_dataset['ID'].astype(str)
        gsn_yaml = gsn_yaml_list[7]
        for gsn_yaml in gsn_yaml_list:
            register = RegisterDatasetForGSN(
                session, gsn_yaml, gsn_dataset)
            register.register_gsn_dataset()
#        register = RegisterDatasetForGSN(
#            session, gsn_yaml, gsn_dataset)
#        register.register_gsn_dataset()
        print("AISIのプリセットデータ(ロバスト性)を初期化しました。")

        session.commit()

    except Exception as e:
        session.rollback()
        print(f"AISIプリセットデータ初期化時にエラー: {e}")
        raise
    finally:
        session.close()

def initialize_evaluation_perspectives():
    """
    Function to initialize multiple evaluation perspectives.
    """
    session = Session()
    try:
        names = [
            "有害情報の出力制御",
            "偽誤情報の出力・誘導の防止",
            "公平性と包摂性",
            "ハイリスク利用・目的外利用への対処",
            "プライバシー保護",
            "セキュリティ確保",
            "説明可能性",
            "ロバスト性",
            "データ品質",
            "検証可能性"
        ]
        for n in names:
            session.add(EvaluationPerspective(perspective_name=n))
        session.commit()
        print("評価観点を初期化しました。")
    except Exception as e:
        session.rollback()
        print(f"評価観点初期化時にエラー: {e}")
    finally:
        session.close()

def create_preset_evaluation_definitions():
    """
    Function to create preset evaluation definitions.
    """
    session = Session()
    try:
        # Run the async function synchronously
        evaluation = asyncio.run(
            EvaluationManager(session).register_evaluation_from_json(
                PRESET_EVALUATION_JSON
            )
        )
        print(f"create_evaluation: 評価(ID={evaluation.id}) の作成が完了しました。")
        return {"evaluation_id": evaluation.id}
    except Exception as e:
        session.rollback()
        print(f"デフォルト評価定義作成時にエラー: {e}")
        raise
    finally:
        session.close()

def initialize_sample_data():
    """
    Function to initialize sample data.
    """
    recreate_all_tables()
    initialize_evaluation_perspectives()
    initialize_AISI_preset_data()
    create_preset_evaluation_definitions()

if __name__ == "__main__":
    initialize_sample_data()
