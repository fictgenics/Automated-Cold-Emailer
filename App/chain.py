import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class Chain:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(temperature=0, google_api_key=os.getenv("GOOGLE_API_KEY"), model="gemini-2.5-flash")
    def extract_jobs(self, cleaned_text):
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills` and `description`.
            Only return the valid JSON.
            ### VALID JSON (NO PREAMBLE):
            """
        )
        chain_extract = prompt_extract | self.llm
        res = chain_extract.invoke(input={"page_data": cleaned_text})
        try:
            json_parser = JsonOutputParser()
            res = json_parser.parse(res.content)
        except OutputParserException:
            raise OutputParserException("Context too big. Unable to parse jobs.")
        return res if isinstance(res, list) else [res]

    def write_mail(self, job, links,tone):
        prompt_email = PromptTemplate.from_template(
            """

            ### ROLE
            
            Aight, bet. You're Fictgenics. You're a low-key fire consultancy that builds automations so businesses can chill and get things done.

            ### The Mission
            Your job is to slide into a client's DMs with a cold email. The goal is to show them how Fictgenics can handle the gig they're posting. Here's the deal:

            **JOB DESCRIPTION:**
            {job_description}

            ### INSTRUCTIONS
            - Write this email in a {tone} tone.
            - Flex on 'em and show off how Fictgenics can get the job done.
            - Drop the most relevant links from this list to prove you're not capping: {link_list}
            - Keep it 💯. Don't add any extra text or intros. Just the email.

            ### EMAIL(NO PREAMBLE):
            
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": links, "tone":tone})
        return res.content

if __name__ == "__main__":
    print(os.getenv("GOOGLE_API_KEY"))