# Dialog summarization system for a RAG chatbot system

## Summary
## Environment setup
## Fine-tuning BART-based with SamSUM and TweeetSUM
<details>
<summary> Dataset</summary>
In this project, I will conduct on a 2 public dataset called SamSUM(2019) and TweetSUM(2021), in which the 1st will be used for pre-trained and the last one is used for fine-tune purpose.
I have already uploaded 2 datasets to this repos. If you are interested in the original dataset, please see the link below each type of dataset.
 
- **SamSUM dataset**:
 SamSUM is a dataset with the format of messenger-like conversations with summaries, with style and register are diversified.
![Header](./Image/DatasetPreparation/samsum_dataset.png)
Dataset link: [Dataset/SamSUM](./Dataset/SamSUM) . For the orignal one, please visit this site [SamSUM](https://paperswithcode.com/dataset/samsum-corpus)
- **TweetSUM dataset**:
TweetSUM is a dataset focused on summarization of dialogs, which represents the rich domain of Twitter customer care conversations
![Header](./Image/DatasetPreparation/TweetSUM_dataset.png)
Dataset link: [Dataset/TweetSUM](./Dataset/TweetSUM)  . For the orignal one, please visit this site [TweetSUM](https://github.com/guyfe/Tweetsumm)

Both the dataset will be pre-processed by this script before being fine-tuned by BART-based:
![Header](./Image/DatasetPreparation/preprocessing_dataset.png) 
</details>

<details>
<summary> Pre-training with BART-base</summary>
 BART-based will first be pre-trained with SamSUM dataset in order to have a better understaanding in general chat format, by the following configuration:
 
![Header](./Image/Pre-trained_BART/SamSUM_trainedconfiguration.png) 

After the trainning here are some results in terms of ROUGE score for the pre-trained BART-based:

![Header](./Image/Pre-trained_BART/SamSUM_pretrained_batched.png) 

Final ROUGE score:

![Header](./Image/Pre-trained_BART/SamSUM_ROUGEScore.png) 

Details can be witnessed on wandb records:
![Header](./Image/Pre-trained_BART/SamSUM_train.png) 
![Header](./Image/Pre-trained_BART/SamSUM_eval.png) 

</details>

<details>
<summary> Fine-tuning BART-SamSUM</summary>
 After pre-trainning with BART-based, it will be fine-tuned with TweetSUM for customer-service summary understanding :
 
![Header](./Image/Fine-tuned_BART/TweetSUM_trainconfiguration.png) 

After the trainning here are some results in terms of ROUGE score for the fine-tuned BART-based:

![Header](./Image/Fine-tuned_BART/TweetSUM_Finetuned.png) 

Final ROUGE score:

![Header](./Image/Fine-tuned_BART/TweetSUM_ROUGEScore.png) 

Details can be witnessed on wandb records:
![Header](./Image/Fine-tuned_BART/TweetSUM_trained.png) 
![Header](./Image/Fine-tuned_BART/TweetSUM_eval.png) 
</details>

For the fine-tuned checkpoint, I have already uploaded on huggingface, please visit this site to get the model: [BART_SamSUM_TweetSUM](https://huggingface.co/husthunterpy01/BART-SamTweetSUM/tree/main) 

## Chat bot execution
### Document for retrival
In this demo, I use the Iphonne User Guide as the document for this RAG chatbot, referring to [Customer-Service-Handbook-English.pdf](./Docs). I have already uploaded some other documents on the Docs Folder for testing, or you can also use other types of documents to test with this chatbot.
The document uploaded will be saved in the vector database, here is a screenshot of a document I have uploaded:

![Header](./Image/Chatbot/Database_saving/document_db_saving.png) 


### Method for increaseing searching performance
As the base RAG architecture does not work well for document retrival in some cases, I have implemented some methods to improve the retrival performance
<details>
<summary> Hybrid search</summary>
   Hybrid search will optimize the strength of both vector-search (contextual search) and key-word search, which is useful in some cases when you need to search for keyword or name of a person that can't be handled properly in terms of single vector search
 
![Header](./Image/Chatbot/hybridsearch.png) 
</details>

<details>
<summary>Semantic chunking</summary>
 Instead of fixed chunking at a fixed size, using semantic chunking helps user to seperate the chunk into meaningful chunks, which is conducive for later content retrival
 
![Header](./Image/Chatbot/semantic_chunking.png) 
</details>

### Chatbot implementation
This chatbot is built for the customer serivce purpose Q&A for a larger sytstem.
Before getting started, this chatbot is built based on the granite LLM by IBM, for more infomration please visit the site to download the model [Granite_LLM](https://huggingface.co/ibm-granite/granite-3.1-8b-instruct).
In here, I use the Granite version: **Granite-3.1-3b-a800m-instruct-Q6_K.gguf** as the LLM model due to the fact that my P.C only has CPU for execution, and you can find that the chat response in the demo video is a little bit slow due to this fact.
Here is some screenshot on this RAG chatbot system:
- Main screen:

![Header](./Image/Chatbot/chatbot_interface.png) 

- Chat dialog sample:

![Header](./Image/Chatbot/sample_chatdialog.png) 

This chatbot allows users to ask question based on document uploaded via the system and some possible knowledge acquired from the LLM model. In the chat, the dialog can be summarized with the use of the BART-SamTweetSUM and saved every time we summarize the data, as well as the whole chatlog session:

![Header](./Image/Chatbot/Database_saving/chatsession_db_saving.png) 

Reminded that the chat conversation will be saved as the context for the user prompt after each summary. For the 1st time without summary, the whole chat session will be loaded as context.

### Performance comparison with summary and without summary as context
My system also use the latest summary as the context for the user's prompt so as to minimize the time response of the bot to user by reducing the input tokens. To help you understand the impact of having summary as context, I have developed a function to compare the response of the chatbot in terms of using latest summary as context and not using it as context

Here is a sample question to compare:

![Header](./Image/Chatbot/chat_perf.png) 

Please enable the comparison so as for the system to calculate the execution time and the input/output token for the response. After the execution, here is the result for the above response:

![Header](./Image/Chatbot/chat_perf1.png) 
![Header](./Image/Chatbot/chat_perf2.png) 

As you can see by adding summary as context, the response can be much faster compared to non-summary as context
## Conclusion
- The demo shows how summary can work well with short dialog, but still needs improvement to cover more contents from the prev dialog
- Needs improvement in terms of speed
- Should also takes care of the case of hallucination
- Will later work on web/app development integrated to provide a more friendly chat interface and oriented to the purpose of the application.
