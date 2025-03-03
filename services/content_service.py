from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from services import llm
from models.user import User
from models.content import Article
from schemas.rag_schema import ArticleOutput


class ContentService:

    @staticmethod
    async def generate_article(user: User):
        with open(f'utils/prompts/prompt_generate_article.txt', 'r') as file:
            system_prompt = file.read()

        system_prompt = system_prompt.replace("{preferred_language}", user.language.get_prompt_language())
        system_prompt = system_prompt.replace("{username}", user.username)

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
        ])
        structured_model = llm.with_structured_output(ArticleOutput)

        chat_history = await user.get_recent_messages()
        formatted_history = [{"role": msg.role, "content": msg.content} for msg in chat_history]
        
        articles = await Article.get_articles_by_user(user.id)
        formatted_articles = [article.model_dump_json() for article in articles]

        messages = prompt.format(
            chat_history=formatted_history,
            previous_articles=formatted_articles
        )

        article_output: ArticleOutput = structured_model.invoke(messages)
        if article_output:
            article = Article(
                user_id=user.id,
                title=article_output.title,
                tags=article_output.tags,
                summary=article_output.summary,
                content=article_output.content,
                estimated_reading_time=article_output.estimated_reading_time
            )
            await article.insert()
            return article
        return None
