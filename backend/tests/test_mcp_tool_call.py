"""MCP 工具调用示例

演示如何使用正确参数调用 MCP Filesystem 工具。
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


async def test_list_directory():
    """测试 list_directory 工具"""
    from app.mcp.manager import MCPClientManager
    from app.mcp.schemas import MCPServerConfig
    from app.mcp.tools import MCPTool
    from app.mcp.schemas.metadata import MCPToolMetadata
    from app.tools.base.registry import ToolRegistry

    print("=" * 60)
    print("MCP Filesystem 工具调用测试")
    print("=" * 60)

    # 1. 连接 MCP Server
    print("\n[1] 连接 Filesystem MCP Server...")
    client_manager = MCPClientManager()
    config = MCPServerConfig(
        server_id="filesystem",
        name="Filesystem MCP",
        transport="stdio",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", "D:/Code/AI热点"],
        enabled=True,
    )

    client = await client_manager.add_client(config)
    print(f"  [OK] 已连接: {client.is_connected()}")

    # 2. 发现工具
    print("\n[2] 发现工具...")
    tools = await client.list_tools()
    print(f"  [OK] 发现 {len(tools)} 个工具")

    # 3. 创建 MCPTool 实例
    print("\n[3] 创建 list_directory 工具...")
    list_dir_metadata = None
    for tool in tools:
        if tool.tool_name == "list_directory":
            list_dir_metadata = tool
            break

    if not list_dir_metadata:
        print("  [FAIL] 未找到 list_directory 工具")
        return

    mcp_tool = MCPTool(metadata=list_dir_metadata, client=client)
    print(f"  [OK] 工具名称: {mcp_tool.name}")

    # 4. 调用工具 - 列出项目根目录
    print("\n[4] 调用 list_directory 工具...")
    print(f"  目标目录: D:/Code/AI热点")

    # 动态创建输入模型
    from pydantic import create_model, Field
    ListDirInput = create_model(
        "ListDirInput",
        path=(str, Field("D:/Code/AI热点", description="目录路径"))
    )

    result = await mcp_tool.execute(ListDirInput())
    print(f"  [OK] 执行结果:")
    if result.success:
        print(result.result[:500])  # 只显示前500字符
    else:
        print(f"  [FAIL] 错误: {result.error}")

    # 5. 测试 read_file 工具
    print("\n[5] 测试 read_file 工具...")
    read_file_metadata = None
    for tool in tools:
        if tool.tool_name == "read_text_file":
            read_file_metadata = tool
            break

    if read_file_metadata:
        read_tool = MCPTool(metadata=read_file_metadata, client=client)

        ReadFileInput = create_model(
            "ReadFileInput",
            path=(str, Field("D:/Code/AI热点/README.md", description="文件路径"))
        )

        result = await read_tool.execute(ReadFileInput())
        print(f"  [OK] 读取 README.md:")
        if result.success:
            print(result.result[:300] + "..." if len(str(result.result)) > 300 else result.result)
        else:
            print(f"  [FAIL] 错误: {result.error}")

    # 清理
    print("\n清理资源...")
    await client_manager.disconnect_all()
    print("  [OK] 已断开连接")

    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_list_directory())
