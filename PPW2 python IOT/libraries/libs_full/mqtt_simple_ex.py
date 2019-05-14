import ustruct as struct
from umqtt.simple import MQTTClient


class MQTTClientEx(MQTTClient):
    def unsubscribe(self, topic):
        pkt = bytearray(b"\xA2\0\0\0")
        self.pid += 5
        struct.pack_into("!BH", pkt, 1, 2 + 2 + len(topic), self.pid)
        self.sock.write(pkt)
        self._send_str(topic)
        while 1:
            op = self.wait_msg()
            if op == 0xB0:
                resp = self.sock.read(3)
                assert resp[1] == pkt[2] and resp[2] == pkt[3]
                return
