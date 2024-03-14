
"""GGUF Configs module implements a wide range of configuration and formal interface elements to enable GGUF and the
use of llama.cpp as a back-end inference engine.   This module consists of the following major elements:

    1.  Formal ctype interfaces to access C++/C methods and objects in Python
        -- includes exposing ~100 python interfaces in 'add_ctypes_declarations' method
        -- over time, will add more linkages into GGUFGenerativeModel class
    2.  Formal python wrapper objects on major llama.cpp classes - _Model, _Context, _Batch, _TokenDataArray
    3.  Minimal callback function to control verbosity from back-end llama.cpp
    4.  GGUFConfigs - most commonly used configuration items

    Most of the items in 1-3 are 'formal' code that should generally not need to be changed.

    Where possible, we have opted to use similar class and object names to conform with norms from llama_cpp
    and llama_cpp_python and provide intuitive mapping for users of those libraries. """


import ctypes
import os
import sys
import numpy as np
from dataclasses import field
import multiprocessing

from llmware.exceptions import FilePathDoesNotExistException, ModelNotFoundException, ConfigKeyException

#   Ctypes Struct wrappers that map to llama.cpp C++/C objects
llama_model_p_ctypes = ctypes.c_void_p
llama_context_p_ctypes = ctypes.c_void_p
llama_pos = ctypes.c_int32
llama_token = ctypes.c_int32
llama_token_p = ctypes.POINTER(llama_token)
llama_seq_id = ctypes.c_int32
ggml_backend_sched_eval_callback = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_bool, ctypes.c_void_p)
llama_log_callback = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p)
llama_grammar_p = ctypes.c_void_p
llama_progress_callback = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_float, ctypes.c_void_p)


class llama_token_data(ctypes.Structure):

    _fields_ = [
        ("id", llama_token),
        ("logit", ctypes.c_float),
        ("p", ctypes.c_float),
    ]

llama_token_data_p = ctypes.POINTER(llama_token_data)

class llama_token_data_array(ctypes.Structure):

    _fields_ = [
        ("data", llama_token_data_p),
        ("size", ctypes.c_size_t),
        ("sorted", ctypes.c_bool),
    ]

llama_token_data_array_p = ctypes.POINTER(llama_token_data_array)

class llama_batch(ctypes.Structure):

    _fields_ = [
        ("n_tokens", ctypes.c_int32),
        ("token", ctypes.POINTER(llama_token)),
        ("embd", ctypes.POINTER(ctypes.c_float)),
        ("pos", ctypes.POINTER(llama_pos)),
        ("n_seq_id", ctypes.POINTER(ctypes.c_int32)),
        ("seq_id", ctypes.POINTER(ctypes.POINTER(llama_seq_id))),
        ("logits", ctypes.POINTER(ctypes.c_int8)),
        ("all_pos_0", llama_pos),
        ("all_pos_1", llama_pos),
        ("all_seq_id", llama_seq_id),
    ]

class llama_model_kv_override_value(ctypes.Union):
    _fields_ = [
        ("int_value", ctypes.c_int64),
        ("float_value", ctypes.c_double),
        ("bool_value", ctypes.c_bool),
    ]


class llama_model_kv_override(ctypes.Structure):
    _fields_ = [
        ("key", ctypes.c_char * 128),
        ("tag", ctypes.c_int),
        ("value", llama_model_kv_override_value),
    ]

class llama_model_params(ctypes.Structure):

    _fields_ = [
        ("n_gpu_layers", ctypes.c_int32),
        ("split_mode", ctypes.c_int),
        ("main_gpu", ctypes.c_int32),
        ("tensor_split", ctypes.POINTER(ctypes.c_float)),
        ("progress_callback", llama_progress_callback),
        ("progress_callback_user_data", ctypes.c_void_p),
        ("kv_overrides", ctypes.POINTER(llama_model_kv_override)),
        ("vocab_only", ctypes.c_bool),
        ("use_mmap", ctypes.c_bool),
        ("use_mlock", ctypes.c_bool),
    ]


ggml_abort_callback = ctypes.CFUNCTYPE(ctypes.c_bool, ctypes.c_void_p)


