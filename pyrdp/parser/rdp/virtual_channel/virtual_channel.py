#
# This file is part of the PyRDP project.
# Copyright (C) 2018 GoSecure Inc.
# Licensed under the GPLv3 or later.
#

from io import BytesIO

from pyrdp.core import Uint32LE
from pyrdp.enum import VirtualChannelPDUFlag
from pyrdp.parser.parser import Parser
from pyrdp.pdu import VirtualChannelPDU


class VirtualChannelParser(Parser):
    """
    Parser class for VirtualChannel PDUs.
    """

    MAX_CHUNK_SIZE = 1600  # https://msdn.microsoft.com/en-us/library/cc240548.aspx

    def parse(self, data):
        """
        :type data: bytes
        :return: VirtualChannelPDU
        """
        stream = BytesIO(data)
        length = Uint32LE.unpack(stream)
        flags = Uint32LE.unpack(stream)
        payload = stream.read(length)
        return VirtualChannelPDU(length, flags, payload)

    def write(self, pdu):
        """
        :type pdu: VirtualChannelPDU
        :return: A LIST of VirtualChannelPDUs as raw bytes. The first one has the CHANNEL_FLAG_FIRST
                 set and the last one has the CHANNEL_FLAG_LAST set.
        """
        rawPacketList = []
        length = pdu.length
        dataStream = BytesIO(pdu.payload)
        while length > 0:
            stream = BytesIO()
            Uint32LE.pack(pdu.length, stream)
            flags = pdu.flags & 0b11111111111111111111111111111100
            if len(rawPacketList) == 0:
                # Means it's the first packet.
                flags |= VirtualChannelPDUFlag.CHANNEL_FLAG_FIRST
            if length <= self.MAX_CHUNK_SIZE:
                # Means it's the last packet.
                flags |= VirtualChannelPDUFlag.CHANNEL_FLAG_LAST
            Uint32LE.pack(flags, stream)
            toWrite = self.MAX_CHUNK_SIZE if length >= self.MAX_CHUNK_SIZE else length
            stream.write(dataStream.read(toWrite))
            rawPacketList.append(stream.getvalue())
            length -= toWrite
        return rawPacketList
