"""MCP管理器 - 简化版"""
import json
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent


class SimpleMCPManager:
    def __init__(self, config_file: str = "mcp_config.json"):
        # 加载配置
        with open(config_file, 'r') as f:
            self.config = json.load(f)

        # 初始化大模型
        self.llm = ChatOpenAI(
            model="deepseek-chat",
            api_key="sk-f17bb0e9d999481c89d999f74f08489a",
            base_url="https://api.deepseek.com",
            temperature=0.1
        )

        self.client = None
        self.tools = []

    async def initialize(self):
        """初始化MCP客户端"""
        config = self.config.get("mcpServers", {})
        self.client = MultiServerMCPClient(config)

        # 获取所有工具
        for server_name in config.keys():
            tools = await self.client.get_tools(server_name=server_name)
            self.tools.extend(tools)

        print(f"✅ 发现 {len(self.tools)} 个MCP工具")
        print("\n===== MCP工具列表 =====")
        for tool in self.tools:
            print(tool.name)

        print("======================\n")
        allowed_tools = [
            "current_timestamp",
            "finance_news",
            "stock_data",
            "index_data",
            "macro_econ",
            "company_performance",
            "fund_data",
            "money_flow",
            "hot_news_7x24",
        ]

        self.tools = [
            tool for tool in self.tools
            if tool.name in allowed_tools
        ]

        print(f"✅ 过滤后剩余 {len(self.tools)} 个工具")

        return True

    def create_agent(self, system_prompt: str, use_tools: bool = True):
        """创建智能体"""
        tools = self.tools if use_tools else []
        agent = create_react_agent(
            self.llm,
            tools,
            prompt=system_prompt
        )
        # # 创建带系统提示的LLM
        # llm_with_prompt = self.llm.bind(system=system_prompt)
        #
        # # 创建React智能体
        # agent = create_react_agent(llm_with_prompt, tools)
        return agent