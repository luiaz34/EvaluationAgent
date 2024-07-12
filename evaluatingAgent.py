import os
from dotenv import load_dotenv
import fitz
from typing import Literal
from langchain_core.messages import HumanMessage
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.checkpoint import MemorySaver
from langgraph.graph import END, StateGraph, MessagesState
from langgraph.prebuilt import ToolNode

# Load environment variables
load_dotenv()

# Define tools to read job description, interview transcript, and extract text from PDF
@tool
def job_description() -> str:
    """Read and return the job description from a text file."""
    file_path = r"C:\Users\khain\Documents\EvaluatingAgent\JD.txt"
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        content = ""
    except IOError:
        print(f"An error occurred while reading the file at {file_path}.")
        content = ""
    return content

@tool
def interview_transcript() -> str:
    """Read and return the interview transcript from a text file."""
    file_path = r"C:\Users\khain\Documents\EvaluatingAgent\goodTranscript.txt"
    try:
        with open(file_path, 'r') as file:
            content = file.read()
    except FileNotFoundError:
        print(f"The file at {file_path} was not found.")
        content = ""
    except IOError:
        print(f"An error occurred while reading the file at {file_path}.")
        content = ""
    return content

@tool
def cv() -> str:
    """Extract and return text from a PDF CV."""
    pdf_path = r'C:\Users\khain\Documents\EvaluatingAgent\candidateCV.pdf'
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
    except FileNotFoundError:
        print(f"The file at {pdf_path} was not found.")
        text = ""
    except IOError:
        print(f"An error occurred while reading the file at {pdf_path}.")
        text = ""
    return text

tools = [job_description, interview_transcript, cv]

tool_node = ToolNode(tools)

# Initialize the ChatAnthropic client
model = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0).bind_tools(tools)

# Define the function that determines whether to continue or not
def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state['messages']
    last_message = messages[-1]
    # If the LLM makes a tool call, then we route to the "tools" node
    if last_message.tool_calls:
        return "tools"
    # Otherwise, we stop (reply to the user)
    return END

# Define the function that calls the model
def call_model(state: MessagesState) -> dict:
    messages = state['messages']
    response = model.invoke(messages)
    # We return a list, because this will get added to the existing list
    return {"messages": [response]}

# Define the prompt template
template = """
You are a hiring agent or recruiter tasked with evaluating candidates for a specific job position. You will be provided with a job description, an interview transcript, and a candidate's CV. Your task is to evaluate the CV against the job description and interview transcript, provide a rating for the candidate, and suggest alternative roles if necessary.

First, carefully review the following job description:
<job_description>
</job_description>

Next, review the interview transcript:
<interview_transcript>
</interview_transcript>

Now, examine the candidate's CV:
<cv>
</cv>

To evaluate the candidate:

1. Compare the candidate's qualifications, skills, and experience in the CV with the requirements outlined in the job description.
2. Consider how well the candidate's responses in the interview transcript align with the job requirements and company culture.
3. Identify any strengths or weaknesses that stand out in the CV or interview transcript.

Based on your evaluation, rate the candidate on a scale of 1 to 10, where 1 is the lowest and 10 is the highest. Consider the following factors:
- Relevance of skills and experience to the job description
- Educational background
- Work history
- Achievements and accomplishments
- Interview performance

Before providing the final rating, explain your reasoning in detail. Include specific examples from the CV and interview transcript that support your evaluation.

If the candidate's rating is 5 or below, identify alternative roles that might be more suitable based on their skills, experience, and interests. Consider positions within the same company or industry that could be a better fit.

Format your response as follows:

<evaluation>
[Provide a detailed explanation of your evaluation, including specific examples from the CV and interview transcript]
</evaluation>

<rating>
[Candidate's Name]
[Rating (1-10)]
</rating>

<alternative_roles>
[If the rating is 5 or below, list 2-3 alternative roles that might be more suitable for the candidate, along with a brief explanation for each suggestion]
</alternative_roles>

Remember to be objective and fair in your assessment, focusing on the candidate's qualifications and potential fit for the position or alternative roles.
"""

# Define a new graph
workflow = StateGraph(MessagesState)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

# Set the entry point as `agent`
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
    # Next, we pass in the function that will determine which node is called next.
    should_continue,
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("tools", 'agent')

# Initialize memory to persist state between graph runs
checkpointer = MemorySaver()

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable.
# Note that we're (optionally) passing the memory when compiling the graph
app = workflow.compile(checkpointer=checkpointer)

# Use the Runnable
final_state = app.invoke(
    {"messages": [HumanMessage(content=template)]},
    config={"configurable": {"thread_id": 42}}
)
print(final_state["messages"][-1].content)
