import os

module_conf = {
        "ner": {
            "bert_crf": {
                "path": "NER/BERT_CRF/named_entity_recognition.py",
                },
            "bert_crf_property": {
                "path": "NER/BERT_CRF_PROPERTY/named_entity_recognition.py",
                },
            },
        "re": {
            "mtb": {
                "path": "RE/MTB/RE_MTB.py",
                },
            "pure": {
                "path": "RE/PURE/relation_extraction.py",
                },
            "pure_ml": {
                "path": "RE/PURE_MULT_LABEL/relation_extraction.py",
                }
            },
        "ec": {
            "bert_mlp_classification": {
                "path": "EE/MRC/Event_Type_classify.py",
                },
            "bert_mlp_mult_classification": {
                "path": "EE/MRC/Event_Type_classify_BCE.py",
                },
            },
        "ae": {
            "bert_mrc_crf": {
                "path": "EE/MRC/Arguments_Extraction_MRC_CRF.py",
                },
            "ner_bert_mrc_crf": {
                "path": "EE/MRC/ner_Arguments_Extraction_MRC_CRF.py",
                },
            }
        }

valid_dataset_name="qpair_2kw"
data_path="../data/roberta_base_zh.qpair_2kw-split.22-01-11-12-03-36"
i2i_model_path="../i2i/output/roberta_base_zh.qpair_2kw-split.22-01-11-12-03-36"
valid_name=f"valid_add_neg.{valid_dataset_name}-%s.10.csv"
valid_list=["rand", "randpv", "highpv", "train_query"]
enable_valid_list=["train_query"]
faiss_topk=1000

config = dict(
    topk=faiss_topk,
    model_path=i2i_model_path,
    dim = 128,
    verbose = True,
    n_centroids = 0, #0表示根据样本数量动态生成聚类中心
    byte_per_vec = 8, #必须是dim的约数
    subQuantizer = 32, #必须是dim的约数
    train_fname = os.path.join(data_path, f'query.filtered.embedding'),
    emb_bin_fname = os.path.join(data_path, f'query.filtered.embedding.emb.bin'),
    query_bin_fname = os.path.join(data_path, f'query.filtered.embedding.query.bin'),
    model_fname = os.path.join(data_path, f'query.filtered.faiss.model'),
    valid_list = enable_valid_list,
    valid_fname = os.path.join('../data', valid_name),
    valid_emb_fname = os.path.join(data_path, valid_name + ".embedding"),
    result_fname = os.path.join(data_path, valid_name + f".top{faiss_topk}"),
    eval_result = os.path.join(data_path, valid_dataset_name + "_eval.metrics"),
)


