---
layout: default
title: Troubleshooting
parent: Community
nav_order: 2
description: overview of the major modules and classes of LLMWare  
permalink: /community/troubleshooting
---
# Common Troubleshooting Issues
___


1. **Can not install the pip package**  

    -- Check your Python version.   If using Python 3.9-3.11, then almost any version of llmware should work.  If using an older Python (before 3.9), then it is likely that dependencies will fail in the pip process.  If you are using Python 3.12, then you need to use llmware>=0.2.12.  
    
    -- Dependency constraint error.   If you receive a specific error around a dependency version constraint, then please raise an issue and include details about your OS, Python version, any unique elements in your virtual environment, and specific error.   


2. **Parser module not found**

    -- Check your OS and confirm that you are using a [supported platform](platforms.md/#platform-support).  
    -- If you cloned the repository, please confirm that the /lib folder has been copied into your local path.  


3. **Pytorch Model not loading**

   -- Confirm the obvious stuff - correct model name, model exists in Huggingface repository, connected to the Internet with open ports for HTTPS connection, etc.  

   -- Check Pytorch version - update Pytorch to >2.0, which is required for many recent models released in the last 6 months, and in some cases, may require other dependencies not included in the llmware package.  
        --note: we have seen some compatibility issues with Pytorch==2.3 on Wintel platforms - if you run into these issues, we recommend using a back-level Pytorch==2.1, which we have seen fixing the issue.  

4. **GGUF Model not loading**

   -- Confirm that you are using llmware>=0.2.11 for the latest GGUF support.  

   -- Confirm that you are using a [supported platform](platforms.md/#platform-support).  We provide pre-built binaries for llama.cpp as a back-end GGUF engine on the following platforms:  
        
        - Mac M1/M2/M3 - OS version 14 - "with accelerate framework"
        - Mac M1/M2/M3 - OS older versions - "without accelerate framework"  
        - Windows - x86
        - Windows with CUDA  
        - Linux - x86  (Ubuntu 20+)
        - Linux with CUDA  (Ubuntu 20+)  
   
If you are using a different OS platform, you have the option to "bring your own llama.cpp" lib as follows:  

```python
from llmware.gguf_configs import GGUFConfigs
GGUFConfigs().set_config("custom_lib_path", "/path/to/your/libllama_binary")  
```

If you have any trouble, feel free to raise an Issue and we can provide you with instructions and/or help compiling llama.cpp for your platform.  
        
   -- Specific GGUF model - if you are successfully using other GGUF models, and only having problems with a specific model, then please raise an Issue, and share the specific model and architecture.  


5. **Example not working as expected** - please raise an issue, so we can evaluate and fix any bugs in the example code.  Also, pull requests are always especially welcomed with a fix or improvement in an example.  


6. **Model not leveraging CUDA available in environment.**  

    -- **Check CUDA drivers installed correctly** - easy check of the NVIDIA CUDA drivers is to use `nvidia-smi` and `nvcc --version` from the command line.  Both commands should respond positively with details on the versions and implementations.  Any errors indicates that either the driver or CUDA toolkit are not installed or recognized.  It can be complicated at times to debug the environment, usually with some trial and error.   See extensive [Nvidia Developer documentation](https://docs.nvidia.com) for trouble-shooting steps, specific to your environment.  

    -- **Check CUDA drivers are up to date** - we build to CUDA 12.1, which translates to a minimum of 525.60 on Linux, and 528.33 on Windows.  

    -- **Pytorch model** - check that Pytorch is finding CUDA, e.g., `torch.cuda.is_available()` == True.   We have seen issues on Windows, in particular, to confirm that your Pytorch version has been compiled with CUDA drivers.  For Windows, in particular, we have found that you may need to compile a CUDA-specific version of Pytorch, using the following command:  
    
    ```pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121```
    
    -- **GGUF model** - logs will be displayed on the screen confirming that CUDA is being used, or whether 'fall-back' to CPU drivers.  We run a custom CUDA install check, which you can run on your system with:  
        ```gpu_status = ModelCatalog().gpu_available``` 
        
       If you are confirming CUDA present, but fall-back to CPU is being used, you can set the GGUFConfigs to force to CUDA:  
        ```GGUFConfigs().set_config("force_gpu", True)```  
      
       If you are looking to use specific optimizations, you can bring your own llama.cpp lib as follows:
        ```GGUFConfigs().set_config("custom_lib_path", "/path/to/your/custom/llama_cpp_backend")``` 

    -- If you can not debug after these steps, then please raise an Issue.   We are happy to dig in and work with you to run FAST local inference.  


7.  **Model result inconsistent**  

    -- when loading the model, set `temperature=0.0` and `sample=False` -> this will give a deterministic output for better testing and debugging.  

    -- usually the issue will be related to the retrieval step and formation of the Prompt, and as always, good pipelines and a little experimentation usually help !  


8. **Newly added examples not working as intended**

    -- If you run a recently added example and it does not run as intended, it is possible that the feature being used in the example has not yet been added to the latest pip install.

    -- To fix this, move the example file to the outer-most directory of the repository, so that the example file you are trying to run is in the same directory as the `llmware` source code directory.

    -- This will let you run the example using the latest source code!


9. **Git permission denied error**

    -- If you are using SSH to clone the repository and you get an error that looks similar to `git@github.com: Permission denied (publickey)`, then you might not have configured your SSH key correctly.

    -- If you don't already have one, you will need to create a new SSH key on your local machine. For instructions on how to do this, check out this page: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent.

    -- You then need to add the SSH key to your GitHub account. For instructions on how to do this, check out this page: https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account.


# More information about the project - [see main repository](https://www.github.com/llmware-ai/llmware.git)


# About the project

`llmware` is &copy; 2023-{{ "now" | date: "%Y" }} by [AI Bloks](https://www.aibloks.com/home).

## Contributing
Please first discuss any change you want to make publicly, for example on GitHub via raising an [issue](https://github.com/llmware-ai/llmware/issues) or starting a [new discussion](https://github.com/llmware-ai/llmware/discussions).
You can also write an email or start a discussion on our Discord channel.
Read more about becoming a contributor in the [GitHub repo](https://github.com/llmware-ai/llmware/blob/main/CONTRIBUTING.md).

## Code of conduct
We welcome everyone into the ``llmware`` community.
[View our Code of Conduct](https://github.com/llmware-ai/llmware/blob/main/CODE_OF_CONDUCT.md) in our GitHub repository.

## ``llmware`` and [AI Bloks](https://www.aibloks.com/home)
``llmware`` is an open source project from [AI Bloks](https://www.aibloks.com/home) - the company behind ``llmware``.
The company offers a Software as a Service (SaaS) Retrieval Augmented Generation (RAG) service.
[AI Bloks](https://www.aibloks.com/home) was founded by [Namee Oberst](https://www.linkedin.com/in/nameeoberst/) and [Darren Oberst](https://www.linkedin.com/in/darren-oberst-34a4b54/) in October 2022.

## License

`llmware` is distributed by an [Apache-2.0 license](https://www.github.com/llmware-ai/llmware/blob/main/LICENSE).

## Thank you to the contributors of ``llmware``!
<ul class="list-style-none">
{% for contributor in site.github.contributors %}
  <li class="d-inline-block mr-1">
     <a href="{{ contributor.html_url }}">
        <img src="{{ contributor.avatar_url }}" width="32" height="32" alt="{{ contributor.login }}">
    </a>
  </li>
{% endfor %}
</ul>


---
<ul class="list-style-none">
    <li class="d-inline-block mr-1">
        <a href="https://discord.gg/MhZn5Nc39h"><span><i class="fa-brands fa-discord"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.youtube.com/@llmware"><span><i class="fa-brands fa-youtube"></i></span></a>
    </li>
  <li class="d-inline-block mr-1">
    <a href="https://huggingface.co/llmware"><span> <img src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg" alt="Hugging Face" class="hugging-face-logo"/> </span></a>
     </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.linkedin.com/company/aibloks/"><span><i class="fa-brands fa-linkedin"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://twitter.com/AiBloks"><span><i class="fa-brands fa-square-x-twitter"></i></span></a>
    </li>
    <li class="d-inline-block mr-1">
        <a href="https://www.instagram.com/aibloks/"><span><i class="fa-brands fa-instagram"></i></span></a>
    </li>
</ul>
---
