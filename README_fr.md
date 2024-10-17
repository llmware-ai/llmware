# llmware
![Static Badge](https://img.shields.io/badge/python-3.9_%7C_3.10%7C_3.11%7C_3.12-blue?color=blue)
![PyPI - Version](https://img.shields.io/pypi/v/llmware?color=blue)
[![discord](https://img.shields.io/badge/Chat%20on-Discord-blue?logo=discord&logoColor=white)](https://discord.gg/MhZn5Nc39h)   
[![Documentation](https://github.com/llmware-ai/llmware/actions/workflows/pages.yml/badge.svg)](https://github.com/llmware-ai/llmware/actions/workflows/pages.yml)

![DevFest GIF](https://i.giphy.com/media/v1.Y2lkPTc5MGI3NjExc3dodTV4czFsd2lrYWV5N3BhaXV5MXpucDhrcWZ2ODF4amM2aXo3diZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/Bkax2GRzAt0PDHcmSq/giphy.gif)

<div style="display: flex; justify-content: center; margin: 20px 0;">
    <a href="README.md" style="padding: 5px 10px; background-color: #e7e7e7; color: #333; text-decoration: none; border: 1px solid #ccc; border-radius: 3px; margin-right: 5px; font-size: 12px;">English</a>
    <a href="README_fr.md" style="padding: 5px 10px; background-color: #e7e7e7; color: #333; text-decoration: none; border: 1px solid #ccc; border-radius: 3px; font-size: 12px;">Français</a>
</div>


**Les gagnants sélectionnés remporteront un prix de 25 $ sous forme de parrainage GitHub !**

## 🧰🛠️🔩Construire des pipelines RAG d'entreprise avec de petits modèles spécialisés  

`llmware` fournit un cadre unifié pour construire des applications basées sur les LLM (par exemple, RAG, Agents), en utilisant de petits modèles spécialisés qui peuvent être déployés en privé, intégrés en toute sécurité aux sources de connaissances d'entreprise et adaptés de manière rentable à tout processus métier.  

`llmware` comprend deux composants principaux :  

1. **Pipeline RAG** - des composants intégrés pour tout le cycle de vie de la connexion des sources de connaissances aux modèles d'IA générative ; et 

2. **50+ petits modèles spécialisés** adaptés à des tâches clés dans l'automatisation des processus d'entreprise, y compris les questions-réponses factuelles, la classification, le résumé et l'extraction.  

En rassemblant ces deux composants et en intégrant des modèles open source de premier plan et des technologies sous-jacentes, `llmware` offre un ensemble complet d'outils pour construire rapidement des applications LLM basées sur la connaissance pour les entreprises.  

La plupart de nos exemples peuvent être exécutés sans serveur GPU - commencez tout de suite sur votre ordinateur portable.   

[Rejoignez-nous sur Discord](https://discord.gg/MhZn5Nc39h)   |  [Regardez nos tutoriels sur YouTube](https://www.youtube.com/@llmware)  | [Explorez nos familles de modèles sur Huggingface](https://www.huggingface.co/llmware)   

Nouveau dans les Agents ?  [Consultez la série de démarrage rapide des Agents](https://github.com/llmware-ai/llmware/tree/main/fast_start/agents)  

Nouveau dans RAG ?  [Regardez la série de vidéos de démarrage rapide](https://www.youtube.com/playlist?list=PL1-dn33KwsmD7SB9iSO6vx4ZLRAWea1DB)  

🔥🔥🔥 [**Agents Multi-Modèles avec des Modèles SLIM**](examples/SLIM-Agents/) - [**Vidéo d'Introduction**](https://www.youtube.com/watch?v=cQfdaTcmBpY) 🔥🔥🔥   

[Introduction aux Modèles SLIM avec Appels de Fonction](https://github.com/llmware-ai/llmware/blob/main/examples/Models/using_function_calls.py)  
Pas envie d'attendre ? Obtenez les SLIM tout de suite :

```python 
from llmware.models import ModelCatalog

ModelCatalog().get_llm_toolkit()  # obtenez tous les modèles SLIM, livrés en tant qu'outils quantifiés petits et rapides 
ModelCatalog().tool_test_run("slim-sentiment-tool") # voyez le modèle en action avec un script de test inclus  
```

## 🎯  Fonctionnalités clés 
Écrire du code avec `llmware` repose sur quelques concepts principaux :

<details>
<summary><b>Catalogue de Modèles</b>: Accédez à tous les modèles de la même manière avec une recherche facile, quel que soit leur implémentation sous-jacente. 
</summary>  

```python
#  150+ modèles dans le catalogue avec plus de 50 modèles RAG optimisés BLING, DRAGON et Industry BERT
#  Support complet pour GGUF, HuggingFace, Sentence Transformers et principaux modèles basés sur API
#  Facile à étendre pour ajouter des modèles personnalisés - voir les exemples

from llmware.models import ModelCatalog
from llmware.prompts import Prompt

#   tous les modèles sont accessibles via le ModelCatalog
models = ModelCatalog().list_all_models()

#   pour utiliser un modèle du catalogue - méthode "load_model" et passer le paramètre model_name
my_model = ModelCatalog().load_model("llmware/bling-phi-3-gguf")
output = my_model.inference("quel est l'avenir de l'IA ?", add_context="Voici l'article à lire")

#   pour intégrer le modèle dans une invite
prompter = Prompt().load_model("llmware/bling-tiny-llama-v0")
response = prompter.prompt_main("quel est l'avenir de l'IA ?", context="Insérer des sources d'information")
```

</details>  

<details>  
<summary><b>Bibliothèque</b>: ingérer, organiser et indexer une collection de connaissances à grande échelle - Analyse, Fragmentation du Texte et Insertion. </summary>  

```python

from llmware.library import Library

#   pour analyser et fragmenter un ensemble de documents (pdf, pptx, docx, xlsx, txt, csv, md, json/jsonl, wav, png, jpg, html)  

#   étape 1 - créer une bibliothèque, qui est la structure de "conteneur de base de connaissances"
#          - les bibliothèques ont à la fois des ressources de collection de texte (DB) et des ressources de fichiers (par exemple, llmware_data/accounts/{library_name})
#          - les embeddings et les requêtes sont exécutés contre une bibliothèque

lib = Library().create_new_library("ma_bibliothèque")

#    étape 2 - add_files est la fonction d'ingestion universelle - pointez-la vers un dossier local avec des types de fichiers mixtes
#           - les fichiers seront traités par extension de fichier pour être analysés, fragmentés en texte et indexés dans la base de données de collection de texte

lib.add_files("/chemin/dossier/vers/mes/fichiers")

#   pour installer un embedding sur une bibliothèque - choisissez un modèle d'embedding et une base de données vectorielle
lib.install_new_embedding(embedding_model_name="mini-lm-sbert", vector_db="milvus", batch_size=500)

#   pour ajouter un deuxième embedding à la même bibliothèque (modèles + base de données vectorielle mix-and-match)  
lib.install_new_embedding(embedding_model_name="industry-bert-sec", vector_db="chromadb", batch_size=100)

#   facile de créer plusieurs bibliothèques pour différents projets et groupes

finance_lib = Library().create_new_library("finance_q4_2023")
finance_lib.add_files("/dossier_finance/")

hr_lib = Library().create_new_library("politiques_rh")
hr_lib.add_files("/dossier_rh/")

#    tirer la carte de la bibliothèque avec les métadonnées clés - documents, fragments de texte, images, tableaux, enregistrement d'embedding
lib_card = Library().get_library_card("ma_bibliothèque")

#   voir toutes les bibliothèques
all_my_libs = Library().get_all_library_cards()

```
</details>  

<details> 
<summary><b>Requête</b>: interroger des bibliothèques avec un mélange de texte, sémantique, hybride, métadonnées et filtres personnalisés. </summary>

```python

from llmware.retrieval import Query
from llmware.library import Library

#   étape 1 - charger la bibliothèque précédemment créée 
lib = Library().load_library("ma_bibliothèque")

#   étape 2 - créer un objet de requête et passer la bibliothèque
q = Query(lib)

#    étape 3 - exécuter plusieurs requêtes différentes (de nombreuses autres options dans les exemples)

#    requête de texte de base
results1 = q.text_query("requête de texte", result_count=20, exact_mode=False)

#    requête sémantique
results2 = q.semantic_query("requête sémantique", result_count=10)

#    combinaison d'une requête textuelle limitée à certains documents de la bibliothèque et "correspondance exacte" avec la requête
results3 = q.text_query_with_document_filter("nouvelle requête", {"file_name": "nom de fichier sélectionné"}, exact_mode=True)

#   pour appliquer un embedding spécifique (si plusieurs sur la bibliothèque), passer les noms lors de la création de l'objet de requête
q2 = Query(lib, embedding_model_name="mini_lm_sbert", vector_db="milvus

")

```
</details>

Here’s the converted text in French:

<details> 
<summary><b>Modèles optimisés RAG</b> - Modèles de 1 à 7 milliards de paramètres conçus pour l'intégration dans les flux de travail RAG et fonctionnant localement.</summary>

```python
""" Cet exemple 'Hello World' démontre comment commencer à utiliser des modèles BLING locaux avec le contexte fourni, 
en utilisant à la fois les versions Pytorch et GGUF. """

import time
from llmware.prompts import Prompt


def hello_world_questions():

    test_list = [

    {"query": "Quel est le montant total de la facture?",
     "answer": "$22,500.00",
     "context": "Services Vendor Inc. \n100 Elm Street Pleasantville, NY \nÀ Alpha Inc. 5900 1st Street "
                "Los Angeles, CA \nDescription Service d'ingénierie frontale $5000.00 \n Service d'ingénierie"
                " arrière $7500.00 \n Gestion de la qualité $10,000.00 \n Montant total $22,500.00 \n"
                "Faites tous les chèques à l'ordre de Services Vendor Inc. Le paiement est dû dans les 30 jours."
                "Si vous avez des questions concernant cette facture, contactez Bia Hermes. "
                "MERCI POUR VOTRE COMMANDE !  FACTURE FACTURE # 0001 DATE 01/01/2022 POUR Projet Alpha P.O. # 1000"},

    {"query": "Quel était le montant de l'excédent commercial?",
     "answer": "62,4 milliards de yens (416,6 millions de dollars)",
     "context": "Le solde commercial du Japon pour septembre passe en excédent, surprenant les attentes."
                "Le Japon a enregistré un excédent commercial de 62,4 milliards de yens (416,6 millions de dollars) pour septembre, "
                "dépassant les attentes des économistes interrogés par Reuters, qui tablaient sur un déficit commercial de 42,5 "
                "milliards de yens. Les données de l'agence des douanes japonaises ont révélé que les exportations en septembre "
                "ont augmenté de 4,3 % par rapport à l'année précédente, tandis que les importations ont chuté de 16,3 % par rapport à "
                "la même période l'année dernière. Selon FactSet, les exportations vers l'Asie ont chuté pour le neuvième mois consécutif, "
                "révélant une faiblesse persistante en Chine. Les exportations ont été soutenues par les envois vers "
                "les marchés occidentaux, a ajouté FactSet. — Lim Hui Jie"},

    {"query": "Quand le marché des machines LISP s'est-il effondré?",
     "answer": "1987.",
     "context": "Les participants sont devenus les leaders de la recherche en IA dans les années 1960."
                " Ils et leurs étudiants ont produit des programmes que la presse a décrits comme 'étonnants': "
                "des ordinateurs apprenaient des stratégies de dames, résolvaient des problèmes de mots en algèbre, "
                "démontraient des théorèmes logiques et parlaient anglais.  Au milieu des années 1960, la recherche aux "
                "États-Unis était fortement financée par le Département de la Défense et des laboratoires avaient été "
                "établis à travers le monde. Herbert Simon a prédit que 'les machines seront capables, "
                "dans vingt ans, de faire tout travail qu'un homme peut faire'. Marvin Minsky était d'accord, écrivant, "
                "'dans une génération ... le problème de la création de 'l'intelligence artificielle' sera "
                "substantiellement résolu'. Ils avaient, cependant, sous-estimé la difficulté du problème.  "
                "Les gouvernements américain et britannique ont interrompu la recherche exploratoire en réponse "
                "aux critiques de Sir James Lighthill et à la pression continue du Congrès américain "
                "pour financer des projets plus productifs. Le livre de Minsky et Papert, Perceptrons, a été compris "
                "comme prouvant que l'approche des réseaux de neurones artificiels ne serait jamais utile pour résoudre "
                "des tâches du monde réel, disqualifiant ainsi complètement l'approche.  L' 'hiver de l'IA', une période "
                "où obtenir un financement pour des projets d'IA était difficile, a suivi.  Au début des années 1980, "
                "la recherche en IA a été relancée par le succès commercial des systèmes experts, une forme d'IA "
                "qui simule les connaissances et les compétences analytiques d'experts humains. D'ici 1985, "
                "le marché de l'IA avait atteint plus d'un milliard de dollars. En même temps, le cinquième projet "
                "d'ordinateur de génération du Japon a inspiré les gouvernements américain et britannique à rétablir le financement "
                "de la recherche académique. Cependant, à partir de l'effondrement du marché des machines Lisp "
                "en 1987, l'IA est tombée à nouveau en disgrâce, et un deuxième hiver, plus long, a commencé."},

    {"query": "Quel est le taux actuel des obligations du Trésor à 10 ans?",
     "answer": "4,58%",
     "context": "Les actions ont grimpé vendredi même après la publication de données sur l'emploi américain plus fortes que prévu "
                "et d'une augmentation majeure des rendements des obligations du Trésor.  L'indice Dow Jones Industrial a gagné 195,12 points, "
                "soit 0,76 %, pour clôturer à 31 419,58. Le S&P 500 a ajouté 1,59 % à 4 008,50. Le Nasdaq Composite, riche en technologie, "
                "a augmenté de 1,35 %, clôturant à 12 299,68. L'économie américaine a ajouté 438 000 emplois en "
                "août, a déclaré le Département du Travail. Les économistes interrogés par Dow Jones s'attendaient à 273 000 "
                "emplois. Cependant, les salaires ont augmenté moins que prévu le mois dernier.  Les actions ont enregistré un retournement "
                "stupéfiant vendredi, après avoir initialement chuté suite au rapport sur l'emploi plus fort que prévu. "
                "À son point bas, le Dow avait chuté de 198 points; il a grimpé de plus de 500 points au plus fort du rallye. "
                "Le Nasdaq et le S&P 500 ont chuté de 0,8 % lors de leurs points les plus bas de la journée.  Les traders étaient incertains "
                "des raisons de l'inversion intrajournalière. Certains ont noté que cela pourrait être dû au chiffre des salaires plus faibles "
                "dans le rapport sur l'emploi qui a amené les investisseurs à reconsidérer leur position baissière précédente. "
                "D'autres ont noté le recul des rendements par rapport aux sommets de la journée. Une partie du rallye pourrait simplement "
                "être liée à un marché qui avait été extrêmement survendu, le S&P 500 étant à un moment donné de la semaine en baisse de plus de 9 % "
                "par rapport à son sommet plus tôt cette année.  Les rendements ont initialement augmenté après le rapport, le taux des "
                "obligations du Trésor à 10 ans se négociant près de son niveau le plus élevé en 14 ans. Le taux de référence a ensuite diminué "
                "de ces niveaux, mais était toujours en hausse d'environ 6 points de base à 4,58 %.  'Nous voyons un peu de retour "
                "des rendements par rapport à ce que nous étions autour de 4,8 %. [Avec] eux qui se replient un peu, je pense que cela "
                "aide le marché boursier,' a déclaré Margaret Jones, responsable des investissements chez Vibrant Industries "
                "Capital Advisors. 'Nous avons eu beaucoup de faiblesse sur le marché ces dernières semaines, et potentiellement "
                "certaines conditions de survente.'"},

    {"query": "La marge brute attendue est-elle supérieure à 70 %?",
     "answer": "Oui, entre 71,5 % et 72%.",
     "context": "Prévisions La prévision de NVIDIA pour le troisième trimestre de l'exercice 2024 est la suivante :"
                "Les revenus devraient être de 16,00 milliards de dollars, plus ou moins 2 %. Les marges brutes GAAP et non-GAAP "
                "sont attendues respectivement à 71,5 % et 72,5 %, plus ou moins "
                "50 points de base.  Les dépenses d'exploitation GAAP et non-GAAP devraient être "
                "respectivement d'environ 2,95 milliards de dollars et 2,00 milliards de dollars.  Les autres revenus et dépenses GAAP et "
                "non-GAAP devraient être d'un revenu d'environ 100 millions de dollars, hors gains et pertes provenant d'investissements non affiliés. "
                "Les taux d'imposition GAAP et non-GAAP devraient être de 14,5 %, plus ou moins 1 %, excluant tout élément distinct. "
                "Faits saillants NVIDIA a réalisé des progrès depuis sa précédente annonce

 de bénéfices, son action ayant grimpé "
                "de 42 % depuis lors.  Les revenus de NVIDIA pour le deuxième trimestre ont atteint 13,51 milliards de dollars, "
                "ce qui représente une augmentation de 101 % par rapport à l'année précédente. "
                "NVIDIA a enregistré des bénéfices net de 6,19 milliards de dollars, ou 2,48 $ par action. "
                "Les prévisions de l'entreprise indiquent une forte demande pour ses unités de traitement graphique (GPU) utilisées dans l'IA. "
                "Les analystes s'attendent à ce que l'IA et les services de cloud computing propulsent la croissance de l'entreprise à l'avenir."},

    {"query": "Quel est le taux de croissance de l'économie japonaise?",
     "answer": "2,5%",
     "context": "Le produit intérieur brut (PIB) du Japon a augmenté à un rythme annualisé de 2,5 % au cours du "
                "troisième trimestre, dépassant les attentes du marché. "
                "Cette croissance a été alimentée par la consommation des ménages, qui a augmenté de 1,2 %."
                " Le Japon fait face à des défis, notamment une inflation élevée et des tensions géopolitiques croissantes. "
                "Les experts estiment que le pays devra continuer à investir dans ses infrastructures et ses technologies "
                "pour soutenir cette croissance."},

    {"query": "Combien d'employés de la société ont quitté leurs postes?",
     "answer": "200 employés.",
     "context": "Au total, 200 employés de l'entreprise XYZ ont quitté leurs postes au cours du dernier trimestre, "
                "ce qui représente une augmentation de 15 % par rapport au trimestre précédent. "
                "Les dirigeants de l'entreprise attribuent ce départ à des changements dans la culture d'entreprise et "
                "à l'augmentation de la concurrence dans le secteur."},

    {"query": "Quelle entreprise a annoncé une augmentation de sa production?",
     "answer": "L'entreprise ABC.",
     "context": "L'entreprise ABC a annoncé qu'elle augmenterait sa production de 20 % au cours du prochain trimestre "
                "en raison d'une forte demande pour ses produits. "
                "Cette décision a été saluée par les investisseurs, qui voient cela comme un signe de la robustesse "
                "des performances de l'entreprise sur le marché."}
    
    ]

Voici la version française du script que tu as fourni :

```python
# Ceci est le script principal à exécuter

def bling_meets_llmware_hello_world(model_name):

    t0 = time.time()

    # Charger les questions
    test_list = hello_world_questions()

    print(f"\n > Chargement du modèle : {model_name}...")

    # Charger le modèle 
    prompter = Prompt().load_model(model_name)

    t1 = time.time()
    print(f"\n > Temps de chargement du modèle {model_name} : {t1-t0} secondes")
 
    for i, entries in enumerate(test_list):

        print(f"\n{i+1}. Question : {entries['query']}")
     
        # Exécuter le prompt
        output = prompter.prompt_main(entries["query"], context=entries["context"],
                                      prompt_name="default_with_context", temperature=0.30)

        # Afficher les résultats
        llm_response = output["llm_response"].strip("\n")
        print(f"Réponse LLM : {llm_response}")
        print(f"Réponse correcte : {entries['answer']}")
        print(f"Utilisation LLM : {output['usage']}")

    t2 = time.time()

    print(f"\nTemps total de traitement : {t2-t1} secondes")

    return 0


if __name__ == "__main__":

    # Liste des petits modèles bling prêts pour ordinateur portable 'rag-instruct' sur HuggingFace

    pytorch_models = ["llmware/bling-1b-0.1",                    #  le plus populaire
                      "llmware/bling-tiny-llama-v0",             #  le plus rapide 
                      "llmware/bling-1.4b-0.1",
                      "llmware/bling-falcon-1b-0.1",
                      "llmware/bling-cerebras-1.3b-0.1",
                      "llmware/bling-sheared-llama-1.3b-0.1",    
                      "llmware/bling-sheared-llama-2.7b-0.1",
                      "llmware/bling-red-pajamas-3b-0.1",
                      "llmware/bling-stable-lm-3b-4e1t-v0",
                      "llmware/bling-phi-3"                      # le plus précis (et le plus récent)  
                      ]

    # Les versions GGUF quantifiées se chargent généralement plus rapidement et fonctionnent bien sur un ordinateur portable avec au moins 16 Go de RAM
    gguf_models = ["bling-phi-3-gguf", "bling-stablelm-3b-tool", "dragon-llama-answer-tool", "dragon-yi-answer-tool", "dragon-mistral-answer-tool"]

    # Essayer un modèle de la liste des modèles pytorch ou gguf
    # Le plus récent (et le plus précis) est 'bling-phi-3-gguf'  

    bling_meets_llmware_hello_world(gguf_models[0])  

    # Consulter la fiche du modèle sur Huggingface pour les résultats de performance du test de référence RAG et d'autres informations utiles
```
</details>

Voici la version française de ton texte :

<details>
<summary><b>Options de Base de Données Simples à Évoluer</b> - magasins de données intégrés de l'ordinateur portable au cluster parallélisé.</summary>

```python
from llmware.configs import LLMWareConfig

#   pour définir la base de données de collection - mongo, sqlite, postgres  
LLMWareConfig().set_active_db("mongo")  

#   pour définir la base de données vectorielle (ou déclarer lors de l'installation)  
#   --options : milvus, pg_vector (postgres), redis, qdrant, faiss, pinecone, mongo atlas  
LLMWareConfig().set_vector_db("milvus")  

#   pour un démarrage rapide - aucune installation requise  
LLMWareConfig().set_active_db("sqlite")  
LLMWareConfig().set_vector_db("chromadb")   # essayer également faiss et lancedb  

#   pour un déploiement unique de postgres  
LLMWareConfig().set_active_db("postgres")  
LLMWareConfig().set_vector_db("postgres")  

#   pour installer mongo, milvus, postgres - voir les scripts docker-compose ainsi que les exemples
```

</details>

<details>

<summary> 🔥 <b> Agents avec Appels de Fonction et Modèles SLIM </b> 🔥 </summary>  

```python
from llmware.agents import LLMfx

text = ("L'action de Tesla a chuté de 8 % lors des échanges avant le marché après avoir annoncé un chiffre d'affaires et un bénéfice du quatrième trimestre qui "
        "n'ont pas atteint les estimations des analystes. L'entreprise de véhicules électriques a également averti que la croissance du volume des véhicules en "
        "2024 'pourrait être sensiblement inférieure' à celle de l'année dernière. Les revenus automobiles, quant à eux, n'ont augmenté "
        "que de 1 % par rapport à l'année précédente, en partie parce que les VE se vendaient à un prix inférieur à celui d'avant. "
        "Tesla a mis en œuvre d'importantes réductions de prix au cours de la seconde moitié de l'année dans le monde entier. Lors d'une présentation mercredi, "
        "l'entreprise a averti les investisseurs qu'elle était 'actuellement entre deux vagues majeures de croissance.'")

#   créer un agent en utilisant la classe LLMfx
agent = LLMfx()

#   charger le texte à traiter
agent.load_work(text)

#   charger 'models' comme 'tools' à utiliser dans le processus d'analyse
agent.load_tool("sentiment")
agent.load_tool("extract")
agent.load_tool("topics")
agent.load_tool("boolean")

#   exécuter des appels de fonction en utilisant différents outils
agent.sentiment()
agent.topics()
agent.extract(params=["company"])
agent.extract(params=["automotive revenue growth"])
agent.xsum()
agent.boolean(params=["est-ce que la croissance de 2024 est prévue pour être forte ? (expliquer)"])

#   à la fin du traitement, afficher le rapport qui a été automatiquement agrégé par clé
report = agent.show_report()

#   afficher un résumé de l'activité dans le processus
activity_summary = agent.activity_summary()

#   liste des réponses collectées
for i, entries in enumerate(agent.response_list):
    print("mise à jour : analyse de la réponse : ", i, entries)

output = {"report": report, "activity_summary": activity_summary, "journal": agent.journal}  
```

</details>


<details>

<summary> 🚀 <b>Commencer à coder - Démarrage rapide pour RAG</b> 🚀 </summary>

```python
# Cet exemple illustre une analyse simple de contrat
# utilisant un LLM optimisé pour RAG fonctionnant localement

import os
import re
from llmware.prompts import Prompt, HumanInTheLoop
from llmware.setup import Setup
from llmware.configs import LLMWareConfig

def contract_analysis_on_laptop(model_name):

    #  Dans ce scénario, nous allons :
    #  -- télécharger un ensemble d'échantillons de fichiers de contrat
    #  -- créer un Prompt et charger un modèle LLM BLING
    #  -- analyser chaque contrat, extraire les passages pertinents et poser des questions à un LLM local

    #  Boucle principale - Itérer à travers chaque contrat :
    #
    #      1.  analyser le document en mémoire (convertir un fichier PDF en morceaux de texte avec des métadonnées)
    #      2.  filtrer les morceaux de texte analysés avec un "sujet" (par exemple, "droit applicable") pour extraire les passages pertinents
    #      3.  emballer et assembler les morceaux de texte dans un contexte prêt pour le modèle
    #      4.  poser trois questions clés pour chaque contrat au LLM
    #      5.  imprimer à l'écran
    #      6.  sauvegarder les résultats en json et csv pour un traitement et une révision ultérieurs.

    #  Charger les fichiers d'exemple de llmware

    print(f"\n > Chargement des fichiers d'exemple de llmware...")

    sample_files_path = Setup().load_sample_files()
    contracts_path = os.path.join(sample_files_path, "Agreements")
 
    #  Liste de requêtes - voici les 3 sujets principaux et questions que nous aimerions que le LLM analyse pour chaque contrat

    query_list = {"contrat de travail exécutif": "Quels sont les noms des deux parties ?",
                  "salaire de base": "Quel est le salaire de base de l'exécutif ?",
                  "vacances": "Combien de jours de vacances l'exécutif recevra-t-il ?"}

    #  Charger le modèle sélectionné par nom qui a été passé à la fonction

    print(f"\n > Chargement du modèle {model_name}...")

    prompter = Prompt().load_model(model_name, temperature=0.0, sample=False)

    #  Boucle principale

    for i, contract in enumerate(os.listdir(contracts_path)):

        #   exclure l'artefact de fichier Mac (énervant, mais fait de la vie dans les démos)
        if contract != ".DS_Store":

            print("\nAnalyse du contrat : ", str(i + 1), contract)

            print("Réponses du LLM :")

            for key, value in query_list.items():

                # étape 1 + 2 + 3 ci-dessus - le contrat est analysé, découpé en morceaux de texte, filtré par clé de sujet,
                # ... puis emballé dans le prompt

                source = prompter.add_source_document(contracts_path, contract, query=key)

                # étape 4 ci-dessus - appel au LLM avec les informations 'source' déjà emballées dans le prompt

                responses = prompter.prompt_with_source(value, prompt_name="default_with_context")  

                # étape 5 ci-dessus - imprimer à l'écran

                for r, response in enumerate(responses):
                    print(key, ":", re.sub("[\n]", " ", response["llm_response"]).strip())

                # Nous avons terminé avec ce contrat, vider la source du prompt
                prompter.clear_source_materials()

    # étape 6 ci-dessus - sauvegarde de l'analyse en jsonl et csv

    # Sauvegarder le rapport jsonl dans jsonl dans le dossier /prompt_history
    print("\nÉtat du prompt sauvegardé à : ", os.path.join(LLMWareConfig.get_prompt_path(), prompter.prompt_id))
    prompter.save_state()

    # Sauvegarder le rapport csv qui inclut le modèle, la réponse, le prompt et les preuves pour révision humaine
    csv_output = HumanInTheLoop(prompter).export_current_interaction_to_csv()
    print("sortie csv sauvegardée à :  ", csv_output)


if __name__ == "__main__":

    # utiliser un modèle CPU local - essayer le plus récent - RAG finetune de Phi-3 quantifié et emballé en GGUF  
    model = "bling-phi-3-gguf"

    contract_analysis_on_laptop(model)
```
</details>


## 🔥 Quoi de neuf ? 🔥  

- **Évaluation des capacités des petits modèles** - voir [résultats de benchmark](https://medium.com/@darrenoberst/best-small-language-models-for-accuracy-and-enterprise-use-cases-benchmark-results-cf71964759c8) et [exemple_de_classement_de_modèle](fast_start/agents/agents-15-get_model_benchmarks.py)  

- **Utilisation des modèles Qwen2 pour RAG, appel de fonction et chat** - commencez en quelques minutes - voir [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Models/using-qwen2-models.py)  

- **Nouveaux modèles d'appel de fonction Phi-3** - commencez en quelques minutes - voir [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Models/using-phi-3-function-calls.py)  

- **BizBot - RAG + Chatbot SQL Local** - voir [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/biz_bot.py) et [vidéo](https://youtu.be/4nBYDEjxxTE?si=o6PDPbu0PVcT-tYd)  

- **Cas d'utilisation de l'outil de conférence - posez des questions à un enregistrement audio** - voir [outil_de_conférence](https://github.com/llmware-ai/llmware/blob/main/examples/Use_Cases/lecture_tool/)   

- **Services Web avec appels d'agents pour la recherche financière** - scénario de bout en bout - [vidéo](https://youtu.be/l0jzsg1_Ik0?si=hmLhpT1iv_rxpkHo) et [exemple](examples/Use_Cases/web_services_slim_fx.py)  

- **Transcription vocale avec WhisperCPP** - [premiers_pas](examples/Models/using-whisper-cpp-getting-started.py), [utilisation_des_fichiers_exemples](examples/Models/using-whisper-cpp-sample-files.py), et [cas_d'utilisation_d'analyse](examples/Use_Cases/parsing_great_speeches.py) avec [vidéo_de_grandes_discours](https://youtu.be/5y0ez5ZBpPE?si=KVxsXXtX5TzvlEws)    

- **Chatbot local Phi-3 GGUF en streaming avec interface utilisateur** - configurez votre propre chatbot Phi-3-gguf sur votre ordinateur en quelques minutes - [exemple](examples/UI/gguf_streaming_chatbot.py) avec [vidéo](https://youtu.be/gzzEVK8p3VM?si=8cNn_do0oxSzCEnM)  

- **Exemple de requête en langage naturel vers CSV de bout en bout** - utilisant le modèle slim-sql - [vidéo](https://youtu.be/z48z5XOXJJg?si=V-CX1w-7KRioI4Bi) et [exemple](examples/SLIM-Agents/text2sql-end-to-end-2.py) et maintenant en utilisant des tables personnalisées sur Postgres [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/agent_with_custom_tables.py)  

- **Agents multi-modèles avec modèles SLIM** - agents à étapes multiples avec SLIM sur CPU - [vidéo](https://www.youtube.com/watch?v=cQfdaTcmBpY) - [exemple](examples/SLIM-Agents)  

- **Exemple d'images de documents intégrés OCR** - extraire systématiquement du texte à partir d'images intégrées dans des documents [exemple](examples/Parsing/ocr_embedded_doc_images.py)   

- **Fonctions d'analyseur améliorées pour PDF, Word, Powerpoint et Excel** - nouveaux contrôles et stratégies de découpage de texte, extraction de tableaux, images, texte d'en-tête - [exemple](examples/Parsing/pdf_parser_new_configs.py)   

- **Serveur d'inférence d'agent** - configurer des agents multi-modèles sur le serveur d'inférence [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/SLIM-Agents/agent_api_endpoint.py)  

- **Optimisation de la précision des prompts RAG** - consultez [exemple](examples/Models/adjusting_sampling_settings.py) et vidéos - [partie I](https://youtu.be/7oMTGhSKuNY?si=14mS2pftk7NoKQbC) et [partie II](https://youtu.be/a7ErHxdRo8E?si=UJzdMoRXnHdkaA84)  

- **Nouveau scénario de conversation sur la durabilité** - ajustements pour un développement basé sur des prompts - [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/sustainability_conversation.py)  

- **Nouveau cadre et exemple de chatbot local intégré pour la recherche sur les produits** - consultez [exemple](examples/Use_Cases/llm_research_chatbot.py) 

- **Pour une démonstration visuelle des mises à jour récentes, regardez notre [vidéo](https://www.youtube.com/watch?v=yCR0z2x5p9g)**.



## 🌱 Commencer

**Étape 1 - Installer llmware** -  `pip3 install llmware` ou `pip3 install 'llmware[full]'`  

- Remarque : à partir de la version v0.3.0, nous proposons des options pour une [installation de base](https://github.com/llmware-ai/llmware/blob/main/llmware/requirements.txt) (ensemble minimal de dépendances) ou une [installation complète](https://github.com/llmware-ai/llmware/blob/main/llmware/requirements_extras.txt) (ajoute au cœur un ensemble plus large de bibliothèques Python connexes).

<details>
<summary><b>Étape 2 - Accéder aux Exemples</b> - Commencez rapidement avec plus de 100 recettes 'Copier-Coller'</summary>

## 🔥 Nouveaux Exemples Principaux 🔥  

Scénario de bout en bout - [**Appels de Fonction avec SLIM Extract et Services Web pour la Recherche Financière**](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/web_services_slim_fx.py)  
Analyse des Fichiers Vocaux - [**Grandes Discours avec Requête et Extraction LLM**](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/parsing_great_speeches.py)  
Nouveau sur LLMWare - [**Série de tutoriels Fast Start**](https://github.com/llmware-ai/llmware/tree/main/fast_start)  
Configuration - [**Premiers Pas**](https://github.com/llmware-ai/llmware/tree/main/examples/Getting_Started)  
Exemples SLIM -  [**Modèles SLIM**](examples/SLIM-Agents/)  

| Exemple     |  Détails      |
|-------------|--------------|
| 1.   Modèles BLING fast start ([code](examples/Models/bling_fast_start.py) / [vidéo](https://www.youtube.com/watch?v=JjgqOZ2v5oU)) | Commencez avec des modèles rapides, précis, basés sur CPU - questions-réponses, extraction clé-valeur et résumé de base.  |
| 2.   Analyser et Intégrer 500 Documents PDF ([code](examples/Embedding/docs2vecs_with_milvus-un_resolutions.py))  | Exemple de bout en bout pour l'Analyse, l'Intégration et la Consultation des documents de Résolution de l'ONU avec Milvus  |
| 3.  Récupération Hybride - Sémantique + Texte ([code](examples/Retrieval/dual_pass_with_custom_filter.py)) | Utiliser la récupération 'dual pass' pour combiner le meilleur de la recherche sémantique et textuelle |  
| 4.   Multiples Intégrations avec PG Vector ([code](examples/Embedding/using_multiple_embeddings.py) / [vidéo](https://www.youtube.com/watch?v=Bncvggy6m5Q)) | Comparaison de plusieurs Modèles d'Intégration utilisant Postgres / PG Vector |
| 5.   Modèles DRAGON GGUF ([code](examples/Models/dragon_gguf_fast_start.py) / [vidéo](https://www.youtube.com/watch?v=BI1RlaIJcsc&t=130s)) | Modèles GGUF RAG de pointe 7B.  | 
| 6.   RAG avec BLING ([code](examples/Use_Cases/contract_analysis_on_laptop_with_bling_models.py) / [vidéo](https://www.youtube.com/watch?v=8aV5p3tErP0)) | Utilisant l'analyse de contrats comme exemple, expérimentez avec RAG pour une analyse complexe de documents et extraction de texte en utilisant le modèle GPT BLING d'environ 1B paramètres fonctionnant sur votre ordinateur portable. |  
| 7.   Analyse de l'Accord de Service Principal avec DRAGON ([code](examples/Use_Cases/msa_processing.py) / [vidéo](https://www.youtube.com/watch?v=Cf-07GBZT68&t=2s)) | Analyse des MSAs en utilisant le Modèle YI 6B de DRAGON.   |                                                                                                                          |
| 8.   Exemple Streamlit ([code](examples/UI/simple_rag_ui_with_streamlit.py))  | Posez des questions sur les factures avec l'UI exécutant l'inférence.  |  
| 9.   Intégration de LM Studio ([code](examples/Models/using-open-chat-models.py) / [vidéo](https://www.youtube.com/watch?v=h2FDjUyvsKE&t=101s)) | Intégration des Modèles LM Studio avec LLMWare  |                                                                                                                                        |
| 10.  Prompts Avec Sources ([code](examples/Prompts/prompt_with_sources.py))  | Attachez une large gamme de sources de connaissances directement dans les Prompts.   |   
| 11.  Vérification des Faits ([code](examples/Prompts/fact_checking.py))  | Explorez l'ensemble complet des méthodes de preuve dans ce script exemple qui analyse un ensemble de contrats.   |
| 12.  Utiliser des Modèles de Chat GGUF 7B ([code](examples/Models/chat_models_gguf_fast_start.py)) | Utiliser 4 modèles de chat de pointe 7B en quelques minutes fonctionnant localement |  

Consultez :  [exemples llmware](https://github.com/llmware-ai/llmware/blob/main/examples/README.md)  

</details>  

<details>
<summary><b>Étape 3 - Vidéos Tutoriels</b> - consultez notre chaîne Youtube pour des tutoriels percutants de 5 à 10 minutes sur les derniers exemples.   </summary>

🎬 Consultez ces vidéos pour commencer rapidement :  
- [Résumé de Document](https://youtu.be/Ps3W-P9A1m8?si=Rxvst3RJv8ZaOk0L)  
- [Bling-3-GGUF Chatbot Local](https://youtu.be/gzzEVK8p3VM?si=8cNn_do0oxSzCEnM)  
- [Analyse de Recherche Complexe Basée sur des Agents](https://youtu.be/y4WvwHqRR60?si=jX3KCrKcYkM95boe)  
- [Commencer avec les SLIMs (avec code)](https://youtu.be/aWZFrTDmMPc?si=lmo98_quo_2Hrq0C)  
- [Prompting Incorrect pour RAG - Échantillonnage Stochastique - Partie I](https://youtu.be/7oMTGhSKuNY?si=_KSjuBnqArvWzYbx)  
- [Prompting Incorrect pour RAG - Échantillonnage Stochastique - Partie II - Expériences de Code](https://youtu.be/iXp1tj-pPjM?si=3ZeMgipY0vJDHIMY)  
- [Introduction aux Modèles SLIM](https://www.youtube.com/watch?v=cQfdaTcmBpY)  
- [Introduction à Text2SQL](https://youtu.be/BKZ6kO2XxNo?si=tXGt63pvrp_rOlIP)  
- [RAG avec BLING sur votre ordinateur portable](https://www.youtube.com/watch?v=JjgqOZ2v5oU)    
- [Modèles DRAGON-7B](https://www.youtube.com/watch?v=d_u7VaKu6Qk&t=37s)  
- [Installer et Comparer Plusieurs Intégrations avec Postgres et PGVector](https://www.youtube.com/watch?v=Bncvggy6m5Q)  
- [Contexte sur la Quantification GGUF & Exemple de Modèle DRAGON](https://www.youtube.com/watch?v=ZJyQIZNJ45E)  
- [Utiliser les Modèles de LM Studio](https://www.youtube.com/watch?v=h2FDjUyvsKE)  
- [Utiliser les Modèles Ollama](https://www.youtube.com/watch?v=qITahpVDuV0)  
- [Utiliser n'importe quel Modèle GGUF](https://www.youtube.com/watch?v=9wXJgld7Yow)  
- [Utiliser de petits LLM pour RAG pour l'Analyse de Contrat (avec LLMWare)](https://www.youtube.com/watch?v=8aV5p3tErP0)
- [Traitement des Factures avec LLMware](https://www.youtube.com/watch?v=VHZSaBBG-Bo&t=10s)
- [Ingestion de PDF à Grande Échelle](https://www.youtube.com/watch?v=O0adUfrrxi8&t=10s)
- [Évaluer les LLM pour RAG avec LLMWare](https://www.youtube.com/watch?v=s0KWqYg5Buk&t=105s)
- [Démarrage Rapide avec la Bibliothèque Open Source LLMWare](https://www.youtube.com/watch?v=0naqpH93eEU)
- [Utiliser la Génération Augmentée par Récupération (RAG) sans Base de Données](https://www.youtube.com/watch?v

=y4WvwHqRR60)
- [Récupération Multi-Modalité avec LLMware](https://www.youtube.com/watch?v=2zw8ByzEo1I)
- [Construire un Agent RAG en utilisant des Modèles SLIM](https://www.youtube.com/watch?v=6wIg7F5-kFg)

</details>



## Options de Stockage de Données

<details>
<summary><b>Début Rapide</b> : utilisez SQLite3 et ChromaDB (basé sur des fichiers) prêt à l'emploi - aucune installation requise </summary>  

```python
from llmware.configs import LLMWareConfig 
LLMWareConfig().set_active_db("sqlite")   
LLMWareConfig().set_vector_db("chromadb")  
```
</details>  

<details>
<summary><b>Vitesse + Échelle</b> : utilisez MongoDB (collection de texte) et Milvus (base de données vectorielle) - installez avec Docker Compose </summary> 

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose.yaml
docker compose up -d
```

```python
from llmware.configs import LLMWareConfig
LLMWareConfig().set_active_db("mongo")
LLMWareConfig().set_vector_db("milvus")
```

</details>  

<details>
<summary><b>Postgres</b> : utilisez Postgres pour la collection de texte et la base de données vectorielle - installez avec Docker Compose </summary> 

```bash
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose-pgvector.yaml
docker compose up -d
```

```python
from llmware.configs import LLMWareConfig
LLMWareConfig().set_active_db("postgres")
LLMWareConfig().set_vector_db("postgres")
```

</details>  

<details>
<summary><b>Mélange et Association</b> : LLMWare prend en charge 3 bases de données de collection de texte (Mongo, Postgres, SQLite) et 
10 bases de données vectorielles (Milvus, PGVector-Postgres, Neo4j, Redis, Mongo-Atlas, Qdrant, Faiss, LanceDB, ChromaDB et Pinecone)  </summary>

```bash
# scripts pour déployer d'autres options
curl -o docker-compose.yaml https://raw.githubusercontent.com/llmware-ai/llmware/main/docker-compose-redis-stack.yaml
```

</details>  

## Rencontrez nos Modèles    

- **Série de modèles SLIM :** petits modèles spécialisés ajustés pour les appels de fonction et les workflows d'agents multi-étapes et multi-modèles.  
- **Série de modèles DRAGON :** modèles optimisés RAG de qualité production de 6 à 9 milliards de paramètres - "Delivering RAG on ..." les modèles de base leaders.  
- **Série de modèles BLING :** modèles optimisés RAG, basés sur CPU, suivant les instructions de 1 à 5 milliards de paramètres.  
- **Modèles Industry BERT :** modèles d'embedding personnalisés formés par défaut, affinés pour les industries suivantes : assurance, contrats, gestion d'actifs, SEC.  
- **Quantification GGUF :** nous fournissons des versions 'gguf' et 'tool' de nombreux modèles SLIM, DRAGON et BLING, optimisés pour le déploiement sur CPU.  

## Utilisation des LLM et Configuration des Clés API et Secrets

LLMWare est une plateforme ouverte et prend en charge une large gamme de modèles open source et propriétaires. Pour utiliser LLMWare, vous n'avez pas besoin d'utiliser un LLM propriétaire - nous vous encourageons à expérimenter avec [SLIM](https://www.huggingface.co/llmware/), [BLING](https://huggingface.co/llmware), [DRAGON](https://huggingface.co/llmware), [Industry-BERT](https://huggingface.co/llmware), les exemples GGUF, tout en intégrant vos modèles préférés de HuggingFace et Sentence Transformers. 

Si vous souhaitez utiliser un modèle propriétaire, vous devrez fournir vos propres clés API. Les clés API et les secrets pour les modèles, AWS et Pinecone peuvent être configurés pour une utilisation dans des variables d'environnement ou passés directement aux appels de méthode.  

<details>  
<summary> ✨  <b>Feuille de Route - Où allons-nous ... </b>  </summary>

- 💡 Faciliter le déploiement de modèles open source finement ajustés pour construire des workflows RAG à la pointe de la technologie  
- 💡 Cloud privé - garder les documents, les pipelines de données, les magasins de données et les modèles sûrs et sécurisés  
- 💡 Quantification des modèles, en particulier GGUF, et démocratisation de l'utilisation révolutionnaire des LLM basés sur CPU de 1 à 9 milliards  
- 💡 Développer de petits LLM spécialisés optimisés pour RAG entre 1 et 9 milliards de paramètres  
- 💡 LLM spécifiques à l'industrie, modèles d'embedding et processus pour soutenir des cas d'utilisation basés sur la connaissance clés  
- 💡 Évolutivité pour les entreprises - conteneurisation, déploiements de travailleurs et Kubernetes  
- 💡 Intégration de SQL et d'autres sources de données d'entreprise à grande échelle  
- 💡 Workflows basés sur des agents multi-étapes et multi-modèles avec de petits modèles spécialisés appelant des fonctions  

Comme nos modèles, nous aspirons à ce que llmware soit "petit, mais puissant" - facile à utiliser et à démarrer, mais avec un impact puissant !  

</details>

Intéressé à contribuer à llmware ? Les informations sur les façons de participer se trouvent dans notre [Guide des Contributeurs](https://github.com/llmware-ai/llmware/blob/main/repo_docs/CONTRIBUTING.md#contributing-to-llmware). Comme pour tous les aspects de ce projet, les contributions sont régies par notre [Code de Conduite](https://github.com/llmware-ai/llmware/blob/main/repo_docs/CODE_OF_CONDUCT.md).

Questions et discussions sont les bienvenues dans nos [discussions GitHub](https://github.com/llmware-ai/llmware/discussions). 

Sure! Here’s the translation of the release notes and change log into French:

## 📣 Notes de version et journal des modifications

Voir aussi [notes de déploiement/install supplémentaires dans wheel_archives](https://github.com/llmware-ai/llmware/tree/main/wheel_archives)

**Dimanche 6 octobre - v0.3.7**  
- Ajout d'une nouvelle classe de modèle - OVGenerativeModel - pour prendre en charge l'utilisation de modèles empaquetés au format OpenVino  
- Ajout d'une nouvelle classe de modèle - ONNXGenerativeModel - pour prendre en charge l'utilisation de modèles empaquetés au format ONNX  
- Premiers pas avec [l'exemple OpenVino](https://github.com/llmware-ai/llmware/blob/main/examples/Models/using_openvino_models.py)  
- Premiers pas avec [l'exemple ONNX](https://github.com/llmware-ai/llmware/blob/main/examples/Models/using_onnx_models.py)  

**Mardi 1er octobre - v0.3.6**  
- Ajout de nouveaux modèles de chat pour les invites  
- Amélioration et mise à jour des configurations de modèle  
- Nouvelles fonctions utilitaires pour localiser et mettre en surbrillance les correspondances de texte dans les résultats de recherche  
- Amélioration des fonctions utilitaires de vérification de hachage  

**Lundi 26 août - v0.3.5**  
- Ajout de 10 nouveaux modèles BLING+SLIM au catalogue de modèles - avec Qwen2, Phi-3 et Phi-3.5  
- Lancement de nouveaux modèles DRAGON sur Qwen-7B, Yi-9B, Mistral-v0.3 et Llama-3.1  
- Nouveaux modèles Qwen2 (et RAG + réglages d'appel de fonction) - [using-qwen2-models](https://github.com/llmware-ai/llmware/blob/main/examples/Models/using-qwen2-models.py)  
- Nouveaux modèles d'appel de fonction Phi-3 - [using-phi-3-function-calls](https://github.com/llmware-ai/llmware/blob/main/examples/Models/using-phi-3-function-calls.py)  
- Nouvel exemple de cas d'utilisation - [lecture_tool](https://github.com/llmware-ai/llmware/blob/main/examples/Use_Cases/lecture_tool/)  
- Amélioration des configurations GGUF pour étendre la fenêtre de contexte  
- Ajout de données de performance de référence de modèle aux configurations de modèle  
- Amélioration des fonctions de hachage des utilitaires  

Pour l'historique complet des notes de version, veuillez ouvrir l'onglet journal des modifications.

**Systèmes d'exploitation pris en charge** : MacOS (Metal - M1/M2/M3), Linux (x86) et Windows  
- Linux - support d'Ubuntu 20+ (glibc 2.31+)  
- si vous avez besoin d'une autre version de Linux, veuillez signaler un problème - nous donnerons la priorité aux tests et assurerons le support.  

**Bases de données vectorielles prises en charge** : Milvus, Postgres (PGVector), Neo4j, Redis, LanceDB, ChromaDB, Qdrant, FAISS, Pinecone, Mongo Atlas Vector Search

**Bases de données d'index textuel prises en charge** : MongoDB, Postgres, SQLite

<details>
<summary><b>Optionnel</b></summary>

- [Docker](https://docs.docker.com/get-docker/)
  
- Pour activer les capacités de parsing OCR, installez les packages natifs [Tesseract v5.3.3](https://tesseract-ocr.github.io/tessdoc/Installation.html) et [Poppler v23.10.0](https://poppler.freedesktop.org/).

</details>

<details>
<summary><b>🚧 Journal des modifications</b></summary>

**Lundi 29 juillet - v03.4**  
- Amélioration des protections de sécurité pour les lectures de texte2sql db pour les agents LLMfx  
- Nouveaux exemples - voir [exemple](https://github.com/llmware-ai/llmware/blob/main/examples/UI/dueling_chatbot.py)  
- Plus d'exemples de Notebook - voir [exemples de notebook](https://github.com/llmware-ai/llmware/blob/main/examples/Notebooks)  

**Lundi 8 juillet - v03.3**  
- Améliorations des options de configuration des modèles, de journalisation et divers petits correctifs  
- Amélioration des configurations Azure OpenAI - voir [exemple](https://github.com/llmware-ai/llmware/blob/main/examples/Models/using-azure-openai.py)  

**Samedi 29 juin - v0.3.2**  
- Mise à jour des parseurs PDF et Office - améliorations des configurations dans les options de journalisation et de découpage de texte  

**Samedi 22 juin - v0.3.1**  
- Ajout du module 3 à la série d'exemples Fast Start [exemples 7-9 sur Agents & Appels de fonction](https://github.com/llmware-ai/llmware/tree/main/fast_start)  
- Ajout du modèle de rerank Jina pour la similarité sémantique en mémoire RAG - voir [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Embedding/using_semantic_reranker_with_rag.py)  
- Amélioration de la paramétrisation de récupération des modèles dans le processus de chargement des modèles  
- Ajout de nouvelles versions 'tiny' de slim-extract et slim-summary dans les versions Pytorch et GGUF - consultez 'slim-extract-tiny-tool' et 'slim-summary-tiny-tool'  
- Cas d'utilisation [Biz Bot] - voir [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/biz_bot.py) et [vidéo](https://youtu.be/4nBYDEjxxTE?si=o6PDPbu0PVcT-tYd)  
- Mise à jour des exigences numpy <2 et mise à jour de la version minimum de yfinance (>=0.2.38)  



**Mardi 4 juin - v0.3.0**  
- Ajout de la prise en charge de la nouvelle base de données intégrée 'no-install' Milvus Lite - voir [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Embedding/using_milvus_lite.py).  
- Ajout de deux nouveaux modèles SLIM au catalogue et aux processus d'agent - ['q-gen'](https://github.com/llmware-ai/llmware/tree/main/examples/SLIM-Agents/using-slim-q-gen.py) et ['qa-gen'](https://github.com/llmware-ai/llmware/tree/main/examples/SLIM-Agents/using-slim-qa-gen.py)  
- Mise à jour de l'instanciation de la classe de modèle pour fournir plus d'extensibilité afin d'ajouter de nouvelles classes dans différents modules  
- Nouveaux scripts d'installation rapide welcome_to_llmware.sh et welcome_to_llmware_windows.sh  
- Amélioration de la classe de modèle de base avec de nouvelles méthodes post_init et register configurables  
- Création de InferenceHistory pour suivre l'état global de toutes les inférences complétées  
- Améliorations et mises à jour multiples des journaux au niveau du module  
- Remarque : à partir de v0.3.0, l'installation avec pip fournit deux options - une installation minimale de base `pip3 install llmware` qui prendra en charge la plupart des cas d'utilisation, et une installation plus large `pip3 install 'llmware[full]'` avec d'autres bibliothèques couramment utilisées.  

**Mercredi 22 mai - v0.2.15**  
- Améliorations dans la gestion des dépendances Pytorch et Transformers par la classe de modèle (chargement juste à temps, si nécessaire)  
- Expansion des options de point de terminaison de l'API et de la fonctionnalité du serveur d'inférence - voir les nouvelles [options d'accès client](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/llmware_inference_api_client.py) et [server_launch](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/llmware_inference_server.py)  

**Samedi 18 mai - v0.2.14**  
- Nouvelles méthodes de parsing d'images OCR avec [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/slicing_and_dicing_office_docs.py)  
- Ajout de la première partie des améliorations de journalisation (WIP) dans les Configs et les Modèles.  
- Nouveau modèle d'embedding ajouté au catalogue - industry-bert-loans.  
- Mises à jour des méthodes d'importation de modèle et des configurations.  

**Dimanche 12 mai - v0.2.13**  
- Nouvelle méthode de streaming GGUF avec [exemple de base](https://github.com/llmware-ai/llmware/tree/main/examples/Models/gguf_streaming.py) et [chatbot local phi3](https://github.com/llmware-ai/llmware/tree/main/examples/UI/gguf_streaming_chatbot.py)  
- Nettoyages significatifs dans les imports auxiliaires et les dépendances pour réduire la complexité de l'installation - note : les fichiers requirements.txt et setup.py mis à jour.  
- Code défensif pour fournir un avertissement informatif sur toute dépendance manquante dans les parties spécialisées du code, par exemple, OCR, Web Parser.  
- Mises à jour des tests, des avis et de la documentation.  
- OpenAIConfigs créés pour prendre en charge Azure OpenAI.  



**Dimanche 5 mai - Mise à jour v0.2.12**  
- Lancement de ["bling-phi-3"](https://huggingface.co/llmware/bling-phi-3) et ["bling-phi-3-gguf"](https://huggingface.co/llmware/bling-phi-3-gguf) dans le ModelCatalog - le modèle BLING/DRAGON le plus récent et le plus précis  
- Nouvelle méthode de résumé de documents longs utilisant slim-summary-tool [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Prompts/document_summarizer.py)  
- Nouveaux fichiers d'exemple Office (PowerPoint, Word, Excel) [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Parsing/parsing_microsoft_ir_docs.py)  
- Ajout de la prise en charge de Python 3.12  
- Dépréciation de faiss et remplacement par 'no-install' chromadb dans les exemples Fast Start  
- Réorganisation des classes Datasets, Graph et Web Services  
- Mise à jour du parsing de la voix avec WhisperCPP dans la bibliothèque  

**Lundi 29 avril - Mise à jour v0.2.11**  
- Mises à jour des bibliothèques gguf pour Phi-3 et Llama-3  
- Ajout de Phi-3 [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Models/using-microsoft-phi-3.py) et Llama-3 [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Models/using-llama-3.py) et versions quantifiées au Model Catalog  
- Intégration de la classe de modèle WhisperCPP et des bibliothèques partagées préconstruites - [exemple de démarrage](https://github.com/llmware-ai/llmware/tree/main/examples/Models/using-whisper-cpp-getting-started.py)  
- Nouveaux fichiers d'exemple de voix pour les tests - [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Models/using-whisper-cpp-sample-files.py)  
- Amélioration de la détection CUDA sur Windows et des vérifications de sécurité pour les anciennes versions de Mac OS  

**Lundi 22 avril - Mise à jour v0.2.10**  
- Mises à jour de la classe Agent pour prendre en charge les requêtes en langage naturel sur des tables personnalisées dans Postgres [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/Use_Cases/agent_with_custom_tables.py)  
- Nouveau point de terminaison API Agent mis en œuvre avec le serveur d'inférence LLMWare et nouvelles capacités de l'agent [exemple](https://github.com/llmware-ai/llmware/tree/main/examples/SLIM-Agents/agent_api_endpoint.py)  

**Mardi 16 avril - Mise à jour v0.2.9**  
- Nouvelle classe CustomTable pour créer rapidement des tables de base de données personnalisées en conjonction avec des flux de travail basés sur LLM.  
- Méthodes améliorées pour convertir des fichiers CSV et JSON/JSONL en tables de base de données.  
- Voir les nouveaux exemples [Exemple de création de table personnalisée](https://github.com/llmware-ai/llmware/tree/main/examples/Structured_Tables/create_custom_table-1.py)  

**Mardi 9 avril - Mise à jour v0.2.8**  
- Analyseur Office (Word Docx, PowerPoint PPTX et Excel XLSX) - plusieurs améliorations - nouvelles bibliothèques + méthode Python.  
- Comprend : plusieurs corrections, contrôle amélioré du découpage de texte, extraction de texte d'en-tête et options de configuration.  
- En général, les nouvelles options d'analyseur Office sont conformes aux nouvelles options d'analyseur PDF.  
- Veuillez consulter [Exemple de configurations d'analyse de bureau](https://github.com/llmware-ai/llmware/tree/main/examples/Parsing/office_parser_new_configs.py)  

**Mercredi 3 avril - Mise à jour v0.2.7**  
- Analyseur PDF - plusieurs améliorations - nouvelles bibliothèques + méthodes Python.  
- Comprend : encodage UTF-8 pour les langues européennes.  
- Comprend : meilleur contrôle du découpage de texte, extraction de texte d'en-tête et options de configuration.  
- Veuillez consulter [Exemple de configurations d'analyse PDF](https://github.com/llmware-ai/llmware/tree/main/examples/Parsing/pdf_parser_new_configs.py) pour plus de détails.  
- Remarque : dépréciation de la prise en charge de aarch64-linux (utilisera les analyseurs 0.2.6). Prise en charge complète à l'avenir pour Linux Ubuntu20+ sur x86_64 + avec CUDA.  


**Vendredi 22 mars - Mise à jour v0.2.6**  
- Nouveaux modèles SLIM : résumé, extraction, xsum, booléen, tags-3b et combo sentiment-ner.  
- Nouvelles analyses de logit et d'échantillonnage.  
- Nouveaux exemples SLIM montrant comment utiliser les nouveaux modèles.  

**Jeudi 14 mars - Mise à jour v0.2.5**  
- Amélioration de la prise en charge de GGUF sur CUDA (Windows et Linux), avec de nouveaux binaires précompilés et gestion des exceptions.  
- Options de configuration de modèle améliorées (échantillonnage, température, capture du logit supérieur).  
- Ajout d'un support complet pour Ubuntu 20+ avec les analyseurs et le moteur GGUF.  
- Prise en charge des nouveaux modèles Anthropic Claude 3.  
- Nouvelles méthodes de récupération : document_lookup et aggregate_text.  
- Nouveau modèle : bling-stablelm-3b-tool - modèle de questions-réponses quantifié 3b rapide et précis - l'un de nos nouveaux favoris.  

**Mercredi 28 février - Mise à jour v0.2.4**  
- Mise à jour majeure de la classe de modèle génératif GGUF - prise en charge de Stable-LM-3B, options de construction CUDA et meilleur contrôle sur les stratégies d'échantillonnage.  
- Remarque : nouvelles bibliothèques construites avec llama.cpp emballées avec la construction à partir de v0.2.4.  
- Amélioration de la prise en charge GPU pour les modèles d'incorporation HF.  

**Vendredi 16 février - Mise à jour v0.2.3**  
- Ajout de 10+ modèles d'incorporation au ModelCatalog - nomic, jina, bge, gte, ember et uae-large.  
- Mise à jour de la prise en charge d'OpenAI >=1.0 et nouveaux modèles d'incorporation text-3.  
- Clés de modèle SLIM et output_values désormais accessibles dans le ModelCatalog.  
- Mise à jour des encodages à 'utf-8-sig' pour mieux gérer les fichiers txt/csv avec BOM.  

**Dernières mises à jour - 19 janv. 2024 - llmware v0.2.0**  
- Ajout de nouvelles options d'intégration de bases de données - Postgres et SQLite.  
- Amélioration des options de mise à jour d'état et de journalisation des événements d'analyseur pour l'analyse parallélisée.  
- Améliorations significatives des interactions entre les bases de données d'incorporation et de collection de texte.  
- Amélioration de la gestion des exceptions d'erreur lors du chargement de modules dynamiques.  

**Dernières mises à jour - 15 janv. 2024 : llmware v0.1.15**  
- Améliorations des requêtes de récupération à double passage.  
- Objets de configuration élargis et options pour les ressources de point de terminaison.  

**Dernières mises à jour - 30 déc. 2023 : llmware v0.1.14**  
- Ajout de la prise en charge des serveurs d'inférence Open Chat (compatible avec l'API OpenAI).  
- Amélioration des capacités pour plusieurs modèles d'incorporation et configurations de base de données vectorielles.  
- Ajout de scripts d'installation docker-compose pour les bases de données vectorielles PGVector et Redis.  
- Ajout de 'bling-tiny-llama' au catalogue de modèles.  

**Dernières mises à jour - 22 déc. 2023 : llmware v0.1.13**  
- Ajout de 3 nouvelles bases de données vectorielles - Postgres (PG Vector), Redis et Qdrant.  
- Amélioration de la prise en charge de l'intégration des transformateurs de phrases directement dans le catalogue de modèles.  
- Améliorations des attributs du catalogue de modèles.  
- Plusieurs nouveaux exemples dans Models & Embeddings, y compris GGUF, base de données vectorielle et catalogue de modèles.  

- **17 déc. 2023 : llmware v0.1.12**  
  - dragon-deci-7b ajouté au catalogue - modèle RAG affiné sur la nouvelle base de modèle haute performance 7B de Deci.  
  - Nouvelle classe GGUFGenerativeModel pour une intégration facile des modèles GGUF.  
  - Ajout de bibliothèques partagées préconstruites llama_cpp / ctransformer pour Mac M1, Mac x86, Linux x86 et Windows.  
  - 3 modèles DRAGON empaquetés en tant que modèles GGUF Q4_K_M pour une utilisation sur ordinateur portable CPU (dragon-mistral-7b, dragon-llama-7b, dragon-yi-6b).  
  - 4 modèles de chat open source de premier plan ajoutés au catalogue par défaut avec Q4_K_M.  

- **8 déc. 2023 : llmware v0.1.11**  
  - Nouveaux exemples de démarrage rapide pour l'ingestion et les embeddings de documents en haute volume avec Milvus.  
  - Nouvelle classe de modèle de serveur d'inférence 'Pop up' LLMWare et script d'exemple.  
  - Nouvel exemple de traitement de factures pour RAG.  
  - Amélioration de la gestion de la pile Windows pour prendre en charge le parsing de documents plus volumineux.  
  - Amélioration des options de mode de sortie de journalisation de débogage pour les analyseurs PDF et Office.  

- **30 nov. 2023 : llmware v0.1.10**  
  - Windows ajouté en tant que système d'exploitation pris en charge.  
  - Améliorations supplémentaires du code natif pour la gestion de la pile.  
  - Corrections mineures de défauts.  

- **24 nov. 2023 : llmware v0.1.9**  
  - Les fichiers Markdown (.md) sont désormais analysés et traités comme des fichiers texte.  
  - Optimisations de la pile des analyseurs PDF et Office qui devraient éviter la nécessité de définir ulimit -s.  
  - Nouvel exemple llmware_models_fast_start.py qui permet de découvrir et de sélectionner tous les modèles llmware HuggingFace.  
  - Dépendances natives (bibliothèques partagées et dépendances) désormais incluses dans le dépôt pour faciliter le développement local.  
  - Mises à jour de la classe Status pour prendre en charge les mises à jour de statut d'analyse de documents PDF et Office.  
  - Corrections mineures de défauts, y compris la gestion des blocs d'images dans les exportations de bibliothèque.  



- **17 nov. 2023 : llmware v0.1.8**  
  - Performance de génération améliorée en permettant à chaque modèle de spécifier le paramètre d'espace de fin.  
  - Amélioration de la gestion pour eos_token_id pour llama2 et mistral.  
  - Meilleure prise en charge du chargement dynamique de Hugging Face.  
  - Nouveaux exemples avec les nouveaux modèles DRAGON de llmware.  

- **14 nov. 2023 : llmware v0.1.7**  
  - Passé au format de paquet Python Wheel pour la distribution PyPi afin de fournir une installation transparente des dépendances natives sur toutes les plateformes prises en charge.  
  - Améliorations du ModelCatalog :  
    - Mise à jour d'OpenAI pour inclure les nouveaux modèles « turbo » 4 et 3.5 récemment annoncés.  
    - Mise à jour de l'incorporation Cohere v3 pour inclure les nouveaux modèles d'incorporation Cohere.  
    - Modèles BLING en tant qu'options enregistrées prêtes à l'emploi dans le catalogue. Ils peuvent être instanciés comme tout autre modèle, même sans le drapeau « hf=True ».  
    - Capacité à enregistrer de nouveaux noms de modèles, au sein des classes de modèles existantes, avec la méthode register dans le ModelCatalog.  
  - Améliorations des prompts :  
    - “evidence_metadata” ajouté aux dictionnaires de sortie prompt_main permettant aux réponses de prompt_main d'être intégrées dans les étapes de preuve et de vérification des faits sans modification.  
    - La clé API peut maintenant être passée directement dans une prompt.load_model(model_name, api_key = “[ma-clé-api]”).  
  - Serveur LLMWareInference - Livraison initiale :  
    - Nouvelle classe pour LLMWareModel qui est un wrapper sur un modèle basé sur une API de style HF personnalisé.  
    - LLMWareInferenceServer est une nouvelle classe qui peut être instanciée sur un serveur distant (GPU) pour créer un serveur API de test qui peut être intégré dans n'importe quel flux de travail de prompt.  

- **03 nov. 2023 : llmware v0.1.6**  
  - Mise à jour de l'emballage pour nécessiter mongo-c-driver 1.24.4 afin de contourner temporairement le plantage de segmentation avec mongo-c-driver 1.25.  
  - Mises à jour dans le code Python nécessaires en prévision d'un support futur de Windows.  

- **27 oct. 2023 : llmware v0.1.5**  
  - Quatre nouveaux scripts d'exemple axés sur les flux de travail RAG avec de petits modèles d'instruction ajustés finement qui fonctionnent sur un ordinateur portable (modèles BLING de `llmware` [BLING](https://huggingface.co/llmware)).  
  - Options élargies pour définir la température à l'intérieur d'une classe de prompt.  
  - Amélioration du post-traitement de la génération de modèles Hugging Face.  
  - Chargement simplifié des modèles génératifs Hugging Face dans les prompts.  
  - Livraison initiale d'une classe de statut central : lecture/écriture de l'état d'incorporation avec une interface cohérente pour les appelants.  
  - Amélioration du support de recherche de dictionnaire en mémoire pour des requêtes multi-clés.  
  - Suppression de l'espace final dans l'encadrement humain-bot pour améliorer la qualité de génération dans certains modèles ajustés finement.  
  - Corrections mineures de défauts, scripts de test mis à jour et mise à jour de version pour Werkzeug afin de résoudre une [alerte de sécurité de dépendance](https://github.com/llmware-ai/llmware/security/dependabot/2).  

- **20 oct. 2023 : llmware v0.1.4**  
  - Prise en charge GPU pour les modèles Hugging Face.  
  - Corrections de défauts et scripts de test supplémentaires.  


- **13 oct. 2023 : llmware v0.1.3**  
  - Prise en charge de la recherche vectorielle MongoDB Atlas.  
  - Prise en charge de l'authentification à l'aide d'une chaîne de connexion MongoDB.  
  - Méthodes de résumé de documents.  
  - Améliorations dans la capture automatique de la fenêtre de contexte du modèle et le passage des modifications dans la longueur de sortie attendue.  
  - Carte de jeu de données et description avec recherche par nom.  
  - Temps de traitement ajouté au dictionnaire d'utilisation de l'inférence du modèle.  
  - Scripts de test supplémentaires, exemples et corrections de défauts.  

- **06 oct. 2023 : llmware v0.1.1**  
  - Ajout de scripts de test au dépôt GitHub pour les tests de régression.  
  - Corrections mineures de défauts et mise à jour de version de Pillow pour résoudre une [alerte de sécurité de dépendance](https://github.com/llmware-ai/llmware/security/dependabot/1).  

- **02 oct. 2023 : llmware v0.1.0** 🔥 Version initiale de llmware en open source !! 🔥  

</details>