from datetime import datetime
from Chatbot.utils.database import conversation_collection
from Chatbot.Model.ChatLog import Chatlog
from Chatbot.Model.ChatSummarySession import ChatSummarizeSession

def saveChatConversation(sessionId: str, chatSession: Chatlog):
    message_dicts = [message.model_dump() for message in chatSession.message]

    conversation_collection.update_one(
        {"session_id": sessionId},
        {
            "$set": {"messages": message_dicts},  #
            "$setOnInsert": {"session_id": sessionId}
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
        {
            "$setOnInsert": {
                "session_id": sessionId,
                "messages": []
            },
            "$push": {"summaries": insertedSummary}
        },
        upsert=True
    )

def createSessionIdIndex():
    existing_indexes = conversation_collection.index_information()
    # Check if the index on the field already exists
    index_name = "session_id_1" #Index_name_sortoder naming convention for mongo 1:ascending 0: descending
    if index_name in existing_indexes:
        return
    else:
        conversation_collection.create_index([("session_id", 1)], unique=True)
