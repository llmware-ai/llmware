
""" This example shows a multimedia bot created in less than 100 lines of code that
leverages the CPU, GPU and NPU

    -- designed to run on an AI PC with Intel Lunar Lake with CPU, GPU and NPU
    -- if you do not have GPU, it will auto-fallback to CPU
    -- if you do not have NPU, you can change the option to GPU

    To run this example, we will need the following dependencies in addition to llmware:

    -- pip3 install openvino_genai
    -- pip3 install pywebio

"""

from llmware.models import ModelCatalog
from llmware.configs import LLMWareConfig

import os
import threading

from pywebio.input import input_group, textarea, actions
from pywebio.output import put_text, put_markdown, put_image, use_scope, put_info
from pywebio.session import set_env


def text_gen_bot(**kwargs):

    """ Simple text generation streaming bot - will run using GGUF on CPU """

    user_msg = kwargs.get("user_msg", "")
    img_counter = kwargs.get("img_counter", 0)

    # llmware load_model
    text_gen_model = ModelCatalog().load_model("phi-3-gguf",
                                               max_output=200)

    inst = "Complete this story: "
    prompt = inst + user_msg
    text_output = ""

    with use_scope(f"text_gen" + str(img_counter)):

        # llmware stream generation
        for token in text_gen_model.stream(prompt):
            put_text(token, inline=True)
            text_output += token

        put_text("\nTo be continued ...")

    # for demo example, we will write the text from the thread to a tmp file
    fp = os.path.join(LLMWareConfig().get_llmware_path(), "txt_tmp.txt")
    if os.path.exists(fp):
        os.remove(fp)
    f = open(fp, "w")
    f.write(text_output)
    f.close()

    return text_output


def image_gen_bot(**kwargs):

    """ Image generation bot that will run on GPU. """

    user_msg = kwargs.get("user_msg", "")
    img_counter = kwargs.get("img_counter", 0)

    # llmware load_model
    model = ModelCatalog().load_model("lcm-dreamshaper-ov")

    inst = "Draw an image: "
    prompt = inst + user_msg

    # specialized pipeline on the model
    img_path = model.text_to_image_gen(prompt, f"test_image_{img_counter}")
    content = open(img_path, "rb").read()

    # display the image on the screen with pywebio
    with use_scope(f"img_gen" + str(img_counter)):
        put_image(content)

    return img_path


def classifier_agent_bot(**kwargs):

    """ Simple classification agent running on NPU """

    text_output = kwargs.get("text_output", "")
    npu_model = kwargs.get("npu_model", None)

    # pass the model to the thread - and execute a function call
    response = npu_model.function_call(text_output)

    put_text("\n\nNPU Classification Agent: " + str(response["llm_response"]))

    return True


def run_bot():

    """ Main function - starts a user prompt loop, and then kicks off
    three threads in parallel on CPU, GPU and NPU. """

    set_env(input_panel_fixed=False, output_animation=False)
    put_markdown("""# Multimedia Bot with LLMWare, OpenVINO, & PyWebio""")

    img_counter = 0
    start_bot = True

    while start_bot:

        # user input chat box

        form = input_group('', [
            textarea(name='msg', placeholder='Ask LLMWare Bot', rows=3),
            actions(name='cmd', buttons=['Send', 'Exit'])
        ])

        if form['cmd'] == "Exit":
            start_bot = False
            break

        user_msg = form['msg']

        # display the user prompt
        put_info(user_msg)

        # thread 1 - CPU - text gen
        text_gen_thread = threading.Thread(target=text_gen_bot,
                                           kwargs={"user_msg": user_msg,
                                                   "img_counter": img_counter})
        text_gen_thread.start()

        # thread 2 - GPU - text to image gen
        image_gen_thread = threading.Thread(target=image_gen_bot,
                                            kwargs={"user_msg": user_msg,
                                                    "img_counter": img_counter})
        image_gen_thread.start()

        # load the npu model in main and pass to thread
        npu_model = ModelCatalog().load_model("slim-topics-npu-ov",
                                              sample=False,temperature=0.0,
                                              device="NPU")

        image_gen_thread.join()
        text_gen_thread.join()

        # pull the text output file created in the text gen thread
        fp = os.path.join(LLMWareConfig().get_llmware_path(), "txt_tmp.txt")
        text_output = ""
        if os.path.exists(fp):
            text_output = open(fp, "r").read()

        # kick off NPU thread
        npu_gen_thread = threading.Thread(target=classifier_agent_bot,
                                          kwargs={"text_output": text_output,
                                                  "npu_model": npu_model})

        npu_gen_thread.start()

        img_counter += 1

    return True


if __name__ == "__main__":
    run_bot()
