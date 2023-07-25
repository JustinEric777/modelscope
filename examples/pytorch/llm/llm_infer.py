# ### Setting up experimental environment.
from _common import *


@dataclass
class InferArguments:
    device: str = '0'  # e.g. '-1'; '0'; '0,1'
    model_type: str = field(
        default='baichuan-7b',
        metadata={
            'choices':
            ['baichuan-7b', 'baichuan-13b', 'chatglm2', 'llama2-7b']
        })
    sft_type: str = field(
        default='lora', metadata={'choices': ['lora', 'full']})
    ckpt_fpath: str = '/path/to/your/iter_xxx.pth'
    eval_human: bool = False  # False: eval test_dataset
    data_sample: Optional[int] = None
    # sft_type: lora
    lora_target_modules: Optional[List[str]] = None
    lora_rank: int = 8
    lora_alpha: int = 32
    lora_dropout_p: float = 0.1

    max_new_tokens: int = 512
    temperature: float = 0.9
    top_k: int = 50
    top_p: float = 0.9

    def __post_init__(self):
        if self.lora_target_modules is None:
            if self.model_type in {'baichuan-7b', 'baichuan-13b'}:
                self.lora_target_modules = ['W_pack']
            elif self.model_type == 'chatglm2':
                self.lora_target_modules = ['query_key_value']
            elif self.model_type == 'llama2-7b':
                self.lora_target_modules = ['q_proj', 'k_proj', 'v_proj']
            else:
                raise ValueError(f'model_type: {self.model_type}')

        if not os.path.isfile(self.ckpt_fpath):
            raise ValueError(f'Please enter a valid fpath: {self.ckpt_fpath}')


def parse_args() -> InferArguments:
    # return_remaining_strings=True for notebook compatibility
    args, remaining_args = HfArgumentParser([
        InferArguments
    ]).parse_args_into_dataclasses(return_remaining_strings=True)
    logger.info(f'args: {args}')
    if len(remaining_args) > 0:
        logger.warning(f'remaining_args: {remaining_args}')
    return args


def llm_infer(args: InferArguments) -> None:
    select_device(args.device)
    # ### Loading Model and Tokenizer
    support_bf16 = torch.cuda.is_bf16_supported()
    if not support_bf16:
        logger.warning(f'support_bf16: {support_bf16}')
    model, tokenizer, _ = get_model_tokenizer(
        args.model_type, torch_dtype=torch.bfloat16)

    # ### Preparing lora
    if args.sft_type == 'lora':
        lora_config = LoRAConfig(
            replace_modules=args.lora_target_modules,
            rank=args.lora_rank,
            lora_alpha=args.lora_alpha,
            lora_dropout=args.lora_dropout_p,
            pretrained_weights=args.ckpt_fpath)
        logger.info(f'lora_config: {lora_config}')
        Swift.prepare_model(model, lora_config)
    elif args.sft_type == 'full':
        state_dict = torch.load(args.ckpt_fpath, map_location='cpu')
        model.load_state_dict(state_dict)
    else:
        raise ValueError(f'args.sft_type: {args.sft_type}')

    # ### Inference
    streamer = TextStreamer(
        tokenizer, skip_prompt=True, skip_special_tokens=True)
    generation_config = GenerationConfig(
        max_new_tokens=args.max_new_tokens,
        temperature=args.temperature,
        top_k=args.top_k,
        top_p=args.top_p,
        do_sample=True,
        pad_token_id=tokenizer.eos_token_id)
    logger.info(f'generation_config: {generation_config}')

    if args.eval_human:
        while True:
            instruction = input('<<< ')
            data = {'instruction': instruction, 'input': None, 'output': None}
            inference(data, model, tokenizer, streamer, generation_config)
            print('-' * 80)
    else:
        _, test_dataset = get_alpaca_en_zh_dataset(
            None, True, split_seed=42, data_sample=args.data_sample)
        mini_test_dataset = test_dataset.select(range(10))
        for data in mini_test_dataset:
            output = data['output']
            data['output'] = None
            inference(data, model, tokenizer, streamer, generation_config)
            print()
            print(f'[LABELS]{output}')
            print('-' * 80)
            # input('next[ENTER]')


if __name__ == '__main__':
    args = parse_args()
    llm_infer(args)
