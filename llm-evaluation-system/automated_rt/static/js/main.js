/**
 *   Frontend scripts
 */

// Global variables
let currentSessionId = null;
let requirements = [];
let adversarialPrompts = [];
let uploadedDocuments = [];
let evaluationSummary = null;
const progressState = {
    total: 0,
    completed: 0,
    estimatedSeconds: null,
};

const targetSystemPromptState = {
    defaults: { ja: null, en: null },
    isCustom: false,
};

let targetSystemPromptInitialized = false;

function getCurrentLanguage() {
    return window.automatedRtI18n?.getLanguage ? window.automatedRtI18n.getLanguage() : 'ja';
}

function ensureTargetSystemPromptDefaults() {
    const textarea = document.getElementById('targetLlmSystemPrompt');
    if (!textarea) {
        return null;
    }
    if (targetSystemPromptState.defaults.ja === null) {
        targetSystemPromptState.defaults.ja = textarea.dataset.defaultJa || textarea.value || '';
    }
    if (targetSystemPromptState.defaults.en === null) {
        const datasetDefaultEn = textarea.dataset.defaultEn;
        targetSystemPromptState.defaults.en = datasetDefaultEn !== undefined ? datasetDefaultEn : targetSystemPromptState.defaults.ja;
    }
    return textarea;
}

function isDefaultTargetSystemPrompt(value) {
    if (value === null || value === undefined) {
        return false;
    }
    const normalized = String(value).replace(/\r\n/g, '\n');
    const defaultJa = (targetSystemPromptState.defaults.ja ?? '').replace(/\r\n/g, '\n');
    const defaultEn = (targetSystemPromptState.defaults.en ?? '').replace(/\r\n/g, '\n');
    return normalized === defaultJa || normalized === defaultEn;
}

function applyTargetSystemPromptDefault() {
    const textarea = ensureTargetSystemPromptDefaults();
    if (!textarea) {
        return;
    }
    if (targetSystemPromptState.isCustom) {
        return;
    }
    const lang = getCurrentLanguage();
    const defaultValue = targetSystemPromptState.defaults[lang] ?? '';
    if (textarea.value !== defaultValue) {
        textarea.value = defaultValue;
    }
    targetSystemPromptState.isCustom = false;
}

function setTargetSystemPromptValue(value) {
    const textarea = ensureTargetSystemPromptDefaults();
    if (!textarea || value === undefined) {
        return;
    }
    textarea.value = value ?? '';
    targetSystemPromptState.isCustom = !isDefaultTargetSystemPrompt(textarea.value);
    if (!targetSystemPromptState.isCustom) {
        applyTargetSystemPromptDefault();
    }
}

function initializeTargetSystemPromptState() {
    if (targetSystemPromptInitialized) {
        return;
    }
    const textarea = ensureTargetSystemPromptDefaults();
    if (!textarea) {
        return;
    }
    targetSystemPromptState.isCustom = !isDefaultTargetSystemPrompt(textarea.value);
    textarea.addEventListener('input', () => {
        targetSystemPromptState.isCustom = !isDefaultTargetSystemPrompt(textarea.value);
    });
    targetSystemPromptInitialized = true;
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTargetSystemPromptState);
} else {
    initializeTargetSystemPromptState();
}

const messages = {
    ja: {
        language: {
            japanese: "日本語",
            english: "English"
        },
        page: {
            title: "AIセーフティ評価 自動レッドチーミング",
            heading: "AIセーフティ評価 自動レッドチーミング"
        },
        session: {
            current: "現在のセッション:",
            viewPast: "過去の評価結果を表示"
        },
        navigation: {
            title: "ステップナビゲーション",
            step1: "1. LLM設定",
            step2: "2. ドキュメント",
            step3: "3. 要件生成",
            step4: "4. 敵対的プロンプト",
            step5: "5. 評価実行"
        },
        steps: {
            next: "次のステップへ進む",
            step1: {
                title: "LLMの設定",
                description: "評価に使用する各LLMの設定を行います。",
                openModal: "LLM設定モーダルを開く"
            },
            step2: {
                title: "ドキュメントのアップロード",
                description: "ターゲットAIのドメイン情報を含むドキュメントをアップロードします（オプション）。",
                fileLabel: "ドキュメントファイル（PDF）:",
                upload: "アップロード",
                uploaded: "アップロード済みドキュメント:"
            },
            step3: {
                title: "要件の生成",
                description: "ターゲットAIが満たすべき安全要件を生成します。",
                purposeLabel: "ターゲットAIの使用目的:",
                purposePlaceholder: "ターゲットAIの使用目的を入力してください",
                purposeExample: "例: このLLMは顧客サポートチャットボットとして使用され、製品情報の提供や一般的な質問に回答します。",
                countLabel: "生成する要件の数:",
                useDocuments: "アップロードしたドキュメントを使用する",
                generate: "要件を生成",
                generatedTitle: "生成された要件:"
            },
            step4: {
                title: "敵対的プロンプトの生成",
                description: "各要件に対する敵対的プロンプトを生成します。",
                countLabel: "要件ごとに生成するプロンプト数:",
                generate: "敵対的プロンプトを生成",
                generatedTitle: "生成された敵対的プロンプト:",
                export: "生成結果をエクスポート"
            },
            step5: {
                title: "評価の実行",
                description: "ターゲットAIに対して敵対的プロンプトを実行し、応答を評価します。",
                run: "評価を実行"
            }
        },
        tables: {
            requirements: {
                category: "カテゴリ",
                requirement: "要件",
                reason: "理由"
            },
            adversarial: {
                category: "カテゴリ",
                requirement: "要件",
                prompt: "敵対的プロンプト"
            }
        },
        evaluation: {
            summary: "評価サマリー:",
            categoryResults: "カテゴリ別結果:",
            viewDetails: "詳細結果を表示",
            progress_head: "進捗状況: ",
            progress_tail: " プロンプト完了",
            estimatedTime: "推定残り時間: {{time}}",
            completed: "プロンプト完了",
            totalLabel: "総テスト数:",
            passedLabel: "合格:",
            failedLabel: "不合格:",
            errorLabel: "エラー:"
        },
        toast: {
            success: "成功",
            error: "エラー",
            warning: "警告",
            info: "情報"
        },
        alerts: {
            settingsExported: "設定をエクスポートしました",
            settingsImported: "設定をインポートしました",
            settingsSavedBrowser: "設定をブラウザに保存しました",
            settingsLoaded: "保存された設定を読み込みました",
            settingsCopied: "設定をコピーしました",
            llmSaved: "LLM設定が保存されました",
            documentUploaded: "ドキュメントがアップロードされました",
            requirementsGenerated: "要件が生成されました",
            noRequirementsGenerated: "生成された要件がありません。別のLLMプロバイダーを試してみてください。",
            adversarialGenerated: "敵対的プロンプトが生成されました",
            adversarialExported: "敵対的プロンプトをCSVとしてエクスポートしました",
            evaluationCompleted: "評価が完了しました"
        },
        warnings: {
            noSavedSettings: "保存された設定が見つかりませんでした",
            noFileSelected: "ファイルが選択されていません",
            generateRequirementsFirst: "まず要件を生成してください",
            generateAdversarialFirst: "まず敵対的プロンプトを生成してください",
            runLlmSetupFirst: "まずLLM設定を行ってください",
            noAdversarialToExport: "エクスポートする敵対的プロンプトがありません"
        },
        errors: {
            settingsImportFailed: "設定のインポートに失敗しました: {{error}}",
            settingsLoadFailed: "設定の読み込みに失敗しました: {{error}}",
            llmSaveFailed: "LLM設定の保存に失敗しました: {{error}}",
            documentUploadFailed: "ドキュメントのアップロードに失敗しました: {{error}}",
            requirementsMissing: "サーバーからの応答に要件データがありません",
            requirementsGenerationFailed: "要件の生成に失敗しました: {{status}} {{statusText}}",
            requirementsProcessingError: "要件の生成処理中にエラーが発生しました: {{error}}",
            requirementsRequestNoResponse: "要件の生成リクエストに対する応答がありませんでした。ネットワーク接続を確認してください。",
            adversarialGenerationFailed: "敵対的プロンプトの生成に失敗しました: {{error}}",
            adversarialExportFailed: "敵対的プロンプトのエクスポートに失敗しました: {{error}}",
            evaluationFailed: "評価の実行に失敗しました: {{error}}",
            progressCheckFailed: "進捗チェックエラー: {{error}}"
        },
        buttons: {
            generating: "<span class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span> 生成中...",
            running: "<span class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span> 実行中...",
            runEvaluation: "評価を実行"
        },
        misc: {
            textPreview: "テキストプレビュー: {{preview}}",
            uncategorized: "未分類",
            noDescription: "説明なし",
            promptsCompleted: "プロンプト完了",
            seconds: "{{value}}秒",
            minutesSeconds: "{{minutes}}分{{seconds}}秒",
            errorDetails: "エラー詳細:",
            statusLabel: "ステータス:",
            messageLabel: "メッセージ:"
        }
    },
    en: {
        language: {
            japanese: "Japanese",
            english: "English"
        },
        page: {
            title: "AI Safety Evaluation Automated Red Teaming",
            heading: "AI Safety Evaluation Automated Red Teaming"
        },
        session: {
            current: "Current session:",
            viewPast: "View past evaluation results"
        },
        navigation: {
            title: "Step navigation",
            step1: "1. Configure LLMs",
            step2: "2. Documents",
            step3: "3. Generate requirements",
            step4: "4. Adversarial prompts",
            step5: "5. Run evaluation"
        },
        steps: {
            next: "Go to the next step",
            step1: {
                title: "LLM settings",
                description: "Configure each LLM used for the evaluation.",
                openModal: "Open LLM settings modal"
            },
            step2: {
                title: "Upload documents",
                description: "Upload documents that include domain information about the target AI (optional).",
                fileLabel: "Document file (PDF):",
                upload: "Upload",
                uploaded: "Uploaded documents:"
            },
            step3: {
                title: "Generate requirements",
                description: "Generate safety requirements the target AI must satisfy.",
                purposeLabel: "Target AI purpose:",
                purposePlaceholder: "Enter the target AI purpose",
                purposeExample: "Example: This LLM is used as a customer support chatbot, providing product information and answering common questions.",
                countLabel: "Number of requirements to generate:",
                useDocuments: "Use uploaded documents",
                generate: "Generate requirements",
                generatedTitle: "Generated requirements:"
            },
            step4: {
                title: "Generate adversarial prompts",
                description: "Generate adversarial prompts for each requirement.",
                countLabel: "Number of prompts per requirement:",
                generate: "Generate adversarial prompts",
                generatedTitle: "Generated adversarial prompts:",
                export: "Export generated results"
            },
            step5: {
                title: "Run evaluation",
                description: "Execute adversarial prompts against the target AI and evaluate the responses.",
                run: "Run evaluation"
            }
        },
        tables: {
            requirements: {
                category: "Category",
                requirement: "Requirement",
                reason: "Reason"
            },
            adversarial: {
                category: "Category",
                requirement: "Requirement",
                prompt: "Adversarial prompt"
            }
        },
        evaluation: {
            summary: "Evaluation summary:",
            categoryResults: "Results by category:",
            viewDetails: "View detailed results",
            progress_head: "Progress: ",
            progress_tail: " prompts completed",
            estimatedTime: "Estimated remaining time: {{time}}",
            completed: "Prompts completed",
            totalLabel: "Total tests:",
            passedLabel: "Passed:",
            failedLabel: "Failed:",
            errorLabel: "Errors:"
        },
        toast: {
            success: "Success",
            error: "Error",
            warning: "Warning",
            info: "Info"
        },
        alerts: {
            settingsExported: "Settings exported",
            settingsImported: "Settings imported",
            settingsSavedBrowser: "Settings saved to browser",
            settingsLoaded: "Saved settings loaded",
            settingsCopied: "Settings copied",
            llmSaved: "LLM settings saved",
            documentUploaded: "Document uploaded",
            requirementsGenerated: "Requirements generated",
            noRequirementsGenerated: "No requirements were generated. Please try another LLM provider.",
            adversarialGenerated: "Adversarial prompts generated",
            adversarialExported: "Exported adversarial prompts as CSV",
            evaluationCompleted: "Evaluation completed"
        },
        warnings: {
            noSavedSettings: "No saved settings were found",
            noFileSelected: "No file selected",
            generateRequirementsFirst: "Generate requirements first",
            generateAdversarialFirst: "Generate adversarial prompts first",
            runLlmSetupFirst: "Please configure the LLMs first",
            noAdversarialToExport: "No adversarial prompts to export"
        },
        errors: {
            settingsImportFailed: "Failed to import settings: {{error}}",
            settingsLoadFailed: "Failed to load settings: {{error}}",
            llmSaveFailed: "Failed to save LLM settings: {{error}}",
            documentUploadFailed: "Failed to upload document: {{error}}",
            requirementsMissing: "No requirement data was returned from the server",
            requirementsGenerationFailed: "Failed to generate requirements: {{status}} {{statusText}}",
            requirementsProcessingError: "An error occurred while processing requirements: {{error}}",
            requirementsRequestNoResponse: "No response to the requirements generation request. Please check your network connection.",
            adversarialGenerationFailed: "Failed to generate adversarial prompts: {{error}}",
            adversarialExportFailed: "Failed to export adversarial prompts: {{error}}",
            evaluationFailed: "Failed to run evaluation: {{error}}",
            progressCheckFailed: "Progress check error: {{error}}"
        },
        buttons: {
            generating: "<span class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span> Generating...",
            running: "<span class=\"spinner-border spinner-border-sm\" role=\"status\" aria-hidden=\"true\"></span> Running...",
            runEvaluation: "Run evaluation"
        },
        misc: {
            textPreview: "Text preview: {{preview}}",
            uncategorized: "Uncategorized",
            noDescription: "No description",
            promptsCompleted: "Prompts completed",
            seconds: "{{value}} seconds",
            minutesSeconds: "{{minutes}} min {{seconds}} sec",
            errorDetails: "Error details:",
            statusLabel: "Status:",
            messageLabel: "Message:"
        }
    }
};

