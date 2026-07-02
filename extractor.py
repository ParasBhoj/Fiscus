import json
from typing import Literal, Optional
from pydantic import BaseModel, Field
from openai import OpenAI

import config

# Define the strict Pydantic extraction schema requested by the user
class RegulatoryUpdate(BaseModel):
    title: str = Field(
        description="The formal title of the regulatory update or press release"
    )
    date_issued: str = Field(
        description="The date the update was issued (e.g. June 02, 2026 or YYYY-MM-DD)"
    )
    summary: str = Field(
        description="A concise, high-value 2-sentence summary (TL;DR) of the update"
    )
    regulatory_impact: Literal["High", "Medium", "Low"] = Field(
        description="The estimated impact level of the update on financial institutions, banks, or markets"
    )
    affected_entities: list[str] = Field(
        default_factory=list,
        description="List of specific entities, banks, or sectors affected by this update."
    )

def get_llm_client() -> OpenAI:
    """
    Initializes and returns the OpenAI client configured per config settings.
    """
    # If base url is provided, use it (handles Gemini or local proxy), otherwise default to standard OpenAI
    if config.LLM_BASE_URL:
        return OpenAI(
            api_key=config.LLM_API_KEY,
            base_url=config.LLM_BASE_URL
        )
    return OpenAI(api_key=config.LLM_API_KEY)

async def extract_structured_update(raw_text: str, title_fallback: str = None, date_fallback: str = None, progress_callback=None) -> Optional[RegulatoryUpdate]:
    """
    Uses LLM to parse unstructured text into the strict Pydantic RegulatoryUpdate schema.
    Uses structured outputs or standard JSON mode as a fallback.
    """
    if not config.LLM_API_KEY or config.LLM_API_KEY == "mock-key-for-offline":
        if progress_callback:
            progress_callback("[bold yellow]LLM API Key not configured. Using Mock Extraction Mode...[/bold yellow]")
        # Return mock parsed data for demo purposes when offline
        return generate_mock_extraction(raw_text, title_fallback, date_fallback)

    client = get_llm_client()
    
    system_prompt = (
        "You are an expert financial compliance engineer. Your task is to analyze "
        "the raw text of a regulatory update (press release / notification) "
        "and extract specific information to populate the requested schema.\n"
        "Rules:\n"
        "1. 'summary' MUST be exactly a concise 2-sentence TL;DR.\n"
        "2. 'regulatory_impact' must represent the severity/importance of the policy update. "
        "For example, major penalty policies or interest rate revisions are 'High', "
        "routine pilot releases are 'Medium', and general announcements are 'Low'.\n"
        "3. Provide dates exactly as mentioned in the press release."
    )
    
    if progress_callback:
        progress_callback(f"Calling LLM ({config.LLM_MODEL}) for structured extraction...")
        
    try:
        # Method 1: Try modern Structured Outputs (.parse)
        completion = client.beta.chat.completions.parse(
            model=config.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Extract details from this press release:\n\n{raw_text}"}
            ],
            response_format=RegulatoryUpdate,
            temperature=0.1
        )
        return completion.choices[0].message.parsed
        
    except Exception as parse_error:
        if progress_callback:
            progress_callback(f"[dim]Structured output parse failed ({parse_error}). Falling back to JSON-mode...[/dim]")
            
        try:
            # Method 2: Fallback to standard chat completions with JSON Mode
            json_schema_desc = (
                "Provide the response as a JSON object matching this schema:\n"
                "{\n"
                "  \"title\": \"string\",\n"
                "  \"date_issued\": \"string\",\n"
                "  \"summary\": \"string (2 sentences TL;DR)\",\n"
                "  \"regulatory_impact\": \"High\" | \"Medium\" | \"Low\",\n"
                "  \"affected_entities\": [\"string\"]\n"
                "}"
            )
            
            completion = client.chat.completions.create(
                model=config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": f"{system_prompt}\n\n{json_schema_desc}"},
                    {"role": "user", "content": f"Extract details from this press release:\n\n{raw_text}"}
                ],
                response_format={"type": "json_object"},
                temperature=0.1
            )
            
            json_str = completion.choices[0].message.content
            return RegulatoryUpdate.model_validate_json(json_str)
            
        except Exception as fallback_error:
            if progress_callback:
                progress_callback(f"[bold red]LLM extraction failed completely: {fallback_error}[/bold red]")
            return None

def generate_mock_extraction(raw_text: str, title_fallback: str = None, date_fallback: str = None) -> RegulatoryUpdate:
    """
    Generates a deterministic mock extraction based on simple keyword matches.
    Used for offline demo / testing when no LLM API key is present.
    """
    raw_lower = raw_text.lower()
    
    # Try to extract the title from fallback or first line
    title = title_fallback
    if not title:
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        title = lines[0] if lines else "RBI Regulatory Update"
    
    # Determine mock dates
    date = date_fallback
    if not date:
        date = "June 02, 2026"
        lines = [line.strip() for line in raw_text.split("\n") if line.strip()]
        for line in lines:
            if "date:" in line.lower() or "june" in line.lower() or "may" in line.lower():
                date = line.replace("Date:", "").strip()
                break
            
    # Tailor mock summary and impact based on keywords
    if "penalty" in raw_lower:
        summary = (
            "The RBI has imposed a monetary penalty on Apex Co-operative Bank for non-compliance with interest rate directions. "
            "The action highlights the central bank's focus on enforcing strict operational compliance across co-operative banking sectors."
        )
        impact = "High"
    elif "draft guidelines" in raw_lower or "nbfc" in raw_lower:
        summary = (
            "The RBI released draft guidelines proposing a stronger liquidity risk management framework for NBFCs and CICs. "
            "These guidelines introduce stricter LCR requirements and are open for stakeholder comments until June 30, 2026."
        )
        impact = "Medium"
    elif "digital rupee" in raw_lower:
        summary = (
            "The RBI is launching a pilot program to test offline transaction capabilities for the retail Digital Rupee (e₹-R). "
            "The pilot aims to promote financial inclusion by enabling secure cash-like transactions in areas with weak internet access."
        )
        impact = "Medium"
    else:
        summary = (
            "This is a general announcement or update published on the RBI web portal. "
            "It outlines standard administrative updates or general operations of the central bank."
        )
        impact = "Low"
        
    return RegulatoryUpdate(
        title=title,
        date_issued=date,
        summary=summary,
        regulatory_impact=impact,
        affected_entities=["Apex Co-operative Bank"] if "apex" in raw_lower else []
    )

if __name__ == "__main__":
    # Small test
    print("Testing extractor with mock data...")
    sample_text = (
        "RBI imposes monetary penalty on Apex Co-operative Bank Limited\n"
        "Date: June 02, 2026\n"
        "The Reserve Bank of India has imposed a monetary penalty of 5.00 Lakh..."
    )
    result = generate_mock_extraction(sample_text)
    print(result.model_dump_json(indent=2))
