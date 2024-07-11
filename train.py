import os
import sys
import logging
from subprocess import Popen
import threading
from time import sleep
import sys

logging.basicConfig(level=logging.DEBUG)

expName = ""
sampleRate = 48000
if_f0_3 = True
version19 = "v2"
np7 = 7
trainset_dir4 = ""

# read expName from command line
if len(sys.argv) < 3:
    logging.fatal("Usage: python train.py <expName> <trainset_dir>")
    sys.exit(1)

expName = sys.argv[1]
trainset_dir4 = sys.argv[2]

if expName == "" or trainset_dir4 == "":
    logging.fatal("Usage: python train.py <expName> <trainset_dir>")
    sys.exit(1)


def if_done(done, p):
    while 1:
        if p.poll() is None:
            sleep(0.5)
        else:
            break
    done[0] = True


def preprocess_dataset(trainset_dir, exp_dir, sr, n_p):
    now_dir = os.getcwd()
    logging.debug("Current dir: " + now_dir)
    os.makedirs("%s/logs/%s" % (now_dir, exp_dir), exist_ok=True)
    f = open("%s/logs/%s/preprocess.log" % (now_dir, exp_dir), "w")
    f.close()
    cmd = '"%s" infer/modules/train/preprocess.py "%s" %s %s "%s/logs/%s" %s %.1f' % (
        "python",
        trainset_dir,
        sr,
        n_p,
        now_dir,
        exp_dir,
        False,  # TODO: is this correct?
        3.7,  # TODO: is this correct?
    )
    logging.info("Execute: " + cmd)
    # , stdin=PIPE, stdout=PIPE,stderr=PIPE,cwd=now_dir
    p = Popen(cmd, shell=True)
    # 煞笔gr, popen read都非得全跑完了再一次性读取, 不用gr就正常读一句输出一句;只能额外弄出一个文本流定时读
    done = [False]
    threading.Thread(
        target=if_done,
        args=(
            done,
            p,
        ),
    ).start()
    while 1:
        with open("%s/logs/%s/preprocess.log" % (now_dir, exp_dir), "r") as f:
            yield (f.read())
        sleep(1)
        if done[0]:
            break
    with open("%s/logs/%s/preprocess.log" % (now_dir, exp_dir), "r") as f:
        log = f.read()
    logging.info(log)
    yield log


def main():
    preprocess_dataset(trainset_dir4, expName, sampleRate, np7)
    logging.info("Preprocess done.")

main()
