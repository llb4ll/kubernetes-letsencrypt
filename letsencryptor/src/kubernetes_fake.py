import kubernetes_wrapper as k8s

class Kubernetes(k8s.Kubernetes):
    def __init__(self):
        super(Kubernetes, self).__init__(None, None, namespace="test-namespace")

    def _fetch_pykube(self, pykube_type, name=None):
        return pykube_type(api = self.api_client, obj = {})
