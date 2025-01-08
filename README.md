# Dialog summarization system for a RAG chatbot system

## Summary
## Environment setup
## Fine-tuning BART-based with SamSUM and TweeetSUM
<details>
<summary> Dataset</summary>
In this project, I will conduct on a 2 public dataset called SamSUM(2019) and TweetSUM(2021), in which the 1st will be used for pre-trained and the last one is used for fine-tune purpose.
I have already uploaded 2 datasets to this repos. If you are interested in the original dataset, please see the link below each type of dataset.
 
- SamSUM dataset:
 SamSUM is a dataset with the format of messenger-like conversations with summaries, with style and register are diversified.
![Header](./Image/DatasetPreparation/samsum_dataset.png)
Dataset link: [Dataset/SamSUM](./Dataset/SamSUM) . For the orignal one, please visit this site [SamSUM](https://paperswithcode.com/dataset/samsum-corpus)
- TweetSUM dataset:
TweetSUM is a dataset focused on summarization of dialogs, which represents the rich domain of Twitter customer care conversations
![Header](./Image/DatasetPreparation/TweetSUM_dataset.png)
Dataset link: [Dataset/TweetSUM](./Dataset/TweetSUM)  . For the orignal one, please visit this site [TweetSUM](https://github.com/guyfe/Tweetsumm)

Both the dataset will be pre-processed by this script before being fine-tuned by BART-based:
![Header](./Image/DatasetPreparation/preprocessing_dataset.png) 
</details>

<details>
<summary> Pre-training with BART-base</summary>
 BART-based will first be pre-trained with SamSUM dataset in order to have a better understaanding in general chat format, by the following configuration:
![Header](./Image/Pre-trained BART/SamSUM_trainedconfiguration.png) 

</details>

<details>
<summary> Fine-tuning BART-SamSUM</summary>
</details>


## Chat bot execution
### Document for retrival
### Method for increaseing searching performance
- Hybrid search
- Semantic chunking
### Chatbot implementation
### Performance comparison
## Conclusion
