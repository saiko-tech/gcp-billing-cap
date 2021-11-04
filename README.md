# gcp-billing-capper

## Usage

```py
cloudresourcemanager_enable = projects.Service(
    'cloudresourcemanager-api',
    service='cloudresourcemanager.googleapis.com')

billingbudgets_enable = projects.Service(
    'billingbudgets-api',
    service='billingbudgets.googleapis.com')

shutil.make_archive('/tmp/capper', 'zip', 'capper')

billing_project = gcp.organizations.get_project().name
billing_account = organizations.get_billing_account(billing_account=config.require('gcpBillingAccount'))

capper.GCPBillingCap(
    'gcp-billing-cap',
    args=capper.GCPBillingCapArgs(
        billing_account=billing_account.id,
        billing_project=billing_project,
        currency_code=config.require('gcpCurrencyCode'),
        max_spend=config.require('gcpMaxSpend'),
        capper_zip_path='/tmp/capper.zip'),
    opts=ResourceOptions(depends_on=[billingbudgets_enable, cloudresourcemanager_enable]))
```
