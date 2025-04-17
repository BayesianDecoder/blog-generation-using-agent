
# AI Blog Generator with Gemini + LangGraph

This project is a fully autonomous AI-powered blog generation system. It takes a user-defined topic and tone, plans the structure, performs contextual research, generates a blog in Markdown format, enriches it with SEO metadata, and optionally allows file downloads through a Streamlit frontend.

##  Features
-  Powered by **Gemini 1.5 Pro**
- Built using **LangGraph** agentic workflows
-  Generates blogs with clear structure (Markdown: headings, lists, bold text)
-  Creates SEO metadata (title, keywords, slug, etc.)
-  Simple web UI via **Streamlit**
-  Download generated blog and metadata as `.md` and `.json`

##  Project Structure

| File              | Description |
|-------------------|-------------|
| `final_pipeline.py` | Core agent pipeline built with LangGraph. Handles planning, research, writing, SEO, and file export. |
| `.env`              | Contains your environment variables including the `GOOGLE_API_KEY` for Gemini. |
| `app.py`            | Streamlit app for interacting with the pipeline via web UI. |

##  Approach

The pipeline is modular and agentic, structured as a directed graph with the following **nodes**:

### 1. `planner_node`
- Uses Gemini to break the input topic into clear subtopics
- Determines appropriate content depth (basic/intermediate/advanced)

### 2. `research_node`
- (Simulated for now) Adds quotes, recent insights, and relevant keywords

### 3. `writer_node`
- Generates a full-length blog post using the topic, subtopics, and research data
- Formats output in **Markdown** with headings, lists, and examples
- Explicitly avoids image generation

### 4. `seo_node`
- Generates structured SEO metadata (JSON format) including:
  - Title
  - Meta description
  - Keywords
  - Reading time
  - Slug

### 5. `execution_agent`
- Saves blog content to `.md` file and SEO metadata to `.json`
- Returns a CLI summary + file paths for download

##  Running Locally

### 1. Install Dependencies
```bash
pip install -r requirements.txt

```

### 2. Add your .env file:
```bash
GOOGLE_API_KEY=your_google_gemini_api_key
```

### 3. Launch Streamlit App

``` bash
streamlit run app.py
```

## Example Output
- `blog-topic-YYYYMMDD-HHMMSS.md`
- `blog-topic-YYYYMMDD-HHMMSS-metadata.json`

##  Technologies Used

- LangGraph
- Gemini Pro 1.5
- Streamlit
- LangChain
- Python 
