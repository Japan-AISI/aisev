/**
 *   Frontend scripts
 */

// Global variables
let currentSessionId = null;
let requirements = [];
let adversarialPrompts = [];


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
        document.getElementById('targetLlmSystemPrompt').value = settings.target_llm.system_prompt || '';
        
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
    
    showToast('成功', '設定をエクスポートしました', 'success');
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
            showToast('成功', '設定をインポートしました', 'success');
        } catch (error) {
            console.error('設定のインポートエラー:', error);
            showToast('エラー', '設定のインポートに失敗しました: ' + error.message, 'danger');
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
    showToast('成功', '設定をブラウザに保存しました', 'success');
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
            showToast('成功', '保存された設定を読み込みました', 'success');
        } catch (error) {
            console.error('設定の読み込みエラー:', error);
            showToast('エラー', '設定の読み込みに失敗しました: ' + error.message, 'danger');
        }
    } else {
        showToast('警告', '保存された設定が見つかりませんでした', 'warning');
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
        
        showToast('成功', 'LLM設定が保存されました', 'success');
    } catch (error) {
        console.error('LLM設定保存エラー:', error);
        showToast('エラー', `LLM設定の保存に失敗しました: ${error.response?.data?.detail || error.message}`, 'danger');
    }
}

/**
 *   Upload document
 */
async function uploadDocument() {
    if (!currentSessionId) {
        showToast('エラー', 'まずLLM設定を行ってください', 'danger');
        return;
    }
    
    const fileInput = document.getElementById('documentFile');
    if (!fileInput.files || fileInput.files.length === 0) {
        showToast('警告', 'ファイルが選択されていません', 'warning');
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
        const documentsList = document.getElementById('uploadedDocuments');
        const listItem = document.createElement('li');
        listItem.className = 'list-group-item';
        listItem.innerHTML = `
            <strong>${response.data.filename}</strong>
            <small class="d-block text-muted">テキストプレビュー: ${response.data.text_preview}</small>
        `;
        documentsList.appendChild(listItem);
        
        // Clear file input
        fileInput.value = '';
        
        showToast('成功', 'ドキュメントがアップロードされました', 'success');
    } catch (error) {
        console.error('ドキュメントアップロードエラー:', error);
        showToast('エラー', `ドキュメントのアップロードに失敗しました: ${error.response?.data?.detail || error.message}`, 'danger');
    }
}

/**
 *   Generate requirements
 */
async function generateRequirements() {
    if (!currentSessionId) {
        showToast('エラー', 'まずLLM設定を行ってください', 'danger');
        return;
    }
    
    var targetPurpose = document.getElementById('targetPurpose').value;
    if (!targetPurpose) {
        targetPurpose = " ";
        //showToast('警告', 'ターゲットAIの使用目的を入力してください', 'warning');
        //return;
    }
    
    // Display while generation
    const submitButton = document.querySelector('#requirementsForm button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 生成中...';
    
    try {
        console.log('要件生成リクエスト送信...');
        const response = await axios.post('/generate_requirements', {
            session_id: currentSessionId,
            target_purpose: targetPurpose,
            use_documents: document.getElementById('useDocuments').checked,
            num_requirements: parseInt(document.getElementById('numRequirements').value)
        });
        
        console.log('要件生成レスポンス受信:', response.data);
        
        // Check errors
        if (response.data.error) {
            showToast('エラー', `要件の生成中にエラーが発生しました: ${response.data.error}`, 'danger');
            console.error('APIレスポンスエラー:', response.data);
            
            // Display error details
            if (response.data.raw_response) {
                const errorDetails = document.createElement('div');
                errorDetails.className = 'alert alert-danger mt-3';
                errorDetails.innerHTML = `
                    <h5>エラー詳細:</h5>
                    <pre>${response.data.raw_response}</pre>
                `;
                document.getElementById('requirementsForm').appendChild(errorDetails);
            }
            return;
        }
        
        // Save requirements
        if (!response.data.requirements) {
            showToast('エラー', 'サーバーからの応答に要件データがありません', 'danger');
            console.error('要件データが見つかりません:', response.data);
            return;
        }
        
        requirements = response.data.requirements;
        
        // Display on requirement table
        const requirementsTable = document.getElementById('requirementsTable');
        requirementsTable.innerHTML = '';
        
        if (requirements.length > 0) {
            requirements.forEach(req => {
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${req.category || '未分類'}</td>
                    <td>${req.requirement || '説明なし'}</td>
                    <td>${req.rationale || '-'}</td>
                `;
                requirementsTable.appendChild(row);
            });
            
            // Display results
            document.getElementById('requirementsResult').style.display = 'block';
            
            // Update navigation buttons
            updateNavigationButtons();
            
            showToast('成功', '要件が生成されました', 'success');
        } else {
            showToast('警告', '生成された要件がありません。別のLLMプロバイダーを試してみてください。', 'warning');
        }
    } catch (error) {
        console.error('要件生成エラー:', error);
        
        // Output error details to the console
        if (error.response) {
            console.error('エラーレスポンス:', error.response);
            console.error('ステータス:', error.response.status);
            console.error('データ:', error.response.data);
            console.error('ヘッダー:', error.response.headers);
            
            showToast('エラー', `要件の生成に失敗しました: ${error.response.status} ${error.response.statusText}`, 'danger');
            
            // Display error details
            const errorDetails = document.createElement('div');
            errorDetails.className = 'alert alert-danger mt-3';
            errorDetails.innerHTML = `
                <h5>エラー詳細:</h5>
                <p>ステータス: ${error.response.status}</p>
                <p>メッセージ: ${error.response.statusText}</p>
                <pre>${JSON.stringify(error.response.data, null, 2)}</pre>
            `;
            document.getElementById('requirementsForm').appendChild(errorDetails);
        } else if (error.request) {
            console.error('リクエストエラー:', error.request);
            showToast('エラー', '要件の生成リクエストに対する応答がありませんでした。ネットワーク接続を確認してください。', 'danger');
        } else {
            console.error('その他のエラー:', error.message);
            showToast('エラー', `要件の生成処理中にエラーが発生しました: ${error.message}`, 'danger');
        }
    } finally {
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
    }
}

/**
 *   Generating adversarial prompts
 */
async function generateAdversarialPrompts() {
    if (!currentSessionId || requirements.length === 0) {
        showToast('エラー', 'まず要件を生成してください', 'danger');
        return;
    }
    
    // Display while generation
    const submitButton = document.querySelector('#adversarialPromptForm button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 生成中...';
    
    try {
        const response = await axios.post('/generate_adversarial_prompts', {
            session_id: currentSessionId,
            target_purpose: document.getElementById('targetPurpose').value,
            prompts_per_requirement: parseInt(document.getElementById('promptsPerRequirement').value)
        });
        
        // Save adversarial prompts
        adversarialPrompts = response.data.adversarial_prompts;
        
        // Display on adversarial prompt table
        const promptsTable = document.getElementById('adversarialPromptsTable');
        promptsTable.innerHTML = '';
        
        adversarialPrompts.forEach(prompt => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${prompt.category}</td>
                <td>${prompt.requirement}</td>
                <td>${prompt.prompt}</td>
            `;
            promptsTable.appendChild(row);
        });
        
        // Display results
        document.getElementById('adversarialPromptsResult').style.display = 'block';
        
        // Update navigation buttons
        updateNavigationButtons();
        
        showToast('成功', '敵対的プロンプトが生成されました', 'success');
    } catch (error) {
        console.error('敵対的プロンプト生成エラー:', error);
        showToast('エラー', `敵対的プロンプトの生成に失敗しました: ${error.response?.data?.detail || error.message}`, 'danger');
    } finally {
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
    }
}

/**
 *   Export adversarial prompts as CSV
 */
async function exportAdversarialPrompts() {
    if (!currentSessionId || adversarialPrompts.length === 0) {
        showToast('エラー', 'エクスポートする敵対的プロンプトがありません', 'danger');
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

        showToast('成功', '敵対的プロンプトをCSVとしてエクスポートしました', 'success');
    } catch (error) {
        console.error('敵対的プロンプトのエクスポートエラー:', error);
        const errorMessage = error.response?.data?.detail || error.message || 'エクスポートに失敗しました';
        showToast('エラー', `敵対的プロンプトのエクスポートに失敗しました: ${errorMessage}`, 'danger');
    }
}

/**
 *   Execute evaluation
 */
async function runEvaluation() {
    if (!currentSessionId || adversarialPrompts.length === 0) {
        showToast('エラー', 'まず敵対的プロンプトを生成してください', 'danger');
        return;
    }
    
    // Display while evaluation
    const submitButton = document.querySelector('#evaluationForm button[type="submit"]');
    const originalButtonText = submitButton.innerHTML;
    submitButton.disabled = true;
    submitButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> 実行中...';
    
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
    
    // Start time measurement
    const startTime = new Date();
    const estimatedTimeElement = document.getElementById('estimatedTimeRemaining');
    
    try {
        // Call the evaluation execution API
        const response = await axios.post('/evaluate_target_llm', {
            session_id: currentSessionId,
            auto_run: true // Always execute all by default
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
                
                // Estimate remaining time
                if (completed > 0) {
                    const elapsedTime = (new Date() - startTime) / 1000; // seconds
                    const timePerPrompt = elapsedTime / completed;
                    const remainingPrompts = total - completed;
                    const estimatedTimeRemaining = remainingPrompts * timePerPrompt;
                    
                    if (estimatedTimeRemaining > 0) {
                        let timeString = '';
                        if (estimatedTimeRemaining > 60) {
                            const minutes = Math.floor(estimatedTimeRemaining / 60);
                            const seconds = Math.floor(estimatedTimeRemaining % 60);
                            timeString = `${minutes}分${seconds}秒`;
                        } else {
                            timeString = `${Math.floor(estimatedTimeRemaining)}秒`;
                        }
                        estimatedTimeElement.textContent = `推定残り時間: ${timeString}`;
                    }
                }
                
                // If it is not complete, check again
                if (completed < total) {
                    setTimeout(checkProgress, 1000); // Check every second
                } else {
                    // Display results when evaluation is complete
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
        showToast('エラー', `評価の実行に失敗しました: ${error.response?.data?.detail || error.message}`, 'danger');
        
        // Hide progress bar
        document.getElementById('evaluationProgress').style.display = 'none';
        
        // Reset button
        submitButton.disabled = false;
        submitButton.innerHTML = originalButtonText;
    }
}

/**
 *   Display evaluation results
 */
function showEvaluationResults(data) {
    // Hide progress bar
    document.getElementById('evaluationProgress').style.display = 'none';
    
    // Display result summary
    const summary = data.summary;
    document.getElementById('totalTests').textContent = summary.total_tests;
    document.getElementById('passedTests').textContent = summary.passed;
    document.getElementById('failedTests').textContent = summary.failed;
    document.getElementById('errorTests').textContent = summary.error;
    document.getElementById('passRate').textContent = `${summary.pass_rate}%`;
    
    // Display statistics by category
    const categoryStatsDiv = document.getElementById('categoryStats');
    categoryStatsDiv.innerHTML = '';
    
    for (const [category, stats] of Object.entries(summary.category_stats)) {
        const passRate = stats.total > 0 ? (stats.passed / stats.total * 100).toFixed(2) : 0;
        const categoryDiv = document.createElement('div');
        categoryDiv.className = 'mb-3';
        categoryDiv.innerHTML = `
            <h6>${category}</h6>
            <div class="progress">
                <div class="progress-bar bg-success" role="progressbar" style="width: ${passRate}%;" 
                    aria-valuenow="${passRate}" aria-valuemin="0" aria-valuemax="100">
                    ${passRate}% (${stats.passed}/${stats.total})
                </div>
            </div>
        `;
        categoryStatsDiv.appendChild(categoryDiv);
    }
    
    // Display results
    document.getElementById('evaluationResult').style.display = 'block';
    
    // Update navigation buttons
    updateNavigationButtons();
    
    // Reset the execute button
    const submitButton = document.querySelector('#evaluationForm button[type="submit"]');
    submitButton.disabled = false;
    submitButton.innerHTML = '評価を実行';
    
    showToast('成功', '評価が完了しました', 'success');
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
    
    showToast('成功', '設定をコピーしました', 'success');
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
