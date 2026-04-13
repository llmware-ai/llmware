 🚀 Getting Set up - Key Items  🚀  
===============

**How to get started with LLMWare?**    

In this repository, we have small code snippets with a lot of annotation that describe key setup items to get started quickly and successfully with LLMWare:

1.  [**Configuring a DB**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Getting_Started/configure_db.py) - for a fast start, you don't have to do anything except set the .active_db parameter to "sqlite" and all libraries will be written on a local embedded sqlite instance with no installation required.  


    from llmware.configs import LLMWareConfig
    LLMWareConfig().set_active_db("sqlite")
    

   After writing content into your first library, you will find the sqlite db at the path defined here:  
    
    from llmware.configs import SQLiteConfig
    SQLiteConfig().get_config("sqlite_db_folder_path")


2.  [**Loading Sample Files**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Getting_Started/loading_sample_files.py) - for an overview of the sample files available and how to pull down (integrated into many examples too.)  


    from llmware.setup import Setup
    Setup().load_sample_files()


3.  [**Using the Model Catalog**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Getting_Started/using_the_model_catalog.py) - this is the primary model discovery and loading class for LLMWare.  


    from llmware.models import ModelCatalog
    all_models = ModelCatalog().list_all_models()
    for model in all_models: print("model: ", model)


4.  [**Working with Libraries**](https://www.github.com/llmware-ai/llmware/tree/main/examples/Getting_Started/working_with_libraries.py) - Libraries are the main organizing construct for text collections in LLMWare.  


As you are getting started, we would also recommend that you check out the [**Fast Start**](https://www.github.com/llmware-ai/llmware/tree/main/fast_start) examples and videos as well!  



### **Let's get started!  🚀**


