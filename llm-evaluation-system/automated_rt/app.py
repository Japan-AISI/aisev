from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import uvicorn
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
import asyncio
import time
from datetime import datetime
import uuid
import shutil
import logging
import csv
import io


# Logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Importing components
from llm_client import OpenAIClient, AzureOpenAIClient, HuggingFaceClient, OllamaClient
from custom_endpoint_client import CustomEndpointClient
from document_processor import extract_text_from_pdf, summarize_text_with_llm
from models import (
    LLMRequest, 
    RequirementsGenerationRequest, 
    AdversarialPromptRequest, 
    EvaluationRequest,
    TestResult
)
from results_manager import ResultsManager
from html_exporter import setup_html_export_routes
from prompts import (
    REQUIREMENT_BASE_SYSTEM_PROMPT,
    REQUIREMENT_BASE_USER_PROMPT,
    ADVERSARIAL_BASE_SYSTEM_PROMPT,
    ADVERSARIAL_BASE_USER_PROMPT,
    EVALUATION_BASE_SYSTEM_PROMPT,
    EVALUATION_BASE_USER_PROMPT,
    TARGET_SAMPLE_SYSTEM_PROMPTS,
    TARGET_SAMPLE_SYSTEM_PROMPT,
    ENGLISH_OUTPUT_NOTE,
)


MAX_CHAR_SIZE = 8000

DEFAULT_REQUIREMENT_MODEL = "gpt-4o"
DEFAULT_ADVERSARIAL_MODEL = "gpt-4o"
DEFAULT_EVALUATION_MODEL = "gpt-4o"
DEFAULT_TARGET_MODEL = "gpt-5-mini"


app = FastAPI(title="AIセーフティ評価 自動レッドチーミング")

# Settings of templates and static files
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setting of the HTML output root
setup_html_export_routes(app)

# Directory where uploaded files are stored
UPLOAD_DIR = "uploads"
RESULTS_DIR = "results"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

# Session data
sessions = {}


def _ensure_language(language: Optional[str]) -> str:
    return "en" if language == "en" else "ja"


def _append_english_output_note(system_prompt: str, language: Optional[str]) -> str:
    lang = _ensure_language(language)
    if lang == "en" and ENGLISH_OUTPUT_NOTE not in system_prompt:
        separator = "\n" if system_prompt and not system_prompt.endswith("\n") else ""
        return f"{system_prompt}{separator}{ENGLISH_OUTPUT_NOTE}"
    return system_prompt


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Display main page"""
    return templates.TemplateResponse("index.html", {
        "requirement_base_system_prompt": REQUIREMENT_BASE_SYSTEM_PROMPT,
        "requirement_base_user_prompt": REQUIREMENT_BASE_USER_PROMPT,
        "adversarial_base_system_prompt": ADVERSARIAL_BASE_SYSTEM_PROMPT,
        "adversarial_base_user_prompt": ADVERSARIAL_BASE_USER_PROMPT,
        "target_sample_system_prompt": TARGET_SAMPLE_SYSTEM_PROMPT,
        "target_sample_system_prompt_ja": TARGET_SAMPLE_SYSTEM_PROMPTS["ja"],
        "target_sample_system_prompt_en": TARGET_SAMPLE_SYSTEM_PROMPTS["en"],
        "default_requirement_model": DEFAULT_REQUIREMENT_MODEL,
        "default_adversarial_model": DEFAULT_ADVERSARIAL_MODEL,
        "default_evaluation_model": DEFAULT_EVALUATION_MODEL,
        "default_target_model": DEFAULT_TARGET_MODEL,
        "request": request
    })

@app.post("/setup_llm")
async def setup_llm(request: LLMRequest):
    """Save LLM settings"""
    session_id = str(uuid.uuid4())
    sessions[session_id] = {
        "requirements_llm": request.requirements_llm,
        "adversarial_llm": request.adversarial_llm,
        "evaluation_llm": request.evaluation_llm,
        "target_llm": request.target_llm,
        "documents": [],
        "requirements": [],
        "adversarial_prompts": [],
        "evaluation_results": []
    }
    return {"session_id": session_id}

@app.post("/upload_document")
async def upload_document(session_id: str, file: UploadFile = File(...)):
    """Uploading and processing documents"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    
    # Saving files
    file_path = os.path.join(UPLOAD_DIR, f"{session_id}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Extract text from PDF
    if file.filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_path)
    else:
        # Processing other file formats
        text = "未対応のファイル形式です"
    
    # Add to the session
    sessions[session_id]["documents"].append({
        "name": file.filename,
        "path": file_path,
        "text": text
    })
    
    return {"filename": file.filename, "text_preview": text[:500] + "..."}

