from app.platform.dapr import DaprPlatform
from app.platform.interface import PlatformInterface

def get_platform() -> PlatformInterface:
    # FIXME: Implement a platform factory to return the appropriate platform based on the environment
    return DaprPlatform()
