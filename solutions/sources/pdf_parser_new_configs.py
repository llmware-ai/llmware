
""" Starting with llmware 0.2.7, new configuration options are exposed in the PDF parser, with many more to come.
    This should not result in any breaking changes in existing code, but exposes new configuration options.

    Note: default encoding is now 'utf-8' which could result in changes from previous default 'ascii' -> if you
    experience any issues, you can explicitly set the encoding = 'ascii' ... """

from llmware.library import Library

fp = "/path/to/my/pdf/files"

lib = Library().create_new_library("my_library")

# standard call to 'ingest' files into a library (implicitly calls Parser and manages the details)
lib.add_files(input_folder_path=fp)

#   new configuration options in Parser class, exposed in .add_files method for convenience, although it can
#   always be accessed by direct construction of a Parser

#   CHUNK SIZING - implemented in PDF parser (and will be supported fully in Office parser coming soon)
#   Measured in string len characters, e.g., 400 characters as target text chunk size, with max of 600 characters

#   --  there are 3 chunking strategies supported:
#   --   smart_chunking   =   0  -> will stop at the target chunk size (or as close as possible) - breaks words
#   --   smart_chunking   =   1  -> will stop at the first white space after the target chunk size - preserves words
#   --   smart_chunking  =    2  -> will look for a natural break, either a "." or "\r" or "\n", up to the max size
#   --  note: this is applied on a page-by-page basis, so if there are 1800 characters on a page, then in this example,
#       it would result in 4 text chunks of ~400 characters, and a final chunk of the remainder of ~200 characters

lib.add_files(input_folder_path=fp, chunk_size=400, max_chunk_size=600, smart_chunking=0)

#   CAPTURE PARAMETERS

#   --  ability to turn on/off the capture of other features in the parser, e.g, whether to capture images, tables,
#       and formatted header text (e.g., BOLD, ITALICS and Large Font)

#   --  if you are only interested in text, then you can turn off these features for faster performance

lib.add_files(input_folder_path=fp, get_images=False, get_tables=False, get_header_text=False)

#   ENCODING

#   --  encoding = "utf-8" - new default - supports Western European characters, and many characters across the
#       wider Unicode set of code points - note: not full support yet for Asian languages and characters

#   --  backup option = "ascii" - if english only document, then this will often times result in a slightly cleaner
#       output as it will restrict the output to ASCII 7-bit range (1-127)

#   --  backup option (not recommended, but available) = "latin-1" encoding - will attempt to save the 8-bit
#       character directly into the database with UTF-8 bit mapping - which can create downstream validation problems
#       but available if needed in a special case

lib.add_files(input_folder_path=fp, encoding="utf-8")

#   STRIP HEADERS

#   --  some documents prepared by a 3rd party service will insert a repeating header at the top of each page
#   --  if strip_header == True, then the parser will skip the first text box found on each page in an attempt to
#       to remove repeating common header (very useful in some cases- and worth trying)

lib.add_files(input_folder_path=fp, strip_header=True)

#   COPY FILES TO LIBRARY

#   --  by default, input files are collated to different parsers, and then at the end of the process, copied to a
#       library file structure for convenient future access by the library and for downstream retrieval applications
#       that query the library, and then want to provide direct access to the files.

#   --  if you do not want to duplicate files, then set copy_files_to_library = False

lib.add_files(input_folder_path=fp, copy_files_to_library=False)

#   VERBOSE OUTPUT

#   --  four modes of output to screen
#   --  verbose_level   == 0    -> suppresses virtually all output, except major errors/problems
#   --  verbose_level   == 1    -> displays 1st ten pages of document text in text chunks as parsing
#   --  verbose_level   == 2    -> displays file name being parsed only
#   --  verbose_level   == 3    -> deep debugging mode (not recommended) - useful for llmware dev team in tracing errors

lib.add_files(input_folder_path=fp, verbose_level=2)




