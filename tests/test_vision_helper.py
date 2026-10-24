import json
import unittest
from pathlib import Path
import tempfile
from unittest.mock import patch

from scripts.review_reference_images import parse_observations
from scripts import review_reference_images as helper


class VisionHelperTests(unittest.TestCase):
    def test_observations_are_bound_to_actual_input_hashes(self):
        images=[{'role':r,'sha256':str(i)*64} for i,r in enumerate(['overview','layout','details'])]
        body={'images':[{'role':i['role'],'observations':'Visible test image observation of color, shape and arrangement. '*3} for i in images]}
        result=parse_observations({'choices':[{'message':{'content':json.dumps(body)}}]},images)
        self.assertEqual([r['sha256'] for r in result],[i['sha256'] for i in images])

    def test_missing_or_unobserved_roles_are_rejected(self):
        images=[{'role':r,'sha256':'a'*64} for r in ['overview','layout','details']]
        response={'choices':[{'message':{'content':'{"images":[]}'}}]}
        with self.assertRaises(ValueError):
            parse_observations(response,images)

    def test_uncertain_review_is_not_replayed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary)
            folder=root/'artifacts/references'
            folder.mkdir(parents=True)
            images=[{'role':role,'sha256':str(i)*64} for i,role in enumerate(['overview','layout','details'])]
            (folder/'manifest.json').write_text(json.dumps({'images':images}))
            (folder/'vision-helper.json').write_text(json.dumps({'state':'submitted_or_uncertain',
                'input_hashes':{i['role']:i['sha256'] for i in images}}))
            with patch.object(helper,'ROOT',root), patch.object(helper,'check',return_value={'passed':True}), patch.object(helper.urllib.request,'urlopen') as network:
                with self.assertRaisesRegex(ValueError,'no automatic replay'):
                    helper.main()
                network.assert_not_called()