class llama_context_params(ctypes.Structure):

    # update to new llama_context_params as of March 10, 2024

    _fields_ = [
        ("seed", ctypes.c_uint32),
        ("n_ctx", ctypes.c_uint32),
        ("n_batch", ctypes.c_uint32),
        ("n_parallel", ctypes.c_uint32),
        ("n_threads", ctypes.c_uint32),
        ("n_threads_batch", ctypes.c_uint32),
        ("rope_scaling_type", ctypes.c_int),
        ("pooling_type", ctypes.c_int),
        ("rope_freq_base", ctypes.c_float),
        ("rope_freq_scale", ctypes.c_float),
        ("yarn_ext_factor", ctypes.c_float),
        ("yarn_attn_factor", ctypes.c_float),
        ("yarn_beta_fast", ctypes.c_float),
        ("yarn_beta_slow", ctypes.c_float),
        ("yarn_orig_ctx", ctypes.c_uint32),
        ("defrag_thold", ctypes.c_float),
        ("cb_eval", ggml_backend_sched_eval_callback),
        ("cb_eval_user_data", ctypes.c_void_p),
        ("type_k", ctypes.c_int),
        ("type_v", ctypes.c_int),
        ("logits_all", ctypes.c_bool),
        ("embeddings", ctypes.c_bool),
        ("offload_kqv", ctypes.c_bool),
        ("abort_callback", ggml_abort_callback),
        ("abort_callback_data", ctypes.c_void_p),
    ]

    """
    _fields_ = [
        ("seed", ctypes.c_uint32),
        ("n_ctx", ctypes.c_uint32),
        ("n_batch", ctypes.c_uint32),
        ("n_threads", ctypes.c_uint32),
        ("n_threads_batch", ctypes.c_uint32),
        ("rope_scaling_type", ctypes.c_int32),
        ("rope_freq_base", ctypes.c_float),
        ("rope_freq_scale", ctypes.c_float),
        ("yarn_ext_factor", ctypes.c_float),
        ("yarn_attn_factor", ctypes.c_float),
        ("yarn_beta_fast", ctypes.c_float),
        ("yarn_beta_slow", ctypes.c_float),
        ("yarn_orig_ctx", ctypes.c_uint32),
        ("cb_eval", ggml_backend_sched_eval_callback),
        ("cb_eval_user_data", ctypes.c_void_p),
        ("type_k", ctypes.c_int),
        ("type_v", ctypes.c_int),
        ("mul_mat_q", ctypes.c_bool),
        ("logits_all", ctypes.c_bool),
        ("embedding", ctypes.c_bool),
        ("offload_kqv", ctypes.c_bool),
        ("do_pooling", ctypes.c_bool),
    ]
"""

class llama_model_quantize_params(ctypes.Structure):

    _fields_ = [
        ("nthread", ctypes.c_int32),
        ("ftype", ctypes.c_int),
        ("allow_requantize", ctypes.c_bool),
        ("quantize_output_tensor", ctypes.c_bool),
        ("only_copy", ctypes.c_bool),
        ("pure", ctypes.c_bool),
        ("imatrix", ctypes.c_void_p),
    ]



class llama_grammar_element(ctypes.Structure):
    _fields_ = [
        ("type", ctypes.c_int),
        ("value", ctypes.c_uint32),
    ]


class llama_timings(ctypes.Structure):
    _fields_ = [
        ("t_start_ms", ctypes.c_double),
        ("t_end_ms", ctypes.c_double),
        ("t_load_ms", ctypes.c_double),
        ("t_sample_ms", ctypes.c_double),
        ("t_p_eval_ms", ctypes.c_double),
        ("t_eval_ms", ctypes.c_double),
        ("n_sample", ctypes.c_int32),
        ("n_p_eval", ctypes.c_int32),
        ("n_eval", ctypes.c_int32),
    ]

class llama_chat_message(ctypes.Structure):
    _fields_ = [
        ("role", ctypes.c_char_p),
        ("content", ctypes.c_char_p),
    ]

class llama_kv_cache_view_cell(ctypes.Structure):
    _fields_ = [("pos", llama_pos)]

class llama_kv_cache_view(ctypes.Structure):
    _fields_ = [
        ("n_cells", ctypes.c_int32),
        ("n_max_seq", ctypes.c_int32),
        ("token_count", ctypes.c_int32),
        ("used_cells", ctypes.c_int32),
        ("max_contiguous", ctypes.c_int32),
        ("max_contiguous_idx", ctypes.c_int32),
        ("cells", ctypes.POINTER(llama_kv_cache_view_cell)),
        ("cells_sequences", ctypes.POINTER(llama_seq_id)),
    ]

llama_kv_cache_view_p = ctypes.POINTER(llama_kv_cache_view)

class llama_beam_view(ctypes.Structure):
    _fields_ = [
        ("tokens", llama_token_p),
        ("n_tokens", ctypes.c_size_t),
        ("p", ctypes.c_float),
        ("eob", ctypes.c_bool),
    ]


class llama_beams_state(ctypes.Structure):
    _fields_ = [
        ("beam_views", ctypes.POINTER(llama_beam_view)),
        ("n_beams", ctypes.c_size_t),
        ("common_prefix_length", ctypes.c_size_t),
        ("last_call", ctypes.c_bool),
    ]

