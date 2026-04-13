
""" Starting with llmware 0.2.8, new configuration options are exposed in the Office parser, with many more to come.
    This should not result in any breaking changes in existing code, but only exposes new configuration options.

    Note: the configuration options for the Office parser apply to parsing of the following document types:

        --  Word Documents   --  .docx
        --  Powerpoints      --  .pptx
        --  Excel            --  .xlsx

    Wherever possible, the configuration options match the PDF parsing configuration options. """

from llmware.library import Library

fp = "/path/to/my/office/files"

lib = Library().create_new_library("my_library")

# standard call to 'ingest' files into a library (implicitly calls Parser and manages the details)
lib.add_files(input_folder_path=fp)

#   new configuration options in Parser class, exposed in .add_files method for convenience, although it can
#   always be accessed by direct construction of a Parser

#   CHUNK SIZING - implemented in both PDF and Office parser
#   Measured in string len characters, e.g., 400 characters as target text chunk size, with max of 600 characters

#   --  there are 4 text chunking strategies supported in the Office parser:
#   --   smart_chunking   =   0  -> will stop at the target chunk size (or as close as possible) - breaks words
#   --   smart_chunking   =   1  -> will stop at the first white space after the target chunk size - preserves words
#   --   smart_chunking   =   2  -> will look for a natural break, either a "." or "\r" or "\n", up to the max size
#   --   smart_chunking   =   3  -> will follow the structures as set out in the Office XML document

#   --  note:  this applies to all text content types, but does not apply to tables, which will be parsed and captured
#       separately as "table" content types - and generally table will be kept in a single logical chunk, which may
#       exceed the limits of the text chunking.

#   -- note: it is possible that the char lengths will vary by 1-3 bytes, as there are safeguards to prevent breaking a
#       multi-byte utf-8 character.  If there are any breaking changes, they will generally be remediated before
#       entering the text in the database automatically.

lib.add_files(input_folder_path=fp, chunk_size=400, max_chunk_size=600, smart_chunking=1)

#   CAPTURE PARAMETERS

#   --  ability to turn on/off the capture of other features in the parser, e.g, whether to capture images, tables,
#       and formatted header text (e.g., BOLD, ITALICS and Large Font)

#   --  if you are only interested in text, then you can turn off these features for faster performance

lib.add_files(input_folder_path=fp, get_images=False, get_tables=False, get_header_text=False)

#   ENCODING

#   --  encoding = "utf-8" - new default - supports Western European characters, and many characters across the
#       wider Unicode set of code points - note: not full support yet for Asian languages and characters

#   --  right now, the Office parser only supports UTF-8 encoding
#   --  will explore options to add ASCII 7-bit range in the future
#   --  if there is a problem parsing the text's UTF-8 character set, then the problematic text is converted to ASCII.

lib.add_files(input_folder_path=fp, encoding="utf-8")

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




