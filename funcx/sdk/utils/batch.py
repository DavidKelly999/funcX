import os
from collections import defaultdict

from funcx.serialize import FuncXSerializer


class Batch:
    """Utility class for creating batch submission in funcX"""

    def __init__(self):
        self.tasks = []
        self.fx_serializer = FuncXSerializer()

    def add(self, *args, endpoint_id='UNDECIDED', function_id=None, files=None,
            **kwargs):
        """Add an function invocation to a batch submission

        Parameters
        ----------
        *args : Any
            Args as specified by the function signature
        endpoint_id : uuid str
            Endpoint UUID string. Required
        function_id : uuid str
            Function UUID string. Required
        asynchronous : bool
            Whether or not to run the function asynchronously

        Returns
        -------
        None
        """
        assert endpoint_id is not None, "endpoint_id key-word argument must be set"
        assert function_id is not None, "function_id key-word argument must be set"

        assert('_globus_files' not in kwargs)
        kwargs['_globus_files'] = defaultdict(list)
        for globus_id, file_name in files or []:
            if not file_name.startswith('~/.globus_funcx'):
                file_name = os.path.join('~/.globus_funcx', file_name)
            kwargs['_globus_files'][globus_id].append(file_name)

        ser_args = self.fx_serializer.serialize(args)
        ser_kwargs = self.fx_serializer.serialize(kwargs)
        payload = self.fx_serializer.pack_buffers([ser_args, ser_kwargs])

        data = {'endpoint': endpoint_id,
                'function': function_id,
                'args': args,
                'kwargs': kwargs,
                'payload': payload}

        self.tasks.append(data)

    def prepare(self):
        """Prepare the payloads to be post to web service in a batch

        Parameters
        ----------

        Returns
        -------
        payloads in dictionary, Dict[str, list]
        """
        data = {
            'tasks': []
        }

        for task in self.tasks:
            new_task = (task['function'], task['endpoint'], task['payload'])
            data['tasks'].append(new_task)

        return data
