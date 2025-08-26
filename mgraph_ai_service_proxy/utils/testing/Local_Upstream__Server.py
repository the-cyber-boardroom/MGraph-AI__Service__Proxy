import threading
from http.server                                                    import HTTPServer
from time                                                           import sleep
from osbot_utils.type_safe.Type_Safe                                import Type_Safe
from osbot_utils.type_safe.primitives.safe_str.web.Safe_Str__Url    import Safe_Str__Url
from osbot_utils.type_safe.primitives.safe_uint.Safe_UInt           import Safe_UInt
from osbot_utils.utils.Misc                                         import random_port
from mgraph_ai_service_proxy.schemas.http.Safe_Str__Http__Host      import Safe_Str__Http__Host
from mgraph_ai_service_proxy.utils.testing.Local_Upstream__Handler  import Local_Upstream__Handler


class Local_Upstream__Server(Type_Safe):                       # Wrapper for managing mock server lifecycle
    server       : HTTPServer              = None            # HTTP server instance
    thread       : threading.Thread        = None            # Server thread
    port         : Safe_UInt               = None            # Server port
    host         : Safe_Str__Http__Host    ="localhost"      # Server host
    is_running   : bool                    = False           # Running state

    def start(self) -> 'Local_Upstream__Server':               # Start the mock server
        self.port          = Safe_UInt(random_port())
        self.server        = HTTPServer((str(self.host), int(self.port)), Local_Upstream__Handler)
        self.thread        = threading.Thread(target=self.server.serve_forever)
        self.thread.daemon = True
        self.thread.start()

        self.is_running = True
        sleep(0.1)                                                                    # Allow server to start todo: use the osbot-utils 'is port/http open' methods to speed this up
        return self

    def stop(self) -> 'MockUpstreamServer':                                           # Stop the mock server
        if self.server:
            self.server.shutdown()
            self.server.server_close()

        if self.thread:
            self.thread.join(timeout=5)

        self.is_running = False
        return self

    def url(self, path: str = "") -> Safe_Str__Url:                                   # Get server URL
        return Safe_Str__Url(f"http://{self.host}:{self.port}{path}")