@app.post("/generate_requirements")
async def generate_requirements(request: RequirementsGenerationRequest):
    """Generation of requirements"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    
    session = sessions[request.session_id]
    language = _ensure_language(getattr(request, "language", "ja"))
    
    # Initialize LLM client by selecting the appropriate client based on the provider
    llm_client = _create_llm_client(session["requirements_llm"])
    
    # Getting document text
    documents_text = ""
    if request.use_documents:
        for doc in session["documents"]:
            documents_text += f"\n--- {doc['name']} ---\n{doc['text']}"
        if len(documents_text) > MAX_CHAR_SIZE:
            documents_text = await summarize_text_with_llm(documents_text, llm_client, MAX_CHAR_SIZE)
    
    # Default base system prompt
    default_base_system_prompt = REQUIREMENT_BASE_SYSTEM_PROMPT
    
    # Use user defined prompt or default base system prompt
    base_system_prompt = session["requirements_llm"].base_system_prompt or default_base_system_prompt
    
    # Add user custom prompts if available
    custom_prompt = session["requirements_llm"].system_prompt
    if custom_prompt:
        system_prompt = base_system_prompt + "\n\n追加指示：\n" + custom_prompt
    else:
        system_prompt = base_system_prompt

    system_prompt = _append_english_output_note(system_prompt, language)
    
    # Default user prompt template
    default_user_prompt_template = REQUIREMENT_BASE_USER_PROMPT
    
    # Use user defined prompt or default user prompt templates
    user_prompt_template = session["requirements_llm"].user_prompt_template or default_user_prompt_template
    
    # Generate user prompts from templates
    documents_placeholder = "{documents_text}" if "{documents_text}" in user_prompt_template else "{documents}"
    user_prompt = user_prompt_template.replace("{target_purpose}", request.target_purpose) \
                                      .replace(documents_placeholder, documents_text if documents_text else "参考ドキュメントはありません。") \
                                      .replace("{num_requirements}", str(request.num_requirements))
    
    # Request requirements generation to LLM
    try:
        response = await llm_client.generate(system_prompt, user_prompt)
        
        # Parse JSON response
        try:
            # First, try standard JSON parsing
            requirements = json.loads(response)
            # Save to the session
            sessions[request.session_id]["requirements"] = requirements
            return {"requirements": requirements}
        except json.JSONDecodeError as e:
            # If JSON parsing fails, try extracting JSON
            try:
                # Extract JSON-like parts (starting with [ and ending with ] )
                import re
                json_match = re.search(r'\[\s*\{.*\}\s*\]', response, re.DOTALL)
                if json_match:
                    extracted_json = json_match.group(0)
                    print(f"抽出したJSON: {extracted_json}")
                    requirements = json.loads(extracted_json)
                    # Save to the session
                    sessions[request.session_id]["requirements"] = requirements
                    return {"requirements": requirements}
                else:
                    # If any JSON-like parts are not found
                    print(f"JSONパースエラー: {e}")
                    print(f"受け取った生データ: {response}")
                    return {"error": f"応答からJSONを抽出できませんでした: {str(e)}", "raw_response": response}
            except Exception as extract_error:
                # If an error occurs during the extraction process
                print(f"JSON抽出エラー: {extract_error}")
                print(f"受け取った生データ: {response}")
                return {"error": f"応答のパースと抽出に失敗しました: {str(e)}, {str(extract_error)}", "raw_response": response}
    except Exception as e:
        # Handle other exceptions
        print(f"予期しないエラー: {e}")
        return {"error": f"要件生成中にエラーが発生しました: {str(e)}", "raw_response": str(e)}

@app.post("/generate_adversarial_prompts")
async def generate_adversarial_prompts(request: AdversarialPromptRequest):
    """Generation of adversarial prompts"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    
    session = sessions[request.session_id]
    language = _ensure_language(getattr(request, "language", "ja"))

    if not session["requirements"]:
        raise HTTPException(status_code=400, detail="先に要件を生成してください")
    
    # Initialize LLM client by selecting the appropriate client based on the provider
    llm_client = _create_llm_client(session["adversarial_llm"])
    
    all_prompts = []
    
    # Generate adversarial prompts for each requirement
    for req in session["requirements"]:
        # Default base system prompt
        default_base_system_prompt = ADVERSARIAL_BASE_SYSTEM_PROMPT
        
        # Use user defined prompt or default base system prompt
        base_system_prompt = session["adversarial_llm"].base_system_prompt or default_base_system_prompt
        
        # Add user custom prompts if available
        custom_prompt = session["adversarial_llm"].system_prompt
        if custom_prompt:
            system_prompt = base_system_prompt + "\n\n追加指示：\n" + custom_prompt
        else:
            system_prompt = base_system_prompt

        system_prompt = _append_english_output_note(system_prompt, language)
        
        # Generate the specified number of prompts
        prompts_per_requirement = int(request.prompts_per_requirement)
        successful_prompts = 0
        
        # Try each prompt generation individually
        for attempt in range(prompts_per_requirement):
            # Default user prompt template
            default_user_prompt_template = ADVERSARIAL_BASE_USER_PROMPT
            
            # Use user defined prompt or default user prompt templates
            user_prompt_template = session["adversarial_llm"].user_prompt_template or default_user_prompt_template
            
            # Generate user prompts from templates
            user_prompt = user_prompt_template.replace("{target_purpose}", request.target_purpose) \
                                            .replace("{category}", req["category"]) \
                                            .replace("{requirement}", req["requirement"]) \
                                            .replace("{prompts_per_requirement}", str(request.prompts_per_requirement)) \
                                            .replace("{current_attempt}", str(attempt + 1)) \
                                            .replace("{total_attempts}", str(prompts_per_requirement))
            
            try:
                # Request adversarial prompt generation to LLM
                logger.info(f"要件「{req['category']}: {req['requirement'][:50]}...」の敵対的プロンプト生成試行 {attempt+1}/{prompts_per_requirement}")
                response = await llm_client.generate(system_prompt, user_prompt)
                
                try:
                    # Parse JSON responses (supports both single prompt and prompt arrays)
                    try:
                        # First, attempt to parse as a string (single string enclosed in double quotes)
                        if response.strip().startswith('"') and response.strip().endswith('"'):
                            # Strings enclosed in double quotation marks
                            prompt_text = json.loads(response.strip())
                            if isinstance(prompt_text, str):
                                all_prompts.append({
                                    "prompt": prompt_text,
                                    "category": req["category"],
                                    "requirement": req["requirement"]
                                })
                                successful_prompts += 1
                                continue
                    
                        # Next, try analyzing it as an array
                        prompts = json.loads(response)
                        if isinstance(prompts, list) and len(prompts) > 0:
                            # In the case of an array, only the first element is used
                            prompt_text = prompts[0] if isinstance(prompts[0], str) else str(prompts[0])
                            all_prompts.append({
                                "prompt": prompt_text,
                                "category": req["category"],
                                "requirement": req["requirement"]
                            })
                            successful_prompts += 1
                            continue
                    
                    except json.JSONDecodeError:
                        # If JSON parsing fails, try extracting JSON
                        import re
                        
                        # First, find the string enclosed in double quotation marks
                        quote_match = re.search(r'"([^"\\]*(\\.[^"\\]*)*)"', response)
                        if quote_match:
                            prompt_text = quote_match.group(1)
                            if adversarial_prompt_check(prompt_text):
                                all_prompts.append({
                                    "prompt": prompt_text,
                                    "category": req["category"],
                                    "requirement": req["requirement"]
                                })
                                successful_prompts += 1
                            else:
                                all_prompts.append({
                                    "prompt": prompt_text,
                                    "category": req["category"],
                                    "requirement": req["requirement"],
                                    "error": True
                                })
                            continue
                        
                        # Next, try extracting the array
                        json_match = re.search(r'\[\s*"([^"\\]*(\\.[^"\\]*)*)"\s*\]', response, re.DOTALL)
                        if json_match:
                            prompt_text = json_match.group(1)
                            if adversarial_prompt_check(prompt_text):
                                all_prompts.append({
                                    "prompt": prompt_text,
                                    "category": req["category"],
                                    "requirement": req["requirement"]
                                })
                                successful_prompts += 1
                            else:
                                all_prompts.append({
                                    "prompt": prompt_text,
                                    "category": req["category"],
                                    "requirement": req["requirement"],
                                    "error": True
                                })
                            continue
                        
                        # If the parse fails
                        if len(response) == 0:
                            logger.warning(f"敵対的プロンプト生成エラー - JSONパースに失敗: レスポンス: (空)")
                            all_prompts.append({
                                "prompt": f"[エラー] 敵対的プロンプト生成AIから空の応答を受信しました。",
                                "category": req["category"],
                                "requirement": req["requirement"],
                                "error": True
                            })
                        else:
                            logger.warning(f"敵対的プロンプト生成エラー - JSONパースに失敗: レスポンス: {response[:100]}...")
                            all_prompts.append({
                                "prompt": f"[エラー] パースに失敗しました: {response[:100]}...",
                                "category": req["category"],
                                "requirement": req["requirement"],
                                "error": True
                            })
                
                except Exception as e:
                    # Handle other exception
                    logger.error(f"敵対的プロンプト生成中のエラー: {e}")
                    all_prompts.append({
                        "prompt": f"[エラー] プロンプト生成に失敗しました: {str(e)}",
                        "category": req["category"],
                        "requirement": req["requirement"],
                        "error": True
                    })
            
            except Exception as e:
                logger.error(f"LLM呼び出し中のエラー: {e}")
                all_prompts.append({
                    "prompt": f"[エラー] プロンプト生成に失敗しました: {str(e)}",
                    "category": req["category"],
                    "requirement": req["requirement"],
                    "error": True
                })
        
        # Log the results of prompt generation for this requirement
        logger.info(f"要件「{req['category']}」に対して {successful_prompts}/{prompts_per_requirement} 個の敵対的プロンプトを生成しました")
    
    # Save to the session
    sessions[request.session_id]["adversarial_prompts"] = all_prompts

    return {"adversarial_prompts": all_prompts}


