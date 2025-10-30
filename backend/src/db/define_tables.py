from sqlalchemy import Column, Integer, String, ForeignKey, JSON, LargeBinary, DateTime, Float
from sqlalchemy.orm import declarative_base, relationship
from src.db.session import engine
from src.utils.logger import logger
from sqlalchemy.orm import sessionmaker
from src.constants.perspectives import TEN_PERSPECTIVES_JA

Base = declarative_base()


class Dataset(Base):
    __tablename__ = "dataset"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    data_content = Column(LargeBinary)
    type = Column(String)  # "quantitative/qualitative"
    score_rate = Column(Float)
    second_goal = Column(String)
    gsn_leaf = Column(String)  # Maintains information as a GSN leaf
    evaluation_perspective_id = Column(
        Integer, ForeignKey("evaluation_perspective.id"))
    # relationships
    custom_mappings = relationship(
        "DatasetCustomMapping", back_populates="dataset")
    evaluation_perspective = relationship(
        "EvaluationPerspective", back_populates="datasets")

    def __repr__(self):
        return f"<Dataset(id={self.id}, name={self.name}, type={self.type}, score_rate={self.score_rate}, second_goal={self.second_goal},  evaluation_perspective_id={self.evaluation_perspective_id})>"


class CustomDatasets(Base):
    __tablename__ = "custom_datasets"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # relationships
    custom_mappings = relationship(
        "DatasetCustomMapping", back_populates="custom_dataset")
    evaluations = relationship("Evaluation", back_populates="custom_dataset")

    def __repr__(self):
        return f"<CustomDatasets(id={self.id}, name={self.name})>"


class EvaluationPerspective(Base):
    __tablename__ = "evaluation_perspective"
    id = Column(Integer, primary_key=True)
    perspective_name = Column(String)
    # relationships
    datasets = relationship("Dataset", back_populates="evaluation_perspective")

    def __repr__(self):
        return f"<EvaluationPerspective(id={self.id}, perspective_name={self.perspective_name})>"


class DatasetCustomMapping(Base):
    __tablename__ = "dataset_custom_mapping"
    dataset_id = Column(Integer, ForeignKey("dataset.id"), primary_key=True)
    custom_datasets_id = Column(Integer, ForeignKey(
        "custom_datasets.id"), primary_key=True)
    perspective_id = Column(Integer, ForeignKey(
        "evaluation_perspective.id"), primary_key=True)
    prompt = Column(String)  # New column as per ER diagram
    percentage = Column(Float)  # Added column for percentage
    # relationships
    dataset = relationship("Dataset", back_populates="custom_mappings")
    custom_dataset = relationship(
        "CustomDatasets", back_populates="custom_mappings")

    def __repr__(self):
        return f"<DatasetCustomMapping(dataset_id={self.dataset_id}, custom_datasets_id={self.custom_datasets_id}, perspective_id={self.perspective_id}, prompt={self.prompt}, percentage={self.percentage})>"


class AIModel(Base):
    __tablename__ = "ai_model"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    model_name = Column(String)
    url = Column(String)
    api_key = Column(String)
    api_request_format = Column(JSON)
    type = Column(String)  # "target/eval/both"
    # relationships
    target_evaluation_results = relationship(
        "EvaluationResult", back_populates="target_ai_model", foreign_keys='EvaluationResult.target_ai_model_id')
    evaluator_evaluation_results = relationship(
        "EvaluationResult", back_populates="evaluator_ai_model", foreign_keys='EvaluationResult.evaluator_ai_model_id')

    def __repr__(self):
        return f"<AIModel(id={self.id}, name={self.name}, model_name={self.model_name}, url={self.url}, api_key={self.api_key}, api_request_format={self.api_request_format}, type={self.type})>"


class Evaluation(Base):
    __tablename__ = "evaluation"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_date = Column(DateTime)
    custom_datasets_id = Column(Integer, ForeignKey("custom_datasets.id"))
    # relationships
    usegsn = relationship("UseGSN", cascade="all, delete")
    custom_dataset = relationship(
        "CustomDatasets", back_populates="evaluations")
    results = relationship("EvaluationResult", back_populates="evaluation")

    def __repr__(self):
        return f"<Evaluation(id={self.id}, name={self.name}, created_date={self.created_date}, custom_datasets_id={self.custom_datasets_id})>"


class EvaluationResult(Base):
    __tablename__ = "evaluation_result"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    created_date = Column(DateTime)
    evaluation_id = Column(Integer, ForeignKey("evaluation.id"))
    target_ai_model_id = Column(Integer, ForeignKey("ai_model.id"))
    evaluator_ai_model_id = Column(Integer, ForeignKey("ai_model.id"))
    quantitative_results = Column(JSON)
    qualitative_results = Column(JSON)
    quantitative_eval_state = Column(String)  # "running", "done", etc.
    # relationships
    evaluation = relationship("Evaluation", back_populates="results")
    target_ai_model = relationship(
        "AIModel", back_populates="target_evaluation_results", foreign_keys=[target_ai_model_id])
    evaluator_ai_model = relationship(
        "AIModel", back_populates="evaluator_evaluation_results", foreign_keys=[evaluator_ai_model_id])

    def __repr__(self):
        return f"<EvaluationResult(id={self.id}, name={self.name}, created_date={self.created_date}, evaluation_id={self.evaluation_id}, target_ai_model_id={self.target_ai_model_id}, evaluator_ai_model_id={self.evaluator_ai_model_id},  quantitative_eval_state={self.quantitative_eval_state})>"


class UseGSN(Base):
    __tablename__ = "use_gsn"
    evaluation_id = Column(Integer, ForeignKey(
        "evaluation.id"), primary_key=True)
    evaluation_perspective_id = Column(Integer, ForeignKey(
        "evaluation_perspective.id"), primary_key=True)
    # relationships
    evaluation = relationship("Evaluation", backref="use_gsn_links")
    evaluation_perspective = relationship(
        "EvaluationPerspective", backref="use_gsn_links")

    def __repr__(self):
        return f"<UseGSN(evaluation_id={self.evaluation_id}, evaluation_perspective_id={self.evaluation_perspective_id})>"


class InitialDataMigrator():
    def __init__(self, engine):
        self.session = sessionmaker(bind=engine)()

    def initialize_10_perspective(self):

        for n in TEN_PERSPECTIVES_JA[:10]:
            self.session.add(EvaluationPerspective(perspective_name=n))
        self.session.commit()


# NOTE: docker compose up時に初期化が走る
if __name__ == "__main__":
    try:
        logger.info("define_tables: テーブル作成処理を開始します。")
        Base.metadata.create_all(engine)
        InitialDataMigrator(engine).initialize_10_perspective()
        logger.info("define_tables: テーブル作成処理が完了しました。")
    except Exception as e:
        logger.error(f"define_tables: テーブル作成処理中にエラーが発生しました: {e}")
