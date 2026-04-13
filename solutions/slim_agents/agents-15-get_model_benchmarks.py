
""" This example shows how to use the new Model Benchmark lookup to start using benchmark performance test data for
llmware models. """

from llmware.model_configs import model_benchmark_data
from llmware.models import ModelCatalog

#   view all benchmark data available
print("\nModel Benchmark Data Available")
for i, model in enumerate(model_benchmark_data):
    print("model: ", i, model)

#   lookup data for a specific model
model = "bling-phi-3-gguf"
print(f"\nModel Lookup - {model}")
score = ModelCatalog().get_benchmark_score(model)
print("score: ", score)

#   lookup with a simple filter - models with less than 7B parameters and accuracy_score > 95
condition = [{"parameters": "parameters < 7"}, {"accuracy_score": "accuracy_score > 95"}]

accurate_small_models = ModelCatalog().get_benchmark_by_filter(condition)
for a, mod in enumerate(accurate_small_models):
    print("accurate models: ", a, mod)


#   save a copy of the benchmark data to jsonl for future use
ModelCatalog().save_benchmark_report()
