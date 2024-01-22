# coding=utf-8
from __future__ import absolute_import

### (Don't forget to remove me)
# This is a basic skeleton for your plugin's __init__.py. You probably want to adjust the class name of your plugin
# as well as the plugin mixins it's subclassing from. This is really just a basic skeleton to get you started,
# defining your plugin as a template plugin, settings and asset plugin. Feel free to add or remove mixins
# as necessary.
#
# Take a look at the documentation on what other plugin mixins are available.

import octoprint.plugin

class NotifyPlugin(
    octoprint.plugin.SettingsPlugin,
    octoprint.plugin.EventHandlerPlugin,
    octoprint.plugin.TemplatePlugin
):

    def __init__(self):
        self._sub_plugins = dict()

    def register_plugin(self, implementation):
        key = self._get_plugin_key(implementation)

        self._logger.debug(f"Registering plugin: {key}")

        if key not in self._sub_plugins:
            self._logger.info(f"Registered plugin: {key}")
            self._sub_plugins[key] = implementation
        else:
        self._logger.debug(f"Plugin already registered: {key}")

    def do_notify(self, **kwargs):
        plugin = self.config['plugin']
        result = False

        if plugin not in self._sub_plugins:
            self._logger.error(f"Plugin {plugin} is configured for notification but it is not registered.")
        elif not hasattr(self._sub_plugins[plugin], 'notify'):
            self._logger.error(f"Plugin {plugin} is configured for notification but notify is not defined.")
        else:
            callback = self._sub_plugins[plugin].notify
            try:
                result = callback(**kwargs)
            except Exception:
                self._logger.exception(
                    f"Error while executing callback {callback}",
                    extra={"callback": fqfn(callback)},
                )
            self._logger.debug(f"Result: ${result}")

    ##~~ EventHandlerPlugin mixin
    def on_event(self, event, payload):
        _events = list(Events.Z_CHANGE, Events.CONNECTING, Events.CONNECTED, Events.DISCONNECTING, Events.DISCONNECTED, Events.UPLOAD, Events.FILE_SELECTED, Events.FILE_DESELECTED, Events.UPDATED_FILES)
        if event in _events:
            self._logger.info(f"Event {event} occurred, sending notification!")
            notify_options = dict(
                title = event,
                message = 'Z value (height) of printer has changed',
                event = event
            )
            self.do_notify(notify_options)
            return

    ##~~ SettingsPlugin mixin
    def get_settings_defaults(self):
        return dict(
            plugin = None,
        )

    ##~~ AssetPlugin mixin
    def get_assets(self):
        # Define your plugin's asset files to automatically include in the
        # core UI here.
        return {
            "js": ["js/notify.js"],
            "css": ["css/notify.css"],
            "less": ["less/notify.less"]
        }

    ##~~ TemplatePlugin mixin
    def get_template_vars(self):
        available_plugins = []
        for key in list(self._sub_plugins.keys()):
            _plugin = dict(
                pluginIdentifier=key,
                displayName=self._plugin_manager.plugins[key].name
            )
            available_plugins.append(_plugin)

        return {
            "availablePlugins": available_plugins,
        }

    def get_template_configs(self):
        return [
            dict(type="settings", custom_bindings=True)
        ]

    ##~~ Softwareupdate hook
    def get_update_information(self):
        # Define the configuration for your plugin to use with the Software Update
        # Plugin here. See https://docs.octoprint.org/en/master/bundledplugins/softwareupdate.html
        # for details.
        return {
            "notify": {
                "displayName": "Notify Plugin",
                "displayVersion": self._plugin_version,

                # version check: github repository
                "type": "github_release",
                "user": "edekeijzer",
                "repo": "OctoPrint-Notify",
                "current": self._plugin_version,

                # update method: pip
                "pip": "https://github.com/edekeijzer/OctoPrint-Notify/archive/{target_version}.zip",
            }
        }


# If you want your plugin to be registered within OctoPrint under a different name than what you defined in setup.py
# ("OctoPrint-PluginSkeleton"), you may define that here. Same goes for the other metadata derived from setup.py that
# can be overwritten via __plugin_xyz__ control properties. See the documentation for that.
__plugin_name__ = "Notify Plugin"


# Set the Python version your plugin is compatible with below. Recommended is Python 3 only for all new plugins.
# OctoPrint 1.4.0 - 1.7.x run under both Python 3 and the end-of-life Python 2.
# OctoPrint 1.8.0 onwards only supports Python 3.
__plugin_pythoncompat__ = ">=3,<4"  # Only Python 3

def __plugin_load__():
    global __plugin_implementation__
    __plugin_implementation__ = NotifyPlugin()

    global __plugin_hooks__
    __plugin_hooks__ = {
        "octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
    }

    __plugin_helpers__ = dict(
        register_plugin = __plugin_implementation__.register_plugin
    )
