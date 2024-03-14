

Wheel Archives: `llmware` pip install from pypy 
===============

**How to use?**

1.  Download a selected wheel, unzip, and then deploy the code directly into a project.
2.  Place the wheel archive in a folder, and in that folder path, run:

```pip3 install llmware-0.1.15-py3-none-any.whl```  

New wheels are built generally on PyPy on a weekly basis and updated on PyPy versioning.   The development repo is updated  
and current at all times, but may have updates that are not yet in the PyPy wheel.

All wheels are built and tested on:

1.  Mac Metal
2.  Mac x86
3.  Windows x86 (+ with CUDA)
4.  Linux x86 (+ with CUDA) - most testing on Ubuntu 22 and Ubuntu 20 - which are recommended.
5.  Linux aarch64

**Release Notes**  

--**0.2.5** released in the week of March 12, 2024 - continued enhancements of the GGUF implementation, especially for CUDA support, and re-compiling of all binaries to support Ubuntu 20 and Ubuntu 22.  Ubuntu requirements are:  CUDA 12.1 (to use GPU), and GLIBC 2.31+.  

--**GGUF on Windows CUDA**: useful notes and debugging tips -  

    1.  Requirement:  Nvidia CUDA 12.1+  
    
        -- how to check:  `nvcc --version` and `nvidia-smi` - if not found, then drivers are either not installed or not in $PATH and need to be configured 
        -- if you have older drivers (e.g., v11), then you will need to update them.  
        
    2.  Requirement:  CUDA-enabled Pytorch  
    
        -- while GGUF does not use Pytorch, in llmware, we use Pytorch as a proxy to determine if Python is able to find the CUDA drivers (if anyone knows a better 
        way, please let us know!)  
        
        -- how to check:  `torch.cuda.is_available()` and `torch.version.cuda`  

    3.  Installing a CUDA-enabled Pytorch - useful install script:  
    
        -- `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121`  

    4.  Fall-back to CPU - if llmware can not load the CUDA-enabled drivers, it will automatically try to fall back to the CPU version of the drivers.  
    
        -- you can also adjust the GGUFConfigs().set_config - ("use_gpu", False) - and then it will automatically go to the CPU drivers.  

    5.  Custom GGUF libraries - if you have a unique system requirement, you can build llama_cpp from source, and apply custom build settings - or find in the community a prebuilt llama_cpp library that matches your platform.  Happy to help if you share the requirements.  

        -- to "bring your own GGUF":  GGUFConfigs().set_config("custom_lib_path", "/path/to/your/custom/llama_cpp_backend" -> and llmware will try to load that library.  

    6.  Issues?  - please raise an Issue on Github, or on Discord - and we can work with you to get you up and running!  
    
--**0.2.4** released in the week of February 26, 2024 - major upgrade of GGUF implementation to support more options, including CUDA support - which is the main source of growth in the size of the wheel package.   

  -- Note: We will look at making some of the CUDA builds as 'optional' or 'bring your own' over time.    
  -- Note: We will also start to 'prune' the list of wheels kept in the archive to keep the total repo size manageable for cloning.  

--**0.2.2** introduced SLIM models and the new LLMfx class, and the capabilities for multi-model, multi-step Agent-based processes.  

--**0.2.0** released in the week of January 22, 2024 - significant enhancements, including integration of Postgres and SQLite drivers into the c lib parsers.  

--New examples involving Postgres or SQLite support (including 'Fast Start' examples) will require a fresh pip install of 0.2.0 or clone of the repo.  

--If cloning the repo, please be especially careful to pick up the new updated /lib dependencies for your platform.  

--New libs have new dependencies in Linux in particular - most extensive testing on Ubuntu 22. If any issues on a specific version of Linux, please raise a ticket.  


