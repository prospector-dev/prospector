import os
from unittest import TestCase
from pkg_resources import Requirement
from prospector import dependency_detection


class DependencyDetectionTest(TestCase):

    def _expected(self, *requirements):
        return [Requirement.parse(req) for req in requirements]

    def test_requirements_txt_parsing(self):
        filepath = os.path.join(os.path.dirname(__file__), 'dependency_tests/test1/requirements.txt')
        dependencies = dependency_detection.from_requirements_txt(filepath)

        expected = self._expected(
            'amqp!=1.0.13',
            'Django>=1.5.0',
            'six<1.4,>=1.3.0',
            'South==0.8.2',
        )

        self.assertEqual(expected, dependencies)

    def test_requirements_dir_parsing(self):
        filepath = os.path.join(os.path.dirname(__file__), 'dependency_tests/test2/requirements')
        dependencies = dependency_detection.from_requirements_dir(filepath)

        expected = self._expected(
            'amqp==1.0.13',
            'anyjson==0.3.3',
            'Django==1.5.2',
            'South==0.8.2',
        )

        self.assertEqual(expected, dependencies)

    def test_requirements_dir_parsing(self):
        filepath = os.path.join(os.path.dirname(__file__), 'dependency_tests/test2/requirements')
        dependencies = dependency_detection.from_requirements_dir(filepath)

        expected = self._expected(
            'amqp==1.0.13',
            'anyjson==0.3.3',
            'Django==1.5.2',
            'South==0.8.2',
        )

        self.assertEqual(expected, dependencies)

    def test_requirements_blob_parsing(self):
        filepath = os.path.join(os.path.dirname(__file__), 'dependency_tests/test3')
        dependencies = dependency_detection.from_requirements_blob(filepath)

        expected = self._expected(
            'amqp==1.0.13',
            'anyjson==0.3.3',
            'django-gubbins==1.1.2',
        )

        self.assertEqual(expected, dependencies)