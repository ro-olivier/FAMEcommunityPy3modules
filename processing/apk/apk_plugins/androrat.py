import json
from . import APKPlugin


class AndroRAT(APKPlugin):
    name = "androrat"
    extraction = "AndroRAT Configuration"
    probable_name = "AndroRAT"

    def run(self, module):
        for cls in self.vm_analysis.get_classes():
            cls = cls.get_vm_class()
            if 'Lmy/app/client/ProcessCommand;'.lower() in cls.get_name().lower():
                self.process_class = cls
                break
        else:
            return None

        c2Found = False
        portFound = False
        c2 = ""
        port = ""
        string = None
        for method in self.process_class.get_methods():
            if method.name == 'loadPreferences':
                for inst in method.get_instructions():
                    if inst.get_name() == 'const-string':
                        string = inst.get_output().split(',')[-1].strip(" '")
                        if c2Found:
                            c2 = string
                            c2Found = False
                        if string == 'ip':
                            c2Found = True
                        if string == 'port':
                            portFound = True
                    if inst.get_name() == 'const/16':
                        if portFound:
                            string = inst.get_output().split(',')[-1].strip(" '")
                            port = string
                    if c2 and port:
                        break

        server = ""
        if port:
            server = "{0}:{1}".format(c2, str(port))
        else:
            server = c2

        module.add_ioc(server, ['androdat', 'c2'])

        return json.dumps({'c2': server}, indent=2)