def add_ctypes_declarations (_lib):

    # major interfaces
    llama_backend_init = _lib.llama_backend_init
    llama_backend_init.argtypes = []
    llama_backend_init.restype = None

    llama_model_default_params = _lib.llama_model_default_params
    llama_model_default_params.argtypes = []
    llama_model_default_params.restype = llama_model_params

    llama_context_default_params = _lib.llama_context_default_params
    llama_context_default_params.argtypes = []
    llama_context_default_params.restype = llama_context_params

    llama_backend_free = _lib.llama_backend_free
    llama_backend_free.argtypes = []
    llama_backend_free.restype = None

    llama_load_model_from_file = _lib.llama_load_model_from_file
    llama_load_model_from_file.argtypes = [ctypes.c_char_p, llama_model_params]
    llama_load_model_from_file.restype = llama_model_p_ctypes

    _lib.llama_max_devices.argtypes = []
    _lib.llama_max_devices.restype = ctypes.c_size_t

    llama_free_model = _lib.llama_free_model
    llama_free_model.argtypes = [llama_model_p_ctypes]
    llama_free_model.restype = None

    llama_new_context_with_model = _lib.llama_new_context_with_model
    llama_new_context_with_model.argtypes = [llama_model_p_ctypes, llama_context_params]
    llama_new_context_with_model.restype = llama_context_p_ctypes

    # llama_numa_init = _lib.llama_numa_init
    # llama_numa_init.argtypes = [ctypes.c_int]
    # llama_numa_init.restype = None

    llama_free = _lib.llama_free
    llama_free.argtypes = [llama_context_p_ctypes]
    llama_free.restype = None

    llama_time_us = _lib.llama_time_us
    llama_time_us.argtypes = []
    llama_time_us.restype = ctypes.c_int64

    llama_max_devices = _lib.llama_max_devices
    llama_max_devices.argtypes = []
    llama_max_devices.restype = ctypes.c_size_t

    llama_supports_mmap = _lib.llama_supports_mmap
    llama_supports_mmap.argtypes = []
    llama_supports_mmap.restype = ctypes.c_bool

    llama_supports_mlock = _lib.llama_supports_mlock
    llama_supports_mlock.argtypes = []
    llama_supports_mlock.restype = ctypes.c_bool

    llama_supports_gpu_offload = _lib.llama_supports_gpu_offload
    llama_supports_gpu_offload.argtypes = []
    llama_supports_gpu_offload.restype = ctypes.c_bool

    llama_get_model = _lib.llama_get_model
    llama_get_model.argtypes = [llama_context_p_ctypes]
    llama_get_model.restype = llama_model_p_ctypes

    llama_n_ctx = _lib.llama_n_ctx
    llama_n_ctx.argtypes = [llama_context_p_ctypes]
    llama_n_ctx.restype = ctypes.c_uint32

    llama_n_batch = _lib.llama_n_batch
    llama_n_batch.argtypes = [llama_context_p_ctypes]
    llama_n_batch.restype = ctypes.c_uint32

    llama_vocab_type = _lib.llama_vocab_type
    llama_vocab_type.argtypes = [llama_model_p_ctypes]
    llama_vocab_type.restype = ctypes.c_int

    llama_n_vocab = _lib.llama_n_vocab
    llama_n_vocab.argtypes = [llama_model_p_ctypes]
    llama_n_vocab.restype = ctypes.c_int32

    llama_n_ctx_train = _lib.llama_n_ctx_train
    llama_n_ctx_train.argtypes = [llama_model_p_ctypes]
    llama_n_ctx_train.restype = ctypes.c_int32

    llama_n_embd = _lib.llama_n_embd
    llama_n_embd.argtypes = [llama_model_p_ctypes]
    llama_n_embd.restype = ctypes.c_int32

    llama_model_meta_val_str = _lib.llama_model_meta_val_str
    llama_model_meta_val_str.argtypes = [llama_model_p_ctypes, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t, ]
    llama_model_meta_val_str.restype = ctypes.c_int32

    llama_model_meta_count = _lib.llama_model_meta_count
    llama_model_meta_count.argtypes = [llama_model_p_ctypes]
    llama_model_meta_count.restype = ctypes.c_int32

    llama_model_meta_key_by_index = _lib.llama_model_meta_key_by_index
    llama_model_meta_key_by_index.argtypes = [llama_model_p_ctypes, ctypes.c_int32, ctypes.c_char_p, ctypes.c_size_t, ]
    llama_model_meta_key_by_index.restype = ctypes.c_int32

    llama_model_meta_val_str_by_index = _lib.llama_model_meta_val_str_by_index
    llama_model_meta_val_str_by_index.argtypes = [llama_model_p_ctypes, ctypes.c_int32, ctypes.c_char_p,
                                                  ctypes.c_size_t, ]
    llama_model_meta_val_str_by_index.restype = ctypes.c_int32

    llama_model_desc = _lib.llama_model_desc
    llama_model_desc.argtypes = [llama_model_p_ctypes, ctypes.c_char_p, ctypes.c_size_t]
    llama_model_desc.restype = ctypes.c_int32

    llama_model_size = _lib.llama_model_size
    llama_model_size.argtypes = [llama_model_p_ctypes]
    llama_model_size.restype = ctypes.c_uint64

    llama_model_n_params = _lib.llama_model_n_params
    llama_model_n_params.argtypes = [llama_model_p_ctypes]
    llama_model_n_params.restype = ctypes.c_uint64

    llama_get_model_tensor = _lib.llama_get_model_tensor
    llama_get_model_tensor.argtypes = [llama_model_p_ctypes, ctypes.c_char_p]
    llama_get_model_tensor.restype = ctypes.c_void_p

    llama_kv_cache_view_init = _lib.llama_kv_cache_view_init
    llama_kv_cache_view_init.argtypes = [llama_context_p_ctypes, ctypes.c_int32]
    llama_kv_cache_view_init.restype = llama_kv_cache_view

    llama_kv_cache_view_free = _lib.llama_kv_cache_view_free
    llama_kv_cache_view_free.argtypes = [llama_kv_cache_view_p]
    llama_kv_cache_view_free.restype = None

    llama_kv_cache_view_update = _lib.llama_kv_cache_view_update
    llama_kv_cache_view_update.argtypes = [llama_context_p_ctypes, llama_kv_cache_view_p]
    llama_kv_cache_view_update.restype = None

    llama_get_kv_cache_token_count = _lib.llama_get_kv_cache_token_count
    llama_get_kv_cache_token_count.argtypes = [llama_context_p_ctypes]
    llama_get_kv_cache_token_count.restype = ctypes.c_int32

    llama_get_kv_cache_used_cells = _lib.llama_get_kv_cache_used_cells
    llama_get_kv_cache_used_cells.argtypes = [llama_context_p_ctypes]
    llama_get_kv_cache_used_cells.restype = ctypes.c_int32

    llama_kv_cache_clear = _lib.llama_kv_cache_clear
    llama_kv_cache_clear.argtypes = [llama_context_p_ctypes]
    llama_kv_cache_clear.restype = None

    llama_kv_cache_seq_rm = _lib.llama_kv_cache_seq_rm
    llama_kv_cache_seq_rm.argtypes = [llama_context_p_ctypes, llama_seq_id, llama_pos, llama_pos, ]
    llama_kv_cache_seq_rm.restype = None

    llama_kv_cache_seq_cp = _lib.llama_kv_cache_seq_cp
    llama_kv_cache_seq_cp.argtypes = [llama_context_p_ctypes, llama_seq_id, llama_seq_id, llama_pos, llama_pos, ]

    llama_kv_cache_seq_cp.restype = None

    llama_kv_cache_seq_keep = _lib.llama_kv_cache_seq_keep
    llama_kv_cache_seq_keep.argtypes = [llama_context_p_ctypes, llama_seq_id]
    llama_kv_cache_seq_keep.restype = None

    llama_kv_cache_seq_div = _lib.llama_kv_cache_seq_div
    llama_kv_cache_seq_div.argtypes = [llama_context_p_ctypes, llama_seq_id, llama_pos, llama_pos, ctypes.c_int, ]
    llama_kv_cache_seq_div.restype = None

    llama_get_state_size = _lib.llama_get_state_size
    llama_get_state_size.argtypes = [llama_context_p_ctypes]
    llama_get_state_size.restype = ctypes.c_size_t

    llama_copy_state_data = _lib.llama_copy_state_data
    llama_copy_state_data.argtypes = [llama_context_p_ctypes, ctypes.POINTER(ctypes.c_uint8)]
    llama_copy_state_data.restype = ctypes.c_size_t

    llama_set_state_data = _lib.llama_set_state_data
    llama_set_state_data.argtypes = [llama_context_p_ctypes, ctypes.POINTER(ctypes.c_uint8)]
    llama_set_state_data.restype = ctypes.c_size_t

    """
    llama_eval = _lib.llama_eval
    llama_eval.argtypes = [llama_context_p_ctypes, llama_token_p, ctypes.c_int32, ctypes.c_int32]
    llama_eval.restype = ctypes.c_int
    """

    llama_batch_get_one = _lib.llama_batch_get_one
    llama_batch_get_one.argtypes = [llama_token_p, ctypes.c_int, llama_pos, llama_seq_id, ]
    llama_batch_get_one.restype = llama_batch

    llama_batch_init = _lib.llama_batch_init
    llama_batch_init.argtypes = [ctypes.c_int32, ctypes.c_int32, ctypes.c_int32]
    llama_batch_init.restype = llama_batch

    llama_batch_free = _lib.llama_batch_free
    llama_batch_free.argtypes = [llama_batch]
    llama_batch_free.restype = None

    llama_decode = _lib.llama_decode
    llama_decode.argtypes = [llama_context_p_ctypes, llama_batch]
    llama_decode.restype = ctypes.c_int32

    llama_set_n_threads = _lib.llama_set_n_threads
    llama_set_n_threads.argtypes = [llama_context_p_ctypes, ctypes.c_uint32, ctypes.c_uint32, ]
    llama_set_n_threads.restype = None

    llama_get_logits = _lib.llama_get_logits
    llama_get_logits.argtypes = [llama_context_p_ctypes]
    llama_get_logits.restype = ctypes.POINTER(ctypes.c_float)

    llama_get_logits_ith = _lib.llama_get_logits_ith
    llama_get_logits_ith.argtypes = [llama_context_p_ctypes, ctypes.c_int32]
    llama_get_logits_ith.restype = ctypes.POINTER(ctypes.c_float)

    llama_get_embeddings = _lib.llama_get_embeddings
    llama_get_embeddings.argtypes = [llama_context_p_ctypes]
    llama_get_embeddings.restype = ctypes.POINTER(ctypes.c_float)

    llama_get_embeddings_ith = _lib.llama_get_embeddings_ith
    llama_get_embeddings_ith.argtypes = [llama_context_p_ctypes, ctypes.c_int32]
    llama_get_embeddings_ith.restype = ctypes.POINTER(ctypes.c_float)

    llama_token_get_text = _lib.llama_token_get_text
    llama_token_get_text.argtypes = [llama_model_p_ctypes, llama_token]
    llama_token_get_text.restype = ctypes.c_char_p

    llama_token_get_score = _lib.llama_token_get_score
    llama_token_get_score.argtypes = [llama_model_p_ctypes, llama_token]
    llama_token_get_score.restype = ctypes.c_float

    llama_token_get_type = _lib.llama_token_get_type
    llama_token_get_type.argtypes = [llama_model_p_ctypes, llama_token]
    llama_token_get_type.restype = ctypes.c_int

    llama_token_bos = _lib.llama_token_bos
    llama_token_bos.argtypes = [llama_model_p_ctypes]
    llama_token_bos.restype = llama_token

    llama_token_eos = _lib.llama_token_eos
    llama_token_eos.argtypes = [llama_model_p_ctypes]
    llama_token_eos.restype = llama_token

    llama_token_nl = _lib.llama_token_nl
    llama_token_nl.argtypes = [llama_model_p_ctypes]
    llama_token_nl.restype = llama_token

    llama_add_bos_token = _lib.llama_add_bos_token
    llama_add_bos_token.argtypes = [llama_model_p_ctypes]
    llama_add_bos_token.restype = ctypes.c_int32

    llama_add_eos_token = _lib.llama_add_eos_token
    llama_add_eos_token.argtypes = [llama_model_p_ctypes]
    llama_add_eos_token.restype = ctypes.c_int32

    llama_token_prefix = _lib.llama_token_prefix
    llama_token_prefix.argtypes = [llama_model_p_ctypes]
    llama_token_prefix.restype = llama_token

    llama_token_middle = _lib.llama_token_middle
    llama_token_middle.argtypes = [llama_model_p_ctypes]
    llama_token_middle.restype = llama_token

    llama_token_suffix = _lib.llama_token_suffix
    llama_token_suffix.argtypes = [llama_model_p_ctypes]
    llama_token_suffix.restype = llama_token

    llama_token_eot = _lib.llama_token_eot
    llama_token_eot.argtypes = [llama_model_p_ctypes]
    llama_token_eot.restype = llama_token

    llama_tokenize = _lib.llama_tokenize
    llama_tokenize.argtypes = [llama_model_p_ctypes, ctypes.c_char_p, ctypes.c_int32, llama_token_p, ctypes.c_int32,
                               ctypes.c_bool, ctypes.c_bool, ]
    llama_tokenize.restype = ctypes.c_int32

    llama_token_to_piece = _lib.llama_token_to_piece
    llama_token_to_piece.argtypes = [llama_model_p_ctypes, llama_token, ctypes.c_char_p, ctypes.c_int32, ]
    llama_token_to_piece.restype = ctypes.c_int32

    llama_grammar_element_p = ctypes.POINTER(llama_grammar_element)

    llama_grammar_init = _lib.llama_grammar_init
    llama_grammar_init.argtypes = [ctypes.POINTER(llama_grammar_element_p), ctypes.c_size_t, ctypes.c_size_t, ]
    llama_grammar_init.restype = llama_grammar_p

    llama_grammar_free = _lib.llama_grammar_free
    llama_grammar_free.argtypes = [llama_grammar_p]
    llama_grammar_free.restype = None

    llama_grammar_copy = _lib.llama_grammar_copy
    llama_grammar_copy.argtypes = [llama_grammar_p]
    llama_grammar_copy.restype = llama_grammar_p

    llama_set_rng_seed = _lib.llama_set_rng_seed
    llama_set_rng_seed.argtypes = [llama_context_p_ctypes, ctypes.c_uint32]
    llama_set_rng_seed.restype = None

    llama_sample_repetition_penalties = _lib.llama_sample_repetition_penalties
    llama_sample_repetition_penalties.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, llama_token_p,
                                                  ctypes.c_size_t, ctypes.c_float, ctypes.c_float, ctypes.c_float]
    llama_sample_repetition_penalties.restype = None

    llama_sample_apply_guidance = _lib.llama_sample_apply_guidance
    llama_sample_apply_guidance.argtypes = [llama_context_p_ctypes, ctypes.POINTER(ctypes.c_float),
                                            ctypes.POINTER(ctypes.c_float), ctypes.c_float, ]
    llama_sample_apply_guidance.restype = None

    """
    llama_sample_classifier_free_guidance = _lib.llama_sample_classifier_free_guidance
    llama_sample_classifier_free_guidance.argtypes = [llama_context_p_ctypes, llama_token_data_array_p,
                                                      llama_context_p_ctypes, ctypes.c_float, ]
    llama_sample_classifier_free_guidance.restype = None
    """

    llama_sample_softmax = _lib.llama_sample_softmax
    llama_sample_softmax.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, ]
    llama_sample_softmax.restype = None

    llama_sample_top_k = _lib.llama_sample_top_k
    llama_sample_top_k.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, ctypes.c_int32, ctypes.c_size_t, ]
    llama_sample_top_k.restype = None

    llama_sample_top_p = _lib.llama_sample_top_p
    llama_sample_top_p.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, ctypes.c_float, ctypes.c_size_t, ]
    llama_sample_top_p.restype = None

    llama_sample_min_p = _lib.llama_sample_min_p
    llama_sample_min_p.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, ctypes.c_float, ctypes.c_size_t, ]
    llama_sample_min_p.restype = None

    llama_sample_tail_free = _lib.llama_sample_tail_free
    llama_sample_tail_free.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, ctypes.c_float,
                                       ctypes.c_size_t, ]
    llama_sample_tail_free.restype = None

    llama_sample_typical = _lib.llama_sample_typical
    llama_sample_typical.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, ctypes.c_float,
                                     ctypes.c_size_t, ]
    llama_sample_typical.restype = None

    llama_sample_entropy = _lib.llama_sample_entropy
    llama_sample_entropy.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, ctypes.c_float, ctypes.c_float,
                                     ctypes.c_float]
    llama_sample_entropy.restype = None

    llama_sample_temp = _lib.llama_sample_temp
    llama_sample_temp.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, ctypes.c_float, ]
    llama_sample_temp.restype = None

    llama_sample_grammar = _lib.llama_sample_grammar
    llama_sample_grammar.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, llama_grammar_p, ]
    llama_sample_grammar.restype = None

    llama_sample_token_mirostat = _lib.llama_sample_token_mirostat
    llama_sample_token_mirostat.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, ctypes.c_float,
                                            ctypes.c_float, ctypes.c_int32, ctypes.POINTER(ctypes.c_float), ]
    llama_sample_token_mirostat.restype = llama_token

    llama_sample_token_mirostat_v2 = _lib.llama_sample_token_mirostat_v2
    llama_sample_token_mirostat_v2.argtypes = [llama_context_p_ctypes, llama_token_data_array_p, ctypes.c_float,
                                               ctypes.c_float, ctypes.POINTER(ctypes.c_float), ]
    llama_sample_token_mirostat_v2.restype = llama_token

    llama_sample_token_greedy = _lib.llama_sample_token_greedy
    llama_sample_token_greedy.argtypes = [
        llama_context_p_ctypes,
        llama_token_data_array_p,
    ]
    llama_sample_token_greedy.restype = llama_token

    llama_sample_token = _lib.llama_sample_token
    llama_sample_token.argtypes = [
        llama_context_p_ctypes,
        llama_token_data_array_p,
    ]
    llama_sample_token.restype = llama_token

    llama_grammar_accept_token = _lib.llama_grammar_accept_token
    llama_grammar_accept_token.argtypes = [
        llama_context_p_ctypes,
        llama_grammar_p,
        llama_token,
    ]
    llama_grammar_accept_token.restype = None

    llama_beam_search_callback_fn_t = ctypes.CFUNCTYPE(None, ctypes.c_void_p, llama_beams_state)

    llama_beam_search = _lib.llama_beam_search
    llama_beam_search.argtypes = [llama_context_p_ctypes, llama_beam_search_callback_fn_t, ctypes.c_void_p,
                                  ctypes.c_size_t, ctypes.c_int32, ctypes.c_int32, ]
    llama_beam_search.restype = None

    llama_get_timings = _lib.llama_get_timings
    llama_get_timings.argtypes = [llama_context_p_ctypes]
    llama_get_timings.restype = llama_timings

    llama_print_timings = _lib.llama_print_timings
    llama_print_timings.argtypes = [llama_context_p_ctypes]
    llama_print_timings.restype = None

    llama_reset_timings = _lib.llama_reset_timings
    llama_reset_timings.argtypes = [llama_context_p_ctypes]
    llama_reset_timings.restype = None

    llama_print_system_info = _lib.llama_print_system_info
    llama_print_system_info.argtypes = []
    llama_print_system_info.restype = ctypes.c_char_p

    llama_log_set = _lib.llama_log_set
    llama_log_set.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    llama_log_set.restype = None

    llama_dump_timing_info_yaml = _lib.llama_dump_timing_info_yaml
    llama_dump_timing_info_yaml.argtypes = [ctypes.c_void_p, llama_context_p_ctypes]
    llama_dump_timing_info_yaml.restype = None

    return _lib


