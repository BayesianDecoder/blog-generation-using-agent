import os
import json
import datetime
from dotenv import load_dotenv
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

# Initialize Gemini LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-pro",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.5,
    verbose=True
)

# -------------------- PIPELINE NODES -------------------- #

async def planner_node(state: Dict[str, Any]):
    prompt = f"""
    You are an AI blog strategist. Break down this topic into major subtopics for a full-length blog:

    Topic: {state['topic']}
    Tone: {state.get('tone', 'neutral')}

    Respond with:
    Subtopic1|Subtopic2|Subtopic3|...
    Recommended depth: [basic|intermediate|advanced]
    """
    try:
        response = await llm.ainvoke(prompt)
        lines = response.content.strip().split("\n")
        if len(lines) < 2:
            return {"error": "Planner output malformed."}
        subtopics = lines[0].split("|")
        depth = lines[1].split(":")[-1].strip()
        return {
            **state,
            "subtopics": subtopics,
            "depth_level": depth
        }
    except Exception as e:
        return {"error": f"Planner failed: {str(e)}"}

async def research_node(state: Dict[str, Any]):
    # Simulated research output
    return {
        **state,
        "research_data": {
            "quotes": "\"Knowledge is power.\" — Francis Bacon",
            "news": "No recent updates found.",
            "keywords": [state['topic'], "technology", "insights"]
        }
    }

async def writer_node(state: Dict[str, Any]):
    prompt = f"""
    Write a full-length blog post about the topic below.

    Topic: {state['topic']}
    Subtopics: {state['subtopics']}
    Research notes: {json.dumps(state['research_data'])}
    Tone: {state['tone']}

    Format using Markdown:
    - Use H2 for subtopic headings
    - Use bullet points, bold text, and examples
    - Avoid including any images
    - Keep it informative and flowing logically
    """
    try:
        response = await llm.ainvoke(prompt)
        return {**state, "draft": response.content}
    except Exception as e:
        return {"error": f"Writer failed: {str(e)}"}

async def seo_node(state: Dict[str, Any]):
    prompt = f"""
    Generate JSON SEO metadata for this blog:
    {state['draft']}

    Keywords to include: {state['research_data']['keywords']}
    Return JSON with keys: title, meta_description, keywords, reading_time, slug
    """
    try:
        response = await llm.ainvoke(prompt)
        raw = response.content.strip().strip("```json").strip("```")
        return {**state, "seo_data": json.loads(raw)}
    except Exception as e:
        return {"error": f"SEO failed: {str(e)}"}

async def execution_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        slug = state['seo_data'].get('slug', 'blog-post')
        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        base = f"{slug}-{timestamp}"

        md_file = f"{base}.md"
        with open(md_file, 'w', encoding='utf-8') as f:
            f.write(f"# {state['seo_data']['title']}\n\n{state['draft']}\n")

        json_file = f"{base}-metadata.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(state['seo_data'], f, indent=2)

        summary = f"""
🚀 Blog Generation Complete
{'-'*40}
📝 Title: {state['seo_data']['title']}
📊 Word Count: {len(state['draft'].split())}
📂 Files Created:
  - {os.path.abspath(md_file)}
  - {os.path.abspath(json_file)}
🔑 Keywords: {', '.join(state['seo_data']['keywords'][:5])}
⏱️ Generation Time: {timestamp}
"""

        return {
            "cli_summary": summary,
            "exports": {
                "markdown": md_file,
                "metadata": json_file
            },
            "draft": state["draft"],
            "seo_data": state["seo_data"]
        }
    except Exception as e:
        return {"error": f"Export failed: {str(e)}"}

# -------------------- GRAPH -------------------- #

workflow = StateGraph(dict)
workflow.add_node("planner", planner_node)
workflow.add_node("researcher", research_node)
workflow.add_node("writer", writer_node)
workflow.add_node("seo", seo_node)
workflow.add_node("executor", execution_agent)

workflow.set_entry_point("planner")
workflow.add_conditional_edges("planner", lambda s: "error" if s.get("error") else "researcher", {"error": END, "researcher": "researcher"})
workflow.add_conditional_edges("researcher", lambda s: "error" if s.get("error") else "writer", {"error": END, "writer": "writer"})
workflow.add_conditional_edges("writer", lambda s: "error" if s.get("error") else "seo", {"error": END, "seo": "seo"})
workflow.add_conditional_edges("seo", lambda s: "error" if s.get("error") else "executor", {"error": END, "executor": "executor"})
workflow.add_edge("executor", END)

# Compile blog pipeline
blog_chain = workflow.compile()

# -------------------- MAIN EXECUTION -------------------- #

if __name__ == "__main__":
    import asyncio
    import nest_asyncio
    nest_asyncio.apply()

    async def run():
        topic = input("Enter blog topic: ")
        tone = input("Enter content tone (technical, casual, professional) [default: technical]: ") or "technical"
        result = await blog_chain.ainvoke({"topic": topic, "tone": tone})
        print(result.get("cli_summary") or result.get("error"))

    asyncio.run(run())