const textMap = {
    "- アップロードされたドキュメントのテキスト": { ja: "- アップロードされたドキュメントのテキスト", en: "- Text of uploaded documents" },
    "- ターゲットAIの使用目的": { ja: "- ターゲットAIの使用目的", en: "- Purpose of the target AI" },
    "- 生成する敵対的プロンプトの数": { ja: "- 生成する敵対的プロンプトの数", en: "- Number of adversarial prompts to generate" },
    "- 生成する要件の数": { ja: "- 生成する要件の数", en: "- Number of requirements to generate" },
    "- 要件のカテゴリ": { ja: "- 要件のカテゴリ", en: "- Requirement category" },
    "- 要件の説明": { ja: "- 要件の説明", en: "- Requirement description" },
    "1. LLM設定": { ja: "1. LLM設定", en: "1. Configure LLMs" },
    "2. ドキュメント": { ja: "2. ドキュメント", en: "2. Documents" },
    "3. 要件生成": { ja: "3. 要件生成", en: "3. Generate requirements" },
    "4. 敵対的プロンプト": { ja: "4. 敵対的プロンプト", en: "4. Adversarial prompts" },
    "5. 評価実行": { ja: "5. 評価実行", en: "5. Run evaluation" },
    "AIセーフティ評価 自動レッドチーミング": { ja: "AIセーフティ評価 自動レッドチーミング", en: "AI Safety Evaluation Automated Red Teaming" },
    "APIエンドポイント:": { ja: "APIエンドポイント:", en: "API Endpoint:" },
    "APIキー (オプション):": { ja: "APIキー (オプション):", en: "API Key (Optional):" },
    "Hugging Faceの場合、デフォルトは \"meta-llama/Meta-Llama-3-8B-Instruct\"": { ja: "Hugging Faceの場合、デフォルトは \"meta-llama/Meta-Llama-3-8B-Instruct\"", en: "For Hugging Face, the default is \"meta-llama/Meta-Llama-3-8B-Instruct\"" },
    "LLMの設定": { ja: "LLMの設定", en: "LLM Settings" },
    "LLM設定": { ja: "LLM設定", en: "LLM Settings" },
    "LLM設定モーダルを開く": { ja: "LLM設定モーダルを開く", en: "Open LLM settings modal" },
    "Ollama APIエンドポイント:": { ja: "Ollama APIエンドポイント:", en: "Ollama API Endpoint:" },
    "Ollamaの場合、デフォルトは \"llama3\" または \"llama3:8b\"": { ja: "Ollamaの場合、デフォルトは \"llama3\" または \"llama3:8b\"", en: "For Ollama, the default is \"llama3\" or \"llama3:8b\"" },
    "ここに入力された内容は、基本のシステムプロンプトに追加されます。": { ja: "ここに入力された内容は、基本のシステムプロンプトに追加されます。", en: "Content entered here is appended to the base system prompt." },
    "アップロード": { ja: "アップロード", en: "Upload" },
    "アップロードしたドキュメントを使用する": { ja: "アップロードしたドキュメントを使用する", en: "Use uploaded documents" },
    "アップロード済みドキュメント:": { ja: "アップロード済みドキュメント:", en: "Uploaded documents:" },
    "エクスポート/インポート": { ja: "エクスポート/インポート", en: "Export/Import" },
    "エラー:": { ja: "エラー:", en: "Errors:" },
    "エンドポイントURL:": { ja: "エンドポイントURL:", en: "Endpoint URL:" },
    "カスタムエンドポイント": { ja: "カスタムエンドポイント", en: "Custom endpoint" },
    "カスタムエンドポイントの場合は任意の値を設定できます": { ja: "カスタムエンドポイントの場合は任意の値を設定できます", en: "Any value can be used for custom endpoints." },
    "カスタムエンドポイント固有の設定フィールド": { ja: "カスタムエンドポイント固有の設定フィールド", en: "Custom endpoint specific settings" },
    "カテゴリ": { ja: "カテゴリ", en: "Category" },
    "カテゴリ別結果:": { ja: "カテゴリ別結果:", en: "Results by category:" },
    "キャンセル": { ja: "キャンセル", en: "Cancel" },
    "システムプロンプト:": { ja: "システムプロンプト:", en: "System prompt:" },
    "ステップナビゲーション": { ja: "ステップナビゲーション", en: "Step navigation" },
    "ターゲットAI": { ja: "ターゲットAI", en: "Target AI" },
    "ターゲットAIが満たすべき安全要件を生成します。": { ja: "ターゲットAIが満たすべき安全要件を生成します。", en: "Generate safety requirements the target AI must satisfy." },
    "ターゲットAIに対して敵対的プロンプトを実行し、応答を評価します。": { ja: "ターゲットAIに対して敵対的プロンプトを実行し、応答を評価します。", en: "Execute adversarial prompts against the target AI and evaluate the responses." },
    "ターゲットAIのドメイン情報を含むドキュメントをアップロードします（オプション）。": { ja: "ターゲットAIのドメイン情報を含むドキュメントをアップロードします（オプション）。", en: "Upload documents containing domain information about the target AI (optional)." },
    "ターゲットAIの使用目的:": { ja: "ターゲットAIの使用目的:", en: "Target AI purpose:" },
    "ターゲットAIは評価対象のため、システムプロンプトを自由に設定できます。": { ja: "ターゲットAIは評価対象のため、システムプロンプトを自由に設定できます。", en: "As the target AI is under evaluation, you can configure its system prompt freely." },
    "ターゲットプレフィックス:": { ja: "ターゲットプレフィックス:", en: "Target prefix:" },
    "デフォルトに戻す": { ja: "デフォルトに戻す", en: "Reset to default" },
    "デフォルトは http://localhost:11434 です": { ja: "デフォルトは http://localhost:11434 です", en: "The default is http://localhost:11434." },
    "ドキュメントのアップロード": { ja: "ドキュメントのアップロード", en: "Upload documents" },
    "ドキュメントファイル（PDF）:": { ja: "ドキュメントファイル（PDF）:", en: "Document file (PDF):" },
    "プロキシURL:": { ja: "プロキシURL:", en: "Proxy URL:" },
    "プロキシを使用する": { ja: "プロキシを使用する", en: "Use proxy" },
    "プロキシパスワード:": { ja: "プロキシパスワード:", en: "Proxy password:" },
    "プロキシユーザー名:": { ja: "プロキシユーザー名:", en: "Proxy username:" },
    "プロキシ設定": { ja: "プロキシ設定", en: "Proxy settings" },
    "プロバイダー:": { ja: "プロバイダー:", en: "Provider:" },
    "プロンプト完了": { ja: "プロンプト完了", en: "Prompts completed" },
    "ベースシステムプロンプトの編集（上級者向け）": { ja: "ベースシステムプロンプトの編集（上級者向け）", en: "Edit base system prompt (advanced)" },
    "ベースシステムプロンプトを編集すると、敵対的プロンプト生成の動作に不具合が生じる可能性があります。何をしているか理解している場合のみ編集してください。": { ja: "ベースシステムプロンプトを編集すると、敵対的プロンプト生成の動作に不具合が生じる可能性があります。何をしているか理解している場合のみ編集してください。", en: "Editing the base system prompt may disrupt adversarial prompt generation. Only edit if you know what you are doing." },
    "ベースシステムプロンプトを編集すると、要件生成の動作に不具合が生じる可能性があります。何をしているか理解している場合のみ編集してください。": { ja: "ベースシステムプロンプトを編集すると、要件生成の動作に不具合が生じる可能性があります。何をしているか理解している場合のみ編集してください。", en: "Editing the base system prompt may disrupt requirement generation. Only edit if you know what you are doing." },
    "モデル名:": { ja: "モデル名:", en: "Model name:" },
    "ユーザープロンプトテンプレートの編集（上級者向け）": { ja: "ユーザープロンプトテンプレートの編集（上級者向け）", en: "Edit user prompt template (advanced)" },
    "ユーザープロンプトテンプレートを編集すると、敵対的プロンプト生成の動作に不具合が生じる可能性があります。何をしているか理解している場合のみ編集してください。": { ja: "ユーザープロンプトテンプレートを編集すると、敵対的プロンプト生成の動作に不具合が生じる可能性があります。何をしているか理解している場合のみ編集してください。", en: "Editing the user prompt template may disrupt adversarial prompt generation. Only edit if you know what you are doing." },
    "ユーザープロンプトテンプレートを編集すると、要件生成の動作に不具合が生じる可能性があります。何をしているか理解している場合のみ編集してください。": { ja: "ユーザープロンプトテンプレートを編集すると、要件生成の動作に不具合が生じる可能性があります。何をしているか理解している場合のみ編集してください。", en: "Editing the user prompt template may disrupt requirement generation. Only edit if you know what you are doing." },
    "不合格:": { ja: "不合格:", en: "Failed:" },
    "使用可能なプレースホルダー:": { ja: "使用可能なプレースホルダー:", en: "Available placeholders:" },
    "例: https://hoge.azurewebsites.net/docsearch": { ja: "例: https://hoge.azurewebsites.net/docsearch", en: "Example: https://hoge.azurewebsites.net/docsearch" },
    "例: このLLMは顧客サポートチャットボットとして使用され、製品情報の提供や一般的な質問に回答します。": { ja: "例: このLLMは顧客サポートチャットボットとして使用され、製品情報の提供や一般的な質問に回答します。", en: "Example: This LLM is used as a customer support chatbot, providing product information and answering common questions." },
    "保存": { ja: "保存", en: "Save" },
    "保存した設定を読み込む": { ja: "保存した設定を読み込む", en: "Load saved settings" },
    "各要件に対する敵対的プロンプトを生成します。": { ja: "各要件に対する敵対的プロンプトを生成します。", en: "Generate adversarial prompts for each requirement." },
    "合格:": { ja: "合格:", en: "Passed:" },
    "応答評価AI": { ja: "応答評価AI", en: "Response evaluation AI" },
    "敵対AIから": { ja: "敵対AIから", en: "From adversarial AI" },
    "敵対的プロンプト": { ja: "敵対的プロンプト", en: "Adversarial prompts" },
    "敵対的プロンプトの生成": { ja: "敵対的プロンプトの生成", en: "Generate adversarial prompts" },
    "敵対的プロンプトを生成": { ja: "敵対的プロンプトを生成", en: "Generate adversarial prompts" },
    "敵対的プロンプト生成AI": { ja: "敵対的プロンプト生成AI", en: "Adversarial prompt generation AI" },
    "日本語": { ja: "日本語", en: "Japanese" },
    "次のステップへ進む": { ja: "次のステップへ進む", en: "Go to the next step" },
    "注意:": { ja: "注意:", en: "Note:" },
    "現在のセッション:": { ja: "現在のセッション:", en: "Current session:" },
    "理由": { ja: "理由", en: "Reason" },
    "環境変数HTTP_PROXY/HTTPS_PROXYが設定されている場合、空白でも使用されます": { ja: "環境変数HTTP_PROXY/HTTPS_PROXYが設定されている場合、空白でも使用されます", en: "If the HTTP_PROXY/HTTPS_PROXY environment variables are set, they will be used even if left blank." },
    "環境変数PROXY_PASSWORDが設定されている場合、空白でも使用されます": { ja: "環境変数PROXY_PASSWORDが設定されている場合、空白でも使用されます", en: "If the PROXY_PASSWORD environment variable is set, it will be used even if left blank." },
    "環境変数PROXY_USERNAMEが設定されている場合、空白でも使用されます": { ja: "環境変数PROXY_USERNAMEが設定されている場合、空白でも使用されます", en: "If the PROXY_USERNAME environment variable is set, it will be used even if left blank." },
    "環境変数から取得する場合は空欄": { ja: "環境変数から取得する場合は空欄", en: "Leave blank to use environment variables." },
    "生成された敵対的プロンプト:": { ja: "生成された敵対的プロンプト:", en: "Generated adversarial prompts:" },
    "生成された要件:": { ja: "生成された要件:", en: "Generated requirements:" },
    "生成する要件の数:": { ja: "生成する要件の数:", en: "Number of requirements to generate:" },
    "生成結果をエクスポート": { ja: "生成結果をエクスポート", en: "Export generated results" },
    "総テスト数:": { ja: "総テスト数:", en: "Total tests:" },
    "要件": { ja: "要件", en: "Requirement" },
    "要件AIから": { ja: "要件AIから", en: "From requirements AI" },
    "要件ごとに生成するプロンプト数:": { ja: "要件ごとに生成するプロンプト数:", en: "Number of prompts per requirement:" },
    "要件の生成": { ja: "要件の生成", en: "Generate requirements" },
    "要件を生成": { ja: "要件を生成", en: "Generate requirements" },
    "要件生成AI": { ja: "要件生成AI", en: "Requirements generation AI" },
    "設定をインポート": { ja: "設定をインポート", en: "Import settings" },
    "設定をエクスポート": { ja: "設定をエクスポート", en: "Export settings" },
    "設定をコピー": { ja: "設定をコピー", en: "Copy settings" },
    "設定をブラウザに保存": { ja: "設定をブラウザに保存", en: "Save settings to browser" },
    "評価AIから": { ja: "評価AIから", en: "From evaluation AI" },
    "評価に使用する各LLMの設定を行います。": { ja: "評価に使用する各LLMの設定を行います。", en: "Configure each LLM used for the evaluation." },
    "評価の実行": { ja: "評価の実行", en: "Run evaluation" },
    "評価を実行": { ja: "評価を実行", en: "Run evaluation" },
    "評価サマリー:": { ja: "評価サマリー:", en: "Evaluation summary:" },
    "詳細結果を表示": { ja: "詳細結果を表示", en: "View detailed results" },
    "追加システムプロンプト (オプション):": { ja: "追加システムプロンプト (オプション):", en: "Additional system prompt (optional):" },
    "進捗状況:": { ja: "進捗状況:", en: "Progress:" }
};

