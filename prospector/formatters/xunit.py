from prospector.formatters.base import Formatter
from xml.dom.minidom import Document


class XunitFormatter(Formatter):

    """
    This formatter outputs messages in the Xunit xml format, which is used by several
    CI tools to parse output. This formatter is therefore a compatability shim between tools built
    to use Xunit and prospector itself.
    """

    def render(self, summary=True, messages=True, profile=False):
        xml_doc = Document()

        testsuite_el = xml_doc.createElement('testsuite')
        testsuite_el.setAttribute('errors', str(self.summary['message_count']))
        testsuite_el.setAttribute('failures', '0')
        testsuite_el.setAttribute('name', 'prospector-%s' % '-'.join(self.summary['tools']))
        testsuite_el.setAttribute('tests', str(self.summary['message_count']))
        testsuite_el.setAttribute('time', str(self.summary['time_taken']))
        xml_doc.appendChild(testsuite_el)

        prop_el = xml_doc.createElement('properties')
        testsuite_el.appendChild(prop_el)

        sysout_el = xml_doc.createElement('system-out')
        sysout_el.appendChild(xml_doc.createCDATASection(''))
        testsuite_el.appendChild(sysout_el)

        syserr_el = xml_doc.createElement('system-err')
        syserr_el.appendChild(xml_doc.createCDATASection(''))
        testsuite_el.appendChild(syserr_el)

        for message in sorted(self.messages):
            testcase_el = xml_doc.createElement('testcase')
            testcase_el.setAttribute('name', '%s-%s' % (message.location.path, message.location.line))

            failure_el = xml_doc.createElement('error')
            failure_el.setAttribute('message', message.message.strip())
            failure_el.setAttribute('type', '%s Error' % message.source)
            template = '%(path)s:%(line)s: [%(code)s(%(source)s), %(function)s] %(message)s'
            cdata = template % {
                'path': message.location.path,
                'line': message.location.line,
                'source': message.source,
                'code': message.code,
                'function': message.location.function,
                'message': message.message.strip()
            }
            failure_el.appendChild(xml_doc.createCDATASection(cdata))

            testcase_el.appendChild(failure_el)

            testsuite_el.appendChild(testcase_el)

        return xml_doc.toprettyxml()
