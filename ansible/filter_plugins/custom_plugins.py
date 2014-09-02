import hashlib


class FilterModule(object):
    ''' Custom filters are loaded by FilterModule objects '''

    def filters(self):
        return {
            'jenkins_hash': self.jenkins_hash,
        }

    def jenkins_hash(self, value):
        # TODO: generate salt randomly
        salt = "salt"
        h = hashlib.sha256()
        h.update("%s{%s}" % (value, salt))
        return salt + ":" + h.hexdigest()