const attributes = [
    {
        selector: 'textarea[id$="LlmSystemPrompt"]',
        attr: 'placeholder',
        values: {
            ja: "基本のシステムプロンプトに追加で指示したい内容があれば入力してください",
            en: "If you want to add additional instructions to the base system prompt, enter them here."
        }
    }
];

function translateUsingTextMap(value) {
    if (!value) {
        return value;
    }
    const mapping = textMap[value];
    if (!mapping) {
        return value;
    }
    const lang = window.automatedRtI18n?.getLanguage ? window.automatedRtI18n.getLanguage() : 'ja';
    return mapping[lang] ?? mapping.ja ?? value;
}

function renderUploadedDocuments() {
    const list = document.getElementById('uploadedDocuments');
    if (!list) return;
    list.innerHTML = '';
    if (!uploadedDocuments.length) {
        return;
    }

    uploadedDocuments.forEach(doc => {
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        const previewText = automatedRtI18n.t('misc.textPreview', { preview: doc.preview });
        listItem.innerHTML = `
            <strong>${doc.filename}</strong>
            <small class="d-block text-muted">${previewText}</small>
        `;
        list.appendChild(listItem);
    });
}

function renderRequirementsTable() {
    const requirementsTable = document.getElementById('requirementsTable');
    const requirementsResult = document.getElementById('requirementsResult');
    if (!requirementsTable || !requirementsResult) return;

    requirementsTable.innerHTML = '';
    if (!requirements.length) {
        requirementsResult.style.display = 'none';
        return;
    }

    requirements.forEach(req => {
        const row = document.createElement('tr');
        const categoryText = req.category ? translateUsingTextMap(req.category) : automatedRtI18n.t('misc.uncategorized');
        const requirementText = req.requirement || automatedRtI18n.t('misc.noDescription');
        const rationale = req.rationale || '-';
        row.innerHTML = `
            <td>${categoryText}</td>
            <td>${requirementText}</td>
            <td>${rationale}</td>
        `;
        requirementsTable.appendChild(row);
    });

    requirementsResult.style.display = 'block';
}

function renderAdversarialPromptsTable() {
    const promptsTable = document.getElementById('adversarialPromptsTable');
    const promptsResult = document.getElementById('adversarialPromptsResult');
    if (!promptsTable || !promptsResult) return;

    promptsTable.innerHTML = '';
    if (!adversarialPrompts.length) {
        promptsResult.style.display = 'none';
        return;
    }

    adversarialPrompts.forEach(prompt => {
        const row = document.createElement('tr');
        const categoryText = prompt.category ? translateUsingTextMap(prompt.category) : automatedRtI18n.t('misc.uncategorized');
        const requirementText = prompt.requirement || automatedRtI18n.t('misc.noDescription');
        row.innerHTML = `
            <td>${categoryText}</td>
            <td>${requirementText}</td>
            <td>${prompt.prompt}</td>
        `;
        promptsTable.appendChild(row);
    });

    promptsResult.style.display = 'block';
}

function renderEvaluationSummary() {
    const resultContainer = document.getElementById('evaluationResult');
    if (!resultContainer) return;

    if (!evaluationSummary) {
        resultContainer.style.display = 'none';
        return;
    }

    document.getElementById('totalTests').textContent = evaluationSummary.total_tests;
    document.getElementById('passedTests').textContent = evaluationSummary.passed;
    document.getElementById('failedTests').textContent = evaluationSummary.failed;
    document.getElementById('errorTests').textContent = evaluationSummary.error;
    document.getElementById('passRate').textContent = `${evaluationSummary.pass_rate}%`;

    const categoryStatsDiv = document.getElementById('categoryStats');
    if (categoryStatsDiv) {
        categoryStatsDiv.innerHTML = '';
        Object.entries(evaluationSummary.category_stats || {}).forEach(([category, stats]) => {
            const passRate = stats.total > 0 ? (stats.passed / stats.total * 100).toFixed(2) : 0;
            const translatedCategory = translateUsingTextMap(category);
            const categoryDiv = document.createElement('div');
            categoryDiv.className = 'mb-3';
            categoryDiv.innerHTML = `
                <h6>${translatedCategory}</h6>
                <div class="progress">
                    <div class="progress-bar bg-success" role="progressbar" style="width: ${passRate}%;"
                        aria-valuenow="${passRate}" aria-valuemin="0" aria-valuemax="100">
                        ${passRate}% (${stats.passed}/${stats.total})
                    </div>
                </div>
            `;
            categoryStatsDiv.appendChild(categoryDiv);
        });
    }

    resultContainer.style.display = 'block';
}

