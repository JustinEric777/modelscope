PYTHONPATH=. torchrun examples/pytorch/stable_diffusion/cones2/finetune_stable_diffusion_cones2.py \
    --model 'damo/Cones2' \
    --model_revision 'v1.0.1' \
    --instance_prompt="dog" \
    --work_dir './tmp/cones2_diffusion' \
    --train_dataset_name 'buptwq/lora-stable-diffusion-finetune-dog' \
    --max_epochs 250 \
    --save_ckpt_strategy 'by_epoch' \
    --logging_interval 1 \
    --train.dataloader.workers_per_gpu 0 \
    --evaluation.dataloader.workers_per_gpu 0 \
    --train.optimizer.lr 1e-5 \
    --use_model_config true