class _LlamaModel:

    """ _LLamaModel is a Python object wrapper around the C pointer to the llama_cpp model object
    that is created upon loading. It does not do much, except provide a 'home' to self.model, which
    points to the loaded gguf model and is used in all methods. """

    _llama_free_model = None

    def __init__(self, _lib, path_model, params):

        self.path_model = path_model
        self.params = params

        self._llama_free_model = _lib.llama_free_model

        self.model = None

        if not os.path.exists(path_model):
            raise FilePathDoesNotExistException(path_model)

        #   main function call to _lib
        self.model = _lib.llama_load_model_from_file(self.path_model.encode("utf-8"), self.params)

        if self.model is None:
            raise ModelNotFoundException(path_model)

    def __del__(self):
        if self.model is not None and self._llama_free_model is not None:
            self._llama_free_model(self.model)
            self.model = None


class _LlamaContext:

    """ _LlamaContext is a Python object wrapper around the context object pointer instantiated by llama.cpp.
     The context consists of a combination of a model and set of sampling parameters.   This object does not
     do much, except provide the home to self.ctx which is the context object used for all methods. """

    _llama_free = None

    def __init__(self, _lib, model, params):

        self.model = model
        self.params = params

        self._llama_free = _lib.llama_free
        self.ctx = None

        assert self.model.model is not None

        self.ctx = _lib.llama_new_context_with_model(
            self.model.model, self.params
        )

        if self.ctx is None:
            raise ModelNotFoundException("Llama-context-not-created-check-if-model-correctly-loaded")

    def __del__(self):
        if self.ctx is not None and self._llama_free is not None:
            self._llama_free(self.ctx)
            self.ctx = None


