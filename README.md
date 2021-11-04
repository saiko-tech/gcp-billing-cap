# gcp-billing-cap (Pulumi)

Prevent excessive cloud costs via GCP Billing Alerts, Pub/Sub & Cloud Functions.

## Installation

`setup.py`
```py
from setuptools import setup, find_packages

setup(
    name = 'my-project',
    version = '0.1.0',
    url = 'https://example.com/',
    description = 'example.com Infrastructure-As-Code using Pulumi',
    packages = find_packages(),
    install_requires = [
        'gcp-billing-cap @ git+ssh://git@github.com/saiko-tech/gcp-billing-cap@24f76341d8c92305f7e7a8b7052f091a5e879c35#egg=gcp-billing-cap',
    ]
)
```

note the use of an explicit Git SHA in `install_requires` - always do this when linking against dependencies via Git or you will become the victim of a supply chain attack!

## Usage

```py
cloudresourcemanager_enable = projects.Service(
    'cloudresourcemanager-api',
    service='cloudresourcemanager.googleapis.com')

billingbudgets_enable = projects.Service(
    'billingbudgets-api',
    service='billingbudgets.googleapis.com')

# 'capper' needs to point to the `/capper` directory of this repo
shutil.make_archive('/tmp/capper', 'zip', 'capper')

billing_project = gcp.organizations.get_project().name
billing_account = organizations.get_billing_account(billing_account=config.require('gcpBillingAccount'))

capper.GCPBillingCap(
    'gcp-billing-cap',
    args=capper.GCPBillingCapArgs(
        billing_account=billing_account.id,
        billing_project=billing_project,
        currency_code='GBP', # must match the currency used in your GCP billing account
        max_spend='100', # £100 per month, must be a string unfortunately
        capper_zip_path='/tmp/capper.zip'),
    opts=ResourceOptions(depends_on=[billingbudgets_enable, cloudresourcemanager_enable]))
```
