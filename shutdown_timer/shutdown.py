import logging
import subprocess

log = logging.getLogger(__name__)

DBUS_BUS = "org.freedesktop.login1"
DBUS_PATH = "/org/freedesktop/login1"
DBUS_IFACE = "org.freedesktop.login1.Manager"


def shutdown():
    """Trigger system shutdown via systemd-logind D-Bus (no password on active session)."""
    try:
        import dbus

        bus = dbus.SystemBus()
        obj = bus.get_object(DBUS_BUS, DBUS_PATH)
        iface = dbus.Interface(obj, DBUS_IFACE)
        iface.PowerOff(True)
        log.info("Shutdown initiated via D-Bus")
    except ImportError:
        log.warning("dbus-python not available, falling back to systemctl")
        subprocess.run(["systemctl", "poweroff"], check=False)
    except Exception as e:
        log.error("D-Bus shutdown failed (%s), falling back to systemctl", e)
        try:
            subprocess.run(["systemctl", "poweroff"], check=False)
        except Exception as e2:
            log.error("systemctl fallback also failed: %s", e2)
