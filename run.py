import argparse
import requests
import hashlib
import os
import subprocess

import api

def parse_args():
    parser = argparse.ArgumentParser(description="MinecraftOnly instance runner")

    parser.add_argument("-u", "--username", required = True)
    parser.add_argument("-p", "--password", required = True)
    parser.add_argument("-m", "--modpack",  required = True)
    parser.add_argument("-j", "--java",  help="path to java binary(default: java)", default="java")
    parser.add_argument("-M", "--memory", type=int, help="amount of memory given for minecraft(in megabytes, default: 4096)")

    return parser.parse_args()

def main(args):
    base_path = os.path.abspath(args.modpack + "_instance")

    try:
        open(os.path.join(base_path, "bin", "minecraft.jar")).close()
    except FileNotFoundError:
        print(f"Instance \"{args.modpack}\" is not valid or unsupported")
        return

    server = api.get_server(args.modpack)
    session = api.get_session(args.username, args.password, server)

    # FIXME: those argruments is 1.7.10-specific, need to add selection of arguments based on modpack launch type.
    # list of launch types is available here: http://auth.mconly.net/launcher/launch-types.conf

    launch_args = [
        args.java,
        f"-Xmx{args.memory}m",
        "-Dorg.lwjgl.opengl.Display.allowSoftwareOpenGL=true",
        "-Djava.net.preferIPv4Stack=true",
        "-Dfml.ignoreInvalidMinecraftCertificates=true",
        "-Dfml.ignorePatchDiscrepancies=true",
        "-Djava.net.useSystemProxies=true",
        "-Djava.library.path=bin/natives",
        "-cp", "bin/minecraft.jar",
        "net.minecraft.launchwrapper.Launch",

        "--gameDir", base_path,
        "--tweakClass", "cpw.mods.fml.common.launcher.FMLTweaker",
        "--tweakClass", "com.mumfrey.liteloader.launch.LiteLoaderTweaker", # FIXME: liteloader is not always required
        "--version", "1.7.10",
        "--accessToken", "FML",
        "--userProperties", "{}",
        "--assetsDir", "./assets",
        "--assetIndex", "1.7.10",
    ]

    subprocess.run(launch_args, cwd = base_path, input="\n".join([f"{k}:{v}" for k,v in {
        "username": session.username,
        "session": session.session,
    }.items()] + ["initEnd"]).encode())



if __name__ == "__main__":
    args = parse_args()
    main(args)
