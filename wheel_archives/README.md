

Wheel Archives: `llmware` pip install from pypy 
===============

**How to use?**

1.  Download a selected wheel, unzip, and then deploy the code directly into a project.
2.  Place the wheel archive in a folder, and in that folder path, run:

```pip3 install llmware-0.1.15-py3-none-any.whl```  

New wheels are built generally on PyPy on a weekly basis and updated on PyPy versioning.   The development repo is updated  
and current at all times, but may have updates that are not yet in the PyPy wheel.

All wheels are built and tested on five platforms:

1.  Mac Metal
2.  Mac x86
3.  Windows x86
4.  Linux x86
5.  Linx aarch64

**Release Notes**  

--**0.2.4** released in the week of February 26, 2024 - major upgrade of GGUF implementation to support more options, including CUDA support - which is the main source of growth in the size of the wheel package.   

  -- Note: We will look at making some of the CUDA builds as 'optional' or 'bring your own' over time.    
  -- Note: We will also start to 'prune' the list of wheels kept in the archive to keep the total repo size manageable for cloning.  

--**0.2.2** introduced SLIM models and the new LLMfx class, and the capabilities for multi-model, multi-step Agent-based processes.  

--**0.2.0** released in the week of January 22, 2024 - significant enhancements, including integration of Postgres and SQLite drivers into the c lib parsers.  

--New examples involving Postgres or SQLite support (including 'Fast Start' examples) will require a fresh pip install of 0.2.0 or clone of the repo.  

--If cloning the repo, please be especially careful to pick up the new updated /lib dependencies for your platform.  

--New libs have new dependencies in Linux in particular - most extensive testing on Ubuntu 22. If any issues on a specific version of Linux, please raise a ticket.  