class _LlamaBatch:

    """ _LLamaBatch object is a Python object wrapper around llama_cpp batch object pointer, which is
    used in the generation process. """

    # largely follows implementation from llama-cpp-python

    _llama_batch_free = None

    def __init__(self, _lib, n_tokens, embd, n_seq_max):

        self._n_tokens = n_tokens
        self.embd = embd
        self.n_seq_max = n_seq_max

        self._llama_batch_free = _lib.llama_batch_free

        self.batch = None
        self.batch = _lib.llama_batch_init(self._n_tokens, self.embd, self.n_seq_max)

    def __del__(self):
        if self.batch is not None and self._llama_batch_free is not None:
            self._llama_batch_free(self.batch)
            self.batch = None

    def n_tokens(self):
        assert self.batch is not None
        return self.batch.n_tokens

    def reset(self):
        assert self.batch is not None
        self.batch.n_tokens = 0

    def set_batch(self, batch, n_past, logits_all):
        assert self.batch is not None
        n_tokens = len(batch)
        self.batch.n_tokens = n_tokens
        for i in range(n_tokens):
            self.batch.token[i] = batch[i]
            self.batch.pos[i] = n_past + i
            self.batch.seq_id[i][0] = 0
            self.batch.n_seq_id[i] = 1
            self.batch.logits[i] = logits_all

        self.batch.logits[n_tokens - 1] = True

    def add_sequence(self, batch, seq_id, logits_all):
        assert self.batch is not None
        n_tokens = len(batch)
        n_tokens0 = self.batch.n_tokens
        self.batch.n_tokens += n_tokens
        for i in range(n_tokens):
            j = n_tokens0 + i
            self.batch.token[j] = batch[i]
            self.batch.pos[j] = i
            self.batch.seq_id[j][0] = seq_id
            self.batch.n_seq_id[j] = 1
            self.batch.logits[j] = logits_all
        self.batch.logits[n_tokens - 1] = True