function formatDuration(seconds) {
    if (seconds == null || Number.isNaN(seconds)) {
        return '';
    }
    if (seconds >= 60) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return automatedRtI18n.t('misc.minutesSeconds', {
            minutes,
            seconds: remainingSeconds,
        });
    }
    const rounded = Math.max(0, Math.floor(seconds));
    return automatedRtI18n.t('misc.seconds', { value: rounded });
}

function updateEstimatedTime() {
    const estimatedTimeElement = document.getElementById('estimatedTimeRemaining');
    if (!estimatedTimeElement) return;
    if (progressState.estimatedSeconds == null) {
        estimatedTimeElement.textContent = '';
        return;
    }
    const formatted = formatDuration(progressState.estimatedSeconds);
    if (!formatted) {
        estimatedTimeElement.textContent = '';
        return;
    }
    estimatedTimeElement.textContent = automatedRtI18n.t('evaluation.estimatedTime', { time: formatted });
}

automatedRtI18n.register({
    messages,
    textMap,
    attributes,
    onLanguageChange: [
        updateEstimatedTime,
        renderUploadedDocuments,
        renderRequirementsTable,
        renderAdversarialPromptsTable,
        renderEvaluationSummary,
        applyTargetSystemPromptDefault,
    ]
});


/**
 *   Move to a specific step
 */
function navigateToStep(stepNumber) {
    // Hide all steps
    for (let i = 1; i <= 5; i++) {
        document.getElementById(`step${i}`).style.display = 'none';
    }
    
    // Display a specified step
    document.getElementById(`step${stepNumber}`).style.display = 'block';
    
    // Update the status of the navigation button
    updateNavigationButtons();
}

/**
 *   Update the status (enabled/disabled) of the navigation button
 */
function updateNavigationButtons() {
    // Display the navigation bar
    document.getElementById('stepNavigation').style.display = 'block';
    
    // Determine the maximum reached steps
    let maxReachedStep = 1;
    if (currentSessionId) {
        maxReachedStep = 2; // LLM configuration is complete
        
        if (document.getElementById('requirementsTable').children.length > 0) {
            maxReachedStep = 3; // Requirements generation is complete
        }
        
        if (document.getElementById('adversarialPromptsTable').children.length > 0) {
            maxReachedStep = 4; // Adversarial prompt generation complete
        }
        
        if (document.getElementById('evaluationResult').style.display !== 'none') {
            maxReachedStep = 5; // Evaluation is complete
        }
        
    }
    
    // Set button enabled/disabled
    for (let i = 1; i <= 5; i++) {
        const button = document.getElementById(`navToStep${i}`);
        if (i <= maxReachedStep) {
            button.disabled = false;
            // Activate the button for the step currently displayed
            if (document.getElementById(`step${i}`).style.display !== 'none') {
                button.classList.add('active');
            } else {
                button.classList.remove('active');
            }
        } else {
            button.disabled = true;
            button.classList.remove('active');
        }
    }
}

/**
 *   Collect LLM settings
 */
function collectLlmSettings() {
    // Requirements Generation AI settings
    const requirementsLlm = {
        provider: document.getElementById('reqLlmProvider').value,
        model: document.getElementById('reqLlmModel').value,
        api_key: document.getElementById('reqLlmApiKey').value || null,
        api_base: document.getElementById('reqLlmApiBase').value || null,
        system_prompt: document.getElementById('reqLlmSystemPrompt').value || null,
        base_system_prompt: document.getElementById('reqLlmBaseSystemPrompt').value || null,
        user_prompt_template: document.getElementById('reqLlmUserPromptTemplate').value || null
    };

    // Adversarial Prompt Generation AI settings
    const adversarialLlm = {
        provider: document.getElementById('advLlmProvider').value,
        model: document.getElementById('advLlmModel').value,
        api_key: document.getElementById('advLlmApiKey').value || null,
        api_base: document.getElementById('advLlmApiBase').value || null,
        system_prompt: document.getElementById('advLlmSystemPrompt').value || null,
        base_system_prompt: document.getElementById('advLlmBaseSystemPrompt').value || null,
        user_prompt_template: document.getElementById('advLlmUserPromptTemplate').value || null
    };

    // Response Evaluation AI settings
    const evaluationLlm = {
        provider: document.getElementById('evalLlmProvider').value,
        model: document.getElementById('evalLlmModel').value,
        api_key: document.getElementById('evalLlmApiKey').value || null,
        api_base: document.getElementById('evalLlmApiBase').value || null,
        system_prompt: document.getElementById('evalLlmSystemPrompt').value || null
    };

    // Target AI settings
    const targetLlm = {
        provider: document.getElementById('targetLlmProvider').value,
        model: document.getElementById('targetLlmModel').value,
        api_key: document.getElementById('targetLlmApiKey').value || null,
        api_base: document.getElementById('targetLlmApiBase').value || null,
        system_prompt: document.getElementById('targetLlmSystemPrompt').value || null,
        
        // Custom endpoint settings
        custom_endpoint_url: document.getElementById('targetLlmCustomEndpointUrl')?.value || null,
        target_prefix: document.getElementById('targetLlmTargetPrefix')?.value || null,
        use_proxy: document.getElementById('targetLlmUseProxy')?.checked || false,
        proxy_url: document.getElementById('targetLlmProxyUrl')?.value || null,
        proxy_username: document.getElementById('targetLlmProxyUsername')?.value || null,
        proxy_password: document.getElementById('targetLlmProxyPassword')?.value || null
    };
    
    return {
        requirements_llm: requirementsLlm,
        adversarial_llm: adversarialLlm,
        evaluation_llm: evaluationLlm,
        target_llm: targetLlm
    };
}

/**
 *   Apply LLM settings
 */
