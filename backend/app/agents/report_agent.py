import logging
from app.schemas.state.agent_state import AgentState, TaskStatus
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

# 报告生成 System Prompt
REPORT_SYSTEM_PROMPT = """你是一位资深的AI领域研究报告撰写专家，擅长撰写专业、清晰、有深度的研究报告。

## 写作要求
1. 使用专业但易懂的语言，避免过度技术化
2. 结构清晰，逻辑连贯，每个章节有明确的主题
3. 数据驱动，基于提供的研究数据进行分析，不要编造数据
4. 洞察深刻，不仅描述现象，还要分析原因和趋势
5. 总字数控制在 1500-3000 字之间

## 输出格式
必须返回有效的 JSON 格式，包含以下字段：
- title: 报告标题（简洁有力，20字以内）
- summary: 执行摘要（100字以内，概括核心发现）
- markdown_content: 完整的 Markdown 报告内容"""


class ReportAgent:
    """报告Agent - 负责生成研究报告

    职责：
    - 读取 state.research, state.context, state.analysis
    - 输出 state.report（title, summary, markdown_content, is_fallback）
    """

    def __init__(self, llm_service: LLMService | None = None):
        self.llm_service = llm_service or LLMService()

    async def run(self, state: AgentState) -> AgentState:
        """生成研究报告"""
        state.status = TaskStatus.REPORTING

        # 构建研究数据摘要
        papers_summary = "\n".join(
            f"- {p.title}: {p.summary}" for p in state.research.papers
        )
        repos_summary = "\n".join(
            f"- {r.title} ({r.stars}⭐): {r.summary}" for r in state.research.repositories
        )

        # 构建模型数据摘要（新增）
        models_summary = "\n".join(
            f"- {m.title}: {m.summary} (下载量: {m.downloads})"
            for m in state.research.models
        ) if state.research.models else "无"

        # 构建上下文摘要
        context_summary = "\n".join(
            f"- [{c.item_type}] {c.title}: {c.content}"
            for c in state.context.context_items
        ) if state.context.context_items else "无"

        # 构建分析结果摘要
        insights_summary = "\n".join(
            f"- {ins.title}: {ins.description}"
            for ins in state.analysis.insights
        ) if state.analysis.insights else "无"

        hot_topics = ", ".join(state.analysis.hot_topics) if state.analysis.hot_topics else "无"
        trend_summary = state.analysis.trend_summary or "无"

        prompt = f"""请基于以下研究数据和分析结果生成一份专业的研究报告。

## 研究主题
{state.research.topic or state.user_query}

## 关键词
{', '.join(state.research.keywords)}

## 上下文信息
{context_summary}

## 研究论文
{papers_summary}

## 相关项目
{repos_summary}

## 相关模型
{models_summary}

## 分析结果
### 热点话题
{hot_topics}

### 趋势分析
{trend_summary}

### 核心洞察
{insights_summary}

请生成一份Markdown格式的研究报告，包含以下部分：
1. 标题
2. 执行摘要（100字以内）
3. 研究背景
4. 核心发现（基于分析洞察）
5. 技术趋势分析
6. 代表性项目/论文/模型介绍
7. 未来展望

请返回JSON格式：
{{
    "title": "报告标题",
    "summary": "执行摘要",
    "markdown_content": "完整的Markdown报告内容"
}}"""

        try:
            data = await self.llm_service.chat_json(
                prompt=prompt,
                system_prompt=REPORT_SYSTEM_PROMPT,
                temperature=0.3,  # 降低温度，提高报告结构稳定性
            )

            state.report.title = data.get("title", f"{state.research.topic}研究报告")
            state.report.summary = data.get("summary", "")
            markdown = data.get("markdown_content", "")

            # 追加数据来源说明
            attribution = self._build_source_attribution(state)
            if attribution:
                markdown += attribution

            state.report.markdown_content = markdown
            state.report.is_fallback = False

        except Exception as e:
            logger.warning(f"LLM调用失败，使用默认报告: {e}")
            topic = state.research.topic or state.user_query
            state.report.title = f"{topic}研究报告"
            state.report.summary = f"本报告对{topic}进行了研究分析"
            state.report.markdown_content = self._generate_default_report(state)
            state.report.is_fallback = True

        state.status = TaskStatus.COMPLETED
        return state

    def _build_source_attribution(self, state: AgentState) -> str:
        """构建数据来源说明章节

        根据 state.research.data_source_tags 生成 Markdown 格式的来源说明，
        帮助读者区分哪些数据是真实 API 获取、哪些是 LLM 模拟生成。
        """
        tags = state.research.data_source_tags
        sources = state.research.data_sources

        if not tags or not sources:
            return ""

        real_sources = [s for s, t in zip(sources, tags) if t == "real"]
        simulated_sources = [s for s, t in zip(sources, tags) if t == "simulated"]

        lines = ["\n\n## 数据来源说明\n"]

        if real_sources:
            real_labels = self._source_to_labels(real_sources)
            lines.append(f"- **真实数据**：{', '.join(real_labels)}（来自官方 API）")
        if simulated_sources:
            sim_labels = self._source_to_labels(simulated_sources)
            lines.append(f"- **模拟数据**：{', '.join(sim_labels)}（因 API 不可用，由 LLM 生成）")

        if not real_sources:
            lines.append("\n> ⚠️ 本报告所有数据均由 LLM 模拟生成，仅供参考，不代表真实研究数据。")

        return "\n".join(lines)

    @staticmethod
    def _source_to_labels(sources: list[str]) -> list[str]:
        """将 data_source 名称转换为可读标签"""
        label_map = {
            "arxiv": "Arxiv 论文",
            "github": "GitHub 仓库",
            "huggingface": "HuggingFace 模型",
            "web": "网页搜索",
        }
        return [label_map.get(s, s) for s in sources]

    def _generate_default_report(self, state: AgentState) -> str:
        """生成默认报告（LLM调用失败时使用）

        优化：基于已有数据生成更精细的模板报告，而非简单拼接。
        """
        topic = state.research.topic or state.user_query
        keywords = ", ".join(state.research.keywords) if state.research.keywords else topic

        # 论文部分 - 按相关性排序
        papers = sorted(state.research.papers, key=lambda p: len(p.summary), reverse=True)
        papers_section = "\n".join(
            f"### {i+1}. {p.title}\n{p.summary[:300] if p.summary else '无摘要'}\n"
            for i, p in enumerate(papers[:5])  # 只展示前5篇
        ) if papers else "暂无相关论文数据。"

        # 仓库部分 - 按 Stars 排序
        repos = sorted(state.research.repositories, key=lambda r: r.stars, reverse=True)
        repos_section = "\n".join(
            f"### {i+1}. {r.title}\n"
            f"{r.summary.strip()[:200] if r.summary else '无描述'}\n"
            f"- Stars: {r.stars} | Language: {r.language or 'N/A'}\n"
            for i, r in enumerate(repos[:5])  # 只展示前5个
        ) if repos else "暂无相关项目数据。"

        # 模型部分（新增）
        models = sorted(state.research.models, key=lambda m: m.downloads, reverse=True)
        models_section = "\n".join(
            f"### {i+1}. {m.title}\n"
            f"{m.summary[:200] if m.summary else '无描述'}\n"
            f"- Downloads: {m.downloads} | Likes: {m.likes}\n"
            for i, m in enumerate(models[:5])  # 只展示前5个
        ) if models else "暂无相关模型数据。"

        # 分析结果 - 按置信度排序
        insights = sorted(state.analysis.insights, key=lambda i: i.confidence, reverse=True)
        insights_section = "\n".join(
            f"- **{ins.title}** (置信度: {ins.confidence:.0%}): {ins.description}"
            for ins in insights
        ) if insights else "暂无深度洞察。"

        hot_topics = ", ".join(state.analysis.hot_topics) if state.analysis.hot_topics else "暂无热点话题数据。"
        trend = state.analysis.trend_summary or f"{topic}领域正在快速发展，相关研究和项目数量持续增长。"

        # 计算统计数据
        paper_count = len(state.research.papers)
        repo_count = len(state.research.repositories)
        model_count = len(state.research.models)

        return f"""# {topic}研究报告

## 执行摘要

本报告对{topic}领域的最新发展进行了系统性研究分析。研究涵盖了 {paper_count} 篇学术论文、{repo_count} 个开源项目和 {model_count} 个预训练模型。关键词：{keywords}。

## 研究背景

{topic}是当前AI领域的研究热点之一，受到了学术界和工业界的广泛关注。本研究通过多源数据采集和分析，旨在揭示该领域的最新进展、技术趋势和未来方向。

## 热点话题

{hot_topics}

## 趋势分析

{trend}

## 核心洞察

{insights_section}

## 代表性论文

{papers_section}

## 相关开源项目

{repos_section}

## 相关预训练模型

{models_section}

## 未来展望

基于本次研究的发现，{topic}领域呈现以下发展趋势：

1. **技术成熟度提升**：越来越多的研究成果从实验室走向实际应用
2. **生态持续完善**：开源社区活跃度高，工具链和框架不断丰富
3. **跨领域融合**：{topic}与其他AI技术的结合将产生更多创新应用

建议持续关注该领域的顶会论文和头部开源项目的发展动态。

---
*报告生成时间: 本报告由 AI Research OS 自动生成*
*数据来源: Arxiv、GitHub、HuggingFace*
*注意: 本报告为降级版本（LLM 服务不可用），数据为模板拼接，仅供参考*
"""
