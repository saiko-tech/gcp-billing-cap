from setuptools import setup, find_namespace_packages

setup(
    name = 'pulumi-gcp-billing-cap',
    version = '0.4.2',
    url = 'https://github.com/saiko-tech/pulumi-gcp-billing-cap',
    description = 'Pulumi package for capping GCP Billing vi Pub/Sub & Cloud Functions',
    packages = ['pulumi_gcp_billing_cap'],
    package_dir={
        'pulumi_gcp_billing_cap': './pulumi/gcp_billing_cap'
    },
    install_requires=[
        'pulumi>=3.0.0,<4.0.0',
        'pulumi-gcp>=6.0.0,<7.0.0',
        'pulumi-random>=4.2.0,<5.0.0'])
