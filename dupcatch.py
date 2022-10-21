import mlfiles
import dupcatch_subs
import sys

mlfiles.settings_file()
dupcatch_subs.help(sys.argv)
# from importlib import reload
# reload(mlfiles)
# reload(mltext)
# reload(dupcatch_subs)
# reload(anki_functions)
# reload(mlfiles)
# reload(mlscraping)
# reload(general_functions)

if "-r" in sys.argv:
    mlfiles.update_log("-------------------------------------------------------------------")
    mlfiles.update_log(" ")
    mlfiles.update_log("STARTING DUPLICATES RUN")
    mlfiles.update_log("-------------------------------------------------------------------")
    mlfiles.update_log("-------------------------------------------------------------------")
    try:
        dupcatch_subs.run_duplicate_finder()
    except Exception as e:
        mlfiles.log_exception(e)


if "-m" in sys.argv:
    mlfiles.update_log("-------------------------------------------------------------------")
    mlfiles.update_log(" ")
    mlfiles.update_log("STARTING MERGING RUN")
    mlfiles.update_log("-------------------------------------------------------------------")
    mlfiles.update_log("-------------------------------------------------------------------")
    try:
        dupcatch_subs.run_merge()
    except Exception as e:
        mlfiles.log_exception(e)
