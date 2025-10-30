from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union, Literal

class LLMConfig(BaseModel):
    """LLM settings"""
    provider: str = Field(..., description="LLMプロバイダー (openai, azure, huggingface, ollama, custom_endpoint)")
    model: str = Field(..., description="使用するモデル名またはデプロイメント名")
    api_key: Optional[str] = Field(None, description="APIキー（指定がない場合は環境変数から取得）")
    api_base: Optional[str] = Field(None, description="APIエンドポイント（Azureの場合）")
    system_prompt: Optional[str] = Field(None, description="追加システムプロンプト（カスタム）")
    base_system_prompt: Optional[str] = Field(None, description="ベースシステムプロンプト（カスタム）")
    user_prompt_template: Optional[str] = Field(None, description="ユーザープロンプトテンプレート（カスタム）")
    
    # Custom endpoint settings
    custom_endpoint_url: Optional[str] = Field(None, description="カスタムエンドポイントのURL")
    target_prefix: Optional[str] = Field(None, description="ターゲットプレフィックス")
    use_proxy: bool = Field(False, description="プロキシを使用するかどうか")
    proxy_url: Optional[str] = Field(None, description="プロキシURL")
    proxy_username: Optional[str] = Field(None, description="プロキシユーザー名")
    proxy_password: Optional[str] = Field(None, description="プロキシパスワード")

class LLMRequest(BaseModel):
    """LLM settings request"""
    requirements_llm: LLMConfig = Field(..., description="要件生成に使用するLLM設定")
    adversarial_llm: LLMConfig = Field(..., description="敵対的プロンプト生成に使用するLLM設定")
    evaluation_llm: LLMConfig = Field(..., description="評価に使用するLLM設定")
    target_llm: LLMConfig = Field(..., description="テスト対象のLLM設定")

class RequirementsGenerationRequest(BaseModel):
    """Requirements generation request"""
    session_id: str = Field(..., description="セッションID")
    target_purpose: str = Field(..., description="ターゲットAIの使用目的")
    use_documents: bool = Field(True, description="アップロードされたドキュメントを使用するかどうか")
    num_requirements: int = Field(10, description="生成する要件の数", ge=1, le=50)
    language: Literal["ja", "en"] = Field("ja", description="リクエスト時のUI言語")

class Requirement(BaseModel):
    """Safety requirements"""
    category: str = Field(..., description="要件のカテゴリ")
    requirement: str = Field(..., description="要件の説明")
    rationale: Optional[str] = Field(None, description="要件が必要な理由の説明")

class RequirementsGenerationResponse(BaseModel):
    """Requirements generation response"""
    requirements: List[Requirement] = Field(..., description="生成された要件のリスト")

class AdversarialPromptRequest(BaseModel):
    """Adversarial prompts generation request"""
    session_id: str = Field(..., description="セッションID")
    target_purpose: str = Field(..., description="ターゲットAIの使用目的")
    prompts_per_requirement: int = Field(3, description="要件ごとに生成する敵対的プロンプトの数", ge=1, le=10)
    language: Literal["ja", "en"] = Field("ja", description="リクエスト時のUI言語")

class AdversarialPrompt(BaseModel):
    """Adversarial prompts"""
    prompt: str = Field(..., description="敵対的プロンプトのテキスト")
    category: str = Field(..., description="関連する要件のカテゴリ")
    requirement: str = Field(..., description="関連する要件の説明")

class AdversarialPromptResponse(BaseModel):
    """Adversarial prompts generation response"""
    adversarial_prompts: List[AdversarialPrompt] = Field(..., description="生成された敵対的プロンプトのリスト")

class EvaluationRequest(BaseModel):
    """Evaluation request"""
    session_id: str = Field(..., description="セッションID")
    auto_run: bool = Field(False, description="全ての敵対的プロンプトを自動的に実行するかどうか")
    language: Literal["ja", "en"] = Field("ja", description="リクエスト時のUI言語")

class Evaluation(BaseModel):
    """Evaluation results"""
    passed: bool = Field(..., description="要件を満たしているかどうか")
    reason: str = Field(..., description="判断理由")

class TestResult(BaseModel):
    """Testing results"""
    prompt: str = Field(..., description="敵対的プロンプト")
    category: str = Field(..., description="関連する要件のカテゴリ")
    requirement: str = Field(..., description="関連する要件の説明")
    target_response: str = Field(..., description="ターゲットAIの応答")
    evaluation: Evaluation = Field(..., description="評価結果")

class EvaluationSummary(BaseModel):
    """Evaluation summary"""
    total_tests: int = Field(..., description="テストの総数")
    passed: int = Field(..., description="合格したテストの数")
    failed: int = Field(..., description="失敗したテストの数")
    error: int = Field(..., description="エラーが発生したテストの数")
    pass_rate: float = Field(..., description="合格率（%）")
    category_stats: Dict[str, Dict[str, int]] = Field(..., description="カテゴリ別の統計")
    result_file: str = Field(..., description="結果ファイルのパス")

class EvaluationResponse(BaseModel):
    """Evaluation response"""
    summary: EvaluationSummary = Field(..., description="評価サマリー")
    results: List[TestResult] = Field(..., description="詳細なテスト結果")
