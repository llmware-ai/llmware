import streamlit as st


home_text = '''
# Lecture Tool

Welcome to Lecture Tool! This is an AI application that leverages `llmware` to \
transcribe and analyze college lecture videos.

---

### Features
1. Create `Libraries` to group transcripts and store them persistently.
2. Transcribe audio files using Whisper (built into the `llmware` library) and \
store them in a `Library`.
3. Ask general questions and questions about lecture content.
4. Summarize lecture content.
5. View all generated transcripts.

Each of these five features is implemented in its own file in the `pages` \
folder.

---

### Prerequisites
1. *Python libraries*: the only required libraries to be installed are \
`streamlit` and `llmware`. You can install them from the `requirements.txt` \
file.
2. *MongoDB*: it is used to store lecture transcripts. The easiest way to \
install it is to use the Docker Compose file in the \
[LLMWare repository](https://github.com/llmware-ai/llmware/blob/main/docker-compose_mongo_milvus.yaml).
3. *FFmpeg*: it is used to convert MP3 files to WAV files that are compatible \
with Whipser. If you intend to use MP3 files instead of WAV files, you can \
[download FFmpeg here](https://www.ffmpeg.org/download.html). You will likely \
need to restart your computer after installation.

---

### Usage
To run the program, ensure that you have `streamlit` installed. In your \
terminal, navigate to the `lecture_tool` directory and run `streamlit run \
Home.py`.

By default, Streamlit supports file uploads up to 200 MB. To increase \
this limit, run `streamlit run Home.py --server.maxUploadSize fileSize`, \
ensuring to replace `fileSize` with the maximum file size you want to upload \
in megabytes. For example, use 500 if you plan to upload audio files up to 500 \
MB in size.

Sample MP3 and WAV audio files to use the application with are available in \
the `sample_audio_files` directory.

The `saved_files` directory is used as a temporary location in the \
application's implementation and should not be modified by a user.
'''

#
# Launches the home page of the program.

# Run `streamlit run Home.py` to start the application.
#
if __name__ == '__main__':
    st.sidebar.write("Select a page above.")

    st.write(home_text)
