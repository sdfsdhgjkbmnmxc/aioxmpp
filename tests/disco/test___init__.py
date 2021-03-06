import unittest

import aioxmpp.disco as disco
import aioxmpp.disco.service as disco_service
import aioxmpp.disco.xso as disco_xso


class TestExports(unittest.TestCase):
    def test_Service(self):
        self.assertIs(disco.Service, disco_service.Service)

    def test_xso(self):
        self.assertIs(disco.xso, disco_xso)

    def test_Node(self):
        self.assertIs(disco.Node, disco_service.Node)

    def test_StaticNode(self):
        self.assertIs(disco.StaticNode, disco_service.StaticNode)
