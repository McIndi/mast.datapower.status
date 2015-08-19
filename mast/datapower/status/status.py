import os
import flask
from mast.logging import make_logger, logged
from time import sleep
from mast.timestamp import Timestamp
from mast.xor import xordecode, xorencode
from mast.datapower import datapower

PROVIDER_MAP = ({
    "CPUUsage.tenSeconds": datapower.STATUS_XPATH + '/CPUUsage/tenSeconds',
    "TCPSummary.established": datapower.STATUS_XPATH + '/TCPSummary/established',
    "MemoryStatus.Usage": datapower.STATUS_XPATH + '/MemoryStatus/Usage',
    "FilesystemStatus.FreeTemporary": datapower.STATUS_XPATH + 'FilesystemStatus/FreeTemporary',
    "FilesystemStatus.FreeEncrypted": datapower.STATUS_XPATH + 'FilesystemStatus/FreeEncrypted',
    "FilesystemStatus.FreeInternal": datapower.STATUS_XPATH + 'FilesystemStatus/FreeInternal',
    "SystemUsage.Load": datapower.STATUS_XPATH + 'SystemUsage/Load',
    "SystemUsage.WorkList": datapower.STATUS_XPATH + 'SystemUsage/WorkList'
    })

mast_home = os.environ["MAST_HOME"]


@logged("mast.datapower.status")
def get_data_file(f):
    _root = os.path.dirname(__file__)
    path = os.path.join(_root, "data", f)
    with open(path, "rb") as fin:
        return fin.read()


from mast.plugins.web import Plugin
import mast.plugin_utils.plugin_functions as pf
from functools import partial, update_wrapper

class WebPlugin(Plugin):
    def __init__(self):
        logger = make_logger("mast.status")
        global mast_home
        logger.debug("found MAST_HOME: {}".format(mast_home))
        self.route = self.status

        config_file = os.path.join(
            mast_home,
            "etc",
            "default",
            "status.conf")
        if not os.path.exists(config_file):
            logger.debug("Config file doesn't exist creating default config")
            with open(config_file, "w") as fout:
                fout.write(get_data_file("plugin.conf"))



    def css(self):
        return get_data_file("plugin.css")

    def js(self):
        return get_data_file("plugin.js")

    def html(self):
        return get_data_file("plugin.html")

    @logged("mast.datapower.status")
    def status(self):
        logger = make_logger("mast.datapower.status")

        t = Timestamp()
        appliances = flask.request.form.getlist('appliances[]')
        logger.debug("Appliances: {}".format(str(appliances)))
        credentials = [xordecode(_, key=xorencode(
                              flask.request.cookies["9x4h/mmek/j.ahba.ckhafn"]))
                          for _ in flask.request.form.getlist('credentials[]')]
        if not appliances:
            return flask.abort(404)
        # TODO: make this an option
        env = datapower.Environment(appliances, credentials, check_hostname=False)

        providers = flask.request.form.getlist("providers[]")
        logger.debug("Providers: {}".format(str(providers)))

        resp = {
            "appliances": appliances,
            "time": t.short}

        for provider in providers:
            _provider = provider.split(".")[0]
            resp[provider] = []
            for appliance in env.appliances:
                logger.debug(
                    "Checking {} on {}".format(
                        _provider,
                        appliance.hostname))
                try:
                    _status = appliance.get_status(_provider)
                except datapower.AuthenticationFailure:
                    # This is to handle an intermittent authentication failure
                    # sometimes issued by the DataPower. We will sleep 2 seconds
                    # and try again
                    sleep(2)
                    try:
                        return self.status()
                    except:
                        logger.exception(
                            "An unhandled exception occurred during execution")
                        raise
                except:
                    logger.exception(
                        "An unhandled exception occurred during execution")
                    raise
                metric = _status.xml.find(PROVIDER_MAP[provider]).text
                resp[provider].append(metric)
        return flask.jsonify(resp)

