"""主程序 - 运行简化版系统"""
import asyncio
from workflow import build_simple_workflow, mcp, SimpleState


async def main():
    print("🚀 简化版股票分析系统启动")

    # 1. 初始化MCP
    print("\n初始化MCP连接...")
    await mcp.initialize()

    # 2. 构建工作流
    print("\n构建工作流...")
    app = build_simple_workflow()

    # 3. 用户输入
    user_query = input("\n请输入要分析的股票（如：苹果公司、AAPL、TSLA）：")

    # 4. 初始化State
    initial_state: SimpleState = {
        "user_query": user_query,
        "company_info": "",
        "market_analysis": "",
        "final_decision": "",
        "messages": []
    }

    # 5. 运行工作流
    print("\n开始分析...\n" + "=" * 50)
    result = await app.ainvoke(initial_state)

    # 6. 显示结果
    print("\n" + "=" * 50)
    print("\n📊 最终分析结果：\n")
    print(result['final_decision'])

    print("\n💾 执行日志：")
    for msg in result['messages']:
        print(f"  {msg}")


if __name__ == "__main__":
    asyncio.run(main())