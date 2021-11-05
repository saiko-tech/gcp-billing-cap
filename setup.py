from setuptools import setup, find_namespace_packages

setup(
    name = 'gcp-billing-cap',
    version = '0.1.0',
    url = 'https://github.com/saiko-tech/gcp-billing-cap',
    description = 'Pulumi package for capping GCP Billing vi Pub/Sub & Cloud Functions',
    packages = ['gcp_billing_cap'],
    package_dir={
        'gcp_billing_cap': './pulumi/gcp_billing_cap'
    },
    install_requires=[
        'pulumi>=3.0.0,<4.0.0',
        'pulumi-gcp>=5.0.0,<6.0.0',
        'pulumi-random>=4.2.0,<5.0.0'])
