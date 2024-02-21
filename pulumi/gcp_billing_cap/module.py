from typing import Optional
import pulumi
from pulumi.output import Input, Output
import pulumi_gcp
import pulumi_random
from pulumi.resource import ResourceOptions
from pulumi_gcp import billing, pubsub, serviceaccount, cloudfunctions, storage, projects


class GCPBillingCapArgs:

    billing_account: Input[str]
    billing_project_name: Input[str]
    billing_project_number: Input[str]
    currency_code: Input[str]
    max_spend: Input[str]
    capper_zip_path: str

#    @staticmethod
#    def from_inputs(inputs: Inputs) -> 'GCPBillingCapArgs':
#        return GCPBillingCapArgs(
#            billing_account=inputs['billingAccount'],
#            billing_project=inputs['billingProject'],
#            currency_code=inputs['currencyCode'],
#            max_spend=inputs['maxSpend'])

    def __init__(
            self,
            billing_account: Input[str],
            billing_project_name: Input[str],
            billing_project_number: Input[str],
            currency_code: Input[str],
            max_spend: Input[str],
            capper_zip_path: str) -> None:
        self.billing_account = billing_account
        self.billing_project_name = billing_project_name
        self.billing_project_number = billing_project_number
        self.currency_code = currency_code
        self.max_spend = max_spend
        self.capper_zip_path = capper_zip_path


class GCPBillingCap(pulumi.ComponentResource):
    def __init__(
            self,
            name: str,
            args: GCPBillingCapArgs,
            props: Optional[dict] = None,
            opts: ResourceOptions = None):
        super().__init__('gcp_billing_cap:index:GCPBillingCap', name, None, opts)

        topic = pubsub.Topic(
            'billing-alerts',
            name='billing-capper-alerts',
            opts=ResourceOptions(parent=self))

        bucket = storage.Bucket(
            'cloudfunctions-source',
            name='billing-capper-cloudfunction-source',
            opts=ResourceOptions(parent=self))

        archive = storage.BucketObject(
            'cloudfunctions-source',
            bucket=bucket.name,
            source=pulumi.FileAsset(args.capper_zip_path),
            opts=ResourceOptions(parent=self))

        sa = serviceaccount.Account(
            'capper-sa',
            account_id='billing-capper',
            display_name='Billing Capper Cloud Functions service acount',
            opts=ResourceOptions(parent=self))
        sa_id = sa.email.apply(lambda email: f'serviceAccount:{email}')

        billing.AccountIamMember(
            'capper-billing-admin',
            billing_account_id=args.billing_account,
            role='roles/billing.admin',
            member=sa_id,
            opts=ResourceOptions(parent=self))

        function = cloudfunctions.Function(
            'capper',
            name='billing-capper',
            region='europe-west1', # TODO: make this configurable
            runtime='python39',
            available_memory_mb=128,
            source_archive_bucket=bucket.name,
            source_archive_object=archive.name,
            event_trigger=cloudfunctions.FunctionEventTriggerArgs(
                event_type='google.pubsub.topic.publish',
                resource=topic.id),
            entry_point='stop_billing',
            environment_variables={
                'GCP_PROJECT': args.billing_project_name,
            },
            service_account_email=sa.email,
            opts=ResourceOptions(parent=self))

        suffix = pulumi_random.RandomString(
            'account-id-suffix',
            length=3,
            min_lower=3,
            opts=ResourceOptions(parent=self))

        pubsub_invoker_sa = serviceaccount.Account(
            'pubsub-push-to-capper',
            account_id=Output.concat('pubsub-push-to-capper', suffix.result),
            display_name=f'Pub/Sub Push to capper Invoker',
            opts=ResourceOptions(parent=self))

        perms = cloudfunctions.FunctionIamMember(
            'pubsub-to-capper-invoker',
            project=function.project,
            region=function.region,
            cloud_function=function.name,
            role='roles/cloudfunctions.invoker',
            member=pubsub_invoker_sa.email.apply(lambda email: f'serviceAccount:{email}'),
            opts=ResourceOptions(parent=self))

        billing_provider = pulumi_gcp.Provider(
            'billing-provider',
            billing_project=args.billing_project_name,
            user_project_override=True,
            opts=ResourceOptions(parent=self))

        billing.Budget(
            'budget',
            billing_account=args.billing_account,
            display_name='Billing Capper Budget',
            amount=billing.BudgetAmountArgs(
                specified_amount=billing.BudgetAmountSpecifiedAmountArgs(
                    currency_code=args.currency_code,
                    units=args.max_spend)),
            threshold_rules=[billing.BudgetThresholdRuleArgs(
                threshold_percent=0.5)],
            all_updates_rule=billing.BudgetAllUpdatesRuleArgs(
                pubsub_topic=topic.id),
            budget_filter=billing.BudgetBudgetFilter(
                projects=[f'projects/{args.billing_project_number}']),
            opts=ResourceOptions(
                parent=self,
                depends_on=[perms],
                provider=billing_provider))