class _LlamaTokenDataArray:

    """_LlamaTokenDataArray is a Python object wrapper around llama_cpp token data array object, which is used as
    input into the generation inference process. """

    #   follows the implementation from llama-cpp-python

    def __init__(self, *, n_vocab):
        self.n_vocab = n_vocab
        self.candidates_data = np.array(
            [],
            dtype=np.dtype(
                [("id", np.intc), ("logit", np.single), ("p", np.single)], align=True
            ),
        )
        self.candidates_data.resize(3, self.n_vocab, refcheck=False)
        self.candidates = llama_token_data_array(
            data=self.candidates_data.ctypes.data_as(llama_token_data_p),
            size=self.n_vocab,
            sorted=False,
        )
        self.default_candidates_data_id = np.arange(self.n_vocab, dtype=np.intc)
        self.default_candidates_data_p = np.zeros(self.n_vocab, dtype=np.single)

    def copy_logits(self, logits):
        self.candidates_data["id"][:] = self.default_candidates_data_id
        self.candidates_data["logit"][:] = logits
        self.candidates_data["p"][:] = self.default_candidates_data_p
        self.candidates.data = self.candidates_data.ctypes.data_as(llama_token_data_p)
        self.candidates.sorted = ctypes.c_bool(False)
        self.candidates.size = ctypes.c_size_t(self.n_vocab)


