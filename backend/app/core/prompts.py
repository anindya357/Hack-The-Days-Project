DOC_ASSISTANT_SYSTEM = """You are a documentation assistant.

Answer ONLY using retrieved documentation context.
If information is unavailable, say you don't know.
Always cite page URLs.
Generate production-ready code when code is requested.
Keep answers concise, technical, and useful.
"""

ANSWER_PROMPT = """Question:
{question}

Retrieved documentation context:
{context}

Return:
1. A direct answer.
2. A production-ready code example when helpful.
3. Citations using the source URLs.
4. Any uncertainty if the retrieved context is incomplete.
"""

COMPARE_PROMPT = """Compare these frameworks or documentation sets:
{left} vs {right}

Left context:
{left_context}

Right context:
{right_context}

Create a concise markdown table with Feature, {left}, {right}, and Notes columns.
Only use the retrieved documentation. If a point is missing, mark it as unknown.
End with citations for both sides.
"""

CODE_PROMPT = """User wants code:
{request}

Documentation context:
{context}

Generate production-ready code using only the retrieved documentation.
If a required detail is not in the context, explicitly say what is missing.
Include citations after the code.
"""

SUMMARY_PROMPT = """Summarize this documentation set for a developer:
{request}

Documentation context:
{context}

Return concepts, a Mermaid flowchart, and a short learning roadmap.
Only use the retrieved documentation.
"""
