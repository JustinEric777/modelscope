# ### Setting up experimental environment.
"""
pip install numpy pandas matplotlib scikit-learn
pip install transformers datasets
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
pip install tqdm tensorboard torchmetrics sentencepiece charset_normalizer
pip install accelerate transformers_stream_generator

# Install the latest version of modelscope from source
git clone https://github.com/modelscope/modelscope.git
cd modelscope
pip install .

# Resolve torchmetrics dependencies and update numpy
pip install numpy -U
"""

from _common import *


@dataclass
class SftArguments:
    device: str = '0,1'  # e.g. '-1'; '0'; '0,1'
    seed: int = 42
    model_type: str = field(
        default='baichuan-7b',
        metadata={
            'choices':
            ['baichuan-7b', 'baichuan-13b', 'chatglm2', 'llama2-7b']
        })
    # baichuan-7b: 'lora': 16G; 'full': 80G
    sft_type: str = field(
        default='lora', metadata={'choices': ['lora', 'full']})
    data_sample: Optional[int] = None

    lora_target_modules: Optional[List[str]] = None
    lora_rank: int = 8
    lora_alpha: int = 32
    lora_dropout_p: float = 0.1

    gradient_checkpoint: bool = True
    batch_size: int = 1
    max_epochs: int = 1
    learning_rate: Optional[float] = None
    weight_decay: float = 0.01
    n_accumulate_grad: int = 16
    grad_clip_norm: float = 1.
    warmup_iters: int = 200

    save_trainer_state: Optional[bool] = None
    eval_interval: int = 500
    last_save_interval: Optional[int] = None
    last_max_checkpoint_num: int = 1
    best_max_checkpoint_num: int = 1
    logging_interval: int = 5
    tb_interval: int = 5

    def __post_init__(self):
        if self.sft_type == 'lora':
            if self.learning_rate is None:
                self.learning_rate = 1e-4
            if self.save_trainer_state is None:
                self.save_trainer_state = True
            if self.last_save_interval is None:
                self.last_save_interval = self.eval_interval
        elif self.sft_type == 'full':
            if self.learning_rate is None:
                self.learning_rate = 1e-5
            if self.save_trainer_state is None:
                self.save_trainer_state = False  # save disk space
            if self.last_save_interval is None:
                # Saving the model takes a long time
                self.last_save_interval = self.eval_interval * 4
        else:
            raise ValueError(f'sft_type: {self.sft_type}')

        if self.lora_target_modules is None:
            if self.model_type in {'baichuan-7b', 'baichuan-13b'}:
                self.lora_target_modules = ['W_pack']
            elif self.model_type == 'chatglm2':
                self.lora_target_modules = ['query_key_value']
            elif self.model_type == 'llama2-7b':
                self.lora_target_modules = ['q_proj', 'k_proj', 'v_proj']
            else:
                raise ValueError(f'model_type: {self.model_type}')


def parse_args() -> SftArguments:
    # return_remaining_strings=True for notebook compatibility
    args, remaining_args = HfArgumentParser([
        SftArguments
    ]).parse_args_into_dataclasses(return_remaining_strings=True)
    logger.info(f'args: {args}')
    if len(remaining_args) > 0:
        logger.warning(f'remaining_args: {remaining_args}')
    return args


