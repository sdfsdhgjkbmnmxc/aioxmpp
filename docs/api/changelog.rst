.. _changelog:

Changelog
#########

Version 0.5
===========

* Support for `XEP-0045`__ multi-user chats is now available in the
  :mod:`aioxmpp.muc` subpackage.

  __ https://xmpp.org/extensions/xep-0045.html

* Mostly transparent support for `XEP-0115`__ (Entity Capabilities) is now
  available using the :mod:`aioxmpp.entitycaps` subpackage.

  __ https://xmpp.org/extensions/xep-0115.html

* Support for transparent non-scalar attributes, which get mapped to XSOs. Use
  cases are dicts mapping language tags to strings (such as for message
  ``body`` elements) or sets of values which are represented by discrete XML
  elements.

  For this, the method :meth:`~aioxmpp.xso.AbstractType.get_formatted_type` was
  added to :class:`aioxmpp.xso.AbstractType` and two new descriptors,
  :class:`aioxmpp.xso.ChildValueMap` and :class:`aioxmpp.xso.ChildValueList`,
  were implemented.

  .. autosummary::

     ~aioxmpp.xso.ChildValueMap
     ~aioxmpp.xso.ChildValueList
     ~aioxmpp.xso.ChildTextMap

  **Breaking change**: The above descriptors are now used at several places,
  breaking the way these attributes need to be accessed:

  * :attr:`aioxmpp.stanza.Message.subject`,
  * :attr:`aioxmpp.stanza.Message.body`,
  * :attr:`aioxmpp.stanza.Presence.status`,
  * :attr:`aioxmpp.disco.xso.InfoQuery.features`,
  * and possibly others.

* Several stability improvements have been made. A race condition during stream
  management resumption was fixed and :class:`aioxmpp.node.AbstractClient`
  instances now stop if non-:class:`OSError` exceptions emerge from the
  stream (as these usually indicate an implementation or user error).

  :class:`aioxmpp.callbacks.AdHocSignal` now provides full exception
  isolation.

* Support for capturing the raw XML events used for creating
  :class:`aioxmpp.xso.XSO` instances from SAX is now provided through
  :class:`aioxmpp.xso.CapturingXSO`. Helper functions to work with these events
  are also provided, most notably :func:`aioxmpp.xso.events_to_sax`, which can
  be used to re-create the original XML from those events.

  The main use case is to be able to write out a transcript of received XML
  data, independent of XSO-level understanding for the data received, provided
  the parts which are understood are semantically correct (transcripts will be
  incomplete if parsing fails due to incorrect contents).

  .. autosummary::

     ~aioxmpp.xso.CapturingXSO
     ~aioxmpp.xso.capture_events
     ~aioxmpp.xso.events_to_sax

  This feature is already used in :class:`aioxmpp.disco.xso.InfoQuery`, which
  now inherits from :class:`~aioxmpp.xso.CapturingXSO` and provides its
  transcript (if available) at
  :attr:`~aioxmpp.disco.xso.InfoQuery.captured_events`.

* The core SASL implementation has been refactored in its own independent
  package, :mod:`aiosasl`. Only the XMPP specific parts reside in
  :mod:`aioxmpp.sasl` and :mod:`aioxmpp` now depends on :mod:`aiosasl`.

* :meth:`aioxmpp.stream.StanzaStream.register_message_callback` is more clearly
  specified now, a bug in the documentation has been fixed.

* :mod:`aioxmpp.stream_xsos` is now called :mod:`aioxmpp.nonza`, in accordance
  with `XEP-0360`__.

  __ https://xmpp.org/extensions/xep-0360.html

* :class:`aioxmpp.xso.Date` and :class:`aioxmpp.xso.Time` are now available to
  for `XEP-0082`__ use. In addition, support for the legacy date time format is
  now provided in :class:`aioxmpp.xso.DateTime`.

  .. autosummary::

     ~aioxmpp.xso.Date
     ~aioxmpp.xso.Time
     ~aioxmpp.xso.DateTime

  __ https://xmpp.org/extensions/xep-0082.html

* The Python 3.5 compatibility of the test suite has been improved. In a
  corner-case, :class:`StopIteration` was emitted from ``data_received``, which
  caused a test to fail with a :class:`RuntimeError` due to implementation of
  `PEP-0479`__ in Python 3.5. See the `issue at github
  <https://github.com/horazont/aioxmpp/issues/3>`_.

  __ https://www.python.org/dev/peps/pep-0479/

* Helper functions for reading and writing single XSOs (and their children) to
  binary file-like objects have been introduced.

  .. autosummary::

     ~aioxmpp.xml.write_single_xso
     ~aioxmpp.xml.read_xso
     ~aioxmpp.xml.read_single_xso


Version 0.4
===========