@app.get("/export_adversarial_prompts")
async def export_adversarial_prompts(session_id: str):
    """Export adversarial prompts for a session as CSV"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")

    session = sessions[session_id]

    if not session.get("adversarial_prompts"):
        raise HTTPException(status_code=400, detail="エクスポート可能な敵対的プロンプトがありません")

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(["id", "ten_perspective", "text", "requirement", "scorer"])

    for idx, prompt in enumerate(session["adversarial_prompts"], start=1):
        writer.writerow([
            idx,
            prompt.get("category", ""),
            prompt.get("prompt", ""),
            prompt.get("requirement", ""),
            "requirement"
        ])

    csv_content = output.getvalue()
    filename = f"adversarial_prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        content=csv_content.encode('utf-8'),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename=\"{filename}\""
        }
    )


def adversarial_prompt_check(prompt_text):
    """Quick checking for denial of generation"""
    if prompt_text.startwith("申し訳ありません"):
        return False
    return True

@app.post("/evaluate_target_llm")
async def evaluate_target_llm(request: EvaluationRequest):
    """Evaluate target AI"""
    if request.session_id not in sessions:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")

    session = sessions[request.session_id]
    language = _ensure_language(getattr(request, "language", "ja"))

    if not session["adversarial_prompts"]:
        raise HTTPException(status_code=400, detail="先に敵対的プロンプトを生成してください")
    
    # Initialize target AI client by selecting the appropriate client based on the provider
    target_llm = _create_llm_client(session["target_llm"])
    
    # Initialize response evaluation AI client by selecting the appropriate client based on the provider
    eval_llm = _create_llm_client(session["evaluation_llm"])
    
    results = []
    total_prompts = len(session["adversarial_prompts"])
    
    # Test target AI with each adversarial prompt
    for i, prompt_data in enumerate(session["adversarial_prompts"]):
        adversarial_prompt = prompt_data["prompt"]
        
        # Fixed: Prompts with error flags will be skipped
        if prompt_data.get("error", False):
            logger.info(f"プロンプト {i+1}/{total_prompts} はエラーフラグがありスキップします: {adversarial_prompt[:50]}...")
            
            # Record the error content as is in the results
            result = {
                "prompt": adversarial_prompt,
                "category": prompt_data["category"],
                "requirement": prompt_data["requirement"],
                "target_response": "スキップされました（敵対的プロンプト生成時にエラー）",
                "evaluation": {
                    "passed": None,
                    "reason": "敵対的プロンプト生成時にエラーが発生したため評価をスキップしました",
                    "skipped": True
                }
            }
            results.append(result)
            continue
        
        logger.info(f"プロンプト {i+1}/{total_prompts} を評価中: {adversarial_prompt[:50]}...")
        
        # Send adversarial prompts to target AI
        target_system_prompt = session["target_llm"].system_prompt
        if not target_system_prompt:
            target_system_prompt = TARGET_SAMPLE_SYSTEM_PROMPTS.get(language, TARGET_SAMPLE_SYSTEM_PROMPTS["ja"])
        target_system_prompt = _append_english_output_note(target_system_prompt, language)

        target_response = await target_llm.generate(target_system_prompt, adversarial_prompt)
        
        # Preparing system prompts (base prompts + user custom prompts)
        base_system_prompt = EVALUATION_BASE_SYSTEM_PROMPT
        
        # Add user custom prompts if available
        custom_prompt = session["evaluation_llm"].system_prompt
        if custom_prompt:
            system_prompt = base_system_prompt + "\n\n追加指示：\n" + custom_prompt
        else:
            system_prompt = base_system_prompt

        system_prompt = _append_english_output_note(system_prompt, language)
        
        user_prompt = EVALUATION_BASE_USER_PROMPT % {"category": prompt_data["category"], "requirement": prompt_data["requirement"], "adversarial": adversarial_prompt, "response": target_response}
        
        try:
            eval_response = await eval_llm.generate(system_prompt, user_prompt)
            
            try:
                # Parse JSON response
                try:
                    # Attempt standard JSON parsing
                    evaluation = json.loads(eval_response)
                except json.JSONDecodeError:
                    # If JSON parsing fails, try extracting JSON
                    import re
                    json_match = re.search(r'\{\s*"passed"\s*:\s*(true|false).*\}', eval_response, re.DOTALL | re.IGNORECASE)
                    if json_match:
                        extracted_json = json_match.group(0)
                        print(f"抽出したJSON: {extracted_json}")
                        # true/falseを小文字に統一（JSONではtrueとfalseは小文字）
                        extracted_json = extracted_json.replace('True', 'true').replace('False', 'false')
                        evaluation = json.loads(extracted_json)
                    else:
                        # If extraction fails, attempt to determine from context
                        passed = None
                        reason = "自動判断できませんでした"
                        
                        # If it contains ‘true’ or ‘pass’, it will be marked as successful
                        if re.search(r'(pass|true)', eval_response.lower()):
                            passed = True
                            reason = "「pass」または「true」が応答に含まれていたため、自動的に合格と判断しました"
                        # If it contains ‘false’ or ‘fail’, it will be marked as failing
                        elif re.search(r'(fail|false)', eval_response.lower()):
                            passed = False
                            reason = "「fail」または「false」が応答に含まれていたため、自動的に不合格と判断しました"
                        
                        evaluation = {
                            "passed": passed,
                            "reason": reason,
                            "raw_response": eval_response
                        }
                
                # Record results
                result = {
                    "prompt": adversarial_prompt,
                    "category": prompt_data["category"],
                    "requirement": prompt_data["requirement"],
                    "target_response": target_response,
                    "evaluation": evaluation
                }
                results.append(result)
            except json.JSONDecodeError as e:
                # If JSON parsing fails
                print(f"評価レスポンスのパースに失敗: {e}")
                print(f"受け取った生データ: {eval_response}")
                result = {
                    "prompt": adversarial_prompt,
                    "category": prompt_data["category"],
                    "requirement": prompt_data["requirement"],
                    "target_response": target_response,
                    "evaluation": {
                        "passed": None,
                        "reason": f"評価結果のパースに失敗しました: {str(e)}",
                        "raw_response": eval_response
                    }
                }
                results.append(result)
        except Exception as e:
            print(f"評価中のエラー: {e}")
            result = {
                "prompt": adversarial_prompt,
                "category": prompt_data["category"],
                "requirement": prompt_data["requirement"],
                "target_response": target_response,
                "evaluation": {
                    "passed": None,
                    "reason": f"評価処理中にエラーが発生しました: {str(e)}",
                    "error": True
                }
            }
            results.append(result)
    
    # Save evaluation results to the session
    sessions[request.session_id]["evaluation_results"] = results
    
    # Save to a results file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = os.path.join(RESULTS_DIR, f"evaluation_{request.session_id}_{timestamp}.json")
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    # Creating a summary of results
    total = len(results)
    # Fixed: Count excluding items with a skipped flag
    not_skipped_results = [r for r in results if not r.get("evaluation", {}).get("skipped", False)]
    passed = sum(1 for r in not_skipped_results if r.get("evaluation", {}).get("passed") == True)
    failed = sum(1 for r in not_skipped_results if r.get("evaluation", {}).get("passed") == False)
    error = len(not_skipped_results) - passed - failed
    skipped = total - len(not_skipped_results)
    
    # Correct category statistics
    category_stats = {}
    for r in results:
        cat = r["category"]
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "passed": 0, "failed": 0, "skipped": 0}
        
        # Check whether evaluation has been skipped
        if r.get("evaluation", {}).get("skipped", False):
            category_stats[cat]["skipped"] += 1
        else:
            category_stats[cat]["total"] += 1
            if r.get("evaluation", {}).get("passed") == True:
                category_stats[cat]["passed"] += 1
            elif r.get("evaluation", {}).get("passed") == False:
                category_stats[cat]["failed"] += 1
    
    # Calculate the total number by category (including skipped items)
    for cat in category_stats:
        category_stats[cat]["total_with_skipped"] = category_stats[cat]["total"] + category_stats[cat]["skipped"]
    
    # Calculation of pass rate (excluding skipped items)
    total_not_skipped = total - skipped
    pass_rate = round(passed / total_not_skipped * 100, 2) if total_not_skipped > 0 else 0
    
    summary = {
        "total_tests": total,
        "passed": passed,
        "failed": failed,
        "error": error,
        "skipped": skipped,  # Number of skipped evaluations
        "pass_rate": pass_rate,
        "category_stats": category_stats,
        "result_file": result_file
    }
    
    return {
        "summary": summary,
        "results": results
    }

@app.get("/evaluation_progress/{session_id}/{prompt_index}")
async def get_evaluation_progress(session_id: str, prompt_index: int):
    """Get evaluation progress"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    
    session = sessions[session_id]
    
    if not session["adversarial_prompts"]:
        raise HTTPException(status_code=400, detail="敵対的プロンプトが見つかりません")
    
    total_prompts = len(session["adversarial_prompts"])
    
    if int(prompt_index) >= total_prompts:
        prompt_index = total_prompts - 1
    
    # Current prompt information
    current_prompt = session["adversarial_prompts"][int(prompt_index)]
    
    # Calclation of progress rate
    progress = round((int(prompt_index) + 1) / total_prompts * 100)
    
    return {
        "progress": progress,
        "current_index": int(prompt_index),
        "total": total_prompts,
        "current_prompt": current_prompt
    }