def llm_sft(args: SftArguments) -> None:
    select_device(args.device)
    seed_everything(args.seed)

    # ### Loading Model and Tokenizer
    support_bf16 = torch.cuda.is_bf16_supported()
    if not support_bf16:
        logger.warning(f'support_bf16: {support_bf16}')
    model, tokenizer, model_dir = get_model_tokenizer(
        args.model_type, torch_dtype=torch.bfloat16)

    if args.gradient_checkpoint:
        # baichuan-13b does not implement the `get_input_embeddings` function
        if args.model_type == 'baichuan-13b':
            model.get_input_embeddings = MethodType(
                lambda self: self.model.embed_tokens, model)
        model.gradient_checkpointing_enable()
        model.enable_input_require_grads()

    # ### Preparing lora
    if args.sft_type == 'lora':
        lora_config = LoRAConfig(
            replace_modules=args.lora_target_modules,
            rank=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout_p)
        logger.info(f'lora_config: {lora_config}')
        Swift.prepare_model(model, lora_config)

    show_freeze_layers(model)
    print_model_info(model)
    # check the device and dtype of the model
    _p: Parameter = list(model.parameters())[-1]
    logger.info(f'device: {_p.device}, dtype: {_p.dtype}')

    # ### Loading Dataset
    tokenize_func = partial(tokenize_function, tokenizer=tokenizer)
    train_dataset, val_dataset = get_alpaca_en_zh_dataset(
        tokenize_func, split_seed=42, data_sample=args.data_sample)
    # Data analysis
    stat_dataset(train_dataset)
    stat_dataset(val_dataset)
    data_collator = partial(data_collate_fn, tokenizer=tokenizer)
    print_example(train_dataset[0], tokenizer)

    # ### Setting Config
    cfg_file = os.path.join(model_dir, 'configuration.json')

    T_max = get_T_max(
        len(train_dataset), args.batch_size, args.max_epochs, True)
    work_dir = get_work_dir(f'runs/{args.model_type}')
    config = Config({
        'train': {
            'dataloader': {
                'batch_size_per_gpu': args.batch_size,
                'workers_per_gpu': 1,
                'shuffle': True,
                'drop_last': True,
                'pin_memory': True
            },
            'max_epochs':
            args.max_epochs,
            'work_dir':
            work_dir,
            'optimizer': {
                'type': 'AdamW',
                'lr': args.learning_rate,
                'weight_decay': args.weight_decay,
                'options': {
                    'cumulative_iters': args.n_accumulate_grad,
                    'grad_clip': {
                        'norm_type': 2,
                        'max_norm': args.grad_clip_norm
                    }
                }
            },
            'lr_scheduler': {
                'type': 'CosineAnnealingLR',
                'T_max': T_max,
                'eta_min': args.learning_rate * 0.1,
                'options': {
                    'by_epoch': False,
                    'warmup': {
                        'type': 'LinearWarmup',
                        'warmup_ratio': 0.1,
                        'warmup_iters': args.warmup_iters
                    }
                }
            },
            'hooks': [
                {
                    'type': 'CheckpointHook',
                    'by_epoch': False,
                    'interval': args.last_save_interval,
                    'max_checkpoint_num': args.last_max_checkpoint_num,
                    'save_trainer_state': args.save_trainer_state
                },
                {
                    'type': 'EvaluationHook',
                    'by_epoch': False,
                    'interval': args.eval_interval
                },
                {
                    'type': 'BestCkptSaverHook',
                    'metric_key': 'loss',
                    'save_best': True,
                    'rule': 'min',
                    'max_checkpoint_num': args.best_max_checkpoint_num,
                    'save_trainer_state': args.save_trainer_state
                },
                {
                    'type': 'TextLoggerHook',
                    'by_epoch': True,  # Whether EpochBasedTrainer is used
                    'interval': args.logging_interval
                },
                {
                    'type': 'TensorboardHook',
                    'by_epoch': False,
                    'interval': args.tb_interval
                }
            ]
        },
        'evaluation': {
            'dataloader': {
                'batch_size_per_gpu': args.batch_size,
                'workers_per_gpu': 1,
                'shuffle': False,
                'drop_last': False,
                'pin_memory': True
            },
            'metrics': [{
                'type': 'my_metric',
                'vocab_size': tokenizer.vocab_size
            }]
        }
    })

    # ### Finetuning

    def cfg_modify_fn(cfg: Config) -> Config:
        cfg.update(config)
        return cfg

    device_kwargs = {}
    if torch.cuda.device_count() > 1:
        # No placement for model, leave the model to `device_map`
        device_kwargs['device'] = 'cpu'

    trainer = EpochBasedTrainer(
        model=model,
        cfg_file=cfg_file,
        data_collator=data_collator,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        remove_unused_data=True,
        seed=42,
        cfg_modify_fn=cfg_modify_fn,
        **device_kwargs,
    )

    trainer.train()

    # ### Visualization
    tb_dir = os.path.join(work_dir, 'tensorboard_output')
    plot_images(tb_dir, ['loss'], 0.9)


if __name__ == '__main__':
    args = parse_args()
    llm_sft(args)
