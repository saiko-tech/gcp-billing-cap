from setuptools import setup, find_packages

setup(
    name = 'gcp-billing-cap',
    version = '0.1.0',
    url = 'https://github.com/saiko-tech/gcp-billing-cap',
    description = 'Pulumi package for capping GCP Billing vi Pub/Sub & Cloud Functions',
    packages = find_packages()
)