@llama_log_callback
def llama_log_callback(level, text, user_data):

    """ Controls the display log output from llama.cpp engine - currently exposing two options 'ON' or 'OFF' """

    #   note: reserving level and user_data as options for the future
    #   --adapted from more sophisticated logging mechanism in llama-cpp-python

    if os.environ.get("llama_cpp_verbose") != "OFF":
        print(text.decode("utf-8"), end="", flush=True, file=sys.stderr)
    else:
        # no action taken if verbose is if OFF
        do_nothing = 0


class GGUFConfigs:

    """GGUFConfigs is main global configuration object for GGUF Generative Models.   Most of these config items
     do not need to be changed - and should be changed only if you know why you are changing them, as it could
     impact the stability of the back-end llama.cpp library.

     The most common configs are exposed in _conf_libs

     """

    #   note: to "bring your own" llama.cpp custom compiled back-end, set the following:
    #   GGUFConfigs().set_config("custom_lib_path") = "/path/to/your/lib"

    _conf_libs = {"custom_lib_path": None,

                  # --Mac:  uses Mac Metal GPU by default
                  # --Linux / Windows - checks for cuda availability
                  "use_gpu": True,

                  # note this will be used on Windows and Linux, but not Mac
                  "n_gpu_layers": 50,
                  "cuda_driver_min_level": 12.1,
                  "cuda_platforms": ["linux", "win32"],
                  "backend_initialized": False,

                  "max_output_tokens": 256,
                  "temperature_default": 0.3,

                  "llama_cpp_verbose": "OFF",

                  # prebuilt shared libraries included in llmware
                  "windows": "libllama_win.dll",
                  "windows_cuda": "libllama_win_cuda.dll",
                  "mac_metal": "libllama_mac_metal.dylib",
                  "mac_x86": "libllama_mac_x86.dylib",
                  "linux_x86": "libllama_linux_x86.so",
                  "linux_cuda": "libllama_linux_cuda.so",

                  "n_threads": max(multiprocessing.cpu_count() // 2, 1),
                  "n_threads_batch": max(multiprocessing.cpu_count() // 2, 1)
    }

    #   note: with temperature used as primary attribute to adjust sampling,
    #   most of the params do not need to be adjusted

    _conf_sampling_params = {"top_k": 40,
                             "top_p": 0.95,
                             "min_p": 0.05,
                             "tfs_z": 1.0,
                             "typical_p": 1.0,
                             "penalty_last_n": 64,
                             "penalty_repeat": 1.1,
                             "penalty_freq": 0.0,
                             "penalty_present": 0.0,
                             "mirostat": 0,
                             "mirostat_tau": 5.0,
                             "mirostat_eta": 0.1,
                             "penalize_nl": True,
                             "logit_bias": {},
                             "cfg_scale": 1.0,
                             "n_probs": 0,
                             "mirostat_mu": field(default_factory=ctypes.c_float)
    }

    _conf_context_params = {"seed": 0xFFFFFFFF,
                            "n_ctx": 2048,
                            "n_batch": 2048,
                            "n_threads": 1,         # check/confirm
                            "n_threads_batch": 1,   # check/confirm
                            "rope_scaling_type": -1,
                            "rope_freq_base": 0.0,
                            "rope_freq_scale": 0.0,
                            "yarn_ext_factor": -1.0,
                            "yarn_attn_factor": 1.0,
                            "yarn_beta_fast": 32.0,
                            "yarn_beta_slow":1.0,
                            "yarn_orig_ctx": 0,
                            "mul_mat_q": True,
                            "logits_all": False,
                            "embedding": False,
                            "offload_kqv": True
    }

    @classmethod
    def get_config(cls, name):
        if name in cls._conf_libs:
            return cls._conf_libs[name]
        raise ConfigKeyException(name)

    @classmethod
    def set_config(cls, name, value):
        cls._conf_libs[name] = value

    @classmethod
    def get_sampling_params(cls):
        return cls._conf_sampling_params


