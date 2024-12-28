from datetime import datetime
from Chatbot.utils.database import conversation_collection
from Chatbot.Model.ChatLog import Chatlog
from Chatbot.Model.ChatSummarySession import ChatSummarizeSession

def saveChatConversation(sessionId: str, chatSession: Chatlog):
    message_dicts = [message.model_dump() for message in chatSession.message]

    conversation_collection.update_one(
        {"session_id": sessionId},
        {
            "$setOnInsert": {"session_id": sessionId},
            "$push": {"messages": {"$each": message_dicts}}
        },
        upsert=True
    )


def saveSummaryBySession(sessionId: str, summaryBySession: ChatSummarizeSession):
    insertedSummary = {
        "timestamp": datetime.now().isoformat(),
        "summary": summaryBySession.summary
    }

    conversation_collection.update_one(
        {"session_id": sessionId},
        {"$push": {"summaries": insertedSummary}}
    )