@app.get("/results/{session_id}", response_class=HTMLResponse)
async def view_results(request: Request, session_id: str):
    """Display evaluation results"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    
    session = sessions[session_id]
    
    return templates.TemplateResponse(
        "results.html", 
        {
            "request": request, 
            "session_id": session_id,
            "results": session["evaluation_results"]
        }
    )

@app.get("/past_results", response_class=HTMLResponse)
async def view_past_results(request: Request):
    """Display a list of past evaluation results files"""
    results_manager = ResultsManager()
    result_files = results_manager.get_result_files()
    
    return templates.TemplateResponse(
        "past_results.html", 
        {
            "request": request,
            "result_files": result_files
        }
    )

@app.get("/past_results/{filename}")
async def view_past_result_detail(request: Request, filename: str):
    """Display details of past evaluation results"""
    results_manager = ResultsManager()
    result = results_manager.get_result_by_filename(filename)
    
    if not result:
        raise HTTPException(status_code=404, detail="結果ファイルが見つかりません")
    
    # Extract basic information from a file name
    parts = filename.replace("evaluation_", "").replace(".json", "").split("_")
    session_id = parts[0]
    timestamp = "_".join(parts[1:]) if len(parts) > 1 else ""
    
    return templates.TemplateResponse(
        "results.html", 
        {
            "request": request,
            "session_id": session_id,
            "timestamp": timestamp,
            "results": result,
            "is_past_result": True,
            "filename": filename
        }
    )

@app.get("/api/past_results")
async def get_past_results_api():
    """Get a list of past evaluation results files in JSON format (for API)"""
    results_manager = ResultsManager()
    return results_manager.get_result_files()

@app.get("/api/past_results/{filename}")
async def get_past_result_api(filename: str):
    """Get evaluation results for specified file names in JSON format (for API)"""
    results_manager = ResultsManager()
    result = results_manager.get_result_by_filename(filename)
    
    if not result:
        raise HTTPException(status_code=404, detail="結果ファイルが見つかりません")
    
    return result

def _create_llm_client(llm_config):
    """
    Create an LLM client from LLM settings
    
    Args:
        llm_config: LLM settings
        
    Returns:
        LLM client instance
    """
    # If a custom endpoint is set, it will be prioritized
    if llm_config.provider == "custom_endpoint" and llm_config.custom_endpoint_url:
        return CustomEndpointClient(
            endpoint_url=llm_config.custom_endpoint_url,
            system_prompt=llm_config.system_prompt,
            target_prefix=llm_config.target_prefix,
            use_proxy=llm_config.use_proxy,
            proxy_url=llm_config.proxy_url,
            proxy_username=llm_config.proxy_username,
            proxy_password=llm_config.proxy_password
        )
    elif llm_config.provider == "azure":
        return AzureOpenAIClient(
            deployment_name=llm_config.model,
            api_key=llm_config.api_key,
            api_base=llm_config.api_base
        )
    elif llm_config.provider == "huggingface":
        return HuggingFaceClient(
            model_name=llm_config.model,
            api_key=llm_config.api_key
        )
    elif llm_config.provider == "ollama":
        return OllamaClient(
            model_name=llm_config.model,
            api_base=llm_config.api_base
        )
    else:
        return OpenAIClient(
            model_name=llm_config.model,
            api_key=llm_config.api_key
        )

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

