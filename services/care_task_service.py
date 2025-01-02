from langchain_core.prompts import ChatPromptTemplate

from schemas.care_task_schema import CareTaskList, Caregiver
from services import llm


class CareTaskService():

    def __init__(self):
        with open(f'utils/prompts/prompt_task_generator.txt', 'r') as file:
            system = file.read()

        prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{input}")])
        structured_model = llm.with_structured_output(CareTaskList)
        self.model = prompt | structured_model

    def generate(self, request: Caregiver) -> CareTaskList:
        careplan = self.model.invoke(request.model_dump_json())
        return careplan
