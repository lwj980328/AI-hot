INFO: 127.0.0.1:54996 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
14:53:29 [app.services.task_service] 创建任务: MCP生态发展趋势
INFO: 127.0.0.1:62001 - "POST /api/v1/tasks HTTP/1.1" 200 OK
INFO: 127.0.0.1:60881 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:64113 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:64115 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
14:53:30 [app.services.workflow_service] 任务状态已更新: f80a1138-993b-45d4-aaed-43bdb4f15a21 -> planning
14:53:31 [watchfiles.main] 5 changes detected
INFO: 127.0.0.1:53475 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:56646 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:63752 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:58832 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:61228 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:62904 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
14:53:40 [app.agents.planner_agent] PlannerAgent: topic=MCP生态发展趋势, keywords=['MCP', 'Model Context Protocol', 'MCP生态', 'MCP生态趋势', 'MCP protocol development', 'MCP ecosystem', 'MCP adoption']
14:53:40 [app.services.workflow_service] 任务状态已更新: f80a1138-993b-45d4-aaed-43bdb4f15a21 -> context_loading
14:53:40 [app.memory.memory_service] 记忆检索: query='MCP生态发展趋势', research=0, trend=0, insight=0
14:53:40 [app.agents.context_agent] ContextAgent: 记忆召回为空，使用 LLM 生成上下文
INFO: 127.0.0.1:49671 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:53904 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:51821 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
14:53:47 [app.agents.context_agent] ContextAgent: 构建了 2 个上下文项
14:53:47 [app.services.workflow_service] 任务状态已更新: f80a1138-993b-45d4-aaed-43bdb4f15a21 -> researching
14:53:47 [app.tools.arxiv.arxiv_tool] ArxivTool: 搜索 'MCP', limit=10
INFO: 127.0.0.1:60534 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:53149 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:61320 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:50739 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:62221 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
14:53:54 [app.agents.research_agent] ResearchAgent: arxiv_search 获取数据成功
14:53:54 [app.tools.github.github_tool] GithubTool: 搜索 'MCP', limit=10
INFO: 127.0.0.1:51868 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
14:53:55 [app.agents.research_agent] ResearchAgent: github_search 获取数据成功
14:53:55 [app.tools.huggingface.huggingface_tool] HuggingFaceTool: 搜索 'MCP', limit=10
14:53:56 [app.agents.research_agent] ResearchAgent: huggingface_search 获取数据成功
14:53:56 [app.services.workflow_service] 工具调用记录已保存: 3 条
14:53:56 [app.services.workflow_service] 任务状态已更新: f80a1138-993b-45d4-aaed-43bdb4f15a21 -> analyzing
INFO: 127.0.0.1:54843 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:54979 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:63406 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:65109 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:58703 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:61878 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:49852 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:60778 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:50989 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:52639 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:61455 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:61340 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:55889 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
14:54:17 [app.agents.analysis_agent] AnalysisAgent: hot_topics=['MCP 生态标准化与行业统一', 'AI Agent 工具调用与环境交互', '科学计算与 HPC 中的 Agent 应用', '本地优先与事件驱动架构'], insights=4, need_more_data=False
14:54:17 [app.workflows.research.graph] 研究数据充足，进入记忆写入阶段
14:54:17 [app.services.workflow_service] 任务状态已更新: f80a1138-993b-45d4-aaed-43bdb4f15a21 -> memory_updating
14:54:17 [app.memory.memory_service] 保存 TrendSnapshot: id=18c4f9e0-0568-4fee-bda1-b2141334bfff, topic=MCP生态发展趋势
14:54:17 [app.memory.memory_service] 保存 InsightMemory: id=7735d14b-f150-4bd6-a234-6a9c757d804d, title=MCP 正成为 AI Agent 工具调用的核心标准
14:54:17 [app.memory.memory_service] 保存 InsightMemory: id=e760282a-697b-45c9-82ff-ae37a72c5796, title=Agent 在科学研究和 HPC 中的需求推动 MCP 扩展
14:54:17 [app.memory.memory_service] 保存 InsightMemory: id=3329f710-6304-4853-a864-5a6528ee107a, title=本地优先与事件驱动架构成为 Agent 记忆与协作的关键模式
14:54:17 [app.memory.memory_service] 保存 InsightMemory: id=06a62080-6a05-4d48-8afd-706b70ecfcb6, title=Agent 评估与安全仍需标准化，MCP 可为此提供底层支持
14:54:17 [app.agents.memory_agent] MemoryAgent: 写入 5 条记忆, topic=MCP生态发展趋势
14:54:17 [app.services.workflow_service] 任务状态已更新: f80a1138-993b-45d4-aaed-43bdb4f15a21 -> reporting
INFO: 127.0.0.1:59831 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:54547 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:50188 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:51602 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:65195 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:54986 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:53717 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:65405 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:56644 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:59986 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:62198 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:55590 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:65054 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:59648 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:50175 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:63775 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:51912 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:50765 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:50062 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:51318 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:56212 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:51893 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:58858 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:49300 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:57035 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:63162 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:53875 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:58846 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:64452 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:56307 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:54591 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:50662 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:55296 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:50945 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:57376 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
14:55:12 [app.services.workflow_service] 工作流执行完成: task_id=f80a1138-993b-45d4-aaed-43bdb4f15a21, report_title=MCP生态演进与AI Agent标准化趋势, report_summary_len=98, report_content_len=3619
14:55:12 [app.services.workflow_service] 报告已保存: report_id=1858fbc4-298d-4c71-a964-2063a6c98413
14:55:12 [app.services.workflow_service] 工作流执行成功: f80a1138-993b-45d4-aaed-43bdb4f15a21
INFO: 127.0.0.1:55799 - "GET /api/v1/workflows/status/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:56481 - "GET /api/v1/tasks/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:55498 - "GET /api/v1/reports/by-task/f80a1138-993b-45d4-aaed-43bdb4f15a21 HTTP/1.1" 200 OK
INFO: 127.0.0.1:54560 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:51973 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
INFO: 127.0.0.1:51423 - "GET /api/v1/tasks?limit=50&offset=0 HTTP/1.1" 200 OK
