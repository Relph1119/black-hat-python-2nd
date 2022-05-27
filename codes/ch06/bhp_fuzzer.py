#!/usr/bin/env python
# encoding: utf-8
"""
@file: bhp_fuzzer.py
@time: 2022/5/24 19:55
@project: black-hat-python-2ed
@desc: P115 Burp模糊测试插件
"""
import random

from burp import IBurpExtender, IIntruderPayloadGenerator
from burp import IIntruderPayloadGeneratorFactory


class BurpExtender(IBurpExtender, IIntruderPayloadGeneratorFactory):
    def registerExtenderCallbacks(self, callbacks):  # type: (IBurpExtenderCallbacks) -> None
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()

        callbacks.registerIntruderPayloadGeneratorFactory(self)
        return

    def getGeneratorName(self):  # type: () -> str
        """
        返回载荷生成器的名字
        :return:
        """
        return "BHP Payload Generator"

    def createNewInstance(self, attack):  # type: (IIntruderAttack) -> IIntruderPayloadGenerator
        """
        读取攻击参数，返回实例
        :param attack:
        :return:
        """
        return BHPFuzzer(self, attack)


class BHPFuzzer(IIntruderPayloadGenerator):
    def __init__(self, extender, attack):
        self._extender = extender
        self._helpers = extender._helpers
        self._attack = attack
        # 控制模糊测试结束的时间
        self.max_payloads = 10
        self.num_iterations = 0

        return

    def hasMorePayloads(self):  # type: () -> bool
        """
        检查最大测试次数
        :return:
        """
        if self.num_iterations == self.max_payloads:
            return False
        else:
            return True

    def getNextPayload(self, current_payload):  # type: (array) -> array
        payload = "".join(chr(x) for x in current_payload)

        payload = self.mutate_payload(payload)

        self.num_iterations += 1
        return payload

    def reset(self):  # type: () -> None
        self.num_iterations = 0
        return

    def mutate_payload(self, original_payload):
        """
        模糊测试函数
        :param original_payload:
        :return:
        """
        picker = random.randint(1, 3)

        offset = random.randint(0, len(original_payload) - 1)

        # 将载荷数据随机切分
        front, back = original_payload[:offset], original_payload[offset:]
    
        if picker == 1:
            front += "'"
        elif picker == 2:
            front += "<script>alert('BHP!');</script>"
        elif picker == 3:
            chunk_length = random.randint(0, len(back) - 1)
            repeater = random.randint(1, 10)
            for _ in range(repeater):
                front += original_payload[:offset + chunk_length]

        return front + back

