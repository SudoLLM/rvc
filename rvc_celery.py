import os

import scipy

from configs.config import Config
from infer.modules.vc.modules import VC
from mcelery.cos import cos_local, download_cos_file, get_local_path, upload_cos_file
from mcelery.infer import celery_app, register_infer_tasks

# rewrite env
os.environ["weight_root"] = str(cos_local)
os.environ["index_root"] = str(cos_local)
os.environ["rmvpe_root"] = "assets/rmvpe"

rvc = VC(Config(parse_arg=False))


@celery_app.task(name="rvc_infer", queue="rvc_infer")
def rvc_infer_task(audio_cos: str, index_cos: str, model_cos: str, pitch: int, output_cos: str) -> str:
    audio_path = download_cos_file(audio_cos)
    index_path = download_cos_file(index_cos)
    # 不需要显式传递 model_path, 因为 get_vc 会拼接 weight_root / model_cos
    _ = download_cos_file(model_cos)
    rvc.get_vc(model_cos)
    _, wav_opt = rvc.vc_single(
        sid=0,
        input_audio_path=str(audio_path),
        f0_up_key=pitch,
        f0_file=None,
        f0_method="rmvpe",
        file_index=str(index_path),
        file_index2=None,
        index_rate=0.75,
        filter_radius=3,
        resample_sr=0,
        rms_mix_rate=0.25,
        protect=0.33,
    )
    output_path = get_local_path(output_cos)
    scipy.io.wavfile.write(filename=output_path, rate=wav_opt[0], data=wav_opt[1])
    upload_cos_file(output_cos)
    return output_cos


register_infer_tasks()