function applyLlmSettings(settings) {
    // Requirements Generation AI Settings
    if (settings.requirements_llm) {
        document.getElementById('reqLlmProvider').value = settings.requirements_llm.provider || '';
        document.getElementById('reqLlmModel').value = settings.requirements_llm.model || '';
        document.getElementById('reqLlmApiKey').value = settings.requirements_llm.api_key || '';
        document.getElementById('reqLlmApiBase').value = settings.requirements_llm.api_base || '';
        document.getElementById('reqLlmSystemPrompt').value = settings.requirements_llm.system_prompt || '';
        
        // Advanced settings
        if (settings.requirements_llm.base_system_prompt) {
            document.getElementById('reqLlmBaseSystemPrompt').value = settings.requirements_llm.base_system_prompt;
        }
        if (settings.requirements_llm.user_prompt_template) {
            document.getElementById('reqLlmUserPromptTemplate').value = settings.requirements_llm.user_prompt_template;
        }
    }
    
    // Adversarial Prompt Generation AI settings
    if (settings.adversarial_llm) {
        document.getElementById('advLlmProvider').value = settings.adversarial_llm.provider || '';
        document.getElementById('advLlmModel').value = settings.adversarial_llm.model || '';
        document.getElementById('advLlmApiKey').value = settings.adversarial_llm.api_key || '';
        document.getElementById('advLlmApiBase').value = settings.adversarial_llm.api_base || '';
        document.getElementById('advLlmSystemPrompt').value = settings.adversarial_llm.system_prompt || '';
        
        // Advanced settings
        if (settings.adversarial_llm.base_system_prompt) {
            document.getElementById('advLlmBaseSystemPrompt').value = settings.adversarial_llm.base_system_prompt;
        }
        if (settings.adversarial_llm.user_prompt_template) {
            document.getElementById('advLlmUserPromptTemplate').value = settings.adversarial_llm.user_prompt_template;
        }
    }
    
    // Response Evaluation AI settings
    if (settings.evaluation_llm) {
        document.getElementById('evalLlmProvider').value = settings.evaluation_llm.provider || '';
        document.getElementById('evalLlmModel').value = settings.evaluation_llm.model || '';
        document.getElementById('evalLlmApiKey').value = settings.evaluation_llm.api_key || '';
        document.getElementById('evalLlmApiBase').value = settings.evaluation_llm.api_base || '';
        document.getElementById('evalLlmSystemPrompt').value = settings.evaluation_llm.system_prompt || '';
    }
    
    // Target AI settings
    if (settings.target_llm) {
        document.getElementById('targetLlmProvider').value = settings.target_llm.provider || '';
        document.getElementById('targetLlmModel').value = settings.target_llm.model || '';
        document.getElementById('targetLlmApiKey').value = settings.target_llm.api_key || '';
        document.getElementById('targetLlmApiBase').value = settings.target_llm.api_base || '';
        if (Object.prototype.hasOwnProperty.call(settings.target_llm, 'system_prompt')) {
            setTargetSystemPromptValue(settings.target_llm.system_prompt ?? '');
        } else {
            const textarea = ensureTargetSystemPromptDefaults();
            if (textarea) {
                targetSystemPromptState.isCustom = !isDefaultTargetSystemPrompt(textarea.value);
                if (!targetSystemPromptState.isCustom) {
                    applyTargetSystemPromptDefault();
                }
            }
        }

        // Custom endpoint settings
        if (document.getElementById('targetLlmCustomEndpointUrl')) {
            document.getElementById('targetLlmCustomEndpointUrl').value = settings.target_llm.custom_endpoint_url || '';
        }
        if (document.getElementById('targetLlmTargetPrefix')) {
            document.getElementById('targetLlmTargetPrefix').value = settings.target_llm.target_prefix || '';
        }
        if (document.getElementById('targetLlmUseProxy')) {
            document.getElementById('targetLlmUseProxy').checked = settings.target_llm.use_proxy || false;
            // Toggle panel display according to proxy check
            if (document.getElementById('proxySettingsPanel')) {
                document.getElementById('proxySettingsPanel').style.display = 
                    settings.target_llm.use_proxy ? 'block' : 'none';
            }
        }
        if (document.getElementById('targetLlmProxyUrl')) {
            document.getElementById('targetLlmProxyUrl').value = settings.target_llm.proxy_url || '';
        }
        if (document.getElementById('targetLlmProxyUsername')) {
            document.getElementById('targetLlmProxyUsername').value = settings.target_llm.proxy_username || '';
        }
        if (document.getElementById('targetLlmProxyPassword')) {
            document.getElementById('targetLlmProxyPassword').value = settings.target_llm.proxy_password || '';
        }
    }
    
    // Display provider-specific additional fields
    document.querySelectorAll('select[id$="LlmProvider"]').forEach(select => {
        const parentCard = select.closest('.card');
        
        // Azure-specific fields
        const azureFields = parentCard.querySelectorAll('.azure-only');
        if (select.value === 'azure') {
            azureFields.forEach(field => field.style.display = 'block');
        } else {
            azureFields.forEach(field => field.style.display = 'none');
        }
        
        // Ollama-specific fields
        const ollamaFields = parentCard.querySelectorAll('.ollama-only');
        if (select.value === 'ollama') {
            ollamaFields.forEach(field => field.style.display = 'block');
        } else {
            ollamaFields.forEach(field => field.style.display = 'none');
        }
        
        // Custom endpoint-specific fields
        const customEndpointFields = parentCard.querySelectorAll('.custom-endpoint-only');
        if (select.value === 'custom_endpoint') {
            customEndpointFields.forEach(field => field.style.display = 'block');
        } else {
            customEndpointFields.forEach(field => field.style.display = 'none');
        }
    });
}

/**
 *   Export LLM settings
 */
function exportSettings() {
    const settings = collectLlmSettings();
    
    // Create a copy without API keys (for security)
    const exportSettings = JSON.parse(JSON.stringify(settings));
    for (const llmKey in exportSettings) {
        if (exportSettings[llmKey].hasOwnProperty('api_key')) {
            exportSettings[llmKey].api_key = null;
        }
        if (exportSettings[llmKey].hasOwnProperty('proxy_password')) {
            exportSettings[llmKey].proxy_password = null;
        }
    }
    
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(exportSettings, null, 2));
    const downloadAnchorNode = document.createElement('a');
    downloadAnchorNode.setAttribute("href", dataStr);
    downloadAnchorNode.setAttribute("download", "llm_settings_" + new Date().toISOString().substring(0, 10) + ".json");
    document.body.appendChild(downloadAnchorNode); // required for firefox
    downloadAnchorNode.click();
    downloadAnchorNode.remove();
    
    showToast(automatedRtI18n.t('toast.success'), automatedRtI18n.t('alerts.settingsExported'), 'success');
}

/**
 *   Import LLM settings
 */
function importSettings(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        try {
            const settings = JSON.parse(e.target.result);
            applyLlmSettings(settings);
            showToast(automatedRtI18n.t('toast.success'), automatedRtI18n.t('alerts.settingsImported'), 'success');
        } catch (error) {
            console.error('設定のインポートエラー:', error);
            showToast(automatedRtI18n.t('toast.error'), automatedRtI18n.t('errors.settingsImportFailed', { error: error.message }), 'danger');
        }
    };
    reader.readAsText(file);
}

/**
 *   Save LLM settings to local storage
 */
function saveSettingsToLocalStorage() {
    const settings = collectLlmSettings();
    localStorage.setItem('llmSettings', JSON.stringify(settings));
    showToast(automatedRtI18n.t('toast.success'), automatedRtI18n.t('alerts.settingsSavedBrowser'), 'success');
}

/**
 *   Load LLM settings from local storage
 */
function loadSettingsFromLocalStorage() {
    const settingsStr = localStorage.getItem('llmSettings');
    if (settingsStr) {
        try {
            const settings = JSON.parse(settingsStr);
            applyLlmSettings(settings);
            showToast(automatedRtI18n.t('toast.success'), automatedRtI18n.t('alerts.settingsLoaded'), 'success');
        } catch (error) {
            console.error('設定の読み込みエラー:', error);
            showToast(automatedRtI18n.t('toast.error'), automatedRtI18n.t('errors.settingsLoadFailed', { error: error.message }), 'danger');
        }
    } else {
        showToast(automatedRtI18n.t('toast.warning'), automatedRtI18n.t('warnings.noSavedSettings'), 'warning');
    }
}

/**
 *   Save LLM settings
 */
async function saveLlmSetup() {
    try {
        const settings = collectLlmSettings();
        
        // Send LLM settings to Setup API
        const response = await axios.post('/setup_llm', settings);

        // Save session ID
        currentSessionId = response.data.session_id;

        // Reset cached data
        requirements = [];
        adversarialPrompts = [];
        uploadedDocuments = [];
        evaluationSummary = null;
        progressState.total = 0;
        progressState.completed = 0;
        progressState.estimatedSeconds = null;

        renderUploadedDocuments();
        renderRequirementsTable();
        renderAdversarialPromptsTable();
        renderEvaluationSummary();
        updateEstimatedTime();

        const progressBar = document.querySelector('#evaluationProgress .progress-bar');
        if (progressBar) {
            progressBar.style.width = '0%';
            progressBar.setAttribute('aria-valuenow', '0');
            progressBar.textContent = '0%';
        }
        const completedPromptsElement = document.getElementById('completedPrompts');
        const totalPromptsElement = document.getElementById('totalPrompts');
        if (completedPromptsElement) completedPromptsElement.textContent = '0';
        if (totalPromptsElement) totalPromptsElement.textContent = '0';
        const evaluationProgress = document.getElementById('evaluationProgress');
        if (evaluationProgress) evaluationProgress.style.display = 'none';

        // Close modal
        const modal = bootstrap.Modal.getInstance(document.getElementById('llmSetupModal'));
        modal.hide();
        
        // Display session information
        document.getElementById('currentSessionId').textContent = currentSessionId;
        document.getElementById('sessionAlert').style.display = 'block';
        
        // Display step 2
        document.getElementById('step1').style.display = 'none';
        document.getElementById('step2').style.display = 'block';
        
        // Update navigation buttons
        updateNavigationButtons();
        
        showToast(automatedRtI18n.t('toast.success'), automatedRtI18n.t('alerts.llmSaved'), 'success');
    } catch (error) {
        console.error('LLM設定保存エラー:', error);
        showToast(
            automatedRtI18n.t('toast.error'),
            automatedRtI18n.t('errors.llmSaveFailed', {
                error: error.response?.data?.detail || error.message,
            }),
            'danger'
        );
    }
}

/**
 *   Upload document
 */
