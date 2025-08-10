# TransFlow

```
conda create -n mcqg python==3.10
conda activate mcqg

pip install PyMuPDF
pip install python-dotenv
pip install tqdm
pip install pandas
pip install langchain
pip install langchain-core
pip install langchain-openai
pip install langchain_ollama
pip install langchain-community
pip install langgraph

```


# Use Example
## nbme translator
1. `python nbme2txt.py`
- convert nbme_item_writing_guide's APPENDIX B: Sample Lead-ins based on task competencies to splited txt files.
    - page from 70 - 84
    - data/parsed_txt/nbme/{page}.txt

