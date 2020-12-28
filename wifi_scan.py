from jnius import autoclass, cast
from kivymd.app import MDApp
from kivy.lang import Builder
from android.broadcast import BroadcastReceiver
from android.permissions import request_permissions, Permission
mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
Context = autoclass('android.content.Context')
WifiManager = autoclass('android.net.wifi.WifiManager')


KV = '''
BoxLayout:
    orientation: 'vertical'
    MDLabel:
        id: lbl
        text: ''
        halign: 'center'
    BoxLayout
        size_hint_y: .1
        MDRaisedButton:
            text: 'start scan'
            size_hint_x: .5
            on_release:
                app.start_scan()
        MDRaisedButton:
            text: 'stop scan'
            size_hint_x: .5
            on_release:
                app.stop_scan()
'''


class Application(MDApp):
    results = set()
    wifi = None
    br = None

    def build(self):

        return Builder.load_string(KV)

    def register_broadcats_receiver(self):
        if not self.br:
            self.br = BroadcastReceiver(
                self.on_broadcast, actions=['SCAN_RESULTS_AVAILABLE_ACTION'])
            self.br.start()

    def on_broadcast(self, context, intent):
        success = intent.getBooleanExtra(
            WifiManager.EXTRA_RESULTS_UPDATED, False)

        if success:
            self.scan_success()
        else:
            self.scan_failure()

    def start_scan(self):

        self.register_broadcats_receiver()
        context = mActivity.getApplicationContext()
        wifiManager = cast(
            WifiManager, context.getSystemService(Context.WIFI_SERVICE))

        self.wifi = wifiManager
        success = self.wifi.startScan()
        if not success:
            self.scan_failure()

    def scan_success(self):
        self.root.ids.lbl.text = ''
        if not self.wifi:
            return

        results = self.wifi.getScanResults()

        for i in range(results.size()):
            result = results.get(i)
            self.results.add(result)
            self.root.ids.lbl.text += f'{result.SSID}\n'

    def on_start(self):
        self.register_broadcats_receiver()
        request_permissions([Permission.ACCESS_FINE_LOCATION])

    def on_resume(self):
        self.register_broadcats_receiver()

    def on_pause(self):
        self.stop_scan()
        return True

    def stop_scan(self):
        if self.br:
            self.br.stop()
            self.br = None
        self.root.ids.lbl.text = ''

    def scan_failure(self):
        if self.results:
            for result in self.results:
                self.root.ids.lbl.text += f'{result}\n'
        else:
            self.root.ids.lbl.text = 'something went wrong'
        self.stop_scan()


if __name__ == "__main__":
    app = Application()
    app.run()