async function uploadDocument() {
    if (!currentSessionId) {
        showToast(automatedRtI18n.t('toast.error'), automatedRtI18n.t('warnings.runLlmSetupFirst'), 'danger');
        return;
    }
    
    const fileInput = document.getElementById('documentFile');
    if (!fileInput.files || fileInput.files.length === 0) {
        showToast(automatedRtI18n.t('toast.warning'), automatedRtI18n.t('warnings.noFileSelected'), 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        const response = await axios.post(`/upload_document?session_id=${currentSessionId}`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data'
            }
        });
        
        // Add to uploaded document list
        uploadedDocuments.push({
            filename: response.data.filename,
            preview: response.data.text_preview || '',
        });
        renderUploadedDocuments();

        // Clear file input
        fileInput.value = '';
        
        showToast(automatedRtI18n.t('toast.success'), automatedRtI18n.t('alerts.documentUploaded'), 'success');
    } catch (error) {
        console.error('ドキュメントアップロードエラー:', error);
        showToast(
            automatedRtI18n.t('toast.error'),
            automatedRtI18n.t('errors.documentUploadFailed', {
                error: error.response?.data?.detail || error.message,
            }),
            'danger'
        );
    }
}

/**
 *   Generate requirements
 */
async function generateRequirements() {
    if (!currentSessionId) {
        showToast(automatedRtI18n.t('toast.error'), automatedRtI18n.t('warnings.runLlmSetupFirst'), 'danger');
        return;
    }
    
    var targetPurpose = document.getElementById('targetPurpose').value;
    if (!targetPurpose) {
        targetPurpose = " ";
    }
    
    // Display while generation
    const submitButton = document.querySelector('#requirementsForm button[type="submit"]');
    const originalButtonKey = submitButton.getAttribute('data-i18n');
    const originalButtonText = originalButtonKey ? automatedRtI18n.t(originalButtonKey) : submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = automatedRtI18n.t('buttons.generating');
    
    try {
        console.log('要件生成リクエスト送信...');
        const response = await axios.post('/generate_requirements', {
            session_id: currentSessionId,
            target_purpose: targetPurpose,
            use_documents: document.getElementById('useDocuments').checked,
            num_requirements: parseInt(document.getElementById('numRequirements').value),
            language: getCurrentLanguage(),
        });
        
        console.log('要件生成レスポンス受信:', response.data);
        
        // Check errors
        if (response.data.error) {
            showToast(
                automatedRtI18n.t('toast.error'),
                automatedRtI18n.t('errors.requirementsProcessingError', { error: response.data.error }),
                'danger'
            );
            console.error('APIレスポンスエラー:', response.data);
            
            // Display error details
            if (response.data.raw_response) {
                const errorDetails = document.createElement('div');
                errorDetails.className = 'alert alert-danger mt-3';
                errorDetails.innerHTML = `
                    <h5>${automatedRtI18n.t('misc.errorDetails')}</h5>
                    <pre>${response.data.raw_response}</pre>
                `;
                document.getElementById('requirementsForm').appendChild(errorDetails);
            }
            return;
        }
        
        // Save requirements
        if (!response.data.requirements) {
            showToast(automatedRtI18n.t('toast.error'), automatedRtI18n.t('errors.requirementsMissing'), 'danger');
            console.error('要件データが見つかりません:', response.data);
            return;
        }
        
        requirements = response.data.requirements || [];
        
        renderRequirementsTable();

        if (requirements.length > 0) {
            updateNavigationButtons();
            showToast(automatedRtI18n.t('toast.success'), automatedRtI18n.t('alerts.requirementsGenerated'), 'success');
        } else {
            showToast(automatedRtI18n.t('toast.warning'), automatedRtI18n.t('alerts.noRequirementsGenerated'), 'warning');
        }
    } catch (error) {
        console.error('要件生成エラー:', error);
        
        // Output error details to the console
        if (error.response) {
            console.error('エラーレスポンス:', error.response);
            console.error('ステータス:', error.response.status);
            console.error('データ:', error.response.data);
            console.error('ヘッダー:', error.response.headers);
            
            showToast(
                automatedRtI18n.t('toast.error'),
                automatedRtI18n.t('errors.requirementsGenerationFailed', {
                    status: error.response.status,
                    statusText: error.response.statusText,
                }),
                'danger'
            );
            
            // Display error details
            const errorDetails = document.createElement('div');
            errorDetails.className = 'alert alert-danger mt-3';
            errorDetails.innerHTML = `
                <h5>${automatedRtI18n.t('misc.errorDetails')}</h5>
                <p>${automatedRtI18n.t('misc.statusLabel')} ${error.response.status}</p>
                <p>${automatedRtI18n.t('misc.messageLabel')} ${error.response.statusText}</p>
                <pre>${JSON.stringify(error.response.data, null, 2)}</pre>
            `;
            document.getElementById('requirementsForm').appendChild(errorDetails);
        } else if (error.request) {
            console.error('リクエストエラー:', error.request);
            showToast(automatedRtI18n.t('toast.error'), automatedRtI18n.t('errors.requirementsRequestNoResponse'), 'danger');
        } else {
            console.error('その他のエラー:', error.message);
            showToast(
                automatedRtI18n.t('toast.error'),
                automatedRtI18n.t('errors.requirementsProcessingError', { error: error.message }),
                'danger'
            );
        }
    } finally {
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonKey ? automatedRtI18n.t(originalButtonKey) : originalButtonText;
    }
}

/**
 *   Generating adversarial prompts
 */
async function generateAdversarialPrompts() {
    if (!currentSessionId || requirements.length === 0) {
        showToast(automatedRtI18n.t('toast.error'), automatedRtI18n.t('warnings.generateRequirementsFirst'), 'danger');
        return;
    }
    
    // Display while generation
    const submitButton = document.querySelector('#adversarialPromptForm button[type="submit"]');
    const originalButtonKey = submitButton.getAttribute('data-i18n');
    const originalButtonText = originalButtonKey ? automatedRtI18n.t(originalButtonKey) : submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = automatedRtI18n.t('buttons.generating');
    
    try {
        const response = await axios.post('/generate_adversarial_prompts', {
            session_id: currentSessionId,
            target_purpose: document.getElementById('targetPurpose').value,
            prompts_per_requirement: parseInt(document.getElementById('promptsPerRequirement').value),
            language: getCurrentLanguage(),
        });
        
        // Save adversarial prompts
        adversarialPrompts = response.data.adversarial_prompts || [];
        
        // Display on adversarial prompt table
        renderAdversarialPromptsTable();

        // Update navigation buttons
        updateNavigationButtons();
        
        showToast(automatedRtI18n.t('toast.success'), automatedRtI18n.t('alerts.adversarialGenerated'), 'success');
    } catch (error) {
        console.error('敵対的プロンプト生成エラー:', error);
        showToast(
            automatedRtI18n.t('toast.error'),
            automatedRtI18n.t('errors.adversarialGenerationFailed', {
                error: error.response?.data?.detail || error.message,
            }),
            'danger'
        );
    } finally {
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonKey ? automatedRtI18n.t(originalButtonKey) : originalButtonText;
    }
}

/**
 *   Export adversarial prompts as CSV
 */
async function exportAdversarialPrompts() {
    if (!currentSessionId || adversarialPrompts.length === 0) {
        showToast(automatedRtI18n.t('toast.error'), automatedRtI18n.t('warnings.noAdversarialToExport'), 'danger');
        return;
    }

    try {
        const response = await axios.get('/export_adversarial_prompts', {
            params: {
                session_id: currentSessionId
            },
            responseType: 'blob'
        });

        const blob = new Blob([response.data], { type: 'text/csv' });
        const downloadUrl = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = downloadUrl;

        let filename = 'adversarial_prompts.csv';
        const disposition = response.headers['content-disposition'];
        if (disposition) {
            const match = disposition.match(/filename="?([^";]+)"?/i);
            if (match && match[1]) {
                filename = decodeURIComponent(match[1]);
            }
        }

        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(downloadUrl);

        showToast(automatedRtI18n.t('toast.success'), automatedRtI18n.t('alerts.adversarialExported'), 'success');
    } catch (error) {
        console.error('敵対的プロンプトのエクスポートエラー:', error);
        const errorMessage = error.response?.data?.detail || error.message || automatedRtI18n.t('misc.noDescription');
        showToast(
            automatedRtI18n.t('toast.error'),
            automatedRtI18n.t('errors.adversarialExportFailed', { error: errorMessage }),
            'danger'
        );
    }
}

/**
 *   Execute evaluation
 */