* Documentation change: A simple sphinx extension has been added which
  auto-detects coroutines and adds a directive to mark up signals.

  The latter has been added to relevant places and the former automatically
  improves the documentations quality.

* :class:`aioxmpp.roster.Service` now implements presence subscription
  management. To track the presence of peers, :mod:`aioxmpp.presence` has been
  added.

* :mod:`aioxmpp.stream` and :mod:`aioxmpp.nonza` are part of the public
  API now. :mod:`aioxmpp.nonza` has gained the XSOs for SASL (previously
  in :mod:`aioxmpp.sasl`) and StartTLS (previously in
  :mod:`aioxmpp.security_layer`).

* :class:`aioxmpp.xso.XSO` subclasses now support copying and deepcopying.

* :mod:`aioxmpp.protocol` has been moved into the internal API part.

* :class:`aioxmpp.stanza.Message` specification fixed to have
  ``"normal"`` as default for :attr:`~aioxmpp.stanza.Message.type_` and relax
  the unknown child policy.

* *Possibly breaking change*: :attr:`aioxmpp.xso.XSO.DECLARE_NS` is now
  automatically generated by the meta class
  :class:`aioxmpp.xso.XMLStreamClass`. See the documentation for the detailed
  rules.

  To get the old behaviour for your class, you have to put ``DECLARE_NS = {}``
  in its declaration.

* :class:`aioxmpp.stream.StanzaStream` has a positional, optional argument
  (`local_jid`) for ejabberd compatiblity.

* Several fixes and workarounds, finally providing ejabberd compatibility:

  * :class:`aioxmpp.nonza.StartTLS` declares its namespace
    prefixless. Otherwise, connections to some versions of ejabberd fail in a
    very humorous way: client says "I want to start TLS", server says "You have
    to use TLS" and closes the stream with a policy-violation stream error.

  * Most XSOs now declare their namespace prefixless, too.

  * Support for legacy (`RFC 3921`__) XMPP session negotiation implemented in
    :class:`aioxmpp.node.AbstractClient`. See :mod:`aioxmpp.rfc3921`.

    __ https://tools.ietf.org/html/rfc3921

  * :class:`aioxmpp.stream.StanzaStream` now supports incoming IQs with the
    bare JID of the local entity as sender, taking them as coming from the
    server.

* Allow pinning of certificates for which no issuer certificate is available,
  because it is missing in the server-provided chain and not available in the
  local certificate store. This is, with respect to trust, treated equivalent
  to a self-signed cert.

* Fix stream management state going out-of-sync when an errorneous stanza
  (unknown payload, type or validator errors on the payload) was received. In
  addition, IQ replies which cannot be processed raise
  :class:`aioxmpp.errors.ErrorneousStanza` from
  :meth:`aioxmpp.stream.StanzaStream.send_iq_and_wait_for_reply` and when
  registering futures for the response using
  :meth:`aioxmpp.stream.StanzaStream.register_iq_response_future`. See the
  latter for details on the semantics.

* Fixed a bug in :class:`aioxmpp.xml.XMPPXMLGenerator` which would emit
  elements in the wrong namespace if the meaning of a XML namespace prefix was
  being changed at the same time an element was emitted using that namespace.

* The defaults for unknown child and attribute policies on
  :class:`aioxmpp.xso.XSO` are now ``DROP`` and not ``FAIL``. This is for
  better compatibility with old implementations and future features.

Version 0.3
===========

* **Breaking change**: The `required` keyword argument on most
  :mod:`aioxmpp.xso` descriptors has been removed. The semantics of the
  `default` keyword argument have been changed.

  Before 0.3, the XML elements represented by descriptors were not required by
  default and had to be marked as required e.g. by setting ``required=True`` in
  :class:`.xso.Attr` constructor.

  Since 0.3, the descriptors are generally required by default. However, the
  interface on how to change that is different. Attributes and text have a
  `default` keyword argument which may be set to a value (which may also be
  :data:`None`). In that case, that value indicates that the attribute or text
  is absent: it is used if the attribute or text is missing in the source XML
  and if the attribute or text is set to the `default` value, it will not be
  emitted in XML.

  Children do not support default values other than :data:`None`; thus, they
  are simply controlled by a boolean flag `required` which needs to be passed
  to the constructor.

* The class attributes :attr:`~aioxmpp.service.Meta.SERVICE_BEFORE` and
  :attr:`~aioxmpp.service.Meta.SERVICE_AFTER` have been
  renamed to :attr:`~aioxmpp.service.Meta.ORDER_BEFORE` and
  :attr:`~aioxmpp.service.Meta.ORDER_AFTER` respectively.

  The :class:`aioxmpp.service.Service` class has additional support to handle
  the old attributes, but will emit a DeprecationWarning if they are used on a
  class declaration.

  See :attr:`aioxmpp.service.Meta.SERVICE_AFTER` for more information on the
  deprecation cycle of these attributes.
