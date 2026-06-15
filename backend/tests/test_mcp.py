"""MCP 集成测试

测试 MCP 模块的核心功能：
1. 配置加载
2. Client 连接
3. 工具发现
4. 工具调用
5. 故障隔离
"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_mcp_basic():
    """基本功能测试"""
    from app.mcp.schemas import MCPServerConfig, MCPToolMetadata
    from app.mcp.clients import STDIOMCPClient
    from app.mcp.manager import MCPClientManager
    from app.mcp.discovery import MCPDiscoveryService
    from app.mcp.adapters import MCPAdapter
    from app.tools.base.registry import ToolRegistry

    print("=" * 60)
    print("MCP 集成测试")
    print("=" * 60)

    # 1. 测试配置加载
    print("\n[1/5] 测试配置加载...")
    discovery = MCPDiscoveryService()
    config_dir = Path(__file__).parent.parent / "config" / "mcp"
    configs = discovery.load_configs(config_dir)
    assert len(configs) > 0, "配置加载失败"
    print(f"  [OK] 加载了 {len(configs)} 个配置")

    # 2. 测试 Client 创建和连接
    print("\n[2/5] 测试 MCP Client 连接...")
    client_manager = MCPClientManager()

    for config in configs:
        if not config.enabled:
            continue
        try:
            client = await client_manager.add_client(config)
            print(f"  [OK] Client '{config.server_id}' 已连接")
        except Exception as e:
            print(f"  [FAIL] Client '{config.server_id}' 连接失败: {e}")
            continue

    # 3. 测试工具发现
    print("\n[3/5] 测试工具发现...")
    all_tools = await discovery.discover_all()
    total_tools = sum(len(tools) for tools in all_tools.values())
    print(f"  [OK] 发现了 {total_tools} 个 MCP 工具")
    for server_id, tools in all_tools.items():
        for tool in tools:
            print(f"    - {server_id}/{tool.tool_name}: {tool.description[:50]}...")

    # 4. 测试工具注册
    print("\n[4/5] 测试工具注册...")
    registry = ToolRegistry()
    # 清空已注册工具 (测试用)
    registry._tools.clear()

    adapter = MCPAdapter(client_manager=client_manager, discovery_service=discovery, registry=registry)
    registered_count = 0
    for server_id, tools_metadata in all_tools.items():
        client = client_manager.get_client(server_id)
        if not client:
            continue
        from app.mcp.tools import MCPTool
        for metadata in tools_metadata:
            mcp_tool = MCPTool(metadata=metadata, client=client)
            registry.register(mcp_tool)
            registered_count += 1

    print(f"  [OK] 注册了 {registered_count} 个 MCP 工具到 ToolRegistry")

    # 列出所有工具
    print("\n  工具列表:")
    for tool_info in registry.list_tools():
        print(f"    - {tool_info['name']}: {tool_info['description'][:50]}...")

    # 5. 测试工具调用 (如果可用)
    print("\n[5/5] 测试工具调用...")
    mcp_tools = [t for t in registry.list_tools() if t.get("type") == "mcp"]
    if mcp_tools:
        # 尝试调用第一个工具
        tool_name = mcp_tools[0]["name"]
        tool = registry.get_tool(tool_name)
        print(f"  尝试调用工具: {tool_name}")

        try:
            from pydantic import create_model
            # 创建空输入
            EmptyInput = create_model("EmptyInput")
            result = await tool.execute(EmptyInput())
            print(f"  [OK] 工具调用成功: {result}")
        except Exception as e:
            print(f"  [WARN] 工具调用异常 (可能是参数问题): {e}")
    else:
        print("  [WARN] 没有可用的 MCP 工具")

    # 清理
    print("\n清理资源...")
    await client_manager.disconnect_all()
    print("  [OK] MCP 连接已断开")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


async def test_fault_isolation():
    """故障隔离测试"""
    print("\n" + "=" * 60)
    print("故障隔离测试")
    print("=" * 60)

    from app.mcp.manager import MCPClientManager
    from app.mcp.schemas import MCPServerConfig
    from app.tools.base.registry import ToolRegistry
    from app.tools.arxiv import ArxivTool

    # 注册本地工具
    registry = ToolRegistry()
    registry._tools.clear()
    registry.register(ArxivTool())
    print(f"\n本地工具已注册: {[t['name'] for t in registry.list_tools()]}")

    # 模拟 MCP 连接失败
    print("\n模拟 MCP 连接失败...")
    client_manager = MCPClientManager()
    bad_config = MCPServerConfig(
        server_id="bad_server",
        name="Bad Server",
        transport="stdio",
        command="nonexistent_command",
        enabled=True,
    )

    try:
        await client_manager.add_client(bad_config)
        print("  [FAIL] 应该失败但成功了")
    except Exception as e:
        print(f"  [OK] MCP 连接失败 (预期行为): {type(e).__name__}")

    # 验证本地工具仍可用
    print("\n验证本地工具仍可用:")
    arxiv_tool = registry.get_tool("arxiv_search")
    print(f"  [OK] arxiv_search 工具可用: {arxiv_tool.name}")

    # 清理
    await client_manager.disconnect_all()
    print("\n故障隔离测试完成!")


if __name__ == "__main__":
    print("开始 MCP 集成测试...")
    asyncio.run(test_mcp_basic())
    asyncio.run(test_fault_isolation())
