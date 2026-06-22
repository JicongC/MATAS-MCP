"""工作流定义 - 简化版（3个智能体）"""
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from mcp_manager import SimpleMCPManager


# 定义State
class SimpleState(TypedDict):
    user_query: str
    company_info: str
    market_analysis: str
    final_decision: str
    messages: List[str]


# 全局MCP管理器
mcp = SimpleMCPManager()


# 节点1：公司信息收集
async def company_info_node(state: SimpleState) -> SimpleState:
    print("\n📋 步骤1：收集公司信息...")

    agent = mcp.create_agent(
        system_prompt="你是信息收集专家，负责获取公司基础信息。",
        use_tools=True  # 使用MCP工具
    )

    prompt = f"获取以下公司的基本信息：{state['user_query']}"
    result = await agent.ainvoke({"messages": [("user", prompt)]})

    state['company_info'] = result['messages'][-1].content
    state['messages'].append(f"✅ 公司信息：{state['company_info'][:100]}...")

    return state


# 节点2：市场分析
async def market_analysis_node(state: SimpleState) -> SimpleState:
    print("\n📊 步骤2：市场分析...")

    agent = mcp.create_agent(
        system_prompt="你是市场分析师，负责分析股票市场数据。",
        use_tools=True  # 使用MCP工具
    )

    prompt = f"""
    公司信息：{state['company_info']}

    任务：
    1. 获取该公司的股价数据
    2. 分析价格趋势
    3. 给出技术面评估
    """

    result = await agent.ainvoke({"messages": [("user", prompt)]})

    state['market_analysis'] = result['messages'][-1].content
    state['messages'].append(f"✅ 市场分析：{state['market_analysis'][:100]}...")

    return state


# 节点3：投资决策
async def decision_node(state: SimpleState) -> SimpleState:
    print("\n💰 步骤3：投资决策...")

    agent = mcp.create_agent(
        system_prompt="你是投资决策专家，综合信息给出投资建议。",
        use_tools=False  # 不使用工具，纯分析
    )

    prompt = f"""
    === 已知信息 ===
    公司信息：{state['company_info']}
    市场分析：{state['market_analysis']}

    === 任务 ===
    基于以上信息，给出明确的投资建议：
    1. 是否建议买入/卖出/持有
    2. 理由是什么
    3. 风险提示
    """

    result = await agent.ainvoke({"messages": [("user", prompt)]})

    state['final_decision'] = result['messages'][-1].content
    state['messages'].append(f"✅ 投资决策：{state['final_decision'][:100]}...")

    return state


# 构建工作流
def build_simple_workflow():
    workflow = StateGraph(SimpleState)

    # 添加节点
    workflow.add_node("company_info", company_info_node)
    workflow.add_node("market_analysis", market_analysis_node)
    workflow.add_node("decision", decision_node)

    # 连接节点
    workflow.set_entry_point("company_info")
    workflow.add_edge("company_info", "market_analysis")
    workflow.add_edge("market_analysis", "decision")
    workflow.add_edge("decision", END)

    return workflow.compile()