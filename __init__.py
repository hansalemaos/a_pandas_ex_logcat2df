import os
import random
import subprocess
from typing import Union

import numpy as np
import keyboard as keyboard__
import kthread
import psutil
import pandas as pd
from time import sleep


def execute_multicommands_adb_shell_bin(
    adb_path,
    device_serial,
    subcommands: list,
    exit_keys: str = "ctrl+x",
    print_output=True,
    timeout=None,
):
    if not isinstance(subcommands, list):
        subcommands = [subcommands]
    return _execute_adb_command_bin(
        cmd=f"{adb_path} -s {device_serial} shell",
        subcommands=subcommands,
        exit_keys=exit_keys,
        end_of_printline="",
        print_output=print_output,
        timeout=timeout,
    )


def _execute_adb_command_bin(
    cmd: str,
    subcommands: list,
    exit_keys: str = "ctrl+x",
    end_of_printline: str = "",
    print_output=True,
    timeout=None,
) -> list:
    if isinstance(subcommands, str):
        subcommands = [subcommands]
    elif isinstance(subcommands, tuple):
        subcommands = list(subcommands)
    popen = None
    t = None

    def run_subprocess(cmd):
        nonlocal t
        nonlocal popen

        def killer():
            sleep(timeout)
            kill_process()

        def kill_process():
            nonlocal popen
            try:
                print("Killing the process")
                p = psutil.Process(popen.pid)
                p.kill()
                try:
                    if exit_keys in keyboard__.__dict__["_hotkeys"]:
                        keyboard__.remove_hotkey(exit_keys)
                except Exception:
                    try:
                        keyboard__.unhook_all_hotkeys()
                    except Exception:
                        pass
            except Exception:
                try:
                    keyboard__.unhook_all_hotkeys()
                except Exception:
                    pass

        if exit_keys not in keyboard__.__dict__["_hotkeys"]:
            keyboard__.add_hotkey(exit_keys, kill_process)

        DEVNULL = open(os.devnull, "wb")
        try:
            popen = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                universal_newlines=False,
                stderr=DEVNULL,
                shell=False,
            )

            for subcommand in subcommands:
                if isinstance(subcommand, str):
                    subcommand = subcommand.rstrip("\n") + "\n"

                    subcommand = subcommand.encode()
                else:
                    subcommand = subcommand.rstrip(b"\n") + b"\n"

                popen.stdin.write(subcommand)

            popen.stdin.close()

            if timeout is not None:
                t = kthread.KThread(
                    target=killer, name=str(random.randrange(1, 100000000000))
                )
                t.start()

            for stdout_line in iter(popen.stdout.readline, b""):
                try:
                    yield stdout_line
                except Exception as Fehler:
                    continue
            popen.stdout.close()
            return_code = popen.wait()
        except Exception as Fehler:
            print(Fehler)
            try:
                popen.stdout.close()
                return_code = popen.wait()
            except Exception as Fehler:
                yield ""

    proxyresults = []
    try:
        for proxyresult in run_subprocess(cmd):
            proxyresults.append(proxyresult)
            if print_output:
                try:
                    print(f"{proxyresult!r}", end=end_of_printline)
                    print("")
                except Exception:
                    pass
    except KeyboardInterrupt:
        try:
            p = psutil.Process(popen.pid)
            p.kill()
            popen = None
        except Exception as da:
            print(da)

    try:
        if popen is not None:
            p = psutil.Process(popen.pid)
            p.kill()
    except Exception as da:
        pass

    try:
        if exit_keys in keyboard__.__dict__["_hotkeys"]:
            keyboard__.remove_hotkey(exit_keys)
    except Exception:
        try:
            keyboard__.unhook_all_hotkeys()
        except Exception:
            pass
    try:
        t.kill()
    except Exception:
        pass
    return proxyresults


def connect_to_adb(adb_path, deviceserial):
    _ = subprocess.run(f"{adb_path} start-server", capture_output=True, shell=False)
    _ = subprocess.run(
        f"{adb_path} connect {deviceserial}", capture_output=True, shell=False
    )


def adb_logcat_to_df(
    adb_path: str,
    deviceserial: str,
    exit_keys: str = "ctrl+x",
    timeout: Union[int, None, float] = None,
) -> pd.DataFrame:
    connect_to_adb(adb_path, deviceserial)
    xx = execute_multicommands_adb_shell_bin(
        adb_path,
        deviceserial,
        ["logcat -b all -c", "logcat threadtime -b all -v printable"],
        exit_keys=exit_keys,
        timeout=timeout,
    )
    dfax = pd.DataFrame(
        [x.strip().decode("utf-8", "replace").split(maxsplit=5) for x in xx]
    )
    dfax = dfax.dropna().reset_index(drop=True)
    dfloggi = dfax[5].str.extractall(r"(^[^:]+:)([^:]+:)?(.*)$").reset_index(drop=True)
    for col in dfloggi:
        dfloggi[col] = dfloggi[col].str.strip(": ")

    dfax.columns = ["bb_day", "aa_time", "aa_pid", "aa_tid", "aa_tag", "aa_whole_log"]
    dfloggi.columns = ["aa_log_1", "aa_log_2", "aa_log_3"]
    dfloga = pd.concat([dfloggi, dfax], axis=1).copy()
    df = dfloga.filter(list(sorted(dfloga.columns))).copy()
    df.aa_log_1 = df.aa_log_1.astype("category")
    df.aa_log_2 = df.aa_log_2.astype("string")
    df.aa_log_3 = df.aa_log_3.astype("string")
    df.aa_pid = df.aa_pid.astype(np.uint32)
    df.aa_tag = df.aa_tag.astype("category")
    df.aa_tid = df.aa_tid.astype(np.uint32)
    df.aa_whole_log = df.aa_whole_log.astype("string")
    df.bb_day = df.bb_day.astype("category")

    return dfloga


def pd_add_adb_logcat_to_df():
    pd.Q_logcat2df = adb_logcat_to_df