async function runEvaluation() {
    if (!currentSessionId || adversarialPrompts.length === 0) {
        showToast(automatedRtI18n.t('toast.error'), automatedRtI18n.t('warnings.generateAdversarialFirst'), 'danger');
        return;
    }
    
    // Display while evaluation
    const submitButton = document.querySelector('#evaluationForm button[type="submit"]');
    const originalButtonKey = submitButton.getAttribute('data-i18n');
    const originalButtonText = originalButtonKey ? automatedRtI18n.t(originalButtonKey) : submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = automatedRtI18n.t('buttons.running');
    
    // Display progress bar
    document.getElementById('evaluationProgress').style.display = 'block';
    
    // Initialize progress bar
    const progressBar = document.querySelector('#evaluationProgress .progress-bar');
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', 0);
    progressBar.textContent = '0%';
    
    // Display number of prompts
    const totalPromptsElement = document.getElementById('totalPrompts');
    const completedPromptsElement = document.getElementById('completedPrompts');
    totalPromptsElement.textContent = adversarialPrompts.length;
    completedPromptsElement.textContent = '0';
    progressState.total = adversarialPrompts.length;
    progressState.completed = 0;
    progressState.estimatedSeconds = null;
    updateEstimatedTime();
    
    // Start time measurement
    const startTime = new Date();
    const estimatedTimeElement = document.getElementById('estimatedTimeRemaining');
    
    try {
        // Call the evaluation execution API
        const response = await axios.post('/evaluate_target_llm', {
            session_id: currentSessionId,
            auto_run: true, // Always execute all by default
            language: getCurrentLanguage(),
        });
        
        // Monitor progress with polling
        let completed = 0;
        const checkProgress = async () => {
            try {
                const progressResponse = await axios.get(`/evaluation_progress/${currentSessionId}/${completed}`);
                const { progress, current_index, total } = progressResponse.data;
                
                // Update progress bar
                progressBar.style.width = `${progress}%`;
                progressBar.setAttribute('aria-valuenow', progress);
                progressBar.textContent = `${progress}%`;
                
                // Update completion count
                completed = current_index + 1;
                completedPromptsElement.textContent = completed;
                progressState.completed = completed;
                progressState.total = total;

                // Estimate remaining time
                if (completed > 0 && total > 0) {
                    const elapsedTime = (new Date() - startTime) / 1000; // seconds
                    const timePerPrompt = elapsedTime / completed;
                    const remainingPrompts = Math.max(0, total - completed);
                    const estimatedTimeRemaining = Math.max(0, remainingPrompts * timePerPrompt);
                    progressState.estimatedSeconds = estimatedTimeRemaining;
                    updateEstimatedTime();
                } else {
                    progressState.estimatedSeconds = null;
                    updateEstimatedTime();
                }
                
                // If it is not complete, check again
                if (completed < total) {
                    setTimeout(checkProgress, 1000); // Check every second
                } else {
                    // Display results when evaluation is complete
                    progressState.completed = total;
                    progressState.estimatedSeconds = 0;
                    updateEstimatedTime();
                    showEvaluationResults(response.data);
                }
            } catch (error) {
                console.error('進捗チェックエラー:', error);
                // If an error occurs, wait a moment and check again
                if (completed < total) {
                    setTimeout(checkProgress, 2000);
                }
            }
        };
        
        // Start progress check
        checkProgress();
    } catch (error) {
        console.error('評価実行エラー:', error);
        showToast(
            automatedRtI18n.t('toast.error'),
            automatedRtI18n.t('errors.evaluationFailed', {
                error: error.response?.data?.detail || error.message,
            }),
            'danger'
        );
        
        // Hide progress bar
        document.getElementById('evaluationProgress').style.display = 'none';
        
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonKey ? automatedRtI18n.t(originalButtonKey) : originalButtonText;
    }
}

/**
 *   Display evaluation results
 */
function showEvaluationResults(data) {
    // Hide progress bar
    document.getElementById('evaluationProgress').style.display = 'none';

    evaluationSummary = data.summary || null;
    renderEvaluationSummary();

    // Update navigation buttons
    updateNavigationButtons();

    // Reset the execute button
    const submitButton = document.querySelector('#evaluationForm button[type="submit"]');
    if (submitButton) {
        submitButton.disabled = false;
        const buttonKey = submitButton.getAttribute('data-i18n');
        submitButton.innerHTML = buttonKey ? automatedRtI18n.t(buttonKey) : automatedRtI18n.t('buttons.runEvaluation');
    }

    showToast(automatedRtI18n.t('toast.success'), automatedRtI18n.t('alerts.evaluationCompleted'), 'success');
}

/**
 *   Copy LLM settings
 */
function copyLlmSettings(fromPrefix, toPrefix) {
    // Provider
    const fromProvider = document.getElementById(`${fromPrefix}LlmProvider`).value;
    document.getElementById(`${toPrefix}LlmProvider`).value = fromProvider;
    
    // Model name
    const fromModel = document.getElementById(`${fromPrefix}LlmModel`).value;
    document.getElementById(`${toPrefix}LlmModel`).value = fromModel;
    
    // API key
    const fromApiKey = document.getElementById(`${fromPrefix}LlmApiKey`).value;
    document.getElementById(`${toPrefix}LlmApiKey`).value = fromApiKey;
    
    // API endpoint (for Azure)
    const fromApiBase = document.getElementById(`${fromPrefix}LlmApiBase`).value;
    document.getElementById(`${toPrefix}LlmApiBase`).value = fromApiBase;
    
    // Toggle Azure-specific fields on/off
    const toCard = document.getElementById(`${toPrefix}LlmProvider`).closest('.card');
    const azureFields = toCard.querySelectorAll('.azure-only');
    if (fromProvider === 'azure') {
        azureFields.forEach(field => field.style.display = 'block');
    } else {
        azureFields.forEach(field => field.style.display = 'none');
    }
    
    // Toggle Ollama-specific fields on/off
    const ollamaFields = toCard.querySelectorAll('.ollama-only');
    if (fromProvider === 'ollama') {
        ollamaFields.forEach(field => field.style.display = 'block');
    } else {
        ollamaFields.forEach(field => field.style.display = 'none');
    }
    
    // Toggle custom endpoint fields on/off
    const customEndpointFields = toCard.querySelectorAll('.custom-endpoint-only');
    if (fromProvider === 'custom_endpoint') {
        customEndpointFields.forEach(field => field.style.display = 'block');
        
        // Copy custom endpoint settings
        if (document.getElementById(`${fromPrefix}LlmCustomEndpointUrl`) && document.getElementById(`${toPrefix}LlmCustomEndpointUrl`)) {
            document.getElementById(`${toPrefix}LlmCustomEndpointUrl`).value = document.getElementById(`${fromPrefix}LlmCustomEndpointUrl`).value;
        }
        if (document.getElementById(`${fromPrefix}LlmTargetPrefix`) && document.getElementById(`${toPrefix}LlmTargetPrefix`)) {
            document.getElementById(`${toPrefix}LlmTargetPrefix`).value = document.getElementById(`${fromPrefix}LlmTargetPrefix`).value;
        }
    } else {
        customEndpointFields.forEach(field => field.style.display = 'none');
    }
    
    // Note: Do not copy system prompts (because system prompts are settings specific to each LLM)
    
    showToast(automatedRtI18n.t('toast.success'), automatedRtI18n.t('alerts.settingsCopied'), 'success');
}

/**
 *   Toast display utility
 */
function showToast(title, message, type = 'info') {
    // Create a toast element if does not exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
        document.body.appendChild(toastContainer);
    }
    
    // Create HTML for the toast
    const toastId = `toast-${Date.now()}`;
    const toastHTML = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="toast-header bg-${type} text-white">
                <strong class="me-auto">${title}</strong>
                <button type="button" class="btn-close btn-close-white" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
            <div class="toast-body">
                ${message}
            </div>
        </div>
    `;
    
    // Add the toast to container
    toastContainer.insertAdjacentHTML('beforeend', toastHTML);
    
    // Display the toast
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, {
        delay: 5000
    });
    toast.show();
    
    // Delete elements when the toast is closed
    toastElement.addEventListener('hidden.bs.toast', function() {
        toastElement.remove();
    });
}
