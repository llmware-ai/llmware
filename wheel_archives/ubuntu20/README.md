

Ubuntu 20 Support 
===============

**Background**

In response to several community members who are still using Ubuntu 20, we will be preparing some 'back-level' builds of our C/C++ libraries, where possible.

**How to use?**

1.  If you clone the LLMWare repo, then 'copy-and-paste' the x86_64 folder into the llmware/lib/linux/ path, and it should be a 'drop-in' replacement for parsers to run on Ubuntu 20.

    --please note also that it has been tested on Ubuntu 22, and is a perfect substitute for the current binary (no degradation in functionality or performance seen so far in testing).
    
    --we have built libxml2 without ICU (much smaller binary) - if there are any Unicode issues, please let us know.

2.  Key dependency:   GLIBC 2.31 minimum requirement

3.  Issues:  our GGUF binary is still on GLIBC 2.32, so likely will not work on most Ubuntu 20 implementations.   We are working on a back-level build and will add here.

4.  To dos:  we will also look at Amazon Linux (which tends to run on older versions of GLIBC), as well as further testing on RHAT linux (9+ should be OK, as it uses GLIBC 2.34).


**Release Notes**  

--first release:  March 6, 2024 - added to this repository - expect to test further, and likely merge into main repo and potentially pypi release in the next week.

-
