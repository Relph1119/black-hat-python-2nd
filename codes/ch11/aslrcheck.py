#!/usr/bin/env python
# encoding: utf-8
"""
@file: aslrcheck.py
@time: 2022/5/27 11:31
@project: black-hat-python-2ed
@desc: P210 查找ASLR（地址空间布局随机化）保护进程
"""
import io
import logging
from typing import Callable, List

import pefile
from volatility.framework import constants, exceptions, interfaces, renderers
from volatility.framework.configuration import requirements
from volatility.framework.renderers import format_hints
from volatility.framework.symbols import intermed
from volatility.framework.symbols.windows import extensions
from volatility.plugins.windows import pslist

vollog = logging.getLogger(__name__)

IMAGE_DLL_CHARACTERISTICS_DYNAMIC_BASE = 0x0040
IMAGE_FILE_RELOCS_STRIPPED = 0x0001


def check_aslr(pe):
    pe.parse_data_directories([pefile.DIRECTORY_ENTRY['IMAGE_DIRECTORY_ENTRY_LOAD_CONFIG']])
    dynamic = False
    stripped = False

    # 检查是否采用DYNAMIC模式编译
    if pe.OPTIONAL_HEADER.DllCharacteristics & IMAGE_DLL_CHARACTERISTICS_DYNAMIC_BASE:
        dynamic = True

    # pe文件中中的重定位表是否被擦除
    if pe.FILE_HEADER.Characteristics & IMAGE_FILE_RELOCS_STRIPPED:
        stripped = True

    # 判断这个文件是否受到ASLR保护
    if not dynamic or (dynamic and stripped):
        aslr = False
    else:
        aslr = True
    return aslr


class AslrCheck(interfaces.plugins.PluginInterface):
    @classmethod
    def get_requirements(cls):
        return [
            # 设定内存层
            requirements.TranslationLayerRequirement(
                name='primary', description='Memory layer for the kernel',
                architectures=["Intel32", "Intel64"]),
            # 设定符号层
            requirements.SymbolTableRequirement(
                name="nt_symbols", description="Windows kernel symbols"),
            # 依赖pslist插件
            requirements.PluginRequirement(
                name='pslist', plugin=pslist.PsList, version=(1, 0, 0)),
            # 创建设置选项，只检查列表中的进程
            requirements.ListRequirement(name='pid',
                                         element_type=int,
                                         description="Process ID to include (all other processes are excluded)",
                                         optional=True),

        ]

    @classmethod
    def create_pid_filter(cls, pid_list: List[int] = None) -> Callable[[interfaces.objects.ObjectInterface], bool]:
        filter_func = lambda _: False
        pid_list = pid_list or []
        filter_list = [x for x in pid_list if x is not None]
        if filter_list:
            filter_func = lambda x: x.UniqueProcessId not in filter_list
        return filter_func

    def _generator(self, procs):
        pe_table_name = intermed.IntermediateSymbolTable.create(
            self.context,
            self.config_path,
            "windows",
            "pe",
            class_types=extensions.pe.class_types)

        procnames = list()
        for proc in procs:
            procname = proc.ImageFileName.cast("string", max_length=proc.ImageFileName.vol.count, errors='replace')
            if procname in procnames:
                continue
            procnames.append(procname)

            proc_id = "Unknown"
            try:
                proc_id = proc.UniqueProcessId
                proc_layer_name = proc.add_process_layer()
            except exceptions.InvalidAddressException as e:
                vollog.error(f"Process {proc_id}: invalid address {e} in layer {e.layer_name}")
                continue

            peb = self.context.object(
                self.config['nt_symbols'] + constants.BANG + "_PEB",
                layer_name=proc_layer_name,
                offset=proc.Peb)

            try:
                dos_header = self.context.object(
                    pe_table_name + constants.BANG + "_IMAGE_DOS_HEADER",
                    offset=peb.ImageBaseAddress,
                    layer_name=proc_layer_name)
            except Exception as e:
                continue

            pe_data = io.BytesIO()
            for offset, data in dos_header.reconstruct():
                pe_data.seek(offset)
                pe_data.write(data)
            pe_data_raw = pe_data.getvalue()
            pe_data.close()

            try:
                # 转换成PE对象
                pe = pefile.PE(data=pe_data_raw)
            except Exception as e:
                continue

            aslr = check_aslr(pe)

            yield (0, (proc_id,
                       procname,
                       format_hints.Hex(pe.OPTIONAL_HEADER.ImageBase),
                       aslr,
                       ))

    def run(self):
        # 使用pslist插件获取进程列表
        procs = pslist.PsList.list_processes(self.context,
                                             self.config["primary"],
                                             self.config["nt_symbols"],
                                             filter_func=self.create_pid_filter(self.config.get('pid', None)))
        # 进行TreeGrid渲染
        return renderers.TreeGrid([
            ("PID", int),
            ("Filename", str),
            ("Base", format_hints.Hex),
            ("ASLR", bool)],
            self._generator(procs))
