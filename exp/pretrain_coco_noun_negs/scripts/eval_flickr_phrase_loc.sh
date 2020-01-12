export HDF5_USE_FILE_LOCKING=FALSE

python -m exp.pretrain_coco_noun_negs.run.eval_flickr_phrase_loc \
    --exp_name 'loss_wts_neg_noun_1_self_sup_0_lang_sup_1' \
    --model_num -100

# python -m exp.pretrain_coco_noun_negs.run.eval_flickr_phrase_loc \
#     --exp_name 'bert_negs_lang_loss_1_neg_loss_1_wo_detach' \
#     --model_num -100

# python -m exp.pretrain_coco_noun_negs.run.eval_flickr_phrase_loc \
#     --exp_name 'bert_negs_wo_obj_encoder' \
#     --model_num -100 \
#     --wo_obj_enc