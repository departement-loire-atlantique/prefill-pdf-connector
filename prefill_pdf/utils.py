import logging
import os
import subprocess
import tempfile

log = logging.getLogger(__name__)

if os.getenv("PDFTK_PATH"):
    PDFTK_PATH = os.getenv("PDFTK_PATH")
else:
    PDFTK_PATH = "/usr/bin/pdftk"
    if not os.path.isfile(PDFTK_PATH):
        PDFTK_PATH = "pdftk"


def check_output(*popenargs, **kwargs):
    if "stdout" in kwargs:
        raise ValueError("stdout argument not allowed, it will be overridden.")
    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        raise subprocess.CalledProcessError(retcode, cmd, output=output)
    return output


def run_command(command, shell=False):
    """run a system command and yield output"""
    p = check_output(command, shell=shell)
    return p.decode("utf-8").splitlines()


try:
    run_command([PDFTK_PATH])
except OSError:
    logging.warning("pdftk test call failed (PDFTK_PATH=%r).", PDFTK_PATH)


def fill_form(pdf_path, xfdf_data="", out_file=None, flatten=True, drop_xfa=False, tmp_dir=None):
    """
    Fills a PDF form with given XFDF input data.
    Return temp file if no out_file provided.
    """
    cleanOnFail = False
    tmp_fdf = gen_xfdf_file(xfdf_data)
    handle = None
    if not out_file:
        cleanOnFail = True
        handle, out_file = tempfile.mkstemp(dir=tmp_dir)

    cmd = "%s %s fill_form %s output %s" % (PDFTK_PATH, pdf_path, tmp_fdf, out_file)
    if flatten:
        cmd += " flatten"
    if drop_xfa:
        cmd += " drop_xfa"
    try:
        run_command(cmd, True)
    except:
        if cleanOnFail:
            os.remove(tmp_fdf)
        raise
    finally:
        if handle:
            os.close(handle)
    os.remove(tmp_fdf)
    return out_file


def gen_xfdf_file(xfdf_data, tmp_dir=None):
    """Generates a temp XFDF file suited for fill_form function, based on XFDF input data"""
    handle, out_file = tempfile.mkstemp(dir=tmp_dir)
    f = os.fdopen(handle, "wb")
    f.write((xfdf_data.encode("UTF-8")))
    f.close()
    return out_file
