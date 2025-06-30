import google.generativeai as genai
from typing import Dict, Any, Union, List
import os
import logging
from ..classes import ResearchState
import asyncio

logger = logging.getLogger(__name__)


class Briefing:
    """Creates briefings for each research category and updates the ResearchState."""

    def __init__(self) -> None:
        self.max_doc_length = 8000  # Maximum document content length
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        if not self.gemini_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        # Configure Gemini
        genai.configure(
            api_key=self.gemini_key,
            transport="rest",
            client_options={"api_endpoint": "https://api.openai-proxy.org/google"},
        )
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash')

    async def generate_category_briefing(
            self, docs: Union[Dict[str, Any], List[Dict[str, Any]]],
            category: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        company = context.get('company', 'Unknown')
        industry = context.get('industry', 'Unknown')
        hq_location = context.get('hq_location', 'Unknown')
        logger.info(f"Generating {category} briefing for {company} using {len(docs)} documents")

        # Send category start status
        if websocket_manager := context.get('websocket_manager'):
            if job_id := context.get('job_id'):
                await websocket_manager.send_status_update(
                    job_id=job_id,
                    status="briefing_start",
                    message=f"Generating {category} briefing",
                    result={
                        "step": "Briefing",
                        "category": category,
                        "total_docs": len(docs)
                    }
                )

        prompts = {
            'company': f"""为{company}（一家位于{hq_location}的{industry}公司）创建一份重点公司简报。
关键要求：
1. 以这样的句式开始："{company}是一家[做什么的]，为[谁]提供[什么服务]"
2. 使用以下确切的标题和要点结构：

### 核心产品/服务
* 列出独特的产品/功能
* 仅包含经验证的技术能力

### 领导团队
* 列出关键领导团队成员
* 包括他们的角色和专长

### 目标市场
* 列出特定目标受众
* 列出经验证的使用案例
* 列出已确认的客户/合作伙伴

### 关键差异化因素
* 列出独特功能
* 列出已证实的优势

### 商业模式
* 讨论产品/服务定价
* 列出分销渠道

3. 每个要点必须是单一、完整的事实
4. 不要提及"未找到信息"或"无可用数据"
5. 不要使用段落，只使用要点
6. 仅提供简报内容，不要解释或评论
7. 所有内容必须使用中文输出""",

            'industry': f"""你是世界顶尖的行业分析师，精通市场研究、竞争情报和战略预测。为{company}（一家位于{hq_location}的{industry}公司）创建一份Gartner风格的行业分析报告。

关键要求：
1. 基于公开数据、历史趋势和逻辑推测，生成清晰有条理的见解
2. 用假设做数据支持的预测（要说明假设）
3. 找出顶尖厂商，按细分领域、规模或创新性分类
4. 指出风险、新兴玩家和未来趋势
5. 明确区分估计数据和已知数据

使用以下结构：

### 1. 市场概览
* {company}的市场定位和细分
* 当前市场规模及增长趋势（注明数据来源年份）
* 关键驱动因素和制约因素

### 2. 主要参与者
* 按细分领域列出TOP 3-5厂商
* 各厂商的核心竞争力和市场份额估计
* 新兴玩家及其创新点

### 3. 预测（1-3年）
* 基于[具体假设]的增长预测
* 技术演进路线图
* 潜在颠覆性因素

### 4. 机会与风险
* 最具潜力的3个市场机会
* 需要警惕的2-3个主要风险
* 监管环境变化的影响

### 5. 战略洞见
* 对{company}的3条具体战略建议
* 需要重点关注的竞争领域
* 推荐的投资方向

注意事项：
1. 保持专业、简洁的分析风格
2. 使用中文标点符号和术语
3. 每个观点必须有数据或逻辑支持
4. 明确标注哪些是估计，哪些是已知数据""",

            'financial': f"""为{company}（一家位于{hq_location}的{industry}公司）创建一份重点财务简报。
关键要求：
1. 使用以下标题和要点结构：

### 融资与投资
* 总融资金额及日期
* 列出每轮融资及日期
* 列出具名投资者

### 收入模式
* 讨论产品/服务定价（如适用）

2. 尽可能包含具体数字
3. 不要使用段落，只使用要点
4. 不要提及"未找到信息"或"无可用数据"
5. 切勿重复提及同一轮融资。始终假设同一月份的多轮融资是同一轮
6. 不要包含融资金额范围。根据提供的信息，用你的最佳判断确定确切金额
7. 仅提供简报内容，不要解释或评论
8. 所有内容必须使用中文输出""",

            'news': f"""为{company}（一家位于{hq_location}的{industry}公司）创建一份重点新闻简报。
关键要求：
1. 使用以下类别结构和要点：

### 重大公告
* 产品/服务发布
* 新举措

### 合作关系
* 集成
* 协作

### 荣誉认可
* 奖项
* 媒体报道

2. 按从新到旧排序
3. 每个要点一个事件
4. 不要提及"未找到信息"或"无可用数据"
5. 不要使用###标题，只使用要点
6. 仅提供简报内容，不要提供解释或评论
7. 所有内容必须使用中文输出""",
        }

        # Normalize docs to a list of (url, doc) tuples
        items = list(docs.items()) if isinstance(docs, dict) else [
            (doc.get('url', f'doc_{i}'), doc) for i, doc in enumerate(docs)
        ]
        # Sort documents by evaluation score (highest first)
        sorted_items = sorted(
            items,
            key=lambda x: float(x[1].get('evaluation', {}).get('overall_score', '0')),
            reverse=True
        )

        doc_texts = []
        total_length = 0
        for _, doc in sorted_items:
            title = doc.get('title', '')
            content = doc.get('raw_content') or doc.get('content', '')
            if len(content) > self.max_doc_length:
                content = content[:self.max_doc_length] + "... [content truncated]"
            doc_entry = f"Title: {title}\n\nContent: {content}"
            if total_length + len(doc_entry) < 120000:  # Keep under limit
                doc_texts.append(doc_entry)
                total_length += len(doc_entry)
            else:
                break

        separator = "\n" + "-" * 40 + "\n"
        prompt = f"""{prompts.get(category, f'请基于提供的文档，创建一份关于{industry}行业中{company}公司的重点研究简报。')}

请分析以下文档并提取关键信息。仅提供简报内容，不要解释或评论。请使用中文输出所有内容：

{separator}{separator.join(doc_texts)}{separator}

注意：
1. 所有内容必须使用中文输出
2. 保持专业、简洁的语言风格
3. 使用中文标点符号
4. 保持统一的中文术语翻译
"""

        try:
            logger.info("Sending prompt to LLM")
            response = self.gemini_model.generate_content(prompt)
            content = response.text.strip()
            if not content:
                logger.error(f"Empty response from LLM for {category} briefing")
                return {'content': ''}

            # Send completion status
            if websocket_manager := context.get('websocket_manager'):
                if job_id := context.get('job_id'):
                    await websocket_manager.send_status_update(
                        job_id=job_id,
                        status="briefing_complete",
                        message=f"Completed {category} briefing",
                        result={
                            "step": "Briefing",
                            "category": category
                        }
                    )

            return {'content': content}
        except Exception as e:
            logger.error(f"Error generating {category} briefing: {e}")
            return {'content': ''}

    async def create_briefings(self, state: ResearchState) -> ResearchState:
        """Create briefings for all categories in parallel."""
        company = state.get('company', 'Unknown Company')
        websocket_manager = state.get('websocket_manager')
        job_id = state.get('job_id')

        # Send initial briefing status
        if websocket_manager and job_id:
            await websocket_manager.send_status_update(
                job_id=job_id,
                status="processing",
                message="Starting research briefings",
                result={"step": "Briefing"}
            )

        context = {
            "company": company,
            "industry": state.get('industry', 'Unknown'),
            "hq_location": state.get('hq_location', 'Unknown'),
            "websocket_manager": websocket_manager,
            "job_id": job_id
        }
        logger.info(f"Creating section briefings for {company}")

        # Mapping of curated data fields to briefing categories
        categories = {
            'financial_data': ("financial", "financial_briefing"),
            'news_data': ("news", "news_briefing"),
            'industry_data': ("industry", "industry_briefing"),
            'company_data': ("company", "company_briefing")
        }

        briefings = {}

        # Create tasks for parallel processing
        briefing_tasks = []
        for data_field, (cat, briefing_key) in categories.items():
            curated_key = f'curated_{data_field}'
            curated_data = state.get(curated_key, {})

            if curated_data:
                logger.info(f"Processing {data_field} with {len(curated_data)} documents")

                # Create task for this category
                briefing_tasks.append({
                    'category': cat,
                    'briefing_key': briefing_key,
                    'data_field': data_field,
                    'curated_data': curated_data
                })
            else:
                logger.info(f"No data available for {data_field}")
                state[briefing_key] = ""

        # Process briefings in parallel with rate limiting
        if briefing_tasks:
            # Rate limiting semaphore for LLM API
            briefing_semaphore = asyncio.Semaphore(2)  # Limit to 2 concurrent briefings

            async def process_briefing(task: Dict[str, Any]) -> Dict[str, Any]:
                """Process a single briefing with rate limiting."""
                async with briefing_semaphore:
                    result = await self.generate_category_briefing(
                        task['curated_data'],
                        task['category'],
                        context
                    )

                    if result['content']:
                        briefings[task['category']] = result['content']
                        state[task['briefing_key']] = result['content']
                        logger.info(f"Completed {task['data_field']} briefing ({len(result['content'])} characters)")
                    else:
                        logger.error(f"Failed to generate briefing for {task['data_field']}")
                        state[task['briefing_key']] = ""

                    return {
                        'category': task['category'],
                        'success': bool(result['content']),
                        'length': len(result['content']) if result['content'] else 0
                    }

            # Process all briefings in parallel
            results = await asyncio.gather(*[
                process_briefing(task)
                for task in briefing_tasks
            ])

            # Log completion statistics
            successful_briefings = sum(1 for r in results if r['success'])
            total_length = sum(r['length'] for r in results)
            logger.info(
                f"Generated {successful_briefings}/{len(briefing_tasks)} briefings with total length {total_length}")

        state['briefings'] = briefings
        return state

    async def run(self, state: ResearchState) -> ResearchState:
        return await self.create_briefings(state